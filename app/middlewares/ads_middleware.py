import logging

from aiogram import Bot
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.ads import CatAdsService
from utils.cache import RedisCache

logger = logging.getLogger(__name__)

class CatAdsServiceMiddleware(BaseMiddleware):
    def __init__(self, cache_storage: RedisCache, bot: Bot):
        self.cache_storage = cache_storage
        self.bot=bot

    async def __call__(
        self,
        handler,
        event,
        data
    ):
        session = data.get('db')
        data['cat_ads_service'] = CatAdsService(session=session, cache_storage=self.cache_storage, bot=self.bot)
        return await handler(event, data)