# Security Policy

## Supported versions

No release is production-ready or supported for live trading. The current repository is a
mock-only Milestone 0 candidate.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting or a private repository security advisory. Do not
open a public issue containing credentials, account identifiers, exploit details, or private data.

Include:

- affected commit and component;
- minimal reproduction without real secrets;
- expected and observed fail-closed behavior;
- potential impact;
- suggested mitigation, if known.

Do not test against real broker or exchange accounts. Do not request or share API keys.

## Secret exposure

If any credential appears in source, history, CI logs, artifacts, screenshots, or a dashboard
bundle:

1. treat it as compromised;
2. revoke it at the provider;
3. preserve evidence without copying the secret into more systems;
4. rotate through a clean channel;
5. inspect Git history and CI artifacts;
6. keep all trading modes halted until reconciliation and human review are complete.

Deleting the text from the latest commit is not sufficient revocation.
