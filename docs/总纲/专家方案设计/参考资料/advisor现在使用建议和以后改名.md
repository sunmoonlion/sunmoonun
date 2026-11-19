# `advisor` 命名溯源、当前使用建议与后续改名规划

> 2026-11-19 主稿人整理。方法两类和任务运行时术语已定；第 4 节是改名实施建议，第 6 节是独立的常驻触发命名建议。旧代码标识用于定位实现。

> **结论先行**：在 `knowbench-app` 中，`advisor` 实质上是**任务运行时调度与工作流执行引擎（Task Runtime / Workflow Engine）**，而不是业务领域的「专家（`expert`）」，也不是拟人化的「顾问角色」。现阶段建议**文档先行正名、代码暂不动刀**；待后续运行器重构或旧路径退役时，再统一将代码与数据库中的 `advisor` 改名为 `runtime` / `engine`。

---

## 一、为什么说 `advisor` 实际是个「引擎」

从 `/home/zymun/worktrees/luna/knowbench-app` 现有源码核对，`advisor` 与领域知识、业务专家没有隶属关系，它承担的是纯宿主运行时职责：

1. **代码定位（表驱动执行器）**：
   - `knowbench-backend/app/app/application/workbench/advisor.py` 的模块注释明确写着：
     > *“表驱动的工作流解释器……不调模型；对用户自己的 Codex thread 逐步发 turn。一步的循环：开 Attempt（预留预算）→ 组 turn 输入 → turn/start → 等 turn/completed → 按预算账扣 token → 确定性验收 → 通过：落新版本 Artifact、游标 +1；不通过：按 on_reject 返工 / 回退 / 交人。”*
   - 在正式方法链路中，`Advisor.drive()` 本身也不做领域推理，而是直接把任务转发给 `FormalModelExecution.drive()` 或 `FormalExecution.drive()` 执行。
2. **与 `expert`（专家方法）的本质区别**：
   - **专家方法（目标类型 `expert`；旧编译器还输出 `expert_team`）**：由 KnowLab 孵化冻结、在 KnowMart 上架的**可复用方法资产定义**（包含步骤编排 `Orchestration`、输入输出槽、验收规则等静态契约，由编译器 `classify_dependencies` 判定 `Kind`）。
   - **`advisor`**：KnowBench 侧负责读取方法步骤、管理预算账本、调度 Codex 轮次、执行确定性验收与状态机流转的**运行宿主引擎**。它既能跑固定专家包，也能跑正式模型/编排方法。

---

## 二、为什么当年会起名 `advisor`（历史混淆源）

`advisor` 这一命名来自早期工作台的两次历史语境：

1. **“方向盘（`Wheel`）”早期拟人隐喻**：
   - 在拆出独立的方法孵化体系（KnowLab）前，工作台把会话控制权抽象为 `Wheel.user`（用户手动对话）与 `Wheel.advisor`（系统接管方向盘推进任务，见 `domain/workbench/states.py` 与 `docs/design/decisions.md` `D4`）。
   - 前端 `knowbench-web-frontend/app/features/shell/model/nav.ts` 与 `features/work/ui/work-screen.tsx` 甚至直接把 `wheel === 'advisor'` 映射成了 `'expert'` 模式，进一步加深了“advisor = expert”的误解。
2. **早期市场应用曾暂名 `advisor-app`**：
   - `docs/design/SDD/modules/0018-advisor-market.md` 最初起草市场骨架时曾使用 `advisor-app` 命名，2026-10-14 已在 `0025-know-names.md` 正式更名为 `knowmart-app`，但工作台后端的 `advisor.py` 与 `Wheel.advisor` 一直沿用至今。

---

## 三、现阶段使用建议（零重构风险约定）

### 1. 文档与讨论口径：立即与“专家”彻底脱钩

* **统一术语**：在总纲、[专家方法孵化与递归编排方案 §1.8.1](../专家孵化方案/luna/专家方法孵化与递归编排方案.md#181-先区分驱动接入与执行)（已使用「任务 runtime」）、架构评审与新 SDD 中，**禁止再用“顾问”或“advisor”指代业务专家、专家方法或成员角色**。
* **正确表达方式**：
  * 指代运行驱动层时，统一写为 **「任务 runtime」** 或 **「工作流执行引擎」**；
  * 仅在标注现有代码落点时补充说明：**“（当前代码实现位于 `advisor.py` / `FormalModelExecution` 等，状态机控制权标记为 `Wheel.advisor`）”**。

### 2. 代码与数据库：现阶段不建议单独为改名做全仓强改

经核对 `wsl-dev`（`/home/zymun/worktrees/luna/knowbench-app`），`"advisor"` 与 `Wheel.advisor` 目前已深度耦合在数据库约束、后端多模块鉴权、历史账本事件和前端状态判断中：

| 层次 | 已落盘耦合位置（部分核心点） |
| :--- | :--- |
| **数据库迁移与 SQL** | `alembic/versions/20260924_0008_workbench.py` 中的约束 `ck_workbench_sessions_wheel`（`wheel in ('user','advisor')`）；`infrastructure/workbench/repository.py` 中直接查询 `s.wheel = 'advisor'` |
| **状态机与错误定义** | `domain/workbench/states.py`（`Wheel.advisor = "advisor"`）、`domain/workbench/errors.py` |
| **执行器与账本** | `application/workbench/advisor.py`、`runner.py`、`ledger.py`（事件 payload 写入 `"to": "advisor"` / `"from": "advisor"`）、`session_service.py` |
| **正式方法与工具门禁** | `formal_model_calls.py`、`formal_host_calls.py`、`method_tools.py`、`method_plans.py`、`execution_plan.py`、`records.py`、`runtime_tools.py` 均校验 `wheel == Wheel.advisor` / `"advisor"` |
| **前端与测试集** | `knowbench-web-frontend/app/features/shell/model/nav.ts`、`features/work/ui/work-screen.tsx`；后端大量 `*_db.py` 测试与前端 `preview/fixtures/` |

因此，当前阶段采用**「文档先正名、代码暂保留」**是最稳妥、性价比最高的策略，不会阻塞当前方法契约（M0–M2）推进。

---

## 四、后续改名规划（建议窗口与目标形态）

### 1. 建议改名窗口

不要为改名单独开一次全栈破坏性变更，建议绑定以下两个自然窗口之一顺带完成：
1. **运行时多角色与执行引擎统一重构时（M3 阶段）**：重构 `advisor.py`、`FormalExecution`、`FormalModelExecution` 以支持多上下文与通用执行块派发时；
2. **固定专家旧路径退役时（参考 SDD `0050`）**：清理 `receipt is None` 等历史分支时一并统一命名。

### 2. 建议目标命名

| 原命名 | 建议新命名 | 说明 |
| :--- | :--- | :--- |
| `advisor.py` / `class Advisor` | `task_runtime.py` / `class TaskRuntime`（或 `workflow_engine.py` / `WorkflowEngine`） | 明确其“任务调度与工作流执行引擎”定位，与 `FormalExecution` / `FormalModelExecution` 形成清晰的宿主-策略层次 |
| `Wheel.advisor`（`"advisor"`） | `Wheel.runtime`（`"runtime"`）或 `Wheel.engine`（`"engine"`） | 与 `Wheel.user`（`"user"`）形成“用户操作 vs 平台执行引擎接管”的无歧义对照 |
| 错误提示中的 `"the advisor ..."` | `"the runtime ..."` / `"the task engine ..."` | 消除对用户和开发者的拟人误导 |
| 前端 `nav.ts` 等的 `wheel === 'advisor'` | `wheel === 'runtime'`（任务形态字段与方向盘归属解耦） | 不再把“方向盘在引擎侧”直接等同于单一 `'expert'` 概念，可承载专家任务及其它工作台任务 |

### 3. 实施切换步骤清单（待执行）

1. **数据库平滑迁移**：新迁移先将 `ck_workbench_sessions_wheel` 放宽为 `('user', 'advisor', 'runtime')`（或停机窗口一次性更新存量 `wheel` 列为 `'runtime'` 后直接切换约束），再收紧为 `('user', 'runtime')`。
2. **账本历史事件策略确认**：确定历史 `events` payload 中已落库的 `"advisor"` 字段是否只读兼容保留（新事件一律写 `"runtime"`），避免篡改审计账本。
3. **后端模块与路由接口切换**：更新 `states.py`、`runner.py`、`ledger.py`、`formal_*_calls.py`、`method_*.py` 及 `advisor.py` 模块重命名。
4. **前端与测试同步**：更新 `knowbench-web-frontend` 的状态判定与 `preview/fixtures/`、后端全量测试后，再更新文档中遗留的 `advisor.py` / `Wheel.advisor` 代码索引。

---

## 五、正式方法的两类及市场分区

分类取决于方法版本冻结时的做法。工具方法（`ToolProcedure`）直接派发固定职责的实现；实现可以执行确定性计算，也可以在规定预算内作模型判断。专家方法（`Orchestration`）用步骤引用已孵化的方法版本，传入约定的输入，独立验收本层承诺，并按声明导出结果。一个专家作为根调用或作为另一专家的一步，都使用相同的定义和接口。

角色、职责、信息隔离与交叉复核属于专家的编排。用户界面统一称“专家”；需要表达分工时直接写出谁分析、谁复核及各自可读的成果。能力标签要有对应的验证证据。两次引用同一专家版本会产生两个调用实例，分别记录输入和产物。

KnowMart 目标分区为工具区和专家区；金融、办公等业务类目可跨分区使用。交付与目录要携带冻结类型及精确版本；可见、购买、组合许可和当前执行授权分别核对。公开专家或工具还须满足相应的发布与验证要求。

**实现衔接。** 2026-11-14 冻结编译器保留三类历史枚举，KnowMart 现有专家交付与目录也采用旧格式。C2 递归候选先按其原始基线验证；M3 契约窗口统一更新 KnowLab 定义与生成器、KnowBench 消费锁、KnowMart 交付和两区展示。迁移须盘点现有精确引用、冻结摘要和测试回执，保留其历史含义；旧类型名不能作为新版本的运行或公开资格。运行时改名可另行安排。方法的完整定义见[专家方法孵化与递归编排方案](../专家孵化方案/luna/专家方法孵化与递归编排方案.md)。

## 六、附记：常驻触发概念拟从 `Duty（职责）` 对齐为 `Always-on / Routine`

同样属于“概念本质没问题、但现用命名易混淆”的，还有 `连接器方案.md` 与 `decisions.md` 里目前的「职责（`Duty`）」：

1. **当前状态与命名问题**：
   - `连接器方案.md` §7 定义的「职责（`Duty`）」专指“用户将某个已冻结专家方法配置为定时、knowfeed 订阅或连接器事件反复唤醒的长期托管配置”（每次唤醒生成一件单次委托 `Task`），而非单次运行。
   - 但“职责（`Duty`）”极易与“专家方法的职能职责”以及“专家团成员角色的职责（`responsibility`）”撞词，且代码里目前尚未落地 `duty` 实现（改名零历史包袱）。
2. **建议对齐行业主流命名（对标 xAI Grok Bot / Meta Muse / OpenAI dots）**：
   - **运行形态对仗**：产品层统一称 **「单次委托（One-off Task）」** vs **「常驻（`Always-on`）」**，明确同一个专家方法可以同时支持单次调用与常驻触发，底层通过 `queued_behind` 串行排队互不冲突；
   - **触发配置对象**：对标 Grok Bot 的 `Routine`，将原 `Duty` 改名为 **「常驻例程（`Routine`）」**（中文界面可称「常驻例程 / 常驻任务」），其核心语义不变——仍是在醒来时生成一件普通单次 `Task`，把上一次写入 knowbase 产出区的成稿作为本次输入，并遵守「不用问我」的收窄白名单与独立预算上限。
3. **清理范围（零代码迁移成本）**：
   - 由于 `knowbench-app` 尚未实施 `duty` 表与调度器，后续只需在实施前将 `连接器方案.md` §7、`decisions.md` 及《方法主稿》中的「职责（`Duty`）」同步替换为「常驻 / 常驻例程（`Always-on` / `Routine`）」，新建表与接口直接以 `routines` 命名即可。
