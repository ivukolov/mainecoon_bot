from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import settings

engine: AsyncEngine = create_async_engine(settings.DB_ENGINE)
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False
)
session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Автоматический коммит при успехе
        except Exception:
            await session.rollback()  # Роллбэк при ошибке
            raise


async def get_db_session_directly():
    """Создать сессию напрямую"""
    return AsyncSessionLocal()
