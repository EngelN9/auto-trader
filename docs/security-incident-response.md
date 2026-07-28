# Security incident response

Status: `MOCK CONTRACT ONLY`

Credential creation, permission elevation, IP allowlist changes, unknown login sources, abnormal
orders, CI runner compromise, dependency tampering, and image digest mismatch must be treated as
security events.

Minimum response:

1. halt affected execution;
2. cancel only when external order state is known;
3. revoke sessions and credentials;
4. block the affected identity or deployment source;
5. rotate through a clean channel;
6. reconcile account state;
7. preserve evidence;
8. return through paper/shadow with human approval.

The mock credential port records fake identifier revocation only. No provider revocation or
detection integration exists.
