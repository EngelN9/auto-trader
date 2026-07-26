# Dependency review

Status: Milestone 0 review. Versions are locked in `uv.lock` and `pnpm-lock.yaml`.

| Dependency group | Purpose | License | Runtime path | Main risk / alternative |
|---|---|---|---|---|
| FastAPI, Uvicorn, HTTPX | Control and mock HTTP boundaries | MIT / BSD-3-Clause | Python services | Framework and parser vulnerabilities; alternatives include Starlette or stdlib boundaries |
| Pydantic | Frozen configuration and API schemas | MIT | Python services | Validation behavior changes; alternative is dataclasses plus explicit validation |
| PyYAML | Versioned YAML configuration | MIT | Startup only | Unsafe loaders are prohibited; alternative is JSON or TOML |
| Hatchling, uv | Build and reproducible environment | MIT / MIT or Apache-2.0 | Build tooling | Compromised packages or installer; verify locks and releases |
| Ruff, mypy, pytest, Hypothesis, pre-commit | Format, lint, typing, tests | MIT / MPL-2.0 | Development and CI | CI supply chain; alternatives are standard-library checks and other maintained tools |
| pip-audit | Python advisory scan | Apache-2.0 | CI only | Advisory coverage and false negatives; alternative is OSV Scanner |
| Next.js, React | Responsive dashboard skeleton | MIT | Dashboard | Large dependency surface and frequent updates; alternative is a smaller static TypeScript client |
| TypeScript, ESLint, Vitest, type packages | Frontend typing, lint, tests | Apache-2.0 / MIT | Development and CI | Plugin supply chain; lockfile and review required |
| PostgreSQL image | Local topology placeholder | PostgreSQL License | Docker development | Mutable development tag; production must use an approved immutable digest |
| GitHub Actions listed in workflows | Checkout and tool setup | Mixed open-source | CI only | Actions must be pinned to full commit SHAs and granted minimal permissions |

Maintenance status is evaluated through lockfile review, advisory scanning, release activity, and
Dependabot or equivalent updates. None of these packages may be silently upgraded in a trading
release.

The initial locks exclude packages published after 2026-07-19, providing a seven-day observation
window at bootstrap time. Future dependency pull requests must advance this cutoff deliberately
after advisory and release review.
