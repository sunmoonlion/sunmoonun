# qwen 回执

- 对应请求：[../request.md](../request.md)
- 本轮：第1轮
- 实际检查版本：
  - 目标提交：`knowbench-backend` `614d0bdc868d3255360c754049a9020d329372f2`（基线 `34f516920ef667907a4b81acd83419ecbde0c8bf`）、`knowbench-app` `154b1cb65b708bf3cc2b68583fc4780b0657d176`（基线 `c138150330dcd0f16b8bb5c4736b8c84051438b8`）。
  - 工位当前后续跟进提交（已一并核对兼容性）：`knowbench-backend` `d3f7dbad9bbad7bcd576f6d1716b8dfb2117c4cc`、`knowbench-app` `c28aafcc225f430f0095b8ebc35dfe7c4f9d2a50`。
- 结论：**本增量通过。适用范围：迁移 `20261114_0041` 原地改名 `workbench_calls` 与历史证据保全、平台/KnowBase/外部 MCP/脚本共用调用账、真实宿主调用键唯一约束与幂等回放、Task 根方法调用身份关联与状态投影、受管审批接口视图隔离。本增量通过不代表 C2 完成或方法能力可开放，不授权生产迁移、部署或开放作者/脚本入口。**

## 发现

- **F01（必须重点核对的 6 项检查全部通过）**
  1. **0041 迁移保全证据与脚本空连接隔离**：`app/alembic/versions/20261114_0041_calls.py:11-43` 原地将 `workbench_capability_calls` 改名为 `workbench_calls`，解除 `connection_id` 非空限制并新增 `source_asset_id`、`kind`、`origin`、`call_key`、`parent_call_id`、`task_id`、`attempt_id`、`registration_id`、`registration_digest`。历史记录保留原 `id`、`digest`、`interaction_id` 与 `detail`；旧 `awaiting_approval` 转为 `expired`、旧 `dispatching` 转为 `unknown`、非空 `runtime` 标记 `status='completed', aborted=true`，不重放未结算外部动作。当资产 `kind='skill'` 时，迁移与新写入路径（`capabilities.py:678-715, 1006-1010, 1138-1155`）及公开回执 `public_call`（`skill_execution.py:57-73`）均将 `source_asset_id` 设为技能资产 ID、将 `connection_id` 设为 `None`，并剥离内部审计列。
  2. **调用键唯一性、并发串行化与防串账**：数据库层建立 `uq_calls_invocation UNIQUE(owner_actor_id, session_id, call_key)`、`uq_calls_owner_session_id UNIQUE(owner_actor_id, session_id, id)` 及复合外键 `fk_calls_parent FOREIGN KEY(owner_actor_id, session_id, parent_call_id) REFERENCES workbench_calls(owner_actor_id, session_id, id)`，从约束层杜绝跨用户/跨会话关联父调用。`CallRepositoryMixin.add_call`（`call_repository.py:34-76`）采用 `INSERT ... ON CONFLICT(owner_actor_id, session_id, call_key) DO NOTHING RETURNING *`，冲突时回查既有行；`CallLedger.begin`（`calls.py:82-121`）核对 `call["digest"] == identity` 且 `call["origin"] == "platform"`，若同一 `call_key` 携带不同参数或跨源复用则抛出 `RecordsRefused`，仅 `fresh == True`（`call["id"] == call_id`）的首次请求进入 `dispatch`。
  3. **Task 根记录稳定性、重试关联与状态投影**：`call_context`（`calls.py:16-74`）在事务内对 `workbench_tasks` 加 `FOR UPDATE` 行锁，以 `call_key = "task:" + str(task_id)` 和部分唯一索引 `uq_calls_root_task` 确保每个 Task 最多一条根方法记录（`kind='method', parent_call_id IS NULL`）。同一 Task 换新 `Attempt` 重试时复用同一 `root["id"]` 作为 `parent_call_id`，并在工具调用行单独记录当前 `attempt_id`，不重复生成方法根身份或记费；普通聊天（`task_id=None`）不造虚构父节点。`WorkbenchRepository.cas_task`（`repository.py:1062-1064`）在更新 Task 状态时同步调用 `update_method_call_state`，单向投影原 Task 状态。
  4. **平台守卫前置、缓存回包安全与 KnowBase 目录缓存复用**：`workbench_mcp.py:206-263` 中 `guard.check(name, args, params.get("_meta"))` 严格位于 `ledger.begin` 之前，未通过宿主事件或任务状态核验的请求无法读取已缓存回包。当 `not fresh` 时，若 `detail.response` 为空（如仍在 `dispatching` 或超时恢复为 `unknown`），直接返回拒绝重发提示而不二次调用 `dispatch`；若已有回包则剥离旧传输层 `id` 后按当前 JSON-RPC `id` 回放。KnowBase 中继调用通过 `await relay.tools()`（`workbench_mcp.py:223`）读取 `DataRelay` 既有内存缓存目录以构造 `ToolRegistration`，仅在缓存未命中时发起一次 `tools/list`。`dispatch`（`workbench_mcp.py:265-336`）对畸形结构、`NaN`/`Inf` 非有限数值及超 `TOOL_RESULT_MAX_BYTES` 回包统一记为 `unknown` 且 `isError=True`，不误记 `succeeded`。
  5. **受管审批接口隔离与证据分工**：`capability_repository.py:277, 288, 314` 中 `capability_calls`、`capability_call_by_invocation`、`capability_call` 均限定 `WHERE origin='managed'`，平台工具调用（`origin='platform'`）与方法根记录（`origin='method'`）不进入能力审批列表，也不能被 `/workbench/capability-calls/{call_id}/decision` 误操作。批准真源仍为 `workbench_interactions`，计算与读数证据保持原表并由调用回包引用。
  6. **0041 降级保护**：`20261114_0041_calls.py:46-51` 在 `downgrade()` 开头检查 `EXISTS(SELECT 1 FROM workbench_calls WHERE origin <> 'managed')`，存在方法或平台调用记录时显式报错拒绝有损降级。

- **F02（两处非阻断实现细节记录，其中迁移测试耦合已在 `d3f7dbad` 同步更新）**
  1. `test_capabilities_db.py:603` 在 `614d0bdc` 中改为单独对 `20261114_0041_calls.py` 执行 `downgrade()/upgrade()`；当后续提交 `d3f7dbad` 新增带外键引用 `workbench_calls` 的 `20261114_0042_authorizations.py` 时，单独降级 `0041` 会因外键依赖失败，`d3f7dbad` 已将该测试更新为按 `0042 -> 0041` 顺序成对降级与升级。
  2. `workbench_mcp.py:304-310` 中，平台本地工具在 `call()` 内部抛出 `WorkbenchError`（如业务参数被 `RecordsRefused` / `ComputeRefused` 拒绝）时，`dispatch()` 返回 `status="unknown"` 并由 `ledger.finish` 保存 `_tool_error` 回包。同一宿主 `call_id` 重复请求时会直接回放该错误回包且不重跑，行为保守安全（fail-closed）；若后续审计需要区分“本地确定性业务拒绝（无外部副作用）”与“跨服务/异常结果未知”，可在状态枚举或 `detail` 原因码中进一步细分，不影响本增量正确性。

- **F03（本增量未完成项与后续边界）**
  - 本增量（`614d0bdc`）仅建立共同调用表与根 Task 调用关联。后续提交 `d3f7dbad` / `b0d37999` 进一步补充了步骤级方法调用身份（`step_call`）、`0042` 持久运行授权与撤权接口、`formal-method/v1` 结构编译候选，但以下 C2/C3–C6 项仍未完成：
    1. 嵌套子方法展开、正式方法工具直接派发与专家/专家团编排运行贯通；
    2. KnowBase 数据与本地工作区（`workspace`）子范围委派，以及运行中撤权后的完整恢复；
    3. 正式方法孵化准入服务（真实验证证据核查、来源归属与许可 C-L4、工作稿/冻结/登记衔接及前端孵化入口）；
    4. 只读范围授权复用、稳定 MCP 配置（C3）、Skill 内容分离存储（C4）、跨工具方法编排产物交接（C5）及连接器生命周期（C6）。

## 验证

在 `/home/zym/worktrees/qwen/knowbench-app/knowbench-backend/app` 下使用现有隔离 PostgreSQL（`127.0.0.1:55432/knowbench_tests`，凭据从私有 `pg.env` 读取，未输出到任何日志或回执）串行复验：

1. **共同调用记录、0041/0042 迁移、双 MCP HTTP 入口、方法权限、runner、脚本与契约回归**
   - 命令：`.venv/bin/python -m pytest -q tests/test_method_access.py tests/test_method_access_db.py tests/test_tool_operations.py tests/test_tool_operations_db.py tests/test_tool_invocation_db.py tests/test_capabilities_db.py tests/test_method_capabilities_db.py tests/test_skill_execution_db.py tests/test_method_tools_db.py tests/test_capability_routes_db.py tests/test_skill_package_db.py tests/test_workbench_mcp_routes.py tests/test_method_runner_mcp_db.py tests/test_tool_registry.py tests/test_capability_mcp.py tests/test_capability_runner.py tests/test_skill_dependencies_db.py tests/test_skill_dependencies.py tests/test_config_security.py tests/test_kernel_invariants.py tests/test_layering.py tests/test_call_outcomes.py tests/test_calls_db.py tests/test_calls_mcp_db.py`
   - 结果：**203 passed, 0 failed, 0 skipped**（耗时 `174.24s`，包含本卡重点要求的 `test_call_outcomes.py`、`test_calls_db.py`、`test_calls_mcp_db.py`、`test_workbench_mcp_routes.py`、`test_method_tools_db.py`、`test_method_runner_mcp_db.py` 全部用例）。
2. **静态与格式检查**
   - `.venv/bin/ruff check .`：All checks passed。
   - `.venv/bin/pyright`：`0 errors, 0 warnings, 0 informations`。
   - `git -C /home/zym/worktrees/qwen/knowbench-app/knowbench-backend diff --check 34f516920ef667907a4b81acd83419ecbde0c8bf..614d0bdc868d3255360c754049a9020d329372f2`：通过（无空白或格式错误）。
3. **未运行与依赖条件**
   - 未跑完整后端全量测试集；未做固定版 Codex 真机协议或真实外部供应商验收；未执行生产库迁移。

## 交回

- 未修改任何被评代码，未清理他人进程，未执行生产迁移或部署。
- 回执文件：`docs/sync-cowork/requests/luna/2026-11-14-C2共同调用记录增量复审/replies/qwen.md`。
- 尚待处理项：由 luna 继续推进上述 F03 所列未完成项及发布前全量验证；本回执已提交至 `sunmoonun`（推送状态见同步操作结果，不修改 `request.md`）。
