import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config import Settings


async def main():
    bot = Bot(token=Settings.BOT_TOKEN.value, parse_mode=ParseMode.HTML)
    storage = RedisStorage.from_url(
        f"redis://{Settings.REDIS_HOST.value}:{Settings.REDIS_PORT.value}"
    )
    dp = Dispatcher(storage=storage)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down")