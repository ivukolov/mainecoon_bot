import typing as t
from datetime import datetime
from logging import getLogger

import sqlalchemy as sa
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMember
from passlib import exc
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
    sa.UniqueConstraint('user_invited', 'user_inviting'),
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
    username: Mapped[str] = mapped_column(
        sa.String(settings.USERNAME_LENGTH), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(sa.String(settings.USER_PASSWORD_HASH_LENGTH), nullable=True, unique=False)
    first_name: Mapped[t.Optional[str]] = mapped_column(
        sa.String(settings.USER_FIRST_NAME_LENGTH), nullable=True, unique=False
    )
    last_name: Mapped[t.Optional[str]] = mapped_column(
        sa.String(settings.USER_LAST_NAME_LENGTH), nullable=True, unique=False
    )
    contact: Mapped[t.Optional[bool]] = mapped_column(sa.Boolean, nullable=True, unique=False)
    mutual_contact: Mapped[t.Optional[bool]] = mapped_column(sa.Boolean, nullable=True, unique=False)
    phone: Mapped[t.Optional[str]] = mapped_column(sa.String(settings.PHONE_LENGTH), nullable=True, unique=False)
    language_code: Mapped[str] = mapped_column(
        sa.String(settings.LANG_CODE_LENGTH), nullable=True, unique=False
    )
    access_hash: Mapped[str] = mapped_column(sa.String(settings.USER_PASSWORD_HASH_LENGTH), nullable=True, unique=False)
    is_premium: Mapped[t.Optional[bool]] = mapped_column(sa.Boolean, nullable=True, unique=False)
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
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=True,)
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

    @staticmethod
    def get_password_hash(password):
        return settings.PWD_CONTEXT.hash(password)

    def set_password(self, password):
        self.password = self.get_password_hash(password)

    def verify_password(self, password) -> bool:
        try:
            return settings.PWD_CONTEXT.verify(password, self.password)
        except exc.UnknownHashError:
            # Хеш в неизвестном формате
            logger.error("Ошибка проверки пароля: неизвестный формат хеша", exc_info=True)
            return False
        except exc.InvalidHashError:
            # Поврежденный или некорректный хеш
            logger.error("Ошибка проверки пароля: некорректный хеш", exc_info=True)
            return False
        except Exception:
            logger.error("Неожиданная ошибка при проверки хеша пароля", exc_info=True)
            return False

    def authenticate_user(self, password) -> bool:
        """Асинхронная функция которая проверят валидность пользователя
            :param username: Имя пользователя для проверки
            :param password: <PASSWORD>
            :return: True если пользователь валиден, False в остальных
        """
        if self.is_admin:
            return self.verify_password(password)
        return False



    async def add_invited_user(self, session, inviting_user: 'User') -> None:
        self.invited_user = inviting_user
        session.add(self.invited_user)
        await session.commit()



    async def invite_user(self, referral: t.Union[str,int], session: AsyncSession) -> None:
        inviting_user: User | None = await User.one_or_none(session=session, id=referral)
        if not inviting_user:
            raise ads.UserNotFoundError()
        await self.add_invited_user(session, inviting_user)

    @classmethod
    async def bulk_get_or_create_users(cls, session, users_id: t.Set[str]) -> t.Dict[str, 'User']:
        if not users_id:
            return {}

        existing_users_stmt = sa.select(cls).where(cls.id.in_(users_id))
        existing_users_result = await session.execute(existing_users_stmt)
        existing_users = {user.name: user for user in existing_users_result.scalars()}
        users_to_create = users_id - set(existing_users.keys())
        if users_to_create:
            new_users = []
            for user in users_to_create:
                new_user = User(id=user)
                new_users.append(new_user)
                existing_users[user] = new_user

            session.add_all(new_users)
            await session.flush()  # Сохраняем, чтобы получить IDs
        return existing_users



class TelegramSession(BaseModel):
    __tablename__ = "sessions"

    name: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True, comment='Сообщение из поста')
    hash: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True, comment='Хэш сессии')