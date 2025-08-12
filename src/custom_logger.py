import asyncio
import logging
from logging.handlers import RotatingFileHandler
from typing import List

from config import Settings


class TelegramHandler(logging.Handler):
    """Отправка логов администратору тг канала."""
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def emit(self, record):
        if record.levelno >= self.level:
            error_msg = (
                f"🚨 <b>{record.levelname}</b>\n\n"
                f"• <b>Сообщение</b>: {record.getMessage()}\n"
                f"• <b>Модуль</b>: {record.pathname}:{record.lineno}\n"
                f"• <b>Время</b>: {self.format(record.created)}"
            )
            for admin_id in Settings.ADMINS:
                try:
                    asyncio.create_task(
                        self.bot.send_message(
                            admin_id,
                            error_msg,
                            parse_mode="HTML"
                        )
                    )
                except Exception as e:
                    logging.error(f"Ошибка отправки лога в Telegram: {e}")

class BotLogger:
    def __init__(
        self,
        name: str = __name__,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(Settings.LOG_LEVEL)
        self.formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.log_dir = Settings.LOG_DIR


    def manage_handlers(self, handlers: List[logging.Handler]):
        """Функция добавления кастомных хэндлеров в проект."""
        for handler in handlers:
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)

    def file_handler(self) -> RotatingFileHandler :
        """Настройка файлового логгера с ротацией"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=Settings.LOG_FILE,
            maxBytes=Settings.LOG_MAX_SIZE,
            backupCount=Settings.LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        return file_handler

    def get_logger(self) -> logging.Logger:
        """Получить настроенный логгер"""
        return self.logger



