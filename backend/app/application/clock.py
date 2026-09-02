"""Deterministic clock abstraction for authoritative application services."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.domain.primitives import utc_now


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return utc_now()


class FixedClock:
    def __init__(self, current: datetime) -> None:
        if current.tzinfo is None:
            raise ValueError("clock time must be timezone-aware")
        self._current = current

    def now(self) -> datetime:
        return self._current

    def set(self, current: datetime) -> None:
        if current.tzinfo is None:
            raise ValueError("clock time must be timezone-aware")
        self._current = current
