from enum import StrEnum, Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator, Field

from utils.parsers import TextParser


class Button(BaseModel):
    name: str


class TagButton(Button):
    tag: str = Field(..., description="Тэг для выборки из бд")

    @field_validator('tag', mode='after')
    @classmethod
    def tag_validate(cls, tag: str) -> str:
        if not tag:
            raise ValueError('Поле Tag не может быть пустым')
        return TextParser.tag_normalize(tag)





class MainMenu(Enum):
    BLOG = Button(name="🐾 Блог (рубрики)")
    PARTNERS = Button(name="🛍 Партнёры и магазины")
    ADS = Button(name="📢 Объявления (купить/продать)")
    INTERACTIVITY = Button(name="🎉 Интерактивы (конкурсы)")
    ABOUT = Button(name="ℹ️ О канале")
    ADMIN = Button(name="👨🏻‍💻 Администрация")


class AdminMenu(StrEnum):
    CHEK_POSTS = 'Проверить актуальность постов в базе'
    PARSE_POSTS = 'Актуализировать все посты'
    ADD_NEW_POSTS = 'Добавить только новые посты'
    UPDATE_USERS = 'Обновить список пользователей'


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


# class KeyboardBlog(StrEnum):
#     BLOG_PSYCHOLOGY_BTN = 'КотоПсихология 🧠'
#     BLOG_PSYCHOLOGY_TAG = '#КотоПсихология'
#     BLOG_PSYCHOLOGY_CALLBACK = 'blog_psychology'
#
#     BLOG_EXHIBITIONS_BTN = 'КотоВыставки 🎉'
#     BLOG_EXHIBITIONS_TAG = '#КотоВыставки'
#     BLOG_EXHIBITIONS_CALLBACK = 'blog_exhibitions'
#
#     BLOG_NUTRITION_BTN = 'КотоПитание 🍽'
#     BLOG_NUTRITION_TAG = '#КотоПитание'
#     BLOG_NUTRITION_CALLBACK = 'blog_nutrition'
#
#     BLOG_HEALTH_BTN = 'КотоЗдоровье 🏥'
#     BLOG_HEALTH_TAG = '#КотоЗдоровье'
#     BLOG_HEALTH_CALLBACK = 'blog_health'
#
#     @classmethod
#     def get_callback_list(cls):
#         callback_list: List = []
#         for name, member in cls.__members__.items():
#             if name.endswith("_CALLBACK"):
#                 callback_list.append(member.value)
#         return callback_list
