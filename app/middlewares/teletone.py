import logging
import typing

from aiogram.dispatcher.middlewares.base import BaseMiddleware

from utils.parsers import TeletonClient

logger = logging.getLogger(__name__)

class TeletonClientMiddleware(BaseMiddleware):
    """Оптимизированный middleware с предварительно созданной фабрикой сессий"""
    def __init__(self, teleton_client: TeletonClient):
        self.teleton_client = teleton_client  # Готовая фабрика сессий

    async def __call__(self, handler, event, data):
        client = await self.teleton_client()# 1 вызов фабрики
        client.parse_mode = 'html'
        data["teleton_client"] = client
        try:
            return await handler(event, data)
        except Exception:
            logger.error('Ошибка парсинга канала', exc_info=True)
            raise
        # finally:
        #     # Закрываем клиент после обработки
        #     await client.close()