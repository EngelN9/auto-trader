---
name: docs-code-drift-check
description: 當需要比對 README、AGENTS、Trader prompts、source、tests、CI、configuration、Milestone 聲明與操作程序是否漂移時使用；不要用於把規格當實作、修改功能、啟用交易環境或自動重寫政策。
---

# Docs-Code Drift Check

唯讀比對 normative specification、descriptive claims 與 executable behavior。規格文件定義要求，但不證明要求已完成。

## 安全邊界

- `AGENTS.md` 是最高層級規格；子目錄 `AGENTS.md` 只能在其範圍內增加或具體化限制。
- 不自動修改 docs、source、tests、config 或 CI。
- 不建立交易連線、不讀秘密、不執行 promotion。
- 不把 README badge、status label、未完成標記、interface、mock、workflow 名稱或 policy skeleton 當成 operation evidence。
- 無法執行或取得必要 evidence 時標 `BLOCKED`。

## 1. 建立來源分類

完整閱讀並分類：

1. `Normative`：根目錄及子目錄 `AGENTS.md`。
2. `Milestone workflow`：`Trader prompts.md`。
3. `Descriptive`：`README.md`、`docs/`、service／infra readmes。
4. `Executable`：`src/`、`services/`、`apps/`、scripts、Dockerfiles。
5. `Configuration`：base、environment、market profiles、environment example。
6. `Verification`：tests、fixtures、CI workflows、reports、manifests、artifacts。
7. `Operations`：runbooks、DR、incident、on-call、deployment、monitoring、migration。

先盤點：

```bash
git status --short --branch
git ls-files
git diff --check
rg -n -i "complete|ready|implemented|supported|enabled|tradable|production|safe|milestone|paper|shadow|canary|live|not implemented|deferred|mock" README.md AGENTS.md "Trader prompts.md" docs services infra apps configs src tests .github
```

## 2. 建立 claim-evidence mapping

對每個 material claim 記錄：

| Claim | Source and line | Claim type | Required implementation | Required verification | Actual evidence |
|---|---|---|---|---|---|

優先處理會改變使用者行為或 promotion 的聲明：

- current Milestone／completed status；
- maximum permitted environment；
- tradable／production-ready／safe／profitable；
- supported market／asset class；
- data quality／backtest／risk／execution／ledger／reconciliation；
- authentication／RBAC／audit／kill switch；
- RPO／RTO／restore／on-call／alerts；
- credential isolation、withdrawal／transfer permissions；
- CI、dependency、container security coverage；
- operational command 與 runbook 可用性。

## 3. 雙向檢查

### Docs -> code

對每個文件聲明：

1. 找到 source／config 實作。
2. 找到直接測試與 CI entry。
3. 若聲明涉及 runtime 或 operations，找到本次可重現 artifact／drill。
4. 檢查 limitation、environment 與 date 是否仍正確。

### Code -> docs

對每個 material behavior change：

1. 檢查 README／architecture／policy／runbook 是否更新。
2. 檢查 config schema、default、units、failure mode 是否記錄。
3. 檢查 new dependency、license、supply-chain risk、alternative。
4. 檢查 API／schema／migration／rollback 與 Milestone impact。
5. 檢查 operator 會不會依舊文件採取危險行動。

### Tests／CI -> claims

- test 名稱不能代替 assertion coverage。
- workflow job 名稱不能代替實際執行命令。
- mock／string-existence test 不證明 production behavior。
- 過期、不同 commit 或不同 config 的 artifact 不證明 current HEAD。
- `PASS` 必須綁定 commit、command、exit code 與 relevant output。

## 4. 必查 drift domains

- README status vs Milestone acceptance evidence。
- `AGENTS.md` MUST／MUST NOT vs application behavior。
- `Trader prompts.md` prerequisite ordering vs repo claims。
- source events／config models vs documented schemas。
- config defaults vs docs environment boundaries。
- Make targets／README commands vs actual Makefile、package scripts、CI。
- tests marker／suite claims vs discovered tests。
- CI workflow permissions、action pins、security scans vs security docs。
- dashboard display vs Control API／runtime mode。
- risk／execution／data docs vs implemented modules。
- disaster recovery／incident／on-call docs vs actual drills and infrastructure。
- future equity／cross-asset language vs currently enabled market profile。

## 5. 分類 drift

- `OVERCLAIM`：文件宣稱的能力高於實作／證據。
- `UNDERDOCUMENTED`：實作行為或風險未文件化。
- `CONTRADICTION`：不同文件、config、code 或 tests 給出互斥事實。
- `STALE PROCEDURE`：命令、路徑、參數、owner 或操作步驟已過期。
- `MISSING EVIDENCE`：聲明可能正確，但沒有 current、reproducible evidence。
- `SAFE DEFERRED`：文件與 code 均清楚標示未實作且 fail closed；不是 defect，但仍列在 scope。

對可能誤導 operator 進入較高環境、使用正式憑證或相信不存在的風控者列最高嚴重性。

## 6. 驗證

只執行 repository 已定義、無外部交易 side effect 的命令：

```bash
uv run pytest
uv run python scripts/check_workflow_pins.py
pnpm lint
pnpm typecheck
pnpm test
pnpm build
docker compose config --quiet
```

命令不可用或環境不相容時標 `BLOCKED`；不要改寫文件聲稱已通過。

驗證所有文件引用的 repository path 與命令：

- path 必須存在於 current tree，或明確標示 future／deferred；
- command 必須存在於 Makefile、package scripts、workflow 或實際可用 tool；
- not implemented target 必須保留非零退出碼，不能被文件描述成可用功能。

## 7. 狀態

- `PASS`：claim 與 current implementation、test／CI 及適用 operational evidence 一致。
- `FAIL`：overclaim、contradiction、stale procedure 或 required docs 缺失。
- `BLOCKED`：缺少 current artifact、工具、權限或 runtime evidence。
- `NOT APPLICABLE`：claim 確實不涉及目前範圍，附理由；future requirement 不應被誤標完成。

## 8. 輸出格式

先列 drift findings，按對安全與 operator 決策的影響排序。每項包含：

- classification、severity、status；
- docs path／line 與 code／test／config counterpart；
- 衝突內容；
- 實際 repository truth；
- 可能後果；
- 最小修正方向（docs、code、test 或 claim）。

再輸出：

| Claim／requirement | Docs evidence | Executable evidence | Verification／operations | Status | Drift |
|---|---|---|---|---|---|

最後列：

- `Current truthful project statement`。
- `Milestone and maximum-environment consistency`。
- `Commands／paths verified`。
- `Blocked evidence`。
- `Verdict`: `PASS`、`FAIL` 或 `BLOCKED`。
- `Explicit non-claims`：未證明可交易、可獲利、安全或 production-ready。

若規格與實作都說「未實作／mock-only／HALT」，這是對齊；不要把缺少未宣稱的功能誤報為 docs drift，但可在 Milestone gate 中另列缺口。
