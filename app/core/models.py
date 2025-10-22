import logging
from datetime import date, datetime, timezone
import typing as t
from decimal import Decimal

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.dialects.postgresql import insert as pg_insert

logger = logging.getLogger(__name__)

T = t.TypeVar('T', bound='BaseModel')

class BaseModelNoID(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        comment='Дата создания'
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        comment='Дата обновления'
    )

    @classmethod
    async def on_conflict_do_update(cls, session, dict_list, exclude_fields: set = None):
        """Асинхронный update пользователя"""
        if not exclude_fields:
            exclude_fields = {'id'}

        all_fields = set(cls.__table__.columns.keys())
        update_fields = all_fields - exclude_fields

        stmt = pg_insert(cls).values(dict_list)

        set_dict = {}
        for field in update_fields:
            set_dict[field] = getattr(stmt.excluded, field)

        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=set_dict
        )

        try:
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f'Ошибка сохранения данных {e}')
            raise ValueError(f'Ошибка сохранения данных {e}')

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs) -> t.Optional[T]:
        stmt = sa.select(cls).filter_by(**kwargs)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()
        return instance


    @classmethod
    async def get_or_create(cls, session: AsyncSession, defaults=None, **kwargs)-> t.Union[T, False]:
        # Пытаемся найти существующую запись
        query = sa.select(cls).filter_by(**kwargs)
        result = await session.execute(query)
        instance = result.scalar_one_or_none()
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
    async def create_or_update(cls, session: AsyncSession, defaults=None, **kwargs) -> t.Union[T, False]:
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
            logger.error(f"Ошибка в работе метода create_or_update {e}", exc_info=True)
            await session.rollback()
            raise e

class BaseModel(BaseModelNoID):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
