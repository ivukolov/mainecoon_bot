from logging import getLogger

from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from typing import Optional, Dict, Any, List, Set, Tuple
from enum import Enum

logger = getLogger(__name__)

class UserType(str, Enum):
    """Тип пользователя Telegram."""
    BOT = "bot"
    USER = "user"
    CHANNEL = "channel"
    GROUP = "group"
    SUPERGROUP = "supergroup"

class UserStatus(str, Enum):
    """Статус пользователя Telegram."""
    ONLINE = "online"
    OFFLINE = "offline"
    RECENTLY = "recently"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"

class MessageType(str, Enum):
    """Тип сообщения Telegram."""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    STICKER = "sticker"
    POLL = "poll"
    ANIMATION = "animation"

class MessageMetrics(BaseModel):
    """Метрики сообщения."""
    views: Optional[int] = None
    forwards: Optional[int] = None
    replies: Optional[int] = None

class TelegramUserDTO(BaseModel):
    """DTO для представления пользователя/чата из Telegram."""

    # Основные идентификаторы
    id: int
    username: Optional[str] = Field(default=None, description="Логин")
    first_name: Optional[str] = Field(default=None, description="Имя")
    last_name: Optional[str] = Field(default=None, description="Фамилия")

    # Тип и статус
    user_type: UserType = Field(default=UserType.USER, description="Тип сообщения")
    status: Optional[UserStatus] = Field(default=None, description="Статус пользователя")
    is_premium: bool = Field(default=False, description="Подписка на телеграмм преимум")
    is_bot: bool = Field(default=False, description="Является ли пользователь ботом")

    # Контактная информация
    phone: Optional[str] = Field(default=None, description="Номер телефона")
    lang_code: Optional[str] = Field(default=None, description="Языковой код")

    # Мета-информация
    last_online: Optional[datetime] = Field(default=None, description="Заходил последний раз")

    # Для групп/каналов
    title: Optional[str] = Field(default=None, description="Название группы")
    participants_count: Optional[int] = Field(default=None, description="Количество подписчиков")
    description: Optional[str] = Field(default=None, description="Описание группы")

    # Дополнительные данные
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Сырые данные")

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

class MessageMetrics(BaseModel):
    """Метрики сообщения."""
    views: Optional[int] = Field(default=None, ge=0, description="Количество просмотров")
    forwards: Optional[int] = Field(default=None, ge=0, description="Количество пересылок")
    replies: Optional[int] = Field(default=None, ge=0, description="Количество ответов")

class TelegramMessageDTO(BaseModel):
    """DTO для представления сообщения из Telegram."""

    # Основные поля
    id: int = Field(gt=0, description="ID сообщения")
    text: Optional[str] = Field(default=None, description="Текст сообщения")
    date: datetime = Field(description="Дата отправки")
    peer_id: Optional[int] = Field(default=None, description="ID чата Telegram")
    post_author: Optional[str] = Field(default=None, description="Автор поста")

    # Статистика
    metrics: MessageMetrics = Field(
        default_factory=MessageMetrics,
        description="Метрики сообщения"
    )
    edit_date: Optional[datetime] = Field(default=None, description="Дата редактирования")
    is_forwarded: Optional[bool] = Field(default=None, description="Является ли пересланным")
    is_reply: Optional[bool] = Field(default=None, description="Является ли ответом")

    # Мета-информация
    message_type: MessageType = Field(default=MessageType.TEXT, description="Тип сообщения")
    media_group_id: Optional[str] = Field(default=MessageType.TEXT, description="id группы сообщений для aiogram")
    has_media: bool = Field(default=False, description="Содержит ли медиа")

    # Дополнительные данные
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Сырые данные")
    #entities: List[Dict[str, Any]] = Field(default_factory=list, description="Сущности для форматирования текста")

    @property
    def is_edited(self) -> bool:
        return self.edit_date is not None

    @property
    def has_text(self) -> bool:
        return bool(self.text and self.text.strip())


class TelegramMessagesListDTO(BaseModel):
    """DTO для списка сообщений Telegram с мета-информацией."""
    messages: List[TelegramMessageDTO] = Field(default_factory=list)
    total_count: int = Field(default=0, ge=0, description="Количество обработанных сообщений")
    error_count: int = Field(default=0, ge=0, description="Количество ошибок при валидации - переданные хэдером")
    failed_count: int = Field(default=0, ge=0, description="Количество неизвестных ошибок валидации")
    validation_errors: list = Field(default_factory=list, description="Ошибка валидации в виде словарей")
    text_messages_count: int = Field(default=0, ge=0, description="Количество обработанных текстовых сообщений")


    @property
    def has_messages(self) -> bool:
        return len(self.messages) > 0

    def get_error_messages_id(self) -> tuple:
        return tuple(msg_id.get('message_id') for msg_id in self.validation_errors if msg_id)

    def add_message(self, message: TelegramMessageDTO) -> None:
        self.messages.append(message)
        self.total_count += 1
        if message.has_text or message.message_type != MessageType.TEXT:
            self.text_messages_count += 1

    def add_failed_message(self) -> None:
        self.failed_count += 1

    def get_messages_by_type(self, message_type: MessageType) -> List[TelegramMessageDTO]:
        return [msg for msg in self.messages if msg.message_type == message_type]

    def get_messages_with_text(self) -> List[TelegramMessageDTO]:
        return [msg for msg in self.messages if msg.has_text]

    def handle_exceptions(self, error: ValidationError, message_id: int = None) -> None:
        self.error_count += 1
        # Форматируем ошибки в читаемый вид
        error_details = []
        for err in error.errors():
            error_details.append({
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
                "type": err["type"]
            })
        logger.warning(
            f"Ошибка валидации для сообщения {message_id}",
            extra={
                "message_id": message_id,
                "error_count": len(error.errors()),
                "errors": error_details
            }
        )
        # Сохраняем информацию об ошибке
        self.validation_errors.append({
            "message_id": message_id,
            "errors": error_details,
            "timestamp": datetime.now().isoformat()
        })

