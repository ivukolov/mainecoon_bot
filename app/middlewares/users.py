import logging
from typing import Any, Awaitable, Callable, Dict, TYPE_CHECKING

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy import select

from aiogram.types import TelegramObject, Message, User as TgUser, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from utils.identifiers import generate_uuid_from_str
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
                username = telegram_user.username or generate_uuid_from_str(name=str(telegram_user.id))
                user, created = await User.get_or_create(session, id=telegram_user.id, defaults={
                    'first_name': telegram_user.first_name,
                    'last_name': telegram_user.last_name,
                    'role': UserRole.BOT if telegram_user.is_bot else UserRole.USER,
                    'username': username,
                })
                if telegram_user.is_banned:
                    await event.bot.send_message(
                        chat_id=telegram_user.id, text=
                        "❌ Вы заблокированы и не можете использовать бота.\n"
                        "Для разблокировки обратитесь к администратору."
                    )
                    return  # Прерываем обработку
                data["tg_user"] = user
        except Exception:
            logger.error(
                'Middleware error. Во время получения информации о пользователе возникла ошибка'
            )
        return await handler(event, data)
