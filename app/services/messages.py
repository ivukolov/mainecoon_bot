import typing as t

import telethon.types as tt_types
import aiogram.types as aio_types
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient

from schemas.dto import TelegramUserDTO, TelegramMessagesListDTO, TelegramMessageDTO
from utils.parsers import TextParser, TextCleaner
from config import settings
from database import Post, Tag, User
from database.blog.models import post_tags
from mappers.telegram import TelegramMessageMapper
from utils.bot_utils import get_or_create_admin_user

from utils.bot_utils import get_moderator_id_from_pool


class MessagesService:
    """Сервис для добавления сообщений в базу"""

    def __init__(
            self,
            session: AsyncSession,
            bot_user: t.Optional[User] = None,
            messages: t.Union[t.List[tt_types.Message], t.List[aio_types.Message]] = None,
            users: t.Optional[TelegramUserDTO] = None,
            is_aiogram: bool = True,
    ):
        self.session = session
        self.messages_dto: TelegramMessagesListDTO = self.__handle_message(
            messages, is_aiogram=is_aiogram
        )
        self.users = users
        self.bot_user = bot_user

    def __handle_message(self, messages: t.List, is_aiogram: bool):
        return TelegramMessageMapper.from_tg_messages(messages, is_aiogram=is_aiogram)

    async def make_tags_from_message(self, message: str) -> t.List[Tag]:
        post_tags = set()
        post_tags.update(TextParser.extract_tags(message))
        tag_objects: dict = await Tag.bulk_get_or_create_tags(session=self.session, tags=post_tags)
        return list(tag for tag in tag_objects.values())

    async def service_and_save_messages(self) -> TelegramMessagesListDTO:
        """Основной метод парсинга и сохранения."""
        dict_list = []
        tags_dict = {}
        for text_message in self.messages_dto.messages:
            if text_message.text:
                dict_message = await self.process_single_message(text_message)
                tags_dict[text_message.id] = dict_message.pop('tags')
                dict_list.append(dict_message)
        await Post.on_conflict_do_update(self.session, dict_list=dict_list)
        for post, tags in tags_dict.items():
            post_obj = await Post.one_or_none(session=self.session, id=post)
            post_obj.tags = tags
            self.session.add(post_obj)
        return self.messages_dto

    async def process_single_message(
            self,
            message: TelegramMessageDTO,
    ) -> dict:
        title = TextParser.extract_title(
            message.text,
            settings.POST_TITLE_LENGTH
        )
        tag_objects = await self.make_tags_from_message(message.text)
        moderator_id = await get_moderator_id_from_pool(self.session)
        return {
            'id': message.id,
            'title': title,
            'message': message.text,
            'date': message.date,
            'edit_date': message.edit_date,
            'views': message.metrics.views,
            'forwards': message.metrics.forwards,
            'tags': tag_objects,
            'author_id': moderator_id,
        }
