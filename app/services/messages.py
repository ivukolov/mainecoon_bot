import typing as t

import telethon.types as tt_types
import aiogram.types as aio_types
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient

from mappers import schemas
from utils.parsers import TextParser, TextCleaner
from config import settings
from database import Post, Tag, User
from mappers.telegram import TelegramMessageMapper
from utils.bot_utils import get_or_create_admin_user



class MessagesService:
    """Сервис для добавления сообщений в базу"""
    def __init__(
            self,
            session: AsyncSession,
            bot_user: t.Optional[User] = None,
            messages: t.Union[t.List[tt_types.Message], t.List[aio_types.Message]] = None,
            users: t.Optional[schemas.TelegramUserDTO] = None,
            is_aiogram: bool = True,
    ):
        self.session = session
        self.messages_dto: schemas.TelegramMessagesListDTO = self.__handle_message(
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

    async def service_and_save_messages(self) -> schemas.TelegramMessagesListDTO:
        """Основной метод парсинга и сохранения."""
        for text_message in self.messages_dto.messages:
            if text_message.text:
                await self.process_single_message(text_message)
        return self.messages_dto

    async def process_single_message(
            self,
            message: schemas.TelegramMessageDTO,
    ) -> None:
        title = TextParser.extract_title(
            message.text,
            settings.POST_TITLE_LENGTH
        )
        tag_objects = await self.make_tags_from_message(message.text)
        author = self.bot_user or await get_or_create_admin_user(self.session)
        post, _ = await Post.create_or_update(
            session=self.session,
            id=message.id,
            defaults={
                'title': title,
                'message': message.text,
                'date': message.date,
                'edit_date': message.edit_date,
                'views': message.metrics.views,
                'forwards': message.metrics.forwards,
                'tags': tag_objects,
                'author_id': author.id,
            }
        )