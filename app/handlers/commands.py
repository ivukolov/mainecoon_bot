from datetime import datetime, timedelta
from logging import getLogger
import typing as t

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject, Command
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.exc as sa_exc


from config import settings
from database.users.models import User
from keyboards.main_menu import  main_menu_kb, admin_mine_menu_kb
from keyboards.lexicon import ActionButtons
from handlers.ads.keyboards import referral_check_kb
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
        try:
            referral = check_referral(user_id=tg_user.id, referral=referral)
        except Exception as e:
            logger.error(e)
            return await message.answer(
                f"❌ {e}",
                reply_markup=main_menu_kb()
            )
        else:
            return await message.answer(
                "✅ Вступите в группу и нажмите на кнопку:",
                reply_markup=referral_check_kb(
                    user_id=tg_user.id, referral=referral
               )
            )
    if tg_user and tg_user.is_admin:
        return await message.answer("Привет Босс !", reply_markup=admin_mine_menu_kb())
    return await message.answer(
        f"Привет {username}! Я — бот канала «Мейн-куны в Воронеже».\n\n",
        reply_markup=main_menu_kb()
    )


@commands_router.message(F.text == ActionButtons.CANCEL.value.name)
async def cancel_from_any_state(message: Message, tg_user: User, state: FSMContext):
    await state.clear()
    if tg_user and tg_user.is_admin:
        return await message.answer("Привет Босс !", reply_markup=admin_mine_menu_kb())
    await message.answer(
        "✅ Возвращяемся в главное меню",
        reply_markup=main_menu_kb()
    )

@commands_router.message(Command("help"))
async def cmd_help(message: Message):
    """Получение справочной информации"""
    return await message.answer(
        "Добрый день! Меню в разработке!",
    )

@commands_router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Настройки аккаунта"""
    return await message.answer(
        "Добрый день! Меню в разработке!",
    )

@commands_router.message(Command("profile"))
async def cmd_info(message: Message, tg_user: User):
    """Получение информации об аккаунте пользователя"""
    invited_users = tg_user.invited_users_count
    return await message.answer(
        f"Профиль: {tg_user.first_name} {tg_user.last_name}\n"
        f"Кол-во приглашённых пользователей: {invited_users}\n",
    )