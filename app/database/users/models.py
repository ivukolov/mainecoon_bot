import typing as t
from datetime import datetime
from logging import getLogger

import sqlalchemy as sa
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMember
from requests import session
from sqlalchemy.dialects.postgresql import CITEXT, TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, backref
from sqlalchemy.sql import expression

from exceptions import ads
from core.models import BaseModel
from config import settings
from database.users.roles import UserRole

logger = getLogger(__name__)

# Информация об отправленных реферальных ссылках.
user_invites = sa.Table(
    'user_invites', BaseModel.metadata,
    sa.Column(
        'user_invited',
        sa.Integer,
        sa.ForeignKey('users.id'),
        primary_key=True,
        comment='Приглашённый пользователь'
    ),
    sa.Column(
        'user_inviting',
        sa.Integer,
        sa.ForeignKey('users.id'),
        primary_key=True,
        comment='Кто пригласил'
    ),
    sa.CheckConstraint('user_invited != user_inviting', name='check_different_users'),
    sa.UniqueConstraint('user_invited', 'user_inviting')
)


class User(BaseModel):
    """Класс для описания модели пользователя"""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        sa.BigInteger,
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
        sa.Enum(UserRole),
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
        sa.String(settings.USERNAME_LENGTH), nullable=True, unique=True
    )
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=True,)
    password: Mapped[str] = mapped_column(sa.String(255), nullable=True, unique=False)
    first_name: Mapped[str] = mapped_column(
        sa.String(settings.USER_FIRST_NAME_LENGTH), nullable=True, unique=False
    )
    last_name: Mapped[str] = mapped_column(
        sa.String(settings.USER_LAST_NAME_LENGTH), nullable=True, unique=False
    )
    language_code: Mapped[str] = mapped_column(
        sa.String(settings.LANG_CODE_LENGTH), nullable=True, unique=False
    )
    info: Mapped[str] = mapped_column(
        sa.String(settings.USER_INFO_LENGTH), nullable=True, unique=False
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    invited_user = relationship(
        'User',
        secondary=user_invites,
        primaryjoin=(id == user_invites.c.user_inviting),
        secondaryjoin=(id == user_invites.c.user_invited),
        backref='inviting_users',
        lazy='selectin', # subquery
        uselist=False,  # Теперь это одиночный объект, а не список
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def __str__(self) -> str:
        return f'<Пользователь: @{self.username} "{self.first_name} {self.last_name}">'


    async def add_invited_user(self, session, inviting_user: 'User') -> None:
        self.invited_user = inviting_user
        session.add(self.invited_user)
        await session.commit()



    async def invite_user(self, referral: t.Union[str,int], session: AsyncSession) -> None:
        inviting_user: User = await User.one_or_none(session=session, id=referral)
        if not inviting_user:
            raise ads.UserNotFoundError()
        await self.add_invited_user(session, inviting_user)
        try:
            await self.add_invited_user(session, inviting_user)
        except Exception as e:
            print(e)



class TelegramSession(BaseModel):
    __tablename__ = "sessions"

    name: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True, comment='Сообщение из поста')
    hash: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True, comment='Хэш сессии')