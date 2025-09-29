import typing as t
from logging import getLogger

from telethon import TelegramClient
from telethon import types
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.main_menu import blog_categories_kb, main_menu_kb

from database import Post
from keyboards.admin_menu import admin_tools_menu_kb
from keyboards.lexicon import MainMenu, KeyboardBlog, AdminMenu
from database.users.models import User
from utils.parsers import get_media_form_message
from utils.decorators import admin_required
from mappers.telegram import TelegramMessageMapper
from mappers.schemas import TelegramMessagesListDTO
from app.services.messages import MessagesService
from config import settings

admin_router = Router()

logger = getLogger(__name__)

@admin_router.message(F.text == MainMenu.ADMIN.value.name)
@admin_required
async def admin_menu(message: Message, tg_user: User):
    chat = await message.bot.get_chat(settings.CHANNEL_ID)
    members_count = await message.bot.get_chat_member_count(settings.CHANNEL_ID)
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
@admin_required
async def admin_menu_parse_posts(message: Message, db: AsyncSession, teleton_client: TelegramClient, tg_user: User):
    channel = await teleton_client.get_entity(settings.CHANNEL_ID)
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    parsed_messages = [m async for m in teleton_client.iter_messages(
        channel,
        limit=None,
    )]
    service = MessagesService(session=db, messages=parsed_messages, is_aiogram=False)
    await service.service_and_save_messages()
    # if dto_list.error_count:
    #     not_added_messages = str(dto_list.get_error_messages_id())[:40] # Добавить корректное отоброжение
    #     return await message.answer(
    #         f"Не удалось акутализировать посты: {not_added_messages}",
    #         reply_markup=admin_tools_menu_kb()
    #     )
    # for parsed_message in parsed_messages:
    #     # print(parsed_message)
    #     data = TelegramMessageMapper.from_telethon_message(parsed_message)
    #     # print(data)
    return await message.answer(f"Все посты актуализированные!", reply_markup=admin_tools_menu_kb())

@admin_router.message(F.text == AdminMenu.ADD_NEW_POSTS)
@admin_required
async def admin_menu_add_new_posts(message: Message,db: AsyncSession, teleton_client: TelegramClient, tg_user: User):
    channel = await teleton_client.get_entity(settings.CHANNEL_ID) # Вынести в отдельный метод
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    last_obj = await Post.get_last_post(db)
    # Получаем генератор с новыми сообщениями!
    parsed_messages = [m async for m in teleton_client.iter_messages(
        channel,
        limit=None,
        min_id=last_obj.id + 1
    )]
    return await message.answer(f"Добавил новые посты босс!", reply_markup=admin_tools_menu_kb())


@admin_router.message(F.text == AdminMenu.UPDATE_USERS)
@admin_required
async def admin_menu_add_new_posts(message: Message, db: AsyncSession, teleton_client: TelegramClient, tg_user: User):
    # Вынести в отдельный метод
    channel = await teleton_client.get_entity(-1003179370474)  # Вынести в отдельный метод
    chat = await teleton_client.get_permissions(channel, await teleton_client.get_me())
    if not chat.is_admin:
        print("❌ Бот не является администратором группы!")
        return await message.answer(
            f"❌ Вы не является администратором группы для сбора информации о пользователях!",
            reply_markup=admin_tools_menu_kb()
        )
        return
    participants = await teleton_client.get_participants(channel)
    print(participants)
    return await message.answer(f"Обновил информация о пользователях", reply_markup=admin_tools_menu_kb())