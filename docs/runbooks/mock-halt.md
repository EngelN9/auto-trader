# Mock halt runbook

Milestone 0 has no external order path. To stop the development topology:

1. record the current branch and commit;
2. capture local service logs if needed;
3. run `docker compose down`;
4. do not treat local PostgreSQL state as an authoritative ledger;
5. do not restart under canary or live configuration.
