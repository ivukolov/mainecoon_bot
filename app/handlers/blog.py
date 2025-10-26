from logging import getLogger

from telethon import TelegramClient
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import User
from keyboards.main_menu import blog_categories_kb
from keyboards.lexicon import MainMenu
from utils.pagintaions import PostPaginationHandler, Paginator, Pagination

logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

blog_router = Router()

@blog_router.message(F.text == MainMenu.BLOG.value.name)
async def blog_menu(message: Message, db: AsyncSession, tg_user: User):
    await message.answer(f"Выберите категорию", reply_markup=blog_categories_kb())

@blog_router.callback_query(Pagination.filter())
async def handle_blog_btn(callback_query: CallbackQuery, callback_data: Pagination, db: AsyncSession, tg_user: User):
    handler = PostPaginationHandler(db)
    await handler.handle_items_page(callback_query.message, tag=callback_data.tag, page=callback_data.page)