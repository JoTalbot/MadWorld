"""Small deterministic scheduler for durable jobs.

The scheduler only decides which persisted jobs are due. State transitions remain
owned by the application/domain layer, so workers cannot bypass authoritative rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.clock import Clock
from app.application.ports import UnitOfWork
from app.application.services import JobService


@dataclass(frozen=True, slots=True)
class DueJob:
    job_id: UUID
    completes_at: datetime


class JobScheduler:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self.uow = uow
        self.clock = clock

    def due(self, job_ids: list[UUID]) -> list[DueJob]:
        now = self.clock.now()
        result: list[DueJob] = []
        for job_id in job_ids:
            job = self.uow.jobs.get(job_id)
            if job is not None and job.state.value in {"QUEUED", "RUNNING"} and job.completes_at <= now:
                result.append(DueJob(job.id, job.completes_at))
        return result

    def complete_due(self, job_ids: list[UUID]) -> list[UUID]:
        completed: list[UUID] = []
        service = JobService(self.uow)
        for due in self.due(job_ids):
            job = service.complete(due.job_id, now=self.clock.now())
            completed.append(job.id)
        return completed
