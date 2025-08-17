import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from config import settings
from database.db import Base
from database.db import engine, session_factory

# Загрузка конфигурации Alembic.
config = context.config

# Настройка логгера (если есть alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Установка target_metadata для миграций
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Миграции в offline-режиме (без подключения к БД)"""
    url = settings.DB_ENGINE
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()