import time

from app.security import SlidingWindowRateLimiter


def test_rate_limiter_remains_bounded_per_window():
    limiter = SlidingWindowRateLimiter(limit=120, window_seconds=60)
    started = time.monotonic()
    decisions = [limiter.check("load-test", now=started + i * 0.01) for i in range(150)]
    assert sum(d.allowed for d in decisions) == 120
    assert all(d.remaining >= 0 for d in decisions)
