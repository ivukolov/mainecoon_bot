from sqlalchemy.exc import IntegrityError

class SelfInvitationError(Exception):
    """Попытка пригласить самого себя"""
    # telegram_message = "❌ Нельзя пригласить самого себя"

class DoubleSubscriptionError(IntegrityError):
    """Попытка подписаться дважды дважды"""


class InvitationError(ValueError):
    """Базовое исключение для ошибок приглашений"""


class InvalidReferralError(InvitationError):
    """Некорректное реферальное значение"""





class UserNotFoundError(InvitationError):
    """Пользователь не найден"""
    # telegram_message = "❌ Пригласивший вас пользователь не найден, попросите ещё раз отправить ссылку"

class UserNotFoundInGroupError(InvitationError):
    """Пользователь не найден в группе"""

