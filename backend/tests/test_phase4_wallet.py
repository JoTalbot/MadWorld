from uuid import uuid4
import pytest
from app.api.phase4_wallet_routes import WalletTransfer


def test_wallet_transfer_requires_exactly_one_recipient():
    with pytest.raises(Exception):
        WalletTransfer(corporation_id=uuid4(), amount=100, reason="test")


def test_wallet_transfer_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        WalletTransfer(corporation_id=uuid4(), recipient_player_id=uuid4(), amount=0, reason="test")
