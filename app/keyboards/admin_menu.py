from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.lexicon import AdminMenu, ActionButtons


def admin_tools_menu_kb() -> ReplyKeyboardMarkup:
    """Панель инструемнов администратора"""
    buttons = [
        [KeyboardButton(text=AdminMenu.CHEK_POSTS)],
        [KeyboardButton(text=AdminMenu.PARSE_POSTS)],
        [KeyboardButton(text=AdminMenu.ADD_NEW_POSTS)],
        [KeyboardButton(text=ActionButtons.MAIN_MENU)],
        [KeyboardButton(text=AdminMenu.UPDATE_USERS)],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)