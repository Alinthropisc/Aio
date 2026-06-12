from typing import Generic, TypeVar

from pydantic import Field

from .base import BaseSchema

T = TypeVar("T")


class SuccessResponse(BaseSchema, Generic[T]):
    """
    Стандартный успешный ответ.

    {
        "success": true,
        "data": { ... }
    }
    """

    success: bool = True
    data: T | None = None

    @classmethod
    def of(cls, data: T) -> "SuccessResponse[T]":
        return cls(data=data)


class ErrorDetail(BaseSchema):
    field: str | None = None
    message: str


class ErrorResponse(BaseSchema):
    """
    Стандартный ответ с ошибкой.

    {
        "success": false,
        "code": "VALIDATION_ERROR",
        "message": "Invalid input",
        "errors": [{ "field": "email", "message": "Invalid email" }]
    }
    """

    success: bool = False
    code: str = "ERROR"
    message: str
    errors: list[ErrorDetail] = Field(default_factory=list)

    @classmethod
    def of(cls, message: str, code: str = "ERROR", errors: list[dict] | None = None) -> "ErrorResponse":
        return cls(
            message=message,
            code=code,
            errors=[ErrorDetail(**e) for e in (errors or [])],
        )


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Ответ с пагинацией.

    {
        "items": [...],
        "total": 100,
        "limit": 20,
        "offset": 0,
        "has_next": true,
        "has_prev": false,
        "pages": 5
    }
    """

    items: list[T]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool
    pages: int

    @classmethod
    def of(cls, page, serializer: type[T] | None = None) -> "PaginatedResponse[T]":
        items = [serializer.model_validate(i) for i in page.items] if serializer else list(page.items)
        return cls(
            items=items,
            total=page.total,
            limit=page.limit,
            offset=page.offset,
            has_next=page.has_next,
            has_prev=page.has_prev,
            pages=page.pages,
        )
