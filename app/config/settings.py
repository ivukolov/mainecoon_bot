import logging
from typing import Final
from enum import Enum
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)


DEBUG: Final[bool] = os.getenv("DEBUG", False) == True
# Telegram.
BOT_TOKEN: Final[str]  = os.getenv("BOT_TOKEN",)
ADMINS: Final[tuple] = tuple(os.getenv("ADMIN", ', ').split(","))
CHANNEL_ID: Final[str] = os.getenv("CHANNEL_ID")
GROUP_ID: Final[str] = os.getenv("GROUP_ID")
# Postgres.
POSTGRES_HOST: Final[str] = os.getenv("POSTGRES_HOST")
POSTGRES_PORT: Final[str] = os.getenv("POSTGRES_PORT")
POSTGRES_DB: Final[str] = os.getenv("POSTGRES_DB")
POSTGRES_USER: Final[str] = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD")
# Redis.
REDIS_HOST: Final[str] = '127.0.0.1'#os.getenv("REDIS_HOST")
REDIS_PORT: Final[str] = os.getenv("REDIS_PORT")
REDIS_STORAGE: Final[str] = f"redis://{REDIS_HOST}:{REDIS_PORT}"
# Pyment.
YOOKASSA_SHOP_ID: Final[str ]= os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY: Final[str] = os.getenv("YOOKASSA_SECRET_KEY")
# Folders.
ROOT_DIR: Final[Path] = Path(__file__).resolve().parent.parent
# Logs
LOGS_DIR: Final[Path] = ROOT_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_MAX_SIZE: Final[int] = 5 * 1024 * 1024 # Размер лога 5 мб.
LOG_BACKUP_COUNT: Final[int] = 3 # Количество итераций лога.
ENCODING: Final[str] = "utf-8"
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
        },
        'simple': {
            'format': '%(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
        'file_info': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'info.log'),
            'formatter': 'standard',
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
            'encoding': ENCODING,
            'mode': 'a'
        },
    },
    # Список модулей проекта, для детальной настройки.
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file_debug'],
            'level': 'INFO',
        },
        'handlers': {
            'handlers': ['console', 'file_error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'config': {
            'handlers': ['console', 'file_error'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
