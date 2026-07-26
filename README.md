# Auto Trader

一個以「可驗證、可重現、可維護」為核心的事件驅動自動交易系統規劃。長期目標是建立 24 小時運行的伺服器端交易應用程式與獨立 Web 管理儀表板，依序支援研究、回測、重播、模擬交易、影子交易、canary 與經人工核准的 live 階段。

> [!WARNING]
> 本專案目前是 Milestone 0 的 mock-only 候選骨架，尚未通過人工驗收，也沒有可用於正式交易的系統。它不保證獲利，不構成投資建議，且不得用於正式下單。

## 核心原則

- 正確性、安全、法令遵循與風險限制優先於報酬。
- 不確定狀態一律 fail closed，不新增風險。
- 策略不能直接送單；所有訂單都必須通過獨立風險引擎。
- 金額、價格、數量與費用使用十進制定點表示。
- `live` 預設關閉，開發與 CI 不接觸正式交易憑證。
- 第一個端到端 MVP 僅聚焦高流動性加密貨幣現貨的 long／flat paper 路徑。
- 股票與跨資產功能必須等待前置驗收完成。

## 文件

- [`AGENTS.md`](AGENTS.md)：最高層級工程、安全、測試與營運規格。
- [`Trader prompts.md`](Trader%20prompts.md)：依 Milestone 拆分的 Codex 開發與驗收提示。
- [`docs/architecture.md`](docs/architecture.md)：目前的模組化單體與服務邊界。
- [`docs/dependencies.md`](docs/dependencies.md)：依賴用途、授權與供應鏈風險。
- [`SECURITY.md`](SECURITY.md)：安全漏洞通報與秘密洩漏處理原則。

## 建議執行順序

1. Repository assessment 與 Issue 拆分。
2. Milestone 0：專案骨架、設定、CI、mock services 與 dashboard placeholder。
3. Milestone 1–4：事件、資料品質、確定性回測、策略、投資組合與獨立風控。
4. Milestone 5–6：僅限 paper／shadow 的端到端流程與操作驗收。
5. 所有 promotion gate、災難復原與人工核准完成後，才評估 canary。

詳細要求與禁止事項以 [`AGENTS.md`](AGENTS.md) 為準。

## 目前狀態

`MILESTONE 0 CANDIDATE / MOCK ONLY / NOT TRADABLE`

- Milestone 0：候選實作，等待 CI 與人工驗收
- 最高允許環境：`research`
- 正式交易：停用
- 外部交易所／券商：未選定
- 正式 API key：不需要，也不得提交

## 本機開發

需求：

- Python 3.12–3.14
- `uv` 0.11.32 或相容版本
- Node.js 24
- pnpm 11.15
- Docker 與 Docker Compose

```bash
make setup
make lint
make typecheck
make test
make dev-up
```

若本機沒有 GNU Make，可直接執行等價命令：

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

啟動後：

- Dashboard：`http://localhost:3000`
- Control API health：`http://localhost:8000/health`
- Mock broker health：`http://localhost:8001/health`

所有畫面和服務均使用 mock data。PostgreSQL 也只是本機拓樸佔位，尚未成為權威交易帳本。

## 授權

目前採「未授予使用權」的保守狀態，詳見 [`LICENSE`](LICENSE)。公開可見不等於開源；若要改採 MIT、Apache-2.0 或其他授權，必須由專案擁有者另行確認。
