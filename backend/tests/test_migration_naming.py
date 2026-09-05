from pathlib import Path

import pytest

from app.infrastructure.migrations import LEGACY_DUPLICATE_PREFIXES, check_migration_prefixes, discover_migrations

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


def test_repository_migrations_have_unique_prefixes_outside_legacy_set() -> None:
    names = sorted(p.name for p in MIGRATIONS.glob("*.sql"))
    assert names, "migrations directory must not be empty"
    assert check_migration_prefixes(names) == []


def test_legacy_set_is_not_growing() -> None:
    # Guard against silently expanding the grandfathered list.
    assert LEGACY_DUPLICATE_PREFIXES == frozenset({"003", "009", "010", "011", "012"})


def test_duplicate_prefix_is_reported_and_blocks_discovery(tmp_path: Path) -> None:
    (tmp_path / "034_a.sql").write_text("SELECT 1;"); (tmp_path / "034_b.sql").write_text("SELECT 2;")
    assert check_migration_prefixes(["034_a.sql", "034_b.sql"]) == ["duplicate migration prefix 034: 034_a.sql, 034_b.sql"]
    with pytest.raises(RuntimeError, match="duplicate migration prefix 034"): discover_migrations(tmp_path)


def test_non_numeric_prefix_is_rejected() -> None:
    assert check_migration_prefixes(["init.sql"]) == ["init.sql: migration name must start with a numeric prefix"]
