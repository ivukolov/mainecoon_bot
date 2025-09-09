import logging
import logging.config
from logging import getLogger

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.exceptions import TelegramServerError, TelegramNotFound
from fastapi import FastAPI
from sqladmin import Admin

from web.admin import app as fastapi_app, UserAdmin
from database.db import session_factory, engine
from middlewares import DatabaseMiddleware, BotMiddleware, TeletonClientMiddleware
from app.utils.parsers import TeletonClient
from config import settings
from handlers import routers, command_start_router

logger = getLogger(__name__)
logging.config.dictConfig(settings.LOGGING_CONFIG)

async def run_fastapi(app: FastAPI):
    """Запуск FastAPI сервера"""
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def run_bot(dp: Dispatcher, bot: Bot):
    """Запуск бота в режиме long polling"""
    await dp.start_polling(bot)

async def main():
    app = fastapi_app
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    # Инициализация клиента
    teletone = TeletonClient()
    # Проверка сессии в случае ошибки автоизация.
    await teletone.connection_check()
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = RedisStorage.from_url(settings.REDIS_STORAGE)
    dp = Dispatcher(storage=storage)
    # for router in routers:
    #     dp.include_router(router)
    dp.update.middleware(DatabaseMiddleware(session_factory))
    dp.update.middleware(BotMiddleware(bot))
    dp.update.middleware(TeletonClientMiddleware(teletone))
    dp.include_routers(routers)
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(run_fastapi(app))
            tg.create_task(run_bot(dp, bot))
        logger.info("Запуск бота")
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