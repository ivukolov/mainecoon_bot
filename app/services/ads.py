import typing as t

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.orm as orm
import sqlalchemy as sa

from config import settings
from database.blog.models import AdType, Ad



class CatAdsService:
    """Сервис для добавления сообщений в базу"""
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.slug = ''

    async def handle_ad_message(self, message: dict[str, t.Any]) -> None:
        cat_ad: Ad = Ad(
            author_id=message['author_id'],
        )