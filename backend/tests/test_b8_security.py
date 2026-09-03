import pytest

from app.security import AbuseScorer, CircuitBreaker, ReplayGuard, SlidingWindowRateLimiter


def test_rate_limiter_bounds_requests_and_expires_window():
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=10)
    assert limiter.check("actor", now=0).allowed
    assert limiter.check("actor", now=1).allowed
    blocked = limiter.check("actor", now=2)
    assert not blocked.allowed
    assert blocked.retry_after > 0
    assert limiter.check("actor", now=11).allowed


def test_replay_guard_rejects_duplicate_and_expires():
    guard = ReplayGuard(ttl_seconds=5, max_entries=2)
    assert guard.check_and_remember("r1", now=0)
    assert not guard.check_and_remember("r1", now=1)
    assert guard.check_and_remember("r1", now=6)


def test_replay_guard_is_bounded():
    guard = ReplayGuard(ttl_seconds=100, max_entries=2)
    assert guard.check_and_remember("r1", now=0)
    assert guard.check_and_remember("r2", now=1)
    assert guard.check_and_remember("r3", now=2)
    assert guard.check_and_remember("r1", now=3)


def test_circuit_breaker_opens_and_recovers():
    breaker = CircuitBreaker(failure_threshold=2, recovery_seconds=10)
    assert breaker.allow(now=0)
    breaker.record_failure(now=1)
    assert breaker.allow(now=2)
    breaker.record_failure(now=3)
    assert not breaker.allow(now=4)
    assert breaker.allow(now=13)


def test_abuse_score_is_explainable_bounded_and_decays():
    scorer = AbuseScorer(decay_seconds=10, threshold=10)
    assert scorer.add("player", 6, now=0) == 6
    assert scorer.add("player", 6, now=1) == 11
    assert scorer.is_abusive("player")
    assert scorer.add("player", 0, now=20) == 0
    assert not scorer.is_abusive("player")


def test_invalid_security_parameters_fail_fast():
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(limit=0)
    with pytest.raises(ValueError):
        CircuitBreaker(failure_threshold=0)
