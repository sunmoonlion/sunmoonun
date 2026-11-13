# 能力调用结果、连接变更与轮次授权修复复审

- 类型：评审。
- 状态：待接手，最终补充回归通过，提交已固定；本批未发布。
- 发起身份：luna。
- 执行身份：评审方 qwen，承接 `opus-qwen.md` 第十二节；由所有者协调复审，不自动启动其它代理。
- 主工位：远程 `/home/zym/worktrees/qwen`，应用与平台分支均为 `qwen`。
- 待评版本：以下四仓确切提交；KnowBench 后端基线为 `5644bfcabdb2f622a9abd4636905a9442f27290a`，本批差异以该基线至待评提交为准。
- 回执：`replies/qwen.md`；评审方自行填写，发起者不代写结论。

## 目标与范围

所有者已同意 Luna 修、评审方复审，先修评审 12.3 的第 1、11、14 条；同时明确“新开发，不要兼容”。本批修复不发布、不启用脚本，不把后续 C2–C6 算作完成。

| 仓 | 待评提交 | 变更 |
| --- | --- | --- |
| knowbench-backend | `3897e3d67b3019e58df262b0c0d273ca3c7f9a5f` | MCP 真实适配器的三类结果与落账；失效能力不阻断普通交流、方法仍严格检查；完成事件依据持久 turn，接管/重连撤销旧范围；空能力快路径；回归测试及协议夹具 |
| knowbench-web-frontend | `4c09a8d7b88b39809667390209ae0d34c33f5c71` | 本次能力面板区分聊天继续与方法等待的提示 |
| knowbench-app | `82dcc184c8eea588f4bbcd25017e31de41b6a682` | 子仓指针、按现有模型重新生成的动态目录 schema 与 KnowLab 消费锁 |
| knowlab-app | `9c134cfec41c88530d8087cfb1d9125578088379` | 作者定义 schema 与动态目录消费锁；本次不改其后端执行逻辑 |

## 请重点复审

1. 真 `RemoteMcp` 经假 HTTP 传输进入 `Capabilities.decide` 落库，而非假 remote 直接抛超时：握手失败/连接尚未建立、匹配结果、读超时/断流/写异常/HTTP 错误/坏回包/超限；重复批准不派发第二次。明确返回失败也不承诺副作用回滚。
2. 更新凭据、刷新目录、停用再启用使旧审批失效。聊天只排除问题能力，不擅自重新绑定账号；并发撤权在锁内复核。方法缺必需能力仍拒绝准备；不能静默绕过依赖。
3. 新建 `SandboxLink`、内存 scope 为空时，完成事件仍按持久 turn 关闭旧范围；接管和重连撤销旧范围，技能正文读取、新请求及旧批准被拒。迟到旧 turn 不关闭新范围。正常聊天已提交的精确审批在原审批时限内仍可由用户确认，接管/重连后的旧批准不允许，包括完成事件先到、随后发生重连的顺序。
4. 稳定配置不靠长效 token：本补丁仍逐轮换令牌，线程重载优化待公共调用身份机制实现；空能力路径不分配无用范围，不跳过已有范围清理或方法要求。
5. 评审 12.6 的契约生成遗漏和测试协议夹具已修。所有提供方生成物与消费锁一致；此变更不引入旧接口别名或双套运行路径。

## 数据与权限边界

线上只读审计结果见 `scripts/results/capabilities-usage-audit-20261113.json`：三张能力表为空；工作稿、专家草稿、市场版本、委托均无方法能力字段；但有 54 个 expert 类型会话。后续新结构直接替换未使用格式；已有数据一次性迁移并对账，不长期兼容，不删除用户会话。此补丁没有数据库迁移、线上写入或发布。

共同机制/C2、作者入口暂停、Skill 随方法交付、账号绑定复用、OAuth、稳定配置、脚本输入与连接器等均未在本补丁完成，继续按接入实施方案 §17.6，不提前宣布收敛完成。

## 允许的动作与验收

阅读指定提交、串行执行本机隔离测试、写本人回执。不要直接改候选代码、部署、发真实邮件或调用收费模型。发现问题交回 Luna 修复；测试只用 `_tests` 数据库中的独立 schema，私有测试配置位于 `~/.config/sunmoon-remote-test/pg.env`，不可输出值。不得停止其它人的测试进程。

本批验证（远程开发工位；测试数据库隔离 schema）：

- 后端全量首跑：**2094 passed、92 skipped、1 failed，17m47s**。唯一失败为 `test_skill_dependencies_db.py` 的旧断言（停用连接应阻断普通聊天），已改为验证排除失效能力、保留原账号选择、不替换为其它账号。该全量运行早于最后补充的“完成后再重连”分支，最终变更以补充回归为准，不记“全量全过”。日志 `/tmp/capability-review-full-pytest.log`。
- 补充回归：**172 passed、1 skipped，3m10s**；启用 `AGENT_TEST_DATABASE_URL` 和 `DELIVERY_TEST_DATABASE_URL`，覆盖上述失败、授权边界及此前跳过的投递测试。唯一跳过项需要独立 `CELERY_PROBE_TEST_BROKER_URL`，本机未配置；没有连接业务 broker。日志 `/tmp/capability-review-supplement.log`。
- 最终跨仓 schema/锁检查：KnowBench **81 passed**；KnowLab **60 passed**。日志 `/tmp/capability-review-final-schema.log`、`/tmp/capability-review-knowlab-contracts-final.log`。
- 前端组件/契约 **15 passed**；TypeScript、改动 ESLint、i18n 通过。后端 Ruff 通过、Pyright **0 errors / 0 warnings**。

评审通过后另按既有 Jenkins 原生流程发布，人工晋级不代批。qwen 分支还包含其它未发布工作，不能直接整支发布；须基于 #93 的隔离发布分支摘取本批提交并复验。
