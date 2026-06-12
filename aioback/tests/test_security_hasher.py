"""Tests for core/security/hasher.py — PasswordHasher."""

import pytest

from core.security.hasher import PasswordHasher


@pytest.fixture
def hasher():
    return PasswordHasher()


class TestPasswordHasher:
    def test_hash_returns_string(self, hasher):
        result = hasher.hash("secret123")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_is_not_plaintext(self, hasher):
        result = hasher.hash("secret123")
        assert result != "secret123"

    def test_hash_is_different_each_time(self, hasher):
        h1 = hasher.hash("secret123")
        h2 = hasher.hash("secret123")
        assert h1 != h2

    def test_verify_correct_password(self, hasher):
        hashed = hasher.hash("mypassword")
        assert hasher.verify("mypassword", hashed) is True

    def test_verify_wrong_password(self, hasher):
        hashed = hasher.hash("mypassword")
        assert hasher.verify("wrongpassword", hashed) is False

    def test_verify_empty_password(self, hasher):
        hashed = hasher.hash("")
        assert hasher.verify("", hashed) is True
        assert hasher.verify("notempty", hashed) is False
