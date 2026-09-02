"""Trusted service worker for the authoritative Phase 6 world clock.

Run as a single long-lived process. PostgreSQL advisory locking makes a second
instance harmless, so deployments may temporarily overlap during restarts.
"""
from __future__ import annotations

import logging
import os
import time

from sqlalchemy import text

from app.application.phase6_world import simulate_tick
from app.infrastructure.db import create_engine_from_env

LOG = logging.getLogger("madworld.world_tick")
LOCK_KEY = 6_2026_01


def tick_once(engine) -> dict | None:
    with engine.begin() as conn:
        locked = conn.execute(
            text("SELECT pg_try_advisory_xact_lock(:key)"),
            {"key": LOCK_KEY},
        ).scalar()
        if not locked:
            return None
        return simulate_tick(conn)


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
                    LOG.info(
                        "world tick=%s events=%s missions=%s",
                        result["tick"], result["generated_events"], result["generated_missions"],
                    )
            except Exception:
                LOG.exception("world tick failed; state transaction was rolled back")
            time.sleep(max(0, interval - (time.monotonic() - started)))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
