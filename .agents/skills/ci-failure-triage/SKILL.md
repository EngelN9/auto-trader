---
name: ci-failure-triage
description: 當 GitHub Actions、security checks、Docker build 或本機驗證失敗，需要找出第一個真正 root cause、最小重現與連鎖錯誤時使用；不要用於在未獲明確要求時修程式、放寬測試或修改風控。
---

# CI Failure Triage

定位第一個可行動的 root cause，將它與後續連鎖錯誤分離，提出最小修正範圍並保存可重現證據。

## 安全邊界

- 預設 `DIAGNOSE ONLY`，不修改任何檔案。
- 只有使用者明確要求「修復」後才可編輯；修復仍須最小化且遵守 `AGENTS.md`。
- 不刪除、skip、xfail 或弱化測試，不放寬 risk limits、security scan、workflow permissions 或 supply-chain controls。
- 不讀取、列印或要求正式 secrets；不重跑需要正式環境或正式帳戶的 job。
- 不以重新執行直到偶然變綠取代 root-cause analysis。
- 外部 log／artifact 無權限時標 `BLOCKED`，不要從 job 名稱猜原因。

## 1. 收集不可變識別資訊

記錄：

- repository、branch、commit SHA、PR／run id；
- workflow、job、step、runner OS；
- 首次失敗時間；
- lockfile hashes 與 relevant image／action SHA；
- local dirty state。

執行：

```bash
git status --short --branch
git rev-parse HEAD
git diff --check
```

若 GitHub CLI 已安裝且目前登入具唯讀權限：

```bash
gh pr checks
gh run view <run-id>
gh run view <run-id> --log-failed
```

不得把 token 或 secret 顯示在報告。若無 `gh`、未登入、run id 不明或 log 不可讀，標記 remote-log 檢查 `BLOCKED`，繼續使用可取得的本機證據。

## 2. 讀取 CI 定義與變更

完整閱讀：

- `.github/workflows/ci.yml`、`.github/workflows/security.yml`。
- `pyproject.toml`、`uv.lock`、`package.json`、dashboard package、`pnpm-workspace.yaml`、`pnpm-lock.yaml`。
- Dockerfiles、`compose.yaml`、`Makefile`。
- `scripts/check_workflow_pins.py` 與相關 tests。
- 失敗 commit 相對基準的完整 diff。

將 failing step 對應到 workflow 內的精確命令、tool version、permissions、environment 與 cache key。不要用 README 的近似命令取代 workflow command。

## 3. 找第一個真正 root cause

依時間順序解析 log：

1. 忽略 setup 噪音與後續「file not found」「job canceled」等衍生錯誤。
2. 找到第一個非零退出碼或明確 failed assertion。
3. 向前追到造成該失敗的最小輸入、版本、設定或程式變更。
4. 判斷類別：
   - application／test defect；
   - dependency／lock drift；
   - workflow／permission／action pin；
   - container／platform；
   - network／registry／advisory database；
   - flaky／race／time-dependent；
   - security finding；
   - missing evidence。
5. 將每個後續錯誤標為 `ROOT CAUSE`、`CONSEQUENCE` 或 `INDEPENDENT FAILURE`。

不要假設最後一行是 root cause，也不要把所有紅色輸出列成多個根因。

## 4. 建立最小重現

先重現 failing step，不先跑完整 suite。repository 目前定義的 CI 命令包括：

```bash
uv sync --frozen --all-groups
uv run ruff format --check src tests scripts
uv run ruff check src tests scripts
uv run mypy
uv run pytest
uv run python scripts/check_workflow_pins.py
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm build
docker compose config --quiet
```

只選擇與失敗 step 完全相符的命令。先確認 tool version 與 workflow 一致；缺少 `uv`、Node／pnpm 版本、Docker daemon 或平台能力時標 `BLOCKED`。

安全掃描：

- secret finding：遮蔽值，記錄檔案／類型，不輸出秘密。
- dependency／OSV／Trivy finding：記錄 package、installed version、advisory、fix availability 與 dependency path。
- 不以 `ignore`、severity 降級、`ignore-unfixed` 變更或 broad allowlist 作為最小修復。
- 第三方 outage 只有在 log 證明時才標 external。

若單一測試可重現，使用精確 node id；確認修復前也能以完整原命令重現。

## 5. 形成最小修正建議

診斷模式只提出：

- root cause；
- 影響範圍；
- 最小候選檔案；
- 不應修改的邊界；
- regression test；
- 驗證命令；
- rollback。

若使用者已明確要求修復：

1. 先確認修正不會啟用交易、讀秘密或放寬安全控制。
2. 只修改 root cause 所需檔案。
3. 新增／保留 regression test。
4. 執行最小重現，再執行受影響 workflow 的完整命令。
5. 不 commit、不 push，除非使用者另行明確要求。

## 6. 狀態規則

- `PASS`：檢查或重現命令成功，且有輸出證據。
- `FAIL`：可重現失敗或確認缺陷。
- `BLOCKED`：log、artifact、工具、平台、權限或安全前置缺失。
- `NOT APPLICABLE`：該 job／platform 與此次 failure 無關，附理由。

Triage verdict：

- `ROOT CAUSE IDENTIFIED`：有最小重現或充分直接 log evidence。
- `PARTIALLY IDENTIFIED`：已縮小範圍但仍有 material ambiguity。
- `BLOCKED`：缺少關鍵 evidence，無法可靠定位。

## 7. 輸出格式

1. `Outcome`：先寫 triage verdict 與第一個 root cause。
2. `Failure timeline`：

| Order | Job／step | Status | Classification | Evidence |
|---|---|---|---|---|

3. `Minimal reproduction`：環境、命令、退出碼、最小錯誤摘要。
4. `Root cause vs cascading failures`。
5. `Smallest repair scope`。
6. `Regression and verification plan`。
7. `Commands executed`。
8. `Blocked evidence`。
9. `Safety impact`：是否影響 trading、data、risk、credentials、CI permissions。
10. `Changes made`：診斷模式必須寫 `None`。

引用 log 時只取必要片段；遮蔽 secrets、token、account id 與敏感 URL。
