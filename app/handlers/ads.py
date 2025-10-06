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
async def ads_handle_referral_invite(callback_query: CallbackQuery, callback_data: ads.ReferralCheck, db: AsyncSession, tg_user: User):
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
async def ads_menu(message: Message, db: AsyncSession, tg_user: User):
    await message.answer(
        f"Для размещения рекламы вам нужно задонатить "
        f"{settings.DONATION_AMOUNT} руб. или пригласить {settings.USERS_CNT} "
        f"подписчиков",
        reply_markup=ads.ads_publisher_kb()
        )
    # bot = message.bot
    # bot_about = await bot.get_me()
    # referral = get_referral(user_id=tg_user.id, bot_name=bot_about.username)
    # await message.answer(f"Ваша реферальная ссылка {referral}")

@ads_router.callback_query(F.data == ads.AdsMenu.GET_REFERRAL.value.callback)
async def ads_referral_btn(callback_query: CallbackQuery, db: AsyncSession, tg_user: User):
    bot = callback_query.message.bot
    bot_about = await bot.get_me()
    referral = get_referral(user_id=tg_user.id, bot_name=bot_about.username)
    await callback_query.message.answer(f"Ваша реферальная ссылка {referral}")

@ads_router.callback_query(F.data == ads.AdsMenu.DONATE.value.callback)
async def ads_donate_btn(callback_query: CallbackQuery, db: AsyncSession, tg_user: User):
    await callback_query.message.answer(f"Спасибо что решили нас поддержать! ")