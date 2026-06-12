import asyncio
import signal

from core.logging import Log
from .job import BaseJob, JobStatus
from .queue import Queue


class Worker:
    """
    Воркер — обрабатывает jobs из очереди.
    Паттерн Template Method — процесс обработки фиксирован,
    детали вынесены в BaseJob.handle().

    Использование:
        worker = Worker(queue, queues=["default", "emails"], concurrency=5)
        await worker.run()   # блокирует, слушает очередь
    """

    def __init__(
        self,
        queue: Queue,
        queues: list[str] | None = None,
        concurrency: int = 3,
    ) -> None:
        self._queue = queue
        self._queues = queues or ["default"]
        self._concurrency = concurrency
        self._running = False
        self._semaphore = asyncio.Semaphore(concurrency)
        self._log = Log.get("Worker", queues=self._queues)

    async def run(self) -> None:
        """Запускает воркер. Останавливается по SIGINT/SIGTERM."""
        self._running = True
        self._log.info(f"Worker started | queues={self._queues} concurrency={self._concurrency}")

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._stop)

        tasks = [asyncio.create_task(self._listen(q)) for q in self._queues]
        await asyncio.gather(*tasks)

    def _stop(self) -> None:
        self._log.info("Worker stopping...")
        self._running = False

    async def _listen(self, queue: str) -> None:
        while self._running:
            try:
                job = await self._queue.pop(queue, timeout=2)
                if job:
                    asyncio.create_task(self._process(job))
            except Exception as exc:
                self._log.error(f"Queue pop error on '{queue}': {exc}")
                await asyncio.sleep(1)

    async def _process(self, job: BaseJob) -> None:
        async with self._semaphore:
            job.status = JobStatus.RUNNING
            job.attempts += 1
            self._log.info(f"Processing {job.__class__.__name__} id={job.id} attempt={job.attempts}")
            try:
                await asyncio.wait_for(job.handle(), timeout=job.timeout)
                job.status = JobStatus.DONE
                self._log.info(f"Done {job.__class__.__name__} id={job.id}")
            except Exception as exc:
                await self._handle_failure(job, exc)

    async def _handle_failure(self, job: BaseJob, exc: Exception) -> None:
        self._log.error(f"Job failed {job.__class__.__name__} id={job.id}: {exc}")
        await job.on_retry(job.attempts, exc)

        if job.attempts < job.max_retries:
            job.status = JobStatus.RETRYING
            self._log.info(
                f"Retrying {job.__class__.__name__} id={job.id} "
                f"in {job.retry_delay}s (attempt {job.attempts}/{job.max_retries})"
            )
            await asyncio.sleep(job.retry_delay)
            await self._queue.push(job)
        else:
            job.status = JobStatus.FAILED
            await job.failed(exc)
            await self._queue.push_failed(job, str(exc))
            self._log.error(f"Job exhausted {job.__class__.__name__} id={job.id}")
