"""Apply authoritative PostgreSQL migrations."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.infrastructure.db import create_engine_from_env
from app.infrastructure.migrations import apply_migrations

if __name__ == "__main__":
    root = BACKEND_ROOT
    engine = create_engine_from_env()
    with engine.begin() as conn:
        applied = apply_migrations(conn, root / "migrations")
    for name in applied:
        print(f"applied {name}")
