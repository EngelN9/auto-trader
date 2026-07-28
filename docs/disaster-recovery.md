# Disaster recovery

Status: `NOT IMPLEMENTED`

Initial policy targets inherited from `AGENTS.md`:

| Item | Initial target | Evidence |
|---|---:|---|
| Critical trading events RPO | 0 seconds | None |
| Audit events RPO | 0 seconds | None |
| Establish safe known state RTO | 15 minutes | None |
| Control plane RTO | 30 minutes | None |
| Backup restore drill | Every 30 days | None |
| Regional failover drill | Every 90 days | None |
| Full trading resume | Manual approval only | None |

The mock restore port always returns `HALT`, unreconciled, and automatic-resume-disabled. It does
not back up PostgreSQL and is not restore evidence.

Required future work includes encrypted cross-fault-domain backups, PostgreSQL point-in-time
recovery, immutable retention, checksum validation, isolated restores, event-chain validation,
external reconciliation, RPO/RTO measurement, and documented owners.
