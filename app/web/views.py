from sqladmin import ModelView

from database import User, Post, Category, Tag


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = [User.id, User.role, User.info]
    can_export = True


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    column_list = [Category.id, Category.name, Category.slug]
    can_export = True


class TagAdmin(ModelView, model=Tag):
    name = "Тэг"
    name_plural = "Тэги"
    column_list = [Tag.id, Tag.name, Tag.emoji]
    can_export = True