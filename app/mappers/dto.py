from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import typing as t


class UserType(Enum):
    """Тип пользователя Telegram."""
    BOT = "bot"
    USER = "user"
    CHANNEL = "channel"
    GROUP = "group"
    SUPERGROUP = "supergroup"

class UserStatus(Enum):
    """Статус пользователя Telegram."""
    ONLINE = "online"
    OFFLINE = "offline"
    RECENTLY = "recently"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"

class MessageType(Enum):
    """Тип сообщения Telegram."""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    STICKER = "sticker"
    POLL = "poll"
    ANIMATION = "animation"

@dataclass
class MessageMetrics:
    """Метрики сообщения."""
    views: t.Optional[int] = None
    forwards: t.Optional[int] = None
    replies: t.Optional[int] = None


@dataclass
class TelegramUserDTO:
    """DTO для представления пользователя/чата из Telegram."""

    # Основные идентификаторы
    id: int
    username: t.Optional[str] = None
    first_name: t.Optional[str] = None
    last_name: t.Optional[str] = None

    # Тип и статус
    user_type: UserType = UserType.USER
    status: t.Optional[UserStatus] = None
    is_premium: bool = False
    is_bot: bool = False

    # Контактная информация
    phone: t.Optional[str] = None
    lang_code: t.Optional[str] = None

    # Мета-информация
    last_online: t.Optional[datetime] = None

    # Для групп/каналов
    title: t.Optional[str] = None
    participants_count: t.Optional[int] = None
    description: t.Optional[str] = None

    # Дополнительные данные
    raw_data: t.Dict[str, t.Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """Возвращает отображаемое имя."""
        if self.title:
            return self.title
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User #{self.id}"

@dataclass
class TelegramMessageDTO:
    """DTO для представления сообщения из Telegram."""

    # Основные поля
    id: int
    text: t.Optional[str]
    date: datetime
    peer_id: t.Optional[int] = None # id чата telegram из которого отправленно сообщение
    post_author: t.Optional[str] = None

    # Статистика
    metrics: MessageMetrics = field(default_factory=MessageMetrics)
    edit_date: t.Optional[datetime] = None
    is_forwarded:t.Optional[bool] = None
    is_reply:t.Optional[bool] = None

    # Мета-информация
    message_type: MessageType = MessageType.TEXT

    # Дополнительные данные
    raw_data: t.Dict[str, t.Any] = field(default_factory=dict)
    entities: t.List[t.Dict[str, t.Any]] = field(default_factory=list)

    @property
    def is_edited(self) -> bool:
        return self.edit_date is not None

    @property
    def has_text(self) -> bool:
        return bool(self.text and self.text.strip())