import jwt

class JwtExpiredException(jwt.ExpiredSignatureError):
    """Токен просрочен"""
    pass


class JwtInvalidException(jwt.InvalidTokenError):
    """Исключение для невалидных токенов"""
    pass

