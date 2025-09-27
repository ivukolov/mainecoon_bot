from enum import Enum


class UserRole(Enum):
    """Роли пользователей"""
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"
    BOT = "BOT"