from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from database.db import AsyncSessionLocal


class DatabaseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async with AsyncSessionLocal() as session:
            # Добавляем сессию в request state
            request.state.db = session
            try:
                # Передаем запрос дальше
                response = await call_next(request)
                await session.commit()
            except Exception as e:
                # Откатываем изменения при ошибке
                await session.rollback()
                raise e
        return response