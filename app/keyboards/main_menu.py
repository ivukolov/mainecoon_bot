from typing import List, Union, Tuple, Optional

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from utils.pagintaions import Pagination
from keyboards.lexicon import MainMenu, ActionButtons, AdminMenu, KeyboardBlog

# --- Reply Keyboards (обычные кнопки под полем ввода) ---

def main_menu_kb(additional_buttons: list = None) -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    if not additional_buttons:
        additional_buttons = []
    buttons = [
        [KeyboardButton(text=MainMenu.BLOG.value.name)],
        [KeyboardButton(text=MainMenu.PARTNERS.value.name)],
        [KeyboardButton(text=MainMenu.ADS.value.name)],
        [KeyboardButton(text=MainMenu.INTERACTIVES.value.name)],
        [KeyboardButton(text=MainMenu.ABOUT.value.name)]

    ] + [additional_buttons]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_mine_menu_kb() -> ReplyKeyboardMarkup:
    """Главное меню администратора"""
    return main_menu_kb(additional_buttons=[KeyboardButton(text=MainMenu.ADMIN.value.name)])

def cancel_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для отмены действия"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=ActionButtons.CANCEL)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# --- Inline Keyboards (кнопки в сообщении) ---

def blog_categories_kb() -> InlineKeyboardMarkup:
    """Кнопки рубрик блога"""
    buttons = [
        [
            InlineKeyboardButton(
            text=data.value.name, callback_data=Pagination(
                action="get", page=1, tag=data.value.tag
            ).pack()
        )
        ]
        for data in KeyboardBlog
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)