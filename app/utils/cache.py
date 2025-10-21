import json
import typing as t
from logging import getLogger

from clients.redis import get_redis_client

logger = getLogger(__name__)

class RedisCache:
    def __init__(self,  default_ttl=3600):
        self.client = get_redis_client()
        self.default_ttl = default_ttl

    async def __aenter__(self):
        self.client = get_redis_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()  # Правильное закрытие соединения

    async def put_str(self, key, value, ttl=None):
        """Кэширование строки"""
        ttl = ttl or self.default_ttl
        return await self.client.setex(key, ttl, value)

    async def fetch_str(self, key):
        """Получение строки"""
        return await self.client.get(key)

    async def put_json(self, key, data, ttl=None):
        """Кэширование JSON данных"""
        ttl = ttl or self.default_ttl
        json_data = json.dumps(data, ensure_ascii=False)
        return await self.client.setex(key, ttl, json_data)

    async def fetch_json(self, key):
        """Получение JSON данных"""
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def put_set(self, key, data: set, ttl=None):
        """Кэширование set данных"""
        ttl = ttl or self.default_ttl
        await self.client.sadd(key, *data)
        return await self.client.expire(key, ttl)

    async def fetch_set(self, key) -> set[t.Any]:
        """Получение set данных"""
        return await self.client.smembers(key)

    async def rem_set(self, key, *args) -> t.Any:
        """Удаляет значение из множества"""
        return await self.client.srem(key, *args)

    async def fetch_set_with_int(self, key) -> set[int]:
        """преобразовывает все значения из set в int
        Arguments:
            key: ключ для получения данных
        Returns:
            Возвращяет set с int внутри

        """
        values = await self.client.smembers(key)
        if values:
            try:
                values = {int(value) for value in values}
            except (ValueError, TypeError):
               logger.error(f"Ошибка конвертации redis данных: {values}")
        return values


    async def put_list(self, key, data: list, ttl=None):
        """Кэширование списка данных"""
        ttl = ttl or self.default_ttl
        await self.client.lpush(key, *data)
        return await self.client.expire(key, ttl)

    async def list_append(self, key, data, ttl=None):
        """Добавляем значение в конец списка"""
        ttl = ttl or self.default_ttl
        await self.client.rpush(key, ttl, data)
        return await self.client.expire(key, ttl)

    async def delete(self, key):
        """Удаление ключа"""
        return await self.client.delete(key)

    async def exists(self, key):
        """Проверка существования ключа"""
        return await self.client.exists(key)

    async def keys(self, pattern="*"):
        """Поиск ключей по паттерну"""
        return await self.client.keys(pattern)