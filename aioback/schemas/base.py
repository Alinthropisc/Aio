import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer


class BaseSchema(BaseModel):
    """
    Базовая схема для всех DTO.
    - from_attributes=True  → можно строить из SQLAlchemy моделей
    - populate_by_name=True → принимает и alias и оригинальное имя
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )

    def to_dict(self, exclude_none: bool = False, exclude_unset: bool = False) -> dict[str, Any]:
        return self.model_dump(exclude_none=exclude_none, exclude_unset=exclude_unset)


class UUIDSchema(BaseSchema):
    """Схема с UUID полем."""
    id: uuid.UUID


class TimestampSchema(BaseSchema):
    """Схема с временными метками."""
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.isoformat()


class BaseEntitySchema(UUIDSchema, TimestampSchema):
    """Полная схема сущности: UUID + timestamps. Используй для ответов (response)."""
    pass
