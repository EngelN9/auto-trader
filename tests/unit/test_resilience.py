from datetime import UTC, datetime, timedelta

from trading_system.resilience import (
    MockCredentialSecurityPort,
    MockLeadershipPort,
    MockRestorePort,
    MockVenueControlPort,
    RecoveryMode,
    VenueHealthState,
)


def test_restore_never_automatically_resumes() -> None:
    result = MockRestorePort().restore("restore-001")

    assert result.recovery_mode is RecoveryMode.HALT
    assert result.externally_reconciled is False
    assert result.automatic_resume_allowed is False


def test_stale_fencing_token_loses_authority() -> None:
    now = datetime.now(UTC)
    leadership = MockLeadershipPort()
    stale = leadership.issue(now + timedelta(minutes=1))
    current = leadership.issue(now + timedelta(minutes=1))

    assert leadership.is_authoritative(stale, now_utc=now) is False
    assert leadership.is_authoritative(current, now_utc=now) is True


def test_expired_lease_cannot_increase_risk() -> None:
    now = datetime.now(UTC)
    leadership = MockLeadershipPort()
    expired = leadership.issue(now - timedelta(seconds=1))

    assert leadership.is_authoritative(expired, now_utc=now) is False


def test_credential_revocation_and_venue_block_are_explicit() -> None:
    credentials = MockCredentialSecurityPort()
    venues = MockVenueControlPort()

    assert venues.state("MOCK") is VenueHealthState.UNKNOWN
    credentials.revoke("fake-credential-id")
    venues.block("MOCK")

    assert credentials.is_revoked("fake-credential-id")
    assert venues.state("MOCK") is VenueHealthState.BLOCKED
