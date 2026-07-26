import asyncio

from httpx import ASGITransport, AsyncClient, Response

from trading_system.brokers.mock.api import create_app as create_mock_broker
from trading_system.control.api import create_app as create_control_api


async def get(app: object, path: str) -> Response:
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


def test_control_api_reports_mock_halted_state() -> None:
    response = asyncio.run(get(create_control_api(), "/api/v1/system/status"))

    assert response.status_code == 200
    assert response.json() == {
        "environment": "research",
        "market_data_source": "mock",
        "execution_adapter": "mock",
        "trading_enabled": False,
        "live_enabled": False,
        "risk_state": "HALT",
        "message": "Milestone 0 skeleton: external trading is unavailable.",
    }


def test_mock_broker_exposes_no_order_submission_route() -> None:
    app = create_mock_broker()
    paths = {getattr(route, "path", None) for route in app.routes}

    assert "/health" in paths
    assert "/orders" not in paths
