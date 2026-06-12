import pytest

from core.auth.gate import Gate
from litestar.exceptions import NotAuthorizedException


class FakeUser:
    def __init__(self, role: str = "user", id: int = 1):
        self.role = role
        self.id = id


@pytest.fixture
def gate():
    return Gate()


class TestGateDefine:
    def test_define_returns_self(self, gate):
        result = gate.define("edit", lambda u: True)
        assert result is gate

    def test_before_returns_self(self, gate):
        result = gate.before(lambda u: False)
        assert result is gate

    def test_after_returns_self(self, gate):
        result = gate.after(lambda u, r: None)
        assert result is gate


class TestGateAllows:
    async def test_allows_sync_true(self, gate):
        gate.define("admin", lambda u: u.role == "admin")
        assert await gate.allows("admin", FakeUser("admin")) is True

    async def test_allows_sync_false(self, gate):
        gate.define("admin", lambda u: u.role == "admin")
        assert await gate.allows("admin", FakeUser("user")) is False

    async def test_allows_async_check(self, gate):
        async def check(u):
            return u.role == "admin"

        gate.define("admin", check)
        assert await gate.allows("admin", FakeUser("admin")) is True

    async def test_undefined_ability_returns_false(self, gate):
        assert await gate.allows("nonexistent", FakeUser()) is False

    async def test_before_hook_short_circuits(self, gate):
        gate.define("admin", lambda u: False)
        gate.before(lambda u: u.role == "superadmin")
        assert await gate.allows("admin", FakeUser("superadmin")) is True

    async def test_before_hook_does_not_override_when_false(self, gate):
        gate.define("admin", lambda u: u.role == "admin")
        gate.before(lambda u: False)
        assert await gate.allows("admin", FakeUser("admin")) is True

    async def test_after_hook_is_called(self, gate):
        called = []
        gate.define("view", lambda u: True)
        gate.after(lambda u, r: called.append(r))
        await gate.allows("view", FakeUser())
        assert called == [True]

    async def test_allows_with_extra_args(self, gate):
        gate.define("edit-post", lambda u, post: post["author_id"] == u.id)
        user = FakeUser(id=42)
        assert await gate.allows("edit-post", user, {"author_id": 42}) is True
        assert await gate.allows("edit-post", user, {"author_id": 99}) is False


class TestGateDenies:
    async def test_denies_is_inverse(self, gate):
        gate.define("view", lambda u: True)
        assert await gate.denies("view", FakeUser()) is False
        gate.define("edit", lambda u: False)
        assert await gate.denies("edit", FakeUser()) is True


class TestGateAuthorize:
    async def test_authorize_passes_when_allowed(self, gate):
        gate.define("view", lambda u: True)
        await gate.authorize("view", FakeUser())  # no exception

    async def test_authorize_raises_when_denied(self, gate):
        gate.define("admin", lambda u: False)
        with pytest.raises(NotAuthorizedException):
            await gate.authorize("admin", FakeUser())


class TestGateAny:
    async def test_any_returns_true_if_one_matches(self, gate):
        gate.define("admin", lambda u: u.role == "admin")
        gate.define("moderator", lambda u: u.role == "moderator")
        assert await gate.any(["admin", "moderator"], FakeUser("moderator")) is True

    async def test_any_returns_false_if_none_match(self, gate):
        gate.define("admin", lambda u: u.role == "admin")
        assert await gate.any(["admin"], FakeUser("user")) is False


class TestGateAll:
    async def test_all_returns_true_when_all_pass(self, gate):
        gate.define("verified", lambda u: True)
        gate.define("active", lambda u: True)
        assert await gate.all(["verified", "active"], FakeUser()) is True

    async def test_all_returns_false_when_one_fails(self, gate):
        gate.define("verified", lambda u: True)
        gate.define("active", lambda u: False)
        assert await gate.all(["verified", "active"], FakeUser()) is False


class TestGateCheckPolicy:
    async def test_check_policy_delegates(self, gate):
        class PostPolicy:
            def view(self, user):
                return True

            def edit(self, user):
                return user.role == "admin"

        policy = PostPolicy()
        assert await gate.check_policy(policy, "view", FakeUser()) is True
        assert await gate.check_policy(policy, "edit", FakeUser("user")) is False

    async def test_check_policy_undefined_action_returns_false(self, gate):
        class EmptyPolicy:
            pass

        assert await gate.check_policy(EmptyPolicy(), "nonexistent", FakeUser()) is False

    async def test_check_policy_async_handler(self, gate):
        class AsyncPolicy:
            async def view(self, user):
                return True

        assert await gate.check_policy(AsyncPolicy(), "view", FakeUser()) is True
