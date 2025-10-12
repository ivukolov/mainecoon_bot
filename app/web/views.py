from sqladmin import ModelView

from database import User, Post, Category, Tag, TelegramSession
from database.users.roles import UserRole
from sqlalchemy import inspect
from sqlalchemy.orm import declared_attr

class ReadOnlyMixin:
    form_readonly_columns = ["created_at", "updated_at"]

class PostExcludeMixin:
    form_excluded_columns = ['posts', "created_at", "updated_at"]

class ColumnLabelsGeneratorMixin:
    @property
    def column_labels(self):
        """Автоматически генерирует labels для SQLAlchemy моделей"""
        labels = {}
        inspector = inspect(self.model)

        for column in inspector.columns:
            # Используем comment из колонки или генерируем из имени
            if hasattr(column, 'comment') and column.comment:
                labels[column.name] = column.comment
            else:
                labels[column.name] = self._format_column_name(column.name)

        return labels

    def _format_column_name(self, name: str) -> str:
        """Форматирует имя колонки в читаемый вид"""
        # Заменяем подчеркивания на пробелы и делаем заглавные буквы
        return name.replace('_', ' ').title()


class UserAdmin(ColumnLabelsGeneratorMixin, PostExcludeMixin, ReadOnlyMixin, ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = ['id', 'username', 'is_active', 'first_name', 'last_name', 'role', 'info', 'invited_users_count']
    form_columns = ['id', 'username', 'password', 'is_active', 'first_name', 'last_name', 'role', 'info']
    can_export = True
    column_sortable_list = ["id", 'role', 'is_active']
    column_default_sort = [('role', True), ('id', True)]
    column_searchable_list = ["id", "username", "first_name", "last_name"]
    # column_labels = {
    #     "password": "Пароль"
    # }
    field_labels = {
        "username": "Имя пользователя"
    }
    # column_formatters = {
    #     "is_active": lambda model, attr: "✅ Да" if model.is_active else "❌ Нет",
    #     "role": lambda model, attr: UserRole.get_role_name(model.role),
    # }
    form_groups = {
        "main_info": {
            "fields": ["username", "name", "is_active"],
            "label": "Основная информация"
        },
        "additional_info": {
            "fields": ["role", "info"],
            "label": "Дополнительная информация"
        },
        "system_info": {
            "fields": ["created_at"],
            "label": "Системная информация"
        }
    }
    async def on_model_change(self, data, model, is_created, request) -> None:
        if "password" in data:
            plain_password = data["password"]
            data["password"] = model.get_password_hash(plain_password)
        await super().on_model_change(data, model, is_created, request)

class CategoryAdmin(ColumnLabelsGeneratorMixin, PostExcludeMixin, ReadOnlyMixin, ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    column_list = ['id', 'name', 'slug']
    can_export = True


class TagAdmin(ColumnLabelsGeneratorMixin, PostExcludeMixin, ReadOnlyMixin, ModelView, model=Tag):
    name = "Тэг"
    name_plural = "Тэги"
    column_list = ['id', 'name']
    can_export = True

class TelegramSessionAdmin(ColumnLabelsGeneratorMixin, ReadOnlyMixin, ModelView, model=TelegramSession):
    name = "Сессия"
    name_plural = "Сессии"
    column_list = ['id', 'name']
    can_export = True

    form_widget_args = {
    "hash": {
        "type": "textarea",
        "rows": 10,
        "cols": 80
        },
    }



class PostAdmin(ColumnLabelsGeneratorMixin, ReadOnlyMixin, ModelView, model=Post):
    name = "Пост"
    name_plural = "Посты"
    column_list = ['id', 'views', 'forwards' ,'title', 'date']
    can_export = True
    column_sortable_list = ["id", "date", 'views', 'forwards']
    column_default_sort = [('id', True), ('views', True), ('forwards', True)]
    column_searchable_list = ["id", "title"]

    form_widget_args = {
    "message": {
        "type": "textarea",
        "rows": 10,
        "cols": 80
        },
    "views": {
        "type": "number",         # Числовое поле
        "min": 0,                 # Минимальное значение
        "step": 1                 # Шаг изменения
    },
    "forwards": {
        "type": "number",
        "min": 0,
        "step": 1
    },
    }