import logging
from abc import ABC

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Оптимизированный middleware с предварительно созданной фабрикой сессий"""
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        self.session_pool = session_pool  # Готовая фабрика сессий

    async def __call__(self, handler, event, data):
        async with self.session_pool() as session:  # 1 вызов фабрики
            data["db"] = session
            try:
                return await handler(event, data)
            except Exception:
                await session.rollback()
                logger.error('Ошибка взаимодействия с базой данных', exc_info=True)
                raise