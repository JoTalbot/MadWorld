"""Shared request idempotency helpers for authoritative API commands."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.application.errors import IdempotencyConflict
from app.application.ports import IdempotencyRecord, UnitOfWork


def request_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def require_key(value: str | None) -> str:
    if not value or not value.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key header is required")
    return value.strip()


def replay_or_none(uow: UnitOfWork, command_name: str, key: str, payload: object):
    record = uow.idempotency.get(command_name, key)
    if record is None:
        return None
    if record.request_hash != request_hash(payload):
        raise IdempotencyConflict("idempotency key belongs to a different request")
    return record.response_payload


def store_response(
    uow: UnitOfWork,
    command_name: str,
    key: str,
    payload: object,
    response_payload: dict,
    status_code: int,
    actor_id: UUID | None = None,
) -> None:
    uow.idempotency.put(
        IdempotencyRecord(
            command_name=command_name,
            idempotency_key=key,
            request_hash=request_hash(payload),
            response_status=status_code,
            response_payload=response_payload,
            actor_id=actor_id,
            created_at=datetime.now(UTC),
        )
    )
