import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class JobStatus(StrEnum):
    PENDING   = "pending"
    RUNNING   = "running"
    DONE      = "done"
    FAILED    = "failed"
    RETRYING  = "retrying"


@dataclass
class BaseJob(ABC):
    """
    Базовый Job — паттерн Command.
    Каждый job инкапсулирует одну задачу и знает как себя выполнить.

    Использование:
        class SendEmailJob(BaseJob):
            queue = "emails"
            max_retries = 3
            retry_delay = 60  # секунд

            async def handle(self) -> None:
                await mailer.send(self.to, self.subject, self.body)

        await queue.push(SendEmailJob(to="user@example.com", subject="Hi", body="..."))
    """

    # ── Настройки job (переопредели в дочернем классе) ────────────────────────
    queue: str = "default"
    max_retries: int = 3
    retry_delay: int = 5       # секунды между попытками
    timeout: int = 300         # максимальное время выполнения
    priority: int = 0          # выше = важнее

    # ── Автоматические поля ───────────────────────────────────────────────────
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = field(default=JobStatus.PENDING)
    attempts: int = field(default=0)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: datetime | None = field(default=None)
    error: str | None = field(default=None)

    @abstractmethod
    async def handle(self) -> None:
        """Основная логика задачи."""

    async def failed(self, exc: Exception) -> None:
        """Вызывается когда job провалился все попытки. Переопредели при необходимости."""

    async def on_retry(self, attempt: int, exc: Exception) -> None:
        """Вызывается перед каждой повторной попыткой."""

    def serialize(self) -> dict[str, Any]:
        import json
        data = {
            "id": self.id,
            "class": f"{self.__class__.__module__}.{self.__class__.__name__}",
            "queue": self.queue,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
            "priority": self.priority,
            "attempts": self.attempts,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "payload": {
                k: v for k, v in self.__dict__.items()
                if k not in {
                    "id", "class", "queue", "max_retries", "retry_delay",
                    "timeout", "priority", "attempts", "status",
                    "created_at", "scheduled_at", "error",
                }
            },
        }
        return data

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "BaseJob":
        import importlib
        module_path, class_name = data["class"].rsplit(".", 1)
        module = importlib.import_module(module_path)
        klass = getattr(module, class_name)
        payload = data.get("payload", {})
        instance = klass(**payload)
        instance.id = data["id"]
        instance.attempts = data["attempts"]
        instance.status = JobStatus(data["status"])
        instance.queue = data["queue"]
        return instance
