from collections.abc import AsyncIterator

import redis.asyncio as aioredis


class RedisClient:
    def __init__(self, url: str, max_connections: int, decode_responses: bool) -> None:
        self._pool = aioredis.ConnectionPool.from_url(
            url,
            max_connections=max_connections,
            decode_responses=decode_responses,
        )
        self._client = aioredis.Redis(connection_pool=self._pool)

    @property
    def client(self) -> aioredis.Redis:
        return self._client

    async def ping(self) -> bool:
        try:
            return await self._client.ping()
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()
        await self._pool.aclose()


async def create_redis(url: str, max_connections: int, decode_responses: bool) -> AsyncIterator[RedisClient]:
    redis = RedisClient(url, max_connections, decode_responses)
    yield redis
    await redis.close()
