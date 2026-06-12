import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from core.logging import Log


class ThrottleMiddleware(BaseMiddleware):
    """
    Ограничивает частоту сообщений от одного пользователя.
    Паттерн Strategy — стратегия хранения в памяти (можно заменить на Redis).

    Использование:
        dp.message.middleware(ThrottleMiddleware(rate_limit=1.0))
    """

    def __init__(self, rate_limit: float = 1.0) -> None:
        self._rate_limit = rate_limit
        self._last_call: dict[int, float] = {}
        self._log = Log.get("throttle")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_call.get(user.id, 0.0)
        delta = now - last

        if delta < self._rate_limit:
            self._log.warning(f"Throttled user {user.id} | wait {self._rate_limit - delta:.1f}s")
            if isinstance(event, Message):
                await event.answer(
                    f"Слишком быстро. Подожди {self._rate_limit - delta:.1f} сек."
                )
            return None

        self._last_call[user.id] = now
        return await handler(event, data)
