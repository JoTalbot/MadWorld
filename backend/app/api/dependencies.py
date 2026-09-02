"""HTTP dependencies and infrastructure wiring."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache
from uuid import UUID

from fastapi import Header, HTTPException

from app.application.ports import UnitOfWork
from app.infrastructure.db import create_engine_from_env
from app.infrastructure.postgres import PostgresUnitOfWork
from app.api.session_routes import resolve_session


@lru_cache(maxsize=1)
def get_engine():
    """Create one process-local SQLAlchemy engine lazily."""
    return create_engine_from_env()


def get_uow() -> Generator[UnitOfWork, None, None]:
    """Open one authoritative UoW for an HTTP command."""
    with PostgresUnitOfWork(get_engine()) as uow:
        yield uow


def get_authenticated_player(authorization: str | None = Header(default=None)) -> UUID:
    """Resolve the caller from a bearer session token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="bearer session token is required")
    return resolve_session(authorization[7:].strip())
