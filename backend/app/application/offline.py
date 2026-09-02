"""Offline command journal primitives.

A mobile client may resend a command after a timeout. Commands are identified by
stable UUIDs and are intended to be persisted through the existing idempotency
boundary before any domain mutation is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OfflineCommand:
    command_id: UUID
    command_name: str
    created_at: datetime
    payload: dict

    def __post_init__(self) -> None:
        if not self.command_name:
            raise ValueError("command name must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("command time must be timezone-aware")


class OfflineCommandJournal:
    """Deterministic in-memory journal used to define retry semantics."""

    def __init__(self) -> None:
        self._commands: dict[UUID, OfflineCommand] = {}

    def append(self, command: OfflineCommand) -> bool:
        existing = self._commands.get(command.command_id)
        if existing is not None:
            if existing != command:
                raise ValueError("command id already contains a different operation")
            return False
        self._commands[command.command_id] = command
        return True

    def get(self, command_id: UUID) -> OfflineCommand | None:
        return self._commands.get(command_id)

    def pending(self) -> list[OfflineCommand]:
        return list(self._commands.values())
