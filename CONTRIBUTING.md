# Contributing

Read `AGENTS.md` before making changes.

## Workflow

1. Start from the latest `main`.
2. Create a focused branch named `agent/<description>` or `contributor/<description>`.
3. Keep one independently reviewable concern per pull request.
4. Update tests and governing documents with the implementation.
5. Run the relevant checks locally.
6. Open a pull request; do not push implementation changes directly to `main`.

## Safety

- Never commit credentials, account exports, private keys, or large market datasets.
- Never add a risk bypass or generic dashboard order endpoint.
- Never weaken limits or tests to make a check pass.
- Never connect a real account in tests or CI.
- Treat unknown configuration, data, order, persistence, leadership, or credential state as halt or
  close-only.
- Do not claim profitability, production readiness, or live safety without the required evidence.

## Current validation

```bash
uv sync --frozen --all-groups
uv run ruff format --check src tests scripts
uv run ruff check src tests scripts
uv run mypy
uv run pytest
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
docker compose config
```
