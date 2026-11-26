# 2026-11-26 专家孵化与编排复审证据

KnowLab 后端 8ddff90、KnowBench 后端 984fd50（两者均含 Luna 已有的多步模板工作区改动），KnowMart 后端 fbf1e4d、KnowBase 后端 a30b375。KnowLab、KnowBench、KnowMart Web 分别为 b681780、6c96e43、b55591d，KnowMart 管理端为 5f10911。对照结论及优先顺序见[方案第九节](../../../专家方法孵化和编排重构-luna.md#九按用户实际路径重新审查)。

## 七个边界样例

这些断言记录此基线的行为。修复后，应按方案的业务验收条件更新断言。数据库为本机临时 PostgreSQL 16，各应用使用单独的测试库。模型、跨应用传输和脚本供应商按相应夹具替代。

| 样例 | 本次观测 | 离开夹具之后仍需验证 |
| --- | --- | --- |
| [KnowBench 三例](probe_bench.py) | 空目录后同题补工具，原请求重放仍空，换说明为 409；模拟收到无法核实的孵化回执，原题改交接内容和结束均为 409；有效的大声明排第一时，查目录报错，未读取第二个候选 | 真实目录规模、现场故障频率及跨服务对账 |
| [KnowBase 两例](probe_base.py) | 同一读取路径、同样取得父授权与逐次同意，16,000 字节文本读回，16,001 字节得到 method_read_format | 有附件的完整页面委托及其费用 |
| [KnowLab 一例](probe_lab.py) | 两个无条件承诺，只断言第一个输出，试跑请求校验接受；加上条件后，同一套无覆盖标注的输入被拒 | 独立业务复核、正式发布资格 |
| [KnowMart 一例](probe_mart.py) | 条目审核通过后，第三方搜索结果为 1；证照过期并运行 sweep 后为 0，条目仍是 listed；批准新证照后搜索结果恢复为 1，未再次审核条目 | 运营对续证是否应触发重新审条目的决定及真实浏览器呈现 |

可在相应后端的 app 目录，用仓内 .venv 和该仓既有测试夹具重跑。例如以下为 KnowBench。AGENT_TEST_DATABASE_URL 需预先指向一次性 PostgreSQL 数据库，库名以 _tests 结尾。另三仓使用 DELIVERY_TEST_DATABASE_URL，文件名分别为 probe_lab.py、probe_base.py 和 probe_mart.py。命令中的相对路径从每个后端的 app 目录起算。

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:tests .venv/bin/python -m pytest -q -c pyproject.toml \
  ../../../sunmoonun/scripts/results/2026-11-26-Luna全局复审/probe_bench.py
```

## 原仓回归范围

后端均使用 pytest。下表省略 tests/test_ 和 .py。Web 与管理页用仓内 Vitest 跑 component 测试，省略 .test.tsx。

| 仓 | 测试组 | 结果 |
| --- | --- | --- |
| KnowLab 后端 | author_selection、formal_method、formal_method_execution、formal_method_recursive_plan、formal_methods_db、formal_method_service、runtime_method_demand_db、formal_expert_visibility | 86 通过 |
| KnowLab 后端 | knowbot_incubation_db、knowbot_incubation_rounds、knowbot_incubation_routes、method_delivery_preflight_db、method_delivery_preflight、author_method_routes | 25 通过，1 失败。test_incubations_migrate_round_trip_and_run_for_real 仍要求固定 v2 出版成功，服务返回 workdraft_invalid；此断言之后的约束及回退段本次未执行 |
| KnowBench 后端 | hierarchical_planning、temporary_plan_graph、temporary_plan_db、formal_expert_intake_db、formal_expert_preparation_db、formal_orchestration_runtime_db、formal_artifact_authority_db、knowbase_method_read_db、pending_method_usage_db、expert_lookup_guard_db | 95 通过 |
| KnowBench 后端 | formal_script_execution_db、formal_instruction_trial_db、formal_recursive_runtime_db、formal_evidence_db、formal_session_model_concurrency_db、planning_window_recall_db | 50 通过，3 跳过。三例依赖独立容器供应器，覆盖真实容器三步专家及启动后取消、失败的结算 |
| KnowBase 后端 | registered_data_functions、table_format、user_library_db、user_library_http | 63 通过 |
| KnowMart 后端 | market_db、market_routes | 37 通过 |
| KnowLab Web | formal-method-editor、formal-method-execution、author-method-freeze、method-directory、workdraft | 127 通过，含模拟成功的旧出版本按钮 |
| KnowBench Web | expert-desk、expert-run-screen、retired-expert-pages、formal-method-panel | 31 通过 |
| KnowMart Web 与管理页 | market、expert-catalog、market-admin | 38 + 4 通过 |

原仓选定回归共 556 通过、1 失败、3 跳过。上表与七个边界样例独立计数。工作树 verify-contracts.py 通过，--pinned 失败，锁定的 KnowBench 后端 c7d3d14 缺少 app/contracts/formal-method-lock.json。本轮没有进行真实 Kimi 调用、共享环境登录、生产交易或发布。
