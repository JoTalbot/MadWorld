"""Minimal persistent player/session boundary for the first Android vertical slice."""

from __future__ import annotations

import secrets
from datetime import timedelta
from functools import lru_cache
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

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
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="bearer session token is required")
    return token


@router.delete("/current", status_code=204, response_class=Response)
def revoke_current_session(authorization: str | None = Header(default=None), store: SessionStore = Depends(get_session_store)) -> Response:
    """Log out: revoke the presented session token."""
    token = _bearer(authorization)
    if store.resolve(token, utc_now()) is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    store.revoke(token, utc_now())
    return Response(status_code=204)


@router.delete("", response_model=SessionRevokeAllResponse)
def revoke_all_sessions(authorization: str | None = Header(default=None), store: SessionStore = Depends(get_session_store)) -> SessionRevokeAllResponse:
    """Log out everywhere: revoke every active session of the authenticated player."""
    token = _bearer(authorization)
    player_id = store.resolve(token, utc_now())
    if player_id is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return SessionRevokeAllResponse(player_id=player_id, revoked=store.revoke_all(player_id, utc_now()))


class PushTokenRequest(BaseModel):
    token: str = Field(min_length=20, max_length=4096)
    platform: str = Field(default="android", pattern=r"^android$")


class PushTokenResponse(BaseModel):
    registered: bool
    platform: str


@router.put("/push-token", response_model=PushTokenResponse)
def register_push_token(payload: PushTokenRequest, authorization: str | None = Header(default=None)) -> PushTokenResponse:
    """Register or refresh one FCM token for the authenticated player.

    The token is stored as opaque data and is never returned in API responses.
    """
    token = _bearer(authorization)
    player_id = resolve_session(token)
    from app.api.dependencies import get_engine
    with get_engine().begin() as conn:
        conn.execute(
            text("""INSERT INTO device_push_tokens (player_id, token, platform, enabled, updated_at)
                    VALUES (:player_id, :token, 'android', TRUE, NOW())
                    ON CONFLICT (player_id, token) DO UPDATE
                    SET platform = EXCLUDED.platform, enabled = TRUE, updated_at = NOW()"""),
            {"player_id": str(player_id), "token": payload.token},
        )
    return PushTokenResponse(registered=True, platform=payload.platform)


@router.delete("/push-token", status_code=204, response_class=Response)
def unregister_push_token(payload: PushTokenRequest, authorization: str | None = Header(default=None)) -> Response:
    """Disable one previously registered FCM token for the authenticated player."""
    token = _bearer(authorization)
    player_id = resolve_session(token)
    from app.api.dependencies import get_engine
    with get_engine().begin() as conn:
        conn.execute(text("UPDATE device_push_tokens SET enabled = FALSE, updated_at = NOW() WHERE player_id = :player_id AND token = :token"), {"player_id": str(player_id), "token": payload.token})
    return Response(status_code=204)


def resolve_session(token: str, store: SessionStore | None = None) -> UUID:
    """Resolve an active session and update its last-seen timestamp."""
    if not token.strip():
        raise HTTPException(status_code=401, detail="session token is required")
    player_id = (store or get_session_store()).resolve(token, utc_now())
    if player_id is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return player_id
