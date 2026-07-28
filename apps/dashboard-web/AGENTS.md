# Dashboard-specific agent rules

- The dashboard is a control-plane client, never a trading runtime.
- It must not store broker or exchange credentials.
- It must not calculate, bypass, or overwrite backend risk decisions.
- It must not expose a generic order-submission interface.
- Mock, paper, shadow, canary, and live environments must remain visually distinct.
- Milestone 0 must display mock data only and remain visibly marked `NOT TRADABLE`.
- Sensitive API responses must not be cached in the browser.
- All TypeScript must pass strict type checking.
