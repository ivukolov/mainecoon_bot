from logging import getLogger

from pydantic import BaseModel, Field, field_validator, ValidationError, model_validator, ConfigDict, field_serializer
from typing import Optional, List, Union, Any, Collection, Dict
from datetime import date, datetime
import re

from config import settings
from database import User
from database.blog.enums import AdStatus
from keyboards.lexicon import CatGenders

logger = getLogger(__name__)

class PhotoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    photo_id: str | None = None
    file_name: str | None = None
    file_path: str | None = None
    file_size : int | None = None
    sort_order: int = 0
    is_primary: bool = Field(default=False)




class BaseSchema(BaseModel):
    """"Базовая модель для всех типов рекламных акций"""
    bot_message_title: str | None = None
    author_id: int | None = None
    status: AdStatus = Field(default=AdStatus.NEW_BORN)
    photos: List[PhotoSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


    def add_photos(self, values: Collection[dict[str, Any]]) -> 'BaseSchema':
        for key, value in enumerate(values):
            self.photos.append(
                PhotoSchema(
                    photo_id=value.get('photo_id'),
                    file_name=value.get('file_name'),
                    file_path=value.get('file_path'),
                    file_size=value.get('file_size'),
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

    def get_photo_id_tuple(self) -> tuple[str, ...]:
        return tuple(foto.photo_id for foto in self.photos)

    def get_photos(self, is_sorted: bool=False) -> List[Dict[str, Any]]:
        """
        Метод возвращает словарь с дампом PhotoSchema
            Arguments:
                is_sorted: bool Сортирует фотографии перед выдачей
        """
        model_dump = self.model_dump(include={'photos'})['photos']
        if is_sorted:
            try:
                model_dump = sorted(model_dump,key=lambda x: (0 if x['is_primary'] else 1, x['sort_order']))
            except KeyError as e:
                logger.error('Ошибка сортировки фотографий %s', model_dump )
        return self.model_dump(include={'photos'})['photos']

    def getdata_without_photos(self, is_sorted=False):
        return self.model_dump(mode='python', exclude={'photos'})


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
    author_id: int | None = None


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
        header = self.bot_message_title
        return (
        f"{header}\n\n"
        f"🐱 Имя: {self.name}\n"
        f"⚧ Пол: {self.gender}\n"
        f"📅 Дата рождения: {self.birth_date}\n"
        f"🎨 Окрас: {self.color}\n"
        f"🏠 Питомник: {self.cattery}\n"
        f"💰 Цена: {self.price}\n"
        f"📞 Контакты: {self.contacts}"
    )