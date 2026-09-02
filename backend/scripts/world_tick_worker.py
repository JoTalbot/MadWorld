"""Trusted service worker for the authoritative Phase 6 world clock."""
from __future__ import annotations

import logging
import os
import time

from sqlalchemy import text

from app.application.phase6_world import simulate_tick
from app.application.world_tick_pipeline_v2 import run_world_tick
from app.infrastructure.db import create_engine_from_env

LOG = logging.getLogger("madworld.world_tick")
LOCK_KEY = 6_2026_01


def tick_once(engine) -> dict | None:
    with engine.begin() as conn:
        locked = conn.execute(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": LOCK_KEY}).scalar()
        if not locked:
            return None
        result = simulate_tick(conn)
        # The simulator has already committed this tick inside the current
        # transaction. Passing the previous tick to the pipeline makes it load
        # the just-recorded result and apply integration without advancing twice.
        if isinstance(result, dict) and "seed" in result and "tick" in result:
            return run_world_tick(conn, expected_tick=int(result["tick"]) - 1)
        # Compatibility path retained for the lightweight worker unit tests.
        return result


def main() -> None:
    logging.basicConfig(level=os.getenv("MADWORLD_LOG_LEVEL", "INFO"))
    interval = max(5, int(os.getenv("MADWORLD_WORLD_TICK_SECONDS", "60")))
    engine = create_engine_from_env()
    LOG.info("world tick worker started interval=%ss", interval)
    try:
        while True:
            started = time.monotonic()
            try:
                result = tick_once(engine)
                if result is None:
                    LOG.info("world tick skipped: another worker owns the lock")
                else:
                    LOG.info("world tick=%s events=%s missions=%s duration_ms=%s lag_ms=%s",
                             result["tick"], result.get("generated_events", 0), result.get("generated_missions", 0),
                             result.get("tick_duration_ms", 0), result.get("lag_ms", 0))
            except Exception:
                LOG.exception("world tick failed; state transaction was rolled back")
            time.sleep(max(0, interval - (time.monotonic() - started)))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
