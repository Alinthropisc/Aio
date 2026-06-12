from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from config import RedisSettings
from core.cache import RedisClient


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis(self, settings: RedisSettings) -> AsyncIterator[RedisClient]:
        client = RedisClient(
            url=settings.url,
            max_connections=settings.max_connections,
            decode_responses=settings.decode_responses,
        )
        yield client
        await client.close()
