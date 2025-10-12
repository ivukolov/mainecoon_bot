from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.lexicon import ActionButtons, AdsMenu

class ReferralCheck(CallbackData, prefix="referral_check"):
    user_id: int
    referral: int


def referral_check_kb(user_id: int, referral: int) -> InlineKeyboardMarkup:
    """Кнопки для работы с реферальной ссылкой"""
    buttons = [
        [
            InlineKeyboardButton(
                text=ActionButtons.USER_JOIN,
                callback_data=ReferralCheck(
                    user_id=user_id, referral=referral
                ).pack())
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ads_publisher_kb() -> InlineKeyboardMarkup:
    btn = [
        [
            InlineKeyboardButton(
                text=btn.value.name, callback_data=btn.value.callback)
        ]
        for btn in AdsMenu
    ]
    return InlineKeyboardMarkup(inline_keyboard=btn)