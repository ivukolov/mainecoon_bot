from logging import getLogger
import typing
import re
from pprint import pformat

from pyexpat.errors import messages
from telethon import TelegramClient
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.parsers import TeletonClient

from keyboards.main_menu import blog_categories_kb, main_menu_kb, pagination_kb
from keyboards.lexicon import MainMenu, KeyboardBlog
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
        return await message.answer(response, reply_markup=main_menu_kb())
    return await message.answer(
        f"Привет {user.id if not created else 'Котан'}! Я — бот канала «Мейн-куны в Воронеже».\n\n",
        reply_markup=main_menu_kb()
    )

@command_start_router.message(F.text == MainMenu.BLOG)
async def blog_menu(message: Message, bot: Bot , db: AsyncSession, teleton_client: TelegramClient):
    # hashtags = await get_hashtags_from_channel(bot=bot, message_limit=100)
    channel_username = -1001573169353

    # # Получаем entity канала
    # channel = await teleton_client.get_entity(channel_username)
    # async for mess in teleton_client.iter_messages(
    #         channel,
    #         limit=50,
    # ):
    #     text = mess.text
    #     if text:
    #         hashtags = re.findall(r'#КотоПсихология', text)
    #         if hashtags:
    #             print('ЭТО ХЭШТЕГ!!!!!!')
    #             print(mess.id)
    #             print('__________________________________________________________')
    #             print(text)
    #             print('__________________________________________________________')
    #
    #             return await message.answer(mess.text)
    #
    # return await message.answer('Ой! хэштеги не обнаружены!')

    await message.answer(f"Всё ок!", reply_markup=blog_categories_kb())


@command_start_router.callback_query(F.data.in_(KeyboardBlog.get_callback_list()) | F.data.startswith("blog_psychology_next"))
async def handle_blog_btn(callback_query: CallbackQuery, teleton_client: TelegramClient):
    channel_username = -1001573169353
    channel = await teleton_client.get_entity(channel_username)
    page = 1
    page_size = 2
    offset = (page - 1) * page_size
    parsed_data = tuple
    await callback_query.answer()
    print(callback_query.data)
    if callback_query.data == KeyboardBlog.BLOG_PSYCHOLOGY_CALLBACK:
        async for mess in teleton_client.iter_messages(
            channel,
            limit=1,
            add_offset=0,
            # search=KeyboardBlog.BLOG_NUTRITION_TAG
        ):
            text = mess.text
            if text:
                await callback_query.message.answer(text)
        await callback_query.message.answer(
            "Вы нажали кнопку blog_psychology!",
            reply_markup=pagination_kb(
                current_page=page,
                total_pages=page_size,
                prefix=KeyboardBlog.BLOG_PSYCHOLOGY_CALLBACK)
        )
    elif callback_query.data == KeyboardBlog.BLOG_EXHIBITIONS_CALLBACK:
        await callback_query.message.answer("Вы нажали кнопку blog_exhibitions")
    elif callback_query.data == KeyboardBlog.BLOG_NUTRITION_CALLBACK:
        await callback_query.message.answer("Вы нажали кнопку blog_nutrition")
    elif callback_query.data == KeyboardBlog.BLOG_HEALTH_CALLBACK:
        await callback_query.message.answer("Вы нажали кнопку blog_health")