from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.lexicon import ActionButtons

class ReferralCheck(CallbackData, prefix="referral_check"):
    user_id: int
    referral: str


def referral_check_kb(user_id: int, referral: str) -> InlineKeyboardMarkup:
    """Кнопки рубрик блога"""
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