"""HTTP dependencies and infrastructure wiring."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from app.application.ports import UnitOfWork
from app.infrastructure.db import create_engine_from_env
from app.infrastructure.postgres import PostgresUnitOfWork


@lru_cache(maxsize=1)
def get_engine():
    """Create one process-local SQLAlchemy engine lazily."""
    return create_engine_from_env()


def get_uow() -> Generator[UnitOfWork, None, None]:
    """Open one authoritative UoW for an HTTP command."""
    with PostgresUnitOfWork(get_engine()) as uow:
        yield uow
