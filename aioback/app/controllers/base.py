from dataclasses import dataclass
from typing import Any

from litestar import Controller
from litestar.exceptions import HTTPException, NotFoundException
from litestar.status_codes import (
    HTTP_409_CONFLICT,
)

from repositories.base import Page


@dataclass
class PaginatedResponse:
    """Стандартный ответ с пагинацией."""
    items: list[Any]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool
    pages: int

    @classmethod
    def from_page(cls, page: Page, serializer=None) -> "PaginatedResponse":
        items = [serializer(i) for i in page.items] if serializer else list(page.items)
        return cls(
            items=items,
            total=page.total,
            limit=page.limit,
            offset=page.offset,
            has_next=page.has_next,
            has_prev=page.has_prev,
            pages=page.pages,
        )


class BaseWebController(Controller):
    """
    Базовый HTTP контроллер для Litestar.
    Все роуты наследуют общие хелперы и обработку ошибок.

    Использование:
        class UserController(BaseWebController):
            path = "/users"

            @get()
            @inject
            async def list_users(self, service: FromDishka[UserService]) -> list[UserSchema]:
                return await service.get_all()
    """

    # ── Response хелперы ──────────────────────────────────────────────────────

    def ok(self, data: Any = None) -> dict:
        return {"success": True, "data": data}

    def created(self, data: Any = None) -> dict:
        return {"success": True, "data": data}

    def no_content(self) -> None:
        return None

    def paginated(self, page: Page, serializer=None) -> PaginatedResponse:
        return PaginatedResponse.from_page(page, serializer)

    # ── Error хелперы ─────────────────────────────────────────────────────────

    def not_found(self, detail: str = "Not found") -> None:
        raise NotFoundException(detail=detail)

    def conflict(self, detail: str = "Already exists") -> None:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail=detail)

    def bad_request(self, detail: str = "Bad request") -> None:
        raise HTTPException(status_code=400, detail=detail)
