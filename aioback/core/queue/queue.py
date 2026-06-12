import json
from datetime import datetime, timezone

import redis.asyncio as aioredis

from core.logging import Log

from .job import BaseJob


class Queue:
    """
    Redis-based очередь задач — паттерн Producer/Consumer.

    Использование:
        q = Queue(redis_client)

        # Добавить задачу
        await q.push(SendEmailJob(to="user@example.com"))

        # Добавить с задержкой (delayed job)
        await q.push(SendEmailJob(...), delay=60)

        # Получить задачу
        job = await q.pop("default")

        # Размер очереди
        size = await q.size("default")
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis
        self._log = Log.get("Queue")

    def _key(self, queue: str) -> str:
        return f"queue:{queue}"

    def _delayed_key(self, queue: str) -> str:
        return f"queue:{queue}:delayed"

    def _failed_key(self) -> str:
        return "queue:failed"

    async def push(self, job: BaseJob, delay: int = 0) -> str:
        """Добавляет job в очередь. delay в секундах — отложенный запуск."""
        payload = json.dumps(job.serialize())
        if delay > 0:
            score = datetime.now(timezone.utc).timestamp() + delay
            await self._redis.zadd(self._delayed_key(job.queue), {payload: score})
            self._log.debug(f"Delayed job queued: {job.__class__.__name__} id={job.id} delay={delay}s")
        else:
            await self._redis.lpush(self._key(job.queue), payload)
            self._log.debug(f"Job queued: {job.__class__.__name__} id={job.id} queue={job.queue}")
        return job.id

    async def pop(self, queue: str = "default", timeout: int = 5) -> BaseJob | None:
        """Получает следующий job из очереди (блокирует до timeout секунд)."""
        await self._move_delayed(queue)
        result = await self._redis.brpop(self._key(queue), timeout=timeout)
        if not result:
            return None
        _, payload = result
        data = json.loads(payload)
        return BaseJob.deserialize(data)

    async def _move_delayed(self, queue: str) -> None:
        """Перемещает готовые delayed jobs в основную очередь."""
        now = datetime.now(timezone.utc).timestamp()
        items = await self._redis.zrangebyscore(self._delayed_key(queue), 0, now)
        if not items:
            return
        pipe = self._redis.pipeline()
        for item in items:
            pipe.lpush(self._key(queue), item)
            pipe.zrem(self._delayed_key(queue), item)
        await pipe.execute()

    async def push_failed(self, job: BaseJob, error: str) -> None:
        job.error = error
        payload = json.dumps(job.serialize())
        await self._redis.lpush(self._failed_key(), payload)

    async def size(self, queue: str = "default") -> int:
        return await self._redis.llen(self._key(queue))

    async def clear(self, queue: str = "default") -> None:
        await self._redis.delete(self._key(queue))
        await self._redis.delete(self._delayed_key(queue))
