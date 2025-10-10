import json
from clients.redis import redis_client


class RedisCache:
    def __init__(self,  default_ttl=3600):
        self.client = redis_client
        self.default_ttl = default_ttl

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def set(self, key, value, ttl=None):
        """Кэширование строки"""
        ttl = ttl or self.default_ttl
        return await self.client.setex(key, ttl, value)

    async def get(self, key):
        """Получение строки"""
        return await self.client.get(key)

    async def set_json(self, key, data, ttl=None):
        """Кэширование JSON данных"""
        ttl = ttl or self.default_ttl
        json_data = json.dumps(data, ensure_ascii=False)
        return await self.client.setex(key, ttl, json_data)

    async def get_json(self, key):
        """Получение JSON данных"""
        data = await self.client.get(key)
        return json.loads(data) if data else None


    async def delete(self, key):
        """Удаление ключа"""
        return await self.client.delete(key)

    async def exists(self, key):
        """Проверка существования ключа"""
        return await self.client.exists(key)

    async def keys(self, pattern="*"):
        """Поиск ключей по паттерну"""
        return await self.client.keys(pattern)