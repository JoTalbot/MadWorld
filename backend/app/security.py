"""B8 security primitives: bounded rate limiting, replay detection, circuit breaking and abuse scoring."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after: int

class SlidingWindowRateLimiter:
    def __init__(self, limit: int = 120, window_seconds: int = 60) -> None:
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("rate-limit parameters must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, now: float | None = None) -> RateLimitDecision:
        current = monotonic() if now is None else now
        with self._lock:
            hits = self._hits[key]
            cutoff = current - self.window_seconds
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.limit:
                retry = max(1, int(hits[0] + self.window_seconds - current + 0.999))
                return RateLimitDecision(False, 0, retry)
            hits.append(current)
            return RateLimitDecision(True, self.limit - len(hits), 0)

    def reset(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)

class ReplayGuard:
    """Short-lived request replay guard. Authoritative idempotency remains DB-backed."""
    def __init__(self, ttl_seconds: int = 300, max_entries: int = 10000) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._seen: dict[str, float] = {}
        self._lock = Lock()

    def check_and_remember(self, key: str, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        with self._lock:
            expired = [k for k, t in self._seen.items() if t + self.ttl_seconds <= current]
            for item in expired:
                self._seen.pop(item, None)
            if key in self._seen:
                return False
            if len(self._seen) >= self.max_entries:
                oldest = min(self._seen, key=lambda k: self._seen[k])
                self._seen.pop(oldest, None)
            self._seen[key] = current
            return True

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_seconds: int = 30) -> None:
        if failure_threshold <= 0 or recovery_seconds <= 0:
            raise ValueError("circuit-breaker parameters must be positive")
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.opened_at: float | None = None
        self._lock = Lock()

    def allow(self, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        with self._lock:
            if self.opened_at is None:
                return True
            if current - self.opened_at >= self.recovery_seconds:
                self.opened_at = None
                self.failures = 0
                return True
            return False

    def record_success(self) -> None:
        with self._lock:
            self.failures = 0
            self.opened_at = None

    def record_failure(self, now: float | None = None) -> None:
        current = monotonic() if now is None else now
        with self._lock:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.opened_at = current

class AbuseScorer:
    """Bounded, explainable score suitable for containment decisions in B9."""
    def __init__(self, decay_seconds: int = 300, threshold: int = 100) -> None:
        self.decay_seconds = decay_seconds
        self.threshold = threshold
        self._scores: dict[str, tuple[int, float]] = {}
        self._lock = Lock()

    def add(self, actor: str, points: int, now: float | None = None) -> int:
        current = monotonic() if now is None else now
        with self._lock:
            score, at = self._scores.get(actor, (0, current))
            elapsed = max(0.0, current - at)
            decayed = max(0, int(score * max(0.0, 1.0 - elapsed / self.decay_seconds)))
            score = max(0, decayed + points)
            self._scores[actor] = (score, current)
            return score

    def is_abusive(self, actor: str) -> bool:
        with self._lock:
            return self._scores.get(actor, (0, 0.0))[0] >= self.threshold

    def score(self, actor: str) -> int:
        with self._lock:
            return self._scores.get(actor, (0, 0.0))[0]
