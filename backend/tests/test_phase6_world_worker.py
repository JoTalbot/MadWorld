from __future__ import annotations

from app.scripts.world_tick_worker import LOCK_KEY, tick_once


class _Result:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class _Connection:
    def __init__(self, locked: bool):
        self.locked = locked

    def execute(self, statement, params):
        return _Result(self.locked)


class _Context:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, *args):
        return False


class _Engine:
    def __init__(self, connection):
        self.connection = connection

    def begin(self):
        return _Context(self.connection)


def test_worker_skips_when_advisory_lock_is_owned(monkeypatch):
    import app.scripts.world_tick_worker as worker

    called = False

    def fake_simulate(conn):
        nonlocal called
        called = True
        return {"tick": 1}

    monkeypatch.setattr(worker, "simulate_tick", fake_simulate)
    assert tick_once(_Engine(_Connection(False))) is None
    assert called is False


def test_worker_advances_only_after_advisory_lock(monkeypatch):
    import app.scripts.world_tick_worker as worker

    seen = {}

    def fake_simulate(conn):
        seen["conn"] = conn
        return {"tick": 7, "generated_events": 1, "generated_missions": 0}

    monkeypatch.setattr(worker, "simulate_tick", fake_simulate)
    result = tick_once(_Engine(_Connection(True)))
    assert result["tick"] == 7
    assert seen["conn"] is not None
    assert LOCK_KEY == 6_2026_01
