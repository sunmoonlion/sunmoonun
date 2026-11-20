# 评审回执：Skill 目录与正文分存复核

- 请求：[request.md](../request.md)
- 轮次：1
- 核对提交：
  - 工作位置：本地（`wsl-dev`，`/home/zymun/worktrees/luna`，分支 `luna`；后端按独立导出的固定提交快照实测，未受工作区待办第 8 项未提交改动干扰）
  - `knowbench-app/knowbench-backend`：`f3268eeffd9725a234e442d588b0f258ab859e31`（比较基线 `de6e586fc6cc97ef2cabc7ff3a4f538bcf478465`）
  - `knowbench-app/knowbench-web-frontend`：`5bb7f294603929562f2813aa6781c737dfa2ab48`（比较基线 `d1e58d8352077dac2e4a3e107f86ee2e7d666970`）
  - `knowbench-app`：`5999c3e2b00df790f2bc28500ed573af40e1d1f6`（比较基线 `69ca442bdb81ff3a37cedd364f35366b82d3475b`）
- 结论：**通过（无阻断项，附 3 条代码完善建议）**。待办第 4 项（接入方案 §17.6 第 6 项）及 `f3268ee` 的专家原生交互时序修复均已通过代码逐行审计、PostgreSQL 16 迁移升降级与性能实测，达到本地开发候选完成标准。

## 发现

### F01 [info] 5 项复核要求核查结果

1. **0046 迁移与事务/并发一致性**（`knowbench-backend/app/alembic/versions/20261119_0046_skill_files.py:1-73`、`capability_repository.py` `CapabilityRepositoryMixin.capability_insert`）
   - 迁移以 `LOCK TABLE workbench_capability_assets IN SHARE ROW EXCLUSIVE MODE` 并发写锁起手，新建只插不改的 `workbench_skill_files(asset_id, path, data)`，通过触发器 `skill_files_immutable`（`reject_skill_file_update()`）与检查约束 `ck_skill_catalog_metadata` 强制禁止目录记录保留 `content` / `resources`；并在剔除旧大字段前执行双向 `DO $$` 核对（逐文件 `path`、`octet_length`、`sha256` 及 `SKILL.md` 原始字节匹配），不一致直接回滚事务。
   - `CapabilityRepositoryMixin.capability_insert` 将资产插入、幂等键冲突校验与 `workbench_skill_files` 插入包裹在同一 `self.transaction()` 中，保障安装中途失败整笔回滚与同请求幂等重试语义一致。
   - 在隔离 PostgreSQL 16 中使用 40 项（8 项纯指令 + 32 项 ZIP、104 个文件、5,505,216 原始字节）完成 `seed -> before -> migrate -> after -> instructions` 及已填充数据的 `0046 downgrade -> upgrade` 往返演练，前后 `manifest_sha256`（`6c118fb5f11f834ad1a3c5bec04dc6784fcf66d8c20e65bee007280681499c84`）严格一致。

2. **目录元数据分离、设置页展开读取与模型/安装状态权限隔离**（`capabilities.py` `list_assets` / `installed_instructions` / `skill_resource`、`domain/workbench/capabilities.py` `public_asset`、`capabilities-section.tsx`）
   - `public_asset` / `SkillDetail` 移除 `content` 与 `resources`，列表接口仅返回元数据（含 `files` 描述项）；设置页仅在 `asset.status !== 'disconnected'` 时渲染 `InstalledInstructions`，展开 `<details>` 后才触发 `GET /api/workbench/capabilities/skills/{id}/instructions`（响应头 `Cache-Control: private, no-store`，前端 `gcTime: 0`）。
   - 安装者 `disabled` 状态仍保留本人展开说明权限（`skill_file` 条件 `a.status <> 'disconnected'`），卸载后（`disconnected`）前端收起入口且后端返回 404；模型走 `verified_read` + `skill_files` / `skill_read` 路径，停用、换轮与跨账号均被拦截，列文件不载入正文。

3. **路径安全、多模态/二进制返回、脚本批准重核与网页 ZIP 导入形态**（`skill_package.py`、`capabilities.py` `decide`、`capabilities-section.tsx` `SkillForm`）
   - `resolve_path` 与 `unpack_skill` 限制相对规范路径、拒绝符号链接与加密包、校验 PNG/JPEG 与非 UTF-8 二进制；文本按字符支持 Unicode 分页。
   - `decide` 批准 `skill_script` 时在事务内通过 `skill_package_files` 重新装配 `script_input`，重放、拒绝或失效批准无法再次派发；`consume_interaction` 消费锁防止并发重复批准；`SkillForm` 将请求参数封装为单一 `submission()` 并传入 `save.mutate(submission())`，消除了文件未读完误按纯指令提交的形态竞争。

4. **PostgreSQL 16 性能复测对比（独立 tmpfs 实例）**
   - 迁移前（`de6e586`，同库样本 `luna_skill_catalog_measure`）：`sql_calls_per_request = 1`，`sql_result_field_bytes = 1,339,804`，`http_body_bytes = 1,342,832`，`p50 = 19.032 ms`，`p95 = 26.197 ms`。
   - 迁移后目录（`f3268ee`）：`sql_calls_per_request = 1`，`sql_result_field_bytes = 26,526`（降幅 98.0%），`http_body_bytes = 32,752`（降幅 97.6%），`p50 = 3.966 ms`，`p95 = 4.848 ms`。
   - 迁移后单独读取 `SKILL.md`（`instructions`）：`sql_calls_per_request = 1`，`sql_result_field_bytes = 32,768`，`http_body_bytes = 32,770`，`p50 = 3.566 ms`，`p95 = 4.847 ms`。

5. **`f3268ee` 专家原生交互与 Attempt 绑定时序修复**（`runner.py:825-835, 944-946, 1031-1044, 1465-1479`）
   - 在 `expected_attempt` 场景为 `waiter` 创建 `attempt_bound` Future；`on_server_request` 在受理交互/审批/提问前先检查 `thread_id` 并 `await asyncio.shield(binding)`，若 `bind_turn` 失败、轮次已被替换（`active_turns.get(thread_id) != turn_id`）、连接变更或 `_forget_turn` 提前收尾（将未完成 `binding` 设为 `False`），直接返回 JSON-RPC `-32600`，避免在 Attempt 尚未绑定前把 Task 切至 `WAITING` 导致失败。

## 代码合理性评价与完善建议（非阻断）

总体设计合理且干净：分表与数据库约束形成底层不变量，性能收益显著，网页/后端交互闭环严密。发现以下 3 处非阻断完善点供后续优化：

1. **`runner.py:1042` 建议在 `.set_result(bound)` 前增加状态保护**：当前直接在 `bind_turn` 的 `try/except` 后调用 `waiter["attempt_bound"].set_result(bound)`。虽然目前 `_forget_turn` 仅在 `turn/start` 异常分支（1025 行）和外层 `finally`（1199 行）执行，但若未来有并发路径（如提前通知回调或强制清理）先调用 `_forget_turn` 把 `attempt_bound` 置为 `False`，1042 行无条件 `.set_result(bound)` 会抛出 `asyncio.InvalidStateError`。建议改为 `if not waiter["attempt_bound"].done(): waiter["attempt_bound"].set_result(bound)`。
2. **`runner.py:1468` 对无 `waiter` 或缺 `turnId` 的迟到专家原生请求建议显式诊断**：当前若方法轮已结束并执行了 `_forget_turn`（`waiter is None`），`on_server_request` 会跳过 `attempt_bound` 门控并落入后续通用处理分支再因 DB 状态拒绝；若在方法任务上下文下缺少对应活跃 `waiter` 也直接返回明确错误/日志，可减少无效交互表查询与时序混淆。
3. **`capability_repository.py` `capability_insert` 大包批量插入扩展性提示**：当前在单事务中使用 SQLAlchemy `executemany` 插入 `workbench_skill_files`（上限 256 个文件 / 4 MiB），开发候选阶段实测表现稳定；若后续放开更大文件数量限制，建议评估 `UNNEST` 批量插入以控制大包安装耗时。

## 验证结果与范围边界

- **后端（`f3268ee` 干净快照 + 独立 PG 16 tmpfs `127.0.0.1:55441`）**：
  - `.venv/bin/python -m pytest -q tests/test_capability_runner.py tests/test_method_tools_db.py tests/test_workbench_runner_db.py tests/test_skill_package.py tests/test_skill_package_db.py tests/test_skill_execution_db.py tests/test_calls_db.py tests/test_capabilities_db.py tests/test_capability_routes_db.py tests/test_skill_dependencies_db.py tests/test_skill_installation_db.py tests/test_kernel_invariants.py`：**`170 passed in 134.43s`**。
  - `.venv/bin/ruff check`（涉及文件）：**`All checks passed!`**；`.venv/bin/pyright`（应用代码）：**`0 errors, 0 warnings, 0 informations`**。
  - 迁移演练：`skill_catalog_measure.py` 全流程及 40 样本下 `0046 downgrade -> upgrade` 均通过；全链 `0045 -> 0046 -> 0047 -> 0048 -> 0047 -> 0046 -> 0045 -> 0048` 通过。
- **网页（`5bb7f29` 干净快照，`WEB_INTERACTION_CONSUMER_VECTORS` 指向同工位 `tpl-app/contracts/web-interaction-v1.consumer-vectors.json`）**：
  - `pnpm test`：**`498 passed (66 files)`**。
- **范围边界**：遵循协作规则，未修改任何受审源码或 `request.md`；未运行生产部署或真实供应商请求。
