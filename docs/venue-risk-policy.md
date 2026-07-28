# Venue and quote-asset risk policy

Status: `STATE CONTRACTS ONLY`

Venue states include `HEALTHY`, `DEGRADED`, `WITHDRAWALS_SUSPENDED`, `CUSTODY_AT_RISK`,
`INSOLVENCY_SUSPECTED`, `BLOCKED`, and `UNKNOWN`.

Milestone 0 defaults unknown venues to `HALT`. Withdrawal suspension must block additional venue
exposure. Custody risk, insolvency suspicion, blocked, or unknown state must not increase risk.

Quote-asset thresholds are versioned placeholders for research and paper tests only:

- watch: 50 bps;
- close-only: 150 bps;
- halt: 300 bps;
- at least two genuinely independent confirming sources.

No venue, quote asset, data provider, custody provider, or operational threshold has been approved.
