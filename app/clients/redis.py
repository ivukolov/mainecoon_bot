import typing as t

from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from config import settings

def get_redis_client(
        url: t.Optional[str] = None,
        connection_kwargs: t.Optional[t.Dict[str, t.Any]] = None,
        **kwargs: t.Any
) -> Redis:
    if url is None:
        url = settings.REDIS_CASE_STORAGE
    if connection_kwargs is None:
        connection_kwargs = {}
    pool = ConnectionPool.from_url(url, **connection_kwargs)
    return Redis(connection_pool=pool, **kwargs)

redis_client =  Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    max_connections=10,
    password=None,  # Пароль
    decode_responses=True,  # автоматически декодировать в строки
)