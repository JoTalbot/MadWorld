"""PostgreSQL-backed abuse controls shared across API processes.

The in-memory primitives in ``app.security`` protect a single process. These
implementations provide the same interface (``check`` / ``check_and_remember``
/ ``add`` / ``score`` / ``is_abusive``) on top of the ``abuse_control_*``
tables so any number of API replicas enforce one shared policy.

Failure policy: the controls are **fail-open** – if PostgreSQL is unreachable
the request is allowed and the error is logged, because blocking all traffic
on a control-plane outage is worse than a temporary loss of rate limiting.
The readiness probe surfaces the database outage separately.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.domain.primitives import utc_now
from app.security import AbuseScorer, RateLimitDecision, ReplayGuard, SlidingWindowRateLimiter

logger = logging.getLogger("madworld.security")


class RateLimiter(Protocol):
    limit: int
    def check(self, key: str) -> RateLimitDecision: ...


class ReplayDetector(Protocol):
    def check_and_remember(self, key: str) -> bool: ...


class Scorer(Protocol):
    def add(self, actor: str, points: int) -> int: ...
    def score(self, actor: str) -> int: ...
    def is_abusive(self, actor: str) -> bool: ...


class PostgresRateLimiter:
    def __init__(self, engine: Engine, limit: int = 120, window_seconds: int = 60) -> None:
        if limit <= 0 or window_seconds <= 0: raise ValueError("rate-limit parameters must be positive")
        self.engine = engine; self.limit = limit; self.window_seconds = window_seconds

    def check(self, key: str, now: datetime | None = None) -> RateLimitDecision:
        current = now or utc_now(); cutoff = current - timedelta(seconds=self.window_seconds)
        try:
            with self.engine.begin() as conn:
                conn.execute(text("DELETE FROM abuse_control_hits WHERE control_key = :key AND hit_at <= :cutoff"), {"key": key, "cutoff": cutoff})
                # Serialize concurrent checks for the same key with an advisory xact lock so two
                # requests cannot both observe limit-1 and both be admitted.
                conn.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": key})
                count = int(conn.execute(text("SELECT COUNT(*) FROM abuse_control_hits WHERE control_key = :key AND hit_at > :cutoff"), {"key": key, "cutoff": cutoff}).scalar_one())
                if count >= self.limit:
                    oldest = conn.execute(text("SELECT MIN(hit_at) FROM abuse_control_hits WHERE control_key = :key AND hit_at > :cutoff"), {"key": key, "cutoff": cutoff}).scalar_one()
                    retry = max(1, int((oldest + timedelta(seconds=self.window_seconds) - current).total_seconds() + 0.999))
                    return RateLimitDecision(False, 0, retry)
                conn.execute(text("INSERT INTO abuse_control_hits (control_key, hit_at) VALUES (:key, :at)"), {"key": key, "at": current})
                return RateLimitDecision(True, self.limit - count - 1, 0)
        except Exception:  # noqa: BLE001 - fail open, see module docstring
            logger.exception("rate limiter storage unavailable; allowing request")
            return RateLimitDecision(True, self.limit, 0)

    def reset(self, key: str) -> None:
        with self.engine.begin() as conn: conn.execute(text("DELETE FROM abuse_control_hits WHERE control_key = :key"), {"key": key})


class PostgresReplayGuard:
    def __init__(self, engine: Engine, ttl_seconds: int = 300) -> None:
        self.engine = engine; self.ttl_seconds = ttl_seconds

    def check_and_remember(self, key: str, now: datetime | None = None) -> bool:
        current = now or utc_now()
        try:
            with self.engine.begin() as conn:
                conn.execute(text("DELETE FROM abuse_control_replays WHERE expires_at <= :now"), {"now": current})
                inserted = conn.execute(
                    text("""INSERT INTO abuse_control_replays (replay_key, seen_at, expires_at) VALUES (:key, :now, :expires)
                            ON CONFLICT (replay_key) DO NOTHING"""),
                    {"key": key, "now": current, "expires": current + timedelta(seconds=self.ttl_seconds)},
                ).rowcount
                return inserted == 1
        except Exception:  # noqa: BLE001
            logger.exception("replay guard storage unavailable; allowing request")
            return True


class PostgresAbuseScorer:
    def __init__(self, engine: Engine, decay_seconds: int = 300, threshold: int = 100) -> None:
        self.engine = engine; self.decay_seconds = decay_seconds; self.threshold = threshold

    @staticmethod
    def _decay(score: int, at: datetime, now: datetime, decay_seconds: int) -> int:
        elapsed = max(0.0, (now - at).total_seconds())
        return max(0, int(score * max(0.0, 1.0 - elapsed / decay_seconds)))

    def add(self, actor: str, points: int, now: datetime | None = None) -> int:
        current = now or utc_now()
        try:
            with self.engine.begin() as conn:
                row = conn.execute(text("SELECT score, updated_at FROM abuse_control_scores WHERE actor = :actor FOR UPDATE"), {"actor": actor}).mappings().first()
                base = self._decay(int(row["score"]), row["updated_at"], current, self.decay_seconds) if row else 0
                score = max(0, base + points)
                conn.execute(
                    text("""INSERT INTO abuse_control_scores (actor, score, updated_at) VALUES (:actor, :score, :now)
                            ON CONFLICT (actor) DO UPDATE SET score = EXCLUDED.score, updated_at = EXCLUDED.updated_at"""),
                    {"actor": actor, "score": score, "now": current},
                )
                return score
        except Exception:  # noqa: BLE001
            logger.exception("abuse scorer storage unavailable; skipping score update")
            return 0

    def score(self, actor: str, now: datetime | None = None) -> int:
        current = now or utc_now()
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT score, updated_at FROM abuse_control_scores WHERE actor = :actor"), {"actor": actor}).mappings().first()
        return self._decay(int(row["score"]), row["updated_at"], current, self.decay_seconds) if row else 0

    def is_abusive(self, actor: str) -> bool: return self.score(actor) >= self.threshold


def prune_expired(engine: Engine, now: datetime | None = None, rate_window_seconds: int = 60, score_decay_seconds: int = 300) -> dict[str, int]:
    """Bulk prune for operators / periodic jobs. Per-key pruning already happens on the hot path."""
    current = now or utc_now()
    with engine.begin() as conn:
        hits = conn.execute(text("DELETE FROM abuse_control_hits WHERE hit_at <= :cutoff"), {"cutoff": current - timedelta(seconds=rate_window_seconds)}).rowcount
        replays = conn.execute(text("DELETE FROM abuse_control_replays WHERE expires_at <= :now"), {"now": current}).rowcount
        scores = conn.execute(text("DELETE FROM abuse_control_scores WHERE updated_at <= :cutoff"), {"cutoff": current - timedelta(seconds=score_decay_seconds)}).rowcount
    return {"hits": hits, "replays": replays, "scores": scores}


def build_abuse_controls(backend: str, engine_factory, *, rate_limit: int = 120, rate_window_seconds: int = 60, replay_ttl_seconds: int = 300, score_decay_seconds: int = 300, score_threshold: int = 100) -> tuple[RateLimiter, ReplayDetector, Scorer]:
    """Select the abuse-control backend.

    ``backend`` is ``"memory"`` (single process only) or ``"postgres"`` (shared).
    ``engine_factory`` is called lazily and only for the postgres backend.
    """
    if backend == "memory":
        return (SlidingWindowRateLimiter(rate_limit, rate_window_seconds), ReplayGuard(replay_ttl_seconds, 10000), AbuseScorer(score_decay_seconds, score_threshold))
    if backend == "postgres":
        engine = engine_factory()
        return (PostgresRateLimiter(engine, rate_limit, rate_window_seconds), PostgresReplayGuard(engine, replay_ttl_seconds), PostgresAbuseScorer(engine, score_decay_seconds, score_threshold))
    raise ValueError(f"unknown abuse-control backend: {backend!r} (expected 'memory' or 'postgres')")
