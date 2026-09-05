"""Shared abuse controls against PostgreSQL (integration)."""
import os
from datetime import timedelta
from uuid import uuid4

import pytest

from app.domain.primitives import utc_now
from app.infrastructure.abuse_controls import PostgresAbuseScorer, PostgresRateLimiter, PostgresReplayGuard, build_abuse_controls, prune_expired
from app.infrastructure.db import create_engine_from_env

pytestmark = pytest.mark.integration


@pytest.fixture
def engine():
    if not os.getenv("MADWORLD_DATABASE_URL"): pytest.skip("MADWORLD_DATABASE_URL is not configured")
    eng = create_engine_from_env(); yield eng; eng.dispose()


def test_rate_limit_is_shared_between_limiter_instances(engine) -> None:
    key = f"client-{uuid4()}"; a = PostgresRateLimiter(engine, limit=3, window_seconds=60); b = PostgresRateLimiter(engine, limit=3, window_seconds=60)
    now = utc_now()
    assert a.check(key, now).allowed and b.check(key, now).allowed and a.check(key, now).remaining == 0
    denied = b.check(key, now); assert not denied.allowed and denied.retry_after >= 1
    later = now + timedelta(seconds=61); assert a.check(key, later).allowed
    a.reset(key)


def test_replay_guard_rejects_duplicate_across_instances_until_ttl(engine) -> None:
    key = f"POST:/x:{uuid4()}"; a = PostgresReplayGuard(engine, ttl_seconds=5); b = PostgresReplayGuard(engine, ttl_seconds=5); now = utc_now()
    assert a.check_and_remember(key, now) and not b.check_and_remember(key, now)
    assert b.check_and_remember(key, now + timedelta(seconds=6))


def test_abuse_score_accumulates_and_decays(engine) -> None:
    actor = f"actor-{uuid4()}"; s = PostgresAbuseScorer(engine, decay_seconds=100, threshold=50); now = utc_now()
    assert s.add(actor, 30, now) == 30 and s.add(actor, 30, now) == 60 and s.is_abusive(actor)
    assert s.add(actor, 0, now + timedelta(seconds=50)) == 30 and s.score(actor, now + timedelta(seconds=200)) == 0


def test_prune_and_factory(engine) -> None:
    limiter, guard, scorer = build_abuse_controls("postgres", lambda: engine)
    assert isinstance(limiter, PostgresRateLimiter) and isinstance(guard, PostgresReplayGuard) and isinstance(scorer, PostgresAbuseScorer)
    stats = prune_expired(engine, utc_now() + timedelta(days=1)); assert set(stats) == {"hits", "replays", "scores"}
    with pytest.raises(ValueError): build_abuse_controls("redis", lambda: engine)
