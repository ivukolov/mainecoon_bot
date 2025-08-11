from enum import Enum
import os
from pathlib import Path


class Settings(Enum):
    # Telegram.
    BOT_TOKEN: str  = os.getenv("BOT_TOKEN")
    ADMIN_IDS: list = os.getenv("ADMIN_IDS").split(",")
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
    ROOT_DIR = Path(__file__).resolve().parent
