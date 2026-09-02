"""Small, dependency-free primitives used by authoritative domain services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class DomainError(ValueError):
    """Base error for rejected domain commands."""


class InsufficientFunds(DomainError):
    pass


class InvalidQuantity(DomainError):
    pass


class InvalidTransition(DomainError):
    pass


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VehicleState(StrEnum):
    ACTIVE = "active"
    DESTROYED = "destroyed"
    STORED = "stored"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    id: UUID
    wallet_id: UUID
    amount: int
    reason: str
    idempotency_key: str
    created_at: datetime


@dataclass(slots=True)
class Wallet:
    id: UUID
    balance: int = 0
    version: int = 0

    def credit(self, amount: int) -> None:
        if amount <= 0:
            raise InvalidQuantity("credit amount must be positive")
        self.balance += amount

    def debit(self, amount: int) -> None:
        if amount <= 0:
            raise InvalidQuantity("debit amount must be positive")
        if self.balance < amount:
            raise InsufficientFunds("wallet balance is insufficient")
        self.balance -= amount


@dataclass(slots=True)
class InventoryStack:
    item_definition_id: UUID
    quantity: int
    condition: int = 100
    version: int = 0

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidQuantity("inventory quantity must be positive")
        if not 0 <= self.condition <= 100:
            raise InvalidQuantity("condition must be between 0 and 100")


@dataclass(slots=True)
class Job:
    id: UUID
    owner_id: UUID
    job_type: str
    started_at: datetime
    completes_at: datetime
    state: JobState = JobState.QUEUED
    version: int = 0

    @classmethod
    def create(cls, owner_id: UUID, job_type: str, started_at: datetime, completes_at: datetime) -> "Job":
        if completes_at <= started_at:
            raise InvalidTransition("job completion must be after start")
        return cls(uuid4(), owner_id, job_type, started_at, completes_at)

    def start(self) -> None:
        if self.state is not JobState.QUEUED:
            raise InvalidTransition("only queued jobs can start")
        self.state = JobState.RUNNING

    def complete(self, now: datetime) -> None:
        if self.state not in (JobState.QUEUED, JobState.RUNNING):
            raise InvalidTransition("only active jobs can complete")
        if now < self.completes_at:
            raise InvalidTransition("job completion time has not been reached")
        self.state = JobState.COMPLETED

    def cancel(self) -> None:
        if self.state in (JobState.COMPLETED, JobState.CANCELLED):
            raise InvalidTransition("terminal job cannot be cancelled")
        self.state = JobState.CANCELLED


@dataclass(slots=True)
class Character:
    id: UUID
    player_id: UUID
    name: str
    level: int = 1
    version: int = 0

    @classmethod
    def create(cls, player_id: UUID, name: str) -> "Character":
        if not name.strip():
            raise ValueError("character name must not be blank")
        return cls(uuid4(), player_id, name.strip())


@dataclass(slots=True)
class Vehicle:
    id: UUID
    owner_id: UUID
    code: str
    chassis_code: str
    durability: int = 100
    fuel: int = 0
    state: VehicleState = VehicleState.ACTIVE
    version: int = 0

    @classmethod
    def create(cls, owner_id: UUID, code: str, chassis_code: str, fuel: int = 0) -> "Vehicle":
        if not code.strip() or not chassis_code.strip():
            raise ValueError("vehicle code and chassis code must not be blank")
        if fuel < 0:
            raise InvalidQuantity("vehicle fuel must not be negative")
        return cls(uuid4(), owner_id, code.strip(), chassis_code.strip(), 100, fuel)

    def repair(self, amount: int) -> None:
        if amount <= 0:
            raise InvalidQuantity("repair amount must be positive")
        if self.state is VehicleState.DESTROYED:
            raise InvalidTransition("destroyed vehicle must be recovered before repair")
        self.durability = min(100, self.durability + amount)

    def refuel(self, amount: int) -> None:
        if amount <= 0:
            raise InvalidQuantity("refuel amount must be positive")
        self.fuel += amount
