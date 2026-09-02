"""Small structured observability primitives for authoritative commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from time import perf_counter
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CommandMetric:
    command: str
    duration_ms: float
    success: bool
    request_id: UUID | None = None


class MetricsRecorder:
    def __init__(self) -> None:
        self.command_metrics: list[CommandMetric] = []

    def record_command(self, command: str, duration_ms: float, success: bool, request_id: UUID | None = None) -> None:
        self.command_metrics.append(CommandMetric(command, duration_ms, success, request_id))


class StructuredLogger:
    """JSON-shaped records without coupling application code to a logging backend."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def emit(self, level: str, event: str, *, request_id: UUID | None = None, occurred_at: datetime | None = None, **fields: Any) -> None:
        self.records.append({
            "level": level,
            "event": event,
            "request_id": str(request_id) if request_id else None,
            "occurred_at": (occurred_at or datetime.now().astimezone()).isoformat(),
            **fields,
        })


def timed_command(metrics: MetricsRecorder, command: str, request_id: UUID | None = None):
    """Decorator helper for command boundaries; callers retain transaction ownership."""
    def decorate(fn):
        def wrapped(*args, **kwargs):
            started = perf_counter()
            try:
                result = fn(*args, **kwargs)
                metrics.record_command(command, (perf_counter() - started) * 1000, True, request_id)
                return result
            except Exception:
                metrics.record_command(command, (perf_counter() - started) * 1000, False, request_id)
                raise
        return wrapped
    return decorate
