from logging import getLogger

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from keyboards.lexicon import MainMenu
from database.users.models import User


logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

interactives_router = Router()

@interactives_router.message(F.text == MainMenu.INTERACTIVES.value.name)
async def partners_returner(message: Message, db: AsyncSession, tg_user: User):
    return await message.answer("Пришлите фото своего кота!")
    # return await message.answer_poll(
    #     question="Ваш вопрос?",  # chat_id берется из message
    #     options=["Вариант 1", "Вариант 2"],
    #     is_anonymous=False
    # )