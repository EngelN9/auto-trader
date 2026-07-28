from trading_system.resilience import MockCredentialSecurityPort


def test_mock_credential_revocation_is_idempotent() -> None:
    port = MockCredentialSecurityPort()

    port.revoke("fake-id")
    port.revoke("fake-id")

    assert port.revoked_credential_ids == {"fake-id"}
