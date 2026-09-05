"""Minimal persistent player/session boundary for the first Android vertical slice."""

from __future__ import annotations

import secrets
from datetime import timedelta
from functools import lru_cache
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Response
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


class SessionRevokeAllResponse(BaseModel):
    player_id: UUID
    revoked: int


def _bearer(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="bearer session token is required")
    return authorization[7:].strip()


@router.delete("/current", status_code=204, response_class=Response)
def revoke_current_session(authorization: str | None = Header(default=None), store: SessionStore = Depends(get_session_store)) -> Response:
    """Log out: revoke the presented session token. Idempotent for already-revoked tokens of a valid session."""
    token = _bearer(authorization)
    if store.resolve(token, utc_now()) is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    store.revoke(token, utc_now())
    return Response(status_code=204)


@router.delete("", response_model=SessionRevokeAllResponse)
def revoke_all_sessions(authorization: str | None = Header(default=None), store: SessionStore = Depends(get_session_store)) -> SessionRevokeAllResponse:
    """Log out everywhere: revoke every active session of the authenticated player, including this one."""
    token = _bearer(authorization)
    player_id = store.resolve(token, utc_now())
    if player_id is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return SessionRevokeAllResponse(player_id=player_id, revoked=store.revoke_all(player_id, utc_now()))


def resolve_session(token: str, store: SessionStore | None = None) -> UUID:
    """Resolve an active session and update its last-seen timestamp."""
    if not token.strip():
        raise HTTPException(status_code=401, detail="session token is required")
    player_id = (store or get_session_store()).resolve(token, utc_now())
    if player_id is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return player_id
