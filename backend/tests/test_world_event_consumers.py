from uuid import uuid4

from app.application.world_event_consumers import consume_once


class _Result:
    def __init__(self, claimed):
        self._claimed = claimed

    def first(self):
        return (self._claimed,) if self._claimed else None


class _Conn:
    def __init__(self, claimed=True):
        self.claimed = claimed
        self.calls = 0

    def execute(self, statement, params):
        self.calls += 1
        return _Result(self.claimed)


def test_consume_once_applies_claimed_event_once():
    conn = _Conn(True)
    applied = []
    event_id = uuid4()

    assert consume_once(conn, "economy", event_id, {"tick": 7}, applied.append)
    assert applied == [{"tick": 7}]
    assert conn.calls == 1


def test_consume_once_skips_duplicate_delivery():
    conn = _Conn(False)
    applied = []

    assert not consume_once(conn, "territory", uuid4(), {"region": "dust_basin"}, applied.append)
    assert applied == []
