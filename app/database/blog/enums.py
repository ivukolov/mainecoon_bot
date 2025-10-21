from enum import Enum


class AdStatus(Enum):
    """Статусы объявлений"""
    NEW_BORN = "NEW_BORN" # Новые объявления
    AWAIT_MODERATING = "AWAIT_MODERATING" # Ожидают модерации
    APPROVED = "APPROVED" # Одобрены
    REJECTED = "REJECTED" # Отклонены
    PUBLICATED = "PUBLICATED" # Опубликованы

    @classmethod
    def is_processed(cls):
        """Returns:
        {cls.APPROVED, cls.REJECTED, cls.PUBLICATED}
        """
        return {cls.APPROVED, cls.REJECTED, cls.PUBLICATED}