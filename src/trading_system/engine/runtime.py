"""Mock-only server-side runtime skeleton."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from trading_system.config import Settings, load_settings


def load_runtime_settings() -> Settings:
    environment_path = Path(os.getenv("TRADING_CONFIG", "configs/research.yaml"))
    market_path = Path(os.getenv("MARKET_PROFILE", "configs/markets/crypto_spot.yaml"))
    return load_settings(environment_path, market_path)


def heartbeat_payload(settings: Settings) -> dict[str, object]:
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "service": "trading-runtime",
        "environment": settings.system.mode.value,
        "execution_adapter": settings.execution.adapter,
        "external_orders_enabled": settings.execution.external_orders_enabled,
        "risk_state": "HALT",
    }


async def run_forever(settings: Settings, *, interval_seconds: float = 30.0) -> None:
    while True:
        print(json.dumps(heartbeat_payload(settings), sort_keys=True), flush=True)
        await asyncio.sleep(interval_seconds)


def main() -> None:
    settings = load_runtime_settings()
    asyncio.run(run_forever(settings))


if __name__ == "__main__":
    main()
