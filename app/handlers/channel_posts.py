import typing as t
from logging import getLogger
from pprint import pprint

from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from database import User
from services.messages import MessagesService

logger = getLogger(__name__)

channel_listener = Router()

@channel_listener.channel_post()
async def handle_channel_post(message: types.Message, db: AsyncSession,):
    """Получение базовой информации о сообщении в канале"""
    channel_id = message.chat.id
    channel_username = message.chat.username
    message_id = message.message_id
    logger.info(f'Перехвачено сообщение из канала {message.chat.id}')
    try:
        service = MessagesService(session=db, messages=[message], is_aiogram=True)
        await service.service_and_save_messages()
    except Exception as e:
        print(e)
        logger.error(e, exc_info=True)

    # Информация о канале (чате)
    channel_info = (
        f'channel_id: {message.chat.id},\n'
        f'channel_title: {message.chat.title},\n'
        f'channel_username: {message.chat.username},\n'
        f'message_id: {message.message_id},\n'
        f'date: {message.date},\n'
        f'text: {message.text},\n'
        f'content_type: {message.content_type},\n '
        f'caption: {message.caption}\n'
        f'media_group_id: {message.media_group_id},\n'
    )
    print(channel_info)
    print('____________________________________')
    if message.text or message.caption:
        await message.bot.forward_message(-1003179370474, -1003179370474, message.message_id)

    # await channel_post.bot.send_message(chat_id=1382354642, text=channel_info)


@channel_listener.edited_channel_post()
async def handle_edited_channel_post(edited_channel_post: types.Message):
    """
    Обработчик для отредактированных сообщений в канале
    """
    print(f"Сообщение отредактировано: {edited_channel_post.text}")
