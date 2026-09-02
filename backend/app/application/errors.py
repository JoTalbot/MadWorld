"""Application-level errors for persistence boundaries."""


class ApplicationError(RuntimeError):
    """Base error raised by application services."""


class NotFound(ApplicationError):
    """Requested aggregate does not exist."""


class ConcurrencyConflict(ApplicationError):
    """Aggregate changed since the caller read its expected version."""


class IdempotencyConflict(ApplicationError):
    """An idempotency key was reused for a different operation."""
