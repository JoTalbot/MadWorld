from uuid import uuid4
import pytest
from fastapi import HTTPException
from app.api.phase4_wallet_routes import WalletTransfer, _validate_recipient


def test_wallet_transfer_requires_exactly_one_recipient():
    payload = WalletTransfer(corporation_id=uuid4(), amount=100, reason="test")
    with pytest.raises(HTTPException) as exc:
        _validate_recipient(payload)
    assert exc.value.status_code == 400


def test_wallet_transfer_rejects_two_recipients():
    payload = WalletTransfer(corporation_id=uuid4(), recipient_player_id=uuid4(), recipient_corporation_id=uuid4(), amount=100, reason="test")
    with pytest.raises(HTTPException) as exc:
        _validate_recipient(payload)
    assert exc.value.status_code == 400


def test_wallet_transfer_requires_positive_amount():
    with pytest.raises(ValueError):
        WalletTransfer(corporation_id=uuid4(), recipient_player_id=uuid4(), amount=0, reason="test")
