from logging import getLogger

from pydantic import BaseModel, Field, field_validator, ValidationError, model_validator, ConfigDict, field_serializer
from typing import Optional, List, Union
from datetime import date, datetime
import re

from config import settings
from database import User
from keyboards.lexicon import CatGenders

logger = getLogger(__name__)

class PhotoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    photo_id: str | None = None
    sort_order: int = 0
    is_primary: bool = Field(default=False)




class BaseSchema(BaseModel):
    """"Базовая модель для всех типов рекламных акций"""
    bot_message_title: str | None = None
    is_publicated: bool = False
    is_moderated: bool = False
    author_id: int | None = None
    photos: List[PhotoSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


    def add_photos(self, values: list) -> 'BaseSchema':
        for key, value in enumerate(values):
            self.photos.append(
                PhotoSchema(
                    photo_id=value,
                    sort_order=key,
                    is_primary = True if key == 0 else False,
                )
            )
        return self

    def sort_photos_with_primary_first(self, photos_list: dict):
        """Сортировка: основное фото первое, остальные по sort_order"""
        return sorted(
            photos_list,
            key=lambda x: (0 if x['is_primary'] else 1, x['sort_order'])
        )

    def get_photos(self, is_sorted=False):
        model_dump = self.model_dump(include={'photos'})['photos']
        if is_sorted:
            try:
                model_dump = sorted(model_dump,key=lambda x: (0 if x['is_primary'] else 1, x['sort_order']))
            except KeyError as e:
                logger.error('Ошибка сортировки фотографий %s', model_dump )
        return tuple(self.model_dump(include={'photos'})['photos'])



class CatAdsSchema(BaseSchema):
    model_config = ConfigDict(
        from_attributes=True,  # Разрешает загрузку из ORM объектов
        use_enum_values=True,  # Автоматически использует .value для enum
        arbitrary_types_allowed=True  # Разрешает произвольные типы
    )
    name: str | None = Field(
        None,
        max_length=settings.CAT_COLOR_MAX_LENGTH
    )

    gender: CatGenders|  str | None = None
    birth_date: str | date | None = None
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


    @field_serializer('gender')
    def validate_gender(self, value):
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