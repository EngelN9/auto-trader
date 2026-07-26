import pytest

from trading_system.domain import compute_payload_checksum


@pytest.mark.replay
def test_same_bootstrap_event_payload_replays_identically() -> None:
    payload = {
        "environment": "research",
        "risk_state": "HALT",
        "external_orders_enabled": False,
    }

    assert compute_payload_checksum(payload) == compute_payload_checksum(payload)
