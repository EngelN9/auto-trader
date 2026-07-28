import pytest

from trading_system.control.api import create_app


@pytest.mark.contract
def test_control_api_contract_has_queries_but_no_order_command() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]

    assert "/health" in paths
    assert "/api/v1/system/status" in paths
    assert "/orders" not in paths
    assert all("post" not in path_item for path_item in paths.values())
