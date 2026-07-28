# Risk policy

Status: `INTERFACE DEFAULTS ONLY / INDEPENDENT RISK ENGINE NOT IMPLEMENTED`

The configuration defaults to fail closed, zero gross exposure, zero net exposure, mock execution,
and no external orders. Canary and live startup are rejected.

These defaults are scaffolding and are not evidence that the pre-trade checks, drawdown controls,
kill switch, reconciliation, portfolio constraints, or emergency risk policy exist.
