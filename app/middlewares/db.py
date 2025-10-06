import logging

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Оптимизированный middleware с предварительно созданной фабрикой сессий"""
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        self.session_pool = session_pool  # Готовая фабрика сессий

    async def __call__(self, handler, event, data):
        async with self.session_pool() as session:  # 1 вызов фабрики
            try:
                data["db"] = session
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                data["db"] = session
                logger.error(f'Ошибка работы: {self.__class__.__name__}', exc_info=True)
                return await handler(event, data)