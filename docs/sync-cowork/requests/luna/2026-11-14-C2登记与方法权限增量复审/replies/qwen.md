# qwen 回执

- 对应请求：[../request.md](../request.md)
- 本轮：第1轮
- 实际检查版本：
  - 目标提交：`knowbench-backend` `34f516920ef667907a4b81acd83419ecbde0c8bf`（基线 `d5241e423684490095f769c84d01710c65aee872`）、`knowbench-web-frontend` `14c3bf352a53fe8d416c72568294f4698bde393e`（基线 `a9dfe11035b246f44f333df30bf20a9ff7fe901d`）、`knowbench-app` `c138150330dcd0f16b8bb5c4736b8c84051438b8`（基线 `ae5574e8411978edffe6754cb38a5808e68e5b71`）、`knowlab-backend` `57152cb45d97e9606b50baf1a5d91ad15012899a`（基线 `e4c7633d75ef9efe7d011cba8fa5f1600bc74165`）、`knowlab-app` `28a463e75568915cd11e4643dcace06d6afb0026`（基线 `59d58cc9d9ea2916f576cf3f8f42b71e42d1fc1a`）、`knowmart-backend` `b5f83b27bb02d39c983be020b0e2994de161b213`。
  - 工位当前后续跟进提交（已合入下述 F01/F02 修复）：`knowbench-backend` `d3f7dbad9bbad7bcd576f6d1716b8dfb2117c4cc`、`knowbench-web-frontend` `378923a0ae0ca8711794be2582c86b7c870de70a`、`knowbench-app` `c28aafcc225f430f0095b8ebc35dfe7c4f9d2a50`、`knowlab-backend` `b0d379996c23053aa0b8b97281dedf5e17270137`、`knowlab-app` `8925db96fded76940de2465ade6c078a74dc4f7e`。
- 结论：**本增量主体设计及代码实现通过（本卡目标提交上存在 F01 孵化请求 Schema/消费锁漏重新生成、F02 固定工作流步骤在平台工具守卫处未复核 runtime 方法能力授权两项问题，均已在当前 `qwen` 分支后续提交 `8925db96`/`c28aafcc`/`d3f7dbad` 中补齐并通过复验）。适用范围仅限共同工具登记、双 MCP 入口宿主调用身份核验、运营可信操作映射及方法根级 `access_requirements` 确认；不代表整套 C2/C3–C6 方法接入已可开放，不授权部署、开放作者入口或启用脚本。**

## 发现

- **F01（本卡目标提交 `57152cb4`/`28a463e7`/`c1381503` 漏重新生成孵化请求 Schema 与消费锁；已在 `8925db96`/`c28aafcc` 修复）**
  - **证据位置**：`knowlab-backend` `app/app/domain/knowbots/workdraft.py:155`（`class Advanced(MethodAccess)`）、`knowlab-app` `contracts/knowbot-incubation/v1/incubation-request.schema.json`、`knowbench-app` `contracts/knowlab-incubation-lock.json`。
  - **问题与影响**：`57152cb4` 将工作稿步骤 `Advanced` 改为继承 `MethodAccess`（引入 `access_requirements` 及带 `requirement_id` 的 `MethodToolBinding`）。`28a463e7` 重新生成了 `author-method/v1` 与 `v2` 的 `definition.schema.json`，但漏了同样内嵌 `WorkdraftBody` 的 `contracts/knowbot-incubation/v1/incubation-request.schema.json` 及其 `contract-manifest.json`，`knowbench-app` `c1381503` 也未同步更新 `contracts/knowlab-incubation-lock.json`。在 `28a463e7` 上运行 `tests/test_knowbot_incubation_contract.py` 会因 Schema 漂移失败。
  - **处理状态**：核查当前 `qwen` 分支后续提交，`knowlab-app` `8925db96fded76940de2465ade6c078a74dc4f7e` 与 `knowbench-app` `c28aafcc225f430f0095b8ebc35dfe7c4f9d2a50` 已补齐该生成物与消费锁，实跑 `tests/test_knowbot_incubation_contract.py` 及 `tests/test_knowbot_contract_lock.py` 已全部通过。

- **F02（本卡目标提交 `34f51692` 平台入口 `MethodToolGuard.check` 对固定流程早退且未复核受管能力 runtime 状态；已在 `d3f7dbad` 修复）**
  - **证据位置**：`knowbench-backend` `app/app/application/workbench/method_tools.py:142-166`（`34f51692` 版本）。
  - **问题与影响**：在 `34f51692` 中，`MethodToolGuard.check` 在 `if not is_dynamic(task): return` 处直接早退，导致固定工作流（`workflow`）步骤调用平台/KnowBase 工具时未像动态步骤那样核验 `attempt.refs.runtime_turn_id` 与步骤工具白名单 `step.tools`；同时当步骤声明了 `managed_capabilities` 时，平台入口未在 `MethodToolGuard.check` 内复核 `selected["runtime"]` 是否未中止（`not aborted`）且 `check_runtime_method` 仍有效。
  - **处理状态**：核查当前 `qwen` 分支后续提交 `d3f7dbad9bbad7bcd576f6d1716b8dfb2117c4cc`，`MethodToolGuard.check` 已去掉 `if not is_dynamic(task): return` 早退分支，统一核验固定/动态步骤的 `runtime_turn_id` 与 `step.tools`，并在 `scope` 含工具/技能要求时复核 `selected["runtime"]` 与 `check_runtime_method`。

- **F03（请求 8 项重点检查逐项核对结论：通过）**
  1. **共同登记与定义身份隔离**：`app/app/domain/workbench/tool_registry.py:21-72` 中 `ToolRegistration.discover` 对 `"mcp"` 与 `"skill_script"` 仅保留 `name`、`description`、`inputSchema`，剥离远端 `annotations` 等自报字段；`tool_id` 仅由 `[source, service, name]` 计算，不含用户连接 ID 或修订；`registered_call`（`app/application/workbench/tool_registry.py:50-71`）单次调用仅校验所选工具并比对 `descriptor_digest`，账号归属、活跃状态与 `revision` 在 `Capabilities` 各阶段独立核查。
  2. **双 MCP 入口持久事件核验与锁外有界等待**：`app/app/application/workbench/tool_invocation.py:37-118`（`verify_tool_invocation`）通过 runner 持久化的 `observed_mcp_call` 核对 `session_id`、`thread_id`、`turn_id`、`server`、`call_id`、工具名及规范化 JSON 参数（`allow_nan=False`），等待循环以 `observe_seconds=2`、`sleep(0.05)` 在数据库事务与行锁外执行，等待结束后重读 `session` 校验 `thread_id`/`sandbox_id` 未漂移。平台 `/mcp/workbench`（`method_tools.py:92-191`）已删除旧的“无动态任务免核来源”分支；受管 `/mcp/capabilities/{session_id}`（`capabilities.py:918-968`、`capability_routes.py:432-471`）对外部工具、`skill_files`、`skill_read`、`action_result` 均执行同一核验，并在 `request_call` 获取 `capability_selection(..., lock=True)` 行锁后以 `observe_seconds=0` 二次复核（`capabilities.py:1036-1040`）。`ToolInvocation.key` 绑定 `call_id`，同参数的不同调用不合并，超时/异常记 `unknown` 不自动重发。
  3. **运营可信操作映射与一致性拒绝**：`app/domain/workbench/tool_operations.py:16-144` 与 `app/core/config.py` 通过 `WORKBENCH_CAPABILITY_OPERATIONS` 绑定 `service_url`（必须在审核 URL 列表内）、`tool_name`、`descriptor_digest`、`capability_ref`、`version`、`operation`、`effect`（`read`/`write`/`send`）及精确 `ResourceBinding`。未核定或摘要变化时：`view` 标 `operation_unavailable`（`capabilities.py:380-415`）、`save_selection` 拒绝保存（`line 529`）、`runtime_tools` 从 `tools/list` 与 `SKILL.md` 依赖提示中剔除（`lines 99-116`）、`request_call` 在生成审批前拒绝越界参数（`lines 998-1004`）、`decide` 批准前复核 `operation == intent.get("operation")`（`lines 1264-1282`），缺失历史快照不现场补造。
  4. **独立 `access_requirements` 与首期受限边界**：`app/domain/workbench/method_capabilities.py:43-171` 中 `MethodAccess` 强制 `managed_capabilities.tools` 的 `requirement_id` 与 `access_requirements` 一一对应（禁止悬空引用或未绑定声明）；`ResourceScope` 固定 `resource_kind="connector"` 与非空精确值元组，`DataTransfer` 固定 HTTPS `destination`、顶层 `argument_fields` 与非空 `purpose`，`required_when="always"`、`on_unavailable="pause"`，未伪称支持通配、表达式或其它资源域。
  5. **网页展示确认与运行期冻结复核**：`knowbench-web-frontend/app/components/workbench/capability-panel.tsx:150-178, 284-291` 明确渲染操作、资源角色与取值、外发去向与字段、用途，并将按钮文案切换为 `confirmMethodPermissions`。`save_selection` 按当前不可伪造的 `scope["context"]` 写入 `detail["access"]`（`capabilities.py:530-559`），`prepare` 冻结至 `runtime["tools"][key]["access"]`（`lines 693-701`），`request_call` 与 `decide` 分别调用 `check_access`（`method_access.py:31-70`）核对操作摘要、资源集合子集、平台上限与顶层参数字段，每次外部调用（含读取）仍须逐次审批。
  6. **仅实现根范围、无模型自报父 ID 接口**：代码中无任何接受模型自报父调用 ID 的参数或接口；`docs/managed-capabilities.md:63-77` 已如实说明当前仅为现有 Task/Attempt 的根范围。
  7. **KnowLab 生成/校验与作者入口闸门保持关闭**：`knowlab-backend` `compile.py:785-792, 1028-1042, 1203-1217, 1587-1591` 与 `managed_authoring.py:16-24` 已同步校验 `MethodAccess` 并拦截含 `access_requirements` 或 `managed_capabilities` 的工作稿保存、编译、导入与发布（返回 `method_access_not_ready`）。无 `requirement_id` 的旧工具绑定被 Pydantic 严格模式直接拒绝。
  8. **普通聊天/工作 Skill 依赖与脚本边界**：`SkillRequirement.required_tools` 与 `SkillCreate.tool_requirements` 仍为纯技术依赖（`McpRequirement(url, name)`），不要求孵化或方法权限字段；`Capabilities.prepare`（`capabilities.py:638-661`）在会话场景下剔除失效能力并继续普通交流；`WORKBENCH_SKILL_SCRIPTS_ENABLED` 默认关闭，脚本无网络与连接器调用入口。

- **F04（仍未实现的 C2/C3–C6 项清单，严禁因本增量通过而开放方法接入）**
  - **C2 仍未完成项**：（1）嵌套方法展开、子方法调用身份及通用父子调用树（后续 `614d0bd` 与 `d3f7dba` 推进了共同调用表与步骤级持久授权，但嵌套子方法展开与编排派发仍未完成）；（2）KnowBase 数据与本地工作区（`workspace`）子范围委派及运行中撤权后的端到端恢复；（3）资源端实时账号权限核查与任务范围只读授权复用；（4）两类/三类正式方法的孵化准入服务（真实验证证据核查、来源归属与许可 C-L4、工作稿/冻结/登记衔接及前端孵化入口）。
  - **C3–C6 仍未完成项**：稳定 MCP 配置与长连接会话身份分离（C3）、Skill 正文/资源与主表分离存储（C4）、“连接器读取 → 脚本计算 → 发送”跨工具方法编排与输入/产物交接（C5）、OAuth 连接生命周期及完整连接器适配器生态（C6）。

## 验证

所有数据库测试均使用本工位既有隔离 PostgreSQL（`127.0.0.1:55432/knowbench_tests`，凭据仅从私有 `pg.env` 读取，未输出到任何日志或回执），且严格串行执行：

1. **KnowBench 权限、数据库、双 MCP HTTP、runner、Skill/脚本、调用身份与分层回归**
   - 命令：在 `/home/zym/worktrees/qwen/knowbench-app/knowbench-backend/app` 下使用 `.venv/bin/python -m pytest -q` 串行运行 `test_method_access.py`、`test_method_access_db.py`、`test_tool_operations.py`、`test_tool_operations_db.py`、`test_tool_invocation_db.py`、`test_capabilities_db.py`、`test_method_capabilities_db.py`、`test_skill_execution_db.py`、`test_method_tools_db.py`、`test_capability_routes_db.py`、`test_skill_package_db.py`、`test_workbench_mcp_routes.py`、`test_method_runner_mcp_db.py`、`test_tool_registry.py`、`test_capability_mcp.py`、`test_capability_runner.py`、`test_skill_dependencies_db.py`、`test_skill_dependencies.py`、`test_config_security.py`、`test_kernel_invariants.py`、`test_layering.py`、`test_call_outcomes.py`、`test_calls_db.py`、`test_calls_mcp_db.py`。
   - 结果：**203 passed, 0 failed, 0 skipped**（耗时 `174.24s`）。
2. **KnowBench 方法运行契约、计划与消费锁**
   - 命令：`.venv/bin/python -m pytest -q tests/test_dynamic_method_catalog.py tests/test_atomic_method_catalog.py tests/test_referenced_method_catalog.py tests/test_capability_method_plan.py tests/test_method_plan.py tests/test_fixed_plan.py tests/test_execution_plan.py tests/test_knowbot_contract_lock.py tests/test_compute_tool_contract.py` 及新增纯单测 `tests/test_method_authorization.py tests/test_method_registration.py tests/test_formal_method_provider.py`。
   - 结果：契约与计划 **160 passed, 0 failed**（`1.52s`）；方法授权/登记/契约提供方单测 **110 passed**（含与上组重叠的非 DB 用例，`3.96s`）。
3. **KnowLab 编译、作者入口限制、孵化契约生成物与消费锁**
   - 命令：在 `/home/zym/worktrees/qwen/knowlab-app/knowlab-backend/app` 下运行 `.venv/bin/python -m pytest -q tests/test_managed_capabilities.py tests/test_knowbot_workdraft_compile.py tests/test_knowbot_contract_locks.py tests/test_knowbot_incubation_contract.py tests/test_author_methods.py tests/test_dynamic_methods.py tests/test_formal_method.py`。
   - 结果：**130 passed, 0 failed, 0 skipped**（`2.71s`）。
4. **KnowMart 清单与目录消费者**
   - 命令：在 `/home/zym/worktrees/qwen/knowmart-app/knowmart-backend/app`（`b5f83b27bb02d39c983be020b0e2994de161b213`）下运行 `.venv/bin/python -m pytest -q tests/test_knowbot_contract.py tests/test_knowbot_manifest_v2.py tests/test_knowbot_manifest_v3.py`。
   - 结果：**35 passed, 0 failed, 0 skipped**（`0.56s`）。
5. **两后端静态检查与网页前端验证**
   - `knowbench-backend` `.venv/bin/ruff check .`：All checks passed；`.venv/bin/pyright`：`0 errors, 0 warnings, 0 informations`。
   - `knowlab-backend` `.venv/bin/ruff check .`：All checks passed；`.venv/bin/pyright`：`0 errors, 0 warnings, 0 informations`。
   - `knowbench-web-frontend/app`：`pnpm typecheck` 通过、`pnpm lint` 通过、`pnpm check:i18n` 通过（`1291` keys）、`pnpm vitest run tests/component/capabilities.test.tsx tests/unit/capability-contract.test.ts` **2 files / 17 tests passed**（`7.30s`）。
6. **未运行与依赖条件**
   - 未重跑两后端完整全量测试集；未做真实 Codex app-server 二进制协议联调、未连接真实外部 MCP 供应商账号、未触碰生产数据库。

## 交回

- 未修改任何被评业务仓代码，未部署，未开放作者入口或脚本开关。
- 回执文件：`docs/sync-cowork/requests/luna/2026-11-14-C2登记与方法权限增量复审/replies/qwen.md`。
- 尚待处理项：由 luna 继续推进上述 F04 所列剩余 C2/C3–C6 项及最终全量验证；本回执已提交至 `sunmoonun`（推送状态见同步操作结果，不修改 `request.md`）。
