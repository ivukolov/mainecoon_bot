from aiogram import BaseMiddleware, types, Bot
from typing import Callable, Dict, Any, Awaitable

class BotMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
        data['bot'] = self.bot
        return await handler(event, data)