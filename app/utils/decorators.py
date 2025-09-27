import time
from functools import wraps
from logging import getLogger
from aiogram import types
from typing import Callable, Any

logger = getLogger(__name__)

def async_timer(func):
    """
    Декоратор, который засекает время выполнения функции.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        logger.info(f"Функция {func.__name__} выполнилась за {end_time - start_time:.4f} секунд")
        return result
    return wrapper


def admin_required(handler: Callable) -> Callable:
    """
    Декоратор, который проверяет, является ли пользователь администратором
    """

    @wraps(handler)
    async def wrapper(message: types.Message, tg_user=None, *args, **kwargs) -> Any:
        if tg_user and tg_user.is_admin:
            return await handler(message=message, tg_user=tg_user, *args, **kwargs)
        # Проверяем наличие пользователя
        await message.answer("❌ Доступ запрещён. Требуются права администратора.")
        logger.warning(f'Попытка доступка к админ панели от пользователя {message.from_user}')
        return

    return wrapper