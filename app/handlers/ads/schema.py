from pydantic import BaseModel, Field, field_validator, ValidationError, model_validator
from typing import Optional
from datetime import date, datetime
import re

from config import settings

class BaseData(BaseModel):
    """"Базовая модель для всех типов рекламных акций"""



class CatData(BaseData):
    name: str | None = Field(
        None,
        max_length=settings.CAT_COLOR_MAX_LENGTH
    )

    gender: str | None = None
    birth_date: str | None | date = None
    color: str | None = Field(
        None,
        max_length=settings.CAT_NAME_MAX_LENGTH
    )
    cattery: str | None = Field(
        None,
        max_length=settings.CAT_NAME_MAX_LENGTH
    )
    price: float | str | None = Field(
        None,
        gt=0
    )
    contacts: str | None = Field(
        None,
        min_length=settings.CAT_CONTACTS_MIN_LENGTH
    )
    photo_id: str | None = None
    autor_id: int | None = None


    @field_validator('birth_date', mode='before')
    def validate_birth_date(cls, value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                datetime.strptime(value.strip(), '%d.%m.%Y')
                return value
            except ValueError:
                raise ValueError(f'Неверный формат даты')

    @field_validator('price', mode='before')
    def validate_price(cls, v):
        if isinstance(v, str):
            v = v.strip().replace(',', '.')
        try:
            return float(v)
        except (ValueError, TypeError):
            raise ValueError('Цена должна быть числом')
