"""Idempotent bridge for world events into future domain consumers.

Consumers claim an event with a persistent fence before applying a domain
command. The helper intentionally does not mutate economy or territory state;
those mutations belong to their respective domain services.
"""
from __future__ import annotations

import json
from hashlib import sha256
from uuid import UUID

from sqlalchemy import text


def consume_once(conn, consumer_name: str, world_event_id: UUID, payload: dict, apply) -> bool:
    """Apply a world event at most once for a named consumer.

    The fence and domain mutation must execute in the caller's transaction.
    Returning False means the event was already consumed. If ``apply`` raises,
    the surrounding transaction rolls back and the fence is not retained.
    """
    if not consumer_name or len(consumer_name) > 128:
        raise ValueError("invalid consumer name")
    payload_hash = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    claimed = conn.execute(
        text("""
            INSERT INTO world_event_consumptions(consumer_name, world_event_id, payload_hash)
            VALUES (:consumer, :event_id, :payload_hash)
            ON CONFLICT (consumer_name, world_event_id) DO NOTHING
            RETURNING world_event_id
        """),
        {"consumer": consumer_name, "event_id": world_event_id, "payload_hash": payload_hash},
    ).first()
    if not claimed:
        return False
    apply(payload)
    return True
