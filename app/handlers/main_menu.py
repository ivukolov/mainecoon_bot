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
from utils.parsers import get_media_form_message
from utils.pagintaions import PostPaginationHandler, Paginator, Pagination

main_menu_router = Router()

logger = getLogger(__name__)

@main_menu_router.message(F.text == ActionButtons.MAIN_MENU)
async def main_menu_returner(message: Message, db: AsyncSession, tg_user: User, bot: Bot):
    if tg_user.is_admin:
        return await message.answer(
        text='Добро пожаловать в главное меню!',
        reply_markup=admin_mine_menu_kb()
    )
    return await message.answer(
        text='Добро пожаловать в главное меню!',
        reply_markup=main_menu_kb()
    )