from enum import StrEnum


class MainMenu(StrEnum):
    BLOG = "🐾 Блог (рубрики)"
    PARTNERS = "🛍 Партнёры и магазины"
    ADS = "📢 Объявления (купить/продать)"
    INTERACTIVITY = "🎉 Интерактивы (конкурсы)"
    ABOUT = "ℹ️ О канале"


class ActionButtons(StrEnum):
    CANCEL = "❌ Отмена"
    BACK = "⬅️ Назад"
    NEXT_PAGE = "Вперед ▶️"
    PREV_PAGE = "◀️ Назад"
    APPROVE = "✅ Одобрить"
    REJECT = "❌ Отклонить"
    BANE = "⛔ Забанить автора"