import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, asc, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from core.db import BaseModel

Model = TypeVar("Model", bound=BaseModel)


@dataclass
class Page(Generic[Model]):
    items: Sequence[Model]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        return self.offset > 0

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.limit))


class BaseRepository(Generic[Model]):
    """
    Богатый Generic CRUD репозиторий.

    Использование:
        class UserRepository(BaseRepository[User]):
            model = User

        async with get_session(factory) as session:
            repo = UserRepository(session)
            user = await repo.create(name="Alice", email="alice@example.com")
    """

    model: type[Model]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Internal ──────────────────────────────────────────────────────────────

    def _base_select(self) -> Select:
        """Базовый select. Если модель поддерживает soft delete — фильтрует удалённые."""
        stmt = select(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))
        return stmt

    # ── Create ────────────────────────────────────────────────────────────────

    async def create(self, **kwargs: Any) -> Model:
        instance = self.model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def create_instance(self, instance: Model) -> Model:
        """Сохраняет уже созданный объект модели."""
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def bulk_create(self, data: list[dict[str, Any]]) -> Sequence[Model]:
        instances = [self.model(**item) for item in data]
        self._session.add_all(instances)
        await self._session.flush()
        return instances

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_by_id(self, id: uuid.UUID | int) -> Model | None:
        result = await self._session.execute(
            self._base_select().where(self.model.id == id)
        )
        return result.scalars().first()

    async def get_by_id_or_raise(self, id: uuid.UUID | int) -> Model:
        instance = await self.get_by_id(id)
        if instance is None:
            raise ValueError(f"{self.model.__name__} with id={id} not found")
        return instance

    async def get_by(self, **filters: Any) -> Model | None:
        result = await self._session.execute(
            self._base_select().filter_by(**filters)
        )
        return result.scalars().first()

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[Model]:
        result = await self._session.execute(
            self._base_select().limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def filter_by(self, **filters: Any) -> Sequence[Model]:
        result = await self._session.execute(
            self._base_select().filter_by(**filters)
        )
        return result.scalars().all()

    async def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))
        if filters:
            stmt = stmt.filter_by(**filters)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists(self, **filters: Any) -> bool:
        return await self.count(**filters) > 0

    # ── Pagination ────────────────────────────────────────────────────────────

    async def paginate(
        self,
        limit: int = 20,
        offset: int = 0,
        order_by: str | None = None,
        descending: bool = False,
        **filters: Any,
    ) -> Page[Model]:
        stmt = self._base_select()
        if filters:
            stmt = stmt.filter_by(**filters)

        if order_by and hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            stmt = stmt.order_by(desc(col) if descending else asc(col))

        total = await self.count(**filters)
        result = await self._session.execute(stmt.limit(limit).offset(offset))
        items = result.scalars().all()

        return Page(items=items, total=total, limit=limit, offset=offset)

    # ── Search ────────────────────────────────────────────────────────────────

    async def search(self, query: str, fields: list[str], limit: int = 20) -> Sequence[Model]:
        """ILIKE поиск по нескольким полям (OR)."""
        conditions = [
            getattr(self.model, field).ilike(f"%{query}%")
            for field in fields
            if hasattr(self.model, field)
        ]
        if not conditions:
            return []
        result = await self._session.execute(
            self._base_select().where(or_(*conditions)).limit(limit)
        )
        return result.scalars().all()

    # ── Eager loading ─────────────────────────────────────────────────────────

    async def get_with_relations(
        self, id: uuid.UUID | int, *relations: InstrumentedAttribute
    ) -> Model | None:
        """Загружает запись с указанными связями через selectinload."""
        stmt = self._base_select().where(self.model.id == id)
        for rel in relations:
            stmt = stmt.options(selectinload(rel))
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def all_with_relations(
        self, *relations: InstrumentedAttribute, limit: int = 100, offset: int = 0
    ) -> Sequence[Model]:
        stmt = self._base_select().limit(limit).offset(offset)
        for rel in relations:
            stmt = stmt.options(selectinload(rel))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    # ── Update ────────────────────────────────────────────────────────────────

    async def update(self, id: uuid.UUID | int, **kwargs: Any) -> Model | None:
        await self._session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self._session.flush()
        return await self.get_by_id(id)

    async def bulk_update(self, ids: list[uuid.UUID | int], **kwargs: Any) -> int:
        result = await self._session.execute(
            update(self.model).where(self.model.id.in_(ids)).values(**kwargs)
        )
        await self._session.flush()
        return result.rowcount

    async def save(self, instance: Model) -> Model:
        """Обновляет уже существующий объект (merge + flush)."""
        instance = await self._session.merge(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete(self, id: uuid.UUID | int) -> bool:
        result = await self._session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0

    async def bulk_delete(self, ids: list[uuid.UUID | int]) -> int:
        result = await self._session.execute(
            delete(self.model).where(self.model.id.in_(ids))
        )
        return result.rowcount

    async def soft_delete(self, id: uuid.UUID | int) -> bool:
        """Мягкое удаление — только для моделей с SoftDeleteMixin."""
        if not hasattr(self.model, "is_deleted"):
            raise TypeError(f"{self.model.__name__} не поддерживает soft delete")
        result = await self._session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(is_deleted=True, deleted_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0

    async def restore(self, id: uuid.UUID | int) -> Model | None:
        """Восстановление мягко удалённой записи."""
        if not hasattr(self.model, "is_deleted"):
            raise TypeError(f"{self.model.__name__} не поддерживает soft delete")
        await self._session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(is_deleted=False, deleted_at=None)
        )
        await self._session.flush()
        result = await self._session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()
