from pathlib import Path

import pytest
from pydantic import ValidationError

from trading_system.config import EnvironmentMode, UnsafeStartupError, load_settings

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "configs" / "base.yaml"
CRYPTO = ROOT / "configs" / "markets" / "crypto_spot.yaml"


def test_research_configuration_is_mock_only_and_frozen() -> None:
    settings = load_settings(ROOT / "configs" / "research.yaml", CRYPTO, base_path=BASE)

    assert settings.system.mode is EnvironmentMode.RESEARCH
    assert settings.execution.adapter == "mock"
    assert settings.execution.external_orders_enabled is False
    assert settings.credential_security.real_credentials_allowed is False
    assert settings.disaster_recovery.auto_resume_after_restore is False
    with pytest.raises(ValidationError):
        settings.system.mode = EnvironmentMode.LIVE  # type: ignore[misc]


@pytest.mark.parametrize("filename", ["paper.yaml", "shadow.yaml", "canary.yaml", "live.yaml"])
def test_unpromoted_configuration_fails_closed(filename: str) -> None:
    with pytest.raises(UnsafeStartupError, match="startup remains halted"):
        load_settings(ROOT / "configs" / filename, CRYPTO, base_path=BASE)


def test_equities_profile_remains_disabled() -> None:
    settings = load_settings(
        ROOT / "configs" / "research.yaml",
        ROOT / "configs" / "markets" / "equities_cash.yaml",
        base_path=BASE,
    )

    assert settings.market.asset_class == "equity"
    assert settings.market.enabled is False
    assert settings.market.short_allowed is False
