# C2 登记、调用身份和方法权限增量复审

- 类型：独立代码复审
- 状态：待 qwen 接手；开发候选，尚未发布
- 发起身份：luna
- 执行身份：qwen
- 主工位：远程 `/home/zym/worktrees/qwen`，各仓分支 `qwen`
- 回执：`replies/qwen.md`
- 发布边界：本卡不授权部署、开放作者入口、启用脚本或发起真实外部动作。

## 固定版本与范围

| 仓 | 评审基线 | 目标提交 |
| --- | --- | --- |
| knowbench-backend | `d5241e423684490095f769c84d01710c65aee872` | `34f516920ef667907a4b81acd83419ecbde0c8bf` |
| knowbench-web-frontend | `a9dfe11035b246f44f333df30bf20a9ff7fe901d` | `14c3bf352a53fe8d416c72568294f4698bde393e` |
| knowbench-app | `ae5574e8411978edffe6754cb38a5808e68e5b71` | `c138150330dcd0f16b8bb5c4736b8c84051438b8` |
| knowlab-backend | `e4c7633d75ef9efe7d011cba8fa5f1600bc74165` | `57152cb45d97e9606b50baf1a5d91ad15012899a` |
| knowlab-app | `59d58cc9d9ea2916f576cf3f8f42b71e42d1fc1a` | `28a463e75568915cd11e4643dcace06d6afb0026` |

后端范围包括此前尚未独立复审的共同登记、真实宿主调用身份及可信操作映射，不能只审最后一个方法权限提交。KnowBench 父仓范围为本轮 Schema/消费锁及指针；KnowLab 仍保留作者入口限制。KnowMart 无源码修改，仅在 `b5f83b27bb02d39c983be020b0e2994de161b213` 重跑消费验证。

依据：[接入实施方案 §17.6–17.7](../../../../总纲/mcp和skill接入实施方案.md)、[方法主稿](../../../../总纲/专家方案设计/专家孵化方案/luna/专家及专家团孵化模板.md)、[实现与限制](../../../../../../knowbench-app/knowbench-backend/docs/managed-capabilities.md)。Jenkins #94 首批缺陷修复已发布；本卡的 C2 候选不在 #94 中。

## 重点检查

1. 共同登记只保存技术定义；远端 annotations、描述和模型输入不能成为可信操作或权限。多账号共用定义身份，但账号修订与凭据分别核查。
2. 两个 MCP 入口以 runner 持久事件核 session/thread/turn/server/call、工具名与完整参数；Skill 读取同样核验。真实调用身份幂等，参数相同的另一调用不被误合并，未知写结果不重发。事件竞态等待是否有界、是否在锁外。
3. 运营配置绑定服务、工具与描述摘要，声明业务操作、性质、资源角色及平台上限。未核定或定义变化后，选择、目录、调用、批准能否一致拒绝；缺失证据不补造。
4. 方法 `access_requirements` 独立于 URL/工具名绑定，绑定引用要求编号。当前只支持 connector 的精确资源、顶层外发字段、固定去向、无条件必需和缺项暂停；不能误宣称已经支持动态资料范围或其它资源种类。
5. 网页确实展示操作、资源、外发字段、去向和用途，用户按方法上下文确认所选账号。保存的范围冻结到运行工具，调用前越界不生成审批，批准前复核。方法声明本身不是用户授权；每次外部操作仍需批准。
6. 当前只有可信 Task/Attempt 的方法根范围，没有通用父子调用树，因此没有接受模型自报父 ID 的委派接口。父子范围、共同账、孵化准入未实现的边界是否写清；没有把权限纯函数冒充完整 C2。
7. KnowLab 正确生成/校验权限字段，作者保存、编译、导入、发布仍拒绝能力接入。动态执行 Schema、作者 Schema、生成模型、摘要锁、网页响应消费是否一致。旧无要求编号的工具绑定不继续执行。
8. 普通聊天／工作安装 Skill 的技术依赖不需要孵化或方法权限字段；旧能力失效不拖垮无关聊天。脚本仍无连接器调用能力且用户开关关闭。

## 已做验证

以下全部为定向回归，不是候选全量；没有真实 Codex app-server 或外部供应商账号验收。

| 范围 | 结果 | 本工位日志 |
| --- | --- | --- |
| KnowBench 权限、数据库、MCP HTTP、runner、Skill/脚本与分层 | 186 通过、0 跳过 | `/tmp/c2-method-tests.log` |
| KnowBench 方法运行契约与计划 | 129 通过 | `/tmp/c2-method-catalog-tests.log` |
| KnowLab 编译、作者限制、方法与消费锁 | 132 通过 | `/tmp/c2-method-knowlab-tests.log` |
| KnowMart 清单与目录消费者 | 15 通过 | `/tmp/c2-method-knowmart-tests.log` |
| 网页能力组件与契约 | 16 通过 | `/tmp/c2-method-web-tests.log` |
| 两后端 Ruff/Pyright；网页 TypeScript/ESLint/i18n | 通过 | `/tmp/c2-method-{ruff,pyright,knowlab-ruff,knowlab-pyright,web-typecheck,web-lint,web-i18n}.log` |

后端权限回归入口（在 knowbench-backend/app 用现有 `.venv/bin/python -m pytest -q`）：

```text
tests/test_method_access.py tests/test_method_access_db.py
tests/test_tool_operations.py tests/test_tool_operations_db.py
tests/test_tool_invocation_db.py tests/test_capabilities_db.py
tests/test_method_capabilities_db.py tests/test_skill_execution_db.py
tests/test_method_tools_db.py tests/test_capability_routes_db.py
tests/test_skill_package_db.py tests/test_workbench_mcp_routes.py
tests/test_method_runner_mcp_db.py tests/test_tool_registry.py
tests/test_capability_mcp.py tests/test_capability_runner.py
tests/test_skill_dependencies_db.py tests/test_skill_dependencies.py
tests/test_config_security.py tests/test_kernel_invariants.py tests/test_layering.py
```

本工位有已存在的隔离 PostgreSQL，`127.0.0.1:55432` 的 `knowbench_tests`；凭据只从私有 `/home/zym/.config/sunmoon-remote-test/pg.env` 读取，不输出、不写入回执。临时包装脚本 `/tmp/c2-method-test-run.py` 仅设置测试数据库环境并执行上述测试；不要求依赖该临时文件，可按项目测试说明重建环境。所有数据库测试串行，不同时开第二轮全量，不操作生产库或真实连接器。

## 允许动作与交回

允许只读代码、使用现有隔离测试环境复跑验证、写自己的回执并按协作规范提交推送。默认不改被评代码、不清理他人进程、不发邮件、不付费调用模型。需要修复时列问题、可复现路径和建议，由 luna 处理。

请分别说明本增量是否通过，以及仍未实现的 C2/C3–C6 项；不要因本增量通过就判整套方法接入可以开放。最终发布仍需完整候选全量、独立复审、固定 Codex 协议及相应场景验证。线上真实数据需要发布前重新盘点，必要时一次性迁移；不保留旧绑定执行分支。

## 处理记录

- 2026-11-14：luna 提交固定候选及上述定向验证，等待 qwen 独立复审。未部署。
