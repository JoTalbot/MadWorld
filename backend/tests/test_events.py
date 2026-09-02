from datetime import timedelta
from uuid import uuid4

import pytest

from app.domain.events import DEFAULT_EVENT_REGISTRY, EventEnvelope, EventSchemaRegistry
from app.domain.primitives import utc_now


def test_event_envelope_is_stable_and_serializable() -> None:
    aggregate_id = uuid4()
    occurred_at = utc_now()
    event = DEFAULT_EVENT_REGISTRY.create(
        "job.started",
        "job",
        aggregate_id,
        {"state": "running"},
        event_id=uuid4(),
        occurred_at=occurred_at,
    )

    value = event.to_dict()
    assert set(value) == {
        "event_id",
        "event_type",
        "schema_version",
        "aggregate_type",
        "aggregate_id",
        "occurred_at",
        "payload",
    }
    assert value["event_type"] == "job.started"
    assert value["schema_version"] == 1
    assert value["aggregate_id"] == str(aggregate_id)
    assert value["payload"] == {"state": "running"}


def test_registry_rejects_unknown_event_schema() -> None:
    with pytest.raises(ValueError, match="unknown event schema"):
        DEFAULT_EVENT_REGISTRY.create("job.started", "job", uuid4(), {"state": "running"}, schema_version=2)


def test_registry_rejects_invalid_payload() -> None:
    with pytest.raises(ValueError, match="missing required fields"):
        DEFAULT_EVENT_REGISTRY.create("job.started", "job", uuid4(), {})


def test_registry_rejects_duplicate_schema_registration() -> None:
    registry = EventSchemaRegistry()
    registry.register("example.created", 1, lambda payload: None)
    with pytest.raises(ValueError, match="already registered"):
        registry.register("example.created", 1, lambda payload: None)


def test_envelope_defaults_are_unique_and_versioned() -> None:
    first = DEFAULT_EVENT_REGISTRY.create("job.completed", "job", uuid4(), {"state": "completed"})
    second = DEFAULT_EVENT_REGISTRY.create("job.completed", "job", uuid4(), {"state": "completed"})
    assert isinstance(first, EventEnvelope)
    assert first.event_id != second.event_id
    assert first.schema_version == 1
    assert second.occurred_at >= first.occurred_at - timedelta(seconds=1)
