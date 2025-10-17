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
    check_interval = 60  # проверка каждую минуту
    admin_chat_id = settings.ADMIN_ID
    while True:
        try:
            await check_pending_ads(cat_ads_service)
            await asyncio.sleep(check_interval)
        except Exception as e:
            logging.error(f" Ошибка в moderation_watcher: %s", e)
            await asyncio.sleep(check_interval)  # все равно ждем перед повторной попыткой


async def check_pending_ads(cat_ads_service: 'CatAdsService'):
    """
    Проверяет наличие непромодерированных объявлений
    """
    redis_cache = cat_ads_service.cache_storage
    try:
        # Получаем объявления не прошедшие модерацию.
        pending_cat_ads = await cat_ads_service.get_pending_moderation_ads()
        if pending_cat_ads:
            len_pending_ads = len(pending_cat_ads)
            print(pending_cat_ads)
            logging.info("Найдено %d объявления для модерации", len_pending_ads)

            for ad in pending_cat_ads:
                try:
                    # Отправляем объявление модератору
                    # await bot.send_message(
                    #     settings.ADMIN_ID, f'Найдены посты в кол-ве: {len_pending_ads} - '
                    #                        f'ожидающих модерацию'
                    # )

                    # # Помечаем как отправленное на модерацию
                    # await cat_ads_service.mark_as_sent_to_moderation(ad.id)

                    # Небольшая пауза между отправками
                    await asyncio.sleep(1)

                except Exception as e:
                    logging.error(f" Ошибка отправки объявления %d: %s", {ad.id}, e)

        else:
            logging.info("Нет новых объявлений на модерации")
            # Логируем только если есть что-то интересное
            # if datetime.now().minute == 0:  # раз в час
            #     logging.info("✅ Нет новых объявлений на модерации")

    except Exception as e:
        logging.error(f"Ошибка при проверке объявлений: %s ", e)