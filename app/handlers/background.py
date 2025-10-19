import asyncio
from aiogram import Bot, Router
from datetime import datetime
import logging

from config import settings
from database.db import get_db_session, get_db_session_directly
from services.ads import CatAdsService
from utils.cache import RedisCache

# Создаем отдельный роутер для фоновых задач
background_router = Router()



@background_router.startup()
async def start_moderation_watcher(bot: Bot):
    """
    Запускается при старте бота и работает в фоне
    """
    logging.info("Модерационный вотчер запущен")

    async with get_db_session() as session:
        async with RedisCache() as redis_cache:
            cat_ads_service = CatAdsService(session, cache_storage=redis_cache, bot=bot)
            asyncio.create_task(
                moderation_watcher(cat_ads_service)
            )


async def moderation_watcher(cat_ads_service: CatAdsService):
    """
    Фоновая задача для периодической проверки базы
    """
    while True:
        try:
            await cat_ads_service.check_pending_ads()
            await asyncio.sleep(settings.CHECK_INTERVAL)
        except Exception as e:
            await cat_ads_service.bot.send_message(
                settings.ADMIN_ID, f'Ошибка обработки рекламных сообщений! {e}'[:1023]
            )
            logging.error(f" Ошибка в moderation_watcher: %s", e)
            await asyncio.sleep(settings.CHECK_INTERVAL)  # все равно ждем перед повторной попыткой