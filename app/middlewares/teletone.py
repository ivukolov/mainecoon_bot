import logging
import typing

from aiogram.dispatcher.middlewares.base import BaseMiddleware

from clients.teletone import TeletonClientManager as TeletonClient
from config import settings

logger = logging.getLogger(__name__)

class TeletonClientMiddleware(BaseMiddleware):
    """Оптимизированный middleware с предварительно созданной фабрикой сессий"""
    def __init__(self, teleton_client: TeletonClient):
        self.teleton_client = teleton_client  # Готовая фабрика сессий

    async def __call__(self, handler, event, data):
        try:
            client = self.teleton_client# 1 вызов фабрики
            client.parse_mode = settings.PARSE_MODE
            data["teleton_client"] = client
            return await handler(event, data)
        except Exception:
            logger.error(f"Ошибка работы {self.__class__.__name__}", exc_info=True)
            return await handler(event, data)
