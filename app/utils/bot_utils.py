from logging import getLogger
import typing as t
from typing import Any, Coroutine

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMember, ChatInviteLink

from database.users.models import User
from database.users.roles import UserRole
from config import settings
from exceptions.ads import DoubleSubscriptionError
from sqlalchemy.ext.asyncio import AsyncSession

logger = getLogger(__name__)

async def get_bot_user(session: AsyncSession) -> User:
   bot_user, _ = await User.get_or_create(
      session=session,
      id=settings.BOT_ID,
      defaults={
         'first_name': settings.BOT_FIRST_NAME,
         'username': settings.BOT_USERNAME,
         'info': settings.BOT_INFO,
         'is_active': True,
         'role': UserRole.BOT
      }
   )
   return bot_user


async def get_referral(user_id: str, bot_name: str) -> str:
   return  f"https://t.me/{bot_name}?start={user_id}"


async def check_referral(user_id: str, referral: str)  -> t.Tuple[bool, str]:
   try:
      referral = int(referral)
   except ValueError:
      return False, '❌ Некорректное реферальное значение',
   if user_id == referral:
      return False, "❌ Нельзя пригласить самого себя"
   return True, '✅ Вступите в группу и нажмите на кнопку:'


async def get_invite_link(bot: Bot) -> ChatInviteLink:
   return await bot.create_chat_invite_link(settings.CHANNEL_ID)

async def check_user_subscribe(user_id, bot: Bot) -> bool:
   try:
      member: ChatMember = await bot.get_chat_member(settings.CHANNEL_ID, user_id)
      return member.status not in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED}
   except DoubleSubscriptionError as e:
      logger.error('Ошибка получения информации о пользователе из группы', exc_info=True)
      raise DoubleSubscriptionError from e

