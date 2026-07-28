from trading_system.resilience import MockRestorePort, RecoveryMode


def test_restore_contract_requires_external_reconciliation() -> None:
    result = MockRestorePort().restore("restore-drill-placeholder")

    assert result.recovery_mode is RecoveryMode.HALT
    assert not result.externally_reconciled
    assert not result.automatic_resume_allowed
