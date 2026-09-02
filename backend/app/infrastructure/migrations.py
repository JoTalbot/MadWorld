"""Deterministic SQL migration runner with schema history and checksums."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Connection, text


@dataclass(frozen=True, slots=True)
class Migration:
    name: str
    checksum: str
    sql: str


def discover_migrations(directory: Path) -> list[Migration]:
    files = sorted(directory.glob("*.sql"))
    migrations: list[Migration] = []
    for path in files:
        sql = path.read_text(encoding="utf-8")
        migrations.append(Migration(path.name, hashlib.sha256(sql.encode("utf-8")).hexdigest(), sql))
    return migrations


def ensure_history_table(conn: Connection) -> None:
    if conn.dialect.name == "sqlite":
        ddl = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                checksum TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
    else:
        ddl = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                checksum TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """
    conn.execute(text(ddl))


def apply_migrations(conn: Connection, directory: Path) -> list[str]:
    ensure_history_table(conn)
    applied = {
        row.name: row.checksum
        for row in conn.execute(text("SELECT name, checksum FROM schema_migrations ORDER BY version")).mappings()
    }
    applied_now: list[str] = []
    for migration in discover_migrations(directory):
        previous = applied.get(migration.name)
        if previous is not None:
            if previous != migration.checksum:
                raise RuntimeError(f"migration checksum mismatch: {migration.name}")
            continue
        # Migration files are already complete SQL programs. Execute them at the
        # DB-driver level so SQLAlchemy's text() parameter parser cannot mistake
        # JSON/SQL contents such as "%(5)s" for application bind parameters.
        conn.exec_driver_sql(migration.sql)
        conn.execute(
            text("INSERT INTO schema_migrations (name, checksum) VALUES (:name, :checksum)"),
            {"name": migration.name, "checksum": migration.checksum},
        )
        applied_now.append(migration.name)
    return applied_now
