from enum import StrEnum
from typing import List


class MainMenu(StrEnum):
    BLOG = "🐾 Блог (рубрики)"
    PARTNERS = "🛍 Партнёры и магазины"
    ADS = "📢 Объявления (купить/продать)"
    INTERACTIVITY = "🎉 Интерактивы (конкурсы)"
    ABOUT = "ℹ️ О канале"
    ADMIN = "👨🏻‍💻 Администрация"

class AdminMenu(StrEnum):
    CHEK_POSTS = 'Проверить актуальность постов в базе'
    PARSE_POSTS = 'Актуализировать посты'




class ActionButtons(StrEnum):
    CANCEL = "❌ Отмена"
    BACK = "⬅️ Назад"
    NEXT_PAGE = "Вперед ▶️"
    PREV_PAGE = "◀️ Назад"
    APPROVE = "✅ Одобрить"
    REJECT = "❌ Отклонить"
    BANE = "⛔ Забанить автора"
    MAIN_MENU = "Главное Меню"


class KeyboardBlog(StrEnum):
    BLOG_PSYCHOLOGY_BTN = 'КотоПсихология 🧠'
    BLOG_PSYCHOLOGY_TAG = '#КотоПсихология'
    BLOG_PSYCHOLOGY_CALLBACK = 'blog_psychology'

    BLOG_EXHIBITIONS_BTN = 'КотоВыставки 🎉'
    BLOG_EXHIBITIONS_TAG = '#КотоВыставки'
    BLOG_EXHIBITIONS_CALLBACK = 'blog_exhibitions'

    BLOG_NUTRITION_BTN = 'КотоПитание 🍽'
    BLOG_NUTRITION_TAG = '#КотоПитание'
    BLOG_NUTRITION_CALLBACK = 'blog_nutrition'

    BLOG_HEALTH_BTN = 'КотоЗдоровье 🏥'
    BLOG_HEALTH_TAG = '#КотоЗдоровье'
    BLOG_HEALTH_CALLBACK = 'blog_health'

    @classmethod
    def get_callback_list(cls):
        callback_list: List = []
        for name, member in cls.__members__.items():
            if name.endswith("_CALLBACK"):
                callback_list.append(member.value)
        return callback_list
