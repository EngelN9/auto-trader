from datetime import UTC, datetime, timedelta

import pytest

from trading_system.resilience import MockLeadershipPort, MockRestorePort, RecoveryMode


@pytest.mark.chaos
def test_restore_plus_stale_leader_cannot_resume_risk() -> None:
    now = datetime.now(UTC)
    leadership = MockLeadershipPort()
    stale_lease = leadership.issue(now + timedelta(minutes=1))
    leadership.issue(now + timedelta(minutes=1))

    restore = MockRestorePort().restore("compound-restore")

    assert restore.recovery_mode is RecoveryMode.HALT
    assert restore.externally_reconciled is False
    assert leadership.is_authoritative(stale_lease, now_utc=now) is False
