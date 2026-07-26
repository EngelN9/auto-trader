---
name: deterministic-backtest-audit
description: 當需要稽核事件驅動回測的前視偏誤、倖存者偏誤、資料洩漏、seed、dataset hash、成交成本、walk-forward、帳務或重現性時使用；不要用於調參追求績效、建立策略、下載資料或 promotion。
---

# Deterministic Backtest Audit

以唯讀方式判斷回測是否可重現、無已知偏誤、保守建模成交並正確記帳。不得只以 return、Sharpe ratio、勝率或單一最佳參數判定策略有效。

## 安全邊界

- 以 `AGENTS.md` 第 8、9、10、13、14、15、17 節及 `Trader prompts.md` 的回測／驗證 prompts 為準。
- 不修改策略、資料範圍、成本假設、holdout、風控門檻或失敗 fixture。
- 不連線正式市場、broker 或 exchange；不要求任何 API key。
- 不自動 promotion 至 backtest、paper、shadow、canary 或 live。
- 缺資料、manifest、engine、runner 或可重現環境時回報 `BLOCKED`。

## 1. 發現回測實作

完整閱讀：

- `src/trading_system/` 內 data、engine、strategies、portfolio、risk、execution、persistence（存在者）。
- `tests/` 內 unit、property、replay、regression、integration 與 backtest fixtures。
- `data/`、`configs/`，以及 tracked-file inventory 中可找到的 research reports。
- `docs/` 中的 strategy specs、`docs/model-governance.md`、`docs/execution-policy.md`、`Makefile`、CI 與鎖檔。

執行唯讀發現：

```bash
git status --short --branch
git ls-files
rg -n -i "backtest|replay|run.?manifest|random.?seed|walk.?forward|holdout|slippage|partial.?fill|surviv|look.?ahead|available_at" src tests data research docs configs Makefile .github
```

若 `make backtest` 或等價入口明確回傳 not implemented，將 engine existence 標 `FAIL`，行為測試標 `BLOCKED`；不得用 deterministic checksum helper 代替 deterministic backtester。

## 2. 重建事件時間線

對一個最小 fixture 追蹤：

```text
source event
-> available_at
-> feature window
-> signal decision time
-> OrderIntent
-> RiskDecision
-> simulated submit／latency
-> fill／reject／partial fill／non-fill
-> position／cash／fees／PnL ledger
```

確認：

- 決策時間 `t` 只能讀取 `available_at <= t`。
- closed bar 才能使用完整 OHLC；Donchian 等 window 排除 current bar。
- fit、normalization、imputation、universe selection 只使用當時可得資料。
- 執行事件嚴格晚於 signal；同 timestamp 必須有明確穩定排序規則。

## 3. 必查偏誤與重現性

### Bias controls

- look-ahead bias、same-bar fill、future fill／imputation。
- survivorship bias、today's universe、delisted instrument omission。
- data leakage across train／validation／test、overlapping labels、global scaling。
- corporate-action publication timing 與 revised data leakage。
- final holdout 不參與選模；purging／embargo 適用時存在。

### Determinism and provenance

- 所有隨機程序有 explicit seed；相同 input、config、commit、seed 產生 byte-equivalent 或明確 canonical-equivalent 結果。
- run manifest 至少含 `run_id`、git commit、image digest、config hash、strategy／risk version、data manifest hash、universe／calendar version、seed、dependency lock hash、start／end。
- dataset 有 version、cryptographic hash、lineage；執行前與報告時驗證相同 hash。
- event ordering、parallel reduction、Decimal serialization 與 tie-breaking 不依賴 process／filesystem 順序。

### Execution realism

- fee／rebate、half-spread、slippage、market impact 與 safety buffer。
- latency、limit non-fill、partial fill、rejected order、cancel race、unknown order。
- OHLCV-only 模型採保守 bar path 或多路徑 stress；不得觸價即 100% fill。
- 1.5x／2x costs、spread widening、額外 latency、20%／50% fills、gap、zero liquidity、venue outage 與 compound failures。

### Accounting invariants

- cash + marked positions + realized／unrealized PnL - costs 一致。
- fills -> average cost -> positions -> PnL 守恆。
- duplicate event 不改變最終帳本；reject／non-fill 不改變 position。
- gross exposure >= abs(net exposure)。
- price、quantity、fee、cash 使用 Decimal／定點數；rounding tolerance 有方向與單位。
- restart／replay 不重複收費、成交或部位。

## 4. Validation protocol

若存在正式 runner，使用相同 input、config、commit 與 seed 執行至少兩次：

1. 比較 run manifest。
2. 比較 event count、orders、fills、positions、ledger、metrics 與 artifact hashes。
3. 任何未說明差異均為 `FAIL`。

執行 repository 定義的相關測試；工具不可用則 `BLOCKED`：

```bash
uv run pytest -m replay
uv run pytest -m property
uv run pytest
```

對策略證據檢查：

- rolling／expanding walk-forward，各 fold 個別報告；
- final holdout 保護；
- parameter neighborhood、start-date、bootstrap、placebo、shifted signal；
- PnL concentration、regime breakdown、tail loss、capacity；
- benchmark 與簡單 baseline；
- normal／1.5x／2x cost 及極端 scenario。

績效較好不能抵銷 bias、accounting、determinism 或 risk failure。

## 5. 狀態與總結規則

- `PASS`：實作、fixture、兩次重跑與 artifacts 一致，且控制行為符合規格。
- `FAIL`：發現偏誤、非確定性、錯誤帳務、理想化成交或適用控制缺失。
- `BLOCKED`：engine／dataset／manifest／runner／工具或 artifact 缺失而不能執行。
- `NOT APPLICABLE`：目標回測確實不使用該資料或功能；附精確理由。

下列任一項非 `PASS` 時，`Backtest evidence acceptable` 必須為 `NO`：

- no-look-ahead；
- dataset provenance；
- deterministic repeatability；
- cost／fill model；
- position／portfolio accounting；
- walk-forward／holdout（策略 promotion 適用時）。

## 6. 輸出格式

先列 findings，再列：

| Control | Status | Code evidence | Fixture／test | Run／artifact evidence | Impact |
|---|---|---|---|---|---|

接著輸出：

- `Backtest inventory and entry point`
- `Bias assessment`
- `Repeatability comparison`
- `Execution-model assessment`
- `Accounting reconciliation`
- `Walk-forward and robustness evidence`
- `Commands executed` 與退出碼
- `Missing evidence`
- `Verdict`: `PASS`、`FAIL` 或 `BLOCKED`
- `Promotion impact`: 只陳述是否阻止下一 gate，不執行 promotion

不得宣稱正期望值、可獲利或可交易，除非另有完整樣本外與 promotion 證據；即使存在也只能準確描述證據，不做保證。
