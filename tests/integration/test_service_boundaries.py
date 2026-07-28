from pathlib import Path

import pytest

from trading_system.config import load_settings
from trading_system.engine.runtime import heartbeat_payload

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_runtime_uses_validated_mock_configuration() -> None:
    settings = load_settings(
        ROOT / "configs" / "research.yaml",
        ROOT / "configs" / "markets" / "crypto_spot.yaml",
        base_path=ROOT / "configs" / "base.yaml",
    )
    heartbeat = heartbeat_payload(settings)

    assert heartbeat["environment"] == "research"
    assert heartbeat["execution_adapter"] == "mock"
    assert heartbeat["external_orders_enabled"] is False
    assert heartbeat["risk_state"] == "HALT"
