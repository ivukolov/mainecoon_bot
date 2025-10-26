import typing as t
from logging import getLogger

import telethon.types as tt_types
import aiogram.types as aio_types
from aiogram.enums.content_type import ContentType as aio_content_type
from pydantic import ValidationError

from database.users.roles import UserRole
from schemas import dto
from schemas.dto import TelegramUsersListDTO
from utils.identifiers import generate_uuid_from_str

logger = getLogger(__name__)

class TelegramMessageMapper:
    """Маппер для конвертации telethon.Message в DTO."""

    @staticmethod
    def __from_aiogram_message(message: aio_types.Message) -> t.Optional[dto.TelegramMessageDTO]:
        message_type = TelegramMessageMapper._get_aiogram_message_type(message)

        return dto.TelegramMessageDTO(
            id=message.message_id,
            text=message.text or message.caption,
            date=message.date,
            post_author=message.from_user,
            message_type=message_type,
            is_forwarded=message.forward_from is not None,
            is_reply=message.reply_to_message or message.reply_to_story is not None,
            raw_data=message.model_dump()
        )


    @staticmethod
    def __from_telethon_message(message: tt_types.Message) -> t.Optional[dto.TelegramMessageDTO]:
        """Конвертирует telethon.Message в DTO."""

        # Определяем тип сообщения
        message_type = TelegramMessageMapper._get_teletone_message_type(message)

        # Собираем метрики
        metrics = dto.MessageMetrics(
            views=message.views,
            forwards=message.forwards,
            replies=message.replies and message.replies.replies
        )

        return dto.TelegramMessageDTO(
            id=message.id,
            text=message.message or None,
            date=message.date,
            edit_date=message.edit_date,
            metrics=metrics,
            post_author=message.post_author,
            message_type=message_type,
            is_forwarded=message.fwd_from is not None,
            is_reply=message.reply_to is not None,
            raw_data=message.to_dict()
        )

    @staticmethod
    def from_tg_messages(
            messages: t.Union[t.List[tt_types.Message], t.List[aio_types.Message]], is_aiogram=True
    ) -> dto.TelegramMessagesListDTO:
        dto_list = dto.TelegramMessagesListDTO()
        for message in messages:
            try:
                if is_aiogram:
                    dto_message = TelegramMessageMapper.__from_aiogram_message(message)
                else:
                    dto_message = TelegramMessageMapper.__from_telethon_message(message)

            except ValidationError as e:
                dto_list.handle_exceptions(e, message.id)
            except Exception as e:
                logger.error('Неизвестная ошибка формировани DTO', exc_info=True)
                dto_list.add_failed_message()
            else:
                dto_list.add_message(dto_message)
        return dto_list

    @staticmethod
    def _get_aiogram_message_type(message: aio_types.Message) -> dto.MessageType:
        """Определяет тип сообщения."""
        message_content_type = message.content_type
        if message_content_type == aio_content_type.TEXT:
            return dto.MessageType.TEXT
        if message_content_type == aio_content_type.VIDEO:
            return dto.MessageType.VIDEO
        if message_content_type == aio_content_type.AUDIO or aio_content_type.VOICE:
            return dto.MessageType.VOICE
        if message_content_type == aio_content_type.ANIMATION:
            return dto.MessageType.ANIMATION
        return dto.MessageType.TEXT



    @staticmethod
    def _get_teletone_message_type(message: tt_types.Message) -> dto.MessageType:
        """Определяет тип сообщения."""
        if not message.media:
            return dto.MessageType.TEXT

        if isinstance(message.media, tt_types.MessageMediaPhoto):
            return dto.MessageType.PHOTO
        elif isinstance(message.media, tt_types.MessageMediaDocument):
            # Детализируем по mime_type
            doc = message.media.document
            mime_type = getattr(doc, 'mime_type', '')

            if 'video' in mime_type:
                return dto.MessageType.VIDEO
            elif 'audio' in mime_type or 'voice' in mime_type:
                return dto.MessageType.VOICE
            else:
                return dto.MessageType.DOCUMENT

        return dto.MessageType.TEXT


class TelegramUserMapper:
    """Маппер для конвертации telethon User в DTO."""

    @staticmethod
    def get_user_from_telethon_raw_data(
            entity: tt_types.User
    ) -> dto.TelegramUserDTO:
        """Конвертирует telethon сущность в DTO."""

        user_type = TelegramUserMapper._get_entity_type(entity)
        username = entity.username or generate_uuid_from_str(name=str(entity.id))
        return dto.TelegramUserDTO(
            id=entity.id,
            username=username,
            first_name=getattr(entity, 'first_name', None),
            last_name=getattr(entity, 'last_name', None),
            contact=getattr(entity, 'contact', None),
            mutual_contact=getattr(entity, 'mutual_contact', None),
            phone=getattr(entity, 'phone', None),
            access_hash=getattr(entity, 'access_hash', None),
            role=user_type,
            is_premium=getattr(entity, 'premium', False),
            is_active=True,
        )

    @staticmethod
    def get_users_from_telethon_raw_data(entity_list: t.List[tt_types.User]):
        users_list_dto = TelegramUsersListDTO()
        for entity in entity_list:
            dto = TelegramUserMapper.get_user_from_telethon_raw_data(entity)
            users_list_dto.add_user(dto)
        return users_list_dto


    @staticmethod
    def _get_entity_type(entity) -> UserRole:
        """Определяет тип сущности."""
        return UserRole.BOT if getattr(entity, 'bot', True) else UserRole.USER
