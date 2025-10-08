from logging import getLogger
import typing as t
import json
from pathlib import Path
from typing import Final, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.sync import TelegramClient
from telethon.sessions import Session, StringSession

from utils.bot_utils import bot_send_message, get_confirm_code
from utils.decorators import async_timer
from database.blog.models import Tag, Post
from database.users.models import User, TelegramSession
from database.users.roles import UserRole
from database.db import get_db_session, get_db_session_directly
from config import settings

logger = getLogger(__name__)


class TeletonClientManager:
    def __init__(self):
        self.api_id: Final[int] = int(settings.TG_API_ID)
        self.api_hash: Final[str] = settings.TG_API_HASH
        self.phone: Final[str] = settings.TG_PHONE
        self.password: Final[str] = settings.TG_PASSWORD
        self.session_file: Path = Path('session_config.json')
        self._client: t.Optional[TelegramClient] = None
        self._session_name: str = 'tg_session_teletone'

    async def __call__(self):
        """Делаем фабрику callable для использования в middleware"""
        return await self.get_client()

    async def __aenter__(self) -> TelegramClient:
        return await self.get_client()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_client(self) -> TelegramClient:
        """Основной метод для получения клиента."""
        if self._client and self._client.is_connected():
            return self._client
        await self._initialize_client()
        return self._client

    async def close(self):
        if self._client:
            await self._client.disconnect()
            self._client = None

    async def _create_client(self, session_string) -> TelegramClient:
        """Создание клиента teletone"""
        if not self._client:
            self.client = TelegramClient(
                session=StringSession(session_string),
                api_id=self.api_id,
                api_hash=self.api_hash,
                system_version='Windows11',
                device_model='Asus',
                app_version=TelegramClient.__version__,
            )
        return self.client

    async def _load_session(self) -> Optional[str]:
        db_session = await get_db_session_directly()
        """Метод загрузки сессии"""
        try:
            async with db_session as db:
                tg_session: TelegramSession = await TelegramSession.one_or_none(name=settings.TELETONE_SESSION_NAME, session=db)
                return tg_session.hash
        except Exception as e:
            return None

    async def _save_session(self) -> bool:
        """Метод сохранения сесии"""
        db_session = await get_db_session_directly()
        try:
            tg_session_hash = self.client.session.save()
        except Exception as e:
            logger.error(f'Не удалось инициализировать сессию {e}', exc_info=True)
            return False
        try:
            async with db_session as db:
                await TelegramSession.create_or_update(session=db,
                    name=settings.TELETONE_SESSION_NAME, defaults={
                        'hash': tg_session_hash
                    }
                )
                await db.commit()
                logger.info('Новая сессия инициализирована и сохранена в базу.')
        except Exception as e:
            logger.error('Ошибка сохранения сессии в БД', exc_info=True)
        return True

    async def _initialize_client(self):
        """Внутренняя логика инициализации клиента."""
        # 1. Попытка загрузить существующую сессию
        session_string = await self._load_session()
        self._client = await self._create_client(session_string)
        # 2. Подключаемся
        await self._client.connect()
        # 3. Проверяем авторизацию
        if not await self._client.is_user_authorized():
            logger.info("Клиенту Telegram требуется аутентификация")
            await bot_send_message('Клиенту Telegram требуется аутентификация, введите код в консоли!')
            await self._client.start(phone=self.phone, password=self.password or None)
            await self._save_session() # Сохраняем новую сессию
        logger.info("Клиент Telegram успешно инициализирован и авторизован.")
