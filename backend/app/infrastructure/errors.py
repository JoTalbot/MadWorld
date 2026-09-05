"""Safe translation of PostgreSQL integrity failures into application errors."""

from sqlalchemy.exc import IntegrityError

from app.application.errors import ConcurrencyConflict, IdempotencyConflict

IDEMPOTENCY_CONSTRAINTS = {
    "ledger_entries_idempotency_key_key",
    "jobs_idempotency_key_key",
    "idempotency_records_pkey",
}
CONCURRENCY_CONSTRAINTS = {
    "inventory_items_pkey",
    "jobs_pkey",
}


def map_integrity_error(exc: IntegrityError) -> RuntimeError:
    """Map only known constraints; preserve unknown failures for diagnostics."""
    original = getattr(exc, "orig", None)
    constraint = getattr(getattr(original, "diag", None), "constraint_name", None)
    if constraint in IDEMPOTENCY_CONSTRAINTS:
        return IdempotencyConflict("idempotency key already exists")
    if constraint in CONCURRENCY_CONSTRAINTS:
        return ConcurrencyConflict("persistent state changed concurrently")
    return RuntimeError("database integrity constraint failed")
