import typing as t
import telethon.types as tt_types

from .dto import TelegramMessageDTO, TelegramUserDTO, MessageType, MessageMetrics


class TelegramMessageMapper:
    """Маппер для конвертации telethon.Message в DTO."""

    @staticmethod
    def from_telethon(message: tt_types.Message) -> TelegramMessageDTO:
        """Конвертирует telethon.Message в DTO."""

        # Определяем тип сообщения
        message_type = TelegramMessageMapper._get_message_type(message)

        # Собираем метрики
        metrics = MessageMetrics(
            views=message.views,
            forwards=message.forwards,
            replies=message.replies and message.replies.replies
        )

        return TelegramMessageDTO(
            id=message.id,
            text=message.message,
            date=message.date,
            edit_date=message.edit_date,
            metrics=metrics,
            post_author=message.post_author,
            message_type=message_type,
            is_forwarded=message.fwd_from is not None,
            is_reply=message.reply_to is not None,
            entities=message.entities or [],
            raw_data=message.to_dict()  # сохраняем сырые данные на всякий случай
        )

    @staticmethod
    def _get_message_type(message: tt_types.Message) -> MessageType:
        """Определяет тип сообщения."""
        if not message.media:
            return MessageType.TEXT

        if isinstance(message.media, tt_types.MessageMediaPhoto):
            return MessageType.PHOTO
        elif isinstance(message.media, tt_types.MessageMediaDocument):
            # Можно детализировать по mime_type
            doc = message.media.document
            mime_type = getattr(doc, 'mime_type', '')

            if 'video' in mime_type:
                return MessageType.VIDEO
            elif 'audio' in mime_type or 'voice' in mime_type:
                return MessageType.VOICE
            else:
                return MessageType.DOCUMENT

        return MessageType.TEXT