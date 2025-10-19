import asyncio
import typing
import typing as t
from logging import getLogger

from aiogram import Bot
from aiogram.types import InputMediaPhoto, Message, PhotoSize
from aiopath import Path as AioPath
from requests import session
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
import sqlalchemy.orm as so

from config import settings
from database import User
from database.blog.models import CatAd, Photo
from keyboards.ads import moderate_ad_kb
from schemas.ads import CatAdsSchema, PhotoSchema
from utils.bot_utils import bot_save_photos_from_photo_id_list
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
                    foto_for_delete = AioPath(photo.file_path)
                    try:
                        await foto_for_delete.unlink()
                    except FileNotFoundError as e:
                        logger.error('Во время очистки фотографий возникла ошибка %s', e)
            logger.error('Внимание! Рекламное объявление: %s не сформировано', ad_message, exc_info=True)
            await self.session.rollback()
            raise

    async def get_pending_moderation_ads_objects(
            self,
    ) -> t.Optional[t.List[CatAd]]:
        """Функция получения списка модерируемых сообщений для отправки"""
        # Получаем set из cache с уже отправленными объявлениями
        pending_ads_cash: set = await self.cache_storage.fetch_set_with_int(settings.PENDING_ADS_KEY)
        # Формируем список без отправленных объявлений
        try:
            pending_cat_ads = await CatAd.get_ads(self.session, exclude_ids=pending_ads_cash)
        except Exception as e:
            logger.error('Ошибка формирования списка рекламных объявлений %s', e)
            pending_cat_ads = []
        # Если есть новые объявления для отправки, то обновляем cache
        if pending_cat_ads:
            await self.cache_storage.put_set(
                key=settings.PENDING_ADS_KEY,
                data={cat_ads.id for cat_ads in pending_cat_ads},
                ttl=settings.PENDING_ADS_TTL
            )
        return pending_cat_ads

    async def send_pending_moderation_ad(self, pending_cat_ads: CatAd) -> None:
        cat_ads_schema: CatAdsSchema = self.schema.model_validate(pending_cat_ads)
        media = self.get_media_message_from_schema(cat_ads_schema)
        # Отправляем объявление модератору
        await self.bot.send_media_group(settings.ADMIN_ID, media)
        await self.bot.send_message(
            settings.ADMIN_ID,
            'Выберите действие:',
            reply_markup=moderate_ad_kb(ads_id=pending_cat_ads.id)
        )
        return



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

    async def check_pending_ads(self):
        """
        Проверяет наличие непромодерированных объявлений
        """
        try:
            # Получаем объявления не прошедшие модерацию.
            pending_cat_ads = await self.get_pending_moderation_ads_objects()
            if pending_cat_ads:
                len_pending_ads = len(pending_cat_ads)
                logger.info("Найдено %d объявления для модерации", len_pending_ads)
                await self.bot.send_message(
                    settings.ADMIN_ID, f'Найдены посты в кол-ве: {len_pending_ads} - '
                                       f'ожидающих модерацию',
                )
                for ad in pending_cat_ads:
                    try:
                        #Отправляем объявление модератору
                        await self.send_pending_moderation_ad(pending_cat_ads=ad)

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
