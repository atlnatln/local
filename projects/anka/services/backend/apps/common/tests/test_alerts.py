"""
Tests for apps.common.alerts.emit_alarm.
"""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from apps.common.alerts import emit_alarm


def _captured_payload(mock_log: MagicMock) -> dict:
    """Extract the JSON payload string from the first mock_log call."""
    assert mock_log.called, "Logger.log() was not called"
    _level, json_str = mock_log.call_args[0]
    return json.loads(json_str)


@patch("apps.common.alerts.logger")
def test_emit_alarm_logs_json(mock_logger):
    """emit_alarm writes a structured JSON entry via the anka.alarms logger."""
    emit_alarm(
        code="TEST_ALARM",
        message="Test alarm message",
        metadata={"key": "value", "count": 42},
        level="ERROR",
    )

    mock_logger.log.assert_called_once()
    payload = _captured_payload(mock_logger.log)

    assert payload["alarm"] is True
    assert payload["code"] == "TEST_ALARM"
    assert payload["message"] == "Test alarm message"
    assert payload["metadata"]["count"] == 42
    assert payload["level"] == "ERROR"


@patch("apps.common.alerts.logger")
def test_emit_alarm_includes_exception_info(mock_logger):
    """emit_alarm captures exception type and value when exc is provided."""
    exc = ValueError("something went wrong")
    emit_alarm(
        code="EXC_ALARM",
        message="Exception alarm",
        exc=exc,
    )

    mock_logger.log.assert_called_once()
    payload = _captured_payload(mock_logger.log)

    assert payload["exception"]["type"] == "ValueError"
    assert "something went wrong" in payload["exception"]["value"]


@patch("apps.common.alerts.logger")
def test_emit_alarm_does_not_raise_on_broken_metadata(mock_logger):
    """emit_alarm must never raise even if metadata contains non-serializable objects."""

    class Unserializable:
        pass

    # Should NOT raise — json.dumps uses default=str for unknown types
    emit_alarm(
        code="SAFE_ALARM",
        message="Safe alarm",
        metadata={"obj": Unserializable()},
    )

    mock_logger.log.assert_called_once()
    payload = _captured_payload(mock_logger.log)
    # Unserializable object is repr'd via default=str
    assert isinstance(payload["metadata"]["obj"], str)


@patch("apps.common.alerts.logger")
def test_emit_alarm_honours_warning_level(mock_logger):
    """When level=WARNING, logger.log is called with logging.WARNING."""
    emit_alarm(
        code="WARN_ALARM",
        message="Warning level alarm",
        level="WARNING",
    )

    mock_logger.log.assert_called_once()
    level_arg, _json_str = mock_logger.log.call_args[0]
    assert level_arg == logging.WARNING


@patch("apps.common.alerts.logger")
def test_emit_alarm_swallows_internal_errors(mock_logger):
    """emit_alarm must not propagate internal failures to the caller."""
    mock_logger.log.side_effect = RuntimeError("logger broken")

    # Should not raise despite broken logger
    emit_alarm(code="RESILIENT", message="Will still not crash")
