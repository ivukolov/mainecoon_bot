import typing as t
from logging import getLogger

from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from database import User
from database.blog.models import CatAd, Photo
from schemas.ads import CatAdsSchema

logger = getLogger(__name__)


class CatAdsService:
    """Сервис для добавления сообщений в базу"""

    schema = CatAdsSchema
    model = CatAd

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session


    async def save_ad_message(self, ad_message: dict, author: User):
        cat_ads_schema: CatAdsSchema = self.schema(**ad_message)
        cat_ads_dict = cat_ads_schema.model_dump(mode='python',exclude={'photos', 'photo_id'})
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

    # def handle_ad_telegram_message(self, tg_message: Message, form_text: dict):
    #     photos = [photo.file_id for photo in tg_message.photo]
    #     return self.make_ad_message(form_text, photos)
    async def get_pending_moderation_ads(self):
        return await self.session.execute(
            sa.select(CatAd).where(
                CatAd.is_moderated == False,
                CatAd.is_publicated == False
            ).order_by(CatAd.created_at)
        ).scalars().all()

    def get_media_message(self, ad_message: dict):
        cat_ads_schema: CatAdsSchema = self.schema(**ad_message)
        caption = cat_ads_schema.get_caption()
        photos = cat_ads_schema.photos
        return self.make_media_group(photos, caption=caption)

    def make_media_group(self, photos: t.List, caption: str) -> t.List[InputMediaPhoto]:
        media = []
        for idx, photo in enumerate(photos):
            input_media = InputMediaPhoto(
                    media=photo,
            )
            if idx == 0:
                input_media.caption = caption
            media.append(input_media)
        return media







