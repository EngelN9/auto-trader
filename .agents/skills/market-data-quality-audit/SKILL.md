---
name: market-data-quality-audit
description: 當需要稽核市場資料 timestamp、缺口、重複、順序、staleness、instrument metadata、lineage、hash 或 NOT_TRADABLE gate 時使用；不要用於下載大型資料、選定正式供應商、建立交易連線或評估策略績效。
---

# Market Data Quality Audit

唯讀稽核 market-data ingestion、normalization、metadata 與 quality gate。資料品質不合格或不可確認時，必須阻止回測、策略決策與任何增加風險的流程。

## 安全與範圍

- 以根目錄 `AGENTS.md` 為最高規格，並閱讀 `Trader prompts.md` 的資料品質與極端資料要求。
- 不下載市場資料、不呼叫正式 provider／venue、不要求 API key。
- 不修改或修補 raw data；任何修補必須是版本化新產物，本 Skill 只稽核。
- 不把 schema、README、empty interface 或 synthetic happy-path fixture 當作可運行 pipeline。
- 無資料集、manifest、hash、license 或執行工具時輸出 `BLOCKED`，不得假裝抽樣通過。

## 1. 發現實際資料邊界

閱讀：

- `src/trading_system/` 的現有模組與 domain market events，並以 tracked-file inventory 判斷 data module 是否存在。
- `services/market-data-worker/`、`data/`、`configs/markets/`。
- data quality、property、regression、replay、chaos fixtures。
- `docs/` 內 data pipeline、architecture、venue／quote-asset、model governance 文件。
- `Makefile`、CI workflows、dependency locks 與目前 diff。

執行：

```bash
git status --short --branch
git ls-files data src services configs tests docs .github
rg -n -i "timestamp|timezone|sequence|duplicate|stale|missing|lineage|checksum|manifest|symbol|tick.?size|lot.?size|corporate.?action" src services configs tests data docs
```

若 tracked-file inventory 中沒有 data module、實際 manifest 或 quality runner，明確記錄為實作缺口；不要用 `services/market-data-worker/README.md` 取代。

## 2. 建立資料流與 lineage map

對每個資料集或 feed 記錄：

```text
source -> upstream lineage／independence group
       -> raw append-only batch
       -> manifest + schema version + checksum
       -> canonical normalization
       -> quality checks
       -> quarantine／NOT_TRADABLE
       -> backtest／strategy consumer
```

每一段都要引用實際 path、類別、函式、設定、fixture 與測試。缺少任何阻斷閘門時，consumer 不得標示可用。

## 3. 必查資料品質控制

逐項檢查並區分 crypto 與 future equity：

### 時間與事件完整性

- exchange、provider、ingest timestamp 分離且為 timezone-aware UTC。
- session／timezone／calendar 語意正確；crypto 24/7 與 equity exchange calendar 不共用錯誤年化或 session 規則。
- timestamp 單調性、sequence gap、duplicate、out-of-order 與 reconnect replay。
- missing interval、跨 session forward fill、stale payload with fresh timestamp。
- clock skew 與 ingest lag 的閾值、單位、版本與 fail-closed action。

### 價格、數量與 order-book invariants

- 價格與成交量非負且落在定義域。
- OHLC：`low <= open/close <= high`。
- bid <= ask；locked／crossed market、zero depth、極端 jump 與 10x／100x scale change 可被 quarantine。
- price／quantity precision、tick size、lot size、minimum notional 有歷史版本。
- amount、price、quantity、fee 不以 binary float 進入交易邊界。

### Instrument 與 snapshot consistency

- canonical schema 保留 asset class、venue、symbol、session、status 與 precision。
- symbol mapping、base／quote、venue、listing／delisting／rename 不混淆。
- snapshot 與 incremental update 能以 sequence 恢復一致狀態；reconnect 不丟失或重放成雙重事件。
- exchange maintenance、API outage、halt 與 trading status 使 instrument `NOT_TRADABLE`。

### Lineage 與版本

- raw data append-only；修補不覆寫原始批次。
- manifest 保存來源、參數、時間範圍、row count、schema、license、版本與 cryptographic hash。
- hash 驗證實際 bytes，而非只保存字串。
- 第二來源有 upstream lineage 與 independence group；共同上游不得算獨立確認。
- stablecoin／quote asset 來源不足、矛盾或 redemption state 未知時採 `UNKNOWN`／`NOT_TRADABLE`。

### Equity 邊界

即使股票尚未啟用，也檢查 interface 是否明確 deferred：

- split、reverse split、dividend、symbol change、merger、delisting、halt。
- adjusted 與 unadjusted price 分離，避免 double adjustment。
- point-in-time universe、exchange calendar、half-day 與 corporate-action version。

未進入 equity Milestone 時可將執行測試列為 `NOT APPLICABLE`，但若共用 schema 已宣稱支援 equity，契約缺口應標 `FAIL`。

## 4. 驗證測試與阻斷行為

優先執行 repository 已有的 data-quality 測試與 runner，不建立網路連線。若完整 Python suite 是目前唯一入口：

```bash
uv run pytest
```

對每個控制要求 deterministic fixture：

- duplicate、gap、out-of-order、stale、clock skew；
- invalid OHLC、negative values、crossed book、zero depth；
- reconnect snapshot mismatch；
- maintenance、delisting、symbol collision、precision change；
- common-upstream bad data、depeg、stale-content-fresh-timestamp；
- corporate-action double adjustment（equity 適用時）。

驗證輸出不只產生 alert，還必須：

1. quarantine batch／instrument；
2. 設為 `NOT_TRADABLE`；
3. 阻止 backtest 或 strategy consumer；
4. 保留原因、event id、manifest version 與 audit evidence。

缺少 consumer-side enforcement 時，即使 detector 測試通過也標 `FAIL`。

## 5. 狀態規則

- `PASS`：控制已實作，deterministic fixture 與阻斷 consumer 的測試均通過。
- `FAIL`：控制缺失、錯誤資料仍流入 consumer、lineage 不可追或 hash／metadata 不正確。
- `BLOCKED`：必要 dataset、manifest、runner、工具或 artifact 不可取得，無法執行。
- `NOT APPLICABLE`：確實不在目標市場／資料型態範圍，並附理由。

若任何適用的 critical quality gate 為 `FAIL` 或 `BLOCKED`：

- `Backtest permitted: NO`
- `Strategy consumption permitted: NO`
- `Tradability: NOT_TRADABLE`

## 6. 輸出格式

1. `Dataset／feed inventory`：來源、market、時間範圍、manifest、hash、license、consumer。
2. `Data-flow and lineage map`。
3. `Quality acceptance matrix`：

| Control | Market／dataset | Status | Implementation evidence | Fixture／test evidence | Blocking behavior | Gap |
|---|---|---|---|---|---|---|

4. `Critical findings`：先列可污染回測或增加交易風險者。
5. `Backtest and strategy gate`。
6. `Commands executed`、退出碼與摘要。
7. `Missing evidence`。
8. `Verdict`: `PASS`、`FAIL` 或 `BLOCKED`。

不得因缺少市場資料而建立假資料證明 production quality；synthetic fixture 只能證明控制邏輯，不能證明實際供應商資料品質。
