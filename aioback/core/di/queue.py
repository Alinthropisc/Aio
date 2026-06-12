from dishka import Provider, Scope, provide

from core.cache import RedisClient
from core.queue import Queue, Worker


class QueueProvider(Provider):
    @provide(scope=Scope.APP)
    def get_queue(self, redis: RedisClient) -> Queue:
        return Queue(redis.client)

    @provide(scope=Scope.APP)
    def get_worker(self, queue: Queue) -> Worker:
        return Worker(queue, queues=["default", "emails", "notifications"])
