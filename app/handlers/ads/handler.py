from logging import getLogger
from typing import List

import sqlalchemy as sa
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_media_group import media_group_handler
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from keyboards.lexicon import MainMenu, CatGenders, AdsUserApprove
from keyboards import main_menu
from database import User
from services.ads import CatAdsService
from utils.bot_utils import get_referral, check_user_subscribe, get_group_login
from handlers.ads.states import CatForm
from handlers.ads import keyboards as ads_kb
from schemas.ads import CatAdsSchema

logger = getLogger(__name__)
logger.info(f'Инициализируем роутер {__name__}')

ads_router = Router()


@ads_router.callback_query(ads_kb.ReferralCheck.filter())
async def ads_handle_referral_invite(
        callback_query: CallbackQuery, callback_data: ads_kb.ReferralCheck, db: AsyncSession, tg_user: User
):
    """Обработка реферальной ссылки"""
    bot = callback_query.message.bot
    if tg_user.id == callback_data.referral:
        return await callback_query.message.answer('Нельзя пригласить самого себя')
    group_login = await get_group_login(bot)
    is_subscribe = await check_user_subscribe(bot=bot, user_id=tg_user.id)
    if is_subscribe:
        try:
            await tg_user.invite_user(referral=callback_data.referral, session=db)
        except sa.exc.IntegrityError:
            return await callback_query.message.answer('Нельзя принять инвайт дважды')
        except Exception:
            return await callback_query.message.answer(
                'Произошла неизвестная ошибка, обратитесь к администратору канала'
            )
        return await callback_query.message.answer(
            f"Реферальная ссылка обработана. Добро пожаловать в наше сообщество! {group_login}"
        )
    return await callback_query.message.answer(f"Вы не подписаны на группу {group_login}")


@ads_router.callback_query(F.data == ads_kb.AdsMenu.GET_REFERRAL.value.callback)
async def ads_referral_btn(callback_query: CallbackQuery, db: AsyncSession, tg_user: User):
    """Генерация реферальной ссылки"""
    bot = callback_query.message.bot
    bot_about = await bot.get_me()
    referral = get_referral(user_id=tg_user.id, bot_name=bot_about.username)
    return await callback_query.message.answer(f"Ваша реферальная ссылка {referral}")


@ads_router.callback_query(F.data == ads_kb.AdsMenu.DONATE.value.callback)
async def ads_donate_btn(callback_query: CallbackQuery, db: AsyncSession, tg_user: User):
    """Донат"""
    return await callback_query.message.answer(f"Спасибо что решили нас поддержать! ")


@ads_router.message(F.text == MainMenu.ADS.value.name)
async def ads_menu(message: Message, db: AsyncSession, tg_user: User, state: FSMContext):
    """Обработка кнопки меню"""
    users_count = await tg_user.get_invited_users_cnt(session=db)
    if users_count >= 0:
        await state.set_state(CatForm.name)
        return await message.answer(
            f'Поздравляем Вас, вы пригласили {settings.USERS_CNT} подписчиков, '
            f'пора забрать вашу награду! Заполните информацию: '
            f'\n\nВведите имя котика:', reply_markup=main_menu.cancel_kb()
        )
    return await message.answer(
        f"Для размещения рекламы вам нужно задонатить "
        f"{settings.DONATION_AMOUNT} руб. или пригласить {settings.USERS_CNT} "
        f"подписчиков. Текущее кол-во подписчиков: {users_count}",
        reply_markup=ads_kb.ads_publisher_kb()
    )


@ads_router.message(CatForm.name)
async def ads_process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    try:
        name = CatAdsSchema(name=message.text)
    except ValueError as e:
        logger.warning('Ошибка обработки имени %s', e)
        return await message.answer(
            f'Макс длинна: {settings.CAT_NAME_MAX_LENGTH} символов'
        )
    await state.update_data(name=message.text)
    await state.set_state(CatForm.gender)
    await message.answer("Выберите пол котика:", reply_markup=ads_kb.ads_cat_gender_kb())


@ads_router.message(CatForm.gender)
async def ads_process_gender(message: Message, state: FSMContext):
    """Обработка пола"""
    cat_genders: set = CatGenders.get_values()
    if message.text in cat_genders:
        gender = CatAdsSchema(gender=message.text)
        await state.update_data(gender=message.text)
        await state.set_state(CatForm.birth_date)
        return await message.answer(
            f"Введите дату рождения в формате: {settings.CAT_BIRTH_DATE_INFO}:",
            reply_markup=main_menu.cancel_kb()
        )
    return await message.answer(
        "Для выбора пола котика - воспользуйтесь кнопками", reply_markup=ads_kb.ads_cat_gender_kb()
    )


@ads_router.message(CatForm.birth_date)
async def ads_process_birth_date(message: Message, state: FSMContext):
    """Обработка даты рождения"""
    try:
        cat_data = CatAdsSchema(birth_date=message.text)
    except ValueError as e:
        return await message.answer(
            f'Некорректный формат даты, должна быть: {settings.CAT_BIRTH_DATE_INFO}:'
        )
    await state.update_data(birth_date=message.text)
    await state.set_state(CatForm.color)
    await message.answer("Введите окрас котика:", reply_markup=main_menu.cancel_kb())


@ads_router.message(CatForm.color)
async def ads_process_color(message: Message, state: FSMContext):
    """Обработка окраса"""
    try:
        CatAdsSchema(color=message.text)
    except ValueError:
        return await message.answer(
            f'Макс длинна: {settings.CAT_COLOR_MAX_LENGTH} символов'
        )

    await state.update_data(color=message.text)
    await state.set_state(CatForm.cattery)
    await message.answer("Введите название питомника:", reply_markup=main_menu.cancel_kb())


@ads_router.message(CatForm.cattery)
async def ads_process_cattery(message: Message, state: FSMContext):
    """Обработка питомника"""
    try:
        CatAdsSchema(cattery=message.text)
    except ValueError:
        return await message.answer(
            f'Макс длинна: {settings.CAT_CATTERY_MAX_LENGTH} символов'
        )
    await state.update_data(cattery=message.text)
    await state.set_state(CatForm.price)
    await message.answer("Введите цену котика:", reply_markup=main_menu.cancel_kb())


@ads_router.message(CatForm.price)
async def process_price(message: Message, state: FSMContext):
    """Обработка цены"""
    try:
        CatAdsSchema(price=message.text)
    except ValueError as e:
        return await message.answer(
            f'Цена должна быть числом'
        )
    await state.update_data(price=message.text)
    await state.set_state(CatForm.contacts)
    await message.answer("Введите контактные данные:", reply_markup=main_menu.cancel_kb())


@ads_router.message(CatForm.contacts)
async def ads_process_contacts(message: Message, state: FSMContext):
    """Обработка контактов"""
    try:
        CatAdsSchema(contacts=message.text)
    except ValueError as e:
        return await message.answer(
            f'Мин длинна:  {settings.CAT_CONTACTS_MIN_LENGTH} символов'
        )
    await state.update_data(contacts=message.text)
    await state.set_state(CatForm.photo)
    return await message.answer("Отправьте фото котика:", reply_markup=main_menu.cancel_kb())


@ads_router.message(CatForm.photo, F.media_group_id)
@media_group_handler()
async def ads_process_photos(messages: List[Message], state: FSMContext, cat_ads_service: CatAdsService):
    """Обработка медиа группы"""
    # Получаем фотографии самого лучшего качества
    photos = [m.photo[-1].file_id for m in messages]
    # Получаем данные из FSM
    data = await state.get_data()
    # Распаковываем в валидатор
    cat_ad_schema = CatAdsSchema(**data)
    # Добавляем фотографии
    cat_ad_schema.add_photos(photos)
    # Обновляем данные сформированным словарём
    await state.update_data(photos=cat_ad_schema.get_photos())
    # Формируем медисасообщение
    media_message = cat_ads_service.get_media_message_from_schema(cat_ad_schema)
    # Отправляем фото с подписью для проверки пользователю!
    await messages[-1].answer_media_group(media=media_message)
    await messages[-1].answer(
        'Внимательно всё проверьте перед отправкой!', reply_markup=ads_kb.ads_cat_send_to_moderate_kb()
    )
    return await state.set_state(CatForm.approve)


@ads_router.message(CatForm.photo, F.photo, F.media_group_id == None)
async def ads_process_photo(message: Message, state: FSMContext, cat_ads_service: CatAdsService):
    """Обработка фото"""
    # Получаем фотографии самого лучшего качества
    photo_id = message.photo[-1].file_id
    # Получаем данные из FSM
    data = await state.get_data()
    cat_ad_schema = CatAdsSchema(**data)
    cat_ad_schema.add_photos([photo_id, ])
    await state.update_data(photos=cat_ad_schema.get_photos())
    media_message = cat_ads_service.get_media_message_from_schema(cat_ad_schema)
    # Отправляем фото с подписью для проверки пользователю!
    await message.answer_media_group(
        media=media_message,
    )
    await message.answer(
        'Внимательно всё проверьте перед отправкой!', reply_markup=ads_kb.ads_cat_send_to_moderate_kb()
    )
    return await state.set_state(CatForm.approve)


@ads_router.message(CatForm.approve)
async def ads_approve(message: Message, state: FSMContext, tg_user: User, cat_ads_service: CatAdsService):
    data = await state.get_data()
    # await cat_ads_service.save_ad_message(data, author=tg_user)
    if message.text == AdsUserApprove.TO_MODERATE.value.name:
        await state.clear()
        await message.answer(
            'Рекламный пост отправлен но модерацию',
            reply_markup=main_menu.main_menu_kb()
        )
        await cat_ads_service.save_ad_message(data, author=tg_user)
    elif message.text == AdsUserApprove.REPEAT.value.name:
        await state.clear()
        await state.set_state(CatForm.name)
        await message.answer(
            'Введите имя кота',
            reply_markup=main_menu.cancel_kb()
        )
