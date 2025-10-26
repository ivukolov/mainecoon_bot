from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from clients.teletone import TeletonClientManager
from config import settings
from database import User
from services.messages import MessagesService
from services.users import UsersService
from services.teletone import TeletonService


logger = getLogger(__name__)

scheduler = AsyncIOScheduler()

async def every_day_schedule(teleton_manager: TeletonClientManager, db: AsyncSession):
    hour, minute = settings.TG_GROUP_UPDATE_TIME
    async with db as session:
        scheduler.add_job(run_every_day_parsing, CronTrigger(hour=hour, minute=minute), args=[teleton_manager, session])
        scheduler.start()



async def run_every_day_parsing(teleton_manager: TeletonClientManager, db: AsyncSession):
    """Задача для ежедневного обновления постов и пользователей"""
    try:
        teleton_client = await teleton_manager.get_client()
        teleton_manager = TeletonService(teleton_client)
    except Exception as e:
        logger.critical(
            'Не удалось получить инициализировать клиент teleton для ежедневного парсинга! {}'.format(e)
        )
        return
    try:
        parsed_messages = await teleton_manager.get_all_chanel_messages()
    except Exception as e:
        logger.critical(
            'Во время ежедневного обновления информации о постах возникал ошибка: {}'.format(e)
        )
    else:
        try:
            message_service = MessagesService(session=db, messages=parsed_messages, is_aiogram=False)
            saved_messages = await message_service.service_and_save_messages()
            if saved_messages.error_count == 0:
                logger.info(
                    'Все посты актуализированные'
                )
            else:
                logger.error('Во время актуализации постов возникла ошибка!'
                             'обработано корректно: {}, c ошибкой: {}'.format(
                    saved_messages.text_messages_count,
                    saved_messages.error_count
                )
                )
        except Exception as e:
            logger.critical('Не удалось загрузить сообщения из канала группы: {}'.format(e))
    try:
        parsed_users = await teleton_manager.get_all_channel_users()
    except PermissionError as e:
        logger.critical(e)
    except Exception as e:
        logger.critical(
            'Ошибка во время ежедневного обновления информации о пользователях'.format(e)
        )
    else:
        try:
            users_service = UsersService(session=db, users=parsed_users)
            await users_service.service_and_save_users()
        except PermissionError as e:
            logger.critical(e)
        except Exception as e:
            logger.critical(e)