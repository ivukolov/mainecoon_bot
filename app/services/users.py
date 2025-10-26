import typing as t

import telethon.types as tt_types
import aiogram.types as aio_types
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.dto import TelegramUserDTO
from config import settings
from database import User
from mappers.telegram import TelegramUserMapper

from utils.bot_utils import get_moderator_id_from_pool


class UsersService:
    """Сервис для добавления сообщений в базу"""

    def __init__(
            self,
            session: AsyncSession,
            users: t.List[TelegramUserDTO],
    ):
        self.session = session
        self.users = self.__handle_users(users)

    def __handle_users(self, messages: t.List):
        return TelegramUserMapper.get_users_from_telethon_raw_data(messages)

    async def service_and_save_users(self):
        """Основной метод парсинга и сохранения."""
        dict_list = self.users.get_model_dump_list()
        exclude_fields = {'id', 'role'}
        await User.on_conflict_do_update(self.session, dict_list=dict_list, exclude_fields=exclude_fields)

