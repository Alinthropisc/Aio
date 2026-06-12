import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from core.logging import Log


@dataclass
class BaseEvent:
    """Базовый класс для всех событий приложения."""

    name: str = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.__class__.__name__


EventT = TypeVar("EventT", bound=BaseEvent)
ListenerFn = Callable[[Any], Awaitable[None] | None]


class EventBus:
    """
    Шина событий — Mediator паттерн.
    Компоненты общаются через события не зная друг о друге.

    Использование:
        # Подписка
        bus.listen(UserCreatedEvent, send_welcome_email)
        bus.listen(UserCreatedEvent, notify_admin)

        # Публикация
        await bus.dispatch(UserCreatedEvent(user=user))

        # Декоратор
        @bus.on(UserCreatedEvent)
        async def send_welcome(event: UserCreatedEvent) -> None:
            await mailer.send(event.user.email)
    """

    def __init__(self) -> None:
        self._listeners: dict[str, list[ListenerFn]] = defaultdict(list)
        self._log = Log.get("EventBus")

    def listen(self, event_class: type[BaseEvent], listener: ListenerFn) -> None:
        self._listeners[event_class.__name__].append(listener)
        self._log.debug(f"Listener registered: {listener.__name__} → {event_class.__name__}")

    def on(self, event_class: type[BaseEvent]):
        """Декоратор подписки на событие."""

        def decorator(fn: ListenerFn) -> ListenerFn:
            self.listen(event_class, fn)
            return fn

        return decorator

    def forget(self, event_class: type[BaseEvent], listener: ListenerFn | None = None) -> None:
        """Снять подписку. Если listener=None — снять все подписки события."""
        key = event_class.__name__
        if listener is None:
            self._listeners.pop(key, None)
        else:
            self._listeners[key] = [fn for fn in self._listeners[key] if fn is not listener]

    async def dispatch(self, event: BaseEvent) -> None:
        """Публикует событие — вызывает всех подписчиков последовательно."""
        listeners = self._listeners.get(event.name, [])
        if not listeners:
            return
        self._log.debug(f"Dispatching {event.name} → {len(listeners)} listener(s)")
        for listener in listeners:
            try:
                result = listener(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                self._log.error(f"Listener {listener.__name__} failed on {event.name}: {exc}")

    async def dispatch_parallel(self, event: BaseEvent) -> None:
        """Публикует событие — все подписчики запускаются параллельно."""
        listeners = self._listeners.get(event.name, [])
        if not listeners:
            return
        self._log.debug(f"Dispatching parallel {event.name} → {len(listeners)} listener(s)")
        tasks = []
        for listener in listeners:
            result = listener(event)
            if asyncio.iscoroutine(result):
                tasks.append(asyncio.create_task(result))
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for _i, res in enumerate(results):
                if isinstance(res, Exception):
                    self._log.error(f"Parallel listener failed on {event.name}: {res}")


# Глобальный singleton EventBus
event_bus = EventBus()
