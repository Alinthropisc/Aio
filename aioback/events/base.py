from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from core.events.bus import BaseEvent


@dataclass
class ModelEvent(BaseEvent):
    """Базовое событие модели."""

    instance: Any = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ModelCreatedEvent(ModelEvent):
    """Вызывается после создания любой записи."""


@dataclass
class ModelUpdatedEvent(ModelEvent):
    """Вызывается после обновления любой записи."""

    changed_fields: list[str] = field(default_factory=list)


@dataclass
class ModelDeletedEvent(ModelEvent):
    """Вызывается после удаления записи."""


@dataclass
class ModelRestoredEvent(ModelEvent):
    """Вызывается после восстановления soft-deleted записи."""
