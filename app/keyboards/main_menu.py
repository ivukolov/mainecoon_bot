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
        [KeyboardButton(text=MainMenu.INTERACTIVITY.value.name)],
        [KeyboardButton(text=MainMenu.ABOUT.value.name)]

    ] + [additional_buttons]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_mine_menu_kb() -> ReplyKeyboardMarkup:
    """Главное меню администратора"""
    return main_menu_kb(additional_buttons=[KeyboardButton(text=MainMenu.ADMIN.value.name)])


def admin_tools_menu_kb() -> ReplyKeyboardMarkup:
    """Панель инструемнов администратора"""
    buttons = [
        [KeyboardButton(text=AdminMenu.CHEK_POSTS)],
        [KeyboardButton(text=AdminMenu.PARSE_POSTS)]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


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

# def confirm_post_kb(post_id: int) -> InlineKeyboardMarkup:
#     """Кнопки подтверждения для модерации"""
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="✅ Одобрить",
#                     callback_data=f"mod_approve_{post_id}"
#                 ),
#                 InlineKeyboardButton(
#                     text="❌ Отклонить",
#                     callback_data=f"mod_reject_{post_id}"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="⛔ Забанить автора",
#                     callback_data=f"mod_ban_{post_id}"
#                 )
#             ]
#         ]
#     )


def partner_offers_kb(offers: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
    """Динамическая клавиатура партнерских предложений"""
    buttons = [
        [InlineKeyboardButton(text=name, url=link)]
        for name, link in offers
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="partners_back")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Универсальные строители ---

def build_inline_kb(
        buttons: List[Union[Tuple[str, str], List[Tuple[str, str]]]],
        row_width: int = 2
) -> InlineKeyboardMarkup:
    """
    Универсальный строитель inline-клавиатур

    :param buttons: Список кнопок в формате [(текст, callback_data)]
                    или [[(текст, callback_data)]] для явного указания рядов
    :param row_width: Количество кнопок в ряду (если не указаны явные ряды)
    :return: Готовый InlineKeyboardMarkup
    """
    keyboard = []

    # Если переданы готовые ряды
    if buttons and isinstance(buttons[0], list):
        keyboard = [
            [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
            for row in buttons
        ]
    else:
        # Формируем ряды автоматически
        row = []
        for text, data in buttons:
            row.append(InlineKeyboardButton(text=text, callback_data=data))
            if len(row) >= row_width:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Пример использования строителя
example_kb = build_inline_kb(
    buttons=[
        ("Кнопка 1", "btn1"),
        ("Кнопка 2", "btn2"),
        ("Кнопка 3", "btn3"),
        ("Кнопка 4", "btn4")
    ],
    row_width=2
)