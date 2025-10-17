import typing
import typing as t
from logging import getLogger

from aiogram import Bot
from aiogram.types import InputMediaPhoto, Message, PhotoSize
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
import sqlalchemy.orm as so

from database import User
from database.blog.models import CatAd, Photo
from schemas.ads import CatAdsSchema
from utils.bot_utils import bot_save_photo_from_message
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

    async def save_ad_message(self, ad_message: dict, author: User):
        photos: list = ad_message.pop('photos')
        # Получаем объекты с фотографиями
        try:
            user_id = str(author.id)
            saved_photos = []

            for foto in photos:
                photos_dict = await bot_save_photo_from_message(bot=self.bot, file_id=foto.get('file_id'), user_id=user_id)
                saved_photos.append(photos_dict)
        except Exception:
            raise
        else:
            photos = saved_photos
        photo_objects = []
        try:
            for value in photos:
                photo = Photo(
                    photo_id=value.photo_id,
                    sort_order=value.sort_order,
                    is_primary=value.is_primary,
                )
                photo_objects.append(photo)
            self.session.add_all(photo_objects)
            await self.session.flush()
        except Exception as e:
            await self.session.rollback()
            raise e
        # Получаем объект с рекламой
        try:
            cat_ads_object = self.model(**ad_message, author=author)
            self.session.add(cat_ads_object)
            await self.session.flush()
            cat_ads_object.photos.append(photo_objects)
        except Exception as e:
            await self.session.rollback()
            raise e
        self.session.add(cat_ads_object)
        await self.session.flush()
        return cat_ads_object

    async def get_pending_moderation_ads(
            self,
            exclude_ids: t.Union[t.Optional[ t.Collection[int]]] = None,
    ) -> t.Optional[t.List[CatAd]]:
        """Функция получения списка модерируемых сообщений для отправки"""
        pending_ads_key = 'pending_cat_ads'
        pending_ads_cash: set = await self.cache_storage.fetch_set_with_int(pending_ads_key)
        pending_cat_ads = await CatAd.get_ads(self.session)#exclude_ids=pending_ads_cash
        # if pending_cat_ads:
        #     await self.cache_storage.put_set(key=pending_ads_key, data={cat_ads.id for cat_ads in pending_cat_ads}, ttl=5 * 60)
        for pending_ad in pending_cat_ads:
            cat_ads_schema: CatAdsSchema = self.schema.model_validate(pending_ad)
            print(cat_ads_schema)
        return pending_cat_ads


    def get_pydentic_obj_from_fsm(
            self,
            foto_messages: t.Collection[Message] | None = None,
            **kwargs
    ) -> CatAdsSchema:
        """Получаем pydentic объект из фсм словаря.
        Arguments:
            foto_messages: Сообщения с фотографиями
            **kwargs: Словарь данных из FSM
        """
        cat_ads_schema: CatAdsSchema = self.schema(**kwargs)
        if foto_messages:
            photo = [{'photo_id': msg.photo[-1].file_id for msg in foto_messages}]
            cat_ads_schema.add_photos(photo)
        return cat_ads_schema


    def get_media_message_from_schema(self, cat_ad_schema: CatAdsSchema, is_sorted=False) -> t.List[InputMediaPhoto]:
        caption = cat_ad_schema.get_caption()
        photos_dict = cat_ad_schema.get_photos(is_sorted=is_sorted)
        return self.make_media_group(photos_dict, caption=caption)

    def make_media_group(self, photos: tuple, caption: str) -> t.List[InputMediaPhoto]:
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
