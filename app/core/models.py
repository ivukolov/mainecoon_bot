from datetime import date, datetime
import typing as T

import sqlalchemy as sa
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, Session
from sqlalchemy.ext.declarative import declarative_base

class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now())

    @classmethod
    async def get_or_create(cls, session, defaults=None, **kwargs):
        # Пытаемся найти существующую запись
        instance = await session.get(cls, kwargs)
        if instance:
            return instance, False

        # Объединяем аргументы поиска и значения по умолчанию
        instance_kwargs = kwargs | (defaults or {})

        # Создаём новый объект
        instance = cls(**instance_kwargs)
        session.add(instance)
        await session.commit()

        return instance, True