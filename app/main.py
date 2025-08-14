import logging
import logging.config
from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.exceptions import TelegramServerError, TelegramNotFound

from config import settings
from handlers import routers, command_start_router

logger = getLogger(__name__)
logging.config.dictConfig(settings.LOGGING_CONFIG)

async def main():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = RedisStorage.from_url(settings.REDIS_STORAGE)
    dp = Dispatcher(storage=storage)
    # for router in routers:
    #     dp.include_router(router)
    dp.include_router(command_start_router)
    try:
        logger.info("Запуск бота")
        await dp.start_polling(bot)
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