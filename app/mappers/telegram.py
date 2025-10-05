import typing as t
from logging import getLogger

import telethon.types as tt_types
import aiogram.types as aio_types
from aiogram.enums.content_type import ContentType as aio_content_type
from pydantic import ValidationError

from mappers import schemas

logger = getLogger(__name__)

class TelegramMessageMapper:
    """Маппер для конвертации telethon.Message в DTO."""

    @staticmethod
    def __from_aiogram_message(message: aio_types.Message) -> t.Optional[schemas.TelegramMessageDTO]:
        message_type = TelegramMessageMapper._get_aiogram_message_type(message)

        return schemas.TelegramMessageDTO(
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
    def __from_telethon_message(message: tt_types.Message) -> t.Optional[schemas.TelegramMessageDTO]:
        """Конвертирует telethon.Message в DTO."""

        # Определяем тип сообщения
        message_type = TelegramMessageMapper._get_teletone_message_type(message)

        # Собираем метрики
        metrics = schemas.MessageMetrics(
            views=message.views,
            forwards=message.forwards,
            replies=message.replies and message.replies.replies
        )

        return schemas.TelegramMessageDTO(
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
    ) -> schemas.TelegramMessagesListDTO:
        dto_list = schemas.TelegramMessagesListDTO()
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
    def _get_aiogram_message_type(message: aio_types.Message) -> schemas.MessageType:
        """Определяет тип сообщения."""
        message_content_type = message.content_type
        if message_content_type == aio_content_type.TEXT:
            return schemas.MessageType.TEXT
        if message_content_type == aio_content_type.VIDEO:
            return schemas.MessageType.VIDEO
        if message_content_type == aio_content_type.AUDIO or aio_content_type.VOICE:
            return schemas.MessageType.VOICE
        if message_content_type == aio_content_type.ANIMATION:
            return schemas.MessageType.ANIMATION
        return schemas.MessageType.TEXT



    @staticmethod
    def _get_teletone_message_type(message: tt_types.Message) -> schemas.MessageType:
        """Определяет тип сообщения."""
        if not message.media:
            return schemas.MessageType.TEXT

        if isinstance(message.media, tt_types.MessageMediaPhoto):
            return schemas.MessageType.PHOTO
        elif isinstance(message.media, tt_types.MessageMediaDocument):
            # Детализируем по mime_type
            doc = message.media.document
            mime_type = getattr(doc, 'mime_type', '')

            if 'video' in mime_type:
                return schemas.MessageType.VIDEO
            elif 'audio' in mime_type or 'voice' in mime_type:
                return schemas.MessageType.VOICE
            else:
                return schemas.MessageType.DOCUMENT

        return schemas.MessageType.TEXT


class TelegramUserMapper:
    """Маппер для конвертации telethon User/Chat в DTO."""

    @staticmethod
    def from_telethon_raw_data(
            entity: t.Union[tt_types.User, tt_types.Chat, tt_types.Channel]
    ) -> schemas.TelegramUserDTO:
        """Конвертирует telethon сущность в DTO."""

        user_type = TelegramUserMapper._get_entity_type(entity)

        return schemas.TelegramUserDTO(
            id=entity.id,
            username=getattr(entity, 'username', None),
            first_name=getattr(entity, 'first_name', None),
            last_name=getattr(entity, 'last_name', None),
            user_type=user_type,
            is_bot=getattr(entity, 'bot', False),
            is_premium=getattr(entity, 'premium', False),
            phone=getattr(entity, 'phone', None),
            lang_code=getattr(entity, 'lang_code', None),
            title=getattr(entity, 'title', None),
            participants_count=getattr(entity, 'participants_count', None),
            description=getattr(entity, 'about', None),
            raw_data=entity.to_dict() if hasattr(entity, 'to_dict') else {}
        )

    @staticmethod
    def _get_entity_type(entity) -> schemas.UserType:
        """Определяет тип сущности."""
        if isinstance(entity, tt_types.User):
            return schemas.UserType.BOT if getattr(entity, 'bot', False) else schemas.UserType.USER
        elif isinstance(entity, tt_types.Channel):
            return schemas.UserType.SUPERGROUP if getattr(entity, 'megagroup', False) else schemas.UserType.CHANNEL
        elif isinstance(entity, tt_types.Chat):
            return schemas.UserType.GROUP
        return schemas.UserType.USER