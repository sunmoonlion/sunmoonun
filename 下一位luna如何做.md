# 下一位 Luna 如何做

交班日期为 2026-11-22，工位在 `/home/zymun/worktrees/luna`，分支为 `luna`。**接着做待办第 12 项的普通 P3 专家委托。第一条要跑通的路径是：用户请一个已冻结的专家，专家交出产物，图内另一位助手只收到获准的产物版本，复核费用记在这次委托的根预算。**

先看 [CHECKPOINT.md](CHECKPOINT.md) 顶部三条，依次是委托人裁定、严格双轮和单轮复核。再到[统一待办](docs/总纲/luna-待办.md)搜索“按交接边派发独立助手”。前者给出上位 Luna 实际跑过什么，后者决定接下来的顺序。若你接手时已有更新，以较新的交接和已提交代码为准。

## 先认清两条入口

| 从哪里发起 | 到交班时做到哪里 |
| --- | --- |
| KnowLab 作者取回一次试跑的产物，再到 KnowBench 指定助手复核 | 已跑通。已结束的试跑有自己的账。作者重新确认发送范围和费用后，KnowBench 建立独立的复核委托，支持单轮及严格双轮。本人可从项目历史逐条引用原文，记录采纳、不采纳或待定及理由。第二轮失败或取消仍能查看首轮，页面列明缺项。 |
| KnowBench 用户请一个普通专家，专家的冻结图中本来就有 P3 复核边 | 正在接。作者能在草图保存复核安排，普通专家的固定图也已能递归执行基础步骤，但图内 P3 仍会报告运行能力缺口。这次要把产出、交接、复核、计费和恢复串在同一根委托内。 |

最容易做错的是把“采纳这条复核意见”接成“重新执行产生报告的步骤”。裁定回执只表示委托人如何处理意见。原步骤可能发邮件、写文件或计费。返工需要可重做的原步骤、获准的动作范围、根预算和新的产物修订；已有成果的独立复核委托只获得了审阅授权。[现有执行与裁定说明](../knowbench-app/knowbench-backend/docs/method-execution.md)

## 第一轮开发怎样验

1. **先接普通固定图的单轮。** 建议先用无外部副作用的通用样例，从“请专家”的预览和确认进入真实 runner。追清根委托、产出步骤、复核步骤、输入槽与精确产物版本。V0 是程序对这项产物的必过检查。用一过一拒两例证明：通过才给复核者开独立执行单元，失败时复核派发数和模型费用均为零。已有成果的独立复核可以借用执行逻辑，图内路径须保留原根调用身份、逐层收窄的权限和预算。
2. **再验隔离与交接。** 默认单轮。严格双轮先独立审，封存首轮发现、产物版本及用量后，第二轮才看到指定自评。抓取合成供应商实际收到的字段，核对网关、工作容器和线程；在两轮之间加入同名新版产物、撤销连接、模拟重启。恢复应回到原线程和原账。只有一个供应商或一个模型时，按“允许同模型的隔离复核”完成；明确要求不同模型家族的委托须查到实际执行身份才能放行。备用连接装载、跨家族取证、外部 A2A 派单都还在待办。
3. **最后接有界返工。** 首次交付不占返工次数。同一打回决定并发提交、重试或重启只计一次。按计划上限、平台最多两次和剩余预算取更严条件。返工产出新版本，保留旧版及费用，重新跑受影响的 V0；预算不足或第二次仍有分歧，停给委托人裁定。用数据库中的调用、产物、审批和扣费记录验收。先跑通这一条，再按待办推进 P5、P4、P2。

| 要追的代码 | 从这里进 |
| --- | --- |
| 普通委托如何确认、固定图怎样找到父子调用和叶子 | [普通委托入口](../knowbench-app/knowbench-backend/app/app/application/workbench/ordinary_expert_execution.py) · [递归执行](../knowbench-app/knowbench-backend/app/app/application/workbench/formal_recursive_runtime.py) · [普通委托数据库用例](../knowbench-app/knowbench-backend/app/tests/test_ordinary_expert_execution_db.py) |
| 现有成果如何确认目的地、建立独立复核委托；哪些逻辑可复用 | [路由与交接范围](../knowbench-app/knowbench-backend/app/app/application/workbench/branch_review_route.py) · [派发与根预算](../knowbench-app/knowbench-backend/app/app/application/workbench/branch_review_dispatch.py) |
| 首轮何时封存、何时开放自评、运行中断后如何恢复 | [双轮交接](../knowbench-app/knowbench-backend/app/app/application/workbench/review_comparison.py) · [隔离执行器](../knowbench-app/knowbench-backend/app/app/application/workbench/instruction_runner.py) · [模型请求核权](../knowbench-app/knowbench-backend/app/app/application/workbench/instruction_requests.py) |
| 人的回执怎样绑定封存原文、追加修订 | [裁定服务](../knowbench-app/knowbench-backend/app/app/application/workbench/review_decisions.py) · [裁定与取消回归](../knowbench-app/knowbench-backend/app/tests/test_review_decisions_db.py) |

## 几个已经定下来的设计决定

- 正式方法只有工具方法和专家方法。专家角色与分工由图赋予，专家可以递归调用冻结的方法版本。P1–P5 是编排期的草图构造模式，各自依赖宿主真正支持的原语。独立线程与工作目录、分阶段交接、逐叶审批及计费均须由程序落实。财务案例用来测通用机制，业务字段和判据归相应方法。[专家方法主稿](docs/总纲/专家方案设计/专家孵化方案/luna/专家方法孵化与递归编排方案.md) · [编排过滤模式](docs/总纲/专家方案设计/专家孵化方案/luna/编排过滤模式.md)
- KnowBench 方法技能管理中心的登记表是三个可选目录的登记真源。KnowLab 管方法定义、试跑和冻结，KnowMart 管上架、获取及使用资格。每次选择还要结合本人权限和当前用途。孵化按广泛可复用的**能力声明**筛选，即时编排按**当次具体问题和获准资料**筛选，运行中的步骤再受确认清单约束。同一 MCP 或 Skill 的原生安装入口与派生方法版本各有身份；聊天、工作按 Codex 原生方式使用，正式专家由 KnowBench runtime 按清单调度。[方法技能管理中心](docs/总纲/方法技能管理中心.md)
- 总体验收有“两大统一”。一是同一专家版本可做一次委托，也可承担长期职责，按图分工和隔离。二是从 KnowBench 发现能力缺口，经 KnowLab 孵化、KnowMart 获取后回到使用，再按同一路径回炉。第 14 项才做完整验收。新实现按已定架构推进；用户已明确，遇到冲突的旧入口直接改正。[统一待办](docs/总纲/luna-待办.md)

## 本地复跑与交回

从 `knowbench-app/knowbench-backend/app` 运行。数据库用独立临时 PostgreSQL，给 `AGENT_TEST_DATABASE_URL` 设置测试连接，库名以 `_tests` 结尾。未设置时数据库用例会跳过。下面两条分别验证现有行为和真实 Codex 隔离执行，后者仍使用合成供应商。镜像标签因机器而异，先核对本机镜像的 `codex --version` 为 `0.170.0`，再设置 `CODEX_INSTRUCTION_TEST_IMAGE`。[容器测试入口](../knowbench-app/knowbench-backend/app/tests/test_instruction_runner_codex.py)

```sh
.venv/bin/pytest -q tests/test_ordinary_expert_execution_db.py tests/test_review_decisions_db.py tests/test_instruction_runner_db.py
RUN_CODEX_INSTRUCTION_PROBE=1 .venv/bin/pytest -q tests/test_instruction_runner_codex.py -k strict-review
```

**同步和发布分别交接。** 上次开发的 KnowBench 父仓为 `14b5875`，后端 `3c06103`，Web `1098fd5`，本地与 Gitee 已核对。上次 GitHub 在核对远端时超时，文档仓则已同步两端。换账号后先核对这三个提交及父仓的子模块指针；若仍待同步，从工位根运行 `./sunmoonun/docs/sync-cowork/sync/sync.sh push knowbench-app`。第 12 项的开发可从本地这组提交继续。

#103、#104 已有发布回执。本轮 KnowBench 迁移 `20261122_0058` 只验过本地升级、降级、再升级。待发布内容累计在同一张 Cursor 单，交班时状态为“待接手”。**发版由 Cursor 做**，Luna 更新候选提交、迁移头、验证与回退说明。每完成一个可验证步骤，更新统一待办及 CHECKPOINT 顶部，写清提交、实际验证、待验条件及下一步。向 agy 提复核也按发起人 Luna 建请求，回执回来由 Luna 核对、吸收及结单。真实模型费用核对、集群开关及现场行为验收沿用已有授权范围，分别记结果。[合并发版单](docs/sync-cowork/requests/luna/2026-11-22-作者草图和普通专家委托合并发版/request.md) · [工位约定](AGENTS.md) · [协作请求说明](docs/sync-cowork/协作请求使用说明.md)
