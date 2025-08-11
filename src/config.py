import logging
from enum import Enum
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DEBUG: bool = os.getenv("DEBUG",)
    # Telegram.
    BOT_TOKEN: str  = os.getenv("BOT_TOKEN")
    ADMINS: list = os.getenv("ADMIN").split(",")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID")
    GROUP_ID: str = os.getenv("GROUP_ID")
    # Postgres.
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    # Redis.
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: str = os.getenv("REDIS_PORT")
    # Pyment.
    YOOKASSA_SHOP_ID: str = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: str = os.getenv("YOOKASSA_SECRET_KEY")
    # Folders.
    ROOT_DIR = Path(__file__).resolve()
    # Logs
    LOG_LEVEL = logging.INFO
    LOGS_DIR = ROOT_DIR / 'logs'
    LOG_FILE = LOGS_DIR / 'bot.log'
    LOG_MAX_SIZE = 5 * 1024 * 1024 # Размер лога 5 мб.
    LOG_BACKUP_COUNT = 3 # Количество итераций лога.
    ENCODING = "utf-8"

