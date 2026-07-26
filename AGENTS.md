# AGENTS.md — 可驗證、可重現、可維護的自動交易系統

> 本檔案是本儲存庫對 Codex、其他程式設計代理與人類貢獻者的最高層級工程規格。
> 除非子目錄存在更具體的 `AGENTS.md`，否則本規格適用於整個儲存庫。
>
> 本系統的目標是以嚴格研究流程尋找正期望值，並追求穩健的風險調整後報酬；**不保證獲利**。任何策略在真實市場中都可能失效、出現滑價、流動性枯竭、交易所或券商故障、模型漂移與超出歷史樣本的損失。

---

## 0. 規範用語

本文件中的關鍵詞依下列強度解讀：

- **MUST／必須**：不可違反。
- **MUST NOT／禁止**：不可執行。
- **SHOULD／應該**：除非有書面、可審查的理由，否則必須遵循。
- **MAY／可以**：可選實作。

若「提高報酬」與「正確性、可重現性、安全、法令遵循或風險限制」衝突，永遠優先後者。

---

## 1. 專案使命

建立一個事件驅動、可稽核、可回放、可分階段部署的股票與加密貨幣自動交易平台，統一支援：

1. 歷史資料擷取與資料品質驗證。
2. 因子與策略研究。
3. 事件驅動回測。
4. Walk-forward 與樣本外驗證。
5. 模擬交易、影子交易與小額試運行。
6. 即時風險控制與訂單執行。
7. 24 小時監控、對帳、告警與緊急停止。
8. 完整版本、參數、資料與決策稽核軌跡。

「24 小時系統」不代表所有資產都能 24 小時成交。加密貨幣模組可持續運作；股票模組必須依交易所行事曆、休市、盤前盤後規則與券商能力決定是否允許下單。

### 1.1 系統產品形態與責任邊界

本專案必須實作為：

> **24 小時運行的伺服器端交易應用程式，加上一個用於監控與受控操作的 Web 管理儀表板。**

它不是「靠瀏覽器持續開啟才會交易」的網站，也不是以手機 App 為核心的消費型應用程式。瀏覽器、PWA 或未來的原生 App 都只能存取控制平面；真正的行情處理、訊號計算、風險判斷、訂單執行、對帳與持久化必須在伺服器端獨立運作。

```text
券商／交易所 API
        ↓
市場資料與資料品質閘門
        ↓
策略／市場狀態／投資組合引擎
        ↓
獨立風險引擎
        ↓
訂單執行與對帳服務
        ↓
PostgreSQL、事件日誌、Metrics、告警
        ↑
內部 Control API
        ↑
Web 管理儀表板／PWA／通知通道
```

系統劃分為兩個明確平面：

1. **交易資料平面（data／decision／execution plane）**
   - 接收行情、建立特徵、產生訊號與目標部位。
   - 執行 pre-trade risk checks、送單、追蹤訂單、處理成交與對帳。
   - 即使 Web 儀表板停止、重新部署或無法連線，也必須維持安全運作，或依既定規則 fail closed。
   - 禁止依賴瀏覽器 session、前端排程器或使用者裝置保持上線。

2. **控制平面（control plane）**
   - 提供唯讀監控、稽核查詢、策略狀態與受控操作。
   - 任何會影響交易的操作都必須轉換成版本化、可稽核的命令事件，再由後端授權與驗證。
   - 前端禁止直接呼叫券商／交易所交易 API，禁止保存正式 API key，禁止自行計算或覆寫風控結果。

### 1.2 Web 管理儀表板定位

Web 管理儀表板必須優先提供：

- 淨值、現金、已實現／未實現損益與回撤。
- 持倉、gross／net／asset／cluster／venue exposure。
- 策略、訊號、市場狀態、目標部位與實際部位差異。
- 未成交訂單、成交、拒單、取消、partial fill 與未知訂單狀態。
- 資料延遲、服務健康度、心跳、對帳差異與告警。
- 回測、paper、shadow、canary 與 live 的可辨識環境標示。
- 風控限制目前使用量與最近一次 `RiskDecision`。

允許的受控操作只包含：

- `pause-new-risk`：暫停新增風險。
- `close-only`：只允許降低或關閉部位。
- `cancel-all`：取消全部可取消訂單。
- `halt`：啟動外部 kill switch。
- 停用特定策略或交易標的。
- 提交設定變更請求，但不得在前端直接修改正式執行中的未版本化參數。

所有高風險操作必須具備 step-up authentication、明確環境顯示、二次確認、RBAC、原因欄位與 append-only audit log。`cancel-all`、`close-only`、`halt` 與緊急平倉不得因一般儀表板功能故障而失效，必須另有 CLI 或獨立操作通道。

### 1.3 手機端原則

MVP 不開發原生 Android 或 iOS App。Web 儀表板應採 responsive design，並可選擇做成 PWA，供手機執行唯讀監控、接收告警及有限的緊急控制。手機端不得提供高頻參數調校、臨時放寬風險上限或繞過審批的功能。

### 1.4 支援市場與分階段上線策略

本平台的長期產品範圍同時涵蓋：

1. **加密貨幣現貨市場**：24/7 運作，MVP 僅允許 long／flat，不使用槓桿、永續合約、期貨或自動借貸。
2. **股票現貨市場**：依交易所 session 運作，啟用時僅允許 cash-only、long-only，優先支援高流動性 ETF 與大型股票。

平台支援兩類資產，不代表第一個正式版本必須同時交易兩個市場。開發與資本部署必須採以下順序：

```text
共同事件模型、回測、風控、執行與監控核心
                    ↓
Phase A：高流動性加密貨幣現貨
research -> backtest -> replay -> paper -> shadow -> canary
                    ↓
Phase B：股票 ETF／大型股票
historical data -> backtest -> paper -> shadow -> canary
                    ↓
經獨立驗證後，才允許跨資產投資組合
```

**Phase A 是第一個端到端可交易 MVP。** 初始 universe 應限制於少量、流動性充分、資料品質可驗證，且符合所在地法令與交易平台條款的現貨交易對，例如 BTC 或 ETH 對法幣或經核准穩定幣的交易對。任何範例代號都不是推薦標的，實際 universe 必須由 point-in-time liquidity、spread、market-impact、venue risk 與資料品質篩選產生。

**Phase B 只能在 Phase A 的資料、對帳、告警、kill switch、paper／shadow 與 canary 驗收完成後啟動。** 股票模組還必須額外通過交易所行事曆、公司行動、盤前盤後、暫停交易、開盤跳空、lot size、券商限制與時區測試。

兩個市場可以共用：

- 不可變 domain events 與 event bus contracts。
- 資料品質框架、特徵介面與策略介面。
- 事件驅動回測、replay、run manifest 與 regression fixtures。
- 波動率目標、投資組合約束與獨立風險引擎框架。
- 訂單狀態機、冪等性、對帳、監控、告警與 Web 儀表板。

兩個市場禁止無條件共用：

- 年化因子、交易時段與 session 邏輯。
- 手續費、spread、滑價、market impact 與 participation 模型。
- 最小價格跳動、最小數量、最小名目金額與精度規則。
- 流動性門檻、資料新鮮度門檻、單一標的上限與 venue exposure。
- 策略參數、regime 門檻、持有期間、再平衡頻率與風險預算。

任何策略若要從加密貨幣移植到股票，或從股票移植到加密貨幣，必須建立新的策略版本、獨立研究報告與完整 promotion record；禁止僅更換 symbol 後直接啟用。

---

## 2. 明確非目標

第一版禁止將下列內容列為 MVP：

- 高頻交易、共置機房、微秒級延遲競爭。
- 選擇權、期貨、永續合約、槓桿代幣或保證金交易。
- 無限制放空、借券最佳化或複雜衍生品避險。
- 由 LLM 直接產生即時買賣訊號或直接呼叫交易 API。
- 未經人工核准的線上自我修改策略。
- 未經嚴格驗證的強化學習、自動超參數搜尋或黑箱深度模型。
- 以回測績效美化為目的調整風控、刪除虧損期間或挑選有利樣本。
- 任何形式的市場操縱、洗售、自成交、虛假掛單、拉抬出貨或規避交易所限制。

MVP 應先採用：

- 共用平台核心同時保留股票與加密貨幣介面，但**第一個端到端可交易 MVP 只啟用高流動性加密貨幣現貨**。
- 加密貨幣採 spot long／flat，不使用槓桿、永續合約、期貨、借貸或自動轉帳。
- 股票模組第一階段只完成歷史資料、回測、行事曆與 broker interface；通過 Phase A 驗收後，才啟用 cash-only／long-only 的 ETF 或大型股票 paper trading。
- 所有市場均只納入高流動性、資料品質可驗證且平台條款允許的標的。
- 分鐘級至小時級訊號，不追求超低延遲。
- 不得為了宣稱「多資產」而同時上線兩套尚未獨立驗證的市場 adapter。

---

## 3. 最高優先級安全規則

### 3.1 交易權限

- `live` 模式預設為關閉。
- Codex、測試程序與 CI **不得**存取正式交易憑證。
- API 金鑰若平台支援，必須關閉提款、轉帳與子帳戶管理權限。
- 模擬、影子與正式環境必須使用不同帳號、憑證、資料庫與訊息通道。
- 所有正式部署必須經 GitHub Environment 人工核准或等價機制。
- 正式系統必須提供一個不依賴策略程序的外部 kill switch。

### 3.2 Fail closed

遇到下列任何不確定狀態，系統不得新增風險，只能取消訂單、降低部位或進入人工處理：

- 市場資料過期、順序錯亂或來源不一致。
- 帳戶餘額、部位或未成交訂單無法對帳。
- 風控服務不可用。
- 交易所／券商回應不明確或訂單狀態未知。
- 時鐘偏差超出容許值。
- 資料庫寫入失敗。
- 風險參數缺失、無法解析或版本不一致。
- 策略輸出 NaN、無限值或超出定義域。

### 3.3 不可繞過的風控

- 策略層只能產生 `TargetPosition` 或 `OrderIntent`，不能直接送單。
- 每筆訂單必須通過獨立 `RiskEngine`。
- 禁止提供 `skip_risk_check=true`、`force_order=true` 等繞過旗標。
- 緊急平倉也必須經過專用 `EmergencyRiskPolicy`，以避免反向開倉、重複下單或超量平倉。
- 禁止為了讓測試通過而放寬風險參數。

### 3.4 時間與金額

- 系統內部一律使用 UTC。
- 市場行事曆與顯示層可以轉換為交易所當地時區。
- 金額、數量、價格與費用使用 `Decimal` 或等價定點數；禁止以二進位浮點數直接表示實際下單金額。
- 統計、矩陣與模型計算可使用浮點數，但轉成訂單前必須通過精度與最小交易單位正規化。

---

## 4. 環境與晉級流程

系統必須支援下列模式，且策略與風控邏輯盡量共用：

1. `research`：探索性研究，不可送單。
2. `backtest`：使用歷史事件與模擬成交。
3. `replay`：以原始事件順序重播特定日期或事故。
4. `paper`：使用券商／交易所模擬環境或內部模擬成交。
5. `shadow`：讀取即時資料並產生決策，但不送出訂單。
6. `canary`：使用受限資本與更嚴格限制的小額正式交易。
7. `live`：正式交易。

不得跨級晉級。標準路徑為：

`research -> backtest -> replay -> paper -> shadow -> canary -> live`

任何重大策略、資料、風控或執行變更都必須至少退回 `paper`；若改動會影響訊號定義、成交模型或風險邏輯，必須重新完成樣本外驗證。

---

## 5. 建議儲存庫結構

採用 monorepo。MVP 可在單一部署中運行，但程式碼邊界必須允許日後將市場資料、策略、風控、執行、對帳與控制 API 拆成獨立程序。禁止為了看似「微服務化」而過早引入不必要的網路複雜度；先維持模組化單體與清楚的事件介面。

```text
.
├── AGENTS.md
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CODEOWNERS
├── pyproject.toml
├── uv.lock
├── package.json                 # 前端 workspace；若未啟用可省略
├── pnpm-lock.yaml               # 前端鎖檔；不得與其他 JS 鎖檔混用
├── Makefile
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .codex/
│   └── config.toml
├── apps/
│   └── dashboard-web/           # React／Next.js、TypeScript、responsive／PWA
│       ├── app/
│       ├── components/
│       ├── lib/
│       ├── tests/
│       └── AGENTS.md
├── services/
│   ├── control-api/             # FastAPI；認證、查詢、命令與 WebSocket/SSE
│   ├── trading-runtime/         # 事件迴圈與生命週期協調，不含 UI
│   ├── market-data-worker/      # 行情、正規化、品質檢查與持久化
│   ├── reconciliation-worker/   # 帳戶、部位、訂單與成交對帳
│   └── alerting-worker/         # Email／LINE／Telegram／Slack 等通知 adapter
├── configs/
│   ├── base.yaml
│   ├── research.yaml
│   ├── paper.yaml
│   ├── shadow.yaml
│   ├── canary.yaml
│   ├── live.yaml
│   └── markets/
│       ├── crypto_spot.yaml      # 24/7 session、precision、fee、liquidity 與 venue limits
│       └── equities_cash.yaml   # exchange calendar、corporate actions 與 broker limits
├── src/trading_system/
│   ├── config/
│   ├── domain/
│   ├── data/
│   ├── features/
│   ├── strategies/
│   ├── regime/
│   ├── portfolio/
│   ├── risk/
│   ├── execution/
│   ├── brokers/
│   │   ├── crypto/              # exchange market data、orders、fills、balances
│   │   └── equities/            # broker market data、orders、fills、corporate actions
│   ├── engine/
│   ├── persistence/
│   ├── observability/
│   ├── control/                 # 控制命令、RBAC、audit 與 API contracts
│   └── cli/
├── tests/
│   ├── unit/
│   ├── property/
│   ├── integration/
│   ├── contract/                # 前後端與服務事件契約
│   ├── e2e/                     # Web 控制台與受控操作流程
│   ├── replay/
│   ├── regression/
│   ├── chaos/
│   └── fixtures/
├── research/
│   ├── notebooks/
│   ├── experiments/
│   └── reports/
├── data/
│   ├── README.md
│   ├── manifests/
│   └── schemas/
├── docs/
│   ├── architecture.md
│   ├── dashboard-spec.md
│   ├── control-api.md
│   ├── strategy-specs/
│   ├── risk-policy.md
│   ├── execution-policy.md
│   ├── model-governance.md
│   ├── incident-response.md
│   ├── runbooks/
│   ├── ADR/
│   └── RFC/
├── scripts/
├── infra/
│   ├── docker/
│   ├── migrations/
│   ├── reverse-proxy/
│   ├── monitoring/              # Prometheus／Grafana／alert rules
│   └── deployment/              # IaC、manifests、environment overlays
└── .github/
    ├── workflows/
    ├── ISSUE_TEMPLATE/
    └── pull_request_template.md
```

大型原始行情、交易資料、模型檔案與憑證不得提交至 Git。資料只提交 schema、manifest、checksum、產生腳本與小型測試 fixture。前端產物、套件快取與本機資料庫同樣不得提交。

---

## 6. 技術基線

除非 RFC 核准，採用以下基線：

- Python 3.12 或更新的受支援版本。
- `uv` 或等價工具管理鎖定依賴。
- `pydantic` 管理設定與事件 schema。
- `numpy`、`scipy` 與 `polars` 執行數值及資料處理。
- `pandas` 只允許出現在第三方相容邊界或必要研究工具。
- `scikit-learn` 用於基礎模型、校準與時間序列驗證。
- `cvxpy` 為可選投資組合最佳化器；必須有不依賴求解器的確定性 fallback。
- `asyncio`、`httpx` 與標準化 WebSocket 客戶端處理即時連線。
- Parquet + DuckDB 用於研究資料與可重現查詢。
- PostgreSQL 用於正式環境的訂單、成交、部位、設定版本與稽核紀錄。
- Redis 可用於短生命週期快取、rate limiting 或 pub/sub；不得作為訂單、成交、部位或正式風險狀態的唯一真實來源。
- FastAPI 作為內部 Control API；所有命令 endpoint 必須通過 RBAC、冪等鍵、CSRF／origin 防護與 audit logging。
- React／Next.js + TypeScript 作為 Web 管理儀表板基線；前端不得包含任何交易秘密或正式風控邏輯。
- OpenAPI／JSON Schema 作為前後端契約，breaking change 必須版本化並通過 contract tests。
- OpenTelemetry／Prometheus 相容 metrics、Grafana 儀表板與結構化 JSON logging。
- `pytest`、`hypothesis`、`ruff`、`mypy` 或 `pyright`。
- 前端使用 ESLint、TypeScript strict mode、單元測試與 Playwright 或等價 E2E 測試。
- Docker／Docker Compose 建立一致的本機、CI 與部署環境。
- 正式入口使用 TLS reverse proxy 或雲端 load balancer；Control API 不得直接暴露未加密連線。

任何新依賴必須說明：用途、授權、維護狀態、供應鏈風險、可替代方案與是否進入正式執行路徑。

---

## 7. 核心領域事件

所有事件必須不可變，至少包含：

```text
event_id
schema_version
source
venue
symbol
correlation_id
causation_id
event_time_utc
ingest_time_utc
sequence_number
payload_checksum
```

核心事件：

- `MarketStatus`
- `Quote`
- `TradeTick`
- `Bar`
- `CorporateAction`
- `FundingOrFeeUpdate`
- `DataQualityAlert`
- `FeatureSnapshot`
- `RegimeState`
- `Signal`
- `TargetPosition`
- `RiskDecision`
- `OrderIntent`
- `OrderSubmitted`
- `OrderAcknowledged`
- `OrderRejected`
- `OrderCanceled`
- `Fill`
- `PositionSnapshot`
- `AccountSnapshot`
- `PnLSnapshot`
- `KillSwitchChanged`
- `ControlCommandRequested`
- `ControlCommandApproved`
- `ControlCommandExecuted`
- `ControlCommandRejected`
- `ConfigurationChangeRequested`
- `ConfigurationChangeApproved`
- `UserSessionRevoked`
- `Heartbeat`

事件消費者必須具備冪等性。重複收到相同 `event_id` 或 `client_order_id` 不得造成重複下單、重複成交入帳或重複部位更新。

---

## 8. 資料工程與資料品質

### 8.1 原始資料原則

- 原始資料採 append-only。
- 每批資料保存來源、下載時間、參數、checksum、schema 版本與授權資訊。
- 清理資料不得覆寫原始資料。
- 必須區分 exchange timestamp、provider timestamp 與 ingest timestamp。
- 資料修補必須產生新版本與變更說明。

### 8.2 股票資料

必須處理：

- 股票分割、反向分割、股息、代號變更、合併、下市與暫停交易。
- 調整價與未調整價分離保存。
- Point-in-time 成分股清單，避免倖存者偏誤。
- 正確交易所行事曆、半日市、盤前盤後與休市。
- 不得以今日成分股回測過去整段期間。

### 8.3 加密貨幣資料

必須處理：

- 交易對上市、下架與代號變更。
- 最小價格跳動、最小數量、最小名目金額與精度規則的歷史版本。
- 交易所維護、API 中斷、異常成交、穩定幣脫鉤與流動性中斷。
- 同一資產在不同交易所的價格不得無條件視為可套利價格。

### 8.4 品質檢查

每次匯入或即時處理至少檢查：

- schema 與型別。
- timestamp 單調性。
- duplicate 與 sequence gap。
- OHLC 邏輯：`low <= open/close <= high`。
- 負價格、負成交量與不可能值。
- 缺失 bar、跨 session forward fill、極端跳價。
- 與第二來源的抽樣比對。
- 時鐘偏差與資料延遲。

資料品質分數低於門檻時，該標的必須標記為 `NOT_TRADABLE`。

### 8.5 跨市場共用核心與市場專屬設定

資料正規化後必須產生一致的 canonical schema，但不得抹除市場語意。每筆 market event 至少包含 `asset_class`、`venue`、`symbol`、`session_id`、`trading_status`、`price_precision`、`quantity_precision` 與來源時間戳。

市場專屬 metadata 必須版本化：

- 加密貨幣：venue、base／quote asset、24/7 session、maintenance window、fee tier、precision、minimum notional、stablecoin／custody exposure。
- 股票：MIC／exchange、currency、timezone、regular／extended session、lot size、corporate-action version、shortability 狀態與 broker restrictions。

禁止以同一份未分市場的 YAML 同時控制股票與加密貨幣正式交易。共同預設值可以繼承，但每個啟用市場必須有獨立、經驗證的 market profile 與 risk override。

---

## 9. 策略研究總則

每個策略必須有獨立規格文件：

`docs/strategy-specs/<strategy_id>.md`

至少包含：

- 經濟或行為假說。
- 可交易資產與排除條件。
- 所需資料與時間解析度。
- 特徵、訊號、部位與離場公式。
- 交易成本假設。
- 已知失效模式。
- 參數及其允許範圍。
- 回測與樣本外結果。
- 風險限制。
- 版本與負責人。

不得只以「歷史績效很好」作為策略理由。策略必須具有可解釋的風險溢酬、行為偏誤、流動性補償、市場結構或其他合理機制。

---

## 10. MVP 演算法架構

### 10.1 交易頻率

預設以 5 分鐘、15 分鐘、1 小時與日線建立特徵；實際下單頻率受成本門檻限制。MVP 不應在每個 tick 重新最佳化投資組合。

### 10.2 可交易標的篩選

每次再平衡前建立 point-in-time universe。標的需同時符合：

- 上市／交易歷史長度達最低要求。
- 最近一段期間成交量、成交額與有效報價達門檻。
- spread、跳價與市場衝擊估計可接受。
- 交易狀態正常。
- 無資料缺口或品質警告。
- 訂單名目金額可滿足最小交易單位。
- 不在人工封鎖清單。

第一個端到端可交易 MVP 的 universe 僅包含少量高流動性加密貨幣現貨交易對。候選標的必須通過 venue reliability、報價深度、成交額、spread、預估 market impact、precision metadata、stablecoin／quote-asset risk 與資料完整性檢查。

股票在 Phase B 才進入 paper trading，初始 universe 應限制於高流動性 ETF 或大型股票，並另行通過 exchange calendar、corporate actions、opening-gap、halt 與 broker-rule 驗證。禁止只因回測表現好而納入低流動性標的，也禁止在加密貨幣 MVP 尚未通過操作驗收前同時啟用股票 live path。

### 10.3 報酬與波動率

以對數報酬計算研究特徵：

```text
r_t = ln(P_t / P_{t-1})
```

短期波動率使用 EWMA：

```text
sigma_t^2 = lambda * sigma_{t-1}^2 + (1 - lambda) * r_t^2
```

年化因子必須依市場與 bar interval 明確設定，不能將股票交易時數直接套用至 24/7 加密貨幣。

所有除法加入明確、經測試的 epsilon；不得用 epsilon 掩蓋資料錯誤。

### 10.4 市場狀態分類

MVP 使用可解釋、規則式 regime detector，不使用 HMM 或深度模型。

核心量：

```text
trend_strength = abs(EMA_fast - EMA_slow) / ATR
vol_percentile = percentile_rank(realized_vol, rolling_window)
spread_score   = current_spread / median_spread
liquidity_score = rolling_notional_volume / required_notional
```

狀態：

- `TREND`：趨勢強度高、資料正常、波動率未進入危機區。
- `RANGE`：趨勢強度低、流動性足夠、spread 正常。
- `HIGH_VOL`：波動率位於高分位，但市場仍可交易。
- `CRISIS`：波動、spread、gap、資料品質或連線異常。
- `ILLIQUID`：流動性不足或市場衝擊過高。
- `UNKNOWN`：樣本不足或狀態不可判定。

`CRISIS`、`ILLIQUID`、`UNKNOWN` 預設禁止新增部位。

### 10.5 趨勢追蹤訊號

使用多期間時間序列動能：

```text
mom_h(t) = ln(P_t / P_{t-h})
adj_mom_h(t) = mom_h(t) / (sigma_t * sqrt(h))
trend_score = tanh(sum_h a_h * adj_mom_h(t))
```

要求：

- `sum_h a_h = 1`。
- 所有價格只使用決策時點已完成的 bar。
- 不得使用當前未完成 bar 的最終高低收。
- 訊號以 `[-1, 1]` 正規化。
- long-only 模式將負分數轉為減倉或空倉，不得反向放空。

### 10.6 突破訊號

以 Donchian channel 或等價區間突破：

```text
upper_t = max(high_{t-N}, ..., high_{t-1})
lower_t = min(low_{t-N}, ..., low_{t-1})
mid_t   = (upper_t + lower_t) / 2
breakout_score = clip((P_t - mid_t) / ((upper_t - lower_t)/2 + epsilon), -1, 1)
```

突破計算不得包含當前 bar 的 high/low，以避免同 bar 前視偏誤。

### 10.7 均值回歸訊號

僅在 `RANGE` regime 啟用：

```text
basis_t = rolling_vwap_or_ema(P, N)
residual_t = P_t - basis_t
z_t = residual_t / ewma_std(residual, N)
mean_reversion_score = -tanh(z_t / z_scale)
```

額外條件：

- spread 與預估成本在正常範圍。
- 不在重大 gap、停牌恢復或資料修補期間。
- 持有時間與 time stop 必須明確。
- 若趨勢強度超過門檻，立即停止新增逆勢部位。

### 10.8 橫截面動能

當 universe 足夠大且資料為 point-in-time 時，可加入橫截面動能：

```text
raw_rank_i = rank(vol_adjusted_return_i)
cs_score_i = map_rank_to_minus_one_plus_one(raw_rank_i)
```

MVP long-only：

- 僅持有排名前段且絕對趨勢為正的標的。
- 排名後段標的為零部位，不放空。
- 必須設置產業、資產群組與高度相關標的集中限制。

### 10.9 Regime-gated ensemble

合成訊號：

```text
trend_component = 0.60 * trend_score + 0.40 * breakout_score
range_component = mean_reversion_score

combined_score =
    quality_gate
    * liquidity_gate
    * (
        trend_gate * trend_component
        + range_gate * range_component
      )
```

其中：

- `quality_gate` 與 `liquidity_gate` 必須位於 `[0, 1]`。
- `trend_gate`、`range_gate` 不得同時完全開啟。
- 靜態權重為 MVP 預設。
- 動態權重只能使用截至 `t-1` 的樣本外績效，且必須 shrink toward static weights。
- 禁止根據最近幾筆盈虧無限制追高或切換策略。

### 10.10 預期報酬校準

策略分數不是報酬。必須在 rolling training window 內，以保守模型將分數映射成持有期間預期報酬：

```text
mu_hat_i,t = calibrator(score_i,t, regime_t, volatility_t)
```

MVP 可採用：

- 帶正則化的線性模型。
- Isotonic calibration。
- 分箱後的歷史條件平均，並使用 Bayesian／James-Stein shrinkage。

校準器只能在訓練資料擬合，並完整版本化。若樣本不足，`mu_hat` 必須 shrink toward zero。

### 10.11 交易成本門檻

每次交易前估算：

```text
expected_cost = fee + half_spread + slippage + market_impact + safety_buffer
expected_edge = abs(mu_hat) - expected_cost
```

只有在下列條件成立時才允許增加 turnover：

```text
abs(mu_hat) >= cost_multiplier * expected_cost
```

預設 `cost_multiplier >= 2.0`。壓力測試使用至少 2 倍正常成本與較差成交延遲。

### 10.12 波動率目標部位

單一標的未約束權重：

```text
raw_weight_i = signal_i * asset_risk_budget / max(forecast_vol_i, vol_floor)
```

投資組合預估波動率：

```text
portfolio_vol = sqrt(w' * Sigma * w)
```

縮放：

```text
scale = min(1, target_portfolio_vol / max(portfolio_vol, vol_floor))
w_scaled = scale * w
```

`Sigma` 應使用 EWMA covariance 或 shrinkage covariance。資料不足時採用較保守的對角矩陣或提高清算折扣，不得假設零相關。

### 10.13 約束式投資組合建構

若使用最佳化器，目標函數可為：

```text
minimize
    0.5 * (w - w_target)' Lambda (w - w_target)
    + turnover_penalty * ||w - w_prev||_1
    + concentration_penalty
```

約束至少包含：

```text
0 <= w_i <= max_asset_weight          # MVP long-only
sum(abs(w_i)) <= max_gross_exposure
min_net_exposure <= sum(w_i) <= max_net_exposure
cluster_exposure_k <= cluster_limit_k
venue_exposure_v <= venue_limit_v
estimated_turnover <= turnover_limit
```

若最佳化器失敗、不可行或逾時，必須使用確定性 fallback：逐標的 clipping、群組 clipping、總曝險 scaling。不得在求解失敗時直接沿用未約束權重。

### 10.14 Fractional Kelly 的限制用途

Kelly 只能作為額外上限，不得作為主要 sizing：

```text
kelly_fraction ~= mu_hat / variance_hat
allowed_fraction = min(vol_target_fraction, kelly_cap * max(kelly_fraction, 0))
```

預設 `kelly_cap <= 0.10`。估計值不穩定、樣本不足或 regime 改變時，Kelly 上限應趨近零。禁止 full Kelly。

### 10.15 離場規則

離場可以由下列事件觸發：

- 訊號反轉或衰減至退出門檻。
- 風險預算降低。
- regime 進入 `CRISIS`、`ILLIQUID` 或 `UNKNOWN`。
- volatility stop、trailing stop 或結構性 stop。
- 最大持有時間／time stop。
- 資料或連線異常。
- 人工或系統 kill switch。

Stop loss 不是風險控制的替代品。部位在進場前就必須符合最大可能損失與 gap risk 限制。

### 10.16 市場專屬演算法參數與跨資產啟用條件

策略介面可以共用，但每個 `strategy_id` 必須明確宣告 `supported_asset_classes`，並為每個市場保存獨立參數版本。至少分離：

- lookback、holding period、rebalance interval 與 signal decay。
- volatility estimator、annualization factor 與 vol floor。
- cost model、edge-to-cost threshold 與 minimum expected edge。
- regime thresholds、liquidity filters 與 stale-data thresholds。
- portfolio caps、turnover caps、order urgency 與 execution horizon。

跨資產投資組合只有在股票與加密貨幣分別完成樣本外驗證、paper、shadow 與 canary 後才能啟用。啟用前必須額外驗證：

1. 非同步 session 與週末曝險處理。
2. 股票休市期間加密貨幣劇烈波動造成的總風險偏移。
3. 跨資產 covariance 在壓力期失效或突然上升。
4. 不同 quote currency、FX 與 stablecoin 風險。
5. venue／broker failure correlation 與 custody concentration。
6. portfolio-level kill switch 是否能同時降低兩類資產風險。

在上述證據不足時，股票與加密貨幣必須以獨立 risk book、獨立 capital cap 與獨立 promotion status 運作。

---

## 11. 風險引擎規格

所有數值必須配置化、版本化並於每次決策記錄。以下是保守起始值，不是普遍適用的投資建議。

### 11.1 建議 MVP 預設值

```yaml
risk:
  target_annualized_vol: 0.08
  max_gross_exposure: 1.00
  max_net_exposure: 1.00
  max_asset_weight: 0.10
  max_correlated_cluster_weight: 0.25
  max_order_notional_pct_nav: 0.01
  max_participation_rate: 0.05
  max_daily_turnover: 0.50
  per_trade_risk_pct_nav: 0.0025

  soft_daily_loss_pct: 0.0075
  hard_daily_loss_pct: 0.0125
  hard_weekly_loss_pct: 0.025
  soft_drawdown_pct: 0.06
  close_only_drawdown_pct: 0.08
  hard_drawdown_pct: 0.10

  max_data_age_seconds: 120
  max_clock_skew_seconds: 2
  max_consecutive_order_rejects: 3
  max_unknown_order_states: 1
  max_feed_disconnect_seconds: 30
```

實際門檻必須依 bar interval、券商、交易所、標的流動性與資本規模調整。

共同風險預設值不得直接等同於市場啟用設定。至少建立以下兩個獨立 profile：

```yaml
risk_profiles:
  crypto_spot:
    asset_class: crypto
    session_model: continuous_24_7
    leverage_allowed: false
    short_allowed: false
    transfers_allowed: false
    venue_and_quote_asset_limits_required: true

  equities_cash:
    asset_class: equity
    session_model: exchange_calendar
    leverage_allowed: false
    short_allowed: false
    extended_hours_allowed: false
    corporate_action_checks_required: true
```

每個 profile 的數值上限必須由各自的歷史資料、成本模型、流動性與 operational risk 校準。股票與加密貨幣不得因使用同一策略名稱而自動繼承相同的 `max_asset_weight`、`max_data_age_seconds`、turnover 或 drawdown recovery 規則。

### 11.2 Pre-trade checks

每個 `OrderIntent` 依序檢查：

1. 系統模式與交易授權。
2. kill switch 狀態。
3. 市場是否開放與標的是否可交易。
4. 資料新鮮度、品質與 sequence。
5. 帳戶與部位對帳狀態。
6. 價格、數量、tick size、lot size、minimum notional。
7. 現金與可用餘額。
8. 單筆訂單上限。
9. 單一標的、群組、產業、資產類別與交易所曝險。
10. gross、net、槓桿與集中度。
11. turnover 與 participation rate。
12. 預估費用、spread、slippage 與 edge-to-cost ratio。
13. 日／週損失、drawdown 與風險縮放狀態。
14. 自成交、重複訂單、order loop 與訊息頻率。
15. 限價是否偏離 reference price 過多。
16. 下單後最壞情境曝險。

風控回傳必須是具理由的結構化結果：

```text
APPROVE
REJECT
RESIZE
CLOSE_ONLY
CANCEL_ALL
HALT
```

### 11.3 Drawdown scaling

預設階梯：

```text
drawdown < 4%      -> 100% risk budget
4% <= DD < 6%      -> 75% risk budget
6% <= DD < 8%      -> 50% risk budget
8% <= DD < 10%     -> close-only, cancel risk-increasing orders
DD >= 10%           -> cancel all, controlled flatten, HALT
```

恢復風險預算不得只因單日反彈。必須使用冷卻期、人工審查與新的 equity high watermark 規則。

### 11.4 Kill switch 觸發條件

至少包含：

- hard daily／weekly loss 或 hard drawdown。
- 風控服務失聯。
- 未知訂單狀態。
- 重複或爆量下單。
- 連續訂單拒絕。
- 帳戶與內部帳本不一致。
- market data stale 或 timestamp 回退。
- 交易 API 權限異常。
- PnL 突變超出可解釋範圍。
- 資料庫、訊息佇列或關鍵服務故障。
- 人工啟動。

Kill switch 必須支援：

- `CANCEL_NEW_RISK`
- `CANCEL_OPEN_ORDERS`
- `CLOSE_ONLY`
- `CONTROLLED_FLATTEN`
- `FULL_HALT`

不得把「市價全部平倉」當成所有事故的唯一處理，因為在流動性危機時可能放大損失。

### 11.5 對帳

至少每個事件循環與定期快照執行：

```text
internal_positions == broker_positions
internal_open_orders == broker_open_orders
internal_cash ~= broker_cash
sum(fills) -> positions -> PnL consistency
```

差異超過 rounding tolerance 時立即停止新增風險。

---

## 12. 執行引擎

### 12.1 訂單狀態機

```text
CREATED
-> RISK_APPROVED
-> SUBMITTING
-> ACKNOWLEDGED
-> PARTIALLY_FILLED
-> FILLED
-> CANCEL_PENDING
-> CANCELED
-> REJECTED
-> EXPIRED
-> UNKNOWN
```

任何非法狀態轉移必須拋出錯誤、記錄事件並觸發告警。

### 12.2 冪等下單

- 每個訂單使用不可重複的 `client_order_id`。
- 重試前先查詢券商／交易所訂單狀態。
- HTTP timeout 不代表訂單未送達。
- 對 `UNKNOWN` 狀態禁止再次下相同風險訂單，直到對帳完成。

### 12.3 訂單類型

MVP 預設：

- 正常進出場優先使用有價格保護的 limit order。
- 大單拆分為 TWAP 或 participation-capped child orders。
- 禁止無界限 market order。
- 緊急平倉可使用具最大滑價限制的 aggressive limit；只有在明確政策允許時才使用 market order。

### 12.4 價格與急迫度

```text
reference = mid_or_microprice
limit_price = reference + side * urgency_offset
```

`urgency_offset` 應考慮：

- spread。
- signal decay。
- 未完成目標部位。
- volatility。
- order book depth。
- participation rate。
- 剩餘執行時間。

不得以追價方式無限制 cancel/replace。必須限制每分鐘訊息數與最大重掛次數。

### 12.5 成交模型

回測至少支援：

- 手續費與 rebate。
- half-spread。
- volatility-dependent slippage。
- participation-based market impact。
- latency。
- partial fill。
- limit order non-fill。
- bar 內價格不確定性。

禁止假設所有限價單在觸價時 100% 成交。若只有 OHLCV，必須採保守成交順序或多種 bar path 壓力測試。

### 12.6 股票與加密貨幣 Adapter 邊界

執行引擎只能依賴統一的 broker／exchange port，不得在策略中直接呼叫特定平台 SDK。市場 adapter 必須各自處理：

- 加密貨幣：24/7 heartbeat、maintenance、rate limits、precision、minimum notional、fee tier、deposit／withdrawal 狀態與 venue-specific order semantics。交易程式不得取得提款或轉帳權限。
- 股票：exchange session、auction、regular／extended hours、halt、lot size、corporate actions、good-till 規則、券商 buying power 與帳戶限制。

相同 `OrderIntent` 在不同市場可以得到不同的合法化結果或被拒絕。Adapter 不得默默四捨五入到增加風險的方向；任何 quantity／price normalization 必須回傳原值、正規化值、規則版本與風險差異。

---

## 13. 回測與可重現性

### 13.1 回測引擎

- 必須事件驅動。
- 回測與 live 儘量共用 strategy、portfolio、risk 與 order state machine。
- 模擬 broker adapter 取代正式 adapter。
- 每次結果輸出完整 run manifest。

Run manifest 至少包含：

```text
run_id
git_commit
container_image_digest
config_hash
strategy_version
risk_policy_version
data_manifest_hash
universe_version
calendar_version
random_seed
dependency_lock_hash
start_time
end_time
```

### 13.2 禁止前視偏誤

- 決策時間 `t` 只能使用 `available_at <= t` 的資料。
- 基本面資料使用實際公布時間，不用報表期間結束日。
- bar-based 策略在 bar close 後才能使用該 bar 完整資訊。
- 執行價格必須在訊號形成之後。
- rolling normalization 與模型 fit 只能使用過去資料。
- 缺失值填補不得使用未來值。

### 13.3 Walk-forward

每個策略必須使用 expanding 或 rolling walk-forward：

```text
train -> validation -> test
shift forward
train -> validation -> test
...
```

時間長度依策略 horizon 設定，但必須：

- 保留完全未參與選模的 final holdout。
- 不得用 final holdout 反覆調參。
- 有重疊 label 時使用 purging 與 embargo。
- 報告每個 fold，而非只報告合併結果。

### 13.4 成本與壓力測試

至少測試：

- 基準成本。
- 1.5 倍成本。
- 2 倍成本。
- spread 擴大。
- 延遲增加。
- 20%／50% partial fill。
- 極端 gap。
- 資料中斷。
- 流動性下降。
- 相關性上升。

### 13.5 穩健性檢查

- 參數鄰域穩定性，不接受尖銳單點最佳值。
- 不同起訖日與再平衡時間。
- 不同標的子集合。
- block bootstrap／trade bootstrap。
- 隨機延遲與滑價 Monte Carlo。
- placebo signal 與時間位移測試。
- PnL concentration 分析。
- strategy decay 與 regime breakdown。
- benchmark 與簡單 baseline 比較。

---

## 14. 績效指標

不得只報年化報酬。至少包含：

- Net cumulative return。
- CAGR。
- Annualized volatility。
- Sharpe ratio。
- Sortino ratio。
- Calmar ratio。
- Maximum drawdown 與 drawdown duration。
- Expected shortfall／CVaR。
- Hit rate。
- Average win、average loss 與 payoff ratio。
- Trade expectancy。
- Profit factor。
- Turnover。
- Gross／net exposure。
- Fee、spread、slippage、impact 分解。
- Capacity estimate。
- PnL by asset、strategy、regime、venue、hour、day。
- Tail loss 與 worst-N periods。
- Live-vs-model slippage drift。

交易淨期望值：

```text
E[trade_net]
= P(win) * E[win]
- P(loss) * E[loss]
- E[fees + spread + slippage + impact]
```

勝率本身不是策略品質。低勝率高賠率與高勝率尾端風險策略都可能具有正或負期望值。

---

## 15. 晉級門檻

下列門檻是預設工程 gate，不是未來獲利保證。

### 15.1 Research -> Backtest candidate

必須：

- 假說與公式文件完成。
- 資料來源與 point-in-time 規則清楚。
- 無已知 look-ahead 或 survivorship bias。
- 單元測試涵蓋訊號邊界。

### 15.2 Backtest -> Paper

必須：

- 所有結果為費用後。
- 多個樣本外 fold 的 net expectancy 為正。
- 樣本外 Sharpe 預設目標 `>= 1.0`，且 bootstrap 下界大於零；若未達門檻，必須有明確風險委員會核准，不得靠敘事略過。
- 2 倍成本壓力下不出現災難性失效。
- 最大回撤低於 hard drawdown limit。
- 沒有單一標的、月份或少數交易貢獻過度集中；預設單一來源不得超過總 PnL 的 35%。
- 參數鄰域表現穩定。
- 與簡單 baseline 相比有合理增益。
- 全部 regression tests 通過。

### 15.3 Paper -> Shadow

必須：

- 加密策略至少連續 30 日；股票策略至少 20 個交易日，建議更長。
- 至少累積足夠訊號與成交樣本；預設 `>= 500` 個決策、`>= 100` 個模擬成交。
- 100% 訂單與部位可對帳。
- 無 Sev-1／Sev-2 未解事故。
- 實際模擬滑價與模型差異在容許範圍。

### 15.4 Shadow -> Canary

必須：

- 影子運行至少 14 日。
- 即時資料、策略決策與預期成交可重現。
- kill switch 演練完成。
- 斷線、重啟、重複事件、拒單與 partial fill chaos tests 通過。
- 正式憑證、權限、IP allowlist、告警與 runbook 審查完成。

### 15.5 Canary -> Live

- Canary 只能使用原規劃投入資本的一小部分；預設不超過 5%。
- Canary 風險門檻預設為正式規劃的一半。
- 至少運行 30 日或足夠交易樣本。
- 成交品質、風險、PnL attribution 與模型預期一致。
- 無重大對帳差異或未解事故。
- 由人類核准擴大；不得由程式自動提高資本。

---

## 16. 機器學習治理

MVP 先完成規則式 baseline。新增 ML 前必須證明：

- baseline 已穩定運行。
- ML 在嚴格樣本外與成本後有增量價值。
- 特徵可於即時環境準時取得。
- 模型能版本化、回滾與重現。

優先允許：

- Ridge／Elastic Net。
- Logistic regression。
- 經限制深度與正則化的 gradient boosted trees。
- Calibration 與 shrinkage models。

需要額外 RFC：

- 神經網路。
- 強化學習。
- 線上學習。
- 自動特徵生成。
- 自動策略搜尋。

禁止：

- 直接使用 LLM sentiment 作為未經驗證的 live signal。
- 模型在 live 環境自行重新訓練並立即部署。
- 使用 test／holdout 資料調參。
- 缺乏資料 lineage 的第三方特徵。

每個模型保存：

```text
model_id
training_code_commit
feature_schema_version
training_data_manifest
hyperparameters
random_seed
metrics_by_fold
calibration_report
artifact_checksum
approval_record
```

監控：

- feature drift。
- prediction drift。
- calibration drift。
- regime-specific performance。
- live error 與 latency。
- realized edge decay。

---

## 17. 測試規格

### 17.1 單元測試

涵蓋：

- 報酬、EMA、ATR、波動率與 covariance。
- 所有策略公式與 warm-up。
- rounding、tick size、lot size、minimum notional。
- PnL、費用、平均成本與 realized/unrealized PnL。
- 風險 limit 邊界。
- 訂單狀態轉移。
- 時區與交易日曆。

### 17.2 Property-based tests

至少驗證：

- 部位與成交帳本守恆。
- 平倉後不應殘留方向相反的超量部位。
- 風控縮小訂單後不得增加風險。
- 對相同輸入與 seed，結果完全一致。
- 任何 NaN／Inf 不得進入訂單層。
- `gross_exposure >= abs(net_exposure)`。
- 重複事件不改變最終狀態。

### 17.3 Integration tests

- Broker／exchange sandbox adapter。
- REST + WebSocket 斷線重連。
- Rate limit 與退避。
- 訂單送出、拒絕、取消、partial fill。
- 資料庫 migration。
- 服務重啟與狀態復原。

### 17.4 Replay tests

保存具代表性的市場事件：

- 急跌與快速反彈。
- 大幅 gap。
- 高 spread。
- 交易所維護。
- 資料重複與順序錯亂。
- 訂單 acknowledgment 遺失。
- 部分成交後斷線。

### 17.5 Chaos tests

注入：

- 網路延遲、封包遺失與 timeout。
- API 429／5xx。
- 資料庫短暫不可用。
- 時鐘偏差。
- 重複訊息。
- out-of-order events。
- stale market data。
- broker 回傳未知狀態。
- 磁碟空間不足。

所有 chaos case 必須證明系統 fail closed。

### 17.6 Control API 與 Web E2E tests

至少驗證：

- 未登入、過期 session、錯誤角色與缺少 step-up authentication 均被後端拒絕。
- 重複提交相同 idempotency key 不會重複執行控制命令。
- stale expected-state version 不得覆寫較新風險狀態。
- `paper`、`shadow`、`canary`、`live` 不會因前端狀態混淆而送往錯誤環境。
- dashboard 斷線重連後能由 REST snapshot 正確重建，不重播高風險命令。
- 前端 bundle、source map、log 與錯誤追蹤資料不含 secrets。
- 儀表板不可直接建立任意 broker order；所有操作只能映射到允許的後端命令。
- dashboard、Control API 或 Redis 故障時，交易 runtime 仍依風控政策安全運作或 fail closed。

---

## 18. 觀測性與告警

### 18.1 Metrics

至少輸出：

- market data lag。
- feed reconnect count。
- missing sequence count。
- strategy decision latency。
- risk check latency。
- order submit／ack／fill latency。
- order reject rate。
- cancel rate。
- partial fill rate。
- turnover 與 participation rate。
- gross／net／asset／cluster／venue exposure。
- realized／unrealized PnL。
- drawdown。
- estimated vs realized slippage。
- reconciliation differences。
- heartbeat 與 process uptime。

### 18.2 日誌

- 使用結構化 JSON。
- 每個決策保留 `correlation_id`。
- 不記錄 secret、完整 token、私鑰或可重建憑證的資料。
- 訂單、風控與參數變更為 append-only audit events。

### 18.3 告警級別

- `INFO`：正常狀態與非緊急通知。
- `WARN`：退化但仍安全運作。
- `SEV-2`：停止新增風險，需要人工處理。
- `SEV-1`：kill switch、未知訂單、重大對帳錯誤或資金風險。

告警必須包含：時間、環境、策略、帳號、標的、事件 ID、目前風險狀態與 runbook 連結。

### 18.4 Web 儀表板與 Control API

Web 儀表板必須是監控與控制介面，不得成為交易迴圈的必要依賴。最低頁面與功能：

- `Overview`：NAV、PnL、drawdown、風險模式、環境與系統健康。
- `Positions & Exposure`：持倉、曝險、集中度、目標與實際差異。
- `Orders & Fills`：完整訂單狀態機、成交、拒單、取消與未知狀態。
- `Strategies`：策略版本、啟用狀態、市場狀態、訊號與最近決策。
- `Risk`：限制、使用率、觸發紀錄、kill switch 與對帳差異。
- `Data & Services`：行情延遲、斷線、heartbeat、版本與 container digest。
- `Audit`：登入、設定請求、控制命令、核准者、原因與結果。

資料更新可使用 WebSocket 或 Server-Sent Events；斷線後必須以 REST snapshot 重建狀態，不得只依賴前端記憶。所有畫面必須明顯標示 `paper`、`shadow`、`canary` 或 `live`，其中 `live` 採不可與其他環境混淆的持續警示。

Control API 原則：

- 查詢與命令 endpoint 分離；預設角色只能讀取。
- 命令必須包含 `command_id`、操作者、原因、環境、預期狀態版本與 idempotency key。
- 使用 optimistic concurrency 或等價機制，避免以舊畫面覆寫新狀態。
- 禁止提供一般化的 `POST /orders` 給儀表板使用者直接建立任意正式訂單。
- 緊急操作只接受預先定義命令，並由後端再次驗證當前部位、訂單與風控狀態。
- 儀表板顯示資料不得被視為帳本真實來源；PostgreSQL ledger、broker/exchange state 與 reconciliation result 才是後端判斷依據。

### 18.5 通知與手機使用

系統可提供 Email、LINE、Telegram、Slack 或等價通知 adapter。通知通道只用於告警與跳轉至受保護的管理介面；禁止把 API key、完整帳戶資料或可直接重播的高權限操作連結放入訊息。

PWA 可快取靜態資產，但不得快取秘密、敏感 API 回應或過期後可能造成誤判的持倉與風險快照。行動裝置遺失時必須可撤銷 session。

---

## 19. 安全與秘密管理

- `.env` 永遠不得提交；只提交 `.env.example`。
- 正式 secrets 使用雲端 Secret Manager、Vault 或 GitHub Environment secrets。
- GitHub Actions 的 `GITHUB_TOKEN` 預設 read-only，個別 job 才提高最小必要權限。
- 第三方 Actions 固定至完整 commit SHA。
- 啟用 secret scanning、dependency review、Dependabot 或等價工具。
- 禁止 fork PR 存取正式 secrets。
- 正式部署優先使用 OIDC 換取短效憑證，而非長期雲端金鑰。
- 交易 API key 必須最小權限、分環境、定期輪替。
- 若供應商支援，使用 IP allowlist。
- 所有公開 log、錯誤報告與研究報告必須移除帳號 ID、API token 與個資。
- 建立 `SECURITY.md` 與秘密洩漏處理流程。
- 儀表板與 Control API 必須使用 TLS、secure／HttpOnly／SameSite cookies 或等價安全 token 儲存方式；禁止把 access token 放進 localStorage。
- 正式環境至少使用 MFA；`halt`、`close-only`、`cancel-all`、設定核准與資本上限變更使用 step-up authentication。
- 實作 RBAC，至少區分 `viewer`、`operator`、`risk_approver`、`administrator`；任何角色都不得因前端隱藏按鈕而取代後端授權。
- 公開 Web 入口與交易執行網路應隔離；交易服務不接受來自瀏覽器的直接網路連線。
- 所有 session、命令、設定變更與核准行為必須寫入 append-only audit log。
- 提供 session 撤銷、閒置逾時、登入 rate limit、暴力破解防護與安全標頭。

---

## 20. CI/CD 與 GitHub 規則

### 20.1 Pull Request 必跑

```text
format check
lint
type check
unit tests
property tests
integration tests with mocks
schema compatibility
migration validation
security scan
secret scan
backtest smoke test
risk regression suite
```

策略、風控、執行或資料 schema 變更還必須產生：

- baseline 與 candidate 比較報告。
- 交易數、turnover、成本、曝險、回撤與 tail loss 差異。
- 受影響的策略與環境。
- 回滾方案。

### 20.2 Branch protection

- 禁止直接 push 至 `main`。
- 至少一位人類 reviewer。
- `src/trading_system/risk/`、`execution/`、`brokers/`、`control/`、`services/control-api/`、`configs/live.yaml` 與正式部署設定由 CODEOWNERS 強制審查。
- 所有 required checks 通過。
- 已解決所有 review threads。
- 正式 release 使用簽章 tag。

### 20.3 正式部署

- 只部署不可變 container digest。
- 部署前執行 `live-preflight`。
- GitHub Environment 要求人工核准。
- 部署後先進入 `close-only` 或 shadow warm-up，完成資料與帳戶對帳後才允許新增風險。
- 交易後端與 Web 儀表板必須可獨立部署與回滾；儀表板部署不得重新啟動交易迴圈。
- Control API schema 變更先維持向後相容，再部署前端；禁止前端與後端同時以不可回滾的 breaking change 上線。
- 保留前一版本一鍵回滾能力。

---

## 21. Codex 工作規則

### 21.1 開始任何任務前

Codex 必須：

1. 讀取本 `AGENTS.md` 與目標子目錄內較具體的 `AGENTS.md`。
2. 檢查相關 strategy spec、risk policy、ADR、RFC 與測試。
3. 說明假設、影響範圍與驗證方式。
4. 優先做最小、可審查變更。

### 21.2 Codex 禁止事項

Codex MUST NOT：

- 執行正式下單、提款、轉帳或帳戶權限變更。
- 要求或輸出正式 API key。
- 使用 `--dangerously-bypass-approvals-and-sandbox` 或等價無保護模式。
- 修改 live 風控參數而不建立 RFC 與測試。
- 刪除失敗測試、事故 fixture 或不利回測期間以改善結果。
- 將 secrets、原始帳戶資料或大型市場資料提交至 Git。
- 執行破壞性 Git 指令，例如未經核准的 `reset --hard`、強制 push 或刪除遠端 branch。
- 在未說明的情況新增依賴、外部網路服務或 telemetry。
- 以未完成的 notebook 程式碼直接建立 live strategy。

### 21.3 建議 Codex 權限

- 預設使用 workspace-write sandbox。
- 網路存取預設關閉，只有安裝已核准依賴或查閱明確文件時才開啟。
- 任何 workspace 外寫入、secret 存取、部署或外部 side effect 必須人工核准。
- CI 中的 Codex／代理僅允許 read-only review，除非在隔離 branch 產生可審查 patch。

### 21.4 修改策略時

Codex 必須同時：

- 更新 strategy spec。
- 新增或更新單元測試。
- 驗證無 look-ahead。
- 執行成本後回測與壓力測試。
- 比較 baseline 與 candidate。
- 列出 PnL、turnover、drawdown、tail risk 與 concentration 的變化。
- 說明在哪些 regime 變好或變差。

不得只回報 Sharpe 或總報酬。

### 21.5 修改風控或執行時

必須：

- 建立 RFC。
- 列出新的 failure modes。
- 新增 property、integration、replay 與 chaos tests。
- 證明 fail-closed 行為。
- 提供回滾與事故處理步驟。

### 21.6 完成任務的回覆格式

Codex 最終回覆必須包含：

```text
Summary
Files changed
Assumptions
Risk impact
Tests executed and results
Backtest/replay evidence, if applicable
Known limitations
Rollback plan
```

不得聲稱「安全」、「可獲利」或「生產就緒」，除非列出對應證據與尚未完成的 gate。

---

## 22. 程式碼標準

- 公開函式與重要領域類別使用完整型別註記。
- 核心交易路徑禁止 catch-all 後忽略例外。
- 錯誤必須帶具體 context，不得只輸出 `something went wrong`。
- pure function 優先；副作用集中在 adapter／service 邊界。
- config 解析後不可任意變更；每次變更產生新版本事件。
- magic number 放入具名稱、單位與說明的設定。
- 所有單位明確，例如 seconds、bps、percentage、notional currency。
- 每個策略與風控決策可從輸入事件重建。
- 隨機程序固定 seed，並將 seed 寫入 run manifest。
- notebook 只用於探索；通過驗證的邏輯必須移入 `src/` 並測試。

---

## 23. 設定管理

設定優先序：

```text
code defaults
< base.yaml
< environment yaml
< deployment-time non-secret variables
< secret manager values
```

正式環境禁止使用未版本化 CLI 參數臨時覆寫風控。

設定至少分為：

```yaml
system:
  mode: paper
  timezone: UTC
  deterministic: true

data:
  providers: []
  max_age_seconds: 120
  quality_threshold: 0.99

strategy:
  enabled: []
  rebalance_interval: 15m
  signal_threshold: 0.20
  cost_multiplier: 2.0

portfolio:
  target_annualized_vol: 0.08
  covariance_method: ewma_shrinkage
  long_only: true

risk: {}
execution: {}

control:
  read_only_default: true
  require_mfa_in_live: true
  require_step_up_for:
    - cancel-all
    - close-only
    - halt
  allowed_origins: []

dashboard:
  environment_banner: true
  enable_pwa: true
  cache_sensitive_responses: false

notifications:
  enabled_channels: []
  sev1_requires_acknowledgement: true

observability: {}
```

啟動時輸出 redacted config 與 config hash。設定驗證失敗時禁止啟動。

---

## 24. CLI 與 Make targets

至少提供：

```bash
make setup
make format
make lint
make typecheck
make test
make test-property
make test-integration
make test-contract
make test-e2e
make test-replay
make test-chaos
make dev-up                 # 啟動 PostgreSQL、mock broker、API、runtime 與 dashboard
make dev-down
make api-dev
make dashboard-dev
make backtest CONFIG=configs/research.yaml
make report RUN_ID=<id>
make paper CONFIG=configs/paper.yaml
make shadow CONFIG=configs/shadow.yaml
make live-preflight CONFIG=configs/live.yaml
make reconcile
make cancel-all
make close-only
make halt
```

`make live` 不應存在，或必須要求多重人工確認、受保護環境與外部部署程序；避免單一終端機誤觸正式交易。

---

## 25. MVP 與市場擴充里程碑

### Milestone 0 — Repository bootstrap

- 專案骨架。
- lint、type、test、CI。
- config schema。
- domain events。
- GitHub branch protection 與 secrets policy。
- Docker Compose 本機拓樸：PostgreSQL、API、交易 runtime、dashboard 與 mock broker。
- Control API 與 dashboard skeleton，預設僅顯示模擬資料。

### Milestone 1 — Shared data foundation

- Canonical market event schema，保留 `asset_class`、venue 與 session 語意。
- 原始資料 manifest、checksum、schema version 與 data quality pipeline。
- symbol／instrument metadata interface。
- 加密貨幣與股票的 adapter contracts，但不要求同時啟用正式連線。
- 分離的 `crypto_spot` 與 `equities_cash` market profiles。

### Milestone 2 — Crypto spot data and deterministic backtester

- 一個高品質加密貨幣歷史與即時資料來源 adapter。
- 24/7 session、precision、minimum notional、maintenance 與 fee metadata。
- event loop 與 simulated exchange。
- fees、spread、slippage、partial fill、limit non-fill 與 latency。
- run manifest、replay 與 regression fixtures。
- BTC／ETH 等候選交易對只作為測試 universe；是否可交易由流動性與風險規則決定。

### Milestone 3 — Crypto baseline strategies

- buy-and-hold／cash benchmark。
- volatility-scaled trend。
- breakout。
- regime-gated mean reversion。
- static ensemble。
- 24/7 annualization、weekend behavior 與 venue-risk stress tests。

### Milestone 4 — Portfolio and independent risk

- covariance estimate。
- volatility targeting。
- concentration、quote-asset 與 venue limits。
- drawdown scaling。
- kill switch。
- reconciliation ledger。
- `crypto_spot` 專屬 pre-trade risk profile。

### Milestone 5 — Crypto paper trading

- exchange sandbox／paper adapter。
- FastAPI Control API、RBAC、audit log 與 versioned command model。
- Responsive Web dashboard：overview、positions、orders、risk、health 與 audit。
- order state machine、idempotency、reconnect、rate limit 與 unknown-state handling。
- Prometheus／Grafana operational dashboards、告警與 PWA／手機唯讀監控。
- 至少完成規格要求的連續 paper trading 期間與事故演練。

### Milestone 6 — Crypto shadow and canary

- real-time shadow decisions。
- live-preflight。
- incident runbooks。
- canary capital cap。
- human approval workflow。
- venue outage、stablecoin／quote-asset stress、weekend gap substitute、API drift 與 reconciliation drills。

### Milestone 7 — Equity ETF extension

只有在 Crypto Phase A 通過既定驗收後才能開始：

- 一個股票歷史資料來源與一個 broker sandbox adapter。
- exchange calendar、half-day、timezone 與 session tests。
- corporate actions、symbol changes、delisting 與 point-in-time universe。
- ETF／大型股票專屬 cost、slippage、opening-gap 與 halt model。
- `equities_cash` 專屬 risk profile。
- 股票策略重新校準；禁止直接沿用加密貨幣參數。
- 依序完成 equity backtest、replay、paper、shadow 與 canary。

### Milestone 8 — Cross-asset portfolio and advanced research

只在兩個市場分別穩定後考慮：

- 跨資產 covariance 與非同步 session 管理。
- 獨立 risk book 與 portfolio-level capital allocator。
- cross-sectional portfolio。
- market-neutral／shorting。
- derivatives。
- ML calibration。
- multi-venue execution。
- tax-aware or jurisdiction-specific modules。

---

## 26. 初始 GitHub Issues

1. `chore: bootstrap typed Python project and CI`
2. `feat: define immutable market and trading domain events`
3. `feat: implement versioned configuration and redacted config hashing`
4. `feat: implement append-only data manifest and quality checks`
5. `feat: add exchange calendar and symbol metadata interfaces`
6. `feat: build deterministic event-driven backtester`
7. `feat: add conservative fill and transaction-cost model`
8. `feat: implement volatility-scaled trend baseline`
9. `feat: implement regime detector and breakout signal`
10. `feat: implement regime-gated mean reversion`
11. `feat: implement portfolio volatility targeting and constraints`
12. `feat: implement independent pre-trade risk engine`
13. `feat: implement idempotent order state machine`
14. `feat: implement broker reconciliation and unknown-order handling`
15. `test: add property tests for ledger and risk invariants`
16. `test: add replay fixtures for gaps, disconnects, duplicate events and partial fills`
17. `ops: add metrics, dashboards, alerts and incident runbooks`
18. `security: add secret scanning, least-privilege workflows and CODEOWNERS`
19. `docs: add strategy, risk and execution specifications`
20. `release: define paper-to-shadow-to-canary promotion checklist`
21. `feat: add FastAPI control API with RBAC, audit log and idempotent commands`
22. `feat: build responsive Next.js trading operations dashboard`
23. `test: add control API contract and dashboard end-to-end tests`
24. `security: add MFA, step-up authentication and session revocation`
25. `ops: separate dashboard deployment from trading runtime deployment`
26. `feat: define crypto spot market profile and 24/7 session semantics`
27. `feat: implement crypto precision, minimum-notional and venue-limit validation`
28. `feat: add crypto exchange sandbox adapter with disabled transfer permissions`
29. `test: add venue outage, maintenance and quote-asset stress replays`
30. `docs: define crypto paper-to-shadow-to-canary acceptance criteria`
31. `feat: define equities cash market profile and exchange calendar semantics`
32. `feat: implement corporate-action-aware equity data adapter`
33. `test: add equity opening-gap, halt, half-day and symbol-change fixtures`
34. `release: gate equity paper trading on completion of crypto Phase A`
35. `research: validate cross-asset covariance and asynchronous-session risks`
36. `ops: define disaster recovery RPO, RTO, backup, restore and regional-failover policy`
37. `test: add backup restore, point-in-time recovery and trading-state reconstruction drills`
38. `security: implement credential-compromise detection, revocation and key-rotation runbook`
39. `feat: add venue-health, withdrawal-suspension, custody-risk and venue-block state model`
40. `feat: add stablecoin and quote-asset depeg detector with multi-source confirmation`
41. `test: add compound chaos scenarios for crash, outage, partial fill and unknown orders`
42. `ops: implement single-active-leader fencing and split-brain prevention`
43. `ops: define 24/7 on-call escalation, two-person live restart approval and communication fallback`
44. `test: add market-data consensus, symbol-mapping and stale-content-with-fresh-timestamp fixtures`
45. `release: gate canary and live on disaster-recovery and credential-compromise drills`

---

## 27. Pull Request 驗收清單

```markdown
- [ ] 變更目的與範圍清楚
- [ ] 無正式秘密、帳戶資料或大型市場資料
- [ ] 型別、lint、unit、property tests 通過
- [ ] 相關 integration/replay/chaos tests 通過
- [ ] 無 look-ahead、survivorship 或資料洩漏
- [ ] 成本、滑價與 partial fill 已納入
- [ ] 風險限制未被繞過或默默放寬
- [ ] Strategy/Risk/Execution 文件已更新
- [ ] Baseline 與 candidate 報告已附上
- [ ] 已說明 PnL、turnover、drawdown、tail risk 與 concentration
- [ ] 可重現 run manifest 已保存
- [ ] 已提供回滾方案
- [ ] 若影響 Control API／dashboard，OpenAPI contract 與 E2E 測試已通過
- [ ] 前端未包含秘密、券商憑證或可繞過後端風控的邏輯
- [ ] 若影響 live，已完成額外人工核准
- [ ] 若影響持久化或狀態復原，RPO／RTO、備份、restore 與 point-in-time recovery 證據已更新
- [ ] 若影響 leader election、排程或 runtime ownership，已證明不會發生 split-brain 或雙重送單
- [ ] 若影響秘密或帳戶權限，憑證撤銷、輪替、異常偵測與回復流程已測試
- [ ] 若影響 venue、quote asset 或 custody exposure，venue-health／depeg／withdrawal-suspension 規則與 replay 已更新
- [ ] 關鍵路徑變更已執行適用的 compound chaos scenario，而非只測單一故障
- [ ] 任何復原或 failover 後均先進入 `halt` 或 `close-only`，不得自動恢復新增風險
```

---

## 28. 事故處理最低要求

任何 Sev-1 事故：

1. 啟動適當 kill switch；狀況不明時預設為 `FULL_HALT` 或 `CLOSE_ONLY`。
2. 保存 logs、events、config、config hash、container digest、部署版本、身分驗證事件與外部回應。
3. 立即對帳實際帳戶、現金、未成交訂單、成交與部位；在完成前禁止新增風險。
4. 若涉及憑證、帳戶權限或可疑來源，立即撤銷相關 session／API key、阻斷來源並啟動金鑰輪替。
5. 若涉及資料遺失或持久化故障，保存損壞副本，依核准 runbook 執行 point-in-time recovery，並驗證事件鏈與帳本完整性。
6. 禁止在原因未明、對帳未完成或備援狀態未驗證時重新啟動交易。
7. 建立事故時間線、影響範圍、最壞風險曝險與所有人工操作紀錄。
8. 完成 root-cause analysis、contributing-factors analysis 與控制失效分析。
9. 新增可重現 replay fixture、compound chaos case 與 regression test。
10. 更新 runbook、告警、風控規則、RPO／RTO 或權限政策。
11. 正式恢復至少需要兩位具適當角色的人類核准；其中一位必須具 `risk_approver` 權限。
12. 經人工核准後，從 `paper`／`shadow` 重新晉級；不得直接回到原 live 資本與風險預算。

禁止刪改事故紀錄、備份、外部回應或不利市場資料以美化績效或掩蓋事故。

---

## 29. 極端情境、災難復原與營運韌性

本節規範超出一般回測、單一服務故障與日常風控的尾端事件。任何極端事件下的首要目標依序為：

1. 防止新增或重複風險。
2. 建立外部帳戶與內部帳本的可確認狀態。
3. 保存稽核證據與可重建事件鏈。
4. 恢復緊急控制、取消訂單與降低風險能力。
5. 經人工核准後才恢復一般交易。

「服務恢復」不等於「恢復新增風險」。任何 failover、restore、憑證輪替、區域切換或重大事故後，系統預設必須進入 `FULL_HALT` 或 `CLOSE_ONLY`，完成對帳、資料新鮮度驗證、風控健康檢查與人工核准後才可離開。

### 29.1 極端情境矩陣

至少建立下列 machine-readable scenario catalog；每個情境必須指定 owner、觸發條件、偵測來源、系統狀態轉移、允許操作、禁止操作、runbook、測試 fixture、最近演練日期與驗收證據。

| 類別 | 最低情境 | 預設安全反應 | 必要驗證 |
|---|---|---|---|
| 市場 | 瞬間暴跌、快速反彈、極端 gap | 停止新增風險，重算曝險與可成交性 | replay、stress |
| 流動性 | spread 急劇擴大、深度消失、market impact 暴增 | `ILLIQUID`，取消增加風險的訂單 | replay、fill stress |
| 相關性 | 多資產相關性在壓力期趨近一 | 使用 stressed covariance，縮減總風險 | portfolio stress |
| 訂單 | submit timeout、ack 遺失、未知狀態 | `UNKNOWN`，禁止重送同一風險 | integration、replay |
| 成交 | partial fill 後斷線或程序崩潰 | 以外部狀態對帳，不推測剩餘數量 | integration、restart test |
| Venue | API 全面失效、維護、rate limit、語意漂移 | venue `DEGRADED`／`BLOCKED`，停止新增曝險 | chaos、contract test |
| 託管 | 停止提款、帳戶凍結、破產疑慮 | 禁止增加 venue exposure，人工處理 | custody drill |
| Quote asset | stablecoin／法幣脫鉤或贖回中斷 | quote asset `CLOSE_ONLY`／`HALT` | multi-source replay |
| 資料 | bad tick、symbol mapping 錯誤、多來源共同錯價 | `NOT_TRADABLE`，隔離資料批次 | quality／consensus test |
| 持久化 | PostgreSQL 損壞、事件遺失、磁碟滿 | `FULL_HALT`，restore 後完整對帳 | DR drill |
| 基礎設施 | 雲端區域失效、DNS／TLS／網路分割 | 備援只建立安全狀態，不自動交易 | regional-failover drill |
| 協調 | split-brain、兩個 runtime 同時 active | fencing 拒絕其中一方，禁止雙重送單 | leader-election chaos |
| 資安 | API key 洩漏、帳戶接管、CI／runner 遭入侵 | 撤銷憑證、阻斷來源、cancel／halt | security drill |
| 人員 | SEV-1 無人確認或通知通道故障 | 保持 halt，逐級升級與備援通知 | on-call drill |
| 複合事故 | 市場崩跌＋斷線＋partial fill＋資料庫故障 | fail closed，外部對帳優先 | compound chaos |

不得以固定百分比保證涵蓋所有極端市場；情境參數必須依資產、venue、bar interval、資本規模與歷史／假設壓力校準，並包含超出歷史樣本的假設情境。

### 29.2 Disaster Recovery、RPO 與 RTO

必須建立 `docs/disaster-recovery.md`，至少定義：

- 系統與資料集的 RPO、RTO、owner、依賴與恢復順序。
- PostgreSQL point-in-time recovery、備份加密、checksum、保留期與跨故障域保存。
- 事件日誌、訂單、成交、部位、風控、設定與 audit record 的 restore 流程。
- 原始市場資料、研究資料與可再取得資料的不同復原優先級。
- 備份不可與 primary 使用相同單一故障域或相同可被一組憑證刪除的權限邊界。
- restore drill、regional-failover drill 與證據保存頻率。
- restore 後如何驗證 event chain、sequence、checksum、ledger conservation、外部帳戶與內部帳本一致性。

保守初始目標如下；正式數值可經 RFC 調整，但不得默默放寬：

```yaml
disaster_recovery:
  critical_trading_events_rpo_seconds: 0
  audit_events_rpo_seconds: 0
  research_market_data_rpo_minutes: 15
  establish_safe_known_state_rto_minutes: 15
  control_plane_rto_minutes: 30
  full_trading_resume: manual_approval_only
  backup_restore_drill_frequency_days: 30
  regional_failover_drill_frequency_days: 90
```

`critical_trading_events_rpo_seconds: 0` 表示已確認的訂單、成交、部位、風控與控制命令不得只存在於易失性記憶體。若無法證明 durable persistence，系統不得進入 canary 或 live。

RTO 的完成條件是「建立安全且可確認的狀態」，不一定是恢復交易。無法在 RTO 內安全重建時，應維持 halt 並由人工直接透過外部 venue／broker 介面處理。

每次 restore 至少驗證：

```text
external open orders == reconstructed open orders
external positions == reconstructed positions
external cash ~= reconstructed cash
fills -> positions -> PnL consistency
audit event chain and checksums are valid
no command or order is replayed twice
```

### 29.3 Single-active leader 與 split-brain 防護

任何可送出訂單或執行高風險控制命令的 runtime 必須具備 single-active ownership 與 fencing：

- leader lease 必須有單調遞增 fencing token 或等價機制。
- 舊 leader 即使網路恢復，也不得憑過期 lease 送單或寫入權威狀態。
- broker adapter、RiskEngine 與持久化邊界必須驗證有效 epoch／fencing token。
- 不得只依賴 in-memory mutex、單一 Redis lock 或 DNS 判斷 active instance。
- 網路分割時預設兩側都不得新增風險，除非能證明只有一側持有有效 fencing token。
- leader handoff 後必須先查詢外部訂單與部位，再處理待辦事件。

必須測試：雙 leader、lease 過期、時鐘偏差、資料庫延遲、網路分割、舊 leader 復活與 failover 過程中的訂單提交。

### 29.4 憑證外洩、帳戶接管與供應鏈事件

必須建立 `docs/runbooks/credential-compromise.md` 與可演練的 credential incident workflow。

最低偵測事件：

- 新增、刪除或提高 API key 權限。
- IP allowlist、withdrawal allowlist 或帳戶安全設定被修改。
- 來自未知來源的登入、token 使用或下單。
- 異常訊息速率、異常標的、異常名目金額或與策略無關的訂單。
- CI runner、GitHub Action、container registry、dependency lock 或簽章驗證異常。
- container digest、release tag 或部署身份與核准紀錄不一致。

最低反應：

1. `FULL_HALT` 或 venue-specific halt。
2. 取消可取消的未成交訂單；不得因無法確認狀態而重複送單。
3. 撤銷 session、API key、短效 token 與相關機器身份。
4. 阻斷可疑 IP、runner、workload identity 或部署來源。
5. 使用獨立乾淨通道輪替憑證；禁止在疑似被入侵的主機上產生新秘密。
6. 對帳全部帳戶、訂單、成交、轉帳權限與安全設定。
7. 保存證據並由人類核准後從 paper／shadow 重新晉級。

正式交易憑證必須：

- 禁止提款、轉帳、建立子帳戶或修改安全設定。
- 使用最小 symbol／account／IP 權限，若 venue 支援。
- 與 data-only、paper、shadow、canary、live 完全分離。
- 具版本、owner、建立時間、最後輪替時間與撤銷測試紀錄。
- 不得由同一個可部署程式碼的身份同時取得 secret-manager 管理權限。

### 29.5 Venue、託管與提款凍結風險

每個 venue 必須有版本化 `VenueHealthState`：

```text
HEALTHY
DEGRADED
TRADING_RESTRICTED
WITHDRAWALS_SUSPENDED
CUSTODY_AT_RISK
INSOLVENCY_SUSPECTED
BLOCKED
UNKNOWN
```

預設政策：

- `HEALTHY`：依一般限制交易。
- `DEGRADED`：降低 order rate、participation 與 venue cap。
- `TRADING_RESTRICTED`：只允許明確核准的降低風險操作。
- `WITHDRAWALS_SUSPENDED`：禁止增加該 venue 的淨資本與 custody exposure。
- `CUSTODY_AT_RISK`：取消新增風險訂單，降至 close-only，啟動人工審查。
- `INSOLVENCY_SUSPECTED`／`BLOCKED`／`UNKNOWN`：venue-specific `FULL_HALT`；不得自動轉入資產或以追價方式強制退出。

狀態判斷不得只依賴 venue 自己的單一 status endpoint；應整合 API 健康、提款狀態、公告、價格／深度異常、外部帳戶狀態與經核准的人工封鎖。

對 custody risk 的控制至少包含：

- 單一 venue 與關聯 venue 群組 capital cap。
- quote asset、custodian、銀行／支付管道與法域 concentration。
- 不因表面上可交易就忽略提款或資產可攜性風險。
- 禁止自動將資產轉入風險升高的 venue。
- 事故期間保存帳戶快照、交易紀錄與平台回應，以利法律、稅務與索賠需求。

### 29.6 Stablecoin 與 quote-asset 脫鉤

Stablecoin 與其他 quote asset 不得視為無風險現金。必須建立 `QuoteAssetRiskState`：

```text
NORMAL
WATCH
DEPEGGED
REDEMPTION_IMPAIRED
ILLIQUID
HALT
UNKNOWN
```

偵測至少使用：

- 兩個以上經核准且盡量獨立的價格來源。
- 偏離幅度、持續時間、spread、深度與可成交量。
- 跨 venue 價格差異。
- 贖回、存款、提款與鏈上轉帳狀態。
- 來源獨立性；多個 provider 共用同一上游不得視為多重確認。

可先採下列研究／paper 預設值建立測試，但正式門檻必須依 quote asset、venue 與流動性經 RFC 驗證：

```yaml
quote_asset_risk:
  watch_deviation_bps: 50
  close_only_deviation_bps: 150
  halt_deviation_bps: 300
  minimum_confirming_sources: 2
  confirmation_window_seconds: 60
```

任何來源不足、贖回狀態未知或資料互相矛盾時，狀態不得回到 `NORMAL`。脫鉤期間所有 PnL、NAV、曝險與成本報告必須同時以名目 quote value 與保守 reference value 表示。

### 29.7 市場資料共識與語意錯誤

除了 stale、duplicate、sequence gap 與極端跳價，資料品質框架還必須處理：

- bid 大於 ask、長時間 locked／crossed market、深度為零或不合理。
- 價格或數量 scale 突然改變 10 倍、100 倍或 precision metadata 變更。
- symbol mapping、base／quote、venue、contract 或 corporate-action 對應錯誤。
- timestamp 看似新鮮但 payload 重複舊快照。
- provider 回補或修訂歷史資料但未更新 manifest／version。
- 多個來源由同一上游產生的 correlated bad data。
- 股票調整價重複調整、加密貨幣不同交易對被錯誤合併。

重大價格異常應採「quarantine then verify」，不得直接 forward fill、winsorize 或刪除後繼續交易。資料共識不成立時，標的必須為 `NOT_TRADABLE`。

每個資料來源必須保存 `upstream_lineage`、independence group 與最近驗證時間；第二來源比對只有在來源真正獨立時才可作為確認證據。

### 29.8 Compound chaos scenarios

單一故障測試不足以代表真實事故。canary 前至少必須通過以下組合情境：

1. Flash crash + WebSocket 斷線 + REST 429。
2. Partial fill + submit timeout + runtime crash。
3. Unknown order + PostgreSQL 暫時不可用。
4. Venue outage + stablecoin／quote-asset depeg。
5. 重複事件 replay + RiskEngine restart + stale config version。
6. Dashboard／Control API compromise attempt + stale expected-state command。
7. 雲端區域失效 + venue 仍存在未成交訂單。
8. Clock skew + delayed acknowledgment + cancel race。
9. Split-brain + 兩個 runtime 嘗試處理相同 `OrderIntent`。
10. 極端 gap + 流動性枯竭 + controlled flatten 無法完全成交。
11. 資料來源共同錯價 + 新鮮 timestamp +正常 schema。
12. API key 異常使用 + alert channel 部分失效。

每個 scenario 必須證明：

- 不會重複送單或反向超量平倉。
- 無法確認時不新增風險。
- 外部帳戶狀態優先於內部推測。
- 事件、命令、人工操作與狀態轉移可完整稽核。
- 系統可以保持 halt，且不因自動重啟或 failover 恢復交易。

### 29.9 24/7 On-call、通知備援與重新啟動

24 小時系統必須有可驗證的人員與程序覆蓋，不得假設告警一定有人看到。

至少定義：

```yaml
incident_response:
  sev1_ack_minutes: 5
  sev2_ack_minutes: 15
  unresolved_sev1_action: full_halt
  live_restart_requires_two_person_approval: true
  post_incident_maximum_mode: shadow
  primary_and_backup_notification_channels_required: true
```

正式數值由組織能力與法規要求核准，但至少必須：

- 有 primary、secondary 與 escalation owner。
- SEV-1 使用兩個以上不同供應商或技術路徑的通知通道。
- 告警需有 acknowledgment、逾時升級與值班交接紀錄。
- 通知系統故障本身必須可被監控。
- `halt`、`cancel-all` 與外部帳戶檢查需有不依賴一般 Dashboard 的操作通道。
- live 重新啟動必須雙人核准，且一人為 `risk_approver`；原事故處理者不得單獨核准自己的恢復操作。
- 事故後初始最高模式為 `shadow`；是否重新進入 canary 必須依事故嚴重度與 promotion record 決定。

### 29.10 極端情境晉級 Gate

在進入 canary 前，除既有 gate 外還必須具備：

- 最近一次成功的 backup restore 與 trading-state reconstruction 證據。
- point-in-time recovery 後與外部帳戶完整對帳的證據。
- single-active leader、fencing 與 split-brain chaos test。
- 憑證外洩／撤銷／輪替演練。
- venue outage、withdrawal suspension、custody risk 與 quote-asset depeg replay。
- 至少一個 cloud-region 或主要依賴全面失效的演練。
- 全部 mandatory compound chaos scenarios 通過。
- on-call acknowledgment、升級與通知備援演練。
- recovery 後不會自動離開 halt／close-only 的測試。

任一證據過期、缺失、無法重現或最近一次演練失敗時，promotion verdict 必須為 `NOT_READY` 或 `INSUFFICIENT_EVIDENCE`。

---

## 30. 最終成功標準

本專案的成功不是「某次回測報酬最高」，而是：

- 任一決策可由版本化資料、設定與程式碼重建。
- 回測、paper 與 live 使用一致的核心邏輯。
- 交易成本與成交不確定性被保守建模。
- 任何單一服務故障不會無限制增加風險。
- Web 儀表板故障、斷線或重新部署不會中斷安全交易，也不會阻止外部 kill switch。
- 所有控制平面命令均經後端授權、冪等處理、版本檢查與完整稽核。
- 系統可快速停止、對帳與回滾。
- 策略在多個樣本外期間、成本壓力與市場狀態下仍具合理穩健性。
- 研究結果包含失敗、限制與不確定性，而非只有成功案例。
- 正式資本只能透過逐級 gate 與人類核准增加。
- 加密貨幣與股票各自擁有獨立的資料、參數、成本模型、風險 profile、promotion status 與驗收證據。
- 系統不會因架構支援多資產，就在第一版同時暴露兩個未成熟市場的正式交易風險。
- 股票 Phase B 只能在加密貨幣 Phase A 的操作安全與交易生命週期通過驗收後開始。
- 訂單、成交、部位、風控與 audit events 可在備份／failover 後重建，且與外部帳戶完成對帳。
- 系統具有明確 RPO／RTO、定期 restore 證據、跨故障域備份與 point-in-time recovery 能力。
- 任一時間最多只有一個具有效 fencing token 的 runtime 可以新增交易風險。
- 憑證外洩、帳戶接管、供應鏈異常與權限提升都能被偵測、撤銷、輪替並完整稽核。
- Venue 停止提款、custody risk、破產疑慮與 quote-asset 脫鉤不會被當成一般市場波動處理。
- 多來源共同錯價、symbol mapping 錯誤與 payload stale-but-timestamp-fresh 能使標的進入 `NOT_TRADABLE`。
- 系統已通過單一故障與 compound chaos scenarios，且所有復原路徑預設不自動恢復新增風險。
- 24/7 告警具有 acknowledgment、逾時升級、通知備援與雙人 live restart 核准。

在沒有足夠證據時，正確輸出是「不交易」。
