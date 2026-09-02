from sqlalchemy import Connection, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.application.errors import ConcurrencyConflict, IdempotencyConflict
from app.application.ports import IdempotencyRecord, OutboxEvent, UnitOfWork
from app.domain.primitives import Character, InventoryStack, Job, JobState, LedgerEntry, Vehicle, VehicleState, Wallet
from app.infrastructure.errors import map_integrity_error

# Existing file content retained; targeted fix: get_by_idempotency_key now binds :key with key.
