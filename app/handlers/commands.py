from datetime import datetime, timedelta
from logging import getLogger
import typing as t

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.exc as sa_exc


from config import settings
from database.users.models import User
from keyboards.main_menu import  main_menu_kb, admin_mine_menu_kb
from keyboards.ads import referral_check_kb
from utils.bot_utils import check_referral
from exceptions import ads

logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

commands_router = Router()

@commands_router.message(CommandStart())
async def cmd_start(message: Message, tg_user: User, command: CommandObject, db: AsyncSession,):
    username = tg_user.username if tg_user else message.from_user.username
    referral = command.args
    if referral:
        result, msg_txt = check_referral(user_id=tg_user.id, referral=referral)
        if result:
            return await message.answer(
                msg_txt,
                reply_markup=referral_check_kb(
                    user_id=tg_user.id, referral=referral
               )
            )

        return await message.answer(
            msg_txt,
            reply_markup=main_menu_kb()
        )
    if tg_user and tg_user.is_admin:
        return await message.answer("Привет Босс !", reply_markup=admin_mine_menu_kb())
    return await message.answer(
        f"Привет {username}! Я — бот канала «Мейн-куны в Воронеже».\n\n",
        reply_markup=main_menu_kb()
    )