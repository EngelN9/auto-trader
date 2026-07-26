## Summary

Describe the purpose and scope.

## Risk impact

Explain whether data, strategy, risk, execution, persistence, control, credentials, or deployment
behavior changes.

## Validation

List commands and results.

## Rollback

Describe a safe rollback that preserves audit evidence.

## Checklist

- [ ] No secrets, account data, or large market data
- [ ] Format, lint, type checks, and relevant tests pass
- [ ] No look-ahead, survivorship bias, or unversioned configuration
- [ ] No risk bypass or silent risk-limit relaxation
- [ ] Strategy, risk, execution, API, and resilience documents updated where applicable
- [ ] Failure modes and fail-closed behavior tested
- [ ] Rollback plan included
- [ ] No claim of profitability or production readiness without evidence
