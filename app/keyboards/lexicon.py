from enum import StrEnum, Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator, Field

from utils.parsers import TextParser


class Button(BaseModel):
    name: str

class CallbackButton(Button):
    callback: str = Field(..., description="callback data")

class TagButton(Button):
    tag: str = Field(..., description="Тэг для выборки из бд")

    @field_validator('tag', mode='after')
    @classmethod
    def tag_validate(cls, tag: str) -> str:
        if not tag:
            raise ValueError('Поле Tag не может быть пустым')
        return TextParser.tag_normalize(tag)


class AdsButton(CallbackButton):
    """Кнопки для рекламы"""


class InteractivesButton(CallbackButton):
    """Кнопки для админ меню"""


class CatGenders(Enum):
    MALE = 'Мальчик'
    FEMALE = 'Девочка'

    @classmethod
    def get_values(cls) -> set[str]:
        return {gender.value for gender in cls}

    @classmethod
    def get_gender(self, gender_name: str) -> 'CatGenders':
        genders_dict = {gender.value: gender for gender in self}
        return genders_dict[gender_name]


class MainMenu(Enum):
    BLOG = Button(name="🐾 Блог (рубрики)")
    PARTNERS = Button(name="🛍 Партнёры и магазины")
    ADS = Button(name="📢 Объявления (купить/продать)")
    INTERACTIVES = Button(name="🎉 Интерактивы (конкурсы)")
    ABOUT = Button(name="ℹ️ О канале")
    ADMIN = Button(name="👨🏻‍💻 Администрация")


class AdsMenu(Enum):
    GET_REFERRAL = AdsButton(name='Получить реферальную ссылку', callback='get_referral')
    DONATE = AdsButton(name='Оплатить', callback='donate')

class AdsUserApprove(Enum):
    TO_MODERATE = Button(name='✅ Отправить на модерацию')
    REPEAT = Button(name='✏️ Заполнить заново')


class ActionButtons(Enum):
    CANCEL = Button(name="❌ Отмена" )
    BACK = Button(name="⬅️ Назад")
    NEXT_PAGE = Button(name="Вперед ▶️")
    PREV_PAGE = Button(name="◀️ Назад")
    APPROVE = Button(name="✅ Одобрить")
    REJECT = Button(name="❌ Отклонить")
    BANE = Button(name="⛔ Забанить автора")
    MAIN_MENU = Button(name="Главное Меню")
    USER_JOIN = Button(name="Я вступил в группу")



class KeyboardBlog(Enum):
    BLOG_PSYCHOLOGY = TagButton(name='КотоПсихология 🧠', tag='#КотоПсихология')
    BLOG_EXHIBITIONS = TagButton(name='КотоВыставки 🎉',tag='#КотоВыставки')
    BLOG_NUTRITION = TagButton(name='КотоПитание 🍽', tag='#КотоПитание')
    BLOG_HEALTH = TagButton(name='КотоЗдоровье 🏥', tag='#КотоЗдоровье')

# ADMIN
class AdminMenu(Enum):
    ADD_INTERACTIVES = Button(name='Создать Интерактив')
    PARSE_POSTS =  Button(name='Актуализировать все посты')
    UPDATE_USERS =  Button(name='Обновить список пользователей')

class AdminInteractives(Enum):
    POLL = InteractivesButton(name='Создать голосование', callback='poll')
    QUIZ = InteractivesButton(name="Создать викторину", callback='quiz')
    COMPETITIONS = InteractivesButton(name="Создать голосование", callback='competitions')
