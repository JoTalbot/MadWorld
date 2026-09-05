from datetime import UTC, datetime, timezone
from uuid import uuid4

import pytest

from app.application.offline import OfflineCommand, OfflineCommandJournal
from app.application.reconnect import ReconnectService, ResumeCursor


def test_offline_journal_deduplicates_exact_retry() -> None:
    command_id = uuid4()
    command = OfflineCommand(command_id, "inventory.add", datetime.now(UTC), {"quantity": 2})
    journal = OfflineCommandJournal()
    assert journal.append(command) is True
    assert journal.append(command) is False
    assert journal.get(command_id) == command


def test_offline_journal_rejects_reused_command_id_with_different_payload() -> None:
    command_id = uuid4()
    created = datetime.now(UTC)
    journal = OfflineCommandJournal()
    journal.append(OfflineCommand(command_id, "inventory.add", created, {"quantity": 2}))
    with pytest.raises(ValueError, match="different operation"):
        journal.append(OfflineCommand(command_id, "inventory.remove", created, {"quantity": 2}))


def test_reconnect_reconciliation_separates_accepted_and_rejected_commands() -> None:
    session_id = uuid4()
    command_a, command_b = uuid4(), uuid4()
    event_id = uuid4()
    cursor = ResumeCursor(session_id, None, datetime.now(UTC))
    result = ReconnectService().reconcile(cursor, [command_a, command_b], [event_id], [command_a])
    assert result.accepted_command_ids == (command_a,)
    assert result.rejected_command_ids == (command_b,)
    assert result.authoritative_event_ids == (event_id,)
