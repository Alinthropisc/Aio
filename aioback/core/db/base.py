import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    """UUID первичный ключ — рекомендуется для публичных API."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class IntIDMixin:
    """Auto-increment первичный ключ — для внутренних/системных таблиц."""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)


class TimestampMixin:
    """Автоматические временные метки создания и обновления."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDeleteMixin:
    """
    Мягкое удаление — запись остаётся в БД, помечается как удалённая.
    Репозиторий автоматически фильтрует удалённые записи.
    """

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SlugMixin:
    """Человекочитаемый уникальный идентификатор для URL."""

    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)


class BaseModel(UUIDMixin, TimestampMixin, Base):
    """Стандартная модель: UUID pk + timestamps."""

    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class BaseIntModel(IntIDMixin, TimestampMixin, Base):
    """Модель с автоинкрементным pk + timestamps."""

    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class BaseSoftModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Модель с UUID pk + timestamps + soft delete."""

    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} deleted={self.is_deleted}>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
