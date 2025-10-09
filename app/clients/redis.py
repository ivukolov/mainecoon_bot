import redis.asyncio as redis

from config import settings

redis_client =  redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    max_connections=10,
    password=None,  # Пароль
    decode_responses=True,  # автоматически декодировать в строки
)