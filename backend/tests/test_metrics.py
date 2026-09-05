from fastapi.testclient import TestClient

from app.infrastructure.metrics import Counter, Histogram, Registry, gauge_line
from app.main import app


def test_counter_and_histogram_render_prometheus_text() -> None:
    reg = Registry(); c = reg.counter("t_total", "help", ("kind",)); h = reg.histogram("t_seconds", "lat")
    c.inc("a"); c.inc("a"); c.inc('b"q'); h.observe(0.02); h.observe(3)
    out = reg.render()
    assert '# TYPE t_total counter' in out and 't_total{kind="a"} 2' in out and 't_total{kind="b\\"q"} 1' in out
    assert 't_seconds_bucket{le="0.025"} 1' in out and 't_seconds_bucket{le="+Inf"} 2' in out and 't_seconds_count 2' in out


def test_failing_gauge_source_does_not_break_scrape() -> None:
    reg = Registry(); reg.counter("ok_total", "h")
    def boom(): raise RuntimeError("db down"); yield  # noqa: B901
    reg.gauge_source(boom)
    out = reg.render(); assert "ok_total 0" in out and "gauge source failed: RuntimeError" in out


def test_gauge_line_formats_labels_sorted() -> None:
    assert gauge_line("g", 1.5, b="2", a="1") == 'g{a="1",b="2"} 1.5' and gauge_line("g", 3) == "g 3"


def test_metrics_endpoint_counts_requests_by_route_template() -> None:
    from app.api.dependencies import get_uow
    from app.infrastructure.memory import InMemoryUnitOfWork
    uow = InMemoryUnitOfWork()
    def override_uow(): yield uow
    app.dependency_overrides[get_uow] = override_uow
    try:
        client = TestClient(app)
        client.get("/health"); client.get("/api/v1/players/00000000-0000-0000-0000-000000000000/state")  # 401: no bearer
        body = client.get("/metrics").text
    finally: app.dependency_overrides.clear()
    assert 'madworld_http_requests_total{method="GET",route="/health",status="2xx"}' in body
    assert 'route="/api/v1/players/{player_id}/state",status="4xx"' in body
    assert "madworld_http_request_duration_seconds_count" in body


def test_counter_label_arity_is_enforced() -> None:
    import pytest
    with pytest.raises(ValueError): Counter("x", "h", ("a",)).inc()
