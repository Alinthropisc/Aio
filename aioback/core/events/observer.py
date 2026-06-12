from typing import Any

from core.logging import Log


class ModelObserver:
    """
    Базовый Observer для модели — паттерн Observer.
    Переопредели нужные хуки.

    Использование:
        class UserObserver(ModelObserver):
            async def created(self, instance) -> None:
                await event_bus.dispatch(UserCreatedEvent(user=instance))

            async def deleted(self, instance) -> None:
                Log.info(f"User {instance.id} deleted")

        User.observe(UserObserver())
    """

    async def creating(self, instance: Any) -> None:
        """До создания записи в БД."""

    async def created(self, instance: Any) -> None:
        """После создания записи в БД."""

    async def updating(self, instance: Any) -> None:
        """До обновления записи."""

    async def updated(self, instance: Any) -> None:
        """После обновления записи."""

    async def deleting(self, instance: Any) -> None:
        """До удаления записи."""

    async def deleted(self, instance: Any) -> None:
        """После удаления записи."""

    async def restored(self, instance: Any) -> None:
        """После восстановления soft-deleted записи."""


class ObservableMixin:
    """
    Миксин для репозитория — включает поддержку Observer.
    Добавь к BaseRepository или конкретному репозиторию.

    Использование:
        class UserRepository(ObservableMixin, BaseRepository[User]):
            model = User

        repo = UserRepository(session)
        repo.add_observer(UserObserver())
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._observers: list[ModelObserver] = []
        self._log = Log.get("Observable", model=getattr(self, "model", type(self)).__name__)

    def add_observer(self, observer: ModelObserver) -> None:
        self._observers.append(observer)

    def remove_observer(self, observer: ModelObserver) -> None:
        self._observers = [o for o in self._observers if o is not observer]

    async def _notify(self, event: str, instance: Any) -> None:
        for observer in self._observers:
            try:
                hook = getattr(observer, event, None)
                if hook:
                    await hook(instance)
            except Exception as exc:
                self._log.error(f"Observer {type(observer).__name__}.{event} failed: {exc}")

    # ── Переопределяем методы репозитория добавляя хуки ──────────────────────

    async def create(self, **kwargs) -> Any:
        instance = self.model(**kwargs)
        await self._notify("creating", instance)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        await self._notify("created", instance)
        return instance

    async def update(self, id, **kwargs) -> Any:
        instance = await super().get_by_id(id)
        if instance:
            await self._notify("updating", instance)
        result = await super().update(id, **kwargs)
        if result:
            await self._notify("updated", result)
        return result

    async def delete(self, id) -> bool:
        instance = await super().get_by_id(id)
        if instance:
            await self._notify("deleting", instance)
        result = await super().delete(id)
        if result and instance:
            await self._notify("deleted", instance)
        return result

    async def soft_delete(self, id) -> bool:
        instance = await super().get_by_id(id)
        if instance:
            await self._notify("deleting", instance)
        result = await super().soft_delete(id)
        if result and instance:
            await self._notify("deleted", instance)
        return result

    async def restore(self, id) -> Any:
        result = await super().restore(id)
        if result:
            await self._notify("restored", result)
        return result
