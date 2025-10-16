from pydantic import BaseModel, Field, field_validator, ValidationError, model_validator
from typing import Optional, List, Union
from datetime import date, datetime
import re

from config import settings
from database import User
from keyboards.lexicon import CatGenders


class BaseSchema(BaseModel):
    """"Базовая модель для всех типов рекламных акций"""
    bot_message_title: str | None = None
    is_publicated: bool = False
    is_moderated: bool = False
    photos: List[str] = []

    class Config:
        from_attributes = True



class CatAdsSchema(BaseSchema):
    name: str | None = Field(
        None,
        max_length=settings.CAT_COLOR_MAX_LENGTH
    )

    gender: CatGenders|  str | None = None
    birth_date: str | date | None | date = None
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

    @field_validator('gender', mode='after')
    def validate_gender(cls, value):
        return CatGenders.get_gender(value)

    @field_validator('price', mode='before')
    def validate_price(cls, v):
        if isinstance(v, str):
            v = v.strip().replace(',', '.')
        try:
            return float(v)
        except (ValueError, TypeError):
            raise ValueError('Цена должна быть числом')

    @field_validator('birth_date', mode='before')
    def validate_birth_date(cls, value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value.strip(), '%d.%m.%Y')
            except ValueError:
                raise ValueError(f'Неверный формат даты')

    def get_caption(self) -> str:
        return (
        "✅ Рекламный пост \n\n"
        f"🐱 Имя: {self.name}\n"
        f"⚧ Пол: {self.gender}\n"
        f"📅 Дата рождения: {self.birth_date}\n"
        f"🎨 Окрас: {self.color}\n"
        f"🏠 Питомник: {self.cattery}\n"
        f"💰 Цена: {self.price}\n"
        f"📞 Контакты: {self.contacts}"
    )