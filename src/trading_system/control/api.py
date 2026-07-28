"""Read-only Control API skeleton backed exclusively by mock state."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ok"]
    service: Literal["control-api"]
    environment: Literal["research"]
    trading_enabled: Literal[False]


class SystemStatusResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    environment: Literal["research"]
    market_data_source: Literal["mock"]
    execution_adapter: Literal["mock"]
    trading_enabled: Literal[False]
    live_enabled: Literal[False]
    risk_state: Literal["HALT"]
    message: str


def create_app() -> FastAPI:
    app = FastAPI(
        title="Auto Trader Control API",
        version="0.1.0",
        description="Milestone 0 mock-only, read-only control plane.",
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="control-api",
            environment="research",
            trading_enabled=False,
        )

    @app.get("/api/v1/system/status", response_model=SystemStatusResponse)
    async def system_status() -> SystemStatusResponse:
        return SystemStatusResponse(
            environment="research",
            market_data_source="mock",
            execution_adapter="mock",
            trading_enabled=False,
            live_enabled=False,
            risk_state="HALT",
            message="Milestone 0 skeleton: external trading is unavailable.",
        )

    return app


app = create_app()
