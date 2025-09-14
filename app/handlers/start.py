from io import BytesIO
from logging import getLogger
from collections import defaultdict

from telethon import TelegramClient
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.main_menu import blog_categories_kb, main_menu_kb, pagination_kb, admin_mine_menu_kb
from keyboards.lexicon import MainMenu, KeyboardBlog, ActionButtons
from database.users.models import User
from utils.parsers import get_media_form_message
from config import settings

command_start_router = Router()

logger = getLogger(__name__)

@command_start_router.message(CommandStart())
async def cmd_start(message: Message, db: AsyncSession, bot: Bot, tg_user: User):
    username = tg_user.username if tg_user else message.from_user.username
    if tg_user and tg_user.is_admin():
        return await message.answer("Привет Босс !", reply_markup=admin_mine_menu_kb())
    return await message.answer(
        f"Привет {username}! Я — бот канала «Мейн-куны в Воронеже».\n\n",
        reply_markup=main_menu_kb()
    )

@command_start_router.message(F.text == ActionButtons.MAIN_MENU)
async def main_menu_returner(message: Message, db: AsyncSession, tg_user: User, bot: Bot):
    if tg_user.is_admin():
        return await message.answer(
        text='Добро пожаловать в главное меню!',
        reply_markup=admin_mine_menu_kb()
    )
    return await message.answer(
        text='Добро пожаловать в главное меню!',
        reply_markup=main_menu_kb()
    )

@command_start_router.message(F.text == MainMenu.BLOG)
async def blog_menu(message: Message, bot: Bot , db: AsyncSession, teleton_client: TelegramClient):
    # hashtags = await get_hashtags_from_channel(bot=bot, message_limit=100)
    channel_username = -1001573169353

    # # Получаем entity канала
    # channel = await teleton_client.get_entity(channel_username)
    # async for mess in teleton_client.iter_messages(
    #         channel,
    #         limit=50,
    # ):
    #     text = mess.text
    #     if text:
    #         hashtags = re.findall(r'#КотоПсихология', text)
    #         if hashtags:
    #             print('ЭТО ХЭШТЕГ!!!!!!')
    #             print(mess.id)
    #             print('__________________________________________________________')
    #             print(text)
    #             print('__________________________________________________________')
    #
    #             return await message.answer(mess.text)
    #
    # return await message.answer('Ой! хэштеги не обнаружены!')

    await message.answer(f"Всё ок!", reply_markup=blog_categories_kb())


@command_start_router.callback_query(F.data.in_(KeyboardBlog.get_callback_list()) | F.data.startswith("blog_psychology_next"))
async def handle_blog_btn(callback_query: CallbackQuery, teleton_client: TelegramClient, bot: Bot):
    channel_username = -1001573169353
    channel = await teleton_client.get_entity(channel_username)
    page = 1
    page_size = 2
    offset = (page - 1) * page_size
    parsed_data = tuple
    media_group = defaultdict(list)
    await callback_query.answer()
    if callback_query.data == KeyboardBlog.BLOG_PSYCHOLOGY_CALLBACK:
        parsed_messages = [mess async for mess in teleton_client.iter_messages(
            channel,
            limit=3,
        )]

        messeges_id = (mess.id for mess in parsed_messages)
        for msg in parsed_messages:
            if msg.text:
                print(msg)

        # for msg_id in messeges_id:
        #     await bot.forward_message(
        #         chat_id=callback_query.message.chat.id, from_chat_id=channel_username, message_id=msg_id
        #     )


        # async for mess in teleton_client.iter_messages(
        #     channel,
        #     limit=3,
        #     add_offset=0,
        #     # search='Наш еженедельный разбор кормов по итогам голосования — тут! '
        # ):
        #     has_media = mess.photo or mess.video or mess.document
        #     has_text = mess.text
        #     text = mess.text
        #     print(mess.id)
            # await bot.forward_message(
            #     chat_id=target_chat_id,
            #     from_chat_id=source_chat_id,
            #     message_id=msg_id
            # )
            # if text:
            #     await callback_query.message.answer(text)
            # if has_media and has_text:
            #     await teleton_client.get_media_form_message(mess)
        #         # Получаем медиафайл
        #         file_data = BytesIO()
        #         if mess.photo:
        #             print(mess.photo)
        #             await teleton_client.download_media(mess.photo, file=file_data)
        #             file_data.seek(0)
        #             data = BufferedInputFile(
        #                     file=file_data.getvalue(),
        #                     filename="photo.jpg"
        #                 )
        #             await callback_query.message.reply_photo(photo=data, reply_to_message_id=callback_query.message.message_id, caption="Вот ваш пост 📸",)
        # await callback_query.message.answer(
    #         "Вы нажали кнопку blog_psychology!",
    #         reply_markup=pagination_kb(
    #             current_page=page,
    #             total_pages=page_size,
    #             prefix=KeyboardBlog.BLOG_PSYCHOLOGY_CALLBACK)
    #     )
    # elif callback_query.data == KeyboardBlog.BLOG_EXHIBITIONS_CALLBACK:
    #     await callback_query.message.answer("Вы нажали кнопку blog_exhibitions")
    # elif callback_query.data == KeyboardBlog.BLOG_NUTRITION_CALLBACK:
    #     await callback_query.message.answer("Вы нажали кнопку blog_nutrition")
    # elif callback_query.data == KeyboardBlog.BLOG_HEALTH_CALLBACK:
    #     await callback_query.message.answer("Вы нажали кнопку blog_health")