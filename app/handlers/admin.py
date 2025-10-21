import typing as t
from logging import getLogger

from aiogram.fsm.context import FSMContext
from sqlalchemy import delete
from telethon import TelegramClient
from telethon import types
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from database.blog.enums import AdStatus
from keyboards.main_menu import blog_categories_kb, main_menu_kb, cancel_kb

from database import Post, CatAd
from keyboards.admin_menu import admin_tools_menu_kb, maike_interactives_kb
from keyboards.lexicon import MainMenu, KeyboardBlog, AdminMenu, AdminInteractives, ActionButtons
from keyboards.ads import ModerateAd
from database.users.models import User
from services.ads import CatAdsService
from states.admin import AdminModerateStates
from utils.decorators import admin_required
from mappers.telegram import TelegramMessageMapper, TelegramUserMapper
from schemas.dto import TelegramMessagesListDTO
from services.messages import MessagesService
from config import settings

logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

admin_router = Router()


@admin_router.message(F.text == MainMenu.ADMIN.value.name)
@admin_required
async def admin_menu(message: Message, tg_user: User):
    chat = await message.bot.get_chat(settings.CHANNEL_ID)
    members_count = await message.bot.get_chat_member_count(settings.CHANNEL_ID)
    response = (
        f"О великий администратор!\n "
        f"📢 Информация о канале: {members_count}\n"
        f"Название: {chat.title}\n"
        f"ID: {chat.id}\n"
        f"Тип: {chat.type}\n"
        f"Username: @{chat.username if chat.username else 'Нет'}\n"
        f"Описание: {chat.description[:100] + '...' if chat.description and len(chat.description) > 100 else chat.description or 'Нет описания'}"
    )
    await message.answer(response, reply_markup=admin_tools_menu_kb())


@admin_router.message(F.text == AdminMenu.ADD_INTERACTIVES.value.name)
@admin_required
async def admin_menu_make_interactives(message: Message, db: AsyncSession, tg_user: User):
    return await message.answer('Выберите тип интерактива', reply_markup=maike_interactives_kb())


@admin_router.message(F.text == AdminMenu.PARSE_POSTS.value.name)
@admin_required
async def admin_menu_parse_posts(message: Message, db: AsyncSession, teleton_client: TelegramClient, tg_user: User):
    channel = await teleton_client.get_entity(settings.CHANNEL_ID)
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    logger.info('Запущен процесс обновления постов и тэгов')
    parsed_messages = [m async for m in teleton_client.iter_messages(
        channel,
        limit=None,
    )]
    logger.info(f'Из канала загружено {len(parsed_messages)} постов, приступаю к обработке')
    service = MessagesService(session=db, messages=parsed_messages, is_aiogram=False)
    try:
        await service.service_and_save_messages()
    except Exception as e:
        logger.error(e, exc_info=True)
        return await message.answer(f"Не удалось актуализировать все посты {e}", reply_markup=admin_tools_menu_kb())
    logger.info('Все посты актуализированные')
    return await message.answer(f"Все посты актуализированные!", reply_markup=admin_tools_menu_kb())


@admin_router.message(F.text == AdminMenu.UPDATE_USERS.value.name)
@admin_required
async def admin_menu_add_new_posts(message: Message, db: AsyncSession, teleton_client: TelegramClient, tg_user: User):
    # Вынести в отдельный метод
    channel = await teleton_client.get_entity(settings.CHANNEL_ID)  # Вынести в отдельный метод
    chat = await teleton_client.get_permissions(channel, await teleton_client.get_me())
    if not chat.is_admin:
        return await message.answer(
            f"❌ Вы не является администратором группы для сбора информации о пользователях!",
            reply_markup=admin_tools_menu_kb()
        )
    parsed_users = [u async for u in teleton_client.iter_participants(channel, limit=None)]
    users_dto = TelegramUserMapper.get_users_from_telethon_raw_data(parsed_users)
    users_list = users_dto.get_model_dump_list()
    try:
        await User.on_conflict_do_update_users(session=db, users_dict_list=users_list)
    except Exception as e:
        await db.rollback()
        print(f"Ошибка: {e}")
        raise
    return await message.answer(f"Обновил информация о пользователях", reply_markup=admin_tools_menu_kb())


@admin_router.callback_query(ModerateAd.filter())
async def handle_moderating_ads_data(callback_query: CallbackQuery, callback_data: ModerateAd, state: FSMContext,
                                     tg_user: User):
    """Модерированное рекламных сообщений"""
    if callback_data.action == ActionButtons.APPROVE.value.callback:
        await state.set_state(AdminModerateStates.approve)
        await state.update_data(ads_id=callback_data.ads_id)
        await callback_query.message.answer('Одобрено! Введите заголовок рекламного сообщения:',
                                            reply_markup=cancel_kb())
    if callback_data.action == ActionButtons.REJECT.value.callback:
        await state.set_state(AdminModerateStates.reject)
        await state.update_data(ads_id=callback_data.ads_id)
        await callback_query.message.answer(
            'Возвращено пользователю на доработку! Напишите комментарий о причине возврата:', reply_markup=cancel_kb()
        )
    if callback_data.action == ActionButtons.BANE.value.callback:
        await state.set_state(AdminModerateStates.bane)
        await state.update_data(author_id=callback_data.author_id)
        await callback_query.message.answer('Укажите причину бана:', reply_markup=cancel_kb())


@admin_router.message(AdminModerateStates.approve, F.text != ActionButtons.CANCEL.value.name)
async def ads_approve_state(
        message: Message, state: FSMContext, tg_user: User, cat_ads_service: CatAdsService
):
    """Обработка прошедшего модерацию"""
    # Убрать повторяющиеся части!
    comment = message.text
    data = await state.get_data()
    ads_id: int = data.get('ads_id')
    try:
        await cat_ads_service.moderate_ad_message(
            ads_id=ads_id, comment=comment, status=AdStatus.APPROVED
        )
    except Exception as e:
        logger.critical(
            'Не получилось обновить статус сообщения прошедшего модерацию %s', e
        )
        return message.answer(f'Не удалось произвести модерацию объявления! {e}')
    else:
        await state.clear()
        return await message.answer('Объявление в очереди на размещение!')


@admin_router.message(AdminModerateStates.reject, F.text != ActionButtons.CANCEL.value.name)
async def ads_reject_state(
        message: Message, state: FSMContext, tg_user: User, db: AsyncSession, cat_ads_service: CatAdsService
):
    """Обработка не прошедшего модерацию сообщения"""
    # Убрать повторяющиеся части!
    comment = message.text
    data = await state.get_data()
    ads_id = data.get('ads_id')
    try:
        await cat_ads_service.moderate_ad_message(
            ads_id=ads_id, comment=comment, status=AdStatus.REJECTED
        )
    except Exception as e:
        logger.critical(
            'Не получилось обновить статус сообщения - прошедшего модерацию %s', e
        )
        return message.answer(f'Не удалось произвести модерацию объявления! {e}')
    await state.clear()
    return await message.answer('Объявление в очереди на отправку!')


@admin_router.message(AdminModerateStates.bane, F.text != ActionButtons.CANCEL.value.name)
async def ads_bane_state(message: Message, state: FSMContext, tg_user: User, db: AsyncSession):
    """Обработка бана пользователя и удаления рекламного сообщения"""
    # Убрать повторяющиеся части!
    comment = message.text
    data = await state.get_data()
    author_id = data.get('author_id')
    ads_id = data.get('ads_id')
    try:
        user = await User.one_or_none(session=db, id=author_id)
        if not user:
            raise ValueError(f'Пользователь с id: {author_id} не найден! ')
        user.is_banned = True
        db.add(user)
        try:
            await db.execute(delete(CatAd).where(CatAd.id == ads_id))
        except Exception as e:
            raise ValueError('Не смог удалить пост забаненного пользователя {}'.format(e))
        await db.flush()
    except Exception as e:
        logger.critical(
            'Ошибка во время добавления пользователя в бан {}'.format(e)
        )
        await message.answer('Ошибка во время добавления пользователя в бан {}'.format(e))
    else:
        try:
            await message.bot.send_message(chat_id=author_id, text=f'Вы были забанены. Причина: {comment}')
        except Exception as e:
            logger.error('Не удалось отправить сообщение пользователю %s', e)
            return await message.answer('Пользователь забанен, но оповестить его не получилось')
    await message.answer('Пользователь забанен.')
    return await state.clear()
