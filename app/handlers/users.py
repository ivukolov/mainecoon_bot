from logging import getLogger

from aiogram import Router, types, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, IS_MEMBER, LEAVE_TRANSITION
from aiogram.types import ChatMemberUpdated

from database import User
from sqlalchemy.ext.asyncio import AsyncSession

users_router = Router()

logger = getLogger(__name__)

logger.info('Инициализируем хэндлер Users')

@users_router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    )
)
async def bot_added_as_member(event: ChatMemberUpdated, tg_user: User, db: AsyncSession):
    """Обработка вступления новых пользователей"""
    user = event.new_chat_member.user
    chat = event.chat
    tg_user.is_active = True
    # print(f"✅ В группу вступил новый пользователь: {user.full_name} (@{user.username})")
    logger.info(f"В группу вступил новый пользователь: {user.full_name} (@{user.username})")


@users_router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_MEMBER >> IS_NOT_MEMBER
    )
)
async def handle_user_left(event: ChatMemberUpdated, tg_user: User, db: AsyncSession):
    """Обработчик выхода пользователя из канала"""
    user = event.old_chat_member.user
    chat = event.chat
    tg_user.is_active = False
    # print(f"❌ Пользователь вышел: {user.full_name} (@{user.username}) из канала {chat.title}")
    logger.info(f"Пользователь вышел: {user.full_name} (@{user.username}) из канала {chat.title}")