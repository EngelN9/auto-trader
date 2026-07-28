from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from trading_system.config import load_settings

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.property
@given(st.just("research.yaml"))
def test_permitted_bootstrap_mode_never_enables_external_orders(filename: str) -> None:
    settings = load_settings(
        ROOT / "configs" / filename,
        ROOT / "configs" / "markets" / "crypto_spot.yaml",
        base_path=ROOT / "configs" / "base.yaml",
    )

    assert settings.execution.external_orders_enabled is False
    assert settings.execution.withdrawals_enabled is False
    assert settings.execution.transfers_enabled is False
