"""Tests for schemas/response.py — SuccessResponse, ErrorResponse, PaginatedResponse."""
from repositories.base import Page
from schemas.response import ErrorDetail, ErrorResponse, PaginatedResponse, SuccessResponse


class TestSuccessResponse:
    def test_of_creates_success_response(self):
        res = SuccessResponse.of({"id": 1})
        assert res.success is True
        assert res.data == {"id": 1}

    def test_of_with_none_data(self):
        res = SuccessResponse.of(None)
        assert res.success is True
        assert res.data is None

    def test_default_success_is_true(self):
        res = SuccessResponse(data="hello")
        assert res.success is True

    def test_serializes_to_dict(self):
        res = SuccessResponse.of(42)
        d = res.model_dump()
        assert d["success"] is True
        assert d["data"] == 42


class TestErrorResponse:
    def test_of_creates_error_response(self):
        res = ErrorResponse.of("Something went wrong", code="SERVER_ERROR")
        assert res.success is False
        assert res.code == "SERVER_ERROR"
        assert res.message == "Something went wrong"
        assert res.errors == []

    def test_of_with_field_errors(self):
        errors = [{"field": "email", "message": "Invalid email"}]
        res = ErrorResponse.of("Validation failed", code="VALIDATION_ERROR", errors=errors)
        assert len(res.errors) == 1
        assert res.errors[0].field == "email"
        assert res.errors[0].message == "Invalid email"

    def test_default_code_is_error(self):
        res = ErrorResponse.of("oops")
        assert res.code == "ERROR"

    def test_success_is_false(self):
        res = ErrorResponse(message="fail")
        assert res.success is False


class TestErrorDetail:
    def test_field_can_be_none(self):
        detail = ErrorDetail(field=None, message="global error")
        assert detail.field is None

    def test_with_field(self):
        detail = ErrorDetail(field="username", message="too short")
        assert detail.field == "username"


class TestPaginatedResponse:
    def _make_page(self, total=50, limit=10, offset=0):
        items = list(range(min(limit, total - offset)))
        return Page(items=items, total=total, limit=limit, offset=offset)

    def test_of_first_page(self):
        page = self._make_page(total=50, limit=10, offset=0)
        res = PaginatedResponse.of(page)
        assert res.total == 50
        assert res.limit == 10
        assert res.offset == 0
        assert res.has_next is True
        assert res.has_prev is False
        assert res.pages == 5

    def test_of_last_page(self):
        page = self._make_page(total=50, limit=10, offset=40)
        res = PaginatedResponse.of(page)
        assert res.has_next is False
        assert res.has_prev is True

    def test_of_single_page(self):
        page = self._make_page(total=5, limit=10, offset=0)
        res = PaginatedResponse.of(page)
        assert res.pages == 1
        assert res.has_next is False
        assert res.has_prev is False
