import jwt
import datetime
from secrets import token_urlsafe

from config import settings

# Секретный ключ (хранить в env variables!)


async def generate_jwt_referral_code(user_id: str, expires_hours: int = 720, campaign: str = None) -> str:
    """
    Генерирует JWT токен для реферальной ссылки
    """
    payload = {
        'user_id': user_id,
        'campaign': campaign,
        'type': 'referral',
        'exp': (datetime.datetime.now() + datetime.timedelta(hours=expires_hours)).timestamp(),
        'iat': datetime.datetime.now().timestamp(),
        'jti': token_urlsafe(8)  # Unique token ID
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_jwt_referral_code(token: str) -> dict:
    """
    Проверяет JWT токен и возвращает payload
    Возвращает None если токен невалидный
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Токен истек")
        return None
    except jwt.InvalidTokenError:
        print("Невалидный токен")
        return None
