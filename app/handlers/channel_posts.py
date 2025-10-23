import typing as t
from logging import getLogger
from pprint import pprint

from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from database import User
from services.messages import MessagesService

logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

channel_listener = Router()

@channel_listener.channel_post()
async def handle_channel_post(message: types.Message, db: AsyncSession,):
    """Получение базовой информации о сообщении в канале"""

    logger.info(f'Перехвачено сообщение из канала {message.chat.id}')
    try:
        service = MessagesService(session=db, messages=[message], is_aiogram=True)
        await service.service_and_save_messages()
    except Exception as e:
        logger.error(
            'Ошибка сохранения перехваченного поста: {} из группы - {}'.format(
                message.chat.id, e
            )
        )

@channel_listener.edited_channel_post()
async def handle_edited_channel_post(edited_channel_post: types.Message,  db: AsyncSession,):
    """
    Обработчик для отредактированных сообщений в канале
    """
    logger.info('Перехвачено сообщение из канала {}'.format(edited_channel_post.chat.id))
    try:
        service = MessagesService(session=db, messages=[edited_channel_post], is_aiogram=True)
        await service.service_and_save_messages()
    except Exception as e:
        logger.error(
            'Ошибка сохранения отредактированного поста: {} из группы - {}'.format(
                edited_channel_post.chat.id, e
            )
        )
