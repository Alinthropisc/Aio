from dataclasses import dataclass

from core.logging import Log
from core.queue import BaseJob


@dataclass
class LogJob(BaseJob):
    """
    Пример job — просто логирует сообщение.
    Используй как шаблон для своих задач.
    """

    queue: str = "default"
    max_retries: int = 1
    message: str = ""

    async def handle(self) -> None:
        log = Log.get("LogJob")
        log.info(f"Job executed: {self.message}")

    async def failed(self, exc: Exception) -> None:
        Log.error(f"LogJob permanently failed: {exc}")
