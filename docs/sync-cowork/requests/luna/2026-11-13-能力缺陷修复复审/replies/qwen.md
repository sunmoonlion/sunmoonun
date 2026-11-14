# qwen 回执：能力调用结果、连接变更与轮次授权修复复审

- 对应请求：[request.md](../request.md)
- 本轮：第 1 轮，2026-11-14，远程 `qwen` 工位。
- 复审版本：knowbench-backend `3897e3d`（行为修复）、`eb1465b`、`d5241e4`；knowbench-web-frontend `4c09a8d`；knowbench-app `539213c`；knowlab-app `cee838e`（子仓 knowlab-backend `e4c7633`）。基线 knowbench-backend `5644bfc`。
- 结论：**行为修复通过（评审 12.3 第 1、11、14 条都修对了）；请求第 5 项没有全部满足——knowlab 还有一份提供方 schema 没重新生成，knowlab 后端全量有 1 个失败，修掉再发。** 另有两点建议，不拦发布。
- 我没有改候选代码、没有部署、没有外部调用。本回执不代发起者结案，也不是发布批准。

## 1. 我做了什么

- 逐行读了 `5644bfc..3897e3d` 的应用层、领域层、基础设施层和 runner 改动，以及 `d5241e4` 为止的测试改动。
- 独立重跑（远程工位，隔离测试库，串行，没有配消息队列）：
  - knowbench-backend `d5241e4`：`ruff check` 过，`pyright` 0 错，`pytest` **2182 过、8 跳过、0 失败**（20 分 09 秒）。比发起者报的 2187 过、3 跳过多跳了 5 个，是我这边没配 broker，数对得上。
  - knowlab-backend `e4c7633`：`ruff check` 过，`pyright` 0 错，`pytest` **956 过、5 跳过、1 失败**（见第 3 节）。
- 用自己 11-13 的探针（真实 `RemoteMcp` 加假传输：握手成功、`tools/call` 发出后读超时）重跑：修复前抛 `CapabilityError`，现在抛 `CapabilityOutcomeUnknown`。

## 2. 请求的五项

| 项 | 结论 | 依据 |
| --- | --- | --- |
| 1 真实适配器的三类结果 | 通过 | `capability_mcp.py`：连接没建成记失败；JSON-RPC 的明确错误当明确结果；`tools/call` 发出后的读超时、断流、写错误、非 200、超限、坏回包、编号不对都记未知；总时限超时按是否已握手区分。`decide` 先接 `CapabilityOutcomeUnknown` 再接 `CapabilityError`。`test_real_mcp_adapter_outcomes_are_recorded_without_retry` 走的是真实适配器，12 种情况逐个验了落账、重复批准不再派发 |
| 2 连接变更后的旧审批和聊天 | 通过 | `prepare`：聊天只把出问题的能力从本轮去掉并提示，不改用户选择、不换账号，显式模式下依赖缺了的技能一并去掉；方法场景仍然拒绝。锁内复核保留。刷新、换凭据、停用再启用三种情况旧审批都被拒（`test_changed_connection_does_not_block_chat_or_reuse_old_approval`、`test_refresh_of_required_connection_still_blocks_method_step`） |
| 3 范围按持久记录关闭 | 通过 | 完成事件改按库里的 `turn_id` 且状态为 `applied` 关闭，不靠内存；`_expire_approvals` 里加了 `capability_revoke_sandbox`。我核了调用点：runner 启动后第一轮循环对新拿到的全部沙箱做接管，连接重建时也做，不是等下一条命令。迟到的旧轮次按 `turn_id` 对不上，关不掉新范围。正常完成后已提交的精确审批在时限内可批，接管或重连后不可批（含「先完成、后重连」），都有测试 |
| 4 稳定配置 | 如请求所述，本次没改 | 仍逐轮换令牌、有能力的用户每轮重载线程，留给公共调用身份那一批。空能力快路径成立：该用户没有任何资产且会话没有遗留范围时才跳过，不跳过方法场景 |
| 5 契约生成物和测试夹具 | **部分通过** | knowbench 侧三份动态方法 schema 和消费锁已一致，评审 12.6 的 19 个失败在我这里全部消失。knowlab 侧还漏一份，见第 3 节 |

测试改动我逐个看了：断言的变化都对应这次的行为变化（聊天不再整轮拒绝），没有靠放宽断言过关。`test_expert_runtime_tools.py` 是给 runner 传了 `capabilities=None` 绕开，这个用例因此不再覆盖能力路径，可以接受，记一笔。

## 3. 要修的一项

`knowlab-backend/app/tests/test_knowbot_incubation_contract.py::test_schema_files_are_generated_from_the_models[incubation-request.schema.json]` 失败：`507a07f` 给工作稿的步骤加了 `managed_capabilities`，`incubation-request.schema.json` 没重新生成（测试提示 `python -m app.domain.knowbots.schema`）。和评审 12.6 第一类是同一种问题，上次只修了 knowbench 这边。请重新生成并核对有没有消费方锁要同步，然后在 knowlab 后端跑一次全量。请求里 knowlab 报的是 60 项契约子集，没跑全量。

## 4. 两点建议（不拦发布）

1. `tools/call` 收到 401、403 现在落进「非 200」这一支，记成未知，原来「请重新授权」的提示丢了。这两种状态可以确定服务端没执行，建议记失败并保留重新授权的提示；其它 4xx、5xx 记未知是对的。
2. 聊天里有能力被排除时，每一轮都会往模型输入里加一段提示，直到用户去面板处理。量不大，但建议前端在输入框附近给一个明显的入口，免得用户一直不知道。

## 5. 没做的

没连线上、没接真实 MCP 服务、没跑付费模型、没验发布分支上的摘取结果（请求写明另行复验）。前端只看了这次的提示改动。
