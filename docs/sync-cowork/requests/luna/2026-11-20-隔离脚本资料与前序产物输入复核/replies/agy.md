# 评审回执：隔离脚本资料与前序产物输入复核

- 请求：[request.md](../request.md)
- 轮次：1
- 核对提交：
  - 工作位置：本地（`wsl-dev`，`/home/zymun/worktrees/luna`，分支 `luna`）
  - `knowbench-app/knowbench-backend`：`f392957`（基线 `4fd5942`）
  - `knowbench-app`：`27fcbe6`（基线 `399720f`）
  - `sunmoonun`（平台组件、供给器与联调脚本）：`36d980961`（基线 `b7d8b63fa`；请求提交 `798721909`）
- 结论：**通过（无阻断项，附 4 条代码完善建议）**。待办第 8 项（接入实施方案 §17.6 第 10 项）的按需具名资料/前序产物解析、只认绑定 Attempt 产出字段、两阶段空 Job 预留与 Kubernetes `pods/attach` 一次性 stdin 输入流交付、帧摘要校验、4 MiB 包 / 2 MiB 输入边界、并发领取、等待与运行中取消、丢失响应恢复及双后端 real-KIND 联调均已实测闭环。

## 发现

### F01 [info] 4 项复跑要点核查结果

1. **按需具名资料/前序产物解析、撤权/篡改/取消重核与无正文审计**（`script_inputs.py:20-167`、`capabilities.py:2109-2163`、`test_script_inputs_db.py`）
   - 批准前（`request_call` / `awaiting_approval`）不触发任何 KnowBase 资料读取（`data.calls == []`）；仅在 `decide` 批准且完成 `_check_before_send` 后，`Capabilities._start_script` 调用 `resolve_inputs` 通过 `DataRelay(ProjectRecords(...), ..., sandbox="skill-input")` 校验版本/阅读版（`material_id`、`version_no`、`reading`、`offset`）与唯一归属的消费绑定前序产物字段（`step_field` 校验任务所属会话、生产者已 `COMPLETED` 且在当前方法 `consumer["input_artifact_versions"]` 内、`allow_nan=False` 严格 JSON 编码）。
   - `script_executor.prepare` 预留容器就绪后，`_start_script` 立即复核 `_check_before_send` 并在存在输入时重调 `resolve_inputs` 比对 `live != inputs`（防止拉取镜像窗口期间撤权、替换或超限），再入账事件 `capability/script_inputs_prepared`（仅记录 `{name, bytes, sha256}`）；批准前、撤权、更换或取消时均拒绝投递并清理预留 Job；`workbench_calls` 与事件流均不落资料正文。

2. **供给器 23 项单测、真实 KIND 受限命名空间 `script_probe.py`、RBAC 与并发唯一领取**（`provisioner.py:143-183, 420-445`、`script_jobs.py:51-297`、`skill_execute.py:32-194`、`workload.yaml.j2:18-27`）
   - `workload.yaml.j2` 已精确收敛补齐 `pods/attach`（`get, create`）与 `jobs`（`get, list, create, patch, delete`）；`ScriptJobs.reserve` 创建 `skill-execution-deny-all` 全拒入/出站网络策略及无 Secret、无 ENV、无 PVC、无 ServiceAccount Token、`readOnlyRootFilesystem: true`、非 root `10001`、受限 seccomp 与内存 `/tmp` 的单次 Job（仅把帧长度与 SHA-256 传作命令行参数）。
   - `deliver` 先以 JSON Patch 原语（`test /metadata/uid` + `test sunmoonai.com/delivery == "waiting"` -> `replace "claimed"`）在 `409/422` 下争抢一次性投递权，再经 `KubeClient.send_script_input`（WebSocket `v4.channel.k8s.io` 64 KiB 分块流式写 stdin，等待容器打印 `SUNMOON_INPUT_ACCEPTED\n`）；容器 `skill_execute.py` 读取并校验精确长度与 SHA-256 后才进入 `execute()`，`status()` 同时核对 Pod 所有者 UID 与 `SUNMOON_INPUT_ACCEPTED\n` 起始标记。
   - 在真实 `sunmoon-kind` 隔离命名空间 `agy-script-probe`（启用 `pod-security.kubernetes.io/enforce: restricted` 及完全对齐 `workload.yaml.j2` 的 `Role`）实测运行 `script_probe.py` 全部通过（无凭据、断网拒绝集群 API、Python/Bash/Node、`SUNMOON_INPUT_DIR` 具名输入、无 `/input` 目录、产物返回）。两份 `ScriptJobs` 并发投递同一真实 KIND Job 时仅触发一次有效交付。

3. **边界上限、取消清理与丢失响应恢复**（`script_contract.py:31-147`、`skill_executor.py:47-60`、`capabilities.py:2252-2392`）
   - 在真实 KIND 中实测 **4 MiB 脚本包 + 4 × 512 KiB（合计 2 MiB）业务输入** 在同一 Job 内交付执行并返回预期结果；实测单输入 `512 KiB + 1 B`、总输入 `2.5 MiB`、包 `> 4 MiB` 均返回 HTTP `422` 拒绝。
   - 实测故意篡改 attach 输入帧后，容器在打印 `SUNMOON_INPUT_ACCEPTED` 前退出且不会执行用户脚本，`status()` 报告 `failed`，第二次投递被拒且不会重发；实测等待输入期取消与运行期取消均彻底删除 Job、终止 Pod（状态归 `absent`）。
   - `SkillExecutor.start` 在网络丢失 `/input` 响应（非 4xx 拒绝）时保留 `"dispatching"` 状态交由 `reconcile_scripts` 按原 `call_id` 查回唯一真实回执（`test_lost_upload_response_recovers_through_status_without_sending_again` 核对仅发一次 `/prepare` 与一次 `/input`）。

4. **双后端实库 + 真实 KIND `scripts/local-integration/script_inputs.py` 端到端联调**
   - 使用两个独立本地 PostgreSQL 16 `*_tests` 库（`agy_kb_req5_tests`、`agy_base_req5_tests`）运行 KnowBase 与 KnowBench 真实迁移及 `script_inputs.py` 连接真实 KIND 供给器，完成 KnowBase `text/1`（`21`）授权读取 → KnowBench 批准 → 隔离容器 `double.py` 计算 → `reconcile_scripts` 归档产物 `b"42"`（输出 `KnowBase text/1 -> exact KnowBench approval -> isolated Job -> retained result 42`）。

## 代码合理性评价与完善建议（非阻断）

两阶段（轻量摘要 `POST /prepare` 预留空 Job → 二次鉴权/重读材料后 `PUT /input` 流式传参 + JSON Patch `uid` & `claimed` 条件互斥）彻底消除了大体积 Base64/敏感资料长期滞留 Secret 或事件流的问题，容器边界与 RBAC 收敛也很规范。提出以下 4 条非阻断完善建议：

1. **`script_jobs.py:65-81` 共享 `NetworkPolicy` 在并发多用户预留时存在 `409 Conflict` 竞争风险（建议修复）**：`ScriptJobs.reserve` 每次为新用户建 Job 都会调用 `await self.kube.apply("networkpolicies", ...)`，而 `KubeClient.apply`（`provisioner.py:185-198`）在对象已存在时会无条件发起携带 `resourceVersion` 的 `PUT` 更新同一个静态名字 `skill-execution-deny-all`。若两个不同账号同时启动脚本并进入 `reserve`，第二个请求会因为 `resourceVersion` 竞争在 `PUT networkpolicies` 上吃到 Kubernetes `409 Conflict` 而意外失败。建议在 `reserve` 中对静态 `skill-execution-deny-all` 改为仅在 `GET` 返回 `None` 时 `POST` 创建（并吞掉并发创建产生的 `409 AlreadyExists`），避免多租户并发误伤。
2. **`skill_executor.py:53-59` 与 `capabilities.py:2287-2392` `/input` 连接级瞬断的快速失败识别**：目前 `SkillExecutor.start` 捕获全部 `httpx.HTTPError` 并返回 `{"state": "running"}`，以兼容“响应丢失但已送达”。但如果是 `httpx.ConnectError` / `ConnectTimeout`（根本未建立连接或未发包）发生在 `prepare` 刚成功之后，Job 仍停在 `sunmoonai.com/delivery="waiting"` 并空等 `activeDeadlineSeconds: 90` 及 `reconcile_scripts` 的 2 分钟超时上限后才标为 `unknown`。建议区分“连都没连上/未发送”或让 `status` 对长期处于 `waiting` 未领取的过期预留更快回收。
3. **`provisioner.py:165-174` 大帧 attach 传输窗口与读 ACK 上界观测**：`send_script_input` 整体使用 `asyncio.timeout(15)` 覆盖 WebSocket 握手 + 最大约 8–10 MiB 分块写入 + 容器 `json.loads` 吐回 `SUNMOON_INPUT_ACCEPTED`。本次在本地 KIND 实测 4 MiB 包 + 2 MiB 输入轻松过关，但在未来集群跨节点高负载或容器刚被 CPU CFS `500m` 节流时，建议记录 attach/解码耗时指标并对超时时间做显式压测校准。
4. **`script_inputs.py:59` `material_text` 分页单位假设留注**：`offset += len(part)` 依赖 KnowBase `read_input` 以字符偏移分页而外层 `len(data) > FILE_LIMIT` 按 UTF-8 字节计数，配合 `for _ in range(16)` 上限暗含每页不少于 ~32 KiB（全多字节文本场景）；建议在注释或契约测试中显式声明与 KnowBase 分页步长的依赖关系，以免下游缩小页长后触发提前截断报错。

## 验证结果与范围边界

- **KnowBench 后端（`f392957` + 独立 PG 16 tmpfs `127.0.0.1:55442`）**：
  - `.venv/bin/python -m pytest -q tests/test_script_inputs_db.py tests/test_skill_execution_db.py tests/test_skill_executor.py tests/test_calls_db.py tests/test_kernel_invariants.py`：**`35 passed in 19.11s`**。
  - Ruff（`4fd5942..f392957` 涉及 Python 文件）：**`All checks passed!`**；Pyright（应用代码）：**`0 errors, 0 warnings, 0 informations`**。
- **供给器单测（`sunmoonun/infrastructure/applications/component-images/sandbox-platform/provisioner`）**：
  - `PYTHONPATH=. .venv/bin/python -m pytest -q tests`：**`23 passed in 0.51s`**。
- **真实 KIND 隔离命名空间（`sunmoon-kind` -> 临时 `agy-script-probe`，已自动销毁清理）**：
  - `script_probe.py`：**通过**（`{"passed": true, "script_package": true, "named_inputs": true, "python_shell_node": true, "credential_free": true, "cluster_network_denied": true, "artifact_return": true}`）。
  - 边界、并发、篡改与取消实测：**4 MiB 包 + 2 MiB 输入 & 双 `ScriptJobs` 并发领取通过**；超限（`> 512 KiB` / `> 2 MiB` / `> 4 MiB`）**返回 422 拒绝**；篡改输入帧容器立即失败且阻止重发；等待中与运行中取消均完成删除确认。
  - 双后端集成 `python3 scripts/local-integration/script_inputs.py`（两个 PG 16 测试库 + 真实 KIND 供给器）：**`KnowBase text/1 -> exact KnowBench approval -> isolated Job -> retained result 42`**。
- **范围边界**：用户脚本开关仍保持关闭；KnowBase 对象存储与登录身份在 `script_inputs.py` 中使用测试夹具；生产集群构建分发与待办第 9 项专家端到端编排按计划后续单独验收。
