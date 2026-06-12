from dataclasses import dataclass

from core.queue.job import BaseJob, JobStatus


@dataclass
class EchoJob(BaseJob):
    message: str = "hello"

    async def handle(self) -> None:
        pass


@dataclass
class FailingJob(BaseJob):
    async def handle(self) -> None:
        raise RuntimeError("intentional failure")

    async def failed(self, exc: Exception) -> None:
        pass

    async def on_retry(self, attempt: int, exc: Exception) -> None:
        pass


class TestJobStatus:
    def test_statuses_exist(self):
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.DONE == "done"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.RETRYING == "retrying"


class TestBaseJob:
    def test_defaults(self):
        job = EchoJob()
        assert job.queue == "default"
        assert job.max_retries == 3
        assert job.retry_delay == 5
        assert job.timeout == 300
        assert job.priority == 0
        assert job.status == JobStatus.PENDING
        assert job.attempts == 0
        assert job.scheduled_at is None
        assert job.error is None

    def test_id_is_uuid_string(self):
        job = EchoJob()
        assert isinstance(job.id, str)
        assert len(job.id) == 36  # UUID format

    def test_two_jobs_have_different_ids(self):
        j1 = EchoJob()
        j2 = EchoJob()
        assert j1.id != j2.id

    async def test_handle_runs(self):
        job = EchoJob(message="test")
        await job.handle()  # no exception

    async def test_failed_hook_runs(self):
        job = FailingJob()
        await job.failed(RuntimeError("x"))

    async def test_on_retry_hook_runs(self):
        job = FailingJob()
        await job.on_retry(1, RuntimeError("x"))


class TestJobSerialization:
    def test_serialize_contains_expected_keys(self):
        job = EchoJob(message="world")
        data = job.serialize()
        assert data["id"] == job.id
        assert data["queue"] == "default"
        assert data["class"].endswith("EchoJob")
        assert data["status"] == "pending"
        assert "created_at" in data
        assert "payload" in data

    def test_serialize_payload_contains_custom_fields(self):
        job = EchoJob(message="custom")
        data = job.serialize()
        assert data["payload"]["message"] == "custom"

    def test_serialize_scheduled_at_none(self):
        job = EchoJob()
        data = job.serialize()
        assert data["scheduled_at"] is None

    def test_deserialize_roundtrip(self):
        job = EchoJob(message="roundtrip")
        data = job.serialize()
        restored = EchoJob.deserialize(data)
        assert restored.id == job.id
        assert restored.queue == job.queue
        assert restored.status == job.status
        assert restored.attempts == job.attempts
