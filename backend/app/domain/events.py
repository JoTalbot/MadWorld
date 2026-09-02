"""Versioned domain event envelope and schema registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Callable
from uuid import UUID, uuid4

from app.domain.primitives import utc_now


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: UUID
    event_type: str
    schema_version: int
    aggregate_type: str
    aggregate_id: UUID
    occurred_at: datetime
    payload: dict
    def to_dict(self) -> dict:
        value = asdict(self); value["event_id"] = str(self.event_id); value["aggregate_id"] = str(self.aggregate_id); value["occurred_at"] = self.occurred_at.isoformat(); return value


EventValidator = Callable[[dict], None]

def _require_keys(*keys: str) -> EventValidator:
    def validate(payload: dict) -> None:
        missing = [key for key in keys if key not in payload]
        if missing: raise ValueError(f"event payload missing required fields: {', '.join(missing)}")
    return validate


class EventSchemaRegistry:
    def __init__(self) -> None: self._validators: dict[tuple[str, int], EventValidator] = {}
    def register(self, event_type: str, schema_version: int, validator: EventValidator) -> None:
        if not event_type or schema_version < 1: raise ValueError("event type and schema version must be valid")
        key = (event_type, schema_version)
        if key in self._validators: raise ValueError(f"event schema already registered: {event_type} v{schema_version}")
        self._validators[key] = validator
    def validate(self, event_type: str, schema_version: int, payload: dict) -> None:
        validator = self._validators.get((event_type, schema_version))
        if validator is None: raise ValueError(f"unknown event schema: {event_type} v{schema_version}")
        validator(payload)
    def create(self, event_type: str, aggregate_type: str, aggregate_id: UUID, payload: dict, *, schema_version: int = 1, event_id: UUID | None = None, occurred_at: datetime | None = None) -> EventEnvelope:
        self.validate(event_type, schema_version, payload)
        return EventEnvelope(event_id or uuid4(), event_type, schema_version, aggregate_type, aggregate_id, occurred_at or utc_now(), dict(payload))


def build_default_registry() -> EventSchemaRegistry:
    registry = EventSchemaRegistry()
    registry.register("wallet.entry_posted", 1, _require_keys("entry_id", "amount", "reason", "actor_id"))
    registry.register("inventory.item_added", 1, _require_keys("item_definition_id", "quantity", "condition"))
    registry.register("inventory.item_removed", 1, _require_keys("item_definition_id", "quantity"))
    registry.register("job.created", 1, _require_keys("job_type")); registry.register("job.started", 1, _require_keys("state")); registry.register("job.completed", 1, _require_keys("state")); registry.register("job.cancelled", 1, _require_keys("state"))
    registry.register("character.created", 1, _require_keys("player_id", "name"))
    registry.register("vehicle.created", 1, _require_keys("owner_id", "code", "chassis_code", "starter"))
    return registry


DEFAULT_EVENT_REGISTRY = build_default_registry()
