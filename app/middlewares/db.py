import logging
from abc import ABC

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from contextlib import asynccontextmanager
from app.database.db import get_db

logger = logging.getLogger(__name__)


class SafeDatabaseMiddleware(BaseMiddleware, ABC):
    def __init__(self):
        super().__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        try:
            data['db'] = next(get_db())
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            data['db'] = None

    async def on_post_process_message(self, message: types.Message, results, data: dict):
        if 'db' in data and data['db'] is not None:
            try:
                data['db'].close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

    async def on_process_error(self, update: types.Update, error: Exception, data: dict):
        if 'db' in data and data['db'] is not None:
            try:
                data['db'].rollback()
                data['db'].close()
            except Exception as e:
                logger.error(f"Error during error handling: {e}")