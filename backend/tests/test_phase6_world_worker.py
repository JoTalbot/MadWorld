from __future__ import annotations

import importlib.util
from pathlib import Path

_WORKER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "world_tick_worker.py"
_SPEC = importlib.util.spec_from_file_location("world_tick_worker", _WORKER_PATH)
assert _SPEC and _SPEC.loader
worker = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(worker)


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
    called = False

    def fake_simulate(conn):
        nonlocal called
        called = True
        return {"tick": 1}

    monkeypatch.setattr(worker, "simulate_tick", fake_simulate)
    assert worker.tick_once(_Engine(_Connection(False))) is None
    assert called is False


def test_worker_advances_only_after_advisory_lock(monkeypatch):
    seen = {}

    def fake_simulate(conn):
        seen["conn"] = conn
        return {"tick": 7, "generated_events": 1, "generated_missions": 0}

    monkeypatch.setattr(worker, "simulate_tick", fake_simulate)
    result = worker.tick_once(_Engine(_Connection(True)))
    assert result["tick"] == 7
    assert seen["conn"] is not None
    assert worker.LOCK_KEY == 6_2026_01
