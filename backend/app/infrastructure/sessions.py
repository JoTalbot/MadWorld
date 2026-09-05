"""PostgreSQL-backed player session store.

Keeps token hashing and the ``players`` / ``player_sessions`` SQL out of the
API layer so the session routes can be exercised against an in-memory store.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Engine


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class SessionPlayer:
    player_id: UUID
    handle: str


class SessionStore(Protocol):
    def create(self, handle: str, token: str, now: datetime, expires_at: datetime) -> SessionPlayer: ...
    def resolve(self, token: str, now: datetime) -> UUID | None: ...
    def revoke(self, token: str, now: datetime) -> bool: ...
    def revoke_all(self, player_id: UUID, now: datetime) -> int: ...


class PostgresSessionStore:
    def __init__(self, engine: Engine) -> None: self.engine = engine

    def create(self, handle: str, token: str, now: datetime, expires_at: datetime) -> SessionPlayer:
        token_hash = hash_token(token)
        with self.engine.begin() as conn:
            row = conn.execute(text("SELECT id, handle FROM players WHERE handle = :handle"), {"handle": handle}).mappings().first()
            if row is None:
                row = conn.execute(text("INSERT INTO players (handle) VALUES (:handle) RETURNING id, handle"), {"handle": handle}).mappings().one()
            player_id = row["id"]
            # wallets.owner_id uniqueness is a partial index since migration 017 (corporate wallets have NULL owner),
            # so the conflict target must repeat the predicate.
            conn.execute(text("INSERT INTO wallets (owner_id) VALUES (:player_id) ON CONFLICT (owner_id) WHERE owner_id IS NOT NULL DO NOTHING"), {"player_id": player_id})
            # inventories has no unique (owner, name) key; make the personal inventory creation idempotent explicitly.
            conn.execute(text("""INSERT INTO inventories (owner_id, name) SELECT :player_id, 'personal'
                                 WHERE NOT EXISTS (SELECT 1 FROM inventories WHERE owner_id = :player_id AND name = 'personal')"""), {"player_id": player_id})
            conn.execute(
                text("""INSERT INTO player_sessions (player_id, token_hash, created_at, last_seen_at, expires_at)
                        VALUES (:player_id, :token_hash, :created_at, :last_seen_at, :expires_at)"""),
                {"player_id": player_id, "token_hash": token_hash, "created_at": now, "last_seen_at": now, "expires_at": expires_at},
            )
        return SessionPlayer(UUID(str(row["id"])), str(row["handle"]))

    def resolve(self, token: str, now: datetime) -> UUID | None:
        token_hash = hash_token(token)
        with self.engine.begin() as conn:
            row = conn.execute(
                text("""SELECT player_id FROM player_sessions
                        WHERE token_hash = :token_hash AND revoked_at IS NULL AND expires_at > :now"""),
                {"token_hash": token_hash, "now": now},
            ).mappings().first()
            if row is None: return None
            conn.execute(text("UPDATE player_sessions SET last_seen_at = :now WHERE token_hash = :token_hash"), {"now": now, "token_hash": token_hash})
            return UUID(str(row["player_id"]))

    def revoke(self, token: str, now: datetime) -> bool:
        with self.engine.begin() as conn:
            return conn.execute(text("UPDATE player_sessions SET revoked_at = :now WHERE token_hash = :token_hash AND revoked_at IS NULL"), {"now": now, "token_hash": hash_token(token)}).rowcount == 1

    def revoke_all(self, player_id: UUID, now: datetime) -> int:
        with self.engine.begin() as conn:
            return conn.execute(text("UPDATE player_sessions SET revoked_at = :now WHERE player_id = :player_id AND revoked_at IS NULL AND expires_at > :now"), {"now": now, "player_id": player_id}).rowcount


@dataclass
class InMemorySessionStore:
    """Deterministic session store for tests and local development."""
    players: dict[str, SessionPlayer] = field(default_factory=dict)  # handle -> player
    sessions: dict[str, dict] = field(default_factory=dict)  # token_hash -> session record

    def create(self, handle: str, token: str, now: datetime, expires_at: datetime) -> SessionPlayer:
        player = self.players.get(handle)
        if player is None: player = SessionPlayer(uuid4(), handle); self.players[handle] = player
        self.sessions[hash_token(token)] = {"player_id": player.player_id, "created_at": now, "last_seen_at": now, "expires_at": expires_at, "revoked_at": None}
        return player

    def resolve(self, token: str, now: datetime) -> UUID | None:
        record = self.sessions.get(hash_token(token))
        if record is None or record["revoked_at"] is not None or record["expires_at"] <= now: return None
        record["last_seen_at"] = now
        return record["player_id"]

    def revoke(self, token: str, now: datetime) -> bool:
        record = self.sessions.get(hash_token(token))
        if record is None or record["revoked_at"] is not None: return False
        record["revoked_at"] = now; return True

    def revoke_all(self, player_id: UUID, now: datetime) -> int:
        count = 0
        for record in self.sessions.values():
            if record["player_id"] == player_id and record["revoked_at"] is None and record["expires_at"] > now: record["revoked_at"] = now; count += 1
        return count
