from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.lexicon import AdminMenu, ActionButtons, AdminInteractives


def admin_tools_menu_kb() -> ReplyKeyboardMarkup:
    """Панель инструемнов администратора"""
    buttons = [
        [KeyboardButton(text=admin_btn.value.name)] for admin_btn in AdminMenu
    ]
    buttons.append([KeyboardButton(text=ActionButtons.CANCEL.value.name)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def maike_interactives_kb() -> InlineKeyboardMarkup:
    btn = [
        [
            InlineKeyboardButton(
                text=btn.value.name, callback_data=btn.value.callback)
        ]
        for btn in AdminInteractives
    ]
    return InlineKeyboardMarkup(inline_keyboard=btn)