import asyncio
from logging import getLogger
import typing as t
from typing import Any, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.client.session import aiohttp
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMember, ChatInviteLink

from utils.cache import RedisCache
from database.users.models import User
from database.users.roles import UserRole
from config import settings
from exceptions.ads import DoubleSubscriptionError

logger = getLogger(__name__)

async def bot_send_message(text: str) -> None:
   url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
   payload = {
      'chat_id': settings.ADMIN_ID,
      'text': text
   }
   async with aiohttp.ClientSession() as session:
      async with session.post(url, json=payload) as response:
         return await response.json()


async def get_updates(offset=None):
   url =  url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getUpdates"
   params = {
      'timeout': 30,  # Long polling timeout
      'offset': offset
   }

   async with aiohttp.ClientSession() as session:
      async with session.get(url, params=params) as response:
         if response.status == 200:
            data = await response.json()
            return data.get('result', [])
         else:
            print(f"Error: {response.status}")
            return []

async def get_confirm_code():
   cash = RedisCache()
   redis_key = f"{settings.ADMIN_ID}_teletone_code"
   cached_keys = await cash.get_json(redis_key)
   last_update_id = cached_keys.get('last_update_id') if cached_keys else 1
   await bot_send_message('Введите telegram код')
   while True:
      try:
         updates = await get_updates(last_update_id)
         for update in updates:
            last_update_id = update['update_id'] + 1
            message = update.get('message')
            if message and message.get('chat'):
               chat_id = message['chat'].get('id')
               if chat_id == settings.ADMIN_ID:
                  code = message.get('text')
                  try:
                     code = str(code.strip())
                  except ValueError:
                     await bot_send_message('Код должен быть в виде цифр')
                     continue
                  except Exception as e:
                     await bot_send_message(f'Неизвестная ошибка {e}, попробуйте ещё раз')
                     continue
                  data = {'code': [code], 'last_update_id': last_update_id}
                  await cash.set_json(redis_key, data)
                  await bot_send_message('Код принят, обрабатываем!')
                  print(code)
                  return code
                  # if cached_keys and code in cached_keys['code']:
                  #    continue
                  # data = {'code': [code], 'last_update_id': last_update_id}
                  # if cached_keys:
                  #    data['code'] + cached_keys.get('code', [])
                  # await cash.set_json(redis_key, data)


      except Exception as e:
         logger.error(f"Error: {e}")
         await asyncio.sleep(5)

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

