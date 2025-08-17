from datetime import date, datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

class BaseModel(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now())

    # def __repr__(self) -> str:
    #     values = ", ".join(
    #         [
    #             f"{column.name}={getattr(self, column.name)}"
    #             for column in self.__table__.columns.values()
    #         ],
    #     )
    #     return f"{self.__tablename__}({values})"