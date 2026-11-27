# agy 回执

- 对应请求：../request.md
- 本轮：第1轮
- 实际检查版本：
  - `knowlab-app`：`bd2016b5fcae590c678f94426591dc468077f90c`（基线 `3c6f75744ccff64b0895df6fa39edb6666ad60e7`）
  - `knowlab-app/knowlab-backend`：`61cd7d35495da782aa1f1367589e9d77bec409db`（基线 `5c1ad30d02951f8768135ed73c41d1042b635dc0`，含 `45376ea`、`8f025df`、`61cd7d3`）
  - `knowlab-app/knowlab-web-frontend`：`feca6eabbdcd14d41872b60a367627c23ce026f9`（基线 `36c13daea4a3204da629481016985525668be5c2`，含 `0f39ea4`、`2fc34d6`、`feca6ea`）
  - `knowbench-app`：`a3dd03e53cd9f8fe5786bb8afb5dea17f2151ffa`（基线 `7db654728697a89860584a593b228f158669dc3c`）
  - `knowbench-app/knowbench-backend`：`bff21813989392b1ead2dac30fa7e6fcc7ed7623`（基线 `2ec1c338c2f1b3941c44f55470fa50a4f887c040`，含 `a1b0a13`、`a7dd582`、`bff2181`）
  - `knowbench-app/knowbench-web-frontend`：`835481176ad21789187fc09e6ac9fc04cfd91bf2`（基线 `88514dd74794aa03e87f60ff07e2fdab23b8eaf1`）
  - `knowmart-app`：`bdb7e9d79beebc4eae423c510f0587c17cb63c08` / `knowmart-backend`：`7ae8eb8c089d4f57b49deacaa017fcbd468ed080`（详见同批成交修复卡回执）
- 结论：通过（本批已声明多项交付、试跑承诺覆盖、旧申请过滤与 `B585` 资源委托复核均通过独立真库与前端回归；针对请求中列出的第 4 项“省略导出映射时的默认行为”给出明确架构裁定，作为新计划后续增量修订项跟进，不阻塞本批合入）

## 发现

- F01（无阻塞问题，KnowLab 旧申请与工作稿可见性过滤核查通过）：核查 `SqlKnowlabRepository._visible_requests`（`8f025df`）与 `KnowbotBoard`，仅在最新创意版本只有已退役固定包草稿且无后续作者工作时隐藏父申请，同时完整保留更新创意版本、`draft_contract` 五要素草稿及含 `formal_method / method_template / planning / steps / method_refs` 或更新时间晚于旧草稿的过渡工作稿；Web `workdraft-view.tsx`（`2fc34d6`）以 `dynamicDraft = !!doc.body.planning && !doc.body.method_template` 约束工具栏旧预览与发布按钮，普通稿保存后进入正式方法设计。
- F02（无阻塞问题，试跑承诺逐项覆盖与目录准入复核核查通过）：核查 `FormalMethodExecutionRequest.uncovered_promises`（`61cd7d3`）、KnowLab Web `formal-method-execution.tsx`（`feca6ea`）及 KnowBench `formal_test_runs.py` / `formal_method_catalog.py`（`a7dd582`），正例可通过 `covers_promises` 显式标注所核验承诺，仅单一无条件承诺在断言覆盖全部指定输出时自动归属；输出齐备但断言漏查某项承诺时，回执 `uncovered` 明确列出缺项且不签发 `business` 审阅，目录准入复核同步拦截缺项版本。
- F03（无阻塞问题，多项独立交付规划、编译器导出与双端审阅核查通过）：核查 `selection.py`、`incubation_selection.py`、`hierarchical_planning.py`、`temporary_plan.py`、`planning_capabilities.py` 及双端审阅组件（`selection-panel.tsx`、`temporary-plan-review.tsx`）：
  1. 新增根级 `SeparateDeliveries`、`PlanningNode.delivery_goals` 与步骤级 `deliver_as`，独立步骤交换顺序后仍按各自绑定的输出端口与对外名称导出，未绑定的中间输出仅供下游步骤使用；
  2. 多目标规划在恢复后若缺少任一目标绑定由 `check_delivery_targets` 报具体缺项，不存在端口、重复对外名称、条件分支候选端口缺失及宿主未启用 `join` 均被拒绝；
  3. 同一份五要素草稿使用 `step_exports` 与等价 `deliver_as` 生成一致的冻结 `digest`，二者冲突时抛 `selection_export: conflicting delivery bindings`；两端审阅界面均展示来源端口与对外交付名。
- F04（无阻塞问题，KnowBench 资源委托 `B585` 复核核查通过）：核查 `method_calls.py` 与 `method_authorizations.py`（`bff2181`），提取 `step_identity` 与 `matches_step_digest`，在父调用绑定的 `method:{invocation_digest}` 键下同时兼容带父调用的新摘要与早期持久化的步骤摘要幂等重试，命中同一父调用下的同一子调用行，并在权限复核阶段持续核对所属任务、已接受步骤字段及资源授权有效期与撤权状态。
- F05（设计问题裁定，针对“行为与复核重点第 4 项：省略导出映射时的末步全量回退与未传 `draft_contract` 路径”）：
  - **问题确认**：按五要素蓝图“整体统摄局部（M02：根专家对外承诺与交付须由作者根契约确权，禁止把内部辅助端口静默升格为对外交付，禁止克隆末步子工具声明）”复核，当前兼容回退在新生成计划上存在两处确切泄漏路径：
    1. **作者确认入口未向 `expand()` 传递 `draft_contract`**：`SelectionService.materialize()`（`knowlab-backend` `app/app/application/services/incubation_selection.py`）虽读取了 `current.draft_contract` 生成 `target_deliverables`，但调用 `expand()` 时只传了 `template` 与 `scope`、未传 `draft_contract`。当工作稿已有 `MethodDraftV2` 时，确认选型会把作者已确权的 `promises / excludes / access_ceiling / approval_rules / validation_rules` 降级改写为 `template_delivery`；且当模型省略 `deliver_as` 时，若末步工具含多个输出端口（如 `{report, raw_debug}`，其中仅 `report` 为作者声明的交付），`check_delivery_targets` 因 `report in bound` 放行，`expand()` 随后将未确权的 `raw_debug` 一并暴露进根 `procedure.exports`。
    2. **单步新计划落入 `final.document()` 分支克隆子工具承诺并全量导出**：当 `draft_contract is None` 且无显式 `deliver_as` 时，`expand()` 落入 `else` 分支复制末步 `tools[tail].definition.document()`，且仅在 `selection.tree and len(selection.steps) > 1` 时清空子工具 `promises`。因此单步新计划（`selection.tree is not None` 且 `len(steps) == 1`）不仅默认导出单步工具的全部输出端口，还会把子工具自身的 `promises / applies_when / excludes / how_to_validate` 原样带入根定义（KnowBench 即时计划单步 `direct` 工具省略 `deliver_as` 时亦有同类克隆）。
  - **后续修订建议（请 Luna 另立增量提交收口）**：
    1. 在 `SelectionService.materialize()` 中，若 `current.draft_contract` 存在，解析 `MethodDraftV2` 并传入 `expand(..., draft_contract=v2)`；有 `draft_contract` 时根导出集合须严格受根契约声明的输出名约束，不得把末步多余端口并入 `procedure.exports`。
    2. 对新生成的计划（`selection.tree is not None`），若省略 `deliver_as` 且无 `step_exports`：当末步输出端口数 `> 1` 时应直接报 `selection_export` 拒绝隐式全量导出，要求显式指定对外交付；当末步仅有唯一输出端口（`len == 1`）时可保留单端口确定性绑定，但根契约构建统一走 `draft_contract` 或 `_compose_delivery`，不再走 `final.document()` 克隆子工具声明（`final.document()` 末步回退仅保留给 `selection.tree is None` 且无 `draft_contract` 的存量历史回放）。
- F06（范围外顺手提示）：`knowbench-backend` 全仓 Ruff 检查发现早先 `6993698` / `ea220b2` 提交在 `tests/test_connection_oauth_db.py` 留有一处 `I001` 导入排序提示；本卡改动的全部 Python 文件 Ruff 均通过，后续可顺手整理。

## 验证

- 验证环境：本地 `wsl-dev`，在 `/tmp` 建立各仓指定提交的临时脱离工作树，连接本机独立 PostgreSQL 16 容器临时测试库（`agy_card4_knowlab_tests`、`agy_card4_knowbench_tests`，验证后销毁）。
- 已执行并通过：
  1. 静态与跨仓契约门禁：`knowlab-backend`（`61cd7d35`）`.venv/bin/ruff check .` 通过；`knowbench-backend`（`bff21813`）本卡全部改动文件 `.venv/bin/ruff check` 通过；`export_formal_method.py --consumer <knowbench/app> --check` 与 `--web-consumer <knowlab-web/app> --check` 均通过；`python3 sunmoonun/ci/verify-contracts.py --repos /home/zymun/worktrees/luna` 通过。
  2. `knowlab-backend`（`61cd7d35495da782aa1f1367589e9d77bec409db`）独立 PostgreSQL 16：`pytest -q tests/test_formal_method_execution.py tests/test_knowbot_repository_db.py tests/test_knowbot_workdraft_db.py tests/test_knowbot_incubation_db.py tests/test_pr2_drafts_provenance_board.py tests/test_author_selection.py tests/test_five_element_contract_v2.py tests/test_pr3_handoff_v2_and_selection_guidance.py` **60 项全部通过（16.96s）**。
  3. `knowbench-backend`（`bff21813989392b1ead2dac30fa7e6fcc7ed7623`）独立 PostgreSQL 16：`pytest -q tests/test_formal_execution_db.py tests/test_resource_delegation_runtime_db.py tests/test_resource_delegation_runner_db.py tests/test_resource_delegation_routes_db.py tests/test_hierarchical_planning.py tests/test_temporary_plan_graph.py tests/test_pr3_htn_sealed_budget_and_directory.py tests/test_temporary_plan_db.py` **123 项全部通过（123.53s）**（含新增的两种持久摘要重试同一子调用回归）。
  4. `knowlab-web-frontend`（`feca6eabbdcd14d41872b60a367627c23ce026f9`）：`pnpm run typecheck` 通过，`pnpm run check:i18n` 通过（`1817` 键），全量 Vitest **43 个文件、374 项通过、4 项跳过**。
  5. `knowbench-web-frontend`（`835481176ad21789187fc09e6ac9fc04cfd91bf2`）：`pnpm run typecheck` 通过，`pnpm run check:i18n` 通过（`1792` 键），全量 Vitest **66 个文件、488 项通过、2 项跳过**。
  6. KnowMart `0022` 成交修复：见对应请求卡回执（72 项 PostgreSQL 16 测试及升降级验证全部通过）。
- 未运行与依赖条件：未运行真实付费模型端到端规划验收（`B03` 及发布后运行环境实测按请求归各自发布验收）。

## 交回

- 评审性质：只读代码评审与隔离环境真库复验，未修改任何被评代码，未切换主工位分支。
- 尚待处理项：本批提交可直接作为后续候选推进；请 Luna 按 `F05` 裁定在后续增量提交中收紧新计划省略 `deliver_as` 的行为并向作者确认 `expand()` 传入 `draft_contract`。
- 提交与同步状态：本回执已提交本地 `wsl-dev` 的 `luna` 分支、未推送（执行 `sync.sh push sunmoonun` 时因 `sunmoonun` 工作区另有他人未提交改动被脚本预检拦停，按协作规范未夹带他人改动；待主工位处理未提交项后推送，另一端尚未更新）。
