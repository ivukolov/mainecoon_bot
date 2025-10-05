from typing import List, TypeVar

import sqlalchemy as sa
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.blog.models import Tag, Post
from config import settings

T = TypeVar('T')


class Pagination(CallbackData, prefix="pag"):
    action: str  # Действие
    page: int  # Номер страницы
    tag: str

class Paginator:
    def __init__(self, session: AsyncSession, page_size: int = 10):
        self.session = session
        self.page_size = page_size

    async def get_page(
            self,
            query,
            page: int = 1,
    ) -> List[T]:
        """Получить страницу с результатами"""
        offset = (page - 1) * self.page_size
        stmt = query.offset(offset).limit(self.page_size)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_count(self, model, **filters) -> int:
        """Получить общее количество записей"""
        stmt = sa.select(sa.func.count()).select_from(model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar()


class PostPaginationHandler:
    query = sa.select(Post).join(Post.tags)

    def __init__(self, session: AsyncSession):
        self.session = session
        self.page_size = 5
        self.paginator = Paginator(session, page_size=self.page_size)

    def create_pagination_keyboard(self, current_page: int, total_pages: int, tag: str):
        """Создание клавиатуры пагинации"""
        builder = InlineKeyboardBuilder()

        if current_page > 1:
            builder.button(
                text="⬅️ Назад",
                callback_data=Pagination(action="prev", page=current_page - 1, tag=tag).pack()
            )

        builder.button(
            text=f"{current_page}/{total_pages}",
            callback_data="current_page"
        )

        if current_page < total_pages:
            builder.button(
                text="Вперед ➡️",
                callback_data=Pagination(action="next", page=current_page + 1, tag=tag).pack()
            )

        builder.adjust(3)
        return builder.as_markup()

    async def handle_items_page(self, message: Message, tag, page: int = 1,):
        """Обработчик страницы с элементами"""
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        posts = await self.paginator.get_page(
            self.query.filter(
                Tag.name == tag
            ).order_by(Post.id.desc()), page=page
        )

        total_count = await self.paginator.get_total_count(
            self.query.filter(
                Tag.name == tag
            ).order_by(Post.id.desc()))
        total_pages = (total_count + self.paginator.page_size - 1) // self.paginator.page_size

        if not posts:
            await message.answer("Элементы не найдены")
            return
        keyboard = self.create_pagination_keyboard(page, total_pages, tag=tag)
        text = f"Страница {page}, тэг: {tag}\n"
        await message.answer(text, reply_markup=keyboard)
        for idx, post in enumerate(posts):
            await message.bot.forward_message(
                chat_id=message.chat.id,
                from_chat_id=settings.CHANNEL_ID,
                message_id=post.id,
            )

        await message.answer(text, reply_markup=keyboard)