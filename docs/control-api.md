# Control API

Current read-only routes:

- `GET /health`
- `GET /api/v1/system/status`

The API reports research, mock, external-trading-disabled, and halted state. It does not expose command,
authentication, account, position, order, fill, or reconciliation endpoints.

Future command endpoints require versioned commands, RBAC, step-up authentication, reason fields,
idempotency keys, expected-state versions, CSRF/origin protection, and append-only audit events.
