import uuid
from typing import Any, Generic, TypeVar

from loguru import logger

from core.db import BaseModel
from repositories.base import BaseRepository, Page

Model = TypeVar("Model", bound=BaseModel)
Repo = TypeVar("Repo", bound=BaseRepository)


class BaseService(Generic[Model, Repo]):
    """
    Базовый сервис — бизнес логика между контроллером и репозиторием.
    Не зависит от HTTP или Telegram — работает одинаково для Litestar и Aiogram.

    Использование:
        class UserService(BaseService[User, UserRepository]):
            repo_class = UserRepository
    """

    repo_class: type[Repo]

    def __init__(self, repo: Repo) -> None:
        self._repo = repo
        self._log = logger.bind(service=self.__class__.__name__)

    # ── Хуки — переопределяй в дочернем сервисе ──────────────────────────────

    async def before_create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Вызывается перед созданием. Можно валидировать, трансформировать данные."""
        return data

    async def after_create(self, instance: Model) -> Model:
        """Вызывается после создания. Можно отправить событие, нотификацию."""
        return instance

    async def before_update(self, id: uuid.UUID | int, data: dict[str, Any]) -> dict[str, Any]:
        """Вызывается перед обновлением."""
        return data

    async def after_update(self, instance: Model) -> Model:
        """Вызывается после обновления."""
        return instance

    async def before_delete(self, id: uuid.UUID | int) -> None:
        """Вызывается перед удалением. Можно проверить права, зависимости."""

    # ── CRUD ──────────────────────────────────────────────────────────────────

    async def create(self, **kwargs: Any) -> Model:
        data = await self.before_create(kwargs)
        self._log.debug(f"Creating {self._repo.model.__name__}")
        instance = await self._repo.create(**data)
        return await self.after_create(instance)

    async def get_by_id(self, id: uuid.UUID | int) -> Model | None:
        return await self._repo.get_by_id(id)

    async def get_by_id_or_raise(self, id: uuid.UUID | int) -> Model:
        return await self._repo.get_by_id_or_raise(id)

    async def get_by(self, **filters: Any) -> Model | None:
        return await self._repo.get_by(**filters)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Model]:
        return list(await self._repo.get_all(limit=limit, offset=offset))

    async def update(self, id: uuid.UUID | int, **kwargs: Any) -> Model | None:
        data = await self.before_update(id, kwargs)
        self._log.debug(f"Updating {self._repo.model.__name__} id={id}")
        instance = await self._repo.update(id, **data)
        if instance:
            return await self.after_update(instance)
        return None

    async def delete(self, id: uuid.UUID | int) -> bool:
        await self.before_delete(id)
        self._log.debug(f"Deleting {self._repo.model.__name__} id={id}")
        return await self._repo.delete(id)

    async def soft_delete(self, id: uuid.UUID | int) -> bool:
        await self.before_delete(id)
        return await self._repo.soft_delete(id)

    # ── Богатый функционал ────────────────────────────────────────────────────

    async def paginate(
        self,
        limit: int = 20,
        offset: int = 0,
        order_by: str | None = None,
        descending: bool = False,
        **filters: Any,
    ) -> Page[Model]:
        return await self._repo.paginate(
            limit=limit, offset=offset, order_by=order_by, descending=descending, **filters
        )

    async def search(self, query: str, fields: list[str], limit: int = 20) -> list[Model]:
        return list(await self._repo.search(query, fields, limit))

    async def exists(self, **filters: Any) -> bool:
        return await self._repo.exists(**filters)

    async def count(self, **filters: Any) -> int:
        return await self._repo.count(**filters)

    async def bulk_create(self, data: list[dict[str, Any]]) -> list[Model]:
        self._log.debug(f"Bulk creating {len(data)} {self._repo.model.__name__} records")
        return list(await self._repo.bulk_create(data))

    async def bulk_delete(self, ids: list[uuid.UUID | int]) -> int:
        self._log.debug(f"Bulk deleting {len(ids)} records")
        return await self._repo.bulk_delete(ids)

    async def get_or_create(self, defaults: dict[str, Any], **filters: Any) -> tuple[Model, bool]:
        """Возвращает (instance, created). Если не найден — создаёт с defaults."""
        instance = await self._repo.get_by(**filters)
        if instance:
            return instance, False
        data = {**filters, **defaults}
        instance = await self.create(**data)
        return instance, True

    async def update_or_create(self, defaults: dict[str, Any], **filters: Any) -> tuple[Model, bool]:
        """Обновляет если найден, создаёт если нет. Возвращает (instance, created)."""
        instance = await self._repo.get_by(**filters)
        if instance:
            updated = await self.update(instance.id, **defaults)
            return updated, False
        data = {**filters, **defaults}
        instance = await self.create(**data)
        return instance, True

    async def restore(self, id: uuid.UUID | int) -> Model | None:
        """Восстановление soft-deleted записи."""
        return await self._repo.restore(id)
