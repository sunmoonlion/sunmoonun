# fable 回执

- 对应请求：`../request.md`
- 本轮：第 1 轮
- 身份说明：卡面执行身份是 qwen、回执文件 `replies/qwen.md`。所有者 2026-11-14 直接指示 fable（Cursor 中的 Claude Fable 5.2）按本卡写回执，所以写在 `replies/fable.md`，不占用 qwen 的文件名，也不代替 qwen 的回执。
- 实际检查版本（卡面固定提交；主工位已推进，按提交读取并导出快照）：
  - knowbench-backend `34f516920ef667907a4b81acd83419ecbde0c8bf` → `614d0bdc868d3255360c754049a9020d329372f2`
  - knowbench-app `c138150330dcd0f16b8bb5c4736b8c84051438b8` → `154b1cb65b708bf3cc2b68583fc4780b0657d176`（gitlink 已核对：后端 `614d0bd`，网页仍是 `14c3bf352a53fe8d416c72568294f4698bde393e`）
- 结论：**有问题**。适用范围仅限本增量（0041 迁移、共同调用账、调用上下文与 Task 根记录、两个 MCP 入口的记账与回包）。
  - F01 是本增量引入的回归，已复现：测试产出到期清理会被新外键挡住。建议修复后再复审，不建议带着它发布。
  - 记账、幂等、状态投影和迁移保全这几条主线，阅读与复跑都没有发现错误（见“逐条核对”）。
  - F02、F03 为低级别；另有几项说明。
  - 本结论不代表整套方法接入可以开放，见“仍未实现”。

## 发现

### F01 会话树清理被 `workbench_calls` 的新外键挡住（本增量缺陷，已复现，建议发布前修）

- 问题：0041 给 `workbench_calls` 新增 `task_id REFERENCES workbench_tasks(id)` 和 `attempt_id REFERENCES workbench_attempts(id)`，都没有删除策略；而 `delete_session_tree` 是先删 `workbench_tasks` 再删会话，没有先处理调用记录。只要会话里有带 Task 的调用记录，删除就失败。
- 证据：
  - `alembic/versions/20261114_0041_calls.py` 的两处 `ADD COLUMN … REFERENCES …`；`app/infrastructure/workbench/repository.py` 的 `delete_session_tree`（约 2105–2126 行）依次删除 `workbench_approval_log`、`workbench_tool_grants`、`workbench_commands`、`workbench_tasks`，最后删 `workbench_sessions`。
  - 在 `614d0bd` 快照里写了两个只存在于快照的复现用例（不提交）：一个先走受管方法调用，一个只记一条带 Task 的平台工具调用，然后调用 `delete_session_tree`。两个都失败：`ForeignKeyViolationError: update or delete on table "workbench_tasks" violates foreign key constraint "workbench_calls_task_id_fkey" on table "workbench_calls"`，出错语句是 `delete from workbench_tasks where session_id = $1`。日志 `/home/zym/.cache/fable-c2-review/r2-repro.log`。
  - 这是回归：0040 的 `workbench_capability_calls` 只引用会话且带 `ON DELETE CASCADE`，增量之前清理不受调用记录影响。
  - 仓内现有的清理测试 `test_parallel_approval_dispatches_only_once_and_session_cleanup` 只覆盖没有 Task 的聊天会话，所以没有暴露。
- 影响：调用链是 `test_runs.py` 的 `cleanup()` → `purge_test_run` → `delete_session_tree`。本增量之后，平台工具调用也进共同账并挂在 Task 下，所以跑过任务的测试会话基本都会带这类记录，到期清理都会失败。`cleanup()` 的循环没有逐项容错，第一条失败后，后面的到期清理和 `clear_test_outputs` 在这一轮都不会执行（下一轮仍会卡在同一条上）。结果是测试会话、任务、交回物超过保留期后仍留在库里。
- 建议：在 `delete_session_tree` 里先删该会话的 `workbench_calls`（同一条语句内父子记录可以一起删），或给两处外键定明确的删除策略；补一条“带 Task 调用记录的会话可以清理”的数据库测试。
- 范围外提示（只读核对，未在其上跑测试）：knowbench-backend 当前 HEAD `d3f7dbad` 的 `delete_session_tree` 没有变化；其新增的 0042 表 `workbench_method_authorizations` 对 `workbench_calls` 的外键同样没有删除策略，修复时需要一并考虑。

### F02 改名后保留了 0040 的旧唯一约束和旧命名（低）

- 问题：`workbench_calls` 上仍有 0040 留下的 `UNIQUE(session_id, digest)`（约束名 `workbench_capability_calls_session_id_digest_key`），主键和索引也还是旧名（如 `ix_capability_calls_session`）。
- 证据：复现用例 `test_report_constraints_on_shared_call_table` 打印的约束与索引清单，见 `r2-repro.log`。`add_call` 的 `ON CONFLICT` 只指向 `(owner_actor_id, session_id, call_key)`。
- 影响：`digest` 含调用身份快照，按现在的写法两条不同调用不会撞上，所以目前不出错。但“按真实调用键去重”的设计下，这条约束是多余的第二条去重路径；一旦将来 `digest` 的组成变了，撞上时会以完整性错误冒出来，而不是走幂等分支。
- 建议：迁移里明确删除，或在文档写明保留的理由。

### F03 0041 downgrade 的拒绝分支没有仓内测试（低，测试缺口）

- 问题：`test_populated_migration_preserves_evidence_and_revokes_old_execution` 只在全是受管记录时走了 downgrade／upgrade；“存在平台或方法记录时 downgrade 拒绝”没有测试。
- 证据：`tests/test_calls_db.py` 117–195 行。我在快照里补跑了一个用例：先记一条带 Task 的平台调用（连同方法根记录共 2 行），再调 0041 的 `downgrade()`，结果按预期抛出 `shared call history requires forward repair, not downgrade`，表和 2 行记录保持不变。日志 `r2-repro-downgrade.log`。
- 影响：行为本身是对的，只是没有回归保护。
- 建议：把这条用例补进仓内。

### 说明项（不算缺陷，供发起者取舍）

- 迁移把旧的待批调用改成 `expired`、派发中的改成 `unknown`，并把已有选择的运行态标成中止，但不处理正停在等待状态的方法任务本身。发布前需要先排空，或写明这些任务升级后的处理办法。
- `attempt_id` 只有在本轮对话被绑定到 Attempt 时才有值（`runner.py` 里只有拿到 `expected_attempt` 才调 `bind_turn`）。按阅读推断，没走这条绑定路径的任务，其调用记录只挂 Task 根、`attempt_id` 为空。这一点我没有用测试单独验证。
- 中继回包新增了按整个 JSON-RPC 包 90,000 字节（`TOOL_RESULT_MAX_BYTES`）的上限，超限记 `unknown`。这是行为变化；KnowBase 一侧的回包上限我没有核对，是否会出现“资料端成功、这边记未知”需要对照确认。
- 平台侧抛出的 `WorkbenchError` 一律记 `unknown`，偏保守。
- 平台回包全文存进 `detail.response`，调用量大时这张表会增长较快，建议定保留期（与 F01 的清理路径相关）。

### 逐条核对（对应卡面 6 条重点）

1. 迁移保全证据、不重放、脚本 `connection_id` 为空：阅读 0041 并复跑 `test_populated_migration_…` 通过；旧记录的 `detail`、`digest` 不变，`call_key` 为 `historical:<id>`，旧待批不能再批准执行；脚本记录的 `connection_id` 在存储和对外回执里都为空，来源资产在 `source_asset_id`。成立。
2. 任务切换、换 Attempt、跨用户／会话、重复请求、并发写入：`call_context` 锁住 Task 后再建根记录，会话的当前任务或 Attempt 变了就拒绝；重复请求靠 `(owner, session, call_key)` 唯一约束收敛。`CallLedger.begin` 在最外层事务退出时提交，确实发生在派发之前。相关测试通过。成立。
3. Task 根记录与状态：每个 Task 一条方法根记录（部分唯一索引 `uq_calls_root_task`）；`cas_task` 是任务状态的唯一更新路径，根记录状态随之更新。成立。
4. 回包与缓存：重复请求先过 `guard.check` 再读已存回包；没有回包的（未知结果）拒绝重派；`relay.tools()` 有带时限的缓存。成立。
5. 回归：见“验证”，217 通过。
6. 0041 downgrade 拒绝：行为成立（我补跑的用例通过），仓内缺测试，见 F03。

另外确认：应用代码里没有残留的 `workbench_capability_calls` 引用；`capability_call`／`capability_calls` 只读 `origin='managed'` 的记录。

## 验证

环境：用 `git archive` 把 knowbench-app `154b1cb` 与 knowbench-backend `614d0bd` 导出到仓外隔离目录 `/home/zym/.cache/fable-c2-review/wt2/`，没有切换或改动主工位任何仓的工作区。解释器沿用主工位后端现有 `.venv`（依赖以当前安装为准）。数据库为卡面指定的隔离 PostgreSQL `127.0.0.1:55432/knowbench_tests`，每例独立 schema；凭据只从私有文件读取，未输出；全部串行。运行期间工位上另有其他代理的 pytest 进程（非本人启动，未清理）。

已运行（在快照的 `knowbench-backend/app`，`python -m pytest -q`）：

| 范围 | 文件 | 结果 | 日志 |
| --- | --- | --- | --- |
| 相关回归 | 登记与方法权限卡列出的 21 个文件，加 `test_call_outcomes.py test_calls_db.py test_calls_mcp_db.py test_skill_execution.py test_workbench_ledger_db.py`，共 26 个文件 | 217 通过、0 失败、0 跳过（222.92 s） | `/home/zym/.cache/fable-c2-review/r2-backend-tests.log` |
| 复现用例（仅在快照，不提交） | `test_fable_review_repro.py` 的两个清理用例和一个约束清单用例 | 2 失败（即 F01）、1 通过 | `…/r2-repro.log` |
| downgrade 拒绝（仅在快照，不提交） | `test_fable_review_repro.py::test_downgrade_refuses_shared_history` | 1 通过 | `…/r2-repro-downgrade.log` |

说明：卡面只给了“215 项”和 49 项复验的文件名，没有给 215 项的完整清单，我的 26 个文件是自己选的，数量不能直接比较。49 项复验涉及的 6 个文件都在我的 26 个文件里。

未运行：

- Ruff、Pyright、`git diff --check`。
- 后端全量测试。
- 在带真实历史数据的库上执行 0041（只跑了仓内用测试数据构造的迁移用例）。
- 固定版 Codex app-server 真实协议、真实 KnowBase 中继、真实连接器。
- 当前 HEAD `d3f7dbad` 上的任何测试（只读了 `delete_session_tree` 和 0042 的外键定义）。

无法验证：线上现有调用记录、待批调用和等待中任务的实际数量与状态。

## 仍未实现（卡面与文档自述，本人未逐项验证其现状）

- C2 内：嵌套方法展开与子方法调用身份（现在只有 Task 根记录，根记录是审计身份，不是授权）；父子权限交集与撤权传播；三类方法的孵化准入；共同的业务核权规则；只读授权复用；稳定的 MCP 配置；Skill 内容分离；依赖交付与连接生命周期；资源端账号权限；动态资料范围及其它资源种类。
- C3–C6 全部。
- 作者入口与脚本开关保持关闭；没有固定版 Codex 真实协议和外部供应商验收；没有完整候选全量；线上数据需要发布前重新盘点。

本增量的结论不能作为开放方法接入、作者入口或脚本执行的依据。

## 交回

- 提交：本回执单独提交到 sunmoonun，只含本文件与另一张卡的 `replies/fable.md`（提交号见本文件的 git 历史）。提交后立即用 `./sunmoonun/docs/sync-cowork/sync/sync.sh push sunmoonun` 推送；如果推送没有成功，fable 会在本节追加说明。
- 没有修改任何被评代码，没有改 `request.md`；隔离快照、复现用例和日志都在仓外，不提交。需要复现用例原文可以向 fable 要，或直接看 `/home/zym/.cache/fable-c2-review/wt2/knowbench-app/knowbench-backend/app/tests/test_fable_review_repro.py`。
- 待 luna 处理：F01 修复并补测试后再复审（连同 0042 的同类外键）；F02、F03 及说明项自行取舍。
- 是否结案由发起者决定。
