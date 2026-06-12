from core.events.observer import ModelObserver


class LoggingObserver(ModelObserver):
    """
    Универсальный наблюдатель — логирует все события модели.

    Использование:
        repo.add_observer(LoggingObserver())
    """

    def __init__(self, model_name: str = "") -> None:
        from core.logging import Log
        self._log = Log.get("Observer", model=model_name)

    async def created(self, instance) -> None:
        self._log.info(f"Created: id={instance.id}")

    async def updated(self, instance) -> None:
        self._log.info(f"Updated: id={instance.id}")

    async def deleted(self, instance) -> None:
        self._log.info(f"Deleted: id={instance.id}")

    async def restored(self, instance) -> None:
        self._log.info(f"Restored: id={instance.id}")
