import asyncio
import typing
import typing as t
from logging import getLogger

import aiofiles
from aiofiles import os as aio_os
from aiogram import Bot
from aiogram.types import InputMediaPhoto, Message, PhotoSize
# from aiopath import AsyncPath
from requests import session
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
import sqlalchemy.orm as so

from config import settings
from database import User
from database.blog.enums import AdStatus
from database.blog.models import CatAd, Photo
from keyboards.ads import moderate_ad_kb
from schemas.ads import CatAdsSchema, PhotoSchema
from utils.bot_utils import bot_save_photos_from_photo_id_list, get_moderator_id_from_pool
from utils.cache import RedisCache

logger = getLogger(__name__)


class CatAdsService:
    """Сервис для добавления сообщений в базу"""

    schema = CatAdsSchema
    model = CatAd

    def __init__(
            self,
            session: AsyncSession,
            cache_storage: RedisCache,
            bot: Bot
    ):
        self.session = session
        self.cache_storage = cache_storage
        self.bot = bot

    async def save_photo_from_message(self, cat_ads_schema: CatAdsSchema) -> t.List[Photo]:
        """Метод для сохранения фотографий на диск и формируем ORM Объекты
        для последующего их просмотра во время модерации через админ панель
        Arguments:
            cat_ads_schema: объект модели CatAdsSchema
        Returns:
            Список объектов класса Photo для добавления их к объявлению
        """
        # Формируем кортеж данных для скачивания
        photo_id_list = cat_ads_schema.get_photo_id_tuple()
        # Получаем объекты с фотографиями
        try:
            # Поучаем словарь с объектами PhotoSchema
            uploaded_photos_dict = await bot_save_photos_from_photo_id_list(
                bot=self.bot, photo_id_list=photo_id_list, directory=str(cat_ads_schema.author_id)
            )
        except Exception as e:
            logger.error("Ошибка сохранения рекламных фото: %s", e)
        else:
            # Дополняем путями сохранения фотографий объект схемы
            for photo in cat_ads_schema.photos:
                foto_value: PhotoSchema = uploaded_photos_dict.get(photo.photo_id)
                if foto_value:
                    photo.file_name = foto_value.file_name
                    photo.file_size = foto_value.file_size
                    photo.file_path = foto_value.file_path
        # Создаём объекты ORM модели базы с фотографиями
        photo_objects = []
        try:
            for value in cat_ads_schema.photos:
                photo = Photo(**value.model_dump())
                photo_objects.append(photo)
            self.session.add_all(photo_objects)
            await self.session.flush()
        except Exception as e:
            logger.error('Во время формирования фотографий объявления возникала ошибка %s', e)
            raise
        return photo_objects

    async def save_ad_message(self, ad_message: dict) -> CatAd:
        """Сохраняет объявление валидированное и полученное из FSM контекста"""
        # Инициализируем объект класса CatAdsSchema
        cat_ads_schema: CatAdsSchema = self.schema(**ad_message)
        try:
            # Создаём словарь данных без фотографий
            cat_ads_dict = cat_ads_schema.getdata_without_photos()
            # Формируем список с фотографиями
            photo_objects = await self.save_photo_from_message(cat_ads_schema)
            # Создаём объекты ORM модели базы с рекламой
            try:
                cat_ads_object = self.model(**cat_ads_dict, photos=photo_objects)
                self.session.add(cat_ads_object)
                await self.session.flush()
            except Exception as e:
                logger.error('Во время формирования текста объявления возникала ошибка %s ', e)
                raise e
            else:
                self.session.add(cat_ads_object)
                await self.session.flush()
                return cat_ads_object
        except Exception:
            # Удаление фотографий, rollback сессии.
            photos = cat_ads_schema.photos
            for photo in photos:
                if photo and photo.file_path:
                    foto_for_delete = photo.file_path
                    try:
                        await aio_os.remove(foto_for_delete)
                    except FileNotFoundError as e:
                        logger.error('Во время очистки фотографий возникла ошибка %s', e)
            logger.error('Внимание! Рекламное объявление: %s не сформировано', ad_message, exc_info=True)
            await self.session.rollback()
            raise

    async def moderate_ad_message(self, ads_id: int, comment, status: AdStatus):
        """Модерация сообщений"""
        ads_to_moderate: CatAd = await self.model.one_or_none(session=self.session, id=ads_id)
        if not ads_to_moderate:
            raise ValueError('Объявление id: %s не найдено! ', ads_id)
        elif ads_to_moderate.status in AdStatus.is_processed():
            raise ValueError('Объявление id: %s уже прошло модерацию! ', ads_id)
        else:
            ads_to_moderate.status = status
            ads_to_moderate.bot_message_title = comment
            self.session.add(ads_to_moderate)
            await self.session.flush()
            await self.cache_storage.rem_set(settings.PENDING_ADS_KEY, ads_id)

    def handle_mediagroup(self, foto_messages: t.Collection[Message], **kwargs):
        """Обрабатываем фотографии из медиасобщения и добавляем в схему"""
        photos = [{'photo_id': msg.photo[-1].file_id for msg in foto_messages}]
        cat_ads_schema: CatAdsSchema = self.schema(**kwargs).add_photos(photos)
        return cat_ads_schema

    def handle_message(
            self,
            foto_message: Message | None = None,
            **kwargs
    ) -> CatAdsSchema:
        """Получаем pydentic объект из фсм словаря.
        Arguments:
            foto_message: Сообщения с фотографией
            **kwargs: Словарь данных из FSM
        """
        photo: tuple = {'photo_id': foto_message.photo[-1].file_id},
        cat_ads_schema: CatAdsSchema = self.schema(**kwargs).add_photos(photo)
        return cat_ads_schema

    def get_media_message_from_schema(self, cat_ad_schema: CatAdsSchema, is_sorted=False) -> t.List[InputMediaPhoto]:
        """Формируем медисасообщение из Pydentic схемы
        Arguments:
           cat_ad_schema: Объект схемы  CatAdsSchema
           is_sorted: Производить ли сортировку по ключам
           Returns:
               Возвращает медиасообщение с фотографиями и текстом привязанное к Первому сообщению
       """
        caption = cat_ad_schema.get_caption()
        photos_dict = cat_ad_schema.get_photos(is_sorted=is_sorted)
        return self.make_media_group(photos_dict, caption=caption)

    def make_media_group(self, photos: list[dict[str, t.Any]], caption: str) -> t.List[InputMediaPhoto]:
        """Формирует медиагруппу из фотографий и текста
        Arguments:
            photos: Список фотографий для медиагруппы
            caption: Текст, который добавится к первой фотографии
            """
        media = []
        if photos:
            for idx, photo in enumerate(photos):
                photo_id = photo.get('photo_id')
                input_media = InputMediaPhoto(
                    media=photo_id,
                )
                if idx == 0:
                    input_media.caption = caption
                media.append(input_media)
        return media

    async def send_pending_ad(
            self,
            pending_cat_ad: CatAd,
            user_id: int,
            info_message: str | None = None,
            reply_markup = None
    ) -> None:
        cat_ads_schema: CatAdsSchema = self.schema.model_validate(pending_cat_ad)
        media = self.get_media_message_from_schema(cat_ads_schema)
        # Отправляем объявление пользователю
        await self.bot.send_media_group(user_id, media)
        if info_message:
            await self.bot.send_message(
                user_id,
                info_message,
                reply_markup=reply_markup
            )
            return

    async def check_pending_ads(self):
        """
        Проверяет наличие объявлений для модерации.
        """
        try:
            # Получаем объявления для модерации.
            # Получаем id объявлений из кэша для исключения их из выборки
            pending_ads_cash: set = await self.cache_storage.fetch_set_with_int(settings.PENDING_ADS_KEY)
            # Производим выборку объявлений
            # Добавить удаление из кэша сообщений прошедших модерацию!!!!
            pending_cat_ads = await self.model.get_ads(self.session, exclude_ids=pending_ads_cash)
            if pending_cat_ads:
                for ad in pending_cat_ads:
                    try:
                        if ad.status == AdStatus.NEW_BORN:
                            moderator_id = await get_moderator_id_from_pool(session=self.session)
                            len_pending_ads = len(pending_cat_ads)
                            logger.info(f"Найдено {len_pending_ads} объявления для модерации")
                            await self.bot.send_message(
                                moderator_id, f'Найдены посты в кол-ве: {len_pending_ads} - '
                                              f'ожидающих модерацию',
                            )
                            await self.send_pending_ad(
                                pending_cat_ad=ad,
                                user_id=moderator_id,
                                info_message='Выберите действие:',
                                reply_markup=moderate_ad_kb(
                                    ads_id=ad.id, author_id=ad.author_id
                                )
                            )
                            try:
                                await self.cache_storage.put_set(
                                    key=settings.PENDING_ADS_KEY,
                                    data={cat_ads.id for cat_ads in pending_cat_ads},
                                    ttl=settings.PENDING_ADS_TTL
                                )
                            except Exception as e:
                                logger.warning('Не удалось добавить в кэш рекламные объявления %s', e)
                        else:
                            # отправка рекламного поста - отклонённого модератором!
                            if ad.status == AdStatus.REJECTED:
                                await self.send_pending_ad(
                                    pending_cat_ad=ad,
                                    user_id=ad.author_id,
                                    info_message='Ваше рекланый пост был отклонен модератором.')
                                logger.info(f'Сообщение {ad.id} было отклонено модератором!')
                                try:
                                    await self.session.delete(ad)
                                except Exception as e:
                                    logger.error(
                                        'Во время удаления сообщения не прошедшего модерацию '
                                        'произошел сбой {}'.format(e))
                            if ad.status == AdStatus.APPROVED:  # отправка рекламного поста - одобренного модератором!
                                # Отправка сообщения в группу
                                await self.send_pending_ad(
                                    pending_cat_ad=ad,
                                    user_id=ad.author_id,
                                    info_message='Ваш рекламный пост был одобрен модератором.'
                                )
                                await self.send_pending_ad(
                                    pending_cat_ad=ad,
                                    user_id=settings.ADS_CHANNEL_ID,
                                )
                                ad.status = AdStatus.PUBLICATED
                                logger.info('Размещено сообщение в котоборохолке !')
                                self.session.add(ad)
                                await self.session.commit()
                        # отправка рекламного поста - ещё не просмотренного модератором
                        # Небольшая пауза между отправками
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f" Ошибка отправки объявления %d: %s", {ad.id}, e)
                        raise
            else:
                logger.info("Нет новых объявлений на модерации")
        except Exception as e:
            logger.error(f"Ошибка при проверке объявлений: %s ", e)
            raise
