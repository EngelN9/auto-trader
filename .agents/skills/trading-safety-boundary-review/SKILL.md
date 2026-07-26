---
name: trading-safety-boundary-review
description: 當需要唯讀審查交易送單邊界、獨立風控、fail-closed、憑證隔離、Decimal、kill switch 或重複下單防護時使用；不要用於建立交易功能、連線正式環境、讀取秘密或核准 promotion。
---

# Trading Safety Boundary Review

對 Auto Trader 執行唯讀、證據導向的安全邊界稽核。任何可能造成真實資金、部位、帳戶或憑證風險的問題均列為最高嚴重性。

## 不可跨越的邊界

- 不修改 application code、設定或風險門檻。
- 不建立、呼叫或測試外部 broker／exchange 交易連線。
- 不讀取 OS、secret manager、CI secret 或本機 `.env` 中的秘密值。
- 不要求建立 API key；不測試提款、轉帳、子帳戶或正式帳戶權限。
- 不執行 canary／live preflight，不變更環境。
- 採 fail closed：不確定的外部狀態、工具或證據一律 `BLOCKED`。

## 1. 建立稽核範圍

完整閱讀根目錄 `AGENTS.md`，再讀：

- `README.md`、`Trader prompts.md`。
- `src/trading_system/`、`services/`、`apps/dashboard-web/`。
- `configs/`、`.env.example`、`.gitignore`、`.dockerignore`。
- `.github/workflows/`、`CODEOWNERS`、`SECURITY.md`。
- `docs/risk-policy.md`、`docs/execution-policy.md`、`docs/control-api.md`、`docs/security-incident-response.md`、`docs/disaster-recovery.md`。
- `tests/` 內與 config、control、execution、resilience、replay、chaos、credential 相關測試。

先執行：

```bash
git status --short --branch
git ls-files
git diff --check
```

檢查目前 diff 與完整追蹤檔，不能只看新增檔案。

## 2. 建立 trust-boundary map

畫出實際可達路徑：

```text
strategy／control command
  -> TargetPosition／OrderIntent
  -> independent RiskEngine
  -> approved RiskDecision
  -> execution state machine
  -> broker／exchange port
  -> adapter
```

對每一箭頭引用實際類別、函式、route、設定與測試。若某元件不存在，標記 `FAIL`；若只能看到 interface 或 mock，明確標為非操作證據。

使用 `rg` 查找高風險線索，並人工閱讀每個命中：

```bash
rg -n -i "submit_order|place_order|create_order|post.*/orders|broker|exchange|risk.?engine|risk.?decision" src services apps tests
rg -n -i "skip.?risk|force.?order|bypass|external_orders_enabled|live_enabled|startup_permitted" .
rg -n -i "withdraw|transfer|api.?key|secret|token|credential|allowlist" configs src services apps .github docs tests
rg -n -i "float|Decimal|round|quantize|tick.?size|lot.?size|minimum.?notional" src tests
```

只報告檔案與行號，不複製疑似秘密值。若掃描工具發現秘密，將值遮蔽並標記 `CRITICAL`。

## 3. 必查控制

逐項驗證：

1. 策略只能產生 `TargetPosition`／`OrderIntent`，不能 import 或呼叫 adapter。
2. 所有增加風險的訂單必須經獨立 `RiskEngine`，沒有 bypass flag 或 generic order route。
3. 缺 config、風控不可用、stale／out-of-order data、NaN／Inf、unknown order、資料庫失敗或 reconciliation mismatch 時不新增風險。
4. `live`、外部送單、withdrawal、transfer 預設關閉，且不只依賴 UI 或單一環境變數。
5. research、paper、shadow、canary、live 的帳號、憑證、資料庫、訊息通道與 UI 標示不可混用。
6. CI 權限最小化，不可接觸正式秘密；fork PR 不得取得秘密。
7. 若未來存在交易 key，權限設計必須禁止提款、轉帳、帳戶管理，並支援撤銷與輪替。不要讀取真實 key 驗證。
8. 金額、價格、數量與費用使用 `Decimal`／定點數；binary float 只能留在統計邊界，轉單前須正規化。
9. kill switch 獨立於策略與一般 dashboard，且有 `CANCEL_NEW_RISK`、`CANCEL_OPEN_ORDERS`、`CLOSE_ONLY`、`CONTROLLED_FLATTEN`、`FULL_HALT` 語意。
10. stale data、reconciliation failure、unknown venue／credential／leadership／recovery state 都有 fail-closed 測試。
11. `event_id`、`client_order_id`、command idempotency、重試查詢與 fencing 防止 duplicate order。
12. restart／failover 後先外部對帳，維持 halt／close-only，不自動恢復新增風險。

## 4. 驗證層級

對每個控制至少尋找：

- 靜態證據：imports、call graph、route、schema、config validator。
- 動態證據：具體 unit／property／integration／replay／chaos test。
- CI 證據：對應 job 確實執行該測試，而非只有工作名稱。
- 操作證據：kill-switch、restore、credential revoke、split-brain、reconciliation drill。

可執行 repository 已定義的安全檢查；工具缺失時標記 `BLOCKED`：

```bash
uv run pytest
uv run mypy
uv run python scripts/check_workflow_pins.py
pnpm test
docker compose config --quiet
```

不得用 mock health endpoint 證明 execution、risk、reconciliation 或 credential controls 已完成。

## 5. 嚴重度與狀態

嚴重度：

- `CRITICAL`：可達真實送單／提款／轉帳、風控繞過、正式秘密暴露、未知狀態仍增加風險、duplicate live order。
- `HIGH`：安全控制缺失可在後續非 mock 環境造成資金風險，例如無 kill switch、無 reconciliation gate、float monetary path。
- `MEDIUM`：降低可稽核性、隔離或偵測能力，但尚無直接風險路徑。
- `LOW`：防禦縱深、文件或維護性缺口。

控制狀態只使用：

- `PASS`：實作與對應測試均證明控制成立。
- `FAIL`：控制缺失、可被繞過或測試證明行為不符。
- `BLOCKED`：無法安全執行或缺少必要 evidence。
- `NOT APPLICABLE`：目前範圍確實不存在該能力；若它是 promotion prerequisite，不能標 N/A，應標 `FAIL` 或 `BLOCKED`。

## 6. 輸出格式

先輸出 findings，依 `CRITICAL`、`HIGH`、`MEDIUM`、`LOW` 排序。每項包含：

- severity 與 status；
- 檔案和行號；
- 被破壞的 invariant；
- 可觸發情境與最壞後果；
- 現有證據；
- 最小修正範圍；
- 必要 regression／property／chaos test。

再輸出：

| Control | Status | Static evidence | Test／CI evidence | Operational evidence | Gap |
|---|---|---|---|---|---|

最後列出：

- `Boundary verdict`: `PASS`、`FAIL` 或 `BLOCKED`。
- `Commands executed` 與退出碼。
- `Unverified external controls`。
- `Explicit non-actions`：未讀秘密、未連線、未送單、未 promotion。

任何 `CRITICAL`／`HIGH` 未解 finding 都必須阻止 promotion。
