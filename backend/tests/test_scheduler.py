from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

from app.application.clock import FixedClock
from app.application.scheduler import JobScheduler
from app.application.services import JobService
from app.domain.primitives import JobState
from app.infrastructure.memory import InMemoryUnitOfWork


def test_fixed_clock_and_scheduler_are_deterministic() -> None:
    start = datetime(2030, 1, 1, tzinfo=UTC)
    clock = FixedClock(start)
    uow = InMemoryUnitOfWork()
    owner = uuid4()
    with uow:
        job = JobService(uow).create(owner, "repair", start, start + timedelta(minutes=10), "job-1")
        assert JobScheduler(uow, clock).due([job.id]) == []
        clock.set(start + timedelta(minutes=10))
        due = JobScheduler(uow, clock).due([job.id])
        assert [item.job_id for item in due] == [job.id]


def test_scheduler_completes_due_job_using_authoritative_service() -> None:
    start = datetime(2030, 1, 1, tzinfo=UTC)
    clock = FixedClock(start)
    uow = InMemoryUnitOfWork()
    with uow:
        job = JobService(uow).create(uuid4(), "production", start, start + timedelta(seconds=30), "job-2")
        JobService(uow).start(job.id)
        clock.set(start + timedelta(seconds=30))
        completed = JobScheduler(uow, clock).complete_due([job.id])
        assert completed == [job.id]
        assert uow.jobs.get(job.id).state == JobState.COMPLETED
