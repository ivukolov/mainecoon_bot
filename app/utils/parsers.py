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
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import InputPeerChannel
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

    # def __enter__(self):
    #     """Вызывается при входе в контекст"""
    #     logger.info('получение клиента в рамках контекстного менеджера')
    #     return self.client  # Возвращаем объект для использования в with
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     """Вызывается при выходе из контекста"""
    #     logger.info('Клиент телетон отключен!')
    #     self.client.disconnect()
    #     # False - чтобы бросить исключение.
    #     return False

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

async def main():
    parser = TeletonClient()
    await parser.start_client()

if __name__ == '__main__':
    asyncio.run(main())



    # async def __load_session(self):
    #     """Автоматически загружает сессию если она есть"""
    #     try:
    #         if not self.session:
    #         with open(self.session_file, 'r') as f:
    #             data = json.load(f)
    #             client = TelegramClient(
    #                 StringSession(data['session_string']),
    #                 self.API_ID,
    #                 self.API_HASH
    #             )
    #             await client.start()
    #             return client

#     async def session_maker(self):
#
#
# async def pars_test():
#     all_messages = []
#     offset_id = 0
#     limit = 100
#     total_messages = 0
#     total_count_limit = 0
#
#     client = TelegramClient(StringSession(), api_id, api_hash)
#     try:
#         await client.start(phone=phone)
#
#         me = await client.get_me()
#         session_string = client.session.save()
#         with open('session.json', 'w') as f:
#             json.dump({'session_string': session_string}, f)
#         print(me.username)
#         target_group = -1001573169353
#         entity = await client.get_entity(target_group)
#         peer = InputPeerChannel(
#             channel_id=abs(entity.id),
#             access_hash=entity.access_hash
#         )
#         history = await client(
#             GetHistoryRequest(
#                 peer=peer,
#                 limit=10,
#                 offset_id=0,
#                 add_offset=0,
#                 max_id=0,
#                 min_id=0,
#                 hash=0,
#                 offset_date=None
#             )
#         )
#
#         # Обрабатываем сообщения
#         for message in history.messages:
#             if hasattr(message, 'message') and message.message:
#                 print(f"{message.date}: {message.message}")
#
#     except Exception as e:
#         print(f"Ошибка: {e}")
#     finally:
#         await client.disconnect()
#     # group_entity = await client.get_entity(settings.GROUP_ID)
#     # print(group_entity.id)
#     # peer = InputPeerChannel(
#     #     channel_id=target_group,  # Берем абсолютное значение
#     #     access_hash=group_entity.access_hash
#     # )
#
#
# if __name__ == '__main__':
#     asyncio.run(pars_test())
