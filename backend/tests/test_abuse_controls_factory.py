from app.infrastructure.abuse_controls import build_abuse_controls
from app.security import AbuseScorer, ReplayGuard, SlidingWindowRateLimiter


def test_memory_backend_never_touches_engine_factory() -> None:
    def boom(): raise AssertionError("engine must not be created for memory backend")
    limiter, guard, scorer = build_abuse_controls("memory", boom, rate_limit=5)
    assert isinstance(limiter, SlidingWindowRateLimiter) and isinstance(guard, ReplayGuard) and isinstance(scorer, AbuseScorer) and limiter.limit == 5
