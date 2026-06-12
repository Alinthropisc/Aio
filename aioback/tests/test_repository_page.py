"""Tests for repositories/base.py — Page dataclass."""
from repositories.base import Page


class TestPage:
    def test_has_next_true(self):
        page = Page(items=[], total=50, limit=10, offset=0)
        assert page.has_next is True

    def test_has_next_false_on_last_page(self):
        page = Page(items=[], total=50, limit=10, offset=40)
        assert page.has_next is False

    def test_has_prev_false_on_first_page(self):
        page = Page(items=[], total=50, limit=10, offset=0)
        assert page.has_prev is False

    def test_has_prev_true(self):
        page = Page(items=[], total=50, limit=10, offset=10)
        assert page.has_prev is True

    def test_pages_calculation(self):
        page = Page(items=[], total=50, limit=10, offset=0)
        assert page.pages == 5

    def test_pages_rounds_up(self):
        page = Page(items=[], total=21, limit=10, offset=0)
        assert page.pages == 3

    def test_pages_minimum_one(self):
        page = Page(items=[], total=0, limit=10, offset=0)
        assert page.pages == 1

    def test_exact_fit_no_next(self):
        page = Page(items=[], total=10, limit=10, offset=0)
        assert page.has_next is False
        assert page.pages == 1

    def test_single_item(self):
        page = Page(items=["x"], total=1, limit=10, offset=0)
        assert page.has_next is False
        assert page.has_prev is False
        assert page.pages == 1
