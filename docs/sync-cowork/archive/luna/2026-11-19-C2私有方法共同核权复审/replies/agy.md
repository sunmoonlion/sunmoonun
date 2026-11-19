# agy 回执

- 对应请求：[../request.md](../request.md)
- 本轮：第 1 轮
- 实际检查版本（本地 `wsl-dev` 主工位 `/home/zymun/worktrees/luna`，分支 `luna`）：
  - `knowbench-app/knowbench-backend`：`21f14eeb24caf084fc2821c458d41b936bdffe16`（对照前一版 `e9a3e0ce13c573906444bffc0f47afc6eeee9571` 及同批 `6cb2b85`、`caef0cb`）
  - `knowbench-app`：`1ab9c1b21b06fcfd7fd68b34d191e07d19fc0916`
  - `knowbase-app`：`9552fba44565e0a71b5a8f0d9d921b217537bbba`（子仓 `knowbase-backend`：`906f88aeaf8bd6f08495cb16ff3a34151909d9b5`）
  - `knowlab-app`：`a498ed059fc45661554c4ca18976c5ff27e7242b`（子仓 `knowlab-backend`：`eb22655f3ea912a174c6f2b1a606ef5303400dbe`、`knowlab-web-frontend`：`e488d06691a4bb80cbab854f9f01303f117e2763`）
- 结论：**通过（无阻断项）。适用范围：[Luna 待办](../../../../总纲/luna-待办.md)第 2 项的私有方法共同准入与核权开发候选已完成并复验通过（Luna 可勾选待办第 2 项）；[接入实施方案 §17.6](../../../../总纲/mcp和skill接入实施方案.md#176-本次先发布发布后补齐的工作单所有者-2026-11-13-确认) 第 3、4 项在本批“作者本人私有孵化测试、串行唯一必做计划、零内部模型轮次直接 MCP 叶子、单份 $\le 16000$ 字节 UTF-8 文本 KnowBase 读取与已验收平台任务步骤产物读取”范围内已闭合，但第 3、4 项整体仍保持“进行中”（普通用户委托、两类契约与市场分区切换、非零轮次指令/脚本/平台工具叶子及线上发布验收按后续待办推进）。**

---

## 发现

### F01：四项请复核完成条件逐项核对通过

1. **条件 1（宿主与模型双入口读取同一已验收平台产物、权限拒绝与 KnowBase 跨服务共同准入对照）**：
   - **入口识别与绑定构造**：`FormalHostCalls.context`（`knowbench-backend/app/app/application/workbench/formal_host_calls.py:360-399`）在命中 `asset["detail"]["url"] == self.capabilities.task_outputs_url` 且 `source.entry == "read_task_output"` 时，强制校验操作映射为 `effect == "read"` 且含 `ResourceBinding(resource_role="task", argument_path=("task_id",))`，调用 `task_output_reader.read_binding`（`task_output_reader.py:107-155`）生成包含 `task_id`、`owner_actor_id`、`path`、`fields={"value": ref}`、`purpose`、`destination` 及 `return_to=snapshot.caller`（`"host"` 或 `"model"`）的绑定，写入 `intent["artifact_read_digest"]` 并挂入审批交互 `prompt.subject["artifact_read"]`（`formal_host_calls.py:548-551`）。
   - **来源产物核验与越界拒绝**：`selected_output`（`task_output_reader.py:45-105`）核对来源任务归属同一 `owner_actor_id`、`pack_source == "formal-test"`、`snapshot.dependencies` 非空且状态为 `TaskState.SUCCEEDED`；核对产物 `kind == "step"`、所属 Attempt 状态为 `COMPLETED`、`refs.kind == "formal_orchestration_step"`、`refs.reference` 与 `expanded_plan(snapshot).leaf_nodes[index].reference` 一致、`refs.snapshot_digest == task["pack_digest"]`、产物名匹配 `node_artifact(node.path)`（或 `"formal-step:" + node.step.id`）、`attempt["output_artifacts"] == [pinned]`、`receipt["outcome"] == "succeeded"`、`digest(artifact["content"]) == receipt["outputs_digest"]` 且请求字段在 `node.step.outputs` 声明内。更换账号（`OTHER`）、版本（`version: 2`）、字段（`output: "other"`）或来源后，`selected_output` 与派发端 `read_approved`（`task_output_reader.py:158-195`）均重新核验并拒绝，不能沿用旧许可。
   - **实际交付载荷与 KnowBase 对照**：`read_approved` 在事务内加锁复核 `row["status"] == "dispatching"`、`interaction["status"] == "consumed"`、`method/artifactReadAuthority` 最新事件、`digest(displayed) == intent.get("artifact_read_digest")`、`check(...)` 逐层授权及重新读取的 `ref == displayed["fields"].get("value")`；宿主与模型成功时均收到完全一致的 `{"value": value, "source": ref}`（含 `structuredContent` 与 JSON 文本 `content`），撤权/拒绝时模型收到失败回包且不含产物明文（`test_task_output_reader_db.py:163-296`）。对照 `knowbase_method_read.py:13-194`、`knowbase-backend` 的 `user_run_service.py:202-334` / `data_mcp.py:269-313` 及跨服务测试 `c2_method_read.py:84-173`，两条资源路径均遵循“真实调用链绑定 + 本人显式授权 + 派发前后复核 + 撤权即时拒读 + 回包携带精确出处与摘要”的共同准入模型。

2. **条件 2（从叶子沿真实调用账回溯父/根专家、中间层收窄拒派、旧待批补授权与私有测试任务列表隔离）**：
   - **真实调用账回溯与生产步骤钉版**：`planned_read`（`artifact_read_authority.py:28-111`）从根调用 `task:<task_id>` 出发，沿 `leaf.path` 逐层从 `workbench_calls` 取真实调用并校验 `str(call["parent_call_id"]) == path[-1]["call_id"]`，记录每层 `call_id`、`method_id`、`version` 与 `definition_digest`；随后沿 `reversed(legs)` 逆向追踪 `CallerValue` 槽位重命名链直至命中 `StepValue(source="step")`，从已验收 `input_bindings` 提取精确 `producer_path`、`artifact_id`、`name`、`version`、`digest`、`output`，连同 `purpose`、`destination` 形成授权范围。`e9a3e0c` 与 `21f14ee` 在 `formal_recursive_runtime.py:113-139` 及 `formal_orchestration_execution.py:79-100` 中进一步强制校验 `artifact["kind"] == "step"`、期望产物名 `node_artifact(path, exports=exports)` 与正整数版本号（`test_formal_recursive_runtime_db.py:144-178`）。
   - **中间层收窄与派发前拦截**：`grant_state`（`artifact_read_authority.py:113-134`）按调用路径生成逐层 `grants`（含 `call_id`、`recipient_call_id`、`remaining_depth`、`fields`），有效期不超过 `deadline_for(interaction, scopes)`。`PUT /workbench/capability-calls/{call_id}/artifact-read/{node_id}`（`artifact_read_authority.py:274-298`）校验 `keep <= set(grants[index]["fields"])`（只许收窄、禁止扩大，且已有授权禁止通过 `POST` 替换恢复），并将 `grants[index:]` 全部后代字段与 `keep` 求交集后追加新事件。批准派发时 `authorize_dispatch -> check`（`:136-159, 176-193`）校验每跳 `forwarded <= available` 且末端 `available == set(binding["fields"])`；中间层收窄后在派发前即抛出 `Forbidden("An input is outside the current artifact read permission")`，外部适配器不被调用（`test_formal_artifact_authority_db.py:93-117`）。
   - **旧待批动作补授权**：对未带 `artifact_read_digest` 和 `prompt.subject.artifact_read` 的旧待批动作，`FormalHostCalls.approval_context`（`formal_host_calls.py:649-655`）保留其原有 `call["digest"]` 动作身份，但 `authorize_dispatch`（`artifact_read_authority.py:181-189`）在无授权事件时拒绝直接批准；本人须先在 `/artifact-read` 确认精确 `scope_digest` 落盘事件后，才能完成原动作批准并通过 `verify_approval` 的 `legacy` 兼容校验（`test_formal_artifact_authority_db.py:199-244`）。
   - **私有测试任务在普通列表的可见性隔离**：`repository.py:290-295` 将 `_test_task` 过滤条件扩展为 `coalesce(alias.pack_source, '') in ('knowlab-test', 'formal-test')`，使 `browser_view=True` 的普通浏览器会话/任务列表隐藏 `formal-test` 任务并拒绝 `get_task`（抛 `TestManagedInKnowlab`，`test_formal_artifact_authority_db.py:49-57`）；`capability_routes.py:81-86, 367-445, 519-535` 仅对绑定精确 `call_id` 与本人身份的 `/artifact-read`、`/knowbase-read` 及试用 `/decision`（限 `execution_kind in ("formal_mcp", "formal_probe")`）使用 `method_read_service`。

3. **条件 3（并发批准与恢复复用调用身份、派发后丢失回执不重发、回执追溯关系）**：
   - **并发批准与恢复幂等**：`FormalHostCalls.request` 与 `decide` 统一按 `Task -> Attempt / Call` 顺序加行锁，调用键固定为 `formal-host:<task_id>:<slot>` 或 `formal-model:<task_id>`（受 `uq_calls_invocation` 唯一约束保护）。并发 `POST /artifact-read`、重复 `approve` 及双 `FormalExecution.drive` 并发推进均复用同一 `call_id` 与 `Attempt`（`test_formal_artifact_authority_db.py:84-88`、`test_formal_recursive_runtime_db.py:91-142`）。
   - **适配器已接收但丢失回执后绝不重发**：`FormalHostCalls.decide`（`formal_host_calls.py:682-725`）在事务内先将 `workbench_calls.status` 更新为 `"dispatching"` 提交，再在事务外执行 `_dispatch_call`。若适配器已接收请求但进程在写回前中断，超时后恢复者调用 `request_host_call` 先经 `recover_calls` 将该记录转为 `"unknown"` 并直接返回既有 `call_id`，后续再次 `decide` 也直接返回 `"unknown"`，不会发生第二次外部发送（`test_formal_artifact_authority_db.py:127-175`）。
   - **历史回执追溯关系**：平台任务产物读取回执通过 `source(task_id, artifact_id, name, version, digest, producer_path, output)` 追溯到源任务的具体 Attempt 与 Step Artifact；KnowBase 资料读取回执通过 `source(material_id, version_no, method_call_id, grant_id, sha256)` 追溯到 KnowBase `run_grants` 与 `method_read_consents`；递归内部产物传递通过 `Attempt.refs.input_bindings`、`method/artifactReadAuthority` 与 `method/permissionsConfirmed` 事件完整关联。

4. **条件 4（作者私有登记、消费者锁、逐层产物与独立完成器篡改拒绝、完成范围判断）**：
   - **作者私有登记与两份消费者锁**：KnowLab `formal_methods.py:618-625` 与 KnowBench `formal_method_catalog.py:358-373` 严格限制当前正式专家与目录准入为本人 `private`；清理临时测试任务后仍可凭封存证据完成私有登记并作为上层递归依赖，且不开放普通会话专家调用（`test_formal_recursive_db.py:82-100, 202-260`）。核对 `knowlab-web-frontend/app/contracts/formal-method-provider/lock.json` 与 `knowbench-backend/app/contracts/formal-method-lock.json`，5 个契约源文件的 `source_sha256` 完全一致。
   - **逐层产物、独立完成器与篡改拒绝**：`formal_evidence.py:390-418`、`formal_orchestration_evidence.py:203-253` 与 `formal_recursive_evidence.py:374-647, 799-836` 按冻结计划独立重算每层输入绑定、叶子步骤产物（`node_artifact(path)`）、子专家导出产物（`node_artifact(path, exports=True)`）与根导出产物，核对任务下 `calls` 与 `artifacts` 全集，并调用 `verify_approval` 校验授权事件游标先于 `method/permissionsConfirmed`、摘要一致且在有效期内。篡改已落库的 `method/artifactReadAuthority` 产物版本（`test_formal_artifact_authority_db.py:177-197`）或篡改 22 类递归调用/产物/scope/授权事实（`test_formal_recursive_evidence_db.py:53-340`）均被独立完成器拒绝，无法通过封存或冻结。
   - **待办第 2 项与接入方案 §17.6 第 3、4 项完成范围判断**：
     - **待办第 2 项（私有开发候选）**：已完成并验证闭合，满足勾选条件。
     - **接入方案 §17.6 第 3、4 项**：本批私有孵化候选子集已闭合，但第 3、4 项整体还包含后续阶段的普通用户委托入口、两类契约与市场分区切换（M3 / 待办第 12 项）、非零轮次指令/脚本/平台工具叶子（M2 / 待办第 11 项）及最终发布验收，因此 §17.6 表中第 3、4 项整体状态应继续保持“🔄 进行中”。

### F02：两处非阻断实现观察（供后续阶段演进参考，无需本轮修改）

1. **跨任务 `read_task_output` 在封存前依赖源任务记录未被清理**：`formal_evidence.py:408-415` 与 `formal_orchestration_evidence.py:221-230` 在封存阶段会再次调用 `task_output_reader.read_binding -> selected_output` 读取源任务及其 Step Artifact（封存通过后证据写入 `workbench_formal_validations.execution_evidence`）。这与 `docs/managed-capabilities.md:436` “清理掉的来源不能用于新读取”一致；后续若引入自动清理已结束测试任务的后台作业，需保持“被引用源任务不得在引用方测试完成封存前被清理”的时序约束。
2. **叶节点索引取值方式在 M3 引入跳过分支时的统一**：`artifact_read_authority.planned_read`（`:37`）从 `attempt["refs"]["step_index"]` 取叶节点索引，而 `knowbase_method_read.read_binding`（`:40`）从 `int(task["current_step"])` 取叶节点索引。当前唯一必做计划下 `FormalHostCalls.context` 已强制校验两者相等；后续 M3 引入可选分支 `skipped` 时，建议将 `knowbase_method_read.read_binding` 统一改为从 `attempt["refs"]` 读取节点路径/索引。

---

## 验证

在本地 `wsl-dev`（`/home/zymun/worktrees/luna`）使用独立、可清理的临时 tmpfs PostgreSQL 16 容器 `agy-c2-review-tests-pg`（端口 `127.0.0.1:55439`，测试库 `agy_agent_tests` 与 `agy_delivery_tests`，复验结束后容器已由 `trap` 自动销毁，未改动任何既有服务或 `qwen-test-pg`）执行：

1. **平台产物授权与跨任务产物读取专项（KnowBench 后端）**
   - 命令：`.venv/bin/python -m pytest -q tests/test_formal_artifact_authority_db.py tests/test_task_output_reader_db.py`
   - 结果：**6 passed, 0 failed, 0 skipped**（耗时 `28.88s`）。
2. **私有专家递归执行、独立证据篡改与运行时并发恢复专项（KnowBench 后端）**
   - 命令：`.venv/bin/python -m pytest -q tests/test_formal_recursive_db.py tests/test_formal_recursive_evidence_db.py tests/test_formal_recursive_runtime_db.py`
   - 结果：**47 passed, 0 failed, 0 skipped**（耗时 `249.82s`）。
3. **KnowBench ↔ KnowBase 跨服务独立进程与真实 PostgreSQL 双入口读取联调**
   - 命令：`.venv/bin/python -m pytest -q -c pyproject.toml ../../../sunmoonun/scripts/local-integration/c2_method_read.py`
   - 结果：**1 passed, 0 failed, 0 skipped**（耗时 `11.08s`）。
4. **补充核验：KnowLab 递归计划与消费者导出、KnowBench 递归准入、KnowBase 数据 MCP 契约及静态检查**
   - KnowLab（`knowlab-backend/app`）：`.venv/bin/python -m pytest -q tests/test_formal_method_recursive_plan.py tests/test_formal_method_plan.py tests/test_formal_method_web_export.py tests/test_formal_expert_visibility.py` $\rightarrow$ **42 passed, 0 failed, 0 skipped**（`1.33s`）。
   - KnowBase（`knowbase-backend/app`）：`.venv/bin/python -m pytest -q tests/test_data_mcp.py tests/test_user_library_contract.py` $\rightarrow$ **1 passed, 10 skipped, 0 failed**（`0.79s`；其中 `test_data_mcp.py` 的 DB 用例已在第 3 项跨服务联调中通过 `DELIVERY_TEST_DATABASE_URL` 实测）。
   - KnowBench（`knowbench-backend/app`）：`.venv/bin/python -m pytest -q tests/test_formal_orchestration_admission.py` $\rightarrow$ **23 passed, 0 failed, 0 skipped**（`0.82s`）。
   - 静态检查（KnowBench 后端本批涉及的 14 个源码/测试/联调脚本文件）：`.venv/bin/ruff check` **All checks passed!**，`.venv/bin/pyright` **0 errors, 0 warnings, 0 informations**。
5. **未运行与边界条件**
   - 本次独立复审未重跑 KnowBench / KnowBase / KnowLab 全量测试集（全量记录见 `sunmoonun/scripts/results/c2-method-read-parity-20261119.json` 与 `c2-knowbase-method-read-20261119.json`）；使用本地合成模型协议夹具与合成数据，未发起真实外部供应商或付费模型调用，未执行部署。

---

## 交回

- 回执文件：`docs/sync-cowork/requests/luna/2026-11-19-C2私有方法共同核权复审/replies/agy.md`。
- 未修改任何被评应用代码，未修改 `request.md` 状态或处理记录。
- 后续动作：由 Luna 核对本回执、勾选 `docs/总纲/luna-待办.md` 第 2 项并按归档流程结案。本回执已在本地 `wsl-dev` 提交至 `sunmoonun` 并执行 `sync.sh push sunmoonun`。
