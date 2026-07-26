---
name: paper-shadow-readiness
description: 當需要唯讀評估 Auto Trader 的 paper readiness、Paper→Shadow gate、shadow execution boundary 或操作驗收證據時使用；不要用於啟用環境、建立正式憑證、核准 canary／live 或修改資本與風控設定。
---

# Paper and Shadow Readiness

只評估 `paper` 或 `shadow` 的就緒度，不變更模式。paper 與 shadow 必須分開判定：paper 可使用模擬成交；shadow 只產生即時決策與預期成交，絕不送出訂單。

## 安全邊界

- 以 `AGENTS.md` 的 promotion path 與 `Trader prompts.md` Prompt 9、11、15、17 為準。
- 不啟動 paper／shadow，不連線正式 venue，不要求或讀取 API key。
- 不評估或核准 canary／live；若使用者要求，停止並改用專用高階 gate。
- 不修改 `configs/paper.yaml`、`configs/shadow.yaml` 或任何風控值。
- 未取得操作期間、sample count、reconciliation、drill、approval 等 evidence 時標 `BLOCKED`。
- mock port、placeholder dashboard、policy skeleton 與 CI 綠燈不是 paper／shadow 操作證據。

## 1. 確認目標 gate

從請求判定：

- `Paper readiness`：是否具備安全進入／執行 paper 的技術與操作前置條件。
- `Paper -> Shadow`：是否有足夠 paper 運行證據可供人類審核。
- `Shadow boundary`：shadow 是否完全無送單副作用。

若未指定，分別輸出 paper 與 shadow 兩張矩陣，不合併 verdict。

## 2. 建立 repository truth

完整閱讀：

- 根目錄 `AGENTS.md`、`README.md`、`Trader prompts.md`。
- `configs/base.yaml`、paper、shadow 與 market profiles。
- broker／execution／risk／ledger／reconciliation／runtime／control code。
- dashboard environment display 與 command boundary。
- alerting、monitoring、incident、DR、credential、venue、on-call 文件與實作。
- unit、property、integration、contract、e2e、replay、chaos、DR 與 security tests。
- CI workflows、run manifests、reports、artifacts 與目前 diff。

執行：

```bash
git status --short --branch
git ls-files
rg -n -i "paper|shadow|order.?state|idempoten|ledger|reconcil|restart|kill.?switch|alert|audit|environment" src services apps configs tests docs infra
git diff --check
```

## 3. 前置 Milestone gate

在 paper readiness 前，驗證至少已有：

- 可重現 market data 與 quality gate；
- deterministic event-driven backtest／replay；
- conservative fills、fees、spread、slippage、latency、partial fill、reject；
- 已驗證策略與 portfolio；
- 獨立 RiskEngine 及必要 invariants；
- order／ledger／reconciliation contracts。

缺少任一必要前置時，readiness 為 `NOT READY`；不得因 paper 是模擬環境而跳過風控與帳務。

## 4. Paper readiness controls

檢查：

1. paper broker／simulated exchange 與正式 adapter 完全隔離。
2. `system.mode=paper` 的設定經驗證且不可能讀取 live credentials。
3. order state machine 包含 partial fill、reject、cancel、expired、unknown 與非法轉移。
4. order、event、command、fill 與 ledger idempotency。
5. Decimal price／quantity／fee，precision／minimum-notional normalization 不增加風險。
6. append-only ledger 與 orders／fills／positions／cash／PnL 守恆。
7. external／paper-broker snapshot 對帳；mismatch 停止新增風險。
8. restart recovery 先重建狀態並保持 halt／close-only。
9. alert、metrics、heartbeat、data freshness、unknown order 與 reconciliation 告警。
10. dashboard 明顯顯示 `PAPER`，不直接呼叫 broker、不計算風控。
11. dashboard 故障不影響 runtime；halt 有獨立通道。
12. credential policy 最小權限、分環境、禁提款／轉帳；不讀實際 credential。
13. incident、restore、credential revoke、venue block、depeg、split-brain 與 compound chaos drill。
14. unresolved Sev-1／Sev-2、BLOCKER／HIGH findings。
15. operator／risk approver 的明確核准 evidence。

## 5. Shadow boundary and Paper -> Shadow gate

另外驗證：

- shadow adapter 只能記錄 decision／expected execution；不存在 submit／cancel／replace 外部副作用。
- shadow 與 paper／canary／live 的 credentials、database、topic、account 與 UI 不混用。
- 加密策略至少連續 30 日；股票策略至少 20 個交易日。
- 預設至少 500 個決策與 100 個模擬成交，除非核准規格另有版本化門檻。
- 100% orders／positions 可對帳，無未知訂單。
- 無未解 Sev-1／Sev-2。
- modeled vs paper slippage 差異在核准容許值。
- 每個決策與 run manifest 可重現。
- restart、disconnect、duplicate、reject、partial-fill、kill-switch tests 通過。
- backup／restore smoke、fencing、credential revoke、venue outage、withdrawal suspension、depeg、compound chaos 與 on-call escalation 有最近且可重現證據。

任何 sample／duration／drill 缺少可靠 artifact 時標 `BLOCKED`，不是 `PASS`。

## 6. 安全驗證命令

只執行不會連線外部市場的 repository checks：

```bash
uv run pytest
pnpm lint
pnpm typecheck
pnpm test
pnpm build
docker compose config --quiet
```

不要執行會啟動 sandbox／paper feed 的命令，除非其 mock-only、無憑證、無外部網路邊界已由 code 與 config 明確證明，且使用者要求執行。無法證明時標 `BLOCKED`。

## 7. 狀態與 verdict

每個控制使用：

- `PASS`：本次有 implementation、test 及適用的 operational evidence。
- `FAIL`：控制缺失、boundary 可被跨越、前置 Milestone 未完成或最新演練失敗。
- `BLOCKED`：必要 runtime artifact、期間、sample、權限、工具或 drill evidence 不可取得。
- `NOT APPLICABLE`：對目標 gate 確實不適用，並附理由。

Gate verdict：

1. 任一必要 `FAIL`：`NOT READY`。
2. 無 FAIL 但有必要 `BLOCKED`：`BLOCKED`。
3. 全部必要 `PASS`：`READY FOR HUMAN REVIEW`。

即使 ready，也不得改變環境。此 Skill 永遠不輸出 canary／live approval。

## 8. 輸出格式

1. `Target gate and repository snapshot`。
2. `Gate verdict`。
3. `Prerequisite milestone evidence`。
4. `Readiness matrix`：

| Control | Status | Implementation | Test／CI | Runtime／drill evidence | Gap |
|---|---|---|---|---|---|

5. `Runtime statistics`：期間、決策、模擬成交、reconciliation rate；未知則明寫。
6. `Execution and ledger evidence`。
7. `Security and credential design evidence`。
8. `Incident／DR／operator evidence`。
9. `Unresolved high-risk findings`。
10. `Commands executed` 與退出碼。
11. `Required human approvals`。
12. `Explicit non-actions`：未啟動模式、未連線、未讀 credential、未核准 canary/live。
