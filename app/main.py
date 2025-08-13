import logging
from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.exceptions import TelegramServerError, TelegramNotFound

from config import settings
from loggers import BotLogger
from loggers.handlers import TelegramHandler, file_handler, setup_console_handler
from handlers import routers, command_start_router


async def main():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    _logger = BotLogger()
    handlers = (
        file_handler(),
        setup_console_handler()
        # TelegramHandler(bot)
    )
    _logger.manage_handlers(handlers)
    logger = _logger.get_logger()
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
    except TelegramServerError as e:
        logger.critical('telegram server error', exc_info=True)
    except TelegramNotFound as e:
        logger.critical(f'Не удаётся подключится к серерам telegram', exc_info=True)

if __name__ == "__main__":
    import asyncio
    logger = getLogger(__name__)
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)