import logging
from passlib.context import CryptContext
from typing import Final
from enum import Enum
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

DEBUG: Final[bool] = os.getenv("DEBUG", False) == True
ENCODING: Final[str] = "utf-8" # Кодировка в проекте.
ROOT_DIR: Final[Path] = Path(__file__).resolve().parent.parent

# Telegram.
## ПАРАМЕТРЫ АДМИНИСТРАТОРА КАНАЛА
ADMIN_ID: Final[int] = int(os.getenv("ADMIN_ID"))
ADMIN_USERNAME: Final[str] = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD: Final[str] = os.getenv("ADMIN_PASSWORD")
# BOT_ID = 7714336436
# BOT_FIRST_NAME = "Кото-Вет Помощник"
# BOT_USERNAME = 'CatVetHelperBot'
# BOT_INFO = 'Главный трудяга канала'
## Бот
PARTNERS_TAG: Final[str] = '#Партнёры'
BOT_TOKEN: Final[str]  = os.getenv("BOT_TOKEN",) # Токен бота, получается у @botfather
CHANNEL_ID: Final[int] = -1001573169353 #os.getenv("CHANNEL_ID")

# Teletone
TG_API_ID: Final[str] = os.getenv("TG_API_ID")
TG_API_HASH: Final[str] = os.getenv("TG_API_HASH")
TG_PHONE: Final[str] = os.getenv("TG_PHONE")
TG_PASSWORD : Final[str] = os.getenv("TG_PASSWORD")
TELETONE_SESSION_NAME: Final[str] = 'tg_session_teletone'
PARSE_MODE: Final[str] = 'html'
TG_SESSION_RECREATE_TIMEOUT: Final[int] = 3 # Время для перезапуска сессии в случае обрыва секунды

#ADMIN PANEL
PROJECT_NAME: Final[str] = 'Кото-Вет помощник' # Используется для имени web админки интерфейса
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
FAST_API_SECRET_KEY: Final[str] = os.getenv("FAST_API_SECRET_KEY")
## JWT
COMPANY_NAME="Кото-ВетПросвет"
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_HOURS: int = 720
# DB.
## Postgres.
POSTGRES_HOST: Final[str] = os.getenv("POSTGRES_HOST")
POSTGRES_PORT: Final[str] = os.getenv("POSTGRES_PORT")
POSTGRES_DB: Final[str] = os.getenv("POSTGRES_DB")
POSTGRES_USER: Final[str] = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD")
# ENGINE.
# "sqlite+aiosqlite:///./bot.db"
DB_ENGINE =f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
# Models
# User
USERNAME_LENGTH: Final[int] = 100
USER_INFO_LENGTH: Final[int] = 100
USER_FIRST_NAME_LENGTH: Final[int] = 100
USER_LAST_NAME_LENGTH: Final[int] = 100
USER_PASSWORD_HASH_LENGTH: Final[int] = 255
LANG_CODE_LENGTH: Final[int] = 10
PHONE_LENGTH: Final[int] = 25
# Tag
TAG_NAME_LENGTH: Final[int] = 30
TAG_EMOJI_LENGTH: Final[int] = 14
# Post
POST_TITLE_LENGTH: Final[int] = 100
# ADS
DONATION_AMOUNT = 150 # Сумма доната в рублях для размещения рекламы
USERS_CNT = 15 # Количество приглашенных людей для размещения рекламы

# Redis.
REDIS_HOST: Final[str] = os.getenv("REDIS_HOST")
REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT"))
REDIS_STORAGE: Final[str] = f"redis://{REDIS_HOST}:{REDIS_PORT}"
# Pyment.
YOOKASSA_SHOP_ID: Final[str ]= os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY: Final[str] = os.getenv("YOOKASSA_SECRET_KEY")
# Media
MEDIA: Final[str] = "media"
MEDIA_ROOT: Final[Path] = ROOT_DIR / MEDIA
IMAGES: Final[str] = "images"
IMAGES_ROOT: Final[Path] = MEDIA_ROOT / IMAGES
VIDEOS: Final[str] = "videos"
VIDEOS_ROOT: Final[Path] = MEDIA_ROOT / VIDEOS
# Logs
LOGS_DIR: Final[Path] = ROOT_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_MAX_SIZE: Final[int] = 5 * 1024 * 1024 # Размер лога 5 мб.
LOG_BACKUP_COUNT: Final[int] = 3 # Количество итераций лога.
LOG_ENCODING: Final[str] = "utf-8"
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(levelname)s: %(asctime)s %(name)s %(funcName)s %(lineno)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'INFO',
        },
        'file_info': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'info.log'),
            'formatter': 'detailed',
            'level': 'INFO',
        },
        'file_debug': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'debug.log'),
            'formatter': 'detailed',
            'level': 'DEBUG',
        },
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'formatter': 'detailed',
            'level': 'ERROR',
            'maxBytes': LOG_MAX_SIZE,  # 10 MB
            'backupCount': LOG_BACKUP_COUNT,
            'encoding': LOG_ENCODING,
            'mode': 'a'
        },
    },
    # Список модулей проекта, для детальной настройки.
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file_error', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'handlers': {
            'handlers': ['console', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'aiogram.router': {
            'handlers': ['console', 'file_debug'],
            'level': 'ERROR',
            'propagate': False,
        },
        'utils': {
            'handlers': ['console', 'file_debug'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}
