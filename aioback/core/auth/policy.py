from typing import Any

from core.logging import Log


class BasePolicy:
    """
    Laravel-style Policy — авторизация для конкретной модели.
    Паттерн Strategy — каждый метод это стратегия доступа.

    Использование:
        class PostPolicy(BasePolicy):
            def view(self, user, post) -> bool:
                return True  # все могут читать

            def update(self, user, post) -> bool:
                return post.author_id == user.id

            def delete(self, user, post) -> bool:
                return post.author_id == user.id or user.role == "admin"

        # Регистрация
        registry = PolicyRegistry()
        registry.register("post", PostPolicy())

        # Проверка
        await registry.allows("post", "update", user, post)
        await registry.authorize("post", "delete", user, post)
    """

    async def before(self, user: Any, action: str) -> bool | None:
        """Вызывается перед любым методом политики. None = продолжить проверку."""
        return None


class PolicyRegistry:
    """
    Реестр политик — паттерн Registry.
    Одно место для регистрации всех политик.
    """

    def __init__(self) -> None:
        self._policies: dict[str, BasePolicy] = {}
        self._log = Log.get("PolicyRegistry")

    def register(self, name: str, policy: BasePolicy) -> "PolicyRegistry":
        self._policies[name] = policy
        self._log.debug(f"Policy registered: {name} → {type(policy).__name__}")
        return self

    async def allows(self, name: str, action: str, user: Any, *args: Any) -> bool:
        policy = self._policies.get(name)
        if policy is None:
            self._log.warning(f"Policy '{name}' not registered")
            return False

        import asyncio

        before = policy.before(user, action)
        if asyncio.iscoroutine(before):
            before = await before
        if before is not None:
            return bool(before)

        handler = getattr(policy, action, None)
        if handler is None:
            return False

        result = handler(user, *args)
        if asyncio.iscoroutine(result):
            result = await result
        return bool(result)

    async def authorize(self, name: str, action: str, user: Any, *args: Any) -> None:
        from litestar.exceptions import NotAuthorizedException

        if not await self.allows(name, action, user, *args):
            self._log.warning(f"Policy denied: {name}.{action} user={getattr(user, 'id', '?')}")
            raise NotAuthorizedException(detail=f"Access denied: {name}.{action}")

    async def any(self, name: str, actions: list[str], user: Any, *args: Any) -> bool:
        for action in actions:
            if await self.allows(name, action, user, *args):
                return True
        return False
