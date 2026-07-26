---
name: risk-engine-invariant-test
description: 當需要建立測試設計或唯讀稽核獨立 RiskEngine 的部位限制、stale data、reconciliation、kill switch、冪等、restart 與拒單稽核 invariants 時使用；不要用於放寬風控、實作送單、連線正式環境或核准 live。
---

# Risk Engine Invariant Test

驗證所有增加風險的 `OrderIntent` 都必須經獨立 RiskEngine，且任何不確定狀態 fail closed。預設為唯讀稽核；只有使用者明確要求新增測試時，才可在不修改應用功能與風險門檻的前提下建立測試。

## 安全邊界

- 先完整閱讀 `AGENTS.md`，特別是風險引擎、測試、晉級、DR、leadership、credential 與 venue risk 規格。
- 不新增或啟用 broker／exchange adapter，不讀取正式憑證。
- 不修改 `configs/live.yaml`、資本上限、loss／drawdown threshold 或 bypass flag。
- 不以刪除、skip、xfail、放寬 assertion 或固定測試輸出換取通過。
- 緊急平倉仍需 `EmergencyRiskPolicy`；不得建立 `force_order`／`skip_risk_check`。
- 若獨立 RiskEngine 不存在，輸出完整 test design 並將 executable invariant checks 標為 `BLOCKED`，不得假裝測試通過。

## 1. 模式選擇

- `AUDIT`：預設；只讀 source、tests、config、CI 與 artifacts。
- `TEST DESIGN`：實作不存在或使用者只要設計；產生 deterministic cases，不建立功能。
- `TEST AUTHORING`：只有使用者明確要求修改測試時；先確認 app code 不需變更，否則停止並回報超出本 Skill 範圍。

無論何種模式，都不執行真實下單。

## 2. 發現實際風控邊界

閱讀：

- `src/trading_system/` 的現有模組，並以 tracked-file inventory 判斷 risk、portfolio、execution、persistence 邊界是否存在。
- `configs/base.yaml`、各 environment 與 market profile。
- `docs/risk-policy.md`、execution policy、相關 RFC／ADR。
- unit、property、integration、replay、chaos、restart／DR tests。
- CI workflows 與目前 diff。

執行：

```bash
git status --short --branch
git ls-files
rg -n -i "RiskEngine|RiskDecision|OrderIntent|TargetPosition|APPROVE|REJECT|RESIZE|CLOSE_ONLY|CANCEL_ALL|HALT" src tests configs docs
rg -n -i "skip.?risk|force.?order|bypass|stale|reconcil|duplicate|idempoten|fencing|restart" src tests configs docs
```

建立實際 call graph。若策略或控制面可直接到 broker，立即記錄 `CRITICAL / FAIL`。

## 3. 必要 invariants

為每項建立「前置狀態、輸入、預期 `RiskDecision`、禁止副作用、audit evidence」：

1. `No bypass`：沒有通過 RiskEngine 的 intent 不可到達 execution adapter。
2. `Position limits`：order 後的 asset、cluster、venue、quote-asset、gross、net、cash、turnover 與 participation 不超過版本化限制。
3. `Stale data`：stale、out-of-order、quality failure 或 sequence uncertainty 不得增加風險。
4. `Reconciliation`：帳戶、position、cash、open order 不一致時只允許 reject／close-only／halt。
5. `Kill switch`：觸發後新風險單一律拒絕；不得因 restart 清除狀態。
6. `Duplicate safety`：重複 event、intent、command 或 acknowledgment 不產生 duplicate order／fill／ledger entry。
7. `Numeric safety`：Decimal quantization、epsilon、rounding 與 tolerance 不得突破限制；NaN／Inf／overflow 一律拒絕。
8. `Restart durability`：restart、restore、leader handoff 後仍保留 limits、drawdown、kill-switch、idempotency 與 latest config version。
9. `Traceable rejection`：所有 reject／resize 都有 decision id、input event、config／policy version、reason code、correlation／causation 與 immutable audit record。
10. `Unknown state`：unknown order、venue、quote asset、credential、leadership、recovery 或 database state 不得增加風險。
11. `Resize monotonicity`：resize 後風險不得高於原 intent，也不得因 rounding 反向開倉。
12. `Emergency monotonicity`：close／flatten 不得超量、反向、重複或使用無界限 market order。

## 4. Property-based test design

優先使用 Hypothesis 與 deterministic fixtures。每個 property 明確固定：

- Decimal strategy 與合法 precision；
- timezone-aware UTC time；
- deterministic seed；
- config／policy version；
- generated values 的上下界與最小 failing example；
- external broker snapshot 與 initial ledger。

至少設計：

```text
approved_post_trade_exposure <= configured_limit
resized_risk <= original_risk
duplicate(input) leaves terminal_state unchanged
gross_exposure >= abs(net_exposure)
kill_switch_active => no risk_increasing submission
not reconciled => decision in {REJECT, CLOSE_ONLY, HALT}
not fresh_or_ordered => decision in {REJECT, CLOSE_ONLY, HALT}
restart(state) preserves limits and idempotency
```

Boundary cases包含 limit−tick、limit、limit+tick、zero、negative、very large、precision change、clock boundary、drawdown threshold 與 lease expiry。

## 5. Deterministic scenario fixtures

至少覆蓋：

- stale market data + otherwise profitable signal；
- partial fill + submit timeout + runtime crash；
- duplicate event + RiskEngine restart + stale config；
- reconciliation mismatch + database unavailable；
- kill switch + queued intent；
- split-brain + stale fencing token；
- venue withdrawal suspension／custody risk／unknown quote asset；
- rounding near max position；
- reject response lost and replayed。

每個 fixture 必須有 deterministic timeline、seed、expected decisions、expected order／ledger states 與 safe terminal state。禁止任何外部網路。

## 6. 執行與證據

若測試存在，執行 repository 定義命令：

```bash
uv run pytest -m property
uv run pytest -m replay
uv run pytest -m chaos
uv run pytest
```

工具或實作缺失時，不臨時建立假的 RiskEngine。改為輸出：

- 建議 test path；
- fixture input schema；
- property／example；
- expected result；
- 目前 blocker；
- 解除 blocker 所需最小 issue。

mock config 的 `fail_closed: true` 或 zero exposure 只能算設定意圖，不能證明 pre-trade RiskEngine invariant。

## 7. 狀態與輸出

- `PASS`：property、boundary、restart 與 audit evidence 均實際通過。
- `FAIL`：找到繞過、超限、增加風險、重複副作用、狀態遺失或不可追蹤拒單。
- `BLOCKED`：RiskEngine／ledger／runner／fixture／artifact 缺失，無法執行必要行為測試。
- `NOT APPLICABLE`：只允許對真正不在目標 risk profile 的市場專屬控制，並附理由。

輸出順序：

1. `Critical findings`。
2. `Risk boundary map`。
3. `Invariant matrix`：

| Invariant | Status | Implementation | Property／fixture | Result evidence | Missing work |
|---|---|---|---|---|---|

4. `Blocked test designs`：只有未能執行者。
5. `Commands executed` 與退出碼。
6. `Verdict`: `PASS`、`FAIL` 或 `BLOCKED`。
7. `Promotion impact`：任一必要 invariant 非 PASS，阻止 paper 或更高環境。

不得宣稱 RiskEngine 安全、完整或 production-ready；只能陳述已驗證的 invariant 與限制。
