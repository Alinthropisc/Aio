import pytest

from core.auth.policy import BasePolicy, PolicyRegistry
from litestar.exceptions import NotAuthorizedException


class PostPolicy(BasePolicy):
    async def view(self, user, post=None):
        return True

    async def edit(self, user, post=None):
        return user.get("role") == "admin"

    async def delete(self, user, post=None):
        return user.get("role") == "admin"

    def sync_action(self, user):
        return user.get("role") == "editor"


class FakeUser(dict):
    pass


@pytest.fixture
def registry():
    r = PolicyRegistry()
    r.register("post", PostPolicy())
    return r


class TestPolicyRegistry:
    def test_register_returns_self(self):
        r = PolicyRegistry()
        result = r.register("post", PostPolicy())
        assert result is r

    async def test_allows_true(self, registry):
        user = FakeUser(role="admin")
        assert await registry.allows("post", "edit", user) is True

    async def test_allows_false(self, registry):
        user = FakeUser(role="user")
        assert await registry.allows("post", "edit", user) is False

    async def test_allows_unregistered_policy(self, registry):
        assert await registry.allows("nonexistent", "view", {}) is False

    async def test_allows_undefined_action_returns_false(self, registry):
        user = FakeUser(role="user")
        assert await registry.allows("post", "nonexistent_action", user) is False

    async def test_allows_sync_handler(self, registry):
        user = FakeUser(role="editor")
        assert await registry.allows("post", "sync_action", user) is True

    async def test_authorize_passes(self, registry):
        user = FakeUser(role="admin")
        await registry.authorize("post", "edit", user)

    async def test_authorize_raises(self, registry):
        user = FakeUser(role="user")
        with pytest.raises(NotAuthorizedException):
            await registry.authorize("post", "edit", user)

    async def test_any_returns_true(self, registry):
        user = FakeUser(role="admin")
        assert await registry.any("post", ["view", "edit"], user) is True

    async def test_any_returns_false(self, registry):
        user = FakeUser(role="user")
        assert await registry.any("post", ["edit", "delete"], user) is False

    async def test_before_hook_overrides(self):
        class SuperPolicy(BasePolicy):
            async def before(self, user, action):
                if user.get("super"):
                    return True
                return None

            async def edit(self, user):
                return False

        r = PolicyRegistry()
        r.register("item", SuperPolicy())
        assert await r.allows("item", "edit", {"super": True}) is True
        assert await r.allows("item", "edit", {"super": False}) is False

    async def test_before_hook_returns_false_denies(self):
        class StrictPolicy(BasePolicy):
            async def before(self, user, action):
                if user.get("banned"):
                    return False
                return None

            async def view(self, user):
                return True

        r = PolicyRegistry()
        r.register("page", StrictPolicy())
        assert await r.allows("page", "view", {"banned": True}) is False
        assert await r.allows("page", "view", {"banned": False}) is True
