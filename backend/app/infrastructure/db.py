"""SQLAlchemy engine factory for the authoritative PostgreSQL store."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def database_url() -> str:
    """Return the configured PostgreSQL URL.

    The application intentionally does not provide a production default. A
    missing URL is a configuration error rather than an accidental local DB.
    """
    value = os.getenv("MADWORLD_DATABASE_URL")
    if not value:
        raise RuntimeError("MADWORLD_DATABASE_URL is required")
    return value


def create_engine_from_env() -> Engine:
    return create_engine(
        database_url(),
        future=True,
        pool_pre_ping=True,
        pool_size=int(os.getenv("MADWORLD_DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("MADWORLD_DB_MAX_OVERFLOW", "10")),
    )
