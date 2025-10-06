from logging import getLogger

import sqlalchemy as sa
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from keyboards.lexicon import MainMenu
from keyboards import ads
from database import User
from utils.bot_utils import get_referral, check_user_subscribe, get_group_login

logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

ads_router = Router()

@ads_router.callback_query(ads.ReferralCheck.filter())
async def handle_blog_btn(callback_query: CallbackQuery, callback_data: ads.ReferralCheck, db: AsyncSession, tg_user: User):
    """Функция обработки реферальной ссылки"""
    bot = callback_query.message.bot
    if tg_user.id == callback_data.user_id:
        return await callback_query.message.answer('Нельзя пригласить самого себя')
    group_login = await get_group_login(bot)
    is_subscribe = await check_user_subscribe(bot=bot, user_id=tg_user.id)
    if is_subscribe:
        try:
            await tg_user.invite_user(referral=callback_data.referral, session=db)
        except sa.exc.IntegrityError:
            return await callback_query.message.answer('Нельзя принять инвайт дважды')
        except Exception:
            return await callback_query.message.answer('Произошла неизвестная ошибка, обратитесь к администратору канала')
        return await callback_query.message.answer(f"Добро пожаловать в наше сообщество! {group_login}")
    return await callback_query.message.answer(f"Вы не подписаны на группу {group_login}")


@ads_router.message(F.text == MainMenu.ADS.value.name)
async def blog_menu(message: Message, db: AsyncSession, tg_user: User):
    bot = message.bot
    bot_about = await bot.get_me()
    referral = get_referral(user_id=tg_user.id, bot_name=bot_about.username)
    await message.answer(f"Ваша реферальная ссылка {referral}")