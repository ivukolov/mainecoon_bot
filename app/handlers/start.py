from logging import getLogger

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from utils.parsers import get_hashtags_from_channel
from keyboards.main_menu import blog_categories_kb, main_menu_kb
from keyboards.lexicon import MainMenu
from database.users.models import User
from config import settings

command_start_router = Router()

logger = getLogger(__name__)

@command_start_router.message(CommandStart())
async def cmd_start(message: Message, db: AsyncSession, bot: Bot):
    user, created = await User.get_or_create(db, id=message.from_user.id)
    if user.is_admin():
        chat = await bot.get_chat(settings.CHANNEL_ID)
        members_count = await bot.get_chat_member_count(settings.CHANNEL_ID)
        response = (
            f"О великий администратор!\n "
            f"📢 Информация о канале: {members_count}\n"
            f"Название: {chat.title}\n"
            f"ID: {chat.id}\n"
            f"Тип: {chat.type}\n"
            f"Username: @{chat.username if chat.username else 'Нет'}\n"
            f"Описание: {chat.description[:100] + '...' if chat.description and len(chat.description) > 100 else chat.description or 'Нет описания'}"
        )
        return await message.answer(response)
    return await message.answer(
        f"Привет {user.id if not created else 'Котан'}! Я — бот канала «Мейн-куны в Воронеже».\n\n",
        reply_markup=main_menu_kb()
    )

@command_start_router.message(F.text == MainMenu.BLOG)
async def blog_menu(message: Message, bot: Bot , db: AsyncSession):
    hashtags = await get_hashtags_from_channel(bot=bot, message_limit=100)
    await message.answer(f"Список хэштегов {hashtags}", reply_markup=blog_categories_kb())