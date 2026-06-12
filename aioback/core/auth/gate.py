from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from litestar.exceptions import NotAuthorizedException

from core.logging import Log

if TYPE_CHECKING:
    from core.auth.policy import BasePolicy

GateCheck = Callable[..., bool | Awaitable[bool]]


class Gate:
    """
    Laravel-style Gate — проверки авторизации через замыкания.
    Паттерн Strategy — каждая способность это отдельная стратегия.

    Использование:
        gate.define("edit-post", lambda user, post: post.author_id == user.id)
        gate.define("admin", lambda user: user.role == "admin")

        # Проверка
        await gate.allows("admin", user)           # → bool
        await gate.authorize("edit-post", user, post)  # → raise если нет прав
        await gate.any(["admin", "moderator"], user)   # → хотя бы одно
        await gate.all(["verified", "active"], user)   # → все разом
    """

    def __init__(self) -> None:
        self._abilities: dict[str, GateCheck] = {}
        self._before: list[GateCheck] = []
        self._after: list[GateCheck] = []
        self._log = Log.get("Gate")

    # ── Регистрация ───────────────────────────────────────────────────────────

    def define(self, ability: str, check: GateCheck) -> Gate:
        """Определяет способность через callable."""
        self._abilities[ability] = check
        return self

    def before(self, check: GateCheck) -> Gate:
        """Хук — вызывается перед любой проверкой (напр. супер-админ)."""
        self._before.append(check)
        return self

    def after(self, check: GateCheck) -> Gate:
        """Хук — вызывается после проверки."""
        self._after.append(check)
        return self

    # ── Проверки ──────────────────────────────────────────────────────────────

    async def _run(self, check: GateCheck, *args: Any) -> bool:
        import asyncio

        result = check(*args)
        if asyncio.iscoroutine(result):
            return await result
        return bool(result)

    async def allows(self, ability: str, user: Any, *args: Any) -> bool:
        """Возвращает True если пользователь имеет способность."""
        for before in self._before:
            if await self._run(before, user, *args):
                return True

        check = self._abilities.get(ability)
        if check is None:
            self._log.warning(f"Ability '{ability}' not defined")
            return False

        result = await self._run(check, user, *args)

        for after in self._after:
            await self._run(after, user, result, *args)

        return result

    async def denies(self, ability: str, user: Any, *args: Any) -> bool:
        return not await self.allows(ability, user, *args)

    async def authorize(self, ability: str, user: Any, *args: Any) -> None:
        """Бросает NotAuthorizedException если нет прав."""
        if not await self.allows(ability, user, *args):
            self._log.warning(f"Unauthorized: user={getattr(user, 'id', '?')} ability={ability}")
            raise NotAuthorizedException(detail=f"Access denied: {ability}")

    async def any(self, abilities: list[str], user: Any, *args: Any) -> bool:
        """True если пользователь имеет хотя бы одну из способностей."""
        for ability in abilities:
            if await self.allows(ability, user, *args):
                return True
        return False

    async def all(self, abilities: list[str], user: Any, *args: Any) -> bool:
        """True если пользователь имеет все способности."""
        for ability in abilities:
            if not await self.allows(ability, user, *args):
                return False
        return True

    async def check_policy(self, policy: BasePolicy, action: str, user: Any, *args: Any) -> bool:
        """Делегирует проверку в Policy класс."""
        import asyncio

        handler = getattr(policy, action, None)
        if handler is None:
            return False
        result = handler(user, *args)
        if asyncio.iscoroutine(result):
            return await result
        return bool(result)


# Глобальный singleton Gate
gate = Gate()
