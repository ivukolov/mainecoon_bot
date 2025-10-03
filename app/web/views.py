from sqladmin import ModelView

from database import User, Post, Category, Tag
from sqlalchemy.orm import declared_attr


class PostExcludeMixin:
    form_excluded_columns = ['posts']


class UserAdmin(PostExcludeMixin, ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = ['id', 'is_active', 'first_name', 'last_name', 'role', 'info']
    form_columns = ['id', 'is_active', 'first_name', 'last_name', 'role', 'info']
    can_export = True


class CategoryAdmin(PostExcludeMixin, ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    column_list = ['id', 'name', 'slug']
    can_export = True


class TagAdmin(PostExcludeMixin, ModelView, model=Tag):
    name = "Тэг"
    name_plural = "Тэги"
    column_list = ['id', 'name', 'emoji']
    can_export = True


class PostAdmin(ModelView, model=Post):
    name = "Пост"
    name_plural = "Посты"
    column_list = ['id', 'views', 'forwards' ,'title', 'date']
    can_export = True
    column_sortable_list = ["id", "date", 'views', 'forwards']
    column_default_sort = [('id', True), ('views', True), ('forwards', True)]
    column_searchable_list = ["id", "title"]