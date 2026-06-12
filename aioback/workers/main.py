import asyncio

from config import get_settings
from core.cache import RedisClient
from core.logging import Log
from core.queue import Queue, Worker


async def start_worker() -> None:
    settings = get_settings()
    Log.setup(debug=settings.app.is_debug, env=settings.app.env)

    redis = RedisClient(
        url=settings.redis.url,
        max_connections=settings.redis.max_connections,
        decode_responses=False,
    )
    queue = Queue(redis.client)
    worker = Worker(queue, queues=["default", "emails", "notifications"], concurrency=5)

    try:
        await worker.run()
    finally:
        await redis.close()


if __name__ == "__main__":
    asyncio.run(start_worker())
