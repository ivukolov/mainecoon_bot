import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config import Settings
from custom_logger import BotLogger, TelegramHandler


async def main():
    bot = Bot(token=Settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    _logger = BotLogger()
    handlers = [_logger.file_handler(), TelegramHandler(bot)]
    _logger.manage_handlers(handlers)
    logger = _logger.get_logger()
    storage = RedisStorage.from_url(
        f"redis://{Settings.REDIS_HOST}:{Settings.REDIS_PORT}"
    )
    dp = Dispatcher(storage=storage)
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