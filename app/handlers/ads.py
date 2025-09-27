from datetime import datetime, timedelta
from logging import getLogger

import sqlalchemy as sa
from telethon import TelegramClient
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from keyboards.lexicon import MainMenu
from app.keyboards import ads
from database import User
from utils.bot_utils import get_referral, check_user_subscribe
from app.exceptions.ads import DoubleSubscriptionError

logger = getLogger(__name__)

ads_router = Router()

@ads_router.callback_query(ads.ReferralCheck.filter())
async def handle_blog_btn(callback_query: CallbackQuery, callback_data: ads.ReferralCheck, db: AsyncSession, tg_user: User):
    bot = callback_query.message.bot
    is_subscribe = await check_user_subscribe(bot=bot, user_id=tg_user.id)
    invite_link = await bot.create_chat_invite_link(settings.CHANNEL_ID)
    if is_subscribe:
        try:
            await tg_user.invite_user(referral=callback_data.referral, session=db)
        except sa.exc.IntegrityError:
            return await callback_query.message.answer('Нельзя принять инвайт дважды')
        except Exception:
            return await callback_query.message.answer('Произошла неизвестная ошибка, обратитесь к администратору канала')
        return await callback_query.message.answer(f"Добро пожаловать в наше сообщество!")
    return await callback_query.message.answer(f"Вы не подписаны на группу {invite_link.invite_link}")


@ads_router.message(F.text == MainMenu.ADS.value.name)
async def blog_menu(message: Message, db: AsyncSession, tg_user: User):
    bot_about = await message.bot.get_me()
    referral = await get_referral(user_id=tg_user.id, bot_name=bot_about.username)
    await message.answer(f"Ваша ссылка на приглашение {referral}")