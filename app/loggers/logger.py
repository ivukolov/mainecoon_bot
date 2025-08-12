import asyncio
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Tuple

from app.config import settings

class BotLogger:
    def __init__(
        self,
        name: str = __name__,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(settings.LOG_LEVEL)
        self.formatter = logging.Formatter(
            fmt=settings.LOG_FORMATTER.get('fmt'),
            datefmt=settings.LOG_FORMATTER.get('datefmt')
        )


    def manage_handlers(self, handlers: Tuple):
        """Функция добавления кастомных хэндлеров в проект."""
        for handler in handlers:
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        """Получить настроенный логгер"""
        return self.logger
