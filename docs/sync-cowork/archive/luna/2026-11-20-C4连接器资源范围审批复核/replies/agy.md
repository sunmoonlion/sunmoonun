# 评审回执：C4 连接器资源范围审批复核

- 请求：[request.md](../request.md)
- 轮次：1
- 核对提交：
  - 工作位置：本地（`wsl-dev`，`/home/zymun/worktrees/luna`，分支 `luna`；后端按 `4fd5942` 干净导出快照实测，未包含待办第 8 项未提交修改）
  - `knowbench-app/knowbench-backend`：`4fd5942`（基线 `6993698`）
  - `knowbench-app/knowbench-web-frontend`：`6e63616`（基线 `c506cda`）
  - `knowbench-app`：`399720f`（基线 `1fc0b2c`）
- 结论：**通过（无阻断项，附 4 条代码完善建议）**。待办第 7 项（接入实施方案 §17.6 第 9 项）的资源子集可复用只读授权、发送边界前统一凭证与撤权复核、返回值按 ID 投影与字段白名单裁剪、写入/外发附件字节摘要精确锁定及数据库迁移 `0048` 均已逐项核对并通过实测。

## 发现

### F01 [info] 5 项复核判断要点核查结果

1. **资源范围匹配、反扩权/反拼接、可追溯与返回结果严格投影**（`call_approval.py:11-142`、`call_repository.py:96-135`、`capabilities.py:1601-1709`）
   - `read_offer` 仅对显式声明了 `read_result_id_field` 且具备非空 `purpose` 的读取操作生效：剥离唯一可变资源路径 `read_resource_path` 后，连同 `source_asset_id`、`revision`、`purpose`、`selection_revision`、`method`/`authority_revision`/`parent_revision`、当前 `policy_digest` 及全部剩余参数（过滤条件、游标等）共同生成不可变 `read_offer_key`。
   - `active_call_read_scope` 借助 `detail->'operation'->'resources' @> cast(:resources as jsonb)` 与 `ResourceBinding.resolve()` 对 `values` 去重排序的规范化，精确允许原批资源 `[A, B]` 对子集 `[B]` 免弹窗复用，严格拒绝扩权至 `[C]`、拼接多份批准、修改过滤词/用途、超期（PostgreSQL 实时 `clock_timestamp()`）或已撤销（`read_revoked_at`）的调用。
   - 每次复用都生成独立 `dispatching` 调用行并记录 `read_approval_id` 追溯到原始回执，普通聊天下 `task_id` 保持为空；`scoped_result` 对返回记录强制校验标量 ID 落在请求 `allowed` 集合内且无重复、总条数不超上限、仅投影 `read_result_id_field` 与 `read_result_fields` 声明的标量字段，未声明映射或出现未审核嵌套对象/无关记录立即拒绝。

2. **真实方法步骤复用与正式方法精确直授隔离**（`capabilities.py:1640-1709, 2031-2054`、`formal_dispatch_authority.py:15-93`、`formal_host_calls.py:839-840`、`formal_method_calls.py:852-853`）
   - 方法步骤通过 `read_offer` 将 `authority_revision`、`parent_revision`、`step_id` 及权限截止时间纳入 `read_offer_key` 与 `read_offer_until`，在批准与发送边界前（`check_runtime_method` + `active_call_read_scope`）双重重核方法权限；权限一旦撤销，后续读取立即停止，正在等待审批卡恢复原 Task 时亦沿既有锁序与状态机安全拒绝。
   - `FormalHostCalls.decide`、`FormalMethodCalls.decide` 明确拒绝 `remember_read=True`，`formal_dispatch_authority.py` 沿用精确 `MethodAuthorization` 与祖先委派链核验，确保正式方法继续按单次精确批准派发。

3. **同服务同显示名多账号隔离、写/发附件字节校验、幂等派发与握手期撤权拦截**（`call_policy.py` `send_mcp`、`capability_mcp.py:258-272`、`capabilities.py:2068-2107`、`tool_operations.py:161-170+` `McpOperation.resolve`）
   - 同服务不同账号依赖 `source_asset_id` + 连接 `revision` + `account_label` 共同参与 `read_offer_key` 与 `call["digest"]` 计算，同名不混用。
   - 写/发操作通过 `McpOperation.resolve()` 解码 `inline_attachments_field` 并把文件 `name`、`size` 与 `sha256` 存入 `operation["attachments"]` 并参与批准卡片摘要，任何收件人、正文或同名附件字节篡改均使旧批准失效；`decide` 在会话与 call 行锁下将 `status` 从 `awaiting_approval` 原子转为 `dispatching` 并消费 Interaction，重复提交直接幂等返回现状，绝不二次派发。
   - 外部 HTTP MCP 调用统一经 `send_mcp` -> `RemoteMcp.call_checked` 在完成 `initialize` / `notifications/initialized` 握手后、发送 `tools/call` 前回调 `before_send()`（`_check_before_send` 锁内重核撤销、OAuth 凭据与方法授权），实测确认握手期间并发撤权时外部业务请求零发送，且已发出的不确定结果保留 `unknown` 不重发。

4. **多入口审批卡一致性、Playwright E2E 与只读单次默认守门**（`capability-action-card.tsx`、`entries.tsx`、`expert-run-screen.tsx`、`review_view.py`）
   - 聊天、工作时间线（`connectorCall`）与专家步骤面板（`subject.connector_call_id`）三处已统一接入 `PendingConnectorAction` / `CapabilityActionCard`，共同展示账号、连接修订、用途、效果/操作、目的地、零新增费用确认、资源值、附件大小与 SHA-256、可读期限、复用来源 ID 与撤销按钮；未声明 `read_result_id_field` 的只读工具不生成 `read_offer_key`，界面只显示单次允许与拒绝。

5. **0048 迁移可逆性验证与现有调用隔离**（`20261120_0048_call_read_scope.py`）
   - 新增可空列 `read_scope_key`、`read_scope_until`、`read_revoked_at` 与一致性约束 `ck_call_read_scope`、部分索引 `ix_call_read_scope`，既有历史 `workbench_calls` 记录默认三列均为 `NULL`，天然不授予任何范围授权。已在独立 PostgreSQL 16 完整实测 `0047 -> 0048 -> 0047 -> 0048 (head)` 升降级往返通过。

## 代码合理性评价与完善建议（非阻断）

C4 实现的“零隐式范围扩大 + 发送边界再核权 + 回包 ID/字段硬投影”在安全边界上非常扎实，前后端与方法体系融合得也很自然。提出以下 4 条非阻断完善建议：

1. **`capabilities.py:1823-1836` `revoke_read_approval` 仅接受原始批准 `call_id`**：前端 `capability-action-card.tsx` 已在发起撤销时自动取 `call.detail.approval?.origin ?? call.id`，但后端 `revoke_read_approval` 直接判断 `if not call.get("read_scope_key"): raise CapabilityError(...)`，未沿着复用记录的 `call["detail"].get("read_approval_id")` 自动追回原始批准。若未来直接通过后端 API（或第三方/CLI 工具）对某次复用调用 ID 发起撤销会失败，建议在后端增加对 `origin` 的透传/锁定或清晰报错指引。
2. **`call_approval.py:78-117` `scoped_result` 对可选字段缺失与报错消息全清的适配契约提醒**：一方面 `k not in record`（102 行）要求 `read_result_fields` 列出的字段必须在每条记录中全部显式出现（为 `null` 可接受，但部分真实服务在字段为空时会直接省略 JSON key）；另一方面一旦上游返回 `isError=True`，有映射配置的工具当前一律返回空内容 `{"isError": True, "content": []}` 以防止报错文本夹带未审核数据。建议在 `docs/managed-capabilities.md` 明确标注这两条适配器硬约束，避免接入真实服务时排查困难。
3. **`tool_operations.py:164-166` 配置 `inline_attachments_field` 后对“无附件发信”参数缺省的处理**：当配置了 `inline_attachments_field`（如 `"attachments"`）时，若模型发起一封不带附件的调用且未在 `arguments` 中包含 `"attachments"` 字段（或传 `None`），当前 `not isinstance(files, list)` 会直接拒绝，要求必须显式传入 `"attachments": []`。建议按真实工具 Schema 的 `required` 约束明确是在缺省键时视为 `[]` 还是维持显式空数组要求。
4. **`capabilities.py:1700-1704` 复用路径返回结果的安全读取**：当前直接返回 `done["detail"]["result"]` 下标访问；虽正常路径都会填充 `"result"`，但若在极罕见并发下外层 `public_call` 因 `recover_calls` 竞争返回了旧字典快照可能缺少 `"result"` 键，建议改为 `public_result(done["detail"].get("result"), call_id)` 与已有查结果路径保持一致风格。

## 验证结果与范围边界

- **KnowBench 后端（`4fd5942` 干净快照 + 独立 PG 16 tmpfs `127.0.0.1:55441`）**：
  - `.venv/bin/python -m pytest -q tests/test_connector_approval_scopes_db.py tests/test_formal_method_calls_db.py tests/test_formal_host_calls_db.py tests/test_formal_recursive_runtime_db.py tests/test_capability_mcp.py tests/test_formal_session_model_concurrency_db.py tests/test_method_capabilities_db.py tests/test_kernel_invariants.py`：**`105 passed in 146.92s`**。
  - Ruff（`6993698..4fd5942` 涉及全部 Python 文件）：**`All checks passed!`**；Pyright（应用代码）：**`0 errors, 0 warnings, 0 informations`**。
  - Alembic：`20261120_0047 -> 20261120_0048 -> 20261120_0047 -> 20261120_0048 (head)` 升降级往返通过。
- **KnowBench 网页（`6e63616`）**：
  - `pnpm check`（`tsc --noEmit`、`eslint .`、`check:i18n` 1386 键、`vitest run` **`504 passed (66 files)`**、`next build`）：**全部通过**。
  - Playwright Chromium（隔离端口 `PORT=3109 NEXT_PORT=3108 PAIR_FIXTURE_PORT=18180`，配对测试身份与模拟审批接口）：`CI=1 pnpm exec playwright test -g 'named resource scope'` -> **`1 passed (3.5s)`**（`rendering.e2e.ts:200` 通过）。
- **范围边界**：沿用第 6 项真实供应商与部署决策，本轮复核覆盖本地开发候选与隔离联调边界，真实供应商外部账号/连接器适配器及线上迁移/发布各自单独验收与记录。
