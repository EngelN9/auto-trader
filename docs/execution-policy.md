# Execution policy

Status: `NO EXECUTION ENGINE`

The mock broker exposes health only. There is no submit, replace, cancel, market-order, transfer, or
withdrawal path. The runtime cannot connect to an external venue.

Before any sandbox execution is added, an RFC must specify the order state machine, idempotency,
timeout semantics, unknown-order handling, normalization, fencing, reconciliation, and rollback.
