import asyncio
from logging import getLogger
import typing as t
from pathlib import Path
from typing import Any, Coroutine

import os

import aiofiles
from aiofiles import os as async_os
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.client.session import aiohttp
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMember, ChatInviteLink, PhotoSize, Message, File

from schemas.dto import MediaType
from schemas.ads import PhotoSchema
from utils.cache import RedisCache
from database.users.models import User
from database.users.roles import UserRole
from config import settings
from exceptions.ads import DoubleSubscriptionError
from utils.identifiers import generate_uuid_from_str
from utils.files import save_file, get_images_paths, atomic_save_files

logger = getLogger(__name__)


def get_photo_name_from_file_id(file_id: str) -> str:
    """Получает  имя формата - сгенерированный UUID с расширением .jpg из file_id"""
    file_uuid = generate_uuid_from_str(file_id)
    extension = MediaType.PHOTO.value
    return f'{file_uuid}{extension}'


async def bot_save_photos_from_photo_id_list(bot: Bot, photo_id_list: t.Collection[str], directory: str) -> t.Dict[str, PhotoSchema]:
    """Сохраняет фото из сообщения
    Arguments:
         bot: Bot сущность из aiogram
         photo_id_list: Список telegram_id фотографии
         directory: Папка куда будет сохранён файл
    Returns:
         Возвращает словарь с 'photo_id': {file_name, file_path, file_size}
    Example:
        {
         'AgACAg...' : {
         'file_name': '2702fbe2-179e-57f2-b313-e8d1463d60a6.jpg',
         'file_path': 'images\\1382354642\\2702fbe2-179e-57f2-b313-e8d1463d60a6.jpg',
         'file_size': 139954
         },
     }
    """
    files_to_save: dict[str, t.BinaryIO] = {}
    result = {}
    for photo_id in photo_id_list:
        # Генерируем имя файла
        file_name = get_photo_name_from_file_id(photo_id)
        file: File | None = None
        # Получаем пути строка и объект Path
        local_path, global_path = get_images_paths(directory)
        # Получаем url путь
        local_file_path = os.path.join(local_path, file_name)
        # Получаем место сохранения файла
        global_file_path: Path = global_path / file_name
        file = await bot.get_file(photo_id)
        global_file_path_str = str(global_file_path)
        # Загружаем байты
        file_bytes = await bot.download_file(file.file_path)
        # Создаём словарь с параметрами для сохранения
        files_to_save[global_file_path_str] = file_bytes
        # except Exception as e:
        #     logger.error('Ошибка загрузки фото (%s) из tg %s', photo_id, e)
        is_created = await atomic_save_files(files_to_save)
        photo_schema= PhotoSchema(
            photo_id=photo_id,
            file_name=file_name if is_created else None,
            file_path=local_file_path if is_created else None,
            file_size=file.file_size if file else None,
        )
        result[photo_id]=photo_schema
    return result


# return {
#   'photo_id': file_id,
#   'file_name': file_name,
#   'file_path': result or local_file_path, # Если файл сохранился - передаём локальный путь
#   'file_size': file.file_size if result else None,
# }


async def bot_send_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': settings.ADMIN_ID,
        'text': text
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()


async def get_updates(offset=None):
    url = url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getUpdates"
    params = {
        'timeout': 30,  # Long polling timeout
        'offset': offset
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('result', [])
            else:
                print(f"Error: {response.status}")
                return []


async def get_confirm_code():
    cash = RedisCache()
    redis_key = f"{settings.ADMIN_ID}_teletone_code"
    cached_keys = await cash.fetch_json(redis_key)
    last_update_id = cached_keys.get('last_update_id') if cached_keys else 1
    await bot_send_message('Введите telegram код')
    while True:
        try:
            updates = await get_updates(last_update_id)
            for update in updates:
                last_update_id = update['update_id'] + 1
                message = update.get('message')
                if message and message.get('chat'):
                    chat_id = message['chat'].get('id')
                    if chat_id == settings.ADMIN_ID:
                        code = message.get('text')
                        try:
                            code = str(code.strip())
                        except ValueError:
                            await bot_send_message('Код должен быть в виде цифр')
                            continue
                        except Exception as e:
                            await bot_send_message(f'Неизвестная ошибка {e}, попробуйте ещё раз')
                            continue
                        data = {'code': [code], 'last_update_id': last_update_id}
                        await cash.put_json(redis_key, data)
                        await bot_send_message('Код принят, обрабатываем!')
                        return code
        except Exception as e:
            logger.error(f"Error: {e}")
            await asyncio.sleep(5)


async def get_or_create_admin_user(session: AsyncSession) -> User:
    admin, _ = await User.get_or_create(
        session=session,
        id=settings.ADMIN_ID,
        defaults={
            'username': settings.ADMIN_USERNAME,
            'is_active': True,
            'role': UserRole.ADMIN,
            'password': User.get_password_hash(settings.ADMIN_PASSWORD)
        }
    )
    return admin


def get_tg_username(username):
    return f"@{username}"


def reverse_tg_url(login: str) -> str:
    return f"https://t.me/{login}"


async def get_group_login(bot: Bot) -> str:
    chat = await bot.get_chat(settings.CHANNEL_ID)
    return f"@{chat.username}"


def get_referral(user_id: int, bot_name: str) -> str:
    return f"https://t.me/{bot_name}?start={user_id}"


def check_referral(user_id: int, referral: str) -> int:
    try:
        referral = int(referral)
    except ValueError:
        raise ValueError('Некорректное реферальное значение')
    if user_id == referral:
        raise ValueError('❌ Нельзя пригласить самого себя')
    return referral


async def get_invite_link(bot: Bot) -> ChatInviteLink:
    return await bot.create_chat_invite_link(settings.CHANNEL_ID)


async def check_user_subscribe(user_id, bot: Bot) -> bool:
    try:
        member: ChatMember = await bot.get_chat_member(settings.CHANNEL_ID, user_id)
        return member.status not in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED}
    except DoubleSubscriptionError as e:
        logger.error('Ошибка получения информации о пользователе из группы', exc_info=True)
        raise DoubleSubscriptionError from e
