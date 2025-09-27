import logging
from datetime import date, datetime
import typing as t

import sqlalchemy as sa
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import InstrumentedList

logger = logging.getLogger(__name__)

class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now())

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs) -> t.Optional[int]:
        stmt = sa.select(cls).filter_by(**kwargs)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()
        return instance


    @classmethod
    async def get_or_create(cls, session: AsyncSession, defaults=None, **kwargs):
        # Пытаемся найти существующую запись
        query = sa.select(cls).filter_by(**kwargs)
        result = await session.execute(query)
        instance = result.scalar_one_or_none()
        # instance = await session.get(cls, kwargs)
        if instance:
            return instance, False

        # Объединяем аргументы поиска и значения по умолчанию
        instance_kwargs = kwargs | (defaults or {})

        # Создаём новый объект
        instance = cls(**instance_kwargs)
        session.add(instance)
        await session.commit()

        return instance, True

    @classmethod
    async def create_or_update(cls, session: AsyncSession, defaults=None, **kwargs):
        try:
            query = sa.select(cls).filter_by(**kwargs)
            result = await session.execute(query)
            instance = result.scalar_one_or_none()

            if instance:
                # Обновляем существующую запись
                if defaults:
                    for key, value in defaults.items():
                        attr = getattr(instance, key)

                        if isinstance(attr, InstrumentedList):
                            # Для отношений: очищаем и добавляем новые элементы
                            if value:
                                attr.clear()
                                attr.extend(value)
                        else:
                            # Для обычных атрибутов
                            setattr(instance, key, value)
                updated = True
            else:
                # Создаём новую запись
                create_data = kwargs.copy()
                if defaults:
                    create_data.update(defaults)
                instance = cls(**create_data)
                session.add(instance)
                updated = False

            await session.flush()
            await session.refresh(instance)
            return instance, not updated  # True если создан, False если обновлен

        except Exception as e:
            logger.error(e)
            await session.rollback()
            raise e
