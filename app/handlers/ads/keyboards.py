from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.lexicon import ActionButtons, AdsMenu, CatGenders, AdsUserApprove

class ModerateAd(CallbackData, prefix="moderate_ads"):
    ads_id: int
    action: str

class ReferralCheck(CallbackData, prefix="referral_check"):
    user_id: int
    referral: int

def referral_check_kb(user_id: int, referral: int) -> InlineKeyboardMarkup:
    """Кнопки для работы с реферальной ссылкой"""
    buttons = [
        [
            InlineKeyboardButton(
                text=ActionButtons.USER_JOIN.value.name,
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

def ads_cat_gender_kb() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=CatGenders.MALE.value),
                    KeyboardButton(text=CatGenders.FEMALE.value),
                    KeyboardButton(text=ActionButtons.CANCEL.value.name)
                ]
            ],
            resize_keyboard = True
        )


def ads_cat_send_to_moderate_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=AdsUserApprove.TO_MODERATE.value.name),
                KeyboardButton(text=AdsUserApprove.REPEAT.value.name),
                KeyboardButton(text=ActionButtons.CANCEL.value.name)
            ]
        ],
    )