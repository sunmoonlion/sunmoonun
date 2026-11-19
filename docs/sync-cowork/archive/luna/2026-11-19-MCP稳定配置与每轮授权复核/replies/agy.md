# 评审回执：MCP 稳定配置与每轮授权复核

- 请求：[request.md](../request.md)
- 轮次：1
- 核对提交：
  - 工作位置：本地（`wsl-dev`，`/home/zymun/worktrees/luna`，分支 `luna`）
  - `knowbench-app/knowbench-backend`：`de6e586fc6cc97ef2cabc7ff3a4f538bcf478465`（其中 MCP 稳定配置与每轮授权提交为 `9548ca90a3f478e1f6b4d09b0eab25a9ec95fa76`，基线提交为 `ac19fbf95e16aa713f0357363f4a6e21dabe4ca1`）
  - `knowbench-app`：`69ca442bdb81ff3a37cedd364f35366b82d3475b`
  - Sandbox 平台镜像源码（`sunmoonun`）：`5b11c85639cba4c7dedfd09f97bc39db8e14ee59`（当前 `sunmoonun` HEAD `077a5679a5c5950eac9d48b0fbafb63bc3496c19`）
  - Link `0.5.9` 打包源（`sunmoon-link`）：`318f79e54cfe2be27fc9ceb722d172a8e757d975`
- 结论：**通过（无阻断项）**。经源码逐行审计与本地 `wsl-dev` 实库全量回归测试验证，`request.md` 所列 4 项完成条件均已严密闭环；本轮变更可作为 Luna 待办第 3 项（接入实施方案 §17.6 第 5 项）开发候选完成依据。

## 发现

### F01 [info] 4 项完成条件逐项核查结果

1. **条件 1（MCP 订阅跨轮复用、可发现工具目录变化重连与同 `gateway` 令牌下的 Skill 切换越权防护）—— 已闭合**
   - **网关令牌复用与每轮作用域隔离**（`knowbench-backend/app/app/application/workbench/capabilities.py:956-1259`）：
     - `Capabilities.prepare(..., previous_gateway: str | None = None)` 计算工具目录摘要 `inventory = digest([self.runtime_url, bool(method_binding), bool(packages), {key: [spec["tool"], spec.get("execution_kind")] for key, spec in tools.items()}])`。
     - 仅当 `previous_gateway` 存在、`previous.get("status") == "completed"`、`previous.get("inventory") == inventory` 且 `secrets.compare_digest(previous.get("gateway_hash", ""), digest(previous_gateway))` 时复用同一 `token = previous_gateway`；否则生成全新 `token = secrets.token_urlsafe(32)`。
     - 即便复用 `token`（`gateway_hash = digest(token)` 不变），每次 `prepare()` 仍强制生成全新的每轮 `scope_id = secrets.token_hex(16)` 与每轮代际哈希 `token_hash = secrets.token_hex(32)`，并排序输出 `enabled_tools`。
     - `Capabilities.runtime(session_id, token)`（`capabilities.py:1286-1289`）通过 `runtime.get("gateway_hash", runtime.get("token_hash", ""))` 校验 Bearer 令牌摘要，兼顾新旧运行时记录格式。
   - **Runner 订阅复用判定**（`knowbench-backend/app/app/application/workbench/runner.py:507-535`）：
     - `SandboxLink.prepare_capabilities` 从 `self.capability_config.get(thread_id, {})` 提取既有 `Bearer <gateway>` 传入 `previous_gateway=gateway or None`。
     - 当连续轮次可发现工具集（`url`、`Authorization: Bearer <token>`、排序后的 `enabled_tools`）未变时，`self.capability_config.get(thread_id) != config` 为 `False`，跳过 `thread/unsubscribe` + `thread/resume`，直接复用当前 Codex 线程与 MCP 连接；仅在工具集或 `bool(packages)` / `bool(method_binding)` 变化时重连刷新。
     - 实测 `tests/test_skill_package_db.py:232-299`（`test_runner_reuses_mcp_subscription_and_refreshes_turn_scope`）与 `tests/test_skill_package_db.py:344-382` 验证：连续两轮启用 Skill 时 `len(resumes) == sum(unsubscribe) == 1`；在保持同一 `gateway`（`after["config"] == before["config"]`）的情况下将旧 Skill 切换为 `replacement` Skill 后，`scope_id` 刷新，读取已取消勾选的旧 Skill 抛出 `Forbidden("Skill is outside the selected scope")`，读取新勾选 Skill 正常返回 `"SECOND_TURN_BODY"`；第三轮关闭全部 Skill 时触发第 2 次 `unsubscribe` + `resume`。

2. **条件 2（旧轮迟到 `skill_files` / `skill_read` / `action_result` 锁等待竞态与迟到 `turn/start` ACK 串绑防护）—— 已闭合**
   - **读路径锁内二次核验**（`knowbench-backend/app/app/application/workbench/capabilities.py:1320-1346`、`capability_routes.py:361-433`）：
     - `Capabilities.verified_read(session_id, token, name, arguments, meta)` 先在锁外调用 `await self.verify_invocation(session_id, token, name, arguments, meta)`（允许等待 Runner 登记），随后开启事务、锁住会话（`self._locked_session(owner, session_id)`）与能力选择行（`self.repo.capability_selection(owner, session_id, lock=True)`），并在持锁状态下**再次执行 `await self.verify_invocation(session_id, token, name, arguments, meta, observe_seconds=0)`**。
     - `capability_routes.py:367-433` 中的 `skill_resource`（覆盖 `skill_files` 与 `skill_read`）和 `action_result` 均运行在 `async with svc.verified_read(...) as selected:` 锁保护上下文中；且 `action_result` 在锁内进一步校验 `bool(selected["runtime"].get("tools"))`、`not selected["runtime"].get("formal_probe")` 及 `call["detail"].get("method") == selected["runtime"].get("method")`。
     - 实测 `tests/test_skill_package_db.py:301-391`（`test_skill_read_cannot_follow_a_turn_change_while_waiting_for_lock[False/True]`）验证：当旧轮 `skill_read` / `skill_files` 通过锁外初检后阻塞在 `_locked_session`，期间新轮完成旧 `scope`、切换 Skill 并以同一 `gateway` 准备新 `scope`，旧请求获锁后会在锁内复核阶段被拦截并抛出 `Forbidden("... another execution turn")`，不会读出新轮 Skill 文件或新轮列表。
   - **迟到 `turn/start` ACK 精确绑定 `prepared_scope`**（`knowbench-backend/app/app/application/workbench/runner.py:198-212, 900, 1009, 2593, 2611`、`capability_repository.py:243-246`）：
     - `prepare_capabilities` 在准备完成后立即捕获局部变量 `prepared_scope = self.capability_scopes.get(thread_id)`，并在收到 `turn/start` 返回后将该 `prepared_scope` 显式传给 `record_capability_turn(thread_id, turn_id, prepared_scope)`（内部同时通过 `for_update=True` 锁住会话并核对 `session.get("thread_id") == thread_id`）。
     - `capability_runtime_event(..., started=True)` 的 SQL 条件限定 `WHERE session_id=:s AND runtime->>'scope_id'=:scope AND runtime->>'status'='prepared'`。
     - 实测 `tests/test_skill_package_db.py:393-435`（`test_delayed_runner_ack_cannot_bind_replacement_skill_scope`）验证：若下一轮 `prepare_capabilities` 已将 `runtime.scope_id` 更新为 `replacement`，上一轮迟到的 `record_capability_turn(thread, "late-ack", first)` 因 `scope_id` 不匹配不会覆写新轮 `replacement` 作用域。

3. **条件 3（同轮正常结束后的待审批保留 vs 取消/换轮/接管/重连失效，以及 `turn/start` ACK 前停止与针对更早轮次停止的区分）—— 已闭合**
   - **同轮正常完成与换轮失效**（`knowbench-backend/app/app/application/workbench/capabilities.py:1209-1210, 1762-1779`）：
     - 轮次正常完成（`turn/completed` 且 `status == "completed"`）时，`runtime.status` 置为 `"completed"`、`aborted=False`，同时保留当前轮的 `runtime.token_hash` 与 `runtime.turn_id`。因此该轮已挂起的会话级审批（`intent["runtime"] == selected["runtime"]["token_hash"]` 且 `intent["invocation"]["turn_id"] == selected["runtime"]["turn_id"]`）在 15 分钟 Interaction TTL 内仍可精确批准执行（方法步骤除外，`capabilities.py:1776-1779` 额外要求方法步骤必须在 `runtime.status in ("prepared", "applied")` 的活跃轮次内批准）。
     - 一旦下一轮执行 `prepare()`，即使 `gateway_hash` 复用，每轮 `runtime.token_hash` 也会轮换为全新随机值且 `turn_id` 重置，上一轮未决审批在 `decide()` 中因 `turn_id` 或 `token_hash` 失配被立即拒绝。
   - **用户显式停止（含 `turn/start` ACK 之前停止与针对更早轮次的停止）**（`knowbench-backend/app/app/application/workbench/session_service.py:277-307`、`capability_repository.py:321-328`、`workbench_routes.py:779`）：
     - `POST /workbench/sessions/{session_id}/interrupt` 调用 `SessionService.interrupt_user_turn(session_id, owner, body.turn_id)`，在会话行锁（`for_update=True`）内处理：
       - 若 `runtime.status in ("prepared", "applied")` 且（`turn_id is None` 或 `turn_id == runtime.get("turn_id")`），立即将 `runtime` 置为 `{"status": "completed", "aborted": True}`，当下即刻吊销网关访问权与该轮待审批记录（`decide()` 检查 `selected["runtime"].get("aborted")` 拒绝批准）。
       - 若 `runtime.status == "prepared"` 且传入了具体的 `turn_id`（此时 `turn/start` 尚未返回绑定 `runtime.turn_id`），则写入 `runtime["pending_stop"] = True` 并入队 `kind='turn.interrupt', payload={'turn_id': turn_id}`。当随后 `turn/start` ACK 到达并调用 `capability_runtime_event(..., started=True)` 时，SQL 分支 `CASE WHEN runtime ? 'pending_stop' AND EXISTS (SELECT 1 FROM workbench_commands WHERE session_id=:s AND kind='turn.interrupt' AND payload->>'turn_id'=:t)` 仅在 `turn_id` 精确匹配该中断命令时原子转为 `status='completed', aborted=true`；若中断命令针对的是更早轮次（如 `"earlier-turn"`），当前新启动的轮次（如 `"starting-turn"`）正常绑定为 `status='applied'`。
     - 实测 `tests/test_capabilities_db.py:677-737`（`test_stable_gateway_does_not_renew_pending_approval_or_cancelled_turn` 与 `test_interrupt_before_ack_only_revokes_matching_turn[starting-turn/earlier-turn]`）完整覆盖上述场景。
   - **Sandbox 断线重连与 Runner 接管吊销**（`knowbench-backend/app/app/application/workbench/runner.py:218-236`、`capability_repository.py:285-290`）：
     - `SandboxLink.ensure_connected` 在建立新 `AppServerConnection` 之前清空 `live_threads`、`search_scopes`、`capability_config`、`capability_scopes`，拒绝内存态 `pending_approvals`，并调用 `await self.runner.expire_approvals(self.sandbox_id, "connection to the sandbox re-established")`。
     - `abort_sandbox_capability_turns` 通过 `SET runtime=(runtime - 'gateway_hash') || cast(:patch as jsonb)` 显式剥离 `gateway_hash` 并标记 `completed` / `aborted`，确保重连或接管后旧 `gateway` 既无法继续访问，也无法被后续 `prepare()` 复用。

4. **条件 4（Codex `0.170.0` 基线对齐、私有试用显式关闭 `view_image`、精确握手校验与 `0.155.1` 历史证据配对兼容）—— 已闭合**
   - **版本基线与精确握手校验**（`knowbench-backend/app/app/domain/workbench/projects.py:15`、`provisioning.py:69`、`workbench_register.py:37`、`runner.py:324, 428`）：
     - `CODEX_VERSION = "0.170.0"` 已统一作为默认基线；`SandboxLink.configure_formal_probe`（`runner.py:324`）使用正则 `rf"^[^\s/]+/{re.escape(CODEX_VERSION)}(?:\s|$)"` 校验 `server_info.userAgent` 精确版本 token（拒绝 `0.155.1`、`0.170.1`、`0.170.00` 等变体）。
   - **私有试用 `features.view_image: False` 与新旧证据精确配对**（`knowbench-backend/app/app/domain/workbench/formal_model.py:10-42`、`formal_method_catalog.py:131`、`formal_model_evidence.py:104`）：
     - `PROBE_CONFIG` 在原有 6 项隔离配置基础上新增 `"features.view_image": False`，关闭 `0.170.0` 默认开启的原生 `view_image` 工具；`_PREVIOUS_PROBE_CONFIG` 保留 `0.155.1` 的 6 项配置。
     - `verified_probe_profile(evidence)` 强制实施版本与配置的一一绑定：`0.170.0` 证据必须匹配 `version == "codex-0.170.0/formal-probe-v1"` 且 `applied_config == PROBE_CONFIG`（含 `features.view_image: False`）；已冻结的 `0.155.1` 历史证据必须匹配 `version == "codex-0.155.1/formal-probe-v1"` 且 `applied_config == _PREVIOUS_PROBE_CONFIG`（不允许跨版本混配配置）。
   - **离线探针、镜像与 Link 打包源核对**：
     - `knowbench-backend/scripts/probes/codex_mcp_provenance.py:49-58, 275-372` 与 `sunmoonun/scripts/results/codex-0170-mcp-20261119.json`：验证同一线程/网关连续两轮 `turn/start` 期间 MCP `initialize` 计数不增加（保持为 1），且两轮 `mcpToolCall` 的 `(turn_id, call_id)` 均精确匹配。
     - `knowbench-backend/app/scripts/probes/formal_model_isolation_probe.py:18-24, 98-100`：校验 `codex-cli 0.170.0` 并注入 `"features.view_image": False`。
     - `sunmoonun` 提交 `5b11c85639cba4c7dedfd09f97bc39db8e14ee59`：`infrastructure/applications/component-images/sandbox-platform/image/Dockerfile` 的 `ARG CODEX_VERSION=0.170.0` 与文档已同步更新，本地 `wsl-dev` 已构建 `luna-local/sandbox:codex-0.170.0`（`d81a7ceaf95f`）。
     - `sunmoon-link` 提交 `318f79e54cfe2be27fc9ceb722d172a8e757d975`：Link `0.5.9`（`windows-x64.json`、`linux-x64.json`、`package.json`、`pnpm-lock.yaml`、`windowsPolicy.ts` 等）已锁定 `@openai/codex` `0.170.0`。

## 验证结果与范围边界

### 1. 本地（`wsl-dev`）独立实测结果

在 `wsl-dev`（`/home/zymun/worktrees/luna/knowbench-app/knowbench-backend`）使用独立临时 PostgreSQL 16 容器实例（`127.0.0.1:55439`，测试结束后自动销毁）及虚拟环境 `.venv` 完整执行 `request.md` 要求的全部验证命令与静态检查：

1. **MCP 能力、工具调用与 Skill 包实库回归**：
   - 命令：`.venv/bin/python -m pytest -q tests/test_capabilities_db.py tests/test_capability_runner.py tests/test_tool_invocation_db.py tests/test_skill_package_db.py`
   - 结果：**`72 passed in 27.66s`**
2. **方法能力绑定、C2 共同核权 Runner 与工作台计费/用量实库回归**：
   - 命令：`.venv/bin/python -m pytest -q tests/test_method_capabilities_db.py tests/test_method_permission_runner_db.py tests/test_workbench_usage_db.py`
   - 结果：**`24 passed in 34.38s`**
3. **正式模型隔离证据与运行时握手/配对回归**：
   - 命令：`.venv/bin/python -m pytest -q tests/test_formal_model_evidence.py tests/test_formal_model_runtime.py`
   - 结果：**`53 passed in 0.81s`**
4. **静态检查（Ruff & Pyright）**：
   - 对 `ac19fbf..de6e586` 变更涉及的全部 Python 源码与测试文件执行 `.venv/bin/ruff check`：**`All checks passed!`**
   - 对变更涉及的应用层 Python 文件执行 `.venv/bin/pyright`：**`0 errors, 0 warnings, 0 informations`**

### 2. 范围边界确认

- 本次复核严格在本地 `wsl-dev` 开发环境与离线探针结果范围内完成，确认达到开发候选完成标准（对应 Luna 待办第 3 项、接入实施方案 §17.6 第 5 项）。
- 生产/预发集群的 Sandbox 镜像 Tag 切换、Link 产物上传分发、以及真实已授权 `gpt-5.4` 端点下的 `formal_model_isolation_probe.py` 联调证据重采，按 `request.md` 与 `CHECKPOINT.md` 约定留待集群维护窗口与具备真实模型凭证时单独执行。
