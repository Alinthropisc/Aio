from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from litestar import Router
from litestar.types import ControllerRouterHandler


@dataclass
class _RouteGroup:
    prefix: str
    middleware: list = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    name_prefix: str = ""


class ApiRouter:
    """
    Laravel-style fluent router для Litestar.

    Использование:
        router = ApiRouter()

        with router.group("/api/v1", tags=["v1"]):
            router.resource("/users", UserController)

            with router.group("/admin", middleware=[AuthMiddleware]):
                router.get("/stats", StatsController.stats)

        app = Litestar(route_handlers=router.build())

    Паттерны:
    - Builder    — fluent цепочка методов
    - Composite  — группы вложены в группы
    - Facade     — скрывает сложность Litestar Router
    """

    def __init__(self) -> None:
        self._routes: list[dict[str, Any]] = []
        self._group_stack: list[_RouteGroup] = []

    # ── Group (Composite паттерн) ──────────────────────────────────────────────

    @contextmanager
    def group(
        self,
        prefix: str,
        middleware: list | None = None,
        tags: list[str] | None = None,
        name: str = "",
    ) -> Iterator["ApiRouter"]:
        self._group_stack.append(
            _RouteGroup(
                prefix=prefix.rstrip("/"),
                middleware=middleware or [],
                tags=tags or [],
                name_prefix=name,
            )
        )
        try:
            yield self
        finally:
            self._group_stack.pop()

    # ── Внутренний хелпер ─────────────────────────────────────────────────────

    def _current_prefix(self) -> str:
        return "".join(g.prefix for g in self._group_stack)

    def _current_middleware(self) -> list:
        result = []
        for g in self._group_stack:
            result.extend(g.middleware)
        return result

    def _current_tags(self) -> list[str]:
        result = []
        for g in self._group_stack:
            result.extend(g.tags)
        return result

    def _add(self, path: str, handler: ControllerRouterHandler, **kwargs: Any) -> "ApiRouter":
        full_path = self._current_prefix() + ("/" + path.lstrip("/") if path not in ("", "/") else "")
        self._routes.append({
            "path": full_path or "/",
            "handler": handler,
            "middleware": self._current_middleware(),
            "tags": self._current_tags(),
            **kwargs,
        })
        return self

    # ── HTTP методы ───────────────────────────────────────────────────────────

    def get(self, path: str, handler: ControllerRouterHandler, **kw) -> "ApiRouter":
        return self._add(path, handler, method="GET", **kw)

    def post(self, path: str, handler: ControllerRouterHandler, **kw) -> "ApiRouter":
        return self._add(path, handler, method="POST", **kw)

    def put(self, path: str, handler: ControllerRouterHandler, **kw) -> "ApiRouter":
        return self._add(path, handler, method="PUT", **kw)

    def patch(self, path: str, handler: ControllerRouterHandler, **kw) -> "ApiRouter":
        return self._add(path, handler, method="PATCH", **kw)

    def delete(self, path: str, handler: ControllerRouterHandler, **kw) -> "ApiRouter":
        return self._add(path, handler, method="DELETE", **kw)

    # ── Resource (Laravel Route::resource) ───────────────────────────────────

    def resource(self, path: str, controller: type, only: list[str] | None = None) -> "ApiRouter":
        """
        Генерирует CRUD маршруты из контроллера.

        router.resource("/users", UserController)

        Создаёт:
            GET    /users          → controller.index
            POST   /users          → controller.create
            GET    /users/{id}     → controller.show
            PUT    /users/{id}     → controller.update
            DELETE /users/{id}     → controller.destroy
        """
        actions = {
            "index":   ("GET",    path),
            "store":   ("POST",   path),
            "show":    ("GET",    path + "/{id:uuid}"),
            "update":  ("PUT",    path + "/{id:uuid}"),
            "patch":   ("PATCH",  path + "/{id:uuid}"),
            "destroy": ("DELETE", path + "/{id:uuid}"),
        }
        allowed = only or list(actions.keys())
        for action, (method, route_path) in actions.items():
            if action not in allowed:
                continue
            handler = getattr(controller, action, None)
            if handler is None:
                continue
            self._add(route_path, handler, method=method)
        return self

    # ── Build — собирает Litestar Router'ы ───────────────────────────────────

    def build(self) -> list[Router]:
        """Возвращает список Litestar Router-ов готовых для передачи в Litestar()."""
        grouped: dict[str, list] = {}
        for route in self._routes:
            key = route["path"].rsplit("/", 1)[0] or "/"
            grouped.setdefault(key, [])
            grouped[key].append(route["handler"])

        seen_handlers: list[ControllerRouterHandler] = []
        for route in self._routes:
            if route["handler"] not in seen_handlers:
                seen_handlers.append(route["handler"])

        return seen_handlers
