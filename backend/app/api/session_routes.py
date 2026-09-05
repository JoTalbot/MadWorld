"""Minimal persistent player/session boundary for the first Android vertical slice."""

from __future__ import annotations

import secrets
from datetime import timedelta
from functools import lru_cache
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.domain.primitives import utc_now
from app.infrastructure.sessions import SessionStore

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

SESSION_TTL = timedelta(days=30)


class SessionCreateRequest(BaseModel):
    handle: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_]+$")


class SessionResponse(BaseModel):
    player_id: UUID
    handle: str
    token: str
    expires_at: str


@lru_cache(maxsize=1)
def get_session_store() -> SessionStore:
    """Default production store. Tests override this dependency with an in-memory store."""
    from app.api.dependencies import get_engine
    from app.infrastructure.sessions import PostgresSessionStore
    return PostgresSessionStore(get_engine())


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(payload: SessionCreateRequest, store: SessionStore = Depends(get_session_store)) -> SessionResponse:
    now = utc_now()
    expires = now + SESSION_TTL
    token = secrets.token_urlsafe(32)
    player = store.create(payload.handle, token, now, expires)
    return SessionResponse(player_id=player.player_id, handle=player.handle, token=token, expires_at=expires.isoformat())


def resolve_session(token: str, store: SessionStore | None = None) -> UUID:
    """Resolve an active session and update its last-seen timestamp."""
    if not token.strip():
        raise HTTPException(status_code=401, detail="session token is required")
    player_id = (store or get_session_store()).resolve(token, utc_now())
    if player_id is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return player_id
