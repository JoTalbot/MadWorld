from pathlib import Path


def test_production_compose_defines_api_worker_and_migrator():
    text = Path(__file__).parents[2].joinpath("ops/docker-compose.production.yml").read_text()
    for service in ("api:", "world-tick-worker:", "migrator:"):
        assert service in text
    assert "MADWORLD_DATABASE_URL" in text
    assert "MADWORLD_WORLD_TICK_SECONDS" in text


def test_backend_image_is_non_root():
    text = Path(__file__).parents[2].joinpath("ops/Dockerfile.backend").read_text()
    assert "USER 10001" in text


def test_backup_restore_script_is_fail_fast_and_verifies_schema():
    text = Path(__file__).parents[2].joinpath("ops/backup_restore.sh").read_text()
    assert "set -euo pipefail" in text
    assert "pg_dump" in text
    assert "pg_restore" in text
    assert "schema_migrations" in text


def test_operations_docs_define_recovery_order_and_catch_up_boundary():
    text = Path(__file__).parents[2].joinpath("ops/README.md").read_text()
    assert "Catch-up policy" in text
    assert "Recovery priority" in text
    assert "PostgreSQL" in text
