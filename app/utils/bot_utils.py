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

async def get_admin_user(session: AsyncSession) -> User:
   admin, _ = await User.get_or_create(
      session=session,
      id=settings.ADMIN_ID,
      defaults={
         'username': settings.ADMIN_USERNAME,
         'is_active': True,
         'role': UserRole.ADMIN,
      }
   )
   return admin


def reverse_tg_url(login: str) -> str:
   return f"https://t.me/{login}"

async def get_group_login(bot: Bot) -> str:
   chat = await bot.get_chat(settings.CHANNEL_ID)
   return f"@{chat.username}"

def get_referral(user_id: int, bot_name: str) -> str:
   return  f"https://t.me/{bot_name}?start={user_id}"


def check_referral(user_id: int, referral: str)  -> t.Tuple[bool, str]:
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

