**Codex 自動交易系統開發提示詞—極端情境與營運韌性版**

本版已依更新後 AGENTS.md，加入 Disaster Recovery、RPO／RTO、備份復原、single-active／fencing、API key 外洩、交易所與託管風險、stablecoin 脫鉤、複合 chaos、24/7 on-call 與雙人恢復核准。

使用規則

每次開啟新的 Codex 任務時：

1. 使用獨立 Git branch 或 worktree。
2. 一次只執行下列一個提示詞。
3. Codex 完成後，先檢查 diff、測試結果和限制。
4. 通過人工審查後才合併。
5. 不要直接要求 Codex 執行 "live"、輸入正式 API key 或連接具有提款權限的帳戶。
6. 在 Milestone 5 以前，一律只使用 mock、historical、sandbox 或 paper environment。
7. 不要因測試失敗而要求 Codex刪除測試或放寬風控。
8. 不要同時開發股票正式交易與加密貨幣正式交易。
9. 任何災難復原或故障切換完成後，預設只能進入 HALT、close-only 或 shadow warm-up；不得自動恢復新增風險。
10. 任何涉及正式憑證、主從切換、leader election、備份復原、venue health、quote-asset risk 或重新啟動 live 的修改，都必須使用獨立 Issue、RFC、測試與人工審查。
11. 不得把單一 kill switch、單一資料來源、單一雲端區域、單一通知通道或單一管理者視為完整的極端事件控制。
12. Canary／live 前必須完成 restore drill、credential-compromise drill、compound-chaos drill、on-call escalation drill 與雙人重新啟動演練。

---

Prompt 0：首次完整檢查與工作拆分

這是交給 Codex 的第一個提示詞。此階段只分析，不修改程式碼。

請先完整閱讀儲存庫根目錄的 [AGENTS.md](http://AGENTS.md)，以及所有子目錄中的 [AGENTS.md](http://AGENTS.md)。

本次任務只進行 repository assessment 與 implementation planning，不要修改任何檔案，不要安裝依賴，不要建立正式交易連線，也不要要求任何 API key。

請執行以下工作：

1. 檢查目前 repository 的檔案、目錄、Git 狀態、設定檔、測試、CI 與文件。
2. 將目前實作逐項對照 [AGENTS.md](http://AGENTS.md) 的：
   - 安全規則
   - 建議儲存庫結構
   - 技術基線
   - MVP Milestone 0–6
   - 初始 GitHub Issues
   - Pull Request 驗收清單
   - 最終成功標準
3. 對每一項標記：
   - COMPLETE
   - PARTIAL
   - MISSING
   - BLOCKED
4. 找出會阻礙 Milestone 0 的問題。
5. 將工作拆成小型、可獨立審查的 GitHub Issues。
6. 為每個 Issue 提供：
   - Issue title
   - 目的
   - 範圍
   - 不在範圍內的事項
   - 預計修改檔案
   - 驗收標準
   - 必須執行的測試
   - 風險
   - 前置依賴
7. 提出建議執行順序。
8. 明確指出哪些工作需要 RFC、ADR 或人工決策。
9. 不得假設 [AGENTS.md](http://AGENTS.md) 中未明確決定的券商、交易所、雲端平台或正式資料供應商。
10. 不得聲稱系統已安全、可獲利或 production-ready。

輸出格式：

Repository status
[AGENTS.md](http://AGENTS.md) compliance matrix
Critical gaps
Proposed GitHub issues
Dependency graph
Recommended first issue
Human decisions required
Known risks

**新增極端情境與營運韌性盤點要求：**

1. 將目前實作額外逐項對照 AGENTS.md 的極端情境、Disaster Recovery、資安事件、venue／custody／quote-asset risk、compound chaos、on-call 與受控恢復條款。
2. 盤點是否存在明確 RPO、RTO、backup retention、point-in-time recovery、restore drill、跨故障域副本與備份加密。
3. 盤點是否具備 single-active runtime、leader lease、fencing token、split-brain 偵測與禁止雙主下單的證據。
4. 盤點 API key 外洩、帳戶接管、IP allowlist 變更、供應鏈攻擊與 container／artifact 完整性事件的偵測及處置。
5. 盤點交易所停止提款、帳戶凍結、venue insolvency、custody concentration、stablecoin 脫鉤與 quote-asset 流動性枯竭政策。
6. 建立 Extreme-resilience gaps 與 Compound-failure dependency graph，並將缺口拆成獨立 GitHub Issues。
7. 若任一交易狀態無法由 broker／exchange truth 重建，將最高允許環境標記為不高於 paper 或 shadow。

---

Prompt 1：建立 Milestone 0 專案骨架

只有在 Prompt 0 完成後執行。

請完整閱讀 [AGENTS.md](http://AGENTS.md)，然後實作 Milestone 0 — Repository bootstrap。

本次任務只建立安全、可測試、可重現的專案骨架，不實作任何真實交易策略，不連接正式券商或交易所，也不取得任何 API key。

必須完成：

1. 建立符合 [AGENTS.md](http://AGENTS.md) 的 monorepo 基本結構。
2. 建立 Python 3.12 typed project：
   - pyproject.toml
   - uv.lock 或可重現的 dependency lock
   - src/trading\_system package
   - tests 結構
3. 設定：
   - ruff
   - mypy 或 pyright
   - pytest
   - hypothesis
   - pre-commit
4. 建立版本化設定骨架：
   - configs/base.yaml
   - configs/research.yaml
   - configs/paper.yaml
   - configs/shadow.yaml
   - configs/canary.yaml
   - configs/live.yaml
   - configs/markets/crypto\_spot.yaml
   - configs/markets/equities\_cash.yaml
5. live 必須預設關閉；不得建立可直接送出正式訂單的命令。
6. 建立最小 Docker Compose 開發環境：
   - PostgreSQL
   - mock broker
   - control API skeleton
   - trading runtime skeleton
   - dashboard skeleton
7. 建立 Makefile，至少先實作目前可合理完成的：
   - make setup
   - make format
   - make lint
   - make typecheck
   - make test
   - make dev-up
   - make dev-down
8. 建立 GitHub Actions：
   - format
   - lint
   - type check
   - unit tests
   - secret scan
9. 建立：
   - [README.md](http://README.md)
   - [SECURITY.md](http://SECURITY.md)
   - [CONTRIBUTING.md](http://CONTRIBUTING.md)
   - CODEOWNERS
   - .env.example
   - .gitignore
   - pull request template
10. .env.example 只能使用假的 placeholder，不得包含真實秘密。
11. 建立最小 health endpoint 與 dashboard placeholder，只顯示 mock 資料。
12. 所有修改必須有測試。
13. 不得過早拆成多個複雜微服務；以模組化單體和清楚介面為主。
14. 不得建立 make live。

開始修改前，先簡短輸出：

- Assumptions
- Files expected to change
- Validation plan

完成後執行所有可用的 format、lint、typecheck 和 tests。

最終回覆必須包含：

Summary
Files changed
Assumptions
Risk impact
Tests executed and results
Known limitations
Rollback plan
Remaining Milestone 0 items

**新增 Repository bootstrap 韌性骨架：**

1. 建立 docs/disaster-recovery.md、docs/security-incident-response.md、docs/venue-risk-policy.md 與 docs/on-call-policy.md 的安全骨架；可先標示未決值，但不得虛構完成證據。
2. 在設定 schema 預留 disaster\_recovery、leadership、credential\_security、venue\_health、quote\_asset\_risk 與 incident\_response 區塊；預設值必須 fail closed。
3. 建立 tests/chaos/compound、tests/disaster\_recovery 與 tests/security\_incident 目錄。
4. 建立 backup／restore、leader fencing、credential revocation 與 venue block 的 mock interfaces；不得建立自動恢復 live 的路徑。
5. CI 增加 dependency／container security scan 與 workflow permission validation；任何供應鏈工具新增前必須記錄理由。

---

Prompt 2：核心領域事件與設定系統

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務只實作：

1. immutable domain events
2. versioned configuration
3. redacted configuration hashing

不要實作策略、回測績效最佳化、真實交易所連線或正式下單。

Domain events 至少包含 [AGENTS.md](http://AGENTS.md) 指定的共同欄位：

- event\_id
- schema\_version
- source
- venue
- symbol
- correlation\_id
- causation\_id
- event\_time\_utc
- ingest\_time\_utc
- sequence\_number
- payload\_checksum

至少實作以下核心事件的 typed schema：

- Quote
- TradeTick
- Bar
- DataQualityAlert
- FeatureSnapshot
- RegimeState
- Signal
- TargetPosition
- RiskDecision
- OrderIntent
- OrderSubmitted
- OrderAcknowledged
- OrderRejected
- OrderCanceled
- Fill
- PositionSnapshot
- AccountSnapshot
- PnLSnapshot
- KillSwitchChanged
- Heartbeat

要求：

1. 使用 frozen／immutable models。
2. 所有 timestamp 使用 timezone-aware UTC。
3. 金額、價格、數量及費用使用 Decimal。
4. 提供 schema\_version。
5. 提供 canonical serialization。
6. payload checksum 必須具確定性。
7. 相同輸入必須產生相同 canonical representation。
8. config schema 必須驗證 environment、market profile、strategy、risk、execution、control 與 observability。
9. config 驗證失敗時必須 fail closed。
10. 啟動時只能輸出 redacted config 與 config hash。
11. secret field 不得出現在 log、repr 或測試 snapshot。
12. 建立 unit tests 與 property-based tests：
    - immutable
    - serialization round trip
    - deterministic hash
    - UTC validation
    - Decimal precision
    - NaN／Inf rejection
    - secret redaction
    - duplicate event idempotency contract

不要修改 live risk limits，除非只是建立原規格中已有數值的 schema 與 validation。

完成後按照 [AGENTS.md](http://AGENTS.md) 的 Codex 最終回覆格式報告。

**新增事件與設定契約：**

1. 新增或預留 typed events：VenueHealthChanged、QuoteAssetRiskChanged、CredentialSecurityEvent、BackupCompleted、RestoreDrillCompleted、LeaderLeaseChanged、FencingTokenChanged、DisasterRecoveryStateChanged、OnCallEscalationEvent。
2. 所有安全與 DR 事件必須 append-only、具 correlation／causation、不可包含明文秘密，且可由 audit trail 重建。
3. 設定 schema 必須驗證 RPO／RTO、backup retention、restore-drill frequency、single-active、lease TTL、fencing、depeg thresholds、venue states、SEV-1 acknowledgement 與雙人 restart approval。
4. 任何未知、缺失或矛盾的 DR／leadership／credential／venue 設定必須阻止 canary／live 啟動。

---

Prompt 3：資料 Manifest 與資料品質管線

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務只實作 Milestone 1 的 shared data foundation：

1. append-only data manifest
2. canonical market event normalization
3. data quality pipeline
4. instrument metadata interfaces
5. 分離的 crypto\_spot 與 equities\_cash market profiles

不要下載大型歷史資料，不要提交大型資料檔，不要連接正式交易帳戶。

要求：

1. 每個 data batch manifest 至少記錄：
   - source
   - venue
   - asset\_class
   - symbol
   - download／ingest time
   - time range
   - schema version
   - checksum
   - row count
   - parameters
   - license metadata
2. 原始資料 append-only，清理結果建立新版本，不覆寫原始版本。
3. canonical schema 保留：
   - asset\_class
   - venue
   - symbol
   - session\_id
   - trading\_status
   - price\_precision
   - quantity\_precision
   - event／provider／ingest timestamps
4. 實作資料品質檢查：
   - schema and types
   - timestamp monotonicity
   - duplicate
   - sequence gap
   - OHLC invariants
   - negative／impossible values
   - missing bars
   - stale data
   - clock skew
   - extreme jumps
5. 品質低於門檻時輸出 NOT\_TRADABLE，不得只警告後繼續交易。
6. 實作 symbol／instrument metadata port，不綁定特定 provider SDK。
7. crypto 與 equity metadata 必須分開。
8. 建立小型 synthetic fixtures，不提交大型市場資料。
9. 建立 unit、property 與 regression tests。
10. 建立 docs/data-pipeline.md，說明 lineage、versioning、修補與失效模式。

完成前執行 format、lint、typecheck、unit tests 與 property tests。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報，並列出尚未選定的外部資料供應商決策。

**新增極端資料品質要求：**

1. 檢查 crossed／locked book、bid 大於 ask、零深度、價格 scale 突變、symbol mapping 錯誤、重複 corporate-action adjustment 與 timestamp 正常但 payload 為舊快照。
2. 第二來源驗證必須記錄 source lineage，避免兩個 provider 實際依賴同一 upstream 而被誤認為獨立確認。
3. stablecoin／quote-asset 價格與流動性檢查必須使用多來源確認；來源不足或互相矛盾時標記 UNKNOWN／NOT\_TRADABLE。
4. 建立 bad-tick、共同上游錯價、symbol collision、depeg 與 stale-snapshot fixtures。

---

Prompt 4：確定性事件驅動回測器

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務只實作 deterministic event-driven backtester 與 simulated exchange。

不要先實作複雜策略；只使用最小測試策略和 cash／buy-and-hold baseline 驗證引擎。

要求：

1. 回測和未來 paper/live 共用：
   - domain events
   - strategy interface
   - portfolio interface
   - risk interface
   - order state machine interface
2. simulated exchange 必須支援：
   - fees
   - half-spread
   - configurable slippage
   - participation-based impact
   - latency
   - partial fills
   - limit-order non-fill
   - conservative bar-path assumptions
3. 禁止假設限價單觸價即 100% 成交。
4. 決策時間 t 只能使用 available\_at <= t 的資料。
5. 訊號形成後才能成交。
6. 未完成 bar 不得使用最終 OHLC。
7. 所有隨機程序使用明確 random seed。
8. 每次 run 輸出 run manifest：
   - run\_id
   - git\_commit
   - config\_hash
   - strategy\_version
   - risk\_policy\_version
   - data\_manifest\_hash
   - universe\_version
   - calendar\_version
   - random\_seed
   - dependency\_lock\_hash
   - start\_time
   - end\_time
9. 相同 input、config、commit 和 seed 必須產生完全一致的結果。
10. 實作 replay fixture。
11. 實作測試：
    - no look-ahead
    - deterministic replay
    - partial fill
    - limit non-fill
    - fee accounting
    - slippage accounting
    - latency ordering
    - duplicate events
    - out-of-order rejection
    - ledger conservation
12. 建立 make backtest 與 make report。
13. 報告不得只包含總報酬；至少包含 turnover、fees、spread、slippage、exposure 和 drawdown。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報，並明確指出目前成交模型的限制。

**新增極端回測與 replay 能力：**

1. 支援 flash crash、30% 級 gap、spread 大幅擴張、order-book depth 歸零、venue outage、quote-asset depeg、withdrawal suspension 與跨資產 correlation spike 的 scenario fixtures。
2. 支援 compound scenario：partial fill + timeout + process crash + restart + reconciliation。
3. 恢復後必須從 external broker／exchange snapshot 重建訂單與部位；未完成對帳前不得產生新風險訂單。
4. 報告 worst-case fill、unfilled residual risk、time-to-safe-state 與是否觸發 close-only／halt。

---

Prompt 5：基礎演算法與策略

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務實作 Milestone 3 的可解釋規則式 baseline strategies。

僅實作：

1. cash benchmark
2. buy-and-hold benchmark
3. volatility-scaled trend
4. Donchian breakout
5. regime-gated mean reversion
6. static regime-gated ensemble

不要加入神經網路、強化學習、LLM sentiment、自動策略搜尋或線上自我調參。

開始寫程式前，先為每個策略建立：

docs/strategy-specs/<strategy\_id>.md

每份文件必須說明：

- 經濟或行為假說
- supported\_asset\_classes
- universe 和排除條件
- 所需資料
- 完整公式
- warm-up
- decision timing
- entry／exit
- 成本假設
- 參數範圍
- 已知失效模式
- 風險限制
- 版本

演算法要求：

A. Trend：

- multi-horizon log momentum
- volatility adjustment
- tanh normalization
- long-only 時負訊號代表減倉或空倉

B. Breakout：

- Donchian channel
- upper／lower 不得包含當前 bar
- 限制 score 至 [-1, 1]

C. Regime detector：

- TREND
- RANGE
- HIGH\_VOL
- CRISIS
- ILLIQUID
- UNKNOWN
- CRISIS／ILLIQUID／UNKNOWN 禁止新增風險

D. Mean reversion：

- 只在 RANGE 啟用
- residual z-score
- trend strength 超標時禁止逆勢新增部位
- 明確 time stop

E. Ensemble：

- 靜態權重
- quality gate
- liquidity gate
- trend gate 與 range gate 不得同時完全開啟

測試要求：

- 所有公式單元測試
- warm-up boundary
- missing values
- NaN／Inf rejection
- current-bar look-ahead test
- regime transition tests
- deterministic output
- property tests for bounded scores

回測要求：

1. 分別回測每個策略和 benchmark。
2. 使用費用後結果。
3. 執行 baseline、1.5x cost、2x cost。
4. 報告：
   - net return
   - annualized volatility
   - Sharpe
   - Sortino
   - maximum drawdown
   - turnover
   - fees／spread／slippage
   - tail loss
   - PnL concentration
   - regime breakdown
5. 不得因結果不好而調整 holdout 或刪除不利期間。
6. 不得聲稱策略具有正期望值，除非已完成 [AGENTS.md](http://AGENTS.md) 的樣本外 gate。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報。

**新增策略極端狀態限制：**

1. 任何策略在 CRISIS、ILLIQUID、UNKNOWN、VENUE\_BLOCKED、CUSTODY\_AT\_RISK 或嚴重 QUOTE\_ASSET\_DEPEG 狀態不得新增風險。
2. 策略不得假設 stop-loss 必然成交，也不得以回測中的理想平倉取代 gap／liquidity risk。
3. Strategy spec 必須列出 flash crash、depeg、venue outage、共同錯價與 covariance breakdown 下的失效模式。

---

Prompt 6：Walk-forward 與策略驗證框架

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務只建立嚴格的 strategy validation framework，不新增策略。

要求：

1. 實作 rolling 或 expanding walk-forward：
   - train
   - validation
   - test
   - shift forward
2. 保留 final holdout，並阻止程式在 tuning 階段讀取 final holdout。
3. 有重疊 label 時支援 purging 與 embargo。
4. 每個 fold 分別輸出結果，不只輸出合併績效。
5. 實作：
   - baseline cost
   - 1.5x cost
   - 2x cost
   - spread widening
   - additional latency
   - 20% partial fill
   - 50% partial fill
   - gap stress
   - liquidity decline
   - correlation increase
6. 實作：
   - parameter neighborhood stability
   - different start dates
   - block／trade bootstrap
   - randomized slippage Monte Carlo
   - placebo signal
   - shifted-signal test
   - PnL concentration
   - regime breakdown
7. 建立 machine-readable promotion report。
8. Promotion gate 必須 fail closed；缺少資料或證據時結果為 REJECT／INSUFFICIENT\_EVIDENCE。
9. 不要自動晉級到 paper。
10. 建立可重現 fixtures 和 tests。
11. 建立 docs/model-governance.md 或更新既有文件。

完成後執行一個小型 synthetic demonstration，證明 framework 能拒絕有 look-ahead 或不穩定的候選策略。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報。

**新增極端驗證矩陣：**

1. 加入 5x／10x spread、接近零流動性、30% gap、venue unreachable、quote-asset depeg、withdrawal suspension、共同資料錯價與 correlation 接近 1 的壓力測試。
2. 加入 compound stress，不得只逐一測試單一故障。
3. 每個 scenario 輸出：最大曝險、最大未完成訂單、最大對帳差異、time-to-close-only、time-to-halt、恢復後允許的最高環境。
4. 任何無法達到可確認安全狀態的情境，promotion 結論必須為 REJECT。

---

Prompt 7：投資組合與獨立風控引擎

這屬於高風險模組，因此提示詞必須要求 RFC。

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務實作 Milestone 4：

1. covariance estimation
2. volatility targeting
3. portfolio constraints
4. independent pre-trade RiskEngine
5. drawdown scaling
6. kill switch state model

開始修改前，先建立：

docs/RFC/<number>-portfolio-and-independent-risk-engine.md

RFC 必須列出：

- scope
- invariants
- trust boundaries
- failure modes
- fail-closed behavior
- configuration
- audit fields
- tests
- rollback plan
- unresolved decisions

風控要求：

1. Strategy 只能輸出 TargetPosition 或 OrderIntent。
2. Strategy 不得直接呼叫 broker adapter。
3. 每筆 OrderIntent 必須通過 RiskEngine。
4. 不得存在 skip\_risk\_check、force\_order 或其他繞過旗標。
5. RiskDecision 為結構化結果：
   - APPROVE
   - REJECT
   - RESIZE
   - CLOSE\_ONLY
   - CANCEL\_ALL
   - HALT
6. 實作 [AGENTS.md](http://AGENTS.md) 規定的 pre-trade check 順序。
7. 實作 crypto\_spot 和 equities\_cash 分離 risk profile。
8. MVP 維持 long-only、cash-only、no leverage。
9. 實作：
   - max asset weight
   - gross／net exposure
   - correlated cluster cap
   - venue cap
   - quote-asset cap
   - order notional cap
   - participation cap
   - turnover cap
   - cash availability
   - edge-to-cost threshold
   - drawdown scaling
10. covariance 資料不足時使用保守 fallback，不得假設零相關。
11. optimizer 失敗時使用 deterministic clipping／scaling fallback。
12. Fractional Kelly 只能作為額外上限，禁止 full Kelly。
13. 所有風控決策必須保存 input、config version、reason code 與 output。
14. 缺少 config、market data stale、reconciliation failure、NaN／Inf 或 unknown state 時必須禁止新增風險。

測試至少包含：

- unit boundary tests
- property-based invariants
- integration tests
- replay tests
- chaos tests
- risk resize never increases risk
- duplicate intent idempotency
- NaN／Inf rejection
- stale data fail closed
- missing config fail closed
- optimizer failure fallback
- drawdown boundary
- kill switch transitions

不得連接正式帳戶，不得修改 live 資本，不得宣稱 production-ready。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報，並附 RFC、failure-mode matrix 和 rollback plan。

**新增極端風控與資本保護：**

1. RiskEngine 必須納入 VenueHealth、CustodyRisk、QuoteAssetRisk、LeadershipState、RecoveryState 與 CredentialSecurityState。
2. 至少定義 HEALTHY、DEGRADED、WITHDRAWALS\_SUSPENDED、CUSTODY\_AT\_RISK、INSOLVENCY\_SUSPECTED、BLOCKED 等 venue 狀態及其風控動作。
3. withdrawals suspended 或 custody risk 升高時禁止增加該 venue exposure；insolvency suspected 時啟動 venue-level halt。
4. stablecoin／quote-asset depeg 必須支援 warning、close-only、halt 分級；門檻配置化、多來源確認且未確認時趨向保守。
5. DR 或 failover 後，直到 external reconciliation、leader fencing、config hash 與 credential status 全部確認，RiskEngine 只能回傳 REJECT／CLOSE\_ONLY／HALT。

---

Prompt 8：訂單狀態機、模擬 Broker 與對帳

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務實作：

1. idempotent order state machine
2. broker／exchange port
3. mock／sandbox adapter
4. reconciliation ledger
5. unknown-order handling

不要連接正式帳戶，不要要求正式 API key，不要提供提款或轉帳功能。

開始前建立 execution RFC，說明狀態機、冪等性、timeout 語意、重試政策、failure modes 和 rollback。

訂單狀態至少包含：

CREATED
RISK\_APPROVED
SUBMITTING
ACKNOWLEDGED
PARTIALLY\_FILLED
FILLED
CANCEL\_PENDING
CANCELED
REJECTED
EXPIRED
UNKNOWN

要求：

1. 非法狀態轉移必須拒絕、記錄並告警。
2. client\_order\_id 必須唯一。
3. HTTP timeout 不得被解讀成訂單未送達。
4. 重試前先查詢外部訂單狀態。
5. UNKNOWN 狀態禁止重送相同風險訂單。
6. duplicate event 不得造成重複訂單或重複入帳。
7. quantity／price normalization 不得向增加風險方向默默四捨五入。
8. normalization 必須記錄原值、結果、規則版本和差異。
9. 實作：
   - limit orders
   - bounded aggressive limit
   - TWAP child-order interface
   - participation cap
   - cancel／replace limit
10. 禁止無界限 market order。
11. reconciliation 必須比較：
    - internal positions vs broker positions
    - internal orders vs broker orders
    - internal cash vs broker cash
    - fills -> positions -> PnL
12. reconciliation mismatch 必須停止新增風險。
13. 實作 restart recovery。
14. 建立測試：
    - timeout after submit
    - duplicate acknowledgment
    - partial fill then disconnect
    - cancel race
    - out-of-order fill
    - unknown state
    - reconciliation mismatch
    - process restart
    - rate limiting
    - 429／5xx backoff
15. 所有事故 fixture 必須證明 fail closed。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報。

**新增執行韌性與 split-brain 防護：**

1. 建立 single-active execution invariant；只有持有有效 leader lease 與最新 fencing token 的 runtime 可送單。
2. 舊 leader、過期 lease、重複 runtime、網路分割或資料庫 failover 時，任何失去 fencing authority 的程序必須立即停止送單。
3. 加入 split-brain、雙 runtime、leader crash during submit、region failover with open orders、stale fencing token 測試。
4. 災難復原後不得依內部快照直接恢復交易；必須先查詢外部 open orders、fills、balances、positions 並完成對帳。
5. 若 venue 停止提款或疑似破產，adapter 必須阻止任何資金轉入與風險增加，且不得自動轉移資產。

---

Prompt 9：Paper Trading 垂直切片

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務建立完整但僅限 paper environment 的端到端垂直切片：

market data fixture／sandbox feed
-> data quality gate
-> features
-> regime
-> strategy
-> target position
-> portfolio
-> independent risk
-> order intent
-> simulated／sandbox broker
-> fill
-> ledger
-> reconciliation
-> PnL
-> metrics
-> Control API
-> dashboard

限制：

1. system.mode 必須固定為 paper。
2. live 必須保持 disabled。
3. 不得讀取正式憑證。
4. 不得實作提款、轉帳或槓桿。
5. 優先使用 deterministic mock feed；外部 sandbox adapter 可用介面或 feature flag 隔離。
6. Dashboard 不得直接呼叫 broker。
7. Dashboard 不得包含風控決策邏輯。
8. Dashboard 必須清楚顯示 PAPER 環境。
9. 所有控制命令必須由後端授權、驗證、冪等處理並寫入 audit log。

Control API 至少提供：

- health
- system mode
- positions
- orders
- fills
- PnL
- risk usage
- latest RiskDecision
- data freshness
- reconciliation status
- audit events

受控命令只先支援 paper：

- pause-new-risk
- close-only
- cancel-all
- halt

要求：

- RBAC skeleton
- idempotency key
- reason field
- audit log
- OpenAPI schema
- contract tests
- E2E tests
- dashboard 與 runtime 可獨立啟停
- dashboard 故障不得影響交易 runtime 或 halt command

建立 make paper，使其只啟動 paper configuration。

完成後執行端到端測試，證明：

1. 正常訊號可形成模擬成交。
2. stale data 被拒絕。
3. reconciliation mismatch 進入 close-only 或 halt。
4. 重複命令不會重複執行。
5. Dashboard 停止後 runtime 仍安全運行。
6. halt 不依賴一般 dashboard 頁面。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報。

**新增 Paper 垂直切片韌性驗證：**

1. 加入 mock backup、restore、leader failover、credential revoke、venue block、quote-asset depeg 與 on-call escalation 流程。
2. 證明 restore 或 runtime failover 後系統預設為 close-only／halt，只有在完整對帳與人工核准後才能回到 paper normal。
3. 證明兩個 runtime 同時啟動時最多只有一個具送單權限。
4. 證明 credential security event、withdrawal suspension 與 severe depeg 能阻止新增風險並產生可追蹤告警。

---

Prompt 10：監控、告警與事故演練

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務實作 paper environment 的 observability、alerts 與 incident drills。

要求：

1. 結構化 JSON logging，包含：
   - event\_id
   - correlation\_id
   - causation\_id
   - service
   - environment
   - strategy\_version
   - config\_hash
2. Prometheus metrics 至少涵蓋：
   - data freshness
   - event lag
   - strategy decision count
   - risk approvals／rejections／resizes
   - order states
   - fill latency
   - reconciliation mismatch
   - PnL
   - drawdown
   - exposure
   - service heartbeat
3. 建立 Grafana dashboard provisioning。
4. 建立 alert rules：
   - stale market data
   - feed disconnect
   - unknown order
   - repeated rejects
   - reconciliation mismatch
   - service heartbeat missing
   - database failure
   - drawdown thresholds
   - kill switch change
5. 建立 Sev-1／Sev-2 分級。
6. 建立 docs/incident-response.md。
7. 建立 runbooks：
   - stale data
   - exchange unavailable
   - unknown order
   - reconciliation mismatch
   - database unavailable
   - unexpected PnL
   - cancel-all
   - close-only
   - halt
8. 建立 replay／chaos tests：
   - network timeout
   - 429
   - 5xx
   - duplicate messages
   - out-of-order events
   - clock skew
   - database unavailable
   - disk-full simulation where practical
9. 所有測試都必須驗證 fail closed。
10. 不得把 market sell everything 當成所有事故的唯一回應。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報，並提供事故演練結果表。

**新增 DR、資安與複合事故監控：**

1. 新增 metrics／alerts：backup age、restore drill age、replication lag、leader lease、fencing token mismatch、multiple active runtimes、credential age、unexpected key creation、allowlist change、venue withdrawal status、custody state、depeg magnitude、independent-source count、on-call acknowledgement time。
2. 建立 credential-compromise、region outage、split-brain、venue insolvency suspicion、stablecoin depeg 與 restore failure runbooks。
3. 建立至少十組 compound chaos drills，例如市場崩跌 + feed stale + partial fill、資料庫失效 + unknown order、venue outage + depeg、region outage + open orders。
4. 每次演練都要保存 timeline、events、config hash、image digest、外部帳戶快照、time-to-safe-state 與人工確認紀錄。
5. 通知需至少兩種獨立通道；主要通道失效時必須升級，無人確認時保持 HALT。

---

Prompt 11：完整 Milestone 驗收

每完成一個 Milestone 後執行，不要求新增功能。

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務只做 Milestone [填入編號] 驗收與證據整理，不新增範圍外功能。

請：

1. 檢查該 Milestone 的每個要求。
2. 檢查所有相關 GitHub Issues 和 PR。
3. 執行所有必要的：
   - format
   - lint
   - type check
   - unit tests
   - property tests
   - integration tests
   - contract tests
   - E2E tests
   - replay tests
   - chaos tests
   - backtest smoke tests
   - risk regression tests
4. 將每項要求標記：
   - PASS
   - FAIL
   - INCOMPLETE
   - NOT APPLICABLE
5. 每個 PASS 必須提供證據：
   - file
   - test
   - command
   - output摘要
6. 檢查：
   - secrets
   - live credentials
   - risk bypass
   - look-ahead
   - survivorship bias
   - non-determinism
   - missing rollback
   - undocumented dependencies
7. 檢查所有失敗測試是否仍被保留。
8. 不得為了通過驗收修改門檻、刪除 fixture 或更改歷史資料範圍。
9. 若有任何 gate 未通過，結論必須為 NOT READY。
10. 不要自動進入下一 Milestone。

輸出：

Milestone
Overall verdict
Acceptance matrix
Commands executed
Test evidence
Security findings
Risk findings
Reproducibility findings
Missing evidence
Blocking issues
Recommended next issue

**新增 Milestone 極端韌性驗收：**

1. 檢查該 Milestone 是否已完成適用的 RPO／RTO、backup／restore、single-active、credential security、venue／quote-asset risk、compound chaos 與 on-call gates。
2. PASS 必須引用最近一次 restore drill、fencing test、credential revoke drill、venue／depeg replay 與 compound chaos 證據。
3. 任何過期演練、未解 split-brain、無法重建外部交易狀態、未撤銷高風險憑證或無人值班均為 BLOCKER。

---

Prompt 12：審查某個 Pull Request

請以嚴格 reviewer 身分審查目前 branch 相對於 main 的全部變更。

先完整閱讀 [AGENTS.md](http://AGENTS.md)，不要直接修改檔案。

審查重點：

1. 正確性與邊界條件。
2. 是否違反 [AGENTS.md](http://AGENTS.md) 的 MUST／MUST NOT。
3. 是否產生 look-ahead、survivorship bias 或資料洩漏。
4. 是否錯誤使用 float 表示實際訂單金額。
5. 是否存在風控繞過。
6. 是否在錯誤或未知狀態下繼續新增風險。
7. 訂單冪等性。
8. duplicate／out-of-order event。
9. timeout 與 unknown order handling。
10. reconciliation。
11. secret exposure。
12. 日誌是否洩漏敏感資料。
13. 測試是否充分。
14. 是否刪除失敗測試或不利 fixture。
15. 是否新增不必要依賴、服務或 telemetry。
16. 是否具回滾方案。
17. 文件、RFC、ADR、strategy spec 是否同步更新。
18. Dashboard 是否直接呼叫 broker 或包含可繞過後端的風控。
19. 是否有無法重現的隨機行為。
20. 是否錯誤聲稱 safe、profitable 或 production-ready。

依嚴重度輸出：

BLOCKER
HIGH
MEDIUM
LOW
NIT

每項 finding 必須包含：

- 檔案與行號
- 問題
- 可能後果
- 觸發情境
- 建議修正
- 應新增的測試

最後輸出：

Review verdict: APPROVE / REQUEST CHANGES
Required fixes
Optional improvements
Tests that should be rerun

**新增 Reviewer 檢查項目：**

1. 是否破壞 RPO／RTO、backup retention、restore 路徑或資料完整性。
2. 是否允許雙 active runtime、缺少 fencing、錯誤延長 lease 或在 failover 後自動恢復交易。
3. 是否洩漏 secret、降低 key 權限限制、繞過 IP allowlist／MFA／step-up，或缺少 credential revocation。
4. 是否忽略 withdrawals suspended、custody risk、venue insolvency、stablecoin depeg 或資料來源非獨立性。
5. 是否只測單一故障而沒有新增必要的 compound chaos regression。
6. 是否缺少 on-call、雙人 restart approval、演練證據或 time-to-safe-state 指標。

---

Prompt 13：修正審查問題

請完整閱讀 [AGENTS.md](http://AGENTS.md) 和目前 branch 的 review findings。

只修正下列已確認問題：

[貼上 BLOCKER／HIGH／MEDIUM findings]

要求：

1. 不擴大功能範圍。
2. 不進行無關重構。
3. 不刪除或弱化測試。
4. 不放寬 risk limits。
5. 每個修正都新增 regression test。
6. 若 finding 涉及風控或執行：
   - 更新 RFC
   - 更新 failure-mode matrix
   - 新增 property／integration／replay／chaos test 中適用的測試
7. 若修正改變 API：
   - 更新 OpenAPI schema
   - 更新 contract tests
   - 維持向後相容，或明確版本化
8. 完成後執行所有受影響測試以及完整 required checks。
9. 不得把測試標記為 skip 或 xfail 來迴避問題，除非 [AGENTS.md](http://AGENTS.md) 明確允許且有文件理由。

最終回覆依 [AGENTS.md](http://AGENTS.md) 格式，並額外加入：

Review findings resolved
Regression tests added
Findings not resolved and reasons

**新增修正要求：**

1. 若 finding 涉及 DR、leadership、credential、venue、quote-asset 或 on-call，必須同步更新相應政策文件、runbook、failure-mode matrix 與 drill fixture。
2. 不得以延長 timeout、關閉告警、跳過對帳或自動回到 live 方式掩蓋極端情境問題。

---

Prompt 14：回測候選策略的專用提示詞

每次修改演算法時使用。

請完整閱讀 [AGENTS.md](http://AGENTS.md) 與相關 strategy spec。

本次任務評估以下 candidate strategy change：

[描述修改內容]

先不要修改程式碼。先確認：

1. 經濟或行為假說是否合理。
2. 是否可能造成 look-ahead。
3. 所需資料在決策時間是否真的可取得。
4. 是否增加 turnover。
5. 是否增加 tail risk、concentration 或 venue exposure。
6. 是否可能只是在擬合特定期間。
7. 是否需要 RFC。
8. 是否在 MVP 允許範圍內。

若不符合 [AGENTS.md](http://AGENTS.md)，停止並解釋原因。

若符合，進行最小實作，並：

1. 更新 strategy spec。
2. 新增單元與 property tests。
3. 固定 random seed。
4. 使用相同 data manifest 比較 baseline 和 candidate。
5. 執行 walk-forward。
6. 保留 final holdout。
7. 執行：
   - normal cost
   - 1.5x cost
   - 2x cost
   - spread stress
   - latency stress
   - partial-fill stress
8. 報告：
   - net expectancy
   - net return
   - Sharpe
   - Sortino
   - Calmar
   - maximum drawdown
   - expected shortfall
   - turnover
   - fees
   - spread
   - slippage
   - market impact
   - concentration
   - capacity
   - regime breakdown
9. 分別列出改善和惡化的市場狀態。
10. 執行 parameter-neighborhood stability。
11. 不得只選擇最佳參數點。
12. 不得使用 final holdout 重新調參。
13. 若證據不足，結論必須為 REJECT 或 INSUFFICIENT\_EVIDENCE。
14. 不得自動部署至 paper、shadow、canary 或 live。

完成後依 [AGENTS.md](http://AGENTS.md) 格式回報。

**新增候選策略極端情境評估：**

1. 額外測試 flash crash、5x／10x spread、30% gap、zero liquidity、venue outage、quote-asset depeg、共同資料錯價、correlation spike 與策略訊號延遲。
2. 報告策略在 risk-off、close-only 與 unfilled exit 下的 residual exposure 與 tail loss。
3. 若績效依賴危機期間理想成交、提款可用、穩定幣恆定為 1 或資料來源永遠正確，candidate 必須 REJECT。

---

Prompt 15：Paper → Shadow 晉級檢查

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務只評估目前系統是否符合 Paper -> Shadow gate，不啟用 shadow，不修改正式設定。

請驗證：

1. Paper 運行期間是否達到 [AGENTS.md](http://AGENTS.md) 要求。
2. 決策樣本與模擬成交樣本是否足夠。
3. 訂單與部位是否 100% 可對帳。
4. 是否存在未解 Sev-1／Sev-2。
5. 實際模擬滑價與模型差異是否在容許範圍。
6. 每個決策是否可重現。
7. 所有 run manifest 是否完整。
8. kill switch 是否演練。
9. restart、disconnect、duplicate event、reject 和 partial-fill 測試是否通過。
10. secret、權限、RBAC、audit、alerts 和 runbooks 是否完整。
11. Dashboard 故障是否不影響 runtime。
12. halt 是否有獨立通道。
13. live credentials 是否完全不存在於本次環境。

輸出：

Gate verdict: PASS / FAIL / INSUFFICIENT\_EVIDENCE
Evidence matrix
Paper runtime statistics
Reconciliation evidence
Execution-quality evidence
Incident status
Security status
Missing evidence
Blocking issues
Required human approvals

不要自動變更 system.mode。

**新增 Paper → Shadow 韌性 gate：**

1. 最近一次 backup／restore smoke test、service restart recovery 與 external-state reconciliation 已通過。
2. single-active／fencing 測試已通過，無法產生雙重 paper orders。
3. credential revoke、venue outage、withdrawal suspension、depeg 與 compound chaos 演練已完成。
4. SEV-1 告警可由備援通知通道送達並在規定時間內確認。

---

Prompt 16：Shadow → Canary 晉級檢查

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務只評估 Shadow -> Canary readiness。

不要啟用 canary，不要要求正式 API key，不要修改資本上限。

請驗證：

1. Shadow 連續運行期間。
2. 即時資料品質。
3. 訊號、部位、風控決策與預期成交是否可重現。
4. live-preflight 是否完整。
5. kill switch 演練結果。
6. venue outage、API drift、maintenance、quote-asset stress 和 reconciliation drills。
7. 正式部署是否使用 immutable image digest。
8. GitHub Environment 是否要求人工核准。
9. 正式 API key 設計是否：
   - 禁止提款
   - 禁止轉帳
   - 最小權限
   - 與 paper／shadow 分離
10. canary capital cap 是否不超過規格限制。
11. canary risk limits 是否比規劃 live 更嚴格。
12. rollback 與 incident runbook 是否經演練。
13. 是否仍有任何未知訂單或對帳問題。

輸出：

Gate verdict
Evidence matrix
Operational-risk assessment
Execution-risk assessment
Security assessment
Canary configuration review
Missing evidence
Blocking issues
Human approvals required

不得自行啟用 canary。

**新增 Shadow → Canary 硬性 gate：**

1. 定義並驗證 RPO／RTO；完成實際 restore drill，而不是只確認備份存在。
2. 完成 region／host failure、single-active、fencing 與 split-brain 演練；failover 後保持 close-only／halt。
3. 完成 API key compromise drill：偵測、撤銷、輪替、取消訂單、對帳、權限與 allowlist 驗證。
4. 完成 venue outage、withdrawal suspension、custody risk、insolvency suspicion 與 stablecoin depeg 演練。
5. 完成 compound chaos 與 on-call escalation；Canary restart 需要至少兩位授權人員核准。
6. 任一演練無證據、證據過期或存在未解重大 finding，Gate verdict 必須 FAIL。

---

Prompt 17：專案目前做到哪裡

日後可定期用這個提示詞掌握進度。

請完整閱讀 [AGENTS.md](http://AGENTS.md)，並檢查目前 repository 的實際狀態。

不要修改檔案。

請按照 Milestone 0–8 建立進度矩陣，每個項目標記：

- COMPLETE
- PARTIAL
- MISSING
- BLOCKED
- DEFERRED BY DESIGN

每個 COMPLETE 必須引用實際：

- file
- test
- CI check
- report
- run manifest
- RFC／ADR
- operational evidence

另外列出：

1. 目前最高已完成 Milestone。
2. 當前允許的最高環境：
   - research
   - backtest
   - replay
   - paper
   - shadow
   - canary
   - live
3. 尚未通過的 promotion gates。
4. 所有已知安全風險。
5. 所有已知研究限制。
6. 所有尚未解決的 Sev-1／Sev-2。
7. 是否存在未提交、未測試或未文件化的關鍵修改。
8. 下一個最小且最重要的 GitHub Issue。
9. 哪些工作現在不應該做，以避免過度工程或超出 MVP。

輸出：

Current milestone
Maximum permitted environment
Progress matrix
Completed evidence
Blocking gates
Known risks
Deferred scope
Recommended next issue

**新增進度與最高允許環境判定：**

1. 額外建立 Resilience maturity matrix：Data recovery、Execution leadership、Credential security、Venue／custody、Quote asset、Compound chaos、On-call。
2. 列出最近一次成功的 restore drill、split-brain drill、credential drill、venue／depeg drill 與 compound chaos drill 日期與 commit／artifact evidence。
3. 任何關鍵演練未完成時，Maximum permitted environment 不得高於 shadow；若交易狀態無法重建，則不得高於 paper。

---

Prompt 18：判定 Phase A 是否完成

請完整閱讀 [AGENTS.md](http://AGENTS.md)。

本次任務判定 Crypto Phase A 是否達到完成標準。

不要修改程式碼，不要啟用 live，也不要提高資本。

請逐項驗證：

1. 可重現資料與 run manifest。
2. 無 look-ahead、survivorship bias 或資料洩漏。
3. 確定性事件驅動回測。
4. 保守費用、spread、slippage、impact、latency、partial fill 和 non-fill。
5. baseline strategies 與完整 strategy specs。
6. walk-forward、final holdout 和壓力測試。
7. portfolio constraints 與 independent RiskEngine。
8. fail-closed。
9. order idempotency 和 unknown-state handling。
10. reconciliation ledger。
11. paper 與 shadow acceptance evidence。
12. kill-switch、replay、chaos 和 incident drills。
13. Control API、RBAC、audit 和 dashboard isolation。
14. observability、alerts 和 runbooks。
15. canary gate 證據。
16. 所有 required CI checks。
17. 所有 BLOCKER／HIGH findings 已關閉。
18. 所有 promotion 都有人類核准。
19. 策略是否只在成本後、多個樣本外期間和壓力測試下呈現合理穩健性。
20. 是否仍存在尚未量化的 venue、custody、stablecoin 或 operational risk。

結論只能是：

- PHASE\_A\_COMPLETE
- NOT\_COMPLETE
- INSUFFICIENT\_EVIDENCE

除非每項都有證據，否則不得使用 PHASE\_A\_COMPLETE。

即使 Phase A 完成，也不得聲稱保證獲利。

輸出：

Final verdict
Success-criteria matrix
Promotion-gate matrix
Safety evidence
Strategy evidence
Operational evidence
Outstanding limitations
Deferred Phase B items
Human decision required

**新增 Phase A 完成判定項目：**

1. 明確 RPO／RTO、跨故障域加密備份、point-in-time recovery 與成功 restore drill。
2. single-active、leader lease、fencing token、split-brain prevention 與 region／host failover 證據。
3. API key compromise、帳戶接管、allowlist change、credential revoke／rotate 與供應鏈完整性演練。
4. venue withdrawal suspension、custody risk、insolvency suspicion、stablecoin／quote-asset depeg 與多來源價格確認。
5. mandatory compound chaos scenarios 與 time-to-safe-state 指標。
6. 24/7 on-call、備援通知、SEV-1 acknowledgement、雙人 canary／live restart approval。
7. 任何一項缺乏證據時，結論不得為 PHASE\_A\_COMPLETE。

---

**Prompt 19：Disaster Recovery、RPO／RTO 與備份復原**

1. 請完整閱讀 AGENTS.md。本次任務只設計並實作 Disaster Recovery，不啟用 live、不提高資本。
2. 開始前建立 DR RFC，明確定義每一類資料的 RPO、RTO、備份頻率、retention、加密、故障域與責任人。
3. 訂單、成交、部位、現金、風控決策、設定版本與 audit events 的目標應接近 RPO = 0；任何較寬鬆目標都必須有書面風險接受。
4. 實作 PostgreSQL point-in-time recovery、不可變備份、跨故障域副本、checksum／integrity validation 與最小權限 restore credentials。
5. 建立 restore drill：從備份建立隔離環境，重播事件，向 broker／exchange 查詢外部真實狀態，完成 orders／fills／positions／cash 對帳。
6. 恢復完成後系統必須保持 HALT 或 close-only；不得因資料庫可讀就自動恢復下單。
7. 測試 backup corruption、missing WAL／log、partial restore、old config、region unavailable、DNS failure、TLS failure 與 message loss。
8. 輸出 DR evidence matrix、實測 RPO／RTO、資料差異、time-to-safe-state、未達標項目與 rollback plan。

---

**Prompt 20：Single-active、Leader Lease、Fencing 與 Split-brain**

1. 請完整閱讀 AGENTS.md。本次任務只實作交易執行 leadership safety。
2. 建立 RFC，定義 single-active invariant、leader election、lease TTL、renewal、quorum、fencing token、clock assumptions 與 failure modes。
3. 只有持有目前有效且最新 fencing token 的 execution runtime 可呼叫 broker／exchange submit／cancel／replace。
4. 舊 leader 即使網路恢復也不得重新取得寫入能力，除非經新的 lease 與 fencing authority。
5. 測試雙 runtime 同時啟動、network partition、DB failover、lease renewal delay、clock skew、leader crash during submit、stale token、region failover。
6. 每個測試必須證明最多只有一個送單者，且不確定時全部停止新增風險。
7. failover 後必須外部對帳並保持 close-only／halt；禁止自動恢復正常風險。

---

**Prompt 21：API Key 外洩、帳戶接管與供應鏈安全演練**

1. 請完整閱讀 AGENTS.md。本次任務建立 credential-compromise 與 account-takeover response，不使用任何真實 secret。
2. 建立 security RFC 與 runbook，涵蓋 unexpected key creation、權限提升、IP allowlist 變更、異常來源、MFA／session compromise、CI runner compromise、dependency／container tampering。
3. 實作事件分級與自動動作：停止新增風險、cancel open orders、revoke／rotate credentials、block affected identity、保存證據、外部對帳。
4. 正式交易 key 必須禁止提款、轉帳與帳戶管理，並與 data-only key、paper key、CI 完全分離。
5. 測試 secret 出現在 log／exception／source map、舊 key 未失效、allowlist 被修改、container digest 不符、GitHub workflow 權限過大。
6. 重新啟用 canary／live 前必須完成兩人核准、clean credential issuance、image integrity verification、完整對帳與 paper／shadow re-promotion。

---

**Prompt 22：Venue、Custody 與 Stablecoin／Quote-asset 風險**

1. 請完整閱讀 AGENTS.md。本次任務建立 venue health 與 quote-asset risk policy，不連接正式資金。
2. 定義 venue 狀態：HEALTHY、DEGRADED、WITHDRAWALS\_SUSPENDED、TRADING\_ONLY、CUSTODY\_AT\_RISK、INSOLVENCY\_SUSPECTED、BLOCKED。
3. 定義 stablecoin／quote-asset 狀態：NORMAL、WARNING\_DEPEG、SEVERE\_DEPEG、REDEMPTION\_UNAVAILABLE、LIQUIDITY\_COLLAPSE、UNKNOWN。
4. 門檻必須配置化、版本化、依多個真正獨立來源確認；來源不足或相互矛盾時採 UNKNOWN 並禁止新增風險。
5. withdrawals suspended 時禁止增加 venue exposure；custody at risk／insolvency suspected 時 venue-level HALT，禁止自動轉入資金。
6. 測試 depeg、跨 venue 價差、depth 消失、提款停止、帳戶凍結、delisting、maintenance 無限延長、共同上游錯價。
7. 輸出 state-action matrix、風險上限、告警、runbook、replay fixtures 與 promotion impact。

---

**Prompt 23：Mandatory Compound Chaos Scenario Suite**

1. 請完整閱讀 AGENTS.md。本次任務建立複合故障測試套件，不能只將單一 fault tests 串在一起而缺少共同時間線。
2. 至少實作：flash crash + stale feed；partial fill + timeout + crash；DB unavailable + unknown order；venue outage + quote-asset depeg；risk-service restart + duplicate replay；region outage + open orders；split-brain + clock skew；dashboard compromise + stale command；disk full + audit write failure；correlation spike + liquidity collapse。
3. 每個 scenario 必須有 deterministic timeline、seed、external-state fixture、expected RiskDecision、expected order states 與 expected safe terminal state。
4. 測量 maximum unintended exposure、duplicate-order count、reconciliation difference、data loss、time-to-close-only、time-to-halt、time-to-reconcile。
5. 任何 scenario 若產生重複訂單、無界限曝險、未記錄 audit 或未能進入安全狀態，測試必須失敗且阻止 promotion。

---

**Prompt 24：24/7 On-call、告警升級與受控重新啟動**

1. 請完整閱讀 AGENTS.md。本次任務建立 24/7 operational response policy 與演練，不啟用 live。
2. 定義 SEV-1／SEV-2 acknowledgement target、primary／secondary on-call、無人回應 escalation、至少兩種獨立通知通道與定期輪值測試。
3. 定義誰可執行 pause-new-risk、close-only、cancel-all、halt、credential revoke、restore、failover 與 restart。
4. Canary／live restart 必須要求兩位不同授權角色核准，且核准不得由同一服務帳號或同一 session 代替。
5. 事故原因未明、外部對帳未完成、credential 未確認、leader fencing 未確認或 DR evidence 不完整時，禁止 restart。
6. 演練 alert delivery failure、primary on-call unreachable、mobile session lost、operator error、錯誤環境操作與重複 restart request。
7. 輸出演練時間線、acknowledgement／resolution metrics、權限矩陣、未達標項目與改善 Issue。

---

**Prompt 25：Extreme-resilience Canary／Live 最終 Gate**

1. 請完整閱讀 AGENTS.md。本次任務只做 readiness assessment，不修改設定、不啟用 canary／live。
2. 逐項驗證最近且有效的：restore drill、RPO／RTO evidence、single-active／split-brain drill、credential compromise drill、venue／custody／depeg drill、compound chaos、on-call escalation、雙人 restart approval。
3. 驗證所有 open orders、fills、positions、cash、risk state 可由外部 truth 與 append-only events 重建。
4. 驗證所有正式 credentials 為最小權限、禁提款／轉帳、可即時撤銷，且不存在於 repository、CI logs、artifacts、dashboard bundle。
5. 驗證 region／host failover 後預設 HALT／close-only，且沒有自動恢復新增風險的程式路徑。
6. 檢查所有 BLOCKER／HIGH、Sev-1／Sev-2、restore discrepancy、unknown order、split-brain 與 security finding 已關閉。
7. 結論只能為 PASS、FAIL 或 INSUFFICIENT\_EVIDENCE；任何證據過期、缺失或無法重現時不得 PASS。
8. 即使 PASS，也只能提出供人類審核的 promotion recommendation，不得自行變更環境或資本。

---

**版本說明：本文件中的所有數值門檻均應由 AGENTS.md、RFC 與實際市場／平台證據決定。Codex 不得自行把範例值視為正式 production 設定。**
