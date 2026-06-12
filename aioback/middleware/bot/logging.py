from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from core.logging import Log


class BotLoggingMiddleware(BaseMiddleware):
    """
    Логирует каждое входящее Telegram событие.
    Паттерн Chain of Responsibility — middleware цепочка Aiogram.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        user_id = user.id if user else "unknown"
        event_type = type(event).__name__

        log = Log.get("bot", user_id=user_id, event=event_type)
        log.debug(f"→ {event_type} from user {user_id}")

        try:
            result = await handler(event, data)
            log.debug(f"← {event_type} handled")
            return result
        except Exception as exc:
            log.error(f"✗ {event_type} | {type(exc).__name__}: {exc}")
            raise
