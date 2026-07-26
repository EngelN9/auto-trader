# Architecture

Status: `MILESTONE 0 SKELETON / NOT TRADABLE`

```text
Mock broker health ───────────────┐
                                  │
Validated mock configuration ──> Trading runtime (HALT heartbeat)
                                  │
PostgreSQL development topology ──┤
                                  ↓
                           Control API (read-only)
                                  ↓
                         Dashboard (mock display)
```

The repository is a modular monolith with process boundaries that can later be separated. The
Python package owns configuration, domain contracts, resilience ports, runtime lifecycle, broker
ports, and the Control API. The dashboard is an independent TypeScript workspace.

## Trust boundaries

- The dashboard is never an execution authority or ledger.
- The Control API has no arbitrary order route.
- The mock broker has no external connectivity or order route.
- The runtime validates configuration before starting.
- Canary and live configurations are deliberately rejected.
- Restore, leadership, credential, and venue components are mock contracts, not operational
  evidence.

## Deferred

Durable events, PostgreSQL ledger, event bus, market data, strategies, independent risk engine,
execution state machine, reconciliation, authentication, RBAC, metrics, alerts, backups, and
deployment are not implemented.
