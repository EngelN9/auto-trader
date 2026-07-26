"""Mock-only ports that make safe recovery expectations explicit."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class RecoveryMode(StrEnum):
    HALT = "halt"
    CLOSE_ONLY = "close-only"


class VenueHealthState(StrEnum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    WITHDRAWALS_SUSPENDED = "WITHDRAWALS_SUSPENDED"
    CUSTODY_AT_RISK = "CUSTODY_AT_RISK"
    INSOLVENCY_SUSPECTED = "INSOLVENCY_SUSPECTED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class BackupEvidence:
    backup_id: str
    completed_at_utc: datetime
    checksum: str
    mock_only: bool = True


@dataclass(frozen=True)
class RestoreResult:
    restore_id: str
    recovery_mode: RecoveryMode
    externally_reconciled: bool
    automatic_resume_allowed: bool = False


@dataclass(frozen=True)
class LeadershipLease:
    fencing_token: int
    expires_at_utc: datetime

    def __post_init__(self) -> None:
        if self.fencing_token <= 0:
            raise ValueError("fencing_token must be positive")
        if self.expires_at_utc.tzinfo is None or self.expires_at_utc.utcoffset() != UTC.utcoffset(
            self.expires_at_utc
        ):
            raise ValueError("lease expiry must be timezone-aware UTC")

    def permits_risk_increase(self, *, now_utc: datetime, latest_token: int) -> bool:
        return (
            self.fencing_token == latest_token
            and now_utc.tzinfo is not None
            and now_utc.utcoffset() == UTC.utcoffset(now_utc)
            and now_utc <= self.expires_at_utc
        )


@dataclass
class MockBackupPort:
    """Creates evidence only; it does not back up a real database."""

    def create(self, backup_id: str) -> BackupEvidence:
        return BackupEvidence(
            backup_id=backup_id,
            completed_at_utc=datetime.now(UTC),
            checksum="mock-checksum-not-production-evidence",
        )


@dataclass
class MockRestorePort:
    """Every mock restore terminates halted and unreconciled."""

    def restore(self, restore_id: str) -> RestoreResult:
        return RestoreResult(
            restore_id=restore_id,
            recovery_mode=RecoveryMode.HALT,
            externally_reconciled=False,
        )


@dataclass
class MockLeadershipPort:
    latest_fencing_token: int = 0

    def issue(self, expires_at_utc: datetime) -> LeadershipLease:
        self.latest_fencing_token += 1
        return LeadershipLease(
            fencing_token=self.latest_fencing_token,
            expires_at_utc=expires_at_utc,
        )

    def is_authoritative(self, lease: LeadershipLease, *, now_utc: datetime) -> bool:
        return lease.permits_risk_increase(
            now_utc=now_utc,
            latest_token=self.latest_fencing_token,
        )


@dataclass
class MockCredentialSecurityPort:
    revoked_credential_ids: set[str] = field(default_factory=set)

    def revoke(self, credential_id: str) -> None:
        self.revoked_credential_ids.add(credential_id)

    def is_revoked(self, credential_id: str) -> bool:
        return credential_id in self.revoked_credential_ids


@dataclass
class MockVenueControlPort:
    states: dict[str, VenueHealthState] = field(default_factory=dict)

    def block(self, venue: str) -> None:
        self.states[venue] = VenueHealthState.BLOCKED

    def state(self, venue: str) -> VenueHealthState:
        return self.states.get(venue, VenueHealthState.UNKNOWN)
