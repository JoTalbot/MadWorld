from uuid import uuid4

import pytest

from app.application.observability import MetricsRecorder, StructuredLogger, timed_command


def test_structured_logger_keeps_request_context_without_game_state_leakage() -> None:
    request_id = uuid4()
    logger = StructuredLogger()
    logger.emit("INFO", "command.accepted", request_id=request_id, command="inventory.add")
    record = logger.records[0]
    assert record["request_id"] == str(request_id)
    assert record["command"] == "inventory.add"
    assert "payload" not in record


def test_timed_command_records_success_and_failure() -> None:
    metrics = MetricsRecorder()

    @timed_command(metrics, "test.success")
    def success() -> int:
        return 1

    @timed_command(metrics, "test.failure")
    def failure() -> None:
        raise RuntimeError("boom")

    assert success() == 1
    with pytest.raises(RuntimeError):
        failure()
    assert [m.success for m in metrics.command_metrics] == [True, False]
    assert all(m.duration_ms >= 0 for m in metrics.command_metrics)
