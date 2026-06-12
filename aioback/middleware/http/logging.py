import time
import uuid

from litestar import Request
from litestar.middleware import AbstractMiddleware
from litestar.types import Receive, Scope, Send

from core.logging import Log


class LoggingMiddleware(AbstractMiddleware):
    """
    Логирует каждый HTTP запрос: метод, путь, статус, время.
    Паттерн Chain of Responsibility — middleware цепочка Litestar.
    """

    exclude_paths: list[str] = ["/health", "/metrics", "/favicon.ico"]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        log = Log.get("http", request_id=request_id)
        log.info(f"→ {request.method} {request.url.path}")

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            log.error(f"✗ {request.method} {request.url.path} | {type(exc).__name__}: {exc}")
            raise
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
            getattr(log, level)(
                f"← {request.method} {request.url.path} | {status_code} | {elapsed:.1f}ms"
            )
