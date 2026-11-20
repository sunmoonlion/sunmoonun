# C5 专家分步执行与脚本计费复核回执（agy）

- **复核结论**：**通过**（本地候选满足 C5 专家分步执行与核权、根预算预留/结算/释放、Kubernetes 容器终态计量与防重入要求；另附 **5 条代码合理性评价与完善建议** 供第 10 项前生产硬化，均非本轮阻塞项）。
- **工作位置**：本地 `wsl-dev`（工位 `/home/zymun/worktrees/luna`）。
- **日期**：2026-11-20

---

## 一、复核范围与所验提交

| 仓库 | 所验候选提交 | 对比基线 | 复核隔离方式说明 |
| --- | --- | --- | --- |
| KnowLab 后端 | `e7e3c54` | `778c023` | 工位干净，直接在 `e7e3c54` 复测 |
| KnowLab Web | `7eb57a7` | `66e7d14` | 锁文件同步提交（工位干净） |
| KnowLab 应用 | `8bbce62` | `c47e190` | 指针指向上述提交（工位干净） |
| KnowBench 后端 | `dbd142c` | `f392957` | 复核期间工位已有第 10 项未暂存测试改动，经 `git archive dbd142c` 导出到独立临时目录严格按固定提交复测与静态检查，未改动工位任何文件 |
| KnowBench Web | `08c4b9d` | `6e63616` | 工位干净，直接在 `08c4b9d` 复测 |
| KnowBench 应用 | `3039865` | `27fcbe6` | 指针指向受审后端/Web 提交 |
| `sunmoonun`（供给器及 RBAC） | `7769c48a8` | `36d980961` | 真实 KIND 测试通过 `git archive 7769c48a8` 导出固定版本运行；另核对工位当前 `3cdce28b1` 对 `sandbox-platform`（provisioner/image/RBAC）与 `7769c48a8` 零差异 |

---

## 二、独立复测实况记录

### 1. KnowBench 后端非容器 DB 与契约套件（隔离 PostgreSQL 16 + `dbd142c` 快照）
- 环境：`AGENT_TEST_DATABASE_URL` 指向一次性 tmpfs PostgreSQL 16（`postgres:16-alpine`），`PYTHONPATH=/tmp/agy-c5-kb/app`。
- 命令：
  ```bash
  .venv/bin/pytest -q \
    tests/test_formal_script_execution_db.py \
    tests/test_script_budget_db.py \
    tests/test_script_inputs_db.py \
    tests/test_skill_executor.py \
    tests/test_skill_execution_db.py \
    tests/test_method_authorization.py \
    tests/test_kernel_invariants.py
  ```
- 结果：**`64 passed, 3 skipped in 39.94s`**（3 项跳过即为待真实供给器运行的 `real_container` 用例；其余涵盖并发预留与结算、余额不足 `BudgetExhausted`、回执冲突 `IdempotencyConflict`、回执缺失保留预留并阻止 `purge_test_run`、拒绝/运行中撤权/取消/丢失发送回执与重启收集、第 8 项页数上限与操作卡等全部通过）。

### 2. 真实 KIND + PostgreSQL 16 + 环回供给器容器实测（`dbd142c` + `7769c48a8`）
- 集群与权限：在 `sunmoon-kind` 建立临时隔离命名空间 `agy-c5-probe`，按 `sunmoonun/gitops/components/sandbox-platform/provisioner/workload.yaml.j2`（`7769c48a8`）精确施加最小 RBAC（含新增 `pods: [get, list, patch]`）；用 `luna-local/sandbox:codex-0.170.0` 叠加 `7769c48a8` 的 `image/skill_execute.py` 构建一次性镜像 `agy-c5-sandbox:probe` 并经 `ctr` 导入三节点；启用 `7769c48a8` 环回供给器（无 pull secret、无共享环境状态）。
- 命令：
  ```bash
  pytest -q -s tests/test_formal_script_execution_db.py -k real_container
  ```
- 结果：**`3 passed, 11 deselected in 28.14s`**
  - `test_real_container_in_three_step_expert`：**PASSED**（连接器读取 → 真实隔离容器读取 `arguments.json` 并写出 `outputs/result.json` → 连接器按验收字段发送，三步核权及专家冻结与准入校验通过）。
  - `test_real_container_settlement_after_start[cancel]`：**PASSED** — 实测输出 **`cancel: 3 container seconds, 0.030000 CNY on the root task`**，余款释放，根任务 `spent` 与消耗账目一致，终态 Job 已清理。
  - `test_real_container_settlement_after_start[failure]`：**PASSED** — 实测输出 **`failure: 2 container seconds, 0.020000 CNY on the root task`**，余款释放，根任务 `spent` 与消耗账目一致，终态 Job 已清理。
- 供给器观测与清理核验：
  - 环回供给器日志实录 3 项用例共 4 次真实容器 `script_attach` 分阶段耗时（工具自验叶与混合专家第 2 步各 1 次、`cancel` 与 `failure` 各 1 次）：`bytes=794 accepted=True connect_ms=14 write_ms=0 ack_ms=3 elapsed_ms=17`、`bytes=794 accepted=True connect_ms=12 write_ms=0 ack_ms=2 elapsed_ms=14`、`bytes=478 accepted=True connect_ms=16 write_ms=0 ack_ms=3 elapsed_ms=19`、`bytes=530 accepted=True connect_ms=13 write_ms=0 ack_ms=2 elapsed_ms=15`。
  - 测试完成后查 `kubectl get jobs,pods,networkpolicies -n agy-c5-probe`：仅存 `networkpolicy.networking.k8s.io/skill-execution-deny-all`（`app=skill-execution`），无残留 Job 或 Pod；测试结束已全量清理临时命名空间、镜像与 PG 容器。

### 3. Alembic 数据库迁徙往返（隔离 PostgreSQL 16）
- 在独立库执行 `.venv/bin/alembic upgrade 20261120_0048` → `upgrade head (20261120_0049)` → `downgrade 20261120_0048` → `upgrade head (20261120_0049)` 全链路通过。
- `psql` 核验 `alembic_version = 20261120_0049`、`workbench_budget_ledger` 列 `script_call_id` / `script_evidence`、约束 `ck_budget_script_entry` 及部分唯一索引 `uq_budget_script_entry(script_call_id, entry) WHERE script_call_id IS NOT NULL` 均按预期建立；另 `test_script_budget_db.py` 已覆盖含历史 `script-cost/v1:` 备注记录的降级保留与重升恢复。

### 4. 供给器测试套件
- 在 `sunmoonun/infrastructure/applications/component-images/sandbox-platform/provisioner` 运行 `PYTHONPATH=. pytest -q tests`：**`25 passed in 0.52s`**（含 `test_shared_script_policy_creation_race_and_drift`、`test_container_meter_uses_owned_pod_and_kubelet_timestamps`、`test_result_only_reads_pod_owned_by_the_exact_job` 等）。

### 5. KnowLab 后端、静态检查与 KnowBench Web
- **KnowLab 后端（`e7e3c54`）**：
  - `pytest -q tests/test_formal_method_execution.py tests/test_formal_method_recursive_plan.py`：**`20 passed, 2 skipped in 1.34s`**（2 项跳过因未设 `DELIVERY_TEST_DATABASE_URL`）。
  - `.venv/bin/ruff check`（改动 4 个 `.py` 文件）：**`All checks passed!`**。
  - `.venv/bin/pyright app/domain/knowbots/formal_method_execution.py app/domain/knowbots/formal_method_plan.py`：**`0 errors, 0 warnings, 0 informations`**。
- **KnowBench 后端静态检查（`dbd142c` 快照）**：
  - `.venv/bin/ruff check`（`f392957..dbd142c` 变更的 44 个 `.py` 文件）：**`All checks passed!`**。
  - `.venv/bin/pyright`（按 `pyproject.toml` 检查 `app`, `core`, `scripts`）：**`0 errors, 0 warnings, 0 informations`**。
  - `.venv/bin/lint-imports`（328 文件 / 1974 依赖）：**`Contracts: 4 kept, 0 broken.`**。
- **KnowBench Web（`08c4b9d`）**：
  - `pnpm check` 退出码 0：`tsc --noEmit` 通过、`eslint .` 通过、`check:i18n` 通过（`en`/`zh-CN` 1,387 keys）、`vitest run` **`65 passed | 1 skipped`（`503 passed | 2 skipped`）**（跳过的 2 项为 `tests/unit/interaction-consumer-vectors.test.ts`，因独立 Web 仓内未附带 `web-interaction-consumer-vectors-v1.json`）、`next build` 生产构建通过。

---

## 三、核心核查对照要点

1. **三步混合专家与核权链路**：
   - `FormalMethodExecutionRequest`（KnowLab `formal_method_execution.py:291-299`）与 `direct_procedure()`（KnowBench `formal_execution.py:199-209`）强制 `skill_script` 仅允许 `host` 零轮调用。
   - `PermissionGrant`（`method_authorization.py:43-94`）支持 `script_asset_id`/`script_revision` 精确绑定并禁止脚本权限委托（`delegable=False`、`resource_authority is None`、`recipient_call_id` 非空）；`formal_adapter.py` 与 `formal_evidence.py` / `formal_orchestration_evidence.py` / `formal_recursive_evidence.py` / `formal_orchestration_admission.py` 对脚本步核对 `source_asset_id`、`connection_id is None`、包清单摘要、`call_digest`、`script_quote` 及 `outputs/result.json`（`method_script_outputs` 禁重复键与超限嵌套），确保拒绝、运行中撤权、取消、回执丢失及服务重建后不重复调用、失权后后续发送次数为零。
2. **根预算、容器计费与异常保守收敛**：
   - `Settings.validate_base_security()`（`config.py:508-516`）校对 `WORKBENCH_SCRIPT_TARIFF.provisioner_url == WORKBENCH_PROVISIONER_URL`。
   - `ScriptTariff.quote()` 按 `90s + 1s = 91s` 计算预留上限并生成 `tariff_digest` 嵌入 `PermissionGrant` 审批摘要与操作卡展示；`rated_usage()` 以 `ROUND_HALF_UP` 保留六位人民币小数并校验 `run_id`、`finished_at` 及 `<= 91s` / `<= maximum`。
   - `dispatch()` 在前置校验失败、`prepare_connection_not_established`、`slot_occupied_before_creation`、`isolation_unavailable_before_creation` 时按零结算并释放预留；`container_meter()` 仅采信 `ownerReferences` 唯一归属 `Job` 的 `Pod` 中 `name="script"`、`restartCount=0` 且带 `containerID` 的 kubelet 时间戳，或终态未启动 `ScriptNotStarted` 证明（零计费）；回执缺失（含超过 `ttlSecondsAfterFinished: 900` 清理期）、身份冲突或用量超限时 fail-closed 保留预留并由 `purge_test_run()`（`repository.py:2194-2206`）阻止清理待结账测试任务。
3. **第 8 项四条复核建议闭环核对**：
   - `ensure_isolation_policy`（`script_jobs.py:53-90`）已改为先 `GET`、缺失再 `POST`、遇 `409` 重读并校验隔离规则且禁止 `PUT` 覆盖；
   - `script_inputs.py:21` 已调整 `MAX_MATERIAL_PAGES = FILE_LIMIT // 1024` 并以实际 UTF-8 字节累计数及 Provider EOF 为准；
   - `provisioner.py:181-208` 已补齐 `script_attach` 分阶段耗时日志并在本次 KIND 实测中验证输出。

---

## 四、代码合理性评价与完善建议

**整体评价**：C5 整体架构边界严谨、责任清晰。账本采用部分唯一索引 `uq_budget_script_entry` + 根任务行锁 + CAS 双保险防止重入与并发双扣；供给器通过最小新增 RBAC（`pods: patch`）缩短活跃 Pod 的 `activeDeadlineSeconds` 而非直接删除资源，从而完整保留终态 Pod 供 kubelet 计量；`20261120_0049_script_metering.py` 降级时还将结构化计量证据以 `script-cost/v1:<md5>:<json>` 保存在 `note` 以便可逆回退。以下 5 点建议供第 10 项全量验收前进一步硬化（均不阻塞本轮 C5 通过）：

1. **[P1 · 状态机边界] `_collect()` 在“运行中撤权”与“取消后回执缺失”两种路径上的状态收敛不对称**
   - 位置：`knowbench-app/knowbench-backend/app/app/application/workbench/formal_script_execution.py:111-134, 148-174`
   - 问题 A（运行中撤权提前写终态 `failed`）：当容器仍在运行（`receipt["state"] == "running"`）但权限已撤回（`authorized=False` 且非用户主动 `stop_requested`）时，L113 触发 `stop_metered` 后，L114-133 立刻将 `call["status"]` 改为 `failed`（此时容器尚未退出，未完成 `settle()`，且未写 `capability/action_completed` 事件）。等到下轮 `reconcile()` 取回 `container_meter` 结算时，L148 因 `current["status"] != "dispatching"` 跳过事件补写，造成 ① 丢失 `capability/action_completed`；② 若两次轮询间隙推进器观测到 `call` 已 `failed` 并先触发封存校验，可能与尚未释放的 `budget.reserved > 0`（`formal_orchestration_evidence.py:570` / `formal_recursive_evidence.py:775`）发生竞态（单测用同步假执行器直接置 `finished`，未能暴露该真容器异步窗口）。
   - 问题 B（用户停止后若遇 `absent` 或超时将卡死在 `dispatching`）：用户点击停止置位 `stop_requested=True` 后，若遭遇 `receipt["state"] == "absent"`（如异常未建 Job 或超 900s TTL 过期）或 `delayed`（>2 分钟），L114 条件 `and not (intent.get("result") or {}).get("stop_requested")` 恒为假，导致 `call["status"]` 永远停在 `dispatching` 不收敛。
   - 建议：统一策略——只要 `receipt["state"] == "running"` 且 `not delayed`，无论撤权还是 `stop_requested` 都仅下发 `stop_metered` 并保持 `dispatching` 等待容器退出，由 L137-174 在单一事务内原子完成 `settle()` + `update_call` + `append_event`；仅当 `receipt["state"] == "absent"` 或 `delayed` 时，才在 L114-133 收敛状态为 `failed`/`unknown`（仍保留预算预留等待对账）。

2. **[P2 · 并发锁序] `_collect()` 终态结算事务锁序与全仓约定不一致**
   - 位置：`knowbench-app/knowbench-backend/app/app/application/workbench/formal_script_execution.py:137-146`（对比 `capabilities.py:472-503` 与 `formal_script_execution.py:64-66`）
   - 说明：工作台全仓约定严格按 `Task -> Session -> Call -> Selection -> Asset` 加锁；而 `_collect()` L138 先锁 `Task`、L141 锁 `Call`，随后 L144 在 `_check_before_send()` 内经 `_locked_call_session()` 再去锁 `Session`（形成 `Task -> Call -> Session`）。当延迟对账发生且原 `Task` 已非会话当前 `active_task_id` 时，另一并发请求走 `_locked_session()`（`Session -> Call`）可能与此处构成死锁反转风险。
   - 建议：将 L138-140 调整为直接调用 `await svc._locked_call_session(owner, call)`（按 `Task -> Session` 上锁），再锁 `capability_call(..., lock=True)`，恢复全仓统一锁序。

3. **[P2 · 供给器幂等与竞态] `stop_metered()` 未处理 Pod 并发进入终态时的 `409/422` 响应及重复 `PATCH`**
   - 位置：`sunmoonun/infrastructure/applications/component-images/sandbox-platform/provisioner/script_jobs.py:224-250`
   - 说明：若 Pod 在 L231 `owned_pod` 读取与 L237 `PATCH /spec/activeDeadlineSeconds` 之间恰好自然完成或失败，Kubernetes API 会拒绝修改终态 Pod 并返回 `422`（或 `409`），L249 `response.raise_for_status()` 会将其暴露为 `500`（同文件 `deliver()` L359-367 已对 `409/422` 做重读幂等）。此外本次真实 KIND `cancel` 用例实测日志记录在容器终止期间连续收到 **10 次** `POST /stop-metered 202 Accepted` 请求。
   - 建议：在 `response.status_code in (409, 422)` 时重读 `owned_pod(job)`，若同 UID Pod 已为 `Succeeded`/`Failed` 则幂等返回；并在发起 PATCH 前若 `pod.get("spec", {}).get("activeDeadlineSeconds") == 1` 直接跳过重复写操作。

4. **[P2 · 槽位回收可靠性] `_collect()` 落账后若 `executor.cancel()` 瞬时失败，终态 Job 会占位至 900s TTL**
   - 位置：`knowbench-app/knowbench-backend/app/app/application/workbench/formal_script_execution.py:137-175`、`capability_repository.py:526-534`
   - 说明：“先落账提交、后异步清理 Job”保证了财务一致性；但因 `pending_metered_scripts()` 只检索尚无 `consume` 记录的调用，一旦 L175 `executor.cancel()` 因瞬时网络错误、`504` 或进程重启失败，后续 `reconcile()` 不会再次拾起该调用，已结账终态 Job `skill-{owner.hex}` 将占住该账号唯一执行槽长达 `ttlSecondsAfterFinished: 900`（15 分钟）。
   - 建议：在 L175 增加短退避重试（如 2-3 次），或为“已结算待删槽位”留轻量化回收记录由后台清理，避免单次删除瞬时故障阻塞账号后续脚本调用。

5. **[P3 · 边界文案与前端操作卡交互细节]**
   - 后端：`knowbench-app/knowbench-backend/app/app/application/workbench/capabilities.py:2277-2282` 的 `except Exception` 未知回执提示仅判断 `execution_kind == "skill_script"`，漏了 `"formal_script"`，建议改为 `in ("skill_script", "formal_script")`。
   - 前端：`knowbench-app/knowbench-web-frontend/app/components/workbench/capability-action-card.tsx:87-89, 196-203, 234-241`：① L87“正式方法调用”提示未包含 `formal_script`；② 用户点击停止后后端保持 `status="dispatching"` 并写入过渡态 `detail.result = {"stop_requested": true, "message": "Stop requested"}`，当前操作卡仍在 L196 保留可点击的“停止脚本”按钮且在 L234 将该内部过渡 JSON 渲染进“结果”折叠块。建议识别 `stop_requested` 展示“正在停止并等待结算”且禁用重复点击，并在 `dispatching` 阶段屏蔽过渡 JSON 渲染。
