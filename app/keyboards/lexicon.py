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


class ActionButtons(StrEnum):
    CANCEL = "❌ Отмена"
    BACK = "⬅️ Назад"
    NEXT_PAGE = "Вперед ▶️"
    PREV_PAGE = "◀️ Назад"
    APPROVE = "✅ Одобрить"
    REJECT = "❌ Отклонить"
    BANE = "⛔ Забанить автора"
    MAIN_MENU = "Главное Меню"
    USER_JOIN = "Я вступил в группу"



class KeyboardBlog(Enum):
    BLOG_PSYCHOLOGY = TagButton(name='КотоПсихология 🧠', tag='#КотоПсихология')
    BLOG_EXHIBITIONS = TagButton(name='КотоВыставки 🎉',tag='#КотоВыставки')
    BLOG_NUTRITION = TagButton(name='КотоПитание 🍽', tag='#КотоПитание')
    BLOG_HEALTH = TagButton(name='КотоЗдоровье 🏥', tag='#КотоЗдоровье')

# ADMIN
class AdminMenu(Enum):
    ADD_INTERACTIVES = Button(name='Создать Интерактив')
    CHEK_POSTS = Button(name='Проверить актуальность постов в базе')
    PARSE_POSTS =  Button(name='Актуализировать все посты')
    ADD_NEW_POSTS =  Button(name='Добавить только новые посты')
    UPDATE_USERS =  Button(name='Обновить список пользователей')

class AdminInteractives(Enum):
    POLL = InteractivesButton(name='Создать голосование', callback='poll')
    QUIZ = InteractivesButton(name="Создать викторину", callback='quiz')
    COMPETITIONS = InteractivesButton(name="Создать голосование", callback='competitions')
