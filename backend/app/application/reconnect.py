"""Reconnect/resume primitives for authoritative mobile sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ResumeCursor:
    session_id: UUID
    last_event_id: UUID | None
    issued_at: datetime


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    session_id: UUID
    accepted_command_ids: tuple[UUID, ...]
    rejected_command_ids: tuple[UUID, ...]
    authoritative_event_ids: tuple[UUID, ...]


class ReconnectService:
    """Pure reconciliation policy; persistence and authentication stay outside it."""

    def reconcile(
        self,
        cursor: ResumeCursor,
        command_ids: list[UUID],
        authoritative_event_ids: list[UUID],
        accepted_command_ids: list[UUID],
    ) -> ReconciliationResult:
        accepted = set(accepted_command_ids)
        requested = set(command_ids)
        rejected = requested - accepted
        return ReconciliationResult(
            session_id=cursor.session_id,
            accepted_command_ids=tuple(sorted(accepted & requested, key=str)),
            rejected_command_ids=tuple(sorted(rejected, key=str)),
            authoritative_event_ids=tuple(authoritative_event_ids),
        )
