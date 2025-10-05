from io import BytesIO
from logging import getLogger
from collections import defaultdict

from requests import session
from telethon import TelegramClient
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from config import settings
from keyboards.main_menu import blog_categories_kb, main_menu_kb, admin_mine_menu_kb
from keyboards.lexicon import MainMenu, KeyboardBlog, ActionButtons
from database.users.models import User
from database import Tag, Post
from utils.pagintaions import PostPaginationHandler, Paginator, Pagination

logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

about_router = Router()

@about_router.message(F.text == MainMenu.ABOUT.value.name)
async def blog_menu(message: Message, db: AsyncSession, tg_user: User):
    chat = await message.bot.get_chat(settings.CHANNEL_ID)
    members_count = await message.bot.get_chat_member_count(settings.CHANNEL_ID)
    response = (
        f"Здравствуйте! Вас приветствует "
        f"{chat.title}\n"
        f"@{chat.username}\n"
        f"Количество активних подписчиков: {members_count} и постоянно растёт!\n"
        f"В нашем сообществе вы найдёте подсказки о:\n {chat.description}"
    )
    await message.answer(response)


