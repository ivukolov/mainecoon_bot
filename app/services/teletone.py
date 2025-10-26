from logging import getLogger

from telethon import TelegramClient

from clients.teletone import TeletonClientManager

from config import settings

logger = getLogger(__name__)


class TeletonService:
    def __init__(self, teletone_client: TelegramClient):
        self.teleton_client = teletone_client

    async def _get_entity(self, channel_id: int | None = None):
        if channel_id is None:
            channel_id = settings.CHANNEL_ID
        channel = await self.teleton_client.get_entity(channel_id)
        return channel

    async def get_all_chanel_messages(self) -> list:
        try:
            channel = await self._get_entity()
            logger.info('Запущен процесс обновления постов и тэгов')
            parsed_messages = [
                m async for m in self.teleton_client.iter_messages(
                    channel,
                    limit=None,
                )
            ]
            logger.info(f'Из канала загружено {len(parsed_messages)} постов, приступаю к обработке')
            return parsed_messages
        except Exception as e:
            raise ValueError('Не удалось обновить информацию о постах') from e

    async def get_all_channel_users(self) -> list:
        try:
            channel = await self._get_entity()
            chat = await self.teleton_client.get_permissions(channel, await self.teleton_client.get_me())
            if not chat.is_admin:
                logger.critical('У клиента недостаточно прав для получения информации о пользователях')
                raise PermissionError('Вы не является администратором группы для сбора информации о пользователях!')
            parsed_users = [u async for u in self.teleton_client.iter_participants(channel, limit=None)]
            logger.info(f'Из канала загружено {len(parsed_users)} пользователей, приступаю к обработке')
            return parsed_users
        except Exception as e:
            raise ValueError('Не удалось получить информацию о пользователях группы') from e

