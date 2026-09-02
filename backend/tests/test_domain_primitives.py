from datetime import timedelta
from uuid import uuid4

import pytest

from app.domain.primitives import (
    InsufficientFunds,
    InvalidTransition,
    Job,
    JobState,
    Wallet,
    utc_now,
)


def test_wallet_rejects_overdraft() -> None:
    wallet = Wallet(uuid4(), balance=100)
    wallet.debit(60)
    assert wallet.balance == 40
    with pytest.raises(InsufficientFunds):
        wallet.debit(41)
    assert wallet.balance == 40


def test_wallet_credit_requires_positive_amount() -> None:
    wallet = Wallet(uuid4())
    with pytest.raises(ValueError):
        wallet.credit(0)


def test_job_progression_is_authoritative() -> None:
    now = utc_now()
    job = Job.create(uuid4(), "craft", now, now + timedelta(seconds=10))
    assert job.state is JobState.QUEUED
    job.start()
    with pytest.raises(InvalidTransition):
        job.complete(now)
    job.complete(now + timedelta(seconds=10))
    assert job.state is JobState.COMPLETED


def test_completed_job_cannot_be_cancelled() -> None:
    now = utc_now()
    job = Job.create(uuid4(), "repair", now, now + timedelta(seconds=1))
    job.complete(now + timedelta(seconds=1))
    with pytest.raises(InvalidTransition):
        job.cancel()
