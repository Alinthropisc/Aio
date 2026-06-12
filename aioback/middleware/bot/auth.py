from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from core.logging import Log


class BotAuthMiddleware(BaseMiddleware):
    """
    Проверяет что пользователь существует в системе.
    Добавляет db_user в data — доступен в хэндлере через data["db_user"].

    Использование:
        dp.message.middleware(BotAuthMiddleware(user_service=user_service))
    """

    def __init__(self, user_service) -> None:
        self._service = user_service
        self._log = Log.get("bot.auth")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        db_user = await self._service.get_by(telegram_id=user.id)
        if not db_user:
            db_user, _ = await self._service.get_or_create(
                defaults={
                    "username": user.username,
                    "full_name": user.full_name,
                    "language_code": user.language_code,
                },
                telegram_id=user.id,
            )
            self._log.info(f"New user registered: {user.id}")

        data["db_user"] = db_user
        return await handler(event, data)
