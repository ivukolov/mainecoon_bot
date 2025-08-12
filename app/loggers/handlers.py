import asyncio
import logging
from logging.handlers import RotatingFileHandler

from app.config import settings


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
            for admin_id in settings.ADMINS:
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


def file_handler() -> RotatingFileHandler :
    """Настройка файлового логгера с ротацией"""
    settings.LOG_FILE.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding=settings.ENCODING
    )
    return file_handler
