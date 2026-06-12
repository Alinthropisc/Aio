import pytest

from core.events.observer import ModelObserver, ObservableMixin


class RecordingObserver(ModelObserver):
    def __init__(self):
        self.calls: list[tuple[str, object]] = []

    async def creating(self, instance):
        self.calls.append(("creating", instance))

    async def created(self, instance):
        self.calls.append(("created", instance))

    async def updating(self, instance):
        self.calls.append(("updating", instance))

    async def updated(self, instance):
        self.calls.append(("updated", instance))

    async def deleting(self, instance):
        self.calls.append(("deleting", instance))

    async def deleted(self, instance):
        self.calls.append(("deleted", instance))

    async def restored(self, instance):
        self.calls.append(("restored", instance))


class FakeModel:
    def __init__(self, id: int):
        self.id = id


class FakeRepo(ObservableMixin):
    model = FakeModel

    def __init__(self):
        super().__init__()
        self._session = None
        self._store: dict[int, FakeModel] = {}

    async def get_by_id(self, id):
        return self._store.get(id)

    async def create(self, **kwargs):
        return await super().create(**kwargs)

    async def update(self, id, **kwargs):
        return await super().update(id, **kwargs)

    async def delete(self, id):
        return await super().delete(id)

    async def soft_delete(self, id):
        return await super().soft_delete(id)

    async def restore(self, id):
        return await super().restore(id)


class TestModelObserver:
    async def test_default_hooks_do_nothing(self):
        obs = ModelObserver()
        obj = object()
        await obs.creating(obj)
        await obs.created(obj)
        await obs.updating(obj)
        await obs.updated(obj)
        await obs.deleting(obj)
        await obs.deleted(obj)
        await obs.restored(obj)


class TestObservableMixin:
    def test_add_and_remove_observer(self):
        repo = FakeRepo()
        obs = RecordingObserver()
        repo.add_observer(obs)
        assert obs in repo._observers
        repo.remove_observer(obs)
        assert obs not in repo._observers

    async def test_notify_calls_hook(self):
        repo = FakeRepo()
        obs = RecordingObserver()
        repo.add_observer(obs)
        obj = FakeModel(1)
        await repo._notify("created", obj)
        assert ("created", obj) in obs.calls

    async def test_notify_swallows_observer_errors(self):
        class BrokenObserver(ModelObserver):
            async def created(self, instance):
                raise RuntimeError("boom")

        repo = FakeRepo()
        repo.add_observer(BrokenObserver())
        await repo._notify("created", FakeModel(1))  # should not raise

    async def test_notify_unknown_event_does_nothing(self):
        repo = FakeRepo()
        obs = RecordingObserver()
        repo.add_observer(obs)
        await repo._notify("nonexistent_event", FakeModel(1))
        assert obs.calls == []

    async def test_multiple_observers_all_notified(self):
        repo = FakeRepo()
        obs1 = RecordingObserver()
        obs2 = RecordingObserver()
        repo.add_observer(obs1)
        repo.add_observer(obs2)
        obj = FakeModel(1)
        await repo._notify("deleted", obj)
        assert ("deleted", obj) in obs1.calls
        assert ("deleted", obj) in obs2.calls
