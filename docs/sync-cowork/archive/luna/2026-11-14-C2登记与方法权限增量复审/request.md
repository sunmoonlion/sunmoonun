# C2 登记、调用身份和方法权限增量复审

- 类型：独立代码复审
- 状态：已完成本轮评审处理；所有者临时免除本次补丁复审，尚未发布
- 发起身份：luna
- 执行身份：qwen
- 主工位：远程 `/home/zym/worktrees/qwen`，各仓分支 `qwen`
- 回执：[qwen](replies/qwen.md)、[fable](replies/fable.md)（所有者另行指派）
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

### 2026-11-14 回执采纳

保留两份独立回执，不把不同提交、不同测试范围的结果相加。fable 审固定初始候选，qwen 另复验后续补丁，因此“旧候选有问题”和“后续补丁通过”不矛盾。

| 意见 | 处理与去向 |
| --- | --- |
| 两方 F01：孵化请求 Schema 漏生成及消费锁 | 采纳；补丁为 KnowLab 父仓 8925db96fded76940de2465ade6c078a74dc4f7e、KnowBench 父仓 c28aafcc225f430f0095b8ebc35dfe7c4f9d2a50。下一轮固定候选明确包含这两个补丁，回归清单加入 test_knowbot_incubation_contract.py。旧固定目标不改写。 |
| qwen F02 / fable F06：固定流程平台守卫未复核方法授权 | 已由后端 d3f7dbad9bbad7bcd576f6d1716b8dfb2117c4cc 修复，qwen 已复验。仍须纳入最终候选回归，不以此宣称正式方法派发完成。 |
| fable F02：网页与后端同批及旧页面缓存 | 采纳为发布门，纳入 §17.6 第 12 项：API、runner、网页及生成契约同批；明确旧标签页刷新/缓存失效行为并实测，不能靠旧字段兼容分支继续运行。 |
| fable F03：真实 Codex 元数据与事件时序 | 采纳为发布门：固定版本 app-server 分别运行平台、受管工具，保留脱敏事件与 _meta 对照；现有构造事件单测不能替代。无真实供应商测试条件须如实记录。 |
| fable F04：同步登记投影重复消耗 CPU | 纳入第 3、6 项性能验收，按资产/定义摘要测量并设计缓存；运营配置修订和撤权须实时重核，不能缓存授权结果。 |
| fable F05：错误原因码和中英文文案 | 纳入第 3 项网页整理，区分声明不匹配与运营定义缺失，同步前后端契约及翻译。 |
| 两方未完成项 | 仍按 §17.6–17.7 继续 C2 及后续阶段。本次收回评审不等于完成孵化准入、嵌套展开或真实场景验收，作者入口和脚本开关继续关闭。 |

luna 本轮对 F01 补丁再次复验：KnowLab 后端 `b0d379996c23053aa0b8b97281dedf5e17270137`、父仓 `8925db96fded76940de2465ade6c078a74dc4f7e` 上，`tests/test_knowbot_incubation_contract.py` **8 passed**；KnowBench 后端 `d3f7dbad9bbad7bcd576f6d1716b8dfb2117c4cc`、父仓 `c28aafcc225f430f0095b8ebc35dfe7c4f9d2a50` 上，`tests/test_knowbot_incubation_lock.py` **5 passed**。命令均在对应 `app` 目录执行 `.venv/bin/python -m pytest -q <文件>`。随后的清理补丁不改这些契约或锁；其固定版本与验证见[共同调用卡补丁记录](../2026-11-14-C2共同调用记录增量复审/request.md#清理补丁固定版本与复审范围)。不重复宣称原固定候选通过，不改变最终全量和真实协议发布条件。

### 结案（2026-11-14）

所有者本轮临时授权“这次你修复后不再复审”。Schema/消费锁补丁已核对并复验，固定流程守卫修复已有 qwen 独立验证；本次不再追加补丁复审，原回执保留，评审处理结案并归档。F02/F03 仍是第 12 项发布条件，F04/F05 由 luna 按第 3、6 项继续；所有其它开发范围与最终候选验证保持待完成，不将结案解释为 C2 全部通过或获准上线。
