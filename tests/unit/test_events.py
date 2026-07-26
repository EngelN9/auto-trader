from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from trading_system.config import EnvironmentMode
from trading_system.domain import Heartbeat, compute_payload_checksum

EVENT_ID = UUID("00000000-0000-0000-0000-000000000001")
CORRELATION_ID = UUID("00000000-0000-0000-0000-000000000002")
CAUSATION_ID = UUID("00000000-0000-0000-0000-000000000003")


def heartbeat(timestamp: datetime) -> Heartbeat:
    payload = {"service": "runtime", "status": "HALT", "mode": "paper"}
    return Heartbeat(
        event_id=EVENT_ID,
        schema_version="1.0.0",
        source="trading-runtime",
        venue="INTERNAL",
        symbol="SYSTEM",
        correlation_id=CORRELATION_ID,
        causation_id=CAUSATION_ID,
        event_time_utc=timestamp,
        ingest_time_utc=timestamp,
        sequence_number=1,
        payload_checksum=compute_payload_checksum(payload),
        service="runtime",
        status="HALT",
        mode=EnvironmentMode.PAPER,
    )


def test_heartbeat_is_immutable_and_utc() -> None:
    event = heartbeat(datetime(2026, 1, 1, tzinfo=UTC))

    assert event.mode is EnvironmentMode.PAPER
    with pytest.raises(ValidationError):
        event.status = "RUNNING"  # type: ignore[misc]


def test_naive_timestamp_is_rejected() -> None:
    naive_timestamp = datetime(2026, 1, 1, tzinfo=UTC).replace(tzinfo=None)
    with pytest.raises(ValidationError, match="timezone-aware UTC"):
        heartbeat(naive_timestamp)


def test_payload_checksum_is_deterministic() -> None:
    left = compute_payload_checksum({"b": 2, "a": 1})
    right = compute_payload_checksum({"a": 1, "b": 2})

    assert left == right
    assert len(left) == 64
