---
name: pr-evidence-review
description: 當需要審查 Auto Trader pull request、branch diff、測試與 Milestone acceptance evidence 時使用；先列 findings 再摘要，不要用於直接修復、合併、approve promotion、送單或把 PR 敘述當成實作證據。
---

# PR Evidence Review

以嚴格、唯讀 reviewer 身分審查目前 branch 或指定 PR。優先找出會破壞正確性、安全、資料完整性、確定性、風控與可回滾性的問題。

## 安全與授權

- 不修改檔案、不 resolve thread、不 approve／merge PR、不 commit／push。
- 不執行真實交易、部署或正式環境檢查；不要求或讀取 secrets。
- 不把作者摘要、check 名稱或規格文字當作證據，必須看 diff、實作、測試輸出與 artifacts。
- 對未知狀態採 fail closed；無 PR metadata、base、log 或 artifact 時標 `BLOCKED`。
- findings 必須在摘要之前；沒有 actionable finding 時才明寫「No findings」。

## 1. 確立 review scope

完整閱讀：

- 根目錄 `AGENTS.md` 及變更路徑適用的子目錄 `AGENTS.md`。
- `README.md`、`Trader prompts.md` 與相關 risk／execution／strategy／data／DR／security 文件。
- PR 描述、linked issue、acceptance criteria、review threads 與 CI 結果（可取得時）。

記錄：

```bash
git status --short --branch
git rev-parse HEAD
git diff --check
git diff --merge-base main HEAD --stat
git diff --merge-base main HEAD
```

若 base 不是 `main`，使用 PR metadata 的實際 base。若可安全使用已登入的 GitHub CLI：

```bash
gh pr view <number> --json number,title,body,baseRefName,headRefName,commits,files,reviews,statusCheckRollup
gh pr checks <number>
```

無權限時仍完成 local diff review，但將遠端 evidence 標 `BLOCKED`。

## 2. 先理解目的與完整影響

建立 mapping：

| Claimed purpose | Changed files | Runtime consumers | Safety／data impact | Required evidence |
|---|---|---|---|---|

檢查直接與間接影響：

- strategy、portfolio、risk、execution、broker、control、persistence。
- domain／OpenAPI／JSON schema 與 migration compatibility。
- config defaults、environment overlays、market profiles。
- dashboard、service boundary、deployment、CI permissions、dependencies。
- tests、fixtures、reports、docs、RFC／ADR、rollback。

不要只看 diff hunks；閱讀被修改符號的 callers、callees、tests 與配置來源。

## 3. 必查 review controls

### 正確性與安全

- edge cases、illegal states、catch-all、error propagation、fail closed。
- 策略不得直接送單；每筆 intent 經獨立 RiskEngine。
- live 預設關閉；環境、憑證、database、topic 不混用。
- stale／out-of-order data、unknown order、reconciliation／DB failure 不增加風險。
- Decimal／fixed-point 用於 money、price、quantity、fees。
- duplicate／idempotency、restart、fencing、kill switch。

### 資料與研究

- lineage、version、hash、point-in-time、timestamp semantics。
- look-ahead、survivorship、data leakage。
- deterministic seed、run manifest、repeatability。
- fee、spread、slippage、latency、partial fill、reject、non-fill。
- accounting、walk-forward、holdout、stress、concentration；不得只報 return／Sharpe。

### API、schema 與 persistence

- breaking changes 版本化且有 contract test。
- migration forward／rollback、安全預設、資料守恆。
- audit events append-only；未知 schema／config fail closed。
- dashboard 不直連 broker、不計算或覆寫 risk。

### Operational resilience

- observability、reason codes、correlation／causation、alert／runbook。
- rollback 能保存 audit evidence 且不自動恢復新增風險。
- RPO／RTO、restore、leader／fencing、credential revoke、venue／depeg、compound chaos、on-call evidence。

### Evidence integrity

- tests 真正覆蓋變更行為而非只檢查字串或 placeholder。
- 沒有刪除 failing tests、不利期間、fixture 或降低 assertions。
- CI job 確實執行適用 suite。
- 沒有 fake implementation、hard-coded pass 或將未完成標記偽裝成完成。
- Milestone／readiness claim 與實際 acceptance criteria 一致。

## 4. 驗證

依 diff 風險選擇 repository 已定義的唯讀命令：

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

無法執行的適用 check 標 `BLOCKED`。CI 綠燈不替代 reviewer 對 test adequacy 的判斷。

## 5. Finding 嚴重度

- `BLOCKER`：可造成真實交易／憑證風險、風控繞過、資料／帳本不可逆損壞、promotion gate 假通過或 MUST NOT 違規。
- `HIGH`：高機率造成錯誤風險決策、duplicate order、偏誤回測、失效關閉失敗、無法復原。
- `MEDIUM`：重要 correctness、observability、contract、migration、test 或 documentation 缺口。
- `LOW`：有限影響的維護性、防禦縱深或明確未來風險。
- `NIT`：不阻擋、無行為影響；避免把偏好偽裝成 finding。

每個 finding 必須可由具體行為觸發，包含：

- title；
- severity 與 `FAIL`／`BLOCKED`；
- file 與精確 line；
- violated requirement／invariant；
- trigger scenario；
- consequence；
- evidence；
- minimal remediation；
- required regression test。

不要列沒有可行動內容的 finding。

## 6. 狀態與 verdict

Evidence matrix 使用：

- `PASS`：實作與適用測試／artifact 證明要求。
- `FAIL`：發現缺陷、缺少必要實作或證據明確不符。
- `BLOCKED`：必要 remote／runtime／artifact／tool evidence 無法取得。
- `NOT APPLICABLE`：確實不受 diff 影響，附理由。

Review verdict：

- 有任一 `BLOCKER`／`HIGH`：`REQUEST CHANGES`。
- 無 blocker/high，但有 correctness `MEDIUM`：通常 `REQUEST CHANGES`。
- 無 actionable finding，但必要 evidence 被阻擋：`BLOCKED`。
- 無 finding 且所有必要 evidence 完整：`APPROVE`；這仍不代表 promotion approval。

## 7. 輸出格式

嚴格依此順序：

1. `Findings`：由最高嚴重度排序。
2. `Review verdict`。
3. `Change-purpose and impact matrix`。
4. `Evidence matrix`：

| Area | Status | Code evidence | Test／CI evidence | Artifact／operational evidence | Gap |
|---|---|---|---|---|---|

5. `Required fixes`。
6. `Tests to rerun`。
7. `Migration／schema／rollback assessment`。
8. `Milestone acceptance impact`。
9. `Summary`：放最後，保持簡潔。

若沒有 findings，先寫 `No actionable findings.`，再列 residual risks 與被阻擋的 evidence。不得因 diff 小就省略安全邊界審查。
