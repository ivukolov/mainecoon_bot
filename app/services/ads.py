import typing
import typing as t
from logging import getLogger

from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
import sqlalchemy.orm as so

from database import User
from database.blog.models import CatAd, Photo
from schemas.ads import CatAdsSchema
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
    ):
        self.session = session
        self.cache_storage = cache_storage

    async def save_ad_message(self, ad_message: dict, author: User):
        cat_ads_schema: CatAdsSchema = self.schema(**ad_message)
        cat_ads_dict = cat_ads_schema.model_dump(mode='python', exclude={'photos', 'photo_id'})
        cat_ads_object = self.model(**cat_ads_dict, author=author)
        self.session.add(cat_ads_object)
        await self.session.flush()
        photo_objects = []
        for idx, photo_id in enumerate(cat_ads_schema.photos):
            photo = Photo(
                photo_id=photo_id,
                sort_order=idx,
                is_primary=(idx == 0),
                cat_ad_id=cat_ads_object.id
            )
            photo_objects.append(photo)
        self.session.add_all(photo_objects)
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


    def get_media_message_from_dict(self, ad_message: dict, is_sorted=False):
        cat_ads_schema: CatAdsSchema = self.schema(**ad_message)
        return self.get_media_message_from_schema(cat_ads_schema, is_sorted=is_sorted)

    def get_media_message_from_schema(self, cat_ad_schema: CatAdsSchema, is_sorted=False):
        caption = cat_ad_schema.get_caption()
        photos_dict = cat_ad_schema.get_photos(is_sorted=is_sorted)
        return self.make_media_group(photos_dict, caption=caption)

    def make_media_group(self, photos: tuple, caption: str) -> t.Tuple[InputMediaPhoto, ...]:
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
        return tuple(media)
