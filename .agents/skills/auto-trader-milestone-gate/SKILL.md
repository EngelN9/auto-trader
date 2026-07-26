---
name: auto-trader-milestone-gate
description: 當需要判定 Auto Trader 目前里程碑、驗收前置條件、最高允許環境或 promotion readiness 時使用；不要用於實作新功能、啟用 paper／shadow／canary／live，或把規格文件當成完成證據。
---

# Auto Trader Milestone Gate

以唯讀方式依 `AGENTS.md` 與 `Trader prompts.md` 驗收 repository 的實際狀態。正確性、安全、法令遵循與風險限制永遠優先於報酬或進度。

## 安全邊界

- 不修改程式碼、設定、門檻、fixture、歷史資料或 CI。
- 不建立交易所／券商連線，不要求或讀取正式憑證。
- 不變更 `system.mode`，不執行 promotion，不核准資本增加。
- 不把 mock、interface、placeholder、計畫、政策文件或綠色 CI 單獨視為功能完成。
- 任何無法重現、缺少權限、工具、資料、artifact 或操作紀錄的必要檢查標記 `BLOCKED`。
- 不確定時採 fail closed；不得把「沒有看到失敗」寫成 `PASS`。

## 1. 建立 repository truth snapshot

先完整閱讀：

1. 根目錄 `AGENTS.md`。
2. `README.md` 與 `Trader prompts.md`。
3. 目標路徑向上適用的所有子目錄 `AGENTS.md`。
4. `src/`、`services/`、`apps/`、`configs/`、`tests/`、`.github/workflows/`、`docs/`、`infra/`、`data/`、`Makefile`、鎖檔與目前 diff。

執行唯讀盤點：

```bash
git status --short --branch
git ls-files
git log -5 --oneline --decorate
git diff --stat
git diff --check
```

若正在審查 branch，另執行：

```bash
git diff --merge-base main HEAD --stat
git diff --merge-base main HEAD
```

若 `main` 不存在、基準不明或遠端證據不可取得，標記相應檢查 `BLOCKED`，不要猜測。

## 2. 判定候選里程碑

逐項對照 `AGENTS.md` 的 Milestone 0–8 與 `Trader prompts.md` 的 Prompt 11、17、18：

1. 找出最高「所有必要項目皆有實作與驗證證據」的里程碑。
2. 若 Milestone 0 仍有任一必要項目失敗或缺少證據，將目前狀態寫成 `PRE-MILESTONE 0` 或 `MILESTONE 0 CANDIDATE`，不得寫成 Milestone 0 completed。
3. 下一個部分完成的里程碑只能稱為 candidate／partial，不得提升「最高已完成里程碑」。
4. 檢查前一里程碑及全部 promotion gate；禁止跳級。
5. 分別判定 crypto Phase A、equity Phase B 與跨資產範圍，不得以共用介面代替市場專屬驗證。

目前 repository 的標籤可能包含 `MILESTONE 0 CANDIDATE / MOCK ONLY / NOT TRADABLE`。這只是待驗證聲明，每次執行都必須重新以實際檔案、測試、CI 與人工／操作證據判定。

## 3. 建立證據鏈

每個 acceptance criterion 至少尋找四類證據：

| 證據類型 | 可接受範例 | 不足以單獨通過 |
|---|---|---|
| 實作 | 可追蹤的 source、schema、設定與安全邊界 | README、註解、空目錄 |
| 自動測試 | 對應 failure mode 的 unit／property／integration／contract／replay／chaos test | 只測 happy path、只檢查字串存在 |
| 執行結果 | 本次可重現命令、退出碼、測試摘要、artifact hash | 過期截圖、未提供輸出的口頭聲明 |
| 操作證據 | 對帳、restore、incident、on-call、kill-switch drill 與人工核准紀錄 | mock port、政策骨架、尚未執行的 runbook |

不要為了完成驗收而安裝未核准依賴。優先使用 repository 已定義的命令：

```bash
uv run ruff format --check src tests scripts
uv run ruff check src tests scripts
uv run mypy
uv run pytest
pnpm lint
pnpm typecheck
pnpm test
pnpm build
docker compose config --quiet
```

先確認工具與鎖定依賴可用。命令不存在、環境不相容或無法安全執行時，記錄命令、原因與 `BLOCKED`；不得改用未鎖定環境後宣稱等價通過。

## 4. 驗收控制面

至少檢查：

- 專案骨架、typed config、immutable events、mock-only 邊界與 CI。
- market-data lineage、quality gate、symbol metadata 與市場專屬 profile。
- deterministic backtest、run manifest、保守成交與 accounting。
- strategy specs、walk-forward、holdout、成本與極端壓力證據。
- 獨立 RiskEngine、風控 invariants、kill switch 與 emergency policy。
- order state machine、idempotency、ledger、reconciliation 與 restart recovery。
- paper／shadow 的期間、樣本、告警、dashboard isolation 與操作核准。
- RPO／RTO、restore、single-active／fencing、credential drill、venue／quote-asset risk、compound chaos 與 on-call。
- 未解 Sev-1／Sev-2、BLOCKER／HIGH finding、rollback 與人工 approval。

## 5. 狀態與 verdict 規則

每列只使用：

- `PASS`：本次取得且可重現的證據完整證明要求。
- `FAIL`：要求適用，且實作缺失、行為違規、測試失敗或證據明確不符合。
- `BLOCKED`：必要檢查因安全邊界、工具、權限、資料、artifact 或操作證據缺失而不能判定。
- `NOT APPLICABLE`：該要求確實不屬於被驗收里程碑；必須寫理由，不得用來隱藏 deferred prerequisite。

Overall verdict 依下列優先序：

1. 任一必要列為 `FAIL`：`NOT READY`。
2. 無 `FAIL`，但任一必要列為 `BLOCKED`：`BLOCKED`。
3. 所有必要列為 `PASS`，其餘有正當 `NOT APPLICABLE`：`READY`。

`READY` 只代表可提交人類審核，不代表自動 promotion、可交易、安全、可獲利或 production-ready。

## 6. 輸出格式

依序輸出：

1. `Repository truth snapshot`：branch、commit、dirty state、比較基準、檢查時間。
2. `Current milestone`：最高完成里程碑與候選里程碑，附理由。
3. `Maximum permitted environment`：research／backtest／replay／paper／shadow 之一；除非使用者另行要求 canary/live gate，本 Skill 不建議更高環境。
4. `Overall verdict`：`READY`、`NOT READY` 或 `BLOCKED`。
5. `Acceptance matrix`：

| Milestone | Requirement | Status | Implementation evidence | Test／CI evidence | Operational evidence | Gap／next action |
|---|---|---|---|---|---|---|

6. `Prerequisite and promotion gates`。
7. `Security and risk blockers`。
8. `Missing or stale evidence`。
9. `Commands executed`：命令、退出碼與摘要。
10. `Recommended next issue`：只提出一個最小、可審查且不跳級的工作。
11. `Explicit non-claims`：未啟用環境、未連線、未證明可交易或可獲利。

引用 evidence 時提供 repository-relative path、測試名稱、CI job 或 artifact identifier。不可只寫「見文件」。
