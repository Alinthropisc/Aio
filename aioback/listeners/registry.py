from core.events.bus import EventBus, event_bus
from core.logging import Log


class ListenerRegistry:
    """
    Центральная регистрация всех слушателей.
    Паттерн Registry — одно место где видно все подписки.

    Использование:
        registry = ListenerRegistry()
        registry.register()  # вызови при старте приложения

        # В core/di/main.py или main.py:
        ListenerRegistry().register()
    """

    def __init__(self, bus: EventBus = event_bus) -> None:
        self._bus = bus
        self._log = Log.get("ListenerRegistry")

    def register(self) -> None:
        """Регистрируй все слушатели здесь."""
        self._log.info("Registering event listeners...")

        # Пример:
        # from events.base import ModelCreatedEvent
        # from listeners.user import SendWelcomeEmail, NotifyAdmin
        #
        # self._bus.listen(UserCreatedEvent, SendWelcomeEmail())
        # self._bus.listen(UserCreatedEvent, NotifyAdmin())

        self._log.info("Event listeners registered")
