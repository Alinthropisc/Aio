from abc import ABC, abstractmethod

from core.events.bus import BaseEvent
from core.logging import Log


class BaseListener(ABC):
    """
    Базовый слушатель события.

    Использование:
        class SendWelcomeEmail(BaseListener):
            async def handle(self, event: UserCreatedEvent) -> None:
                await mailer.send(event.user.email, "welcome")

        event_bus.listen(UserCreatedEvent, SendWelcomeEmail().handle)
    """

    def __init__(self) -> None:
        self._log = Log.get("Listener", listener=self.__class__.__name__)

    @abstractmethod
    async def handle(self, event: BaseEvent) -> None:
        """Обработай событие здесь."""

    async def __call__(self, event: BaseEvent) -> None:
        self._log.debug(f"Handling {event.name}")
        try:
            await self.handle(event)
        except Exception as exc:
            self._log.error(f"Failed to handle {event.name}: {exc}")
            raise
