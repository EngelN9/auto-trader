# Dashboard specification

Milestone 0 displays deterministic mock data and a persistent `RESEARCH · HALT · NOT TRADABLE`
environment banner.

It must not:

- contain broker or exchange credentials;
- calculate or override backend risk;
- expose a generic order-submission control;
- cache sensitive account, position, or risk responses;
- become necessary for runtime safety.

Positions, orders, fills, audit, authentication, step-up controls, SSE/WebSocket recovery, and
responsive emergency workflows are deferred and must not be inferred from the placeholder.
