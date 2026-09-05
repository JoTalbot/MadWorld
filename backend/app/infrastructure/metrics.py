"""Minimal Prometheus text-format metrics without an external dependency.

Counters are process-local (each API replica exposes its own series; Prometheus
aggregates across instances via labels). Gauges that describe shared state
(world tick lag, abuse table sizes) are read from PostgreSQL at scrape time.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Callable, Iterable


class Counter:
    def __init__(self, name: str, help_text: str, labels: tuple[str, ...] = ()) -> None:
        self.name = name; self.help = help_text; self.labels = labels
        self._values: dict[tuple[str, ...], float] = defaultdict(float)
        self._lock = threading.Lock()

    def inc(self, *label_values: str, amount: float = 1.0) -> None:
        if len(label_values) != len(self.labels): raise ValueError(f"{self.name}: expected labels {self.labels}")
        with self._lock: self._values[tuple(label_values)] += amount

    def render(self) -> Iterable[str]:
        yield f"# HELP {self.name} {self.help}"
        yield f"# TYPE {self.name} counter"
        with self._lock: items = sorted(self._values.items())
        if not items and not self.labels: yield f"{self.name} 0"
        for values, count in items:
            labels = ",".join(f'{k}="{_escape(v)}"' for k, v in zip(self.labels, values, strict=True))
            yield f"{self.name}{{{labels}}} {_fmt(count)}" if labels else f"{self.name} {_fmt(count)}"


class Histogram:
    """Fixed-bucket latency histogram (seconds)."""
    def __init__(self, name: str, help_text: str, buckets: tuple[float, ...] = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)) -> None:
        self.name = name; self.help = help_text; self.buckets = buckets
        self._counts = [0] * len(buckets); self._sum = 0.0; self._total = 0
        self._lock = threading.Lock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._sum += value; self._total += 1
            for i, bound in enumerate(self.buckets):
                if value <= bound: self._counts[i] += 1

    def render(self) -> Iterable[str]:
        yield f"# HELP {self.name} {self.help}"
        yield f"# TYPE {self.name} histogram"
        with self._lock: counts, total, s = list(self._counts), self._total, self._sum
        for bound, count in zip(self.buckets, counts, strict=True): yield f'{self.name}_bucket{{le="{_fmt(bound)}"}} {count}'
        yield f'{self.name}_bucket{{le="+Inf"}} {total}'
        yield f"{self.name}_sum {_fmt(s)}"
        yield f"{self.name}_count {total}"


class Registry:
    def __init__(self) -> None:
        self._metrics: list[Counter | Histogram] = []
        self._gauge_sources: list[Callable[[], Iterable[str]]] = []

    def counter(self, name: str, help_text: str, labels: tuple[str, ...] = ()) -> Counter:
        c = Counter(name, help_text, labels); self._metrics.append(c); return c

    def histogram(self, name: str, help_text: str) -> Histogram:
        h = Histogram(name, help_text); self._metrics.append(h); return h

    def gauge_source(self, source: Callable[[], Iterable[str]]) -> None:
        """Register a callable that yields fully formatted gauge lines at scrape time."""
        self._gauge_sources.append(source)

    def render(self) -> str:
        lines: list[str] = []
        for metric in self._metrics: lines.extend(metric.render())
        for source in self._gauge_sources:
            try: lines.extend(source())
            except Exception as exc:  # noqa: BLE001 - a failing gauge must not break the scrape
                lines.append(f'# gauge source failed: {type(exc).__name__}')
        return "\n".join(lines) + "\n"


def gauge_line(name: str, value: float, **labels: str) -> str:
    label_text = ",".join(f'{k}="{_escape(v)}"' for k, v in sorted(labels.items()))
    return f"{name}{{{label_text}}} {_fmt(value)}" if label_text else f"{name} {_fmt(value)}"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _fmt(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else repr(float(value))


REGISTRY = Registry()
HTTP_REQUESTS = REGISTRY.counter("madworld_http_requests_total", "HTTP requests by method, route and status class", ("method", "route", "status"))
HTTP_LATENCY = REGISTRY.histogram("madworld_http_request_duration_seconds", "HTTP request latency in seconds")
ABUSE_EVENTS = REGISTRY.counter("madworld_abuse_events_total", "Abuse-control decisions", ("kind",))
