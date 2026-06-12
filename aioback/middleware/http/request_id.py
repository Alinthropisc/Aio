import uuid

from litestar.middleware import AbstractMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send


class RequestIdMiddleware(AbstractMiddleware):
    """
    Добавляет X-Request-ID в каждый ответ.
    Если заголовок уже есть в запросе — пробрасывает его дальше.
    """

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = (
            dict(scope.get("headers", [])).get(b"x-request-id", b"").decode()
            or str(uuid.uuid4())
        )

        async def send_with_id(message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_id)
