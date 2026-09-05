"""Apply authoritative PostgreSQL migrations."""

from pathlib import Path

from app.infrastructure.db import create_engine_from_env
from app.infrastructure.migrations import apply_migrations

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    engine = create_engine_from_env()
    with engine.begin() as conn:
        applied = apply_migrations(conn, root / "migrations")
    for name in applied:
        print(f"applied {name}")
