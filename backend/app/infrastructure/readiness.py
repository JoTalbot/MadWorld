"""Readiness evaluation shared by the HTTP probe and tests.

``execute`` is any callable ``(sql, params) -> Result`` so the logic can be
exercised against PostgreSQL or a fake without a running server.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from app.domain.primitives import utc_now


def evaluate_readiness(execute: Callable[..., Any], *, max_tick_lag_seconds: int, now: datetime | None = None) -> dict[str, Any]:
    current = now or utc_now()
    execute("SELECT 1")
    migrations = int(execute("SELECT COUNT(*) FROM schema_migrations").scalar())
    row = execute("SELECT season, tick, last_tick_at FROM world_simulation_state WHERE id = 1").mappings().first()
    report: dict[str, Any] = {"status": "ok", "database": "ok", "migrations_applied": migrations}
    if migrations == 0:
        report["status"] = "degraded"; report["schema"] = "unmigrated"; return report
    if row is None:
        report["status"] = "degraded"; report["world_tick"] = "missing"; return report
    lag = max(0, int((current - row["last_tick_at"]).total_seconds()))
    report["world_tick"] = {"season": int(row["season"]), "tick": int(row["tick"]), "last_tick_at": row["last_tick_at"].isoformat(), "lag_seconds": lag, "max_lag_seconds": max_tick_lag_seconds}
    if lag > max_tick_lag_seconds: report["status"] = "degraded"; report["world_tick"]["state"] = "stale"
    else: report["world_tick"]["state"] = "fresh"
    return report
