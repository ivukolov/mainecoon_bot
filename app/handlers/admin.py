from io import BytesIO
from logging import getLogger
from collections import defaultdict

from telethon import TelegramClient
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.main_menu import blog_categories_kb, main_menu_kb, pagination_kb
from app.keyboards.admin_menu import admin_tools_menu_kb
from keyboards.lexicon import MainMenu, KeyboardBlog, AdminMenu
from database.users.models import User
from utils.parsers import get_media_form_message
from config import settings

admin_router = Router()

logger = getLogger(__name__)

@admin_router.message(F.text == MainMenu.ADMIN)
async def admin_menu(message: Message, bot: Bot, db: AsyncSession, teleton_client: TelegramClient, tg_user: User):
    if tg_user.is_admin():
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
        await message.answer(response, reply_markup=admin_tools_menu_kb())


@admin_router.message(F.text == AdminMenu.PARSE_POSTS)
async def admin_menu_parse(message: Message, bot: Bot, db: AsyncSession, teleton_client: TelegramClient):
    channel_username = -1001573169353
    channel = await teleton_client.get_entity(channel_username)
    parsed_messages = [mess async for mess in teleton_client.iter_messages(
        channel,
        # limit=3,
    )]

    messeges_id = (mess.id for mess in parsed_messages)
    for msg in parsed_messages:
        if msg.text:
            print(msg)
    print(len(parsed_messages))
    return await message.answer(f"Все посты актуализированные!", reply_markup=admin_tools_menu_kb())