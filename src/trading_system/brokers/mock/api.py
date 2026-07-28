"""Mock broker health surface; intentionally exposes no order endpoints."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict


class MockBrokerHealth(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ok"]
    adapter: Literal["mock"]
    external_connectivity: Literal[False]
    order_submission_available: Literal[False]


def create_app() -> FastAPI:
    app = FastAPI(title="Auto Trader Mock Broker", version="0.1.0")

    @app.get("/health", response_model=MockBrokerHealth)
    async def health() -> MockBrokerHealth:
        return MockBrokerHealth(
            status="ok",
            adapter="mock",
            external_connectivity=False,
            order_submission_available=False,
        )

    return app


app = create_app()
