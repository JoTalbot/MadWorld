"""HTTP dependencies and infrastructure wiring."""

from __future__ import annotations
from collections.abc import Generator
from functools import lru_cache
from uuid import UUID
from fastapi import Header, HTTPException, Request
from app.application.ports import UnitOfWork
from app.infrastructure.db import create_engine_from_env
from app.infrastructure.postgres import PostgresUnitOfWork
from app.infrastructure.vehicle_components import ComponentVehicleRepository
from app.infrastructure.contracts import PostgresContractRepository
from app.infrastructure.settlements import PostgresSettlementRepository
from app.infrastructure.sessions import SessionStore
from app.api.session_routes import get_session_store, resolve_session

@lru_cache(maxsize=1)
def get_engine(): return create_engine_from_env()

def get_uow() -> Generator[UnitOfWork, None, None]:
    with PostgresUnitOfWork(get_engine()) as uow:
        uow.vehicles = ComponentVehicleRepository(uow.vehicles)
        uow.contracts = PostgresContractRepository(uow.conn)
        uow.settlements = PostgresSettlementRepository(uow.conn)
        yield uow

def get_authenticated_player(request: Request, authorization: str | None = Header(default=None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(status_code=401, detail="bearer session token is required")
    # Resolve the store lazily (after the header check) so unauthenticated requests never touch storage.
    store: SessionStore = request.app.dependency_overrides.get(get_session_store, get_session_store)()
    return resolve_session(authorization[7:].strip(), store)
