import logging

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.ads import CatAdsService

logger = logging.getLogger(__name__)

class CatAdsServiceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event,
        data
    ):
        session = data.get('db')
        data['cat_ads_service'] = CatAdsService(session=session)
        return await handler(event, data)