import logging
import logging.config
from logging import getLogger
import asyncio
import json
import logging
from pathlib import Path
from typing import Final, Optional, Union
import uuid

from telethon.sync import TelegramClient

from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Photo, Message
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from telethon.sessions import Session, StringSession


from app.config import settings

logger = getLogger(__name__)

api_id = int(settings.TG_API_ID)
api_hash = settings.TG_API_HASH
bot_token = settings.BOT_TOKEN
phone = '+79191828726'


class TeletonClient:
    def __init__(self):
        self.api_id: Final[int] = int(settings.TG_API_ID)
        self.api_hash: Final[str] = settings.TG_API_HASH
        self.phone: Final[str] = settings.TG_PHONE
        self.session: Optional[str] = None
        self.session_name: str = self.gen_session_name()
        self.session_file: Path = Path('session_config.json')
        self.client: Optional[TelegramClient] = None
        self.is_connected: bool = False

    def __call__(self):
        """Делаем фабрику callable для использования в middleware"""
        return self.get_client()

    async def close(self):
        """Закрывает все соединения"""
        if self.client:
            await self.client.disconnect()
            self.client = None

    async def get_client(self) -> TelegramClient:
        """Получает клиент (создает если нужно)"""
        if self.client is None or not self.is_connected:
            await self.start_client()
        return self.client

    def gen_session_name(self) -> uuid:
        """Создание имени сессии"""
        return 'tg_session_teletone'

    async def _load_session(self) -> Optional[str]:
        """Метод загрузки сессии"""
        try:
            with open('teletone_session.json', 'r') as f:
                data = json.load(f)
                self.session = data[self.session_name]
                return data[self.session_name]
        except Exception as e:
            return None

    async def make_client(self,) -> TelegramClient:
        """Инициализация новой сессии или загрузка старой"""
        if not self.client:
            self.client = TelegramClient(
                session=StringSession(self.session),
                api_id=self.api_id,
                api_hash=self.api_hash,
                system_version='Windows11',
                device_model='Asus',
                app_version=TelegramClient.__version__,
            )
        return self.client

    async def connection_check(self) -> bool:
        """Метод Проверки сессии"""
        await self._load_session()
        try:
            await self.make_client()
            await self.client.connect()
        except ConnectionRefusedError:
            logger.error(
                'Соединение разорвано. Попробуйте чуть позже.',
                exc_info=True
            )
            self.is_connected = False
            return self.is_connected
        if await self.client.is_user_authorized():
            logger.info('Сессия Валидна!')
            print("✅ Сессия валидна")
            self.is_connected = True
            return self.is_connected
        logger.error('Сессия не авторизированна')
        print("❌ Сессия не авторизована")
        self.is_connected = False
        return self.is_connected

    async def make_session(self) -> Optional[str]:
        """Метод поднятия сессии или создания новой!"""
        if not self.is_connected:
            logger.info('Создание новой сессии')
            self.session_name = self.gen_session_name()
            await self.make_client()
            await self.client.start(phone=self.phone)
            logger.info('Сессия создана')
            is_created: bool = await self._save_session()
            if not is_created:
                logger.warning('Ошибка сохранения сессии!')
            # Повторная проверка валидности сессии:
            return await self.connection_check()
        logger.info('Запускается клиент')
        await self.client.start()
        return await self.connection_check()

    async def start_client(self) -> bool:
        # Загрузка сохранённой сесии.
        await self._load_session()
        # Создаём клиента
        await self.make_client()
        # Проверка валидности сессии
        await self.connection_check()
        return await self.make_session()

    async def _save_session(self) -> bool:
        """Метод сохранения сесии"""
        try:
            session_data = {
                self.session_name: self.client.session.save()
            }
        except Exception:
            logger.error('Не удалось инициализировать сессию', exc_info=True)
            return False
        try:
            with open('teletone_session.json', 'w') as f:
                json.dump(session_data, f)
            self.session = session_data[self.session_name]
        except Exception:
            logger.error('Не удалось сохранить json файл сессии', exc_info=True)
            return False
        return True


async def get_media_form_message(message):
    page = 1
    page_size = 2
    offset = (page - 1) * page_size
    parsed_data = tuple
    if message.photo:
        print(message.photo)
    if message.document:
        print('Документ')
        print(message.document.mime_type)
    if message.video:
        print('Видео')
        print(message.video.mime_type)
    print(message.text)
    return False

# async def parse_messages(messages: list[Message,]):
#     for message in messages:

