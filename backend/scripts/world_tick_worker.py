"""Trusted service worker for the authoritative Phase 6 world clock."""
from __future__ import annotations

import logging
import os
import time

from sqlalchemy import text

from app.application.world_tick_pipeline_v2 import run_world_tick
from app.infrastructure.abuse_controls import prune_expired
from app.infrastructure.db import create_engine_from_env

LOG = logging.getLogger("madworld.world_tick")
LOCK_KEY = 6_2026_01


def tick_once(engine) -> dict | None:
    with engine.begin() as conn:
        locked = conn.execute(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": LOCK_KEY}).scalar()
        if not locked:
            return None
        return run_world_tick(conn)


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
                    # Housekeeping piggybacks on tick ownership so only one worker prunes.
                    try:
                        pruned = prune_expired(engine)
                        if any(pruned.values()): LOG.info("abuse-control prune hits=%s replays=%s scores=%s", pruned["hits"], pruned["replays"], pruned["scores"])
                    except Exception:
                        LOG.exception("abuse-control prune failed")
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
