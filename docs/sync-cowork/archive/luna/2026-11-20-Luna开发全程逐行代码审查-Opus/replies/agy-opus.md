# Luna 开发全程逐行代码审查回执

- **对应请求**：[request.md](../request.md)
- **执行角色与实际模型**：`agy`（独立主审）；**实际执行模型：Gemini 4 Neon**（原请求指定 Opus，所有者于 2026-11-20 明确改由 Gemini 4 Neon 执行，特此如实注明；回执按约定写入本文件 `replies/agy-opus.md`）
- **审查日期**：2026-11-20
- **工作位置**：本地 `wsl-dev`（`/home/zymun/worktrees/luna`，经 `git archive` 严格固定在 `request.md` 指定的 12 仓审查终点提交进行源码审计与隔离实测；未修改任何受审代码、测试或 `request.md`）
- **逐文件覆盖台账**：[逐文件覆盖记录.tsv](逐文件覆盖记录.tsv)（**898/898 路径全覆盖，0 项待审**）

---

## 一、总体结论与发版研判

**结论：不建议按所审 12 仓固定候选原样全量开放上线；本轮全量逐行审查共定位 21 项发现（2 项 P0 / 跨服务阻断、5 项 P1 高危缺陷、6 项 P2 中危缺陷、8 项 P3 工程建议），并已锁定 `test_after_a_decline_even_allowed_changes_ask_and_say_so` 拆库死锁的精确根因及其对生产停机的租约脑裂影响。**

按风险分层研判：
1. **必须立即修复的发版/生产阻断（F01–F05、F07）**：
   - **F01（P0）**：`sunmoonun/infrastructure/applications/component-images.yaml` 仍将 `sandbox-provisioner` 与 `sandbox` 构建修订号钉在旧提交，遗漏第 8、9 项全部隔离脚本协议与计量变更；按 `ci/release.groovy` 构建发版将导致线上脚本准备/输入/计量全线 404/协议不兼容。
   - **F02（P0/P1）**：KnowLab 调用 KnowBench 的 `POST /internal/v1/knowbot-runtime/formal-method-executions/{run_id}/cancel` 跨服务契约完全断裂（KnowLab 发 JSON Body，KnowBench 声明为必填 Query 参数），**实测必报 HTTP 422**，正式方法测试取消在生产完全失效。
   - **F03（P1）**：`AppServerClient.close()` 不取消也不等待 `_reader`、`_safe_server_request` 未追踪，且 `Runner.run_forever()` 停机前从未等待/取消 `self.driving` 与连接读循环就立即 `release_leases()`。这既是 `test_after_a_decline_even_allowed_changes_ask_and_say_so` 拆库 `workbench_attempts` 死锁的直接根因，也会在生产滚动升级 SIGTERM 时造成旧进程孤儿协程与新租约持有者并发写库脑裂。
   - **F04（P1）**：`POST /workbench/capability-calls/{call_id}/decision` 捕获 `TestManagedInKnowlab` 后白名单漏了 `"formal_script"`，独立审批端点返回 409。
   - **F05（P1）**：KnowMart 正式方法上架/审核/获取（含每次买家 `runtime=True` 取最大 4 MiB Skill 包）持 `formal_method_listing` 行排他锁（`FOR UPDATE`）跨越外部 HTTP 调用，并发使用同一上架方法会串行锁死并打满连接池。
   - **F07（P1）**：KnowBench `approve_knowbase_read` 缺少 `expires_at` 上界校验；同时一阶编排多步同资料读取共享同一 `parent_ref`，后续步骤过期时间晚于首步将必触 KnowBase 409 `method_parent_changed`。
2. **关于工位最新 HEAD 与既有分项回执的同步说明**：
   - 核对时发现 Luna 已在提交本次审查范围之后处理了 C5 分项回执的 5 条建议（对应本报告 **F06、F10、F14**，落在后续提交 `4aa68b7d` / `11a3fd72` / `9edd61e02`）并经 Jenkins #96 发布了 `release-20261120-1`（保持 `WORKBENCH_SKILL_SCRIPTS_ENABLED=false`）。
   - **只读复核当前 `wsl-dev` 工位最新 HEAD 显示：本轮新发现的 F01、F02、F03、F04、F05、F07、F08、F09、F11、F12、F13 在当前 HEAD 上仍然全部存在**，建议 Luna 纳入下一轮修复单优先清零后再放开脚本开关与正式方法测试/市场入口。

---

## 二、实际审阅的 12 仓固定提交与覆盖统计

| 仓 | 范围起点（排除） | 审查终点（包含，实际审计提交） | 路径数 |
| --- | --- | --- | ---: |
| `sunmoonun` | `47e1b05a57462d3b5195173e9066f4f8ccbdc10f` | `d67e1a296fa0f7b3329e6b9f96636a477ebf398e` | 450 |
| `knowbench-app` | `f7c934c50f8a3a960b70aaa35ec163899221069f` | `b9498b59a36dcab369176e06871eb1f9b5051147` | 11 |
| `knowbench-app/knowbench-backend` | `3cb341fedf9516ee949a477a555ced22017b448c` | `5d86118f2473901b0e1673b89f9efd191ebd08b3` | 250 |
| `knowbench-app/knowbench-web-frontend` | `67a74c703a9c0adb78d82d3a2648687f17b89ca5` | `63b5a7c729babae356441773f4048c2d3976a93c` | 35 |
| `knowlab-app` | `7e1bbba94d1bd559698b1862b56f3ce59f4b579e` | `8bbce621c053a861d8e7bcfad1b6ebdeb4c67163` | 21 |
| `knowlab-app/knowlab-backend` | `08376387809080c6e102fee3eb2c05b72920d9c9` | `e7e3c5451492c116cf094c480a974c2068b71018` | 40 |
| `knowlab-app/knowlab-web-frontend` | `36fd5c70cdd8a643198a0fb6111dd268f1d1e879` | `7eb57a755c676e6208dd1b33abf1e30af81e6145` | 34 |
| `knowbase-app` | `fe2c238e34e5c99d0793442ca3142c89e8d0fc2a` | `9552fba44565e0a71b5a8f0d9d921b217537bbba` | 5 |
| `knowbase-app/knowbase-backend` | `31e7ffb876216e5d14ddac867823c78355c89d6a` | `906f88aeaf8bd6f08495cb16ff3a34151909d9b5` | 13 |
| `knowmart-app` | `f1b56537f4c15c3dda66fdd970200cd4c1adfbce` | `bbc14059920140252c9ebf4977ee763d5c3c71ed` | 1 |
| `knowmart-app/knowmart-backend` | `b5f83b27bb02d39c983be020b0e2994de161b213` | `090da88031ef0fa0b6db1300acc778ed41d7c050` | 13 |
| `sunmoon-link` | `8860d2367308efefcb7c68287f83f091ae17a0f1` | `13f2c81842b9342557246d370626d75546df1088` | 25 |

**898 条路径覆盖汇总**（明细见 [逐文件覆盖记录.tsv](逐文件覆盖记录.tsv)）：
- `已逐行审`：**381**（12 仓全部生产源码、13 份数据库迁移、部署清单/RBAC/供给器/沙箱镜像/流水线、联调脚本、核心测试与构建/国际化配置）；
- `指针对账`：**72**（6 个父仓子模块 gitlink、跨仓契约 Schema/样例/消费锁与 7 个自动生成 Python 模块）；
- `历史核对`：**58**（15 个已删文件与 43 个历史路径，均已核对父提交与演进日志）；
- `证据或文档核对`：**387**（288 个 `scripts/results/*` 实测产物及协作请求/回执/总纲/交接文档）；
- `待审`：**0**；
- 另经脚本校验：KnowBench Web 与 KnowLab Web 的 `en.json` / `zh-CN.json` 键集合差集均为 0。

---

## 三、按影响排序的审查发现（F01–F21）

### P0 / 阻断级

#### F01 [P0 · 已证实缺陷 · 发版阻塞] 供给器与沙箱镜像构建修订号严重落后，遗漏第 8、9 项协议与计量代码
- **固定提交与位置**：`sunmoonun` `d67e1a296fa0f7b3329e6b9f96636a477ebf398e`，`infrastructure/applications/component-images.yaml:22, 37`
- **触发条件**：按 `ci/release.groovy` 读取 `component-images.yaml` 构建并发布 `sandbox-provisioner` 和 `sandbox` 镜像，随后在目标集群开启隔离脚本或执行 `gitops/components/sandbox-platform/provisioner/verify.py`。
- **预期 vs 实际**：
  - 预期：`sandbox-provisioner` 与 `sandbox` 的 `revision` 指向包含第 8 项一次性 stdin 输入流（`36d980961`）、第 9 项容器计量与停止协议（`e72eaea08`）及观测日志（`7769c48a8`）的修订提交。
  - 实际：L22 `sandbox-provisioner` 仍钉在 `8fee0080a5b71d0f7e889000dbf74ec267eb2fe3`（早于 `/prepare`、`/input`、`/stop-metered`、`/container-meter` 和 NetworkPolicy 409 竞态修复）；L37 `sandbox` 仍钉在 `5b11c85639cba4c7dedfd09f97bc39db8e14ee59`（缺少新版 `image/skill_execute.py` 的 stdin 帧协议、`SUNMOON_INPUT_ACCEPTED` 回执和 `SUNMOON_INPUT_DIR`）。
- **受影响的人或数据**：所有开启隔离脚本的环境与集群发布；上线后隔离脚本准备、具名资料/前序产物输入、计量与停止全线 404 或协议失败。
- **证据**：静态核对 `d67e1a29:infrastructure/applications/component-images.yaml` L22/L37（且复查工位最新 HEAD `e517ba37` 仍未更新）。
- **建议**：在发布或开启 `WORKBENCH_SKILL_SCRIPTS_ENABLED` 前，将两处 `revision` 同步升级至包含最新 `sandbox-platform`（含 C5 修订 `9edd61e02`）的提交，并在发布前脚本增加 `component-images.yaml` 与 `sandbox-platform/` 最新提交的一致性校验。
- **交叉核对**：既有分项 `agy` 回执（第 8、9 项）因本地 KIND 使用手工临时构建镜像而漏检此发版配置滞后。

#### F02 [P0/P1 · 已证实缺陷 · 跨服务契约断裂] 正式方法测试取消接口 JSON Body 与 Query 参数不匹配，生产必报 HTTP 422
- **固定提交与位置**：
  - `knowlab-app/knowlab-backend` `e7e3c5451492c116cf094c480a974c2068b71018`，`app/app/infrastructure/external/knowbot_clients.py:228-234`
  - `knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/interfaces/endpoints/knowbot_runtime_routes.py:180-186`
- **触发条件**：作者在 KnowLab 发起任意正式方法试跑后，点击“取消运行”，KnowLab 后端调用 `cancel_formal_method_execution(runtime, subject, run_id)`。
- **预期 vs 实际**：
  - 预期：KnowBench 收到请求并取消对应 `run_id`，返回取消后的执行状态。
  - 实际：KnowLab L229-233 发送 `POST /formal-method-executions/{run_id}/cancel`，携带 `json={"owner_subject": subject}`（无 query string）；而 KnowBench L180-182 定义为 `async def cancel_formal_execution(caller: FormalCaller, run_id: UUID, owner_subject: str, svc: FormalExecutionService)`，在 FastAPI 中裸 `str` 参数默认绑定为**必填 Query 参数**而非 JSON Body。实际跨服务请求 100% 触发 **HTTP 422**。
- **受影响的人或数据**：所有在 KnowLab 调试/测试正式方法的作者——无法从 KnowLab 取消运行中的正式方法测试（包含高耗时模型探针、等待审批或隔离脚本测试）。
- **证据**：在 `wsl-dev` 基于 `git archive 5d86118f` 通过 FastAPI `TestClient` 实测 `/internal/v1/knowbot-runtime/formal-method-executions/{run_id}/cancel`：
  - 路由参数元数据：`query_params: ['owner_subject']`, `body_params: []`；
  - 按 KnowLab 实际载荷 `POST ... json={"owner_subject": "user-123"}` 返回：`HTTP 422 {'detail': [{'type': 'missing', 'loc': ['query', 'owner_subject'], 'msg': 'Field required', 'input': None}]}`；
  - 改为 Query 参数返回 `HTTP 200`。（复核工位 HEAD `4aa68b7d` 仍未修复。）
- **建议**：在 KnowBench 定义显式 Pydantic Body 模型（如 `FormalExecutionOwner(BaseModel): owner_subject: str`）接收 JSON Body（与同路由文件 `submit_formal_execution` / `decide_formal_execution` 保持一致），或在双方统一改为 Query 参数；同时补一条跨服务真实 HTTP 环回测试，避免双边单测各自 mock 掩盖协议断层。
- **交叉核对**：既有分项 `agy` 回执未覆盖 KnowLab→KnowBench 真实 HTTP 取消链路，导致该缺陷遗漏至今。

---

### P1 / 高危缺陷

#### F03 [P1 · 已证实缺陷 · `request.md` 重点死锁根因及真实停机脑裂] Runner 与 AppServerClient 后台协程未收尾导致测试拆库死锁与生产停机租约脑裂
- **固定提交与位置**：
  - `knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/infrastructure/workbench/app_server_client.py:91-93, 108-115, 132-137, 155-163`
  - `knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/application/workbench/runner.py:1964-1966, 2240-2262, 2911-2916`
  - `knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/tests/test_workbench_runner_db.py:2054-2098`、`app/tests/test_workbench_ledger_db.py:51-84`
- **触发条件**：
  1. 测试场景：审批/通知尾包尚未结束时测试调用 `wait_drivers()` + `link.client.close()` 并进入 `db` fixture teardown 执行 `DROP SCHEMA CASCADE`；
  2. 生产场景：Kubernetes 滚动更新或缩容向 Runner Pod 发送 SIGTERM 触发 `Runner.stop()`。
- **预期 vs 实际**：
  - 预期：关闭连接前先排空/取消所有 `driving`、`script_receipts`、`_steer`、`_reader` 及在途 `_safe_server_request` 协程，确保无残余数据库事务后再释放租约或拆除测试 schema。
  - 实际：详细根因链路、实测证据与停机影响专列于 **第四节**。简言之：`AppServerClient.close()` 仅关 WebSocket 不等待/取消 `_reader`，`_safe_server_request` 与 `_steer` 为完全无追踪任务；`Runner.run_forever()` 退出循环后只取消 `script_receipts`，**完全未调用 `wait_drivers()` 或取消 `self.driving`** 即执行 `release_leases()`。
- **受影响的人或数据**：CI 偶发 PostgreSQL 死锁；生产滚动更新期间，旧 Runner 进程中尚未退出的驱动/通知协程与新抢到租约的 Runner Pod 并发读写同一 `workbench_tasks`/`workbench_attempts`/`workbench_events`。
- **建议**：见第四节完整修复方案。
- **交叉核对**：本次针对 `request.md` 重点提问独立查实，确认当前 HEAD `4aa68b7d` 仍未修复。

#### F04 [P1 · 已证实缺陷] 独立能力审批端点 `decide_call` 放行白名单遗漏 `"formal_script"`，返回 409
- **固定提交与位置**：`knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/interfaces/endpoints/capability_routes.py:610-632`
- **触发条件**：对处于 KnowLab 正式方法试跑中的 `"formal_script"` 能力调用，经独立端点 `POST /workbench/capability-calls/{call_id}/decision` 提交批准或拒绝。
- **预期 vs 实际**：
  - 预期：与 `"formal_mcp"`、`"formal_probe"` 一致，捕获 `TestManagedInKnowlab` 后委托 `trial_svc.decide(...)` 完成按 token 与 digest 绑定的审批。
  - 实际：L625-629 仅检查 `if call["detail"].get("execution_kind") not in ("formal_mcp", "formal_probe"): raise`，遗漏 `"formal_script"`，直接向外重抛 `TestManagedInKnowlab` 导致 HTTP 409。
- **受影响的人或数据**：通过该审批端点（或后续前端复用该端点）审批正式方法隔离脚本测试调用的作者。
- **证据**：源码 L625-629 与 `inspect.getsource(capability_routes.decide_call)` 核验（且当前 HEAD `4aa68b7d` 仍漏 `"formal_script"`）。
- **建议**：将白名单扩展为 `("formal_mcp", "formal_probe", "formal_script")`，并在 `test_capability_routes_db.py` 补 `"formal_script"` 审批回归用例。
- **交叉核对**：既有 C5 分项测试均走 KnowLab 转发路由 `/actions/{call_id}` 或直接调服务层，未覆盖 `/workbench/capability-calls/{call_id}/decision`。

#### F05 [P1 · 已证实缺陷] KnowMart 正式方法上架、审核与运行时取包持 `FOR UPDATE` 行锁跨越外部 HTTP 调用
- **固定提交与位置**：
  - `knowmart-app/knowmart-backend` `090da88031ef0fa0b6db1300acc778ed41d7c050`，`app/app/application/services/market.py:579-615, 626-649, 662-694`
  - `knowmart-app/knowmart-backend` `090da88031ef0fa0b6db1300acc778ed41d7c050`，`app/app/infrastructure/repositories/market.py:125-153`
- **触发条件**：多个买家并发获取同一上架正式方法，或运行时并发触发 `acquire_formal(..., runtime=True, skill=...)` 拉取最大 4 MiB 的 Skill 交付包；或 KnowBench 交付接口响应慢/超时。
- **预期 vs 实际**：
  - 预期：仅在本地状态变更短事务内持有数据库行锁；外部 HTTP 调用（`self._formal_version` -> KnowBench `POST /formal-method-delivery`）在数据库事务之外执行，或以两段式/版本校验防并发覆盖。
  - 实际：`repo.formal_listing(listing_id)`（L146-152）与 `repo.submit_formal_listing`（L133-143）无条件加 `.with_for_update()`；`submit_formal`（L583-601）、`review_formal`（L627-647）与 `acquire_formal`（L665-693，包括只读的 `runtime=True` 路径！）均在 `async with self.repo.transaction():` 内先持排他行锁，再同步等待 KnowBench HTTP 交付与 4 MiB 包体传输。
- **受影响的人或数据**：所有并发使用同一热门上架正式方法的买家和 KnowMart 数据库连接池；单次上游抖动或慢传输即可将所有并发请求串行阻塞并耗尽连接池。
- **证据**：逐行核对 `market.py:583-693` 与 `repositories/market.py:125-153`。
- **建议**：① `acquire_formal(runtime=True)` 仅需快照读（提供 `formal_listing(listing_id, for_update=False)`），完全不需排他锁；② `submit_formal` / `review_formal` / `acquire_formal(runtime=False)` 将 `self._formal_version(...)` HTTP 调用移出事务，落库短事务内复核行状态与 `delivery_digest`（或用乐观锁/条件 `UPDATE`）。
- **交叉核对**：既有第 5 项分项回执聚焦核权与字节校验，未发现跨 HTTP 持锁瓶颈。

#### F06 [P1 · 已证实缺陷 · C5 延续，固定候选存在 / 后续 `4aa68b7d` 已修] 隔离脚本运行中撤权与用户停止状态机不对称、`_collect()` 锁序倒置
- **固定提交与位置**：`knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/application/workbench/formal_script_execution.py:100-175`
- **触发条件**：
  1. 隔离脚本容器运行中（`receipt["state"] == "running"`）发生撤权，随后推进器并发检查封存或下轮对账落账；
  2. 用户点击停止（`stop_requested=True`）后遭遇 Job 不存在（`absent`）或超时（`delayed`）；
  3. 延迟对账 `_collect()` 与会话并发审批同时执行。
- **预期 vs 实际**：
  - 实际：① 运行中撤权于 L120 提前把调用改为 `failed` 且不写 `capability/action_completed` 事件，待下轮结算时因状态非 `dispatching` 跳过事件补写，并与尚未释放的 `budget.reserved > 0` 存在封存竞态；② `stop_requested=True` 遇 `absent`/`delayed` 因 L114 条件恒假而永久卡死 `dispatching`；③ L138-146 加锁顺序为 `Task -> Call -> Session`，违反全仓 `Task -> Session -> Call` 锁序。
- **受影响的人或数据**：隔离脚本开启后的正式专家运行账本、事件流与根预算封存。
- **建议**：运行中统一仅发 `stop_metered` 保持 `dispatching` 等终态单事务原子结算+写事件；`absent`/`delayed` 统一收敛 `unknown`/`failed` 保留预留；`_collect()` 改为先 `_locked_call_session` 再锁 `Call`。
- **交叉核对**：与既有 C5 分项回执 [agy.md](../../archive/luna/2026-11-20-C5专家分步执行与脚本计费复核/replies/agy.md) 第 1、2 条一致；经核对，**本轮所审固定候选 `5d86118f` 中该缺陷存在**，Luna 已在后续修订提交 `4aa68b7d` 中完成修复并复验。

#### F07 [P1 · 已证实缺陷] KnowBase 读授权 `approve_knowbase_read` 缺 `expires_at` 上界校验，且一阶编排多步同资料读取触发 409 `method_parent_changed`
- **固定提交与位置**：
  - `knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/interfaces/endpoints/capability_routes.py:520-564`、`app/app/application/workbench/knowbase_method_read.py`
  - `knowbase-app/knowbase-backend` `906f88aeaf8bd6f08495cb16ff3a34151909d9b5`，`app/app/application/services/user_run_service.py:218-240`
- **触发条件**：
  1. 调用方在 `POST .../knowbase-read/approve` 传入晚于服务端下发 `request["expires_at"]` 的 `body.expires_at`；
  2. 一阶正式编排（无固定上层 `scope_deadline`）中，两个步骤先后读取同一份 `material_id:version_no` 资料，且第 2 步交互创建晚于第 1 步。
- **预期 vs 实际**：
  - 预期：授权批准不得突破请求上限；同一任务内先后两个步骤读取同一资料，可复用既有有效父授权或独立登记而不互撞。
  - 实际：① `approve_knowbase_read`（L543-552）直接把 `body.expires_at` 传给 KnowBase 且未校验 `body.expires_at <= request["expires_at"]`；② 同任务多步共享同一 `parent_ref = formal-task:{task_id}:{material_id}:{version_no}`，第 2 步请求默认 `expires_at` 晚于第 1 步已签发 `grants[0].expires_at`，触发 KnowBase `user_run_service.py:233` `grants[0].expires_at < request.expires_at` 检查失败，抛出 **HTTP 409 `method_parent_changed`**。
- **受影响的人或数据**：多步读取同一 KnowBase 资料的正式专家编排任务（第 2 步必败）及授权期限边界完整性。
- **证据**：逐行核对 `capability_routes.py:520-564` 与 `user_run_service.py:218-240`。
- **建议**：① `approve_knowbase_read` 校验 `body.expires_at <= request["expires_at"]`（可缩不可扩）；② 为同一任务的根读授权固定任务级 `scope_deadline` 或在复用同一 `parent_ref` 时按现有有效授权截止时间取 `min(now + ttl, existing_parent_expires_at)`，避免后步推高 `expires_at` 触发 `method_parent_changed`。
- **交叉核对**：既有 C2 分项用例多为单资料或嵌套固定 `scope_deadline`，未覆盖一阶多步跨时间读同一资料。

---

### P2 / 中危缺陷

#### F08 [P2 · 已证实缺陷] KnowLab 前端硬编码仅允许 `mcp` 载体，阻断作者页面发起直调 `skill_script` 正式测试
- **固定提交与位置**：`knowlab-app/knowlab-web-frontend` `7eb57a755c676e6208dd1b33abf1e30af81e6145`，`app/components/knowbots/formal-method-execution.tsx:78-82`
- **触发条件**：作者在 KnowLab 网页打开一个 `procedure.kind === 'direct'`、`implementation.kind === 'skill_script'`、`max_model_turns === 0` 的正式方法草稿准备发起试跑。
- **预期 vs 实际**：
  - 预期：与后端 `formal_method_execution.py:290-298` 一致，允许作者从页面发起 `host`-only `skill_script` 正式测试。
  - 实际：前端 L81 仍写死 `draft.definition.procedure.implementation.kind === 'mcp'`，导致 `supported === false`，页面按钮禁用并提示不支持执行测试。（复核工位最新 HEAD `a226641c` 仍未放开。）
- **受影响的人或数据**：所有在 KnowLab 网页端孵化与测试隔离脚本工具方法的作者。
- **建议**：将 L81 调整为 `['mcp', 'skill_script'].includes(draft.definition.procedure.implementation.kind)` 并同步更新 `formal-method-execution.test.tsx` 覆盖直调脚本试跑渲染与提交流程。
- **交叉核对**：既有 C5 分项回执未发现前端条件仍锁死 `mcp`。

#### F09 [P2 · 已证实缺陷] KnowBase 正式方法原件读取对非 UTF-8 文本直接 `.decode("utf-8")` 抛未捕获 `UnicodeDecodeError`
- **固定提交与位置**：`knowbase-app/knowbase-backend` `906f88aeaf8bd6f08495cb16ff3a34151909d9b5`，`app/app/interfaces/mcp/data_mcp.py:429`
- **触发条件**：正式方法（或隔离脚本资料输入）通过 KnowBase `read_for_method` 读取一份 `media_type` 为 `text/*`（且 `<=16000B`）、实际编码为 GBK / UTF-16 / Latin-1 或含非法 UTF-8 字节的资料原件。
- **预期 vs 实际**：
  - 预期：返回结构化受控错误（或按字符集声明解码/与同文件 L506 一致使用安全错误处理），不以未捕获内部异常中断调用。
  - 实际：L429 直接执行 `(got.content or b"").decode("utf-8")`（对比同文件 L506 `read_text` 已使用 `.decode("utf-8", "replace")`），遇非 UTF-8 字节直接抛未捕获 `UnicodeDecodeError`。
- **受影响的人或数据**：使用 GBK/UTF-16 文本资料（如国内财务 CSV/TXT）的正式方法读取链路。
- **建议**：明确非 UTF-8 处理策略：若协议要求严格 UTF-8，则捕获 `UnicodeDecodeError` 并转为可识别的领域错误码（避免静默损坏数据或 500）；若允许替代字符，与 L506 统一并在元数据标明解码状态。

#### F10 [P2 · 已证实缺陷 · C5 延续，固定候选存在 / 后续已修] 供给器 `stop_metered()` 未处理 Pod 终态 `409/422`；结算后 `executor.cancel()` 瞬时失败锁槽 900s
- **固定提交与位置**：
  - `sunmoonun` `d67e1a296fa0f7b3329e6b9f96636a477ebf398e`，`infrastructure/applications/component-images/sandbox-platform/provisioner/script_jobs.py:224-250`
  - `knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/application/workbench/formal_script_execution.py:175`、`app/app/infrastructure/workbench/capability_repository.py:409-417`
- **触发条件**：Pod 并发自然退出瞬间收到 `PATCH /spec/activeDeadlineSeconds` 返回 `409/422`；或结算落账提交后 `executor.cancel()` 遇瞬时网络失败/进程重启。
- **预期 vs 实际**：`stop_metered()` 抛出未处理 500 且在终止期重复 PATCH；已结算的终态 Job 因 `pending_metered_scripts()` 只查无 `consume` 记录的调用而不再被回收，占住单账号脚本槽长达 `ttlSecondsAfterFinished: 900`。
- **交叉核对**：与既有 C5 分项回执第 3、4 条一致；所审固定候选 `d67e1a29`/`5d86118f` 存在，Luna 已在后续 `9edd61e02`/`4aa68b7d` 修复。

#### F11 [P2 · 已证实缺陷] `capability_update` SQL 忽略 `:default_selected` 绑定参数，且禁用资产不清除 `default_selected`
- **固定提交与位置**：`knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/infrastructure/workbench/capability_repository.py:191-216`、`app/app/application/workbench/capabilities.py:417-438`
- **触发条件**：调用 `capability_update(..., default_selected=False)` 修改默认选中，或用户 `disable` 一个已设为默认选中的连接/Skill 后再次 `enable`。
- **预期 vs 实际**：
  - 预期：`capability_update` 传入的 `default_selected` 生效；禁用资产同步取消默认选中，重新启用时需用户显式再设默认。
  - 实际：L198 SQL 写为 `default_selected=CASE WHEN :status IN ('disconnected','reauth_required') THEN false ELSE default_selected END`——`ELSE` 分支引用的是**表列 `default_selected`** 而非绑定参数 `:default_selected`（L205 传入的 `default_selected` 成为完全无效的死参）；同时 `disable` 状态不在 `IN (...)` 中，导致 `default_selected=true` 残留，重新启用后静默恢复默认选中。
- **受影响的人或数据**：停用后重新启用连接/Skill 的用户，可能在新会话中意外自动携带此前已停用的默认能力。
- **建议**：将 L198 改为 `CASE WHEN :status IN ('disabled','disconnected','reauth_required') THEN false ELSE :default_selected END`，并补单测验证 `disable -> enable` 不静默复活 `default_selected`。

#### F12 [P2 · 已证实缺陷] 正式模型探针非 `mcpToolCall` 项采用黑名单而非白名单，存在 Codex 升级漏拦风险
- **固定提交与位置**：`knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/domain/workbench/formal_model.py:114-123`、`app/app/application/workbench/formal_model_evidence.py:283-291`
- **触发条件**：Codex 0.170.0+ 升级或特定配置下模型产生除当前 5 个黑名单类型（`commandExecution`、`fileChange`、`webSearch`、`dynamicToolCall`、`collabAgentToolCall`）外的其他原生工具/执行项（例如 `imageView`、新增内建工具项）。
- **预期 vs 实际**：
  - 预期：正式模型方法探针执行 fail-closed，仅放行明确允许的非调用消息项（如 `agentMessage`、`reasoning`、`userMessage`）及经核验的 `mcpToolCall`，其余未知项一律拒绝。
  - 实际：`FormalProbeGuard.observe()` 与 `formal_model_evidence.py` 采用 5 项黑名单拦截，未知项类型会被静默放过。
- **受影响的人或数据**：正式模型方法的隔离证明与准入边界（特别是后续再升级 Codex 版本时）。
- **建议**：在 `formal_model.py` 与 `formal_model_evidence.py` 同步将黑名单改为显式允许白名单（允许 `agentMessage`、`reasoning`、`userMessage`、`mcpToolCall` 等协议已知无副作用项，其余一律判越界失败）。

#### F13 [P2 · 需进一步验证] 递归编排取消时首次 `drive()` 未同步调用 `settle_ancestors()`
- **固定提交与位置**：`knowbench-app/knowbench-backend` `5d86118f2473901b0e1673b89f9efd191ebd08b3`，`app/app/application/workbench/formal_orchestration_execution.py:184-189`
- **触发条件**：多层嵌套正式专家执行中途收到取消请求（`task.get("cancel_requested_at")` 非空），`drive()` 首次进入取消分支。
- **预期 vs 实际**：
  - 预期：取消时即刻统一收敛活跃调用及所有中间祖先 `formal_method_calls` 记录，避免外部查询或任务取消终态出现中间层调用悬挂在 `running`。
  - 实际：L184-189 直接返回 `await led.request_cancel(...)` 而未先调用 `settle_ancestors(...)`（L175 仅在 `task["state"]` 已终态的下一轮 `drive()` 或 `formal_test_runs.py:306-326` `record_case()` 中触发）。若无后续 `drive()` 或非测试运行入口（如未来 M3 普通用户委托）取消，中间祖先调用存在滞留非终态窗口。
- **建议**：核验 `led.request_cancel` 后的状态推进路径，在 `cancel_requested_at` 触发终态收敛时同步执行 `settle_ancestors()`，并补多层递归取消的直接状态断言测试。

---

### P3 / 低危缺陷与工程建议

#### F14 [P3 · 工程建议 · C5 延续，后续已修] 未知回执提示文案漏判 `"formal_script"` 及操作卡停止过渡态细节
- **位置**：`knowbench-backend` (`5d86118f`) `capabilities.py:2277-2282`；`knowbench-web-frontend` (`63b5a7c7`) `capability-action-card.tsx:87-89, 196-203, 234-241`。
- **说明**：后端 `except Exception` 未知回执提示仅判 `execution_kind == "skill_script"` 漏了 `"formal_script"`；前端操作卡在 `stop_requested` 过渡态仍保留可点“停止脚本”按钮且将内部过渡 JSON 渲染进结果折叠区。与 C5 回执第 5 条一致，Luna 已在 `4aa68b7d`/`11a3fd72` 处理。

#### F15 [P3 · 工程建议] `tool_operations.py` 对可选且省略的 `inline_attachments_field` 误拒
- **位置**：`knowbench-backend` (`5d86118f`) `app/app/domain/workbench/tool_operations.py:161-166`。
- **说明**：若某操作声明了 `inline_attachments_field` 且附件参数为可选，当调用省略该键时 `arguments.get(self.inline_attachments_field)` 为 `None`，L165 `if not isinstance(files, list):` 会将其直接拒绝。建议仅当该字段出现在 `arguments` 且非 `None` 时校验列表类型（或按操作 schema 区分必填与可选）。

#### F16 [P3 · 工程建议] 设置页 `returnTo` 未兼容专家运行路径；已断开非 OAuth 连接未禁用续期按钮
- **位置**：`knowbench-web-frontend` (`63b5a7c7`) `app/features/settings/ui/capabilities-section.tsx:48-54, 320-335`；`knowbench-backend` (`5d86118f`) `app/app/domain/workbench/connection_oauth.py:79-85`。
- **说明**：① 前后端 `returnTo` 正则均仅允许 `/chat/...` 与 `/projects/.../c/...`，从专家运行页跳转设置页后“返回”链接会被丢弃；② L327-333 对已断开（`disconnected`）的非 OAuth 连接未禁用 `renew` 按钮，用户点开提交后才被后端拒绝。建议放行合法专家运行页相对路径并按连接状态禁用不可用按钮。

#### F17 [P3 · 工程建议] 方法连接预览 `connection_preview` 按 `url` 聚合 `required` 存在同 URL 多能力误标
- **位置**：`knowbench-backend` (`5d86118f`) `app/app/application/workbench/formal_method_catalog.py:109`。
- **说明**：`"required": url in needed` 仅以服务 URL 判必选；当同一 MCP 服务 URL 承载多个能力/版本（其中仅部分为必选、其余为可选分支）时，可选能力项会被一并标为 `required=True`。建议改为按 `(url, capability_ref, version)` 精确匹配。

#### F18 [P3 · 工程建议] 正式测试排队等待耗时 `queued_behind` 在首个 `capability_call_id` 生成后被覆盖归零
- **位置**：`knowbench-backend` (`5d86118f`) `app/app/application/workbench/formal_test_runs.py:676-720`。
- **说明**：L684 读入历史 `waited_seconds`，但一旦首个 `call_id` 出现进入 L685-720，直接用各调用审批 `interaction` 等待时长覆盖 `elapsed_wait`，导致此前排队等待时间（`queued_behind`）在计时累计中丢失。建议将排队等待与审批等待分项累计或取不减上限。

#### F19 [P3 · 工程建议] `FormalMethodService.delivery()` 锁定关联资产未按全局 `asset_id` 统一排序
- **位置**：`knowbench-backend` (`5d86118f`) `app/app/application/workbench/formal_methods.py:275-327`。
- **说明**：L279-297 遍历按 `(method_id, version)` 排序并逐项查/核依赖资产；若并发事务涉及多资产行锁，建议与全仓一致显式按 `sorted(asset_id)` 序锁定。另 L326 `skill_dependencies` 列表构造隐式依赖冻结校验保证所有 `skill_*` 来源均有 `delivery_terms`，建议显式断言防守。

#### F20 [P3 · 工程建议] `respond_interaction` 在所有权校验前先校验 capability 决策参数
- **位置**：`knowbench-backend` (`5d86118f`) `app/app/interfaces/endpoints/workbench_routes.py:1418-1445`。
- **说明**：L1426-1433 在调用 `capability_service(repo).decide(_actor(principal), ...)` 核验归属前先对 `body.decision`/`subject_digest` 抛 422。虽然 `interaction_id` 为 UUIDv4 难以枚举，仍建议先校验当前 `principal` 对该会话/交互的归属权限再做业务参数校验。

#### F21 [P3 · 工程建议] KnowLab `listing()` 存在 N+1 顺序 HTTP 注册核验；编译器/展开器未防护循环 `$ref`
- **位置**：`knowlab-backend` (`e7e3c545`) `app/app/application/services/formal_methods.py:280-325`、`app/app/domain/knowbots/formal_method_plan.py:234`、`formal_method_compiler.py:128`。
- **说明**：① `listing()` 对分页内每条冻结方法顺序逐一请求 KnowBench 核对注册状态，列表增大时尾延迟线性放大，建议 KnowBench 提供批量查询接口或并发限流查询；② JSON Schema `$ref` 展开未记录 `visited` 集合，恶意/异常自引用 `$ref` 可触发 `RecursionError`（非领域校验错误），建议增加 `visited` 集合检测并转标准校验错误。

> **已核实排除的潜在误报（无需改动）**：
> - `knowbench-backend` `capability_mcp.py:51-57` 的 `url.copy_with(host=ip)`：已在 `wsl-dev` 使用项目虚拟环境 `httpx 0.28.1` / `httpcore 1.0.9` 实测验证，`httpx.URL("https://tools.example.test/mcp").copy_with(host="2606:4700::1")` 自动规范化为 `https://[2606:4700::1]/mcp`，不存在 IPv6 缺少方括号缺陷。
> - `capability_routes.py:method_call_stream` 并非持 DB 连接 950s：`WorkbenchRepository.transaction()` 在外层退出时即 commit 归还连接池。
> - `revoke_call_read_scope` 仅按 `id = :origin` 撤权并非越权/漏撤：前端 `capability-action-card.tsx:53` 与后端均锚定 `approval.origin ?? call.id`。

---

## 四、重点专题：`test_after_a_decline_even_allowed_changes_ask_and_say_so` 拆库死锁根因与生产停机影响

### 1. 精确因果链（为什么业务断言通过却在拆库报 `workbench_attempts` 死锁，且重跑难以复现）

1. **测试收尾时后台连接读循环仍在运行**：
   - 在 `test_workbench_runner_db.py:2089-2098` 中，答复第 2 次审批并 `_pump(runner)` 后，测试调用：
     ```python
     await runner.wait_drivers(timeout=5)
     for link in runner.links.values():
         if link.client:
             await link.client.close()
     ```
   - `Runner.wait_drivers()`（`runner.py:2911-2916`）**仅等待 `self.driving.values()`**（且超时不取消），不等待 `self.script_receipts`、不等待无追踪的 `_steer` 任务（`runner.py:1964-1966`），也不等待 WebSocket 客户端读循环。
   - `AppServerClient.close()`（`app_server_client.py:108-115`）仅关闭 `self._ws` 并置位 `self.closed`，**既不取消也不等待 `self._reader` 任务（L91-93）**，且 `_read_loop()` 在 L132-137 对服务端请求使用**完全未追踪的 `asyncio.create_task(self._safe_server_request(...))`**，在 L155-163 串行 `await self._on_notification(...)`。
   - 我们已在 `wsl-dev` 对 `5d86118f` 实测验证：当 `_reader` 正在处理回调时调用 `await client.close()`，返回后 **`c._reader.done() == False` 且 `c._reader.cancelled() == False`**，后台协程继续持有/开启新的数据库连接执行逻辑。
2. **残留协程读取 `workbench_attempts` 与 `DROP SCHEMA CASCADE` 相撞形成 AB-BA 死锁**：
   - `on_notification`（`runner.py:706-753`）与 `on_server_request`（`runner.py:1457`、`_where` L1636-1637、`_matches_method_turn` L1655-1659、`method_capability_state` L1764-1767）均独立通过 `async with self.runner.stores() as repo:` 打开新 DB 会话并查询/锁表（`workbench_sessions`、`workbench_tasks`、`workbench_attempts`）。
   - pytest 进入 `db` fixture teardown（`test_workbench_ledger_db.py:70-83`）时，L71 `await engine.dispose()` **在 SQLAlchemy 中只销毁池内空闲连接，不会强制中止已被在途协程借出的活跃连接**！
   - 紧接着 L81 在工作线程执行 `DROP SCHEMA "{schema}" CASCADE`（申请 schema 内所有表的 `ACCESS EXCLUSIVE` 锁）。此时若孤儿 `_reader` / `_safe_server_request` 事务已持有 `workbench_sessions` 或 `workbench_tasks` 上的 `ACCESS SHARE`/`ROW EXCLUSIVE` 锁、正要进一步 `SELECT ... FROM workbench_attempts`，而 `DROP SCHEMA` 已拿到 `workbench_attempts` 的 `ACCESS EXCLUSIVE` 锁并等待 `workbench_sessions`/`workbench_tasks`，PostgreSQL 死锁检测器立即在读取 `workbench_attempts` 处抛出 `deadlock detected`！
   - 该窗口仅在事件循环调度使在途回调刚好跨越 `close()` 与 `DROP SCHEMA` 时触发，因此高负载全量跑分片时偶发、单测重跑极难稳定复现。

### 2. 对真实生产停机（SIGTERM 滚动发布/缩容）的影响

核查 `Runner.run_forever()`（`runner.py:2240-2262`）：
```python
if self.script_receipts:
    self.script_receipts.cancel()
    await asyncio.gather(self.script_receipts, return_exceptions=True)
for link in self.links.values():
    if link.client:
        await link.client.close()
async with self.stores() as repo:
    async with repo.transaction():
        await repo.release_leases(runner_id=self.runner_id)
```
**真实停机存在三处直接缺陷**：
1. `wait_drivers()` 的文档字符串（`runner.py:2912`）明确写着 `"""测试与优雅停机用：等正在驾驶的顾问停下。"""`，但 **`run_forever()` 从未调用它**，也未取消/等待 `self.driving.values()`！
2. `link.client.close()` 不取消/等待 `_reader` 和在途 `_safe_server_request`，`runner` 也不追踪/取消 `_steer`（L1964）任务。
3. 上述协程仍在后台读写数据库时，L2261 就立刻执行 `await repo.release_leases(runner_id=self.runner_id)`。在 K8s 滚动更新场景下，其他 Runner Pod 会立即抢占被释放的会话/任务租约并开始恢复推进，与即将退出的旧 Pod 孤儿协程并发写入同一 Task/Attempt/Event 产生脑裂冲突。

### 3. 修复建议
1. **在 `AppServerClient` 中建立完整任务生命周期管理**：
   - 增加 `self._handlers: set[asyncio.Task] = set()` 追踪所有 `_safe_server_request` 任务（带 `add_done_callback(self._handlers.discard)`）；
   - `close()` 关闭 WS 后，先给 `_reader` 与 `self._handlers` 短暂优雅收尾窗口（如 `wait(..., timeout=...)`），超时则 `cancel()` 并 `await asyncio.gather(..., return_exceptions=True)`，保证 `close()` 返回时零在途回调。
2. **在 `Runner` 中补全统一 `shutdown()` / `close()` 收尾顺序**：
   - 追踪 `_steer` 任务；
   - `run_forever()` 退出循环后严格按序：① 取消 `script_receipts` 并等待；② 关闭所有 `link.client`（使在途驱动收到连接断开并确保零残留回调）；③ `await self.wait_drivers(timeout=...)`，超时后显式 `cancel()` 剩余 `self.driving` 及 `_steer` 并 `await gather(..., return_exceptions=True)`；④ **所有后台协程全部结束后**才执行 `release_leases()`。
3. **测试夹具同步复用 `await runner.close()`**，并在 `test_workbench_runner_db.py` 补一项停机断言测试：注入慢回调/慢驱动，验证 `close()` / `run_forever()` 返回后 `_reader`、`_handlers`、`driving` 全部 `done()` 且之后才释放租约。

---

## 五、六条主链路逐行复核与分项回执交叉核对

| 主链路 | 逐行代码核查结论 | 与既有分项 `agy` 回执交叉核对 |
| --- | --- | --- |
| **1. 方法与递归执行** | KnowLab 编译器（`formal_method_compiler.py`）、展开器（`formal_method_plan.py`）与 KnowBench `formal_recursive_runtime.py` / `formal_recursive_evidence.py` 对重复引用同一冻结版本、直接父链、输入绑定、逐层导出、依赖去重与独立完成器校验严谨；生成模块与锁文件 100% 对齐。发现 **F02**（取消 422）、**F08**（KnowLab 前端锁死 `mcp`）、**F12**（探针黑名单）、**F13**（取消首次 `drive` 未调 `settle_ancestors`）、**F18**、**F21**。 | 既有回执（C2、C5）未测 KnowLab→KnowBench 真实取消 HTTP 链路（漏 F02），未查 KnowLab Web 直调脚本入口（漏 F08），未查探针白名单化（漏 F12）。 |
| **2. 两条调用入口与资源权限（待办 1–3）** | 宿主派发与模型 MCP 入口收敛至同一 `method_access` / `method_authorizations` / `calls` 服务与调用账；KnowBase 原件与平台产物跨层委派收窄、撤权、重启重核、并发领取、未知写入不重发闭环；Codex 0.170.0 断网协议探针与 Link 0.5.9 打包脚本齐备。发现 **F03**（Runner 停机与死锁）、**F07**（KnowBase 授权上界与多步同资料 409）、**F09**（KnowBase 非 UTF-8 解码）。 | 既有 C2、MCP 稳定配置回执未暴露 F03 停机协程收尾缺口及 F07 多步同资料冲突。 |
| **3. Skill 目录、正式方法交付和市场（待办 4–5）** | Skill 目录与正文分存迁移 `0046` 可逆且对账严谨；依赖许可四次独立核权、包内容摘要逐文件核验与跨作者私有依赖隔离成立。发现 **F05**（KnowMart 持 `FOR UPDATE` 行锁跨 HTTP 交付）、**F11**（`capability_update` 忽略 `:default_selected`）、**F19**（`delivery` 锁序）。 | 既有第 4、5 项回执重点在功能与字节校验，未发现 F05 持行锁跨 HTTP 与 F11 SQL 死参。 |
| **4. 用户连接与审批（待办 6–7）** | OAuth PKCE 一次性回调、跨账号保护、并发单次刷新占位、凭据独立密钥轮换、A2A `GetTask`、只读资源范围子集匹配与结果投影、写入附件字节锁定整体设计扎实。发现 **F15**（可选内联附件为 `None`）、**F16**（专家页 `returnTo` 与断开非 OAuth 按钮）、**F17**（预览按 URL 标必选）、**F20**。经实测排除 `httpx` IPv6 误报。 | 与 C3、C4 回执核心通过结论一致，补充了 F15–F17、F20 边界细节。 |
| **5. 隔离输入、计算、产物与费用（待办 8–9）** | 两阶段空 Job 预留、二次核权、`pods/attach` 一次性 stdin 帧协议与摘要校验、4 MiB/2 MiB 边界、根预算部分唯一索引 `uq_budget_script_entry`、kubelet 终态计量及 fail-closed 保留预留均实现到位。发现 **F01**（发版镜像修订滞后）、**F04**（`decide_call` 漏 `"formal_script"`）、**F06**、**F10**、**F14**。 | F06/F10/F14 与 C5 回执一致（后续已修）；**F01 与 F04 为既有回执遗漏的 P0/P1 缺陷**。 |
| **6. 跨场景和运行兼容（待办 10）** | `test_connector_cross_scene_db.py` 已逐行审阅并在隔离 PG16 实测通过，验证同一连接 ID 贯穿聊天/工作/三步专家及发送断链恢复；前端 `en.json`/`zh-CN.json` 键完全对称；但 **F01、F02、F03、F04、F05** 仍影响全功能上线与优雅滚动发布。 | `5d86118f` 新增的 C6 跨场景测试此前尚未经过独立逐行复核，本轮已完成审阅并实测通过。 |

---

## 六、对照方法主稿：「两大统一」已有的工程基础与待开发环节

对照 `sunmoonun/docs/总纲/专家方案设计/专家孵化方案/luna/专家方法孵化与递归编排方案.md`（§1.1、§1.5、§2.10、§4.2–§4.5），两项产品统一决定在所审 12 仓候选中的实际工程落点如下：

### 统一一：同一冻结专家版本支持单次委托中的多角色协作，也能由用户的长期职责反复唤醒

| 维度 | 已有工程基础（已落代码） | 待开发环节（尚未实现，按待办 11–14 / M2–M5 排期） |
| --- | --- | --- |
| **冻结方法定义与递归执行** | `formal_method.py` 已实现两类 `Procedure`（`DirectProcedure` / `Orchestration`）、五要素核心结构、精确 `MethodRef(method_id, version, digest)` 与递归编译/唯一计划展开（`formal_method_compiler.py`、`formal_method_plan.py`）；KnowBench `formal_recursive_runtime.py` 支持同一冻结版本在同一 Task 下重复调用、独立 `call_id`/父链、叶子审批与逐层导出。 | 1. 基准图**允许变化**（可执行 `run_condition`、互斥/依赖约束、多候选槽位、运行时市场选择规则）尚未落地，当前仅支持唯一必做串行计划；<br>2. 编译产物仍输出三类历史枚举标签，尚未完成两类契约正式切换（M3）；<br>3. `Orchestration` 尚无每步 `role`、隔离策略、可读产物交接边界声明字段。 |
| **多角色独立线程与工作目录隔离** | `runner.py` 已有线程创建/恢复、MCP 白名单切换、`FormalProbeGuard` 探针限制与 `artifact_read_authority.py` 产物读取核权基础；`task_output_reader.py` 支持按绑定 Attempt 精确读取前序产物。 | 1. 尚未实现同一委托下按角色分配独立受隔离 Codex 线程与独立工作目录；<br>2. 尚未实现“交叉复核前禁止互读对方历史与工作文件、交接时仅开放指定产物、重启后保持相同可读范围”的运行时强隔离（§2.10.1 / §4.4）。 |
| **长期职责周期/事件唤醒** | 现有普通 Task/Attempt 账本、根预算与跨步产物引用机制可复用；`connect`/OAuth 凭据刷新与撤销框架已就绪。 | 1. 尚无长期职责配置对象、事件/周期触发器与按事件去重生成普通 Task 的调度链；<br>2. 尚无跨期绑定上期获准成稿、成稿缺失/撤权/暂停职责的完整恢复与测试覆盖。 |
| **指令/脚本/平台载体扩展** | MCP 零轮直调、隔离脚本（`skill_script`，仅 `host` 零轮）已打通后端运行与计量；指令型探针有单步模型隔离实验基础。 | 1. KnowLab 前端仍锁死 `mcp`（F08）；<br>2. 指令型工具方法（受限模型轮次 + 能力档强制执行）、平台函数载体（`platform`）尚未打通编排叶子实测与冻结资格。 |

### 统一二：KnowLab 孵化 → KnowMart 目录与许可交付 → KnowBench 使用 → 发现缺口回炉 KnowLab 闭环

| 维度 | 已有工程基础（已落代码） | 待开发环节（尚未实现，按待办 11–14 / M2–M5 排期） |
| --- | --- | --- |
| **KnowLab 创作与孵化** | 已有正式方法草稿、校验、试跑（经 KnowBench 内部接口）、冻结、依赖许可冻结与基本编辑/执行页；提供方生成、消费者持锁的跨仓契约管道已成型。 | 1. 槽位预设编辑、编排草图（`OrchestrationSketch`）往返、AI 起草图级差异包（`ProposalBundle`）与作者逐项采用留痕（待办 11 / M2）尚未完成；<br>2. 独立冻结的作者测试集版本与“判分断言不反向影响规划”评测隔离（§4.5）尚未完成；<br>3. 取消接口跨服务契约断裂（F02）与前端脚本试跑受阻（F08）需先修复。 |
| **KnowMart 目录与许可交付** | 已打通指定版本的正式方法上架申请（`submit_formal`）、运营审核（`review_formal`）、作者撤回（`withdraw_formal`）、买方唯一获取（`acquire_formal`）与运行时跨服务字节级 Skill 依赖包交付（`runtime=True`）。 | 1. 仅完成最小版本获取链路，工具方法/专家方法两类市场分区、能力检索/契约筛选、分页完整性记录与公开详情页尚未建设（待办 12 / M3）；<br>2. 跨作者引用/派生许可与安全撤销影响面阻断尚未落地；<br>3. 需先解决 `FOR UPDATE` 跨 HTTP 持锁瓶颈（F05）。 |
| **KnowBench 普通用户委托与二次编排** | 已有正式方法会话目录、连接需求预览、聊天/工作/专家共用连接器与审批卡、受控隔离脚本操作卡；递归执行已具备宿主测试入口。 | 1. 尚无面向普通用户的正式专家委托入口（与 KnowLab 孵化测试分开记账）、二次编排与确认页重算（选分支/改参数重算数据、账号、费用与权限）；<br>2. 尚无普通委托调用树 UI、剪枝、暂停恢复与用户自组计划保存/复用；<br>3. 需先修复 Runner 停机租约脑裂（F03）与多步同资料授权冲突（F07）。 |
| **发现缺口回炉 KnowLab** | `knowlab/runtime-incubation/v2` 旧孵化回执通道存在，可作为参考；调用账与失败原因持久化完整。 | 1. 尚无从 KnowBench 缺工具/试跑失败一键生成接口草案送回 KnowLab 的完整回炉闭环（区分原作者修订与仅具运行权用户提需权限、防重复建稿、保留原委托钉住 v1、升级 v2 后重核采用，待办 13–14）。 |

---

## 七、隔离本地验证记录（`wsl-dev`）

所有验证均在 `wsl-dev`（`/home/zymun/worktrees/luna`）通过 `git archive` 导出 `request.md` 固定提交快照或读取干净固定仓执行，使用一次性 tmpfs PostgreSQL 16 容器并在结束时自动销毁，未污染任何工作区或持久化库。

| 验证项 | 固定提交 | 来源证据类型 | 命令与结果 |
| --- | --- | --- | --- |
| **F02 复现：取消接口 422 契约断裂** | KnowBench `5d86118f` / KnowLab `e7e3c545` | 真实 FastAPI 路由解析 + `TestClient`（隔离快照） | `POST /internal/v1/knowbot-runtime/formal-method-executions/{run_id}/cancel` 传 `json={"owner_subject": "user-123"}` 返回 **`HTTP 422`**（`loc: ['query', 'owner_subject'], type: 'missing'`）；改为 Query 传参返回 `HTTP 200`；路由 `query_params=['owner_subject']`, `body_params=[]`。 |
| **F03 复现：`AppServerClient.close()` 协程泄漏** | KnowBench `5d86118f` | 隔离异步单测（真实 `AppServerClient`） | 在 `_reader` 活跃期间调用 `await c.close()`，返回后实测 **`_reader.done() = False, _reader.cancelled() = False`**，证实关闭不等待也不取消读循环。 |
| **F04 核验：`decide_call` 漏判 `"formal_script"`** | KnowBench `5d86118f` | 源码检查 + `inspect.getsource`（隔离快照） | 确认 `decide_call` `except TestManagedInKnowlab:` 分支仅允许 `("formal_mcp", "formal_probe")`，`"formal_script"` 不在其中。 |
| **C6 跨场景测试（新引入）** | KnowBench `5d86118f` | **真实 PostgreSQL 16**（一次性 tmpfs `workbench_tests` 库）+ **合成 HTTPS MCP 服务**（本地自签 TLS + `LocalTLS` 传输）+ 测试脚本执行器 | `PYTHONPATH=$TMP/kb/app .venv/bin/pytest -q tests/test_connector_cross_scene_db.py` → **`1 passed in 8.38s`**。 |
| **死锁目标用例复跑** | KnowBench `5d86118f` | **真实 PostgreSQL 16** + `FakeAppServer` | `PYTHONPATH=$TMP/kb/app .venv/bin/pytest -q tests/test_workbench_runner_db.py -k test_after_a_decline_even_allowed_changes_ask_and_say_so` → **`1 passed, 34 deselected in 7.52s`**（与 `request.md` 描述一致，单跑窗口不易命中，已通过 F03 机制根因证实并实测 `_reader` 未收尾）。 |
| **KnowLab 正式方法核心测试** | KnowLab `e7e3c545` | 隔离单元测试（快照导出） | `pytest -q tests/test_formal_method_execution.py tests/test_formal_method_recursive_plan.py` → **`20 passed, 2 skipped in 1.25s`**（2 项跳过因未设 `DELIVERY_TEST_DATABASE_URL`）。 |
| **KnowBase 契约与内核不变量测试** | KnowBase `906f88ae` | 单元测试（干净固定仓） | `pytest -q tests/test_user_library_contract.py tests/test_kernel_invariants.py` → **`7 passed in 0.33s`**。 |
| **KnowMart 路由与内核不变量测试** | KnowMart `090da880` | 单元测试（干净固定仓） | `pytest -q tests/test_market_routes.py tests/test_kernel_invariants.py` → **`14 passed in 1.19s`**。 |
| **供给器测试套件** | `sunmoonun` `d67e1a29` | 单元测试（`git archive` 导出完整 `sandbox-platform` 目录） | `PYTHONPATH=$PROV_DIR pytest -q $PROV_DIR/tests` → **`25 passed in 0.57s`**。 |
| **IPv6 `httpx` 误报排除** | KnowBench `5d86118f` | 真实项目依赖 `httpx 0.28.1` / `httpcore 1.0.9` | `httpx.URL("https://tools.example.test/mcp").copy_with(host="2606:4700::1")` → `https://[2606:4700::1]/mcp`，确认无缺陷。 |
| **真实容器 / 固定版 Codex / 真实供应商边界说明** | — | — | ① 真实 KIND 容器执行与计量、断网容器 Codex `0.170.0` 协议探针及本地浏览器操作卡联调已有 C5/C1-C6 独立实测证据（本轮已核对源码与既有证据，未重复拉起 KIND）；② 真实第三方 OAuth/MCP 供应商（专用账号、应用注册、正式回调地址）与线上目标集群脚本开关验收仍待专用条件完成，不计入本次本地通过结论。 |
