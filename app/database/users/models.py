from datetime import datetime
from sqlalchemy import Enum, String, Unicode, BigInteger
from sqlalchemy.dialects.postgresql import CITEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
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
    info: Mapped[str] = mapped_column(
        String(settings.USER_INFO_LENGTH), nullable=True, unique=False
    )
    # registration_datetime: Mapped[datetime] = mapped_column(
    #     TIMESTAMP(timezone=False, precision=0),
    #     nullable=False,
    #     server_default=expression.text("(now() AT TIME ZONE 'UTC'::text)"),
    # )
    pm_active: Mapped[bool] = mapped_column(nullable=False, server_default=expression.false())

    def is_admin(self):
        return self.role == UserRole.ADMIN