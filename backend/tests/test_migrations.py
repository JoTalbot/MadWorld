from pathlib import Path

import pytest

from app.infrastructure.migrations import apply_migrations, discover_migrations


def test_migrations_are_deterministic_and_unique() -> None:
    migrations = discover_migrations(Path(__file__).parents[1] / "migrations")
    assert [m.name for m in migrations] == sorted(m.name for m in migrations)
    assert len({m.name for m in migrations}) == len(migrations)
    assert all(len(m.checksum) == 64 for m in migrations)


def test_migration_checksum_mismatch_is_rejected() -> None:
    sqlalchemy = pytest.importorskip("sqlalchemy")
    from sqlalchemy import create_engine, text

    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, checksum TEXT NOT NULL, applied_at TEXT NOT NULL)"))
        conn.execute(text("INSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES (1, '001_foundation.sql', 'bad', 'now')"))
        with pytest.raises(RuntimeError, match="checksum mismatch"):
            apply_migrations(conn, Path(__file__).parents[1] / "migrations")
