import logging
from typing import Final
from enum import Enum
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DEBUG: Final[bool] = os.getenv("DEBUG", False) == True
    # Telegram.
    BOT_TOKEN: Final[str]  = os.getenv("BOT_TOKEN")
    ADMINS: Final[tuple] = tuple(os.getenv("ADMIN").split(","))
    CHANNEL_ID: Final[str] = os.getenv("CHANNEL_ID")
    GROUP_ID: Final[str] = os.getenv("GROUP_ID")
    # Postgres.
    POSTGRES_HOST: Final[str] = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: Final[str] = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: Final[str] = os.getenv("POSTGRES_DB")
    POSTGRES_USER: Final[str] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD")
    # Redis.
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: Final[str] = os.getenv("REDIS_PORT")
    # Pyment.
    YOOKASSA_SHOP_ID: Final[str ]= os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: Final[str] = os.getenv("YOOKASSA_SECRET_KEY")
    # Folders.
    ROOT_DIR = Path(__file__).resolve()
    # Logs
    LOG_LEVEL: Final[str] = logging.INFO
    LOGS_DIR: Final[Path] = ROOT_DIR / 'logs'
    LOG_FILE: Final[Path]= LOGS_DIR / 'bot.log'
    LOG_MAX_SIZE: Final[int] = 5 * 1024 * 1024 # Размер лога 5 мб.
    LOG_BACKUP_COUNT: Final[int] = 3 # Количество итераций лога.
    ENCODING: Final[str] = "utf-8"

