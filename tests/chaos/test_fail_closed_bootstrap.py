from pathlib import Path

import pytest

from trading_system.config import UnsafeStartupError, load_settings

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.chaos
def test_missing_configuration_fails_closed() -> None:
    with pytest.raises(UnsafeStartupError, match="unable to read configuration"):
        load_settings(
            ROOT / "configs" / "does-not-exist.yaml",
            ROOT / "configs" / "markets" / "crypto_spot.yaml",
            base_path=ROOT / "configs" / "base.yaml",
        )
