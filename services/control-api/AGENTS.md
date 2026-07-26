# Control API-specific agent rules

- Query and command routes must remain separated.
- The dashboard must never receive a generic broker-order endpoint.
- High-risk commands require backend RBAC, idempotency, reason, expected-state version,
  step-up authentication, and append-only audit events before they can be implemented.
- Milestone 0 is read-only and mock-only.
