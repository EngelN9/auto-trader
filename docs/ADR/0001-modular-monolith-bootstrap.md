# ADR 0001: Modular monolith bootstrap

Status: Accepted for Milestone 0

## Decision

Use one typed Python package for domain and backend boundaries, one TypeScript dashboard workspace,
and separate process entry points sharing explicit contracts.

## Rationale

This keeps local behavior reviewable without adding premature network complexity. Docker Compose
demonstrates boundaries but is not a production deployment architecture.

## Consequences

Later extraction is possible, but durable event contracts and persistence must be introduced before
services can become independently authoritative.
