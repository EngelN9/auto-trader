.DEFAULT_GOAL := test

.PHONY: setup format lint typecheck test test-property test-integration test-contract
.PHONY: test-e2e test-replay test-chaos dev-up dev-down api-dev dashboard-dev
.PHONY: backtest report paper shadow live-preflight reconcile cancel-all close-only halt

setup:
	uv sync --frozen --all-groups
	pnpm install --frozen-lockfile

format:
	uv run ruff format src tests scripts
	uv run ruff check --fix src tests scripts

lint:
	uv run ruff format --check src tests scripts
	uv run ruff check src tests scripts
	pnpm lint

typecheck:
	uv run mypy
	pnpm typecheck

test:
	uv run pytest
	pnpm test

test-property:
	uv run pytest -m property

test-integration:
	uv run pytest -m integration

test-contract:
	uv run pytest -m contract

test-e2e:
	uv run pytest -m e2e

test-replay:
	uv run pytest -m replay

test-chaos:
	uv run pytest -m chaos

dev-up:
	docker compose up --build

dev-down:
	docker compose down

api-dev:
	TRADING_CONFIG=configs/research.yaml MARKET_PROFILE=configs/markets/crypto_spot.yaml \
		uv run uvicorn trading_system.control.api:app --reload

dashboard-dev:
	pnpm --filter dashboard-web dev

backtest:
	@echo "Not implemented: deterministic backtesting begins in Milestone 2."
	@exit 1

report:
	@echo "Not implemented: run reporting begins in Milestone 2."
	@exit 1

paper:
	@echo "NOT READY: paper requires backtest and replay promotion evidence."
	@exit 1

shadow:
	@echo "Not implemented: shadow promotion requires completed paper evidence."
	@exit 1

live-preflight:
	@echo "NOT READY: canary/live preflight is intentionally unavailable in Milestone 0."
	@exit 1

reconcile:
	@echo "Not implemented: external reconciliation begins after a broker sandbox is selected."
	@exit 1

cancel-all:
	@echo "Not implemented: no external order adapter exists."
	@exit 1

close-only:
	@echo "Not implemented: no external position adapter exists."
	@exit 1

halt:
	@echo "Milestone 0 services are mock-only and cannot submit orders."
