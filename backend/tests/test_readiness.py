from datetime import UTC, datetime, timedelta, timezone

from app.infrastructure.readiness import evaluate_readiness

NOW = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)


class _Result:
    def __init__(self, scalar=None, row=None): self._scalar = scalar; self._row = row
    def scalar(self): return self._scalar
    def mappings(self): return self
    def first(self): return self._row


def _fake(migrations: int, last_tick_at):
    def execute(sql, params=None):
        if "schema_migrations" in sql: return _Result(scalar=migrations)
        if "world_simulation_state" in sql: return _Result(row=None if last_tick_at is None else {"season": 1, "tick": 42, "last_tick_at": last_tick_at})
        return _Result(scalar=1)
    return execute


def test_ready_when_tick_is_fresh() -> None:
    report = evaluate_readiness(_fake(34, NOW - timedelta(seconds=30)), max_tick_lag_seconds=900, now=NOW)
    assert report["status"] == "ok" and report["world_tick"]["state"] == "fresh" and report["world_tick"]["lag_seconds"] == 30 and report["world_tick"]["tick"] == 42


def test_degraded_when_tick_is_stale() -> None:
    report = evaluate_readiness(_fake(34, NOW - timedelta(hours=1)), max_tick_lag_seconds=900, now=NOW)
    assert report["status"] == "degraded" and report["world_tick"]["state"] == "stale" and report["database"] == "ok"


def test_degraded_when_unmigrated_or_tick_row_missing() -> None:
    assert evaluate_readiness(_fake(0, NOW), max_tick_lag_seconds=900, now=NOW)["schema"] == "unmigrated"
    assert evaluate_readiness(_fake(34, None), max_tick_lag_seconds=900, now=NOW)["world_tick"] == "missing"
