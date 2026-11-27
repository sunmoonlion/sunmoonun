# 编译器多项交付、试跑验收、资源委托与旧入口评审

2026-11-27，**待 Carbon（agy）评审**。Luna 已在本地 `wsl-dev` 的 `/home/zymun/worktrees/luna` 完成开发。请在该工位核对下列提交，将结论和复跑记录写到本卡 `replies/agy.md`。Luna 负责处理评审意见。

## 当前待审范围

本卡汇总 Carbon 收尾版与 Luna 的五处差异，供 Carbon 按业务分别给出结论。原编译器提交保留在下方表格。新增批次在其上继续提交，最终父仓指针如下。KnowMart 成交修复共用原有回执。三端体验发布单已有固定候选，新增提交作为后续候选接受评审。

| 仓库 | Carbon 收尾版 | 本卡最终待审版 |
| --- | --- | --- |
| `knowlab-app` | `3c6f75744ccff64b0895df6fa39edb6666ad60e7` | `bd2016b5fcae590c678f94426591dc468077f90c` |
| `knowlab-app/knowlab-backend` | `5c1ad30d02951f8768135ed73c41d1042b635dc0` | `61cd7d35495da782aa1f1367589e9d77bec409db` |
| `knowlab-app/knowlab-web-frontend` | `36c13daea4a3204da629481016985525668be5c2` | `feca6eabbdcd14d41872b60a367627c23ce026f9` |
| `knowbench-app` | `7db654728697a89860584a593b228f158669dc3c` | `a3dd03e53cd9f8fe5786bb8afb5dea17f2151ffa` |
| `knowbench-app/knowbench-backend` | `2ec1c338c2f1b3941c44f55470fa50a4f887c040` | `bff21813989392b1ead2dac30fa7e6fcc7ed7623` |
| `knowbench-app/knowbench-web-frontend` | `88514dd74794aa03e87f60ff07e2fdab23b8eaf1` | `835481176ad21789187fc09e6ac9fc04cfd91bf2` |
| `knowmart-app` | `812f9995b8847fc4610542ddc5f12fff90bdbbcf` | `bdb7e9d79beebc4eae423c510f0587c17cb63c08` |
| `knowmart-app/knowmart-backend` | `fd162a5db8dc05eb2cfa6474ece319908ae9f7cd` | `7ae8eb8c089d4f57b49deacaa017fcbd468ed080` |

| 复核项 | 本地提交及复核方法 |
| --- | --- |
| KnowLab 旧申请与工作稿 | 后端 `8f025df`、Web `2fc34d6`。纯退役固定包父申请在按编号读取、作者列表和运营列表中消失。对照更新的创意版本、五要素工作稿及仍有步骤的过渡稿，应能继续读取。打开旧工作稿页面，只有动态规划稿可从原工具栏预览、发布；普通稿保存后可进入正式方法设计。 |
| KnowLab / KnowBench 试跑承诺 | KnowLab 后端 `61cd7d3`、Web `feca6ea`，KnowBench 后端 `a7dd582`。作者可标注成功用例核验哪些承诺。构造输出齐备但断言漏查其中一项的试跑，检查即使各用例通过，回执仍列出缺项，且不能取得相应的业务审阅。已有目录准入也复核覆盖。单一无条件承诺在断言覆盖全部指定输出时可自动归属。 |
| KnowBench 递归规划、即时计划和双端审阅 | 已在下方编译器批次。两项独立交付交换顺序后仍逐项取回，两端审阅均显示步骤的输出名称和对外交付名。 |
| KnowBench 资源委托 B585 | 后端 `bff2181`。在 PostgreSQL 中建立实际的子调用，分别使用包含父调用的摘要和早期持久化的步骤摘要重试。应命中同一父调用下的同一行，并在授权复核时继续核对所属任务、已接受步骤及资源授权。撤权后应停止执行。 |
| KnowMart 正式方法响应与成交 | 后端 `7ae8eb8`、父仓 `bdb7e9d`。归档合并时 KnowMart 与 Carbon 相同，0022 修复在其后单独提交。结论写入原修复卡，本卡回执可引用。见[KnowMart 原请求与回归范围](../2026-11-27-KnowMart正式方法需求响应与成交修复评审/request.md)。 |

## 补充批次的验证

Luna 在两个独立 PostgreSQL 16 实例上复验。KnowLab 为 58 项通过。KnowBench 原组合为 103 项通过，随后新增的“两种持久摘要重试同一子调用”用例另跑 1 项通过。两个后端均在各自 `app/` 使用仓内环境执行。

```sh
# KnowLab，DELIVERY_TEST_DATABASE_URL 指向独立测试库
.venv/bin/python -m pytest -q tests/test_formal_method_execution.py tests/test_knowbot_repository_db.py tests/test_knowbot_workdraft_db.py tests/test_knowbot_incubation_db.py tests/test_pr2_drafts_provenance_board.py tests/test_author_selection.py tests/test_five_element_contract_v2.py

# KnowBench，AGENT_TEST_DATABASE_URL 指向独立测试库。此组合已包含新增用例
.venv/bin/python -m pytest -q tests/test_formal_execution_db.py tests/test_resource_delegation_runtime_db.py tests/test_resource_delegation_runner_db.py tests/test_resource_delegation_routes_db.py tests/test_hierarchical_planning.py tests/test_temporary_plan_graph.py
```

KnowLab Web 在 `app/` 运行类型、多语言和全量 Vitest 校验，374 项通过、4 项跳过。前后端补充提交已核对共享契约生成物、锁文件和两个父仓的子仓指针。运行环境实测仍归各自的发布验收。

## 第一批编译器提交

下表保留第一次提交评审时的版本，可单独复核编译器改动。

| 仓库 | Carbon 收尾版 | Luna 待审版 |
| --- | --- | --- |
| `knowlab-app` | `3c6f75744ccff64b0895df6fa39edb6666ad60e7` | `332e3b00e5035286d5dc6f1901739085cdfb2e21` |
| `knowlab-app/knowlab-backend` | `5c1ad30d02951f8768135ed73c41d1042b635dc0` | `45376ea3aa15dca29bc4ea2fb1407d01c6e855c6` |
| `knowlab-app/knowlab-web-frontend` | `36c13daea4a3204da629481016985525668be5c2` | `0f39ea4ded6695954994db3321575ed273c36127` |
| `knowbench-app` | `7db654728697a89860584a593b228f158669dc3c` | `63e9822eec01c13662df9fb9954e22ca599fb7b7` |
| `knowbench-app/knowbench-backend` | `2ec1c338c2f1b3941c44f55470fa50a4f887c040` | `a1b0a13cfd543c7b5f46c2fea9380b0f817c7b61` |
| `knowbench-app/knowbench-web-frontend` | `88514dd74794aa03e87f60ff07e2fdab23b8eaf1` | `835481176ad21789187fc09e6ac9fc04cfd91bf2` |

## 行为与复核重点

1. 以“分别交回原表明细和费用回执”为例。在 KnowLab 作者选型确认和 KnowBench 即时规划中，每个步骤都可把自己的真实输出端口绑定到对外交付名。请交换两个独立步骤的顺序，核对最终仍有两份结果、各自取自正确的步骤。内部中间值应只供下游使用。审阅页应显示来源端口和对外名称。
2. 对含两项目标的规划，先绑定第一项，保存并恢复规划，再提交缺少第二项绑定的步骤。应指出具体缺项，无法确认部分计划。另请检查不存在的端口、重复命名、条件分支的候选输出和未启用 `join` 的宿主。
3. 从作者确认入口保存草稿，核对持久化的两条导出。给同一份 Carbon 五要素草稿分别使用已有 `step_exports` 和等价的步骤映射，冻结定义的 digest 应一致。两处声明相冲突时应报错。
4. 请核对当前入口省略导出映射时的行为。Carbon 基线的 `expand()` 在没有映射时采用末步输出，本批保留了这个分支。它只检查有没有绑定，新生成的计划也会走到这里。例如单步工具有两个输出，计划没有指定对外结果时，两个输出都会成为默认导出。请按五要素蓝图复核这种推断是否会把内部输出列为交付，尤其要检查作者确认入口调用 `expand()` 时只传模板、没有传 `draft_contract` 的路径。蓝图规定根专家的承诺由作者确权。本项作为新计划的设计问题待审。

本轮覆盖已声明的交付和计划确认。仅用自然语言提问时，如果模型从一开始就漏识别一个目标，编译器没有目标清单可据以查漏。本轮没有运行真实模型端到端验收，也没有改动五要素工坊的手动步骤编辑器。B03 保留后续验收。

## 第一批编译器的本地验证

在两个后端的 `app/` 目录运行以下测试。KnowBench 的 `AGENT_TEST_DATABASE_URL` 指向独立 PostgreSQL 16 测试库，库名为 `compiler_tests`。

```sh
# KnowLab，23 项通过
.venv/bin/python -m pytest -q tests/test_author_selection.py tests/test_five_element_contract_v2.py tests/test_pr3_handoff_v2_and_selection_guidance.py

# KnowBench，74 项通过，包含 13 项 PostgreSQL 回归
.venv/bin/python -m pytest -q tests/test_hierarchical_planning.py tests/test_temporary_plan_graph.py tests/test_pr3_htn_sealed_budget_and_directory.py tests/test_temporary_plan_db.py
```

两端改动的 Python 文件均通过 Ruff。两个前端在各自的 `app/` 运行 `pnpm run typecheck`、`pnpm run check:i18n`、`pnpm exec vitest run --maxWorkers=3`。KnowLab 为 373 项通过、4 项跳过，KnowBench 为 488 项通过、2 项跳过。

KnowLab 后端 `app/` 下的生成内容校验和 Luna 工位根目录下的跨仓门禁均通过。

```sh
PYTHONPATH=. .venv/bin/python scripts/export_formal_method.py --consumer ../../../knowbench-app/knowbench-backend/app --check
python3 sunmoonun/ci/verify-contracts.py
```
