# 编译器多项交付与双入口规划评审

2026-11-27，**待 Carbon（agy）评审**。Luna 已在本地 `wsl-dev` 的 `/home/zymun/worktrees/luna` 完成开发。请在该工位核对下列提交，将结论和复跑记录写到本卡 `replies/agy.md`。Luna 负责处理评审意见。

## 待审提交

每个仓的 Luna 提交都直接接在对应的 Carbon 收尾提交之后。两个父仓已经指向表内的前后端版本。

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
3. 从作者确认入口保存草稿，核对持久化的两条导出。给同一份 Carbon 五要素草稿分别使用已有 `step_exports` 和等价的步骤映射，冻结定义的 digest 应一致。两处声明相冲突时应报错。历史草图省略新字段时继续使用末步默认导出。

本轮覆盖已声明的交付和计划确认。仅用自然语言提问时，如果模型从一开始就漏识别一个目标，编译器没有目标清单可据以查漏。本轮没有运行真实模型端到端验收，也没有改动五要素工坊的手动步骤编辑器。B03 保留后续验收。

## Luna 的本地验证

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
