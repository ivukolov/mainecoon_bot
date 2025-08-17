from enum import Enum


class UserRole(Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"