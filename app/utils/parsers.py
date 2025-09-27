import logging
import logging.config
from logging import getLogger
import typing as t
import re
import json
import logging
from pathlib import Path
from pprint import pprint
from typing import Final, Optional, Union
import uuid
from html import escape

from sqlalchemy import select
from sqlalchemy.orm import selectinload

if t.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from aiogram import types as aio_types

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl import types as tt_types
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from telethon.sessions import Session, StringSession

from utils.decorators import async_timer
from database.blog.models import Tag, Post
from database.users.models import User
from database.users.roles import UserRole
from database.db import get_db_session
from config import settings

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


class MessagesParser:
    def __init__(self, messages, session):
        self.session: t.Optional['AsyncSession'] = session
        self.messages: t.List[tt_types.Message] = messages
        self.all_tags: t.Set[str] | None = None
        self.bot_user: t.Optional['User'] = None

    async def __aenter__(self):
        """Async context manager для управления сессией"""
        self.session = await get_db_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрываем сессию при выходе"""
        if self.session:
            await self.session.close()

    async def get_or_create_bot_user(self):
        user, created = await User.get_or_create(self.session, id=1, defaults={
            'role': UserRole.BOT.value,
            'username': 'mainecoon_bot',
            'first_name': 'Дымок',
            'last_name': 'Колбаскин'
        })
        self.bot_user = user
        return user

    @async_timer
    async def parse_messages(self, full=True):
        """Обрабаотываем сообщения из группы"""
        await self.get_or_create_bot_user()
        for message in self.messages:
            if message.message:
                tags = await self.get_tags_from_message(message.message)
                tags_obs: list = []
                for tag in tags:
                    tag_obj = await self.check_or_create_tag(tag)
                    tags_obs.append(tag_obj)
                if full:
                    await self.create_or_update_posts(message, tags_obs)

    # async def get_all_tags(self):
    #     stmt = select(Tag.name)
    #     self.all_tags = set(await self.session.scalars(stmt))

    async def get_tags_from_message(self, text: str) -> set:
        pattern = r'#[\w\u0400-\u04FF]+'
        return set(re.findall(pattern, text, re.UNICODE))

    async def get_title(self, text: str) -> str:
        points = {'\n', '?', '!', '.',}
        for idx, char in enumerate(text):
            if char in points:
                return await self.remove_emojis(text[:idx+1])
        return await self.remove_emojis(text)


        # split_message = text.split('\n')
        # title = split_message[0].split('.')
        # return await self.remove_emojis(title[0])

    async def remove_emojis(self, text):
    # Паттерн для поиска эмодзи
        emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # эмоции
                               u"\U0001F300-\U0001F5FF"  # символы и пиктограммы
                               u"\U0001F680-\U0001F6FF"  # транспорт и карты
                               u"\U0001F1E0-\U0001F1FF"  # флаги стран
                               u"\U00002500-\U00002BEF"  # китайские иероглифы
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642" 
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # вариационный селектор-16
                               u"\u3030"
                               "]+", flags=re.UNICODE)

        text = emoji_pattern.sub(r'', text)
        return re.sub(r'\s+', ' ', text).strip()


    async def check_or_create_tag(self, tag: str):
        """Проверяет наличие тэга. Если его нет, то создаёт новый."""
        tag, created = await Tag.get_or_create(self.session, name=tag)
        return tag


    async def create_or_update_posts(self, obj: tt_types.Message, tags):
        title = await self.get_title(obj.message[:settings.POST_TITLE_LENGTH])
        post, updated = await Post.create_or_update(
            session=self.session, id=obj.id,
            defaults={
                'title': title,
                'message': obj.message,
                'date': obj.date,
                'edit_date': obj.edit_date,
                'views': obj.views,
                'forwards': obj.forwards,
                'tags': tags,
                'author_id': self.bot_user.id,
            }
        )
        post.author_id = self.bot_user.id
        if not updated:
            post.author_id = self.bot_user.id
        return await self.session.commit()

