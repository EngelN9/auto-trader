import asyncio

import pytest
from httpx import ASGITransport, AsyncClient, Response

from trading_system.control.api import create_app


async def get_status() -> Response:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/api/v1/system/status")


@pytest.mark.e2e
def test_mock_status_remains_not_tradable() -> None:
    response = asyncio.run(get_status())

    body = response.json()
    assert body["environment"] == "research"
    assert body["trading_enabled"] is False
    assert body["risk_state"] == "HALT"
