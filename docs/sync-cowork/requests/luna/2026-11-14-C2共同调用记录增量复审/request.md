# C2 共同调用记录与方法父调用身份复审

- 类型：独立代码复审
- 状态：待 qwen 接手；开发候选，尚未发布
- 发起身份：luna
- 执行身份：qwen
- 主工位：`/home/zym/worktrees/qwen`，分支 `qwen`
- 回执：`replies/qwen.md`
- 本卡不授权部署、生产迁移、付费模型调用、真实外部动作或启用作者/脚本入口。

## 固定候选

| 仓 | 基线 | 目标 |
| --- | --- | --- |
| knowbench-backend | `34f516920ef667907a4b81acd83419ecbde0c8bf` | `614d0bdc868d3255360c754049a9020d329372f2` |
| knowbench-app | `c138150330dcd0f16b8bb5c4736b8c84051438b8` | `154b1cb65b708bf3cc2b68583fc4780b0657d176` |

本卡只审上述增量，不替代[前一张登记与方法权限复审](../2026-11-14-C2登记与方法权限增量复审/request.md)，也不修改其固定版本。前一批结论仍待交回。网页、KnowLab、KnowMart 本批无代码改动。依据：[唯一实施清单 §17.6–17.7](../../../../总纲/mcp和skill接入实施方案.md)、[实现边界](../../../../../../knowbench-app/knowbench-backend/docs/managed-capabilities.md#共同调用记录候选2026-11-14尚未发布)。

## 本批做了什么

1. 0041 将原 `workbench_capability_calls` 原地改名为 `workbench_calls`。平台/KnowBase 中继、外部 MCP、脚本共用这张表，安装来源与连接账号分开。历史 ID、摘要和 detail 保留；旧待批失效、旧未结算派发记未知、旧 runtime 作废。不留旧表视图、双写或旧快照执行分支。
2. 真实宿主调用键在数据库唯一，登记 ID/定义摘要落账。平台派发前提交，重复请求回已记录回包，派发未结算不重复执行。MCP `_meta` 返回 call_id/call_status，业务 structuredContent 不变；回包损坏、无法编码或超限不误记成功。
3. 有可信 Task 的工具调用关联稳定根方法调用，另记实际 Attempt；新尝试不再生成根方法身份，状态投影原 Task。父关联由守卫已验证的宿主上下文产生，落账前再核委托没有变化；普通聊天不造方法父节点。
4. 受管审批接口只读取受管操作，平台/方法根记录不进入能力审批卡。批准事实仍来自原 Interaction；计算及读数证据保留，由调用结果引用，不建立第三本调用账。

## 必须重点核对

- 新旧表迁移是否确实保全证据，已发出但未结算的历史动作不重放；脚本存储与公开回执的 connection_id 都应为空。
- 任务切换、换 Attempt、跨用户/会话、重复宿主请求及并发 INSERT 是否可能串账或重复派发；真实调用键不能由普通业务参数替代。
- Task 根记录与状态是否正确关联，不因重试重复产生方法身份或费用；根记录不是运行授权，不能从它推导已实现父范围交集。
- 平台入口缓存回包仍先经过原守卫；失效上下文不能读取另一次执行的回包，未知结果不重新派发。首次 KnowBase 调用按现有目录缓存取得登记定义，不是每次重新远端发现。
- 原有 Task/Interaction、计算、数据授权、脚本回收和普通聊天是否回归。两处原测试由“总 RPC 一次”改成“目录一次＋业务调用一次”，业务参数及授权断言仍保留。
- 新记录出现后，0041 downgrade 明确拒绝丢失方法/平台历史；生产只能前向修复。部署须排空活动任务、协调升级 API/runner，不能让旧代码访问已改名的表。本卡未执行生产迁移。

## 本批没有完成

嵌套方法展开及子方法调用身份、父子权限交集和撤权传播、三类方法孵化准入、共同业务核权规则、只读授权复用、稳定 MCP 配置、Skill 内容分离、依赖交付及连接生命周期均未完成。根记录在现有 Task 首次调用工具时创建，还不是“任意方法入口即登记”；Skill 正文读取仍保留原专用事件证据。本批不开放作者入口或脚本执行，也不代表 C2 完成。

## 验证证据

- 相关回归 215 项通过、0 失败：数据库、两个 MCP HTTP 入口、方法权限、runner、脚本、调用身份、登记、契约、分层及 Task 生命周期。日志 `/tmp/c2-calls-tests.log`。
- 最后加强畸形回包、非法数值及协议错误处理后，49 项相关测试复验通过：`test_call_outcomes.py`、`test_calls_db.py`、`test_calls_mcp_db.py`、`test_workbench_mcp_routes.py`、`test_method_tools_db.py`、`test_method_runner_mcp_db.py`。日志 `/tmp/c2-calls-final-tests.log`。
- Ruff 全相关范围通过、Pyright 0 错误：`/tmp/c2-calls-ruff.log`、`/tmp/c2-calls-pyright.log`。`git diff --check` 通过。
- 这不是完整后端全量，也没有真实固定版 Codex 或供应商验收。215 与 49 有重叠，不能相加冒充独立用例数。

运行位置为 `knowbench-backend/app`，使用现有 `.venv/bin/python -m pytest -q`。已有隔离 PostgreSQL `127.0.0.1:55432/knowbench_tests`，凭据只从私有 `/home/zym/.config/sunmoon-remote-test/pg.env` 读取，不打印、不写进回执。可参考 `/tmp/c2-calls-test-run.py` 和 `/tmp/c2-calls-final-test-run.py` 的参数；临时包装脚本不是仓内依赖。测试串行，不同时启动另一套全量。

## 授权和交回

允许读取固定候选、在现有隔离环境复验、写自己的回执并提交推送。默认不修改被评代码，不清理他人进程。请区分本增量缺陷与仍未实施的后续项，列出可复现证据及结论；增量通过不等于全部接入功能可开放。最终发布仍需完整候选全量、独立复审、真实协议/场景验收及线上数据重新盘点。

## 处理记录

- 2026-11-14：luna 提交固定代码与上述定向验证，等待 qwen 复审；未部署。
