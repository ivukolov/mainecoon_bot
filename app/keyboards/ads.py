from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.lexicon import ActionButtons, AdsMenu, CatGenders, AdsUserApprove


class ModerateAd(CallbackData, prefix="moderate_ads"):
    ads_id: int
    action: str

def moderate_ad_kb(ads_id: int) -> InlineKeyboardMarkup:
    """Кнопки для модерации рекламных сообщений"""
    buttons = [
        [
            InlineKeyboardButton(
                text=ActionButtons.APPROVE.value.name,
                callback_data=ModerateAd(
                    ads_id=ads_id, action=ActionButtons.APPROVE.value.callback
                ).pack())
        ],
        [
            InlineKeyboardButton(
                text=ActionButtons.REJECT.value.name,
                callback_data=ModerateAd(
                    ads_id=ads_id, action=ActionButtons.REJECT.value.callback
                ).pack())
        ],
        [
            InlineKeyboardButton(
                text=ActionButtons.BANE.value.name,
                callback_data=ModerateAd(
                    ads_id=ads_id, action=ActionButtons.BANE.value.callback
                ).pack())
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)