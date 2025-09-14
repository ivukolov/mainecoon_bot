from datetime import datetime
from sqlalchemy import Enum, String, Unicode, BigInteger, Text
from sqlalchemy.dialects.postgresql import CITEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from core.models import BaseModel
from config import settings
from database.users.roles import UserRole

class User(BaseModel):
    """Класс для описания модели пользователя"""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
        nullable=False,
        unique=True,
        info={
        "verbose_name": "telegram id пользователя",
        "help_text": "Уникальный tg id для рассылки и идентификации"
        }
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.USER.value,
        server_default=UserRole.USER.value,
        unique = False,
        info={
            "verbose_name": "Роль пользователя",
            "help_text": f"Присваивание роли пользователя"
         f": {', '.join([name.value for name in UserRole])}"
        }
    )
    username: Mapped[str] = mapped_column(
        String(settings.USERNAME_LENGTH), nullable=True, unique=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True,)
    password: Mapped[str] = mapped_column(String(255), nullable=True, unique=False)
    first_name: Mapped[str] = mapped_column(
        String(settings.USER_FIRST_NAME_LENGTH), nullable=True, unique=False
    )
    last_name: Mapped[str] = mapped_column(
        String(settings.USER_LAST_NAME_LENGTH), nullable=True, unique=False
    )
    language_code: Mapped[str] = mapped_column(
        String(settings.LANG_CODE_LENGTH), nullable=True, unique=False
    )
    info: Mapped[str] = mapped_column(
        String(settings.USER_INFO_LENGTH), nullable=True, unique=False
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def __str__(self) -> str:
        return f'id пользователя:{self.id}, role: {self.role}'

class TelegramSession(BaseModel):
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, comment='Сообщение из поста')
    hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True, comment='Хэш сессии')