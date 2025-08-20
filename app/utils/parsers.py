from aiogram import Bot
from typing import List, Set
import re

from config import settings


async def get_hashtags_from_channel(bot: Bot, message_limit: int = 100) -> Set[str]:
    """
    Парсит хэштеги из последних сообщений канала
    """
    hashtags = set()
    try:
        chat = await bot.get_chat(settings.CHANNEL_ID)
        test= bot.get_messages(chat.id)
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
    return hashtags