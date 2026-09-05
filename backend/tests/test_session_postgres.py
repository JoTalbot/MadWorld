"""Session boundary against real PostgreSQL (integration). Guards the partial-index ON CONFLICT regression."""
import os
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.domain.primitives import utc_now
from app.infrastructure.db import create_engine_from_env
from app.infrastructure.sessions import PostgresSessionStore

pytestmark = pytest.mark.integration


@pytest.fixture
def engine():
    if not os.getenv("MADWORLD_DATABASE_URL"): pytest.skip("MADWORLD_DATABASE_URL is not configured")
    eng = create_engine_from_env(); yield eng; eng.dispose()


def test_postgres_session_create_resolve_revoke_and_idempotent_provisioning(engine) -> None:
    store = PostgresSessionStore(engine); handle = f"pg_{uuid4().hex[:12]}"; now = utc_now(); exp = now + timedelta(days=1)
    p1 = store.create(handle, "tok-1", now, exp); p2 = store.create(handle, "tok-2", now, exp)
    assert p1.player_id == p2.player_id
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM wallets WHERE owner_id = :p"), {"p": p1.player_id}).scalar() == 1
        assert conn.execute(text("SELECT COUNT(*) FROM inventories WHERE owner_id = :p AND name = 'personal'"), {"p": p1.player_id}).scalar() == 1
    assert store.resolve("tok-1", now) == p1.player_id and store.resolve("tok-1", exp + timedelta(seconds=1)) is None
    assert store.revoke("tok-1", now) and not store.revoke("tok-1", now) and store.resolve("tok-1", now) is None
    store.create(handle, "tok-3", now, exp)
    assert store.revoke_all(p1.player_id, now) == 2 and store.resolve("tok-2", now) is None and store.resolve("tok-3", now) is None


def test_postgres_caps_active_sessions(engine) -> None:
    store = PostgresSessionStore(engine, max_active=2); handle = f"cap_{uuid4().hex[:10]}"; now = utc_now(); exp = now + timedelta(days=1)
    for i in range(4): store.create(handle, f"c-{i}", now + timedelta(seconds=i), exp)
    assert [store.resolve(f"c-{i}", now + timedelta(seconds=10)) is not None for i in range(4)] == [False, False, True, True]
