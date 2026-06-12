"""Tests for core/events/bus.py — EventBus."""
from dataclasses import dataclass

import pytest

from core.events.bus import BaseEvent, EventBus


@dataclass
class UserCreated(BaseEvent):
    user_id: int


@dataclass
class OrderPlaced(BaseEvent):
    order_id: str


@pytest.fixture
def bus():
    return EventBus()


class TestBaseEvent:
    def test_name_is_class_name(self):
        event = UserCreated(user_id=1)
        assert event.name == "UserCreated"

    def test_different_events_have_different_names(self):
        e1 = UserCreated(user_id=1)
        e2 = OrderPlaced(order_id="abc")
        assert e1.name != e2.name


class TestEventBusListen:
    async def test_listen_and_dispatch(self, bus):
        received = []

        async def handler(event: UserCreated):
            received.append(event.user_id)

        bus.listen(UserCreated, handler)
        await bus.dispatch(UserCreated(user_id=42))
        assert received == [42]

    async def test_multiple_listeners(self, bus):
        calls = []

        async def h1(e): calls.append("h1")
        async def h2(e): calls.append("h2")

        bus.listen(UserCreated, h1)
        bus.listen(UserCreated, h2)
        await bus.dispatch(UserCreated(user_id=1))
        assert calls == ["h1", "h2"]

    async def test_dispatch_no_listeners_does_nothing(self, bus):
        await bus.dispatch(UserCreated(user_id=1))  # should not raise

    async def test_different_events_dont_cross(self, bus):
        received = []

        async def handler(e): received.append(e)

        bus.listen(UserCreated, handler)
        await bus.dispatch(OrderPlaced(order_id="x"))
        assert received == []


class TestEventBusOn:
    async def test_decorator_registers_listener(self, bus):
        results = []

        @bus.on(UserCreated)
        async def on_user(event: UserCreated):
            results.append(event.user_id)

        await bus.dispatch(UserCreated(user_id=99))
        assert results == [99]


class TestEventBusForget:
    async def test_forget_specific_listener(self, bus):
        calls = []

        async def h1(e): calls.append("h1")
        async def h2(e): calls.append("h2")

        bus.listen(UserCreated, h1)
        bus.listen(UserCreated, h2)
        bus.forget(UserCreated, h1)
        await bus.dispatch(UserCreated(user_id=1))
        assert calls == ["h2"]

    async def test_forget_all_listeners(self, bus):
        calls = []

        async def h1(e): calls.append("h1")
        async def h2(e): calls.append("h2")

        bus.listen(UserCreated, h1)
        bus.listen(UserCreated, h2)
        bus.forget(UserCreated)
        await bus.dispatch(UserCreated(user_id=1))
        assert calls == []


class TestEventBusParallel:
    async def test_dispatch_parallel_calls_all(self, bus):
        results = []

        async def h1(e): results.append(1)
        async def h2(e): results.append(2)

        bus.listen(UserCreated, h1)
        bus.listen(UserCreated, h2)
        await bus.dispatch_parallel(UserCreated(user_id=1))
        assert sorted(results) == [1, 2]

    async def test_dispatch_parallel_no_listeners(self, bus):
        await bus.dispatch_parallel(UserCreated(user_id=1))  # should not raise


class TestEventBusErrorHandling:
    async def test_failing_listener_does_not_stop_others(self, bus):
        results = []

        async def bad(e): raise RuntimeError("boom")
        async def good(e): results.append("ok")

        bus.listen(UserCreated, bad)
        bus.listen(UserCreated, good)
        await bus.dispatch(UserCreated(user_id=1))
        assert results == ["ok"]

    async def test_sync_listener_is_supported(self, bus):
        """sync listeners (non-coroutine) should also work."""
        results = []

        def sync_handler(e):
            results.append(e.user_id)

        bus.listen(UserCreated, sync_handler)
        await bus.dispatch(UserCreated(user_id=7))
        assert results == [7]
