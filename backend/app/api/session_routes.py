"""Minimal persistent player/session boundary for the first Android vertical slice."""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.domain.primitives import utc_now

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


class SessionCreateRequest(BaseModel):
    handle: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_]+$")


class SessionResponse(BaseModel):
    player_id: UUID
    handle: str
    token: str
    expires_at: str


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _engine():
    from app.api.dependencies import get_engine
    return get_engine()


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(payload: SessionCreateRequest) -> SessionResponse:
    now = utc_now()
    expires = now + timedelta(days=30)
    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)

    with _engine().begin() as conn:
        row = conn.execute(text("SELECT id, handle FROM players WHERE handle = :handle"), {"handle": payload.handle}).mappings().first()
        if row is None:
            row = conn.execute(text("INSERT INTO players (handle) VALUES (:handle) RETURNING id, handle"), {"handle": payload.handle}).mappings().one()
        conn.execute(
            text("""INSERT INTO player_sessions (player_id, token_hash, created_at, last_seen_at, expires_at)
                     VALUES (:player_id, :token_hash, :created_at, :last_seen_at, :expires_at)"""),
            {"player_id": row["id"], "token_hash": token_hash, "created_at": now, "last_seen_at": now, "expires_at": expires},
        )

    return SessionResponse(player_id=UUID(str(row["id"])), handle=str(row["handle"]), token=token, expires_at=expires.isoformat())


def resolve_session(token: str) -> UUID:
    """Resolve an active session and update its last-seen timestamp."""
    if not token.strip():
        raise HTTPException(status_code=401, detail="session token is required")
    now = utc_now()
    with _engine().begin() as conn:
        row = conn.execute(
            text("""SELECT player_id FROM player_sessions
                   WHERE token_hash = :token_hash AND revoked_at IS NULL AND expires_at > :now"""),
            {"token_hash": _hash_token(token), "now": now},
        ).mappings().first()
        if row is None:
            raise HTTPException(status_code=401, detail="invalid or expired session")
        conn.execute(
            text("UPDATE player_sessions SET last_seen_at = :now WHERE token_hash = :token_hash"),
            {"now": now, "token_hash": _hash_token(token)},
        )
        return UUID(str(row["player_id"]))
