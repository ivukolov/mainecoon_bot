import logging
import logging.config
from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.exceptions import TelegramServerError, TelegramNotFound

from utils.bot_utils import bot_send_message
from database.db import session_factory, get_db_session_directly
from middlewares import (
    DatabaseMiddleware,
    BotMiddleware,
    TeletonClientMiddleware,
    UserMiddleware,
    CatAdsServiceMiddleware,
)
from clients.teletone import TeletonClientManager
from utils.cache import RedisCache
from utils.schedules import every_day_schedule
from web.app import run_fastapi
from config import settings
from handlers import routers

logger = getLogger(__name__)
logging.config.dictConfig(settings.LOGGING_CONFIG)

async def run_bot(dp: Dispatcher, bot: Bot):
    """Запуск бота в режиме long polling"""
    logger.info("Запуск бота")
    await dp.start_polling(bot)

async def main():
    # Инициализация клиента
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    cache_storage = RedisCache()
    storage = RedisStorage.from_url(settings.REDIS_AIOGRAM_STORAGE)
    dp = Dispatcher(storage=storage)
    for router in routers:
        dp.include_router(router)
    tt_client_manager = TeletonClientManager()
    try:
        # Попытка инициализации клиента
        await tt_client_manager.initialize_client()
    except Exception as e:
        await bot_send_message(f'Не удалось инициализировать клиент Teletone {e}')
        logger.error(
            "Не удалась инициализация клиента Teletone - "
            "продолжаем загрузку без него. Парсинг временно недоступен!",
            exc_info=True,
        )
    dp.update.middleware(TeletonClientMiddleware(tt_client_manager))
    dp.update.middleware(DatabaseMiddleware(session_factory))
    dp.update.middleware(UserMiddleware())
    dp.update.middleware(CatAdsServiceMiddleware(cache_storage=cache_storage, bot=bot))
    dp.update.middleware(BotMiddleware(bot))
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(run_fastapi())
            tg.create_task(run_bot(dp, bot))
            tg.create_task(every_day_schedule(teleton_manager=tt_client_manager, db=session_factory()))
    except KeyboardInterrupt:
        logger.info("Shutting down")
    except TelegramServerError:
        logger.critical('telegram server error', exc_info=True)
    except TelegramNotFound:
        logger.critical(f'Не удаётся подключится к серерам telegram')

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)