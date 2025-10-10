from enum import Enum


class UserRole(Enum):
    """Роли пользователей"""
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"
    BOT = "BOT"

    @classmethod
    def get_role_name(cls, role) -> str:
        messages = {
            UserRole.ADMIN: "🛠️ Администратор",
            UserRole.USER: "👤 Пользователь",
            UserRole.BOT: "🤖 Бот",
        }
        return messages.get(role)
