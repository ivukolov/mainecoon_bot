from logging import getLogger

from aiogram import Router

from config import settings
from keyboards.lexicon import MainMenu
from database.users.models import User


logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

polls_router = Router()