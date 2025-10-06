import logging
from typing import Any, Awaitable, Callable, Dict, TYPE_CHECKING

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy import select

if TYPE_CHECKING:
    from aiogram.types import TelegramObject, Message, User as TgUser
    from sqlalchemy.ext.asyncio import AsyncSession

from database.users.models import User
from database.users.roles import UserRole
from config import settings

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """middleware для получения данных о пользователе из базы."""

    async def __call__(self, handler, event, data):
        session: AsyncSession = data.get("db")
        telegram_user: TgUser = data.get("event_from_user")
        try:
            if telegram_user:
                user, created = await User.get_or_create(session, id=telegram_user.id, defaults={
                    'first_name': telegram_user.first_name,
                    'last_name': telegram_user.last_name,
                    'role': UserRole.BOT if telegram_user.is_bot else UserRole.USER,
                    'username': telegram_user.username,
                    'language_code': telegram_user.language_code,
                })
                data["tg_user"] = user
        except Exception:
            logger.error(
                'Middleware error. Во время получения информации о пользователе возникла ошибка', exc_info=True
            )



        return await handler(event, data)
