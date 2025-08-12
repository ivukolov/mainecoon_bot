import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.config import settings
from app.loggers import BotLogger
from app.loggers.handlers import TelegramHandler, file_handler
from app.handlers import routers


async def main():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    _logger = BotLogger()
    handlers = (
        file_handler(),
        TelegramHandler(bot))
    _logger.manage_handlers(handlers)
    logger = _logger.get_logger()
    storage = RedisStorage.from_url(settings.REDIS_STORAGE)
    dp = Dispatcher(storage=storage)
    for router in routers:
        dp.include_router(router)
    try:
        logger.info("Запуск бота")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down")