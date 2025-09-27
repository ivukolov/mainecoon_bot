
from logging import getLogger

from aiogram import Router, F, Bot, filters
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession


from config import settings
from keyboards.lexicon import MainMenu, KeyboardBlog, ActionButtons
from app.utils.pagintaions import PostPaginationHandler, Pagination
from database.users.models import User


partners_router = Router()

logger = getLogger(__name__)

@partners_router.message(F.text == MainMenu.PARTNERS.value.name)
async def main_menu_returner(message: Message, db: AsyncSession, tg_user: User):
    handler = PostPaginationHandler(db)
    await handler.handle_items_page(message, tag=settings.PARTNERS_TAG, page=1)

@partners_router.message(Pagination.filter())
async def main_menu_returner(callback_query: CallbackQuery, callback_data: Pagination, db: AsyncSession, tg_user: User):
    handler = PostPaginationHandler(db)
    await handler.handle_items_page(callback_query.message, tag=settings.PARTNERS_TAG, page=callback_data.page)