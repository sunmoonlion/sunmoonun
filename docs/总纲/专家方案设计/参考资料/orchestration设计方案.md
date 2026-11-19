# `Orchestration` 理想路径构建设计方案（KnowLab 孵化编排 $\rightarrow$ KnowBench 执行联动）

> **定位**：本文档聚焦解决“如何按理想路径在 KnowLab 构建合规的 `Orchestration`（第一次编排）”，彻底替代当前“手写导入 `.json`”的过渡做法，并梳理与 KnowBench 运行时门禁联动放开的完整工程路径。  
> **对照依据**：[专家方法孵化与递归编排方案.md](../专家孵化方案/luna/专家方法孵化与递归编排方案.md)、[架构再讨论-gemini.md](./架构再讨论-gemini.md)、[advisor现在使用建议和以后改名.md](./advisor现在使用建议和以后改名.md)，以及 `wsl-dev`（`/home/zymun/worktrees/luna/`）上 `knowlab-app` 与 `knowbench-app` 现行源码。  
> **技术路线声明**：经重读 `/home/zymun/repo/Agently`（`4.1.3.7`，commit `1db342a`）源码确认，Agently 的 `TriggerFlow` 内存事件快照流、宽松字典式 `TaskDAG` 及单向 prompt `AgentlyTaskDAGPlanner` 均不适配本项目的 PostgreSQL 事务账本与强类型冻结契约；本方案**完全基于自有代码体系自建，不引入任何 Agently 依赖或代码**。

---

## 一、现状盘点：设计目标 vs 现存代码缺口

截至当前 `wsl-dev` 代码状态，底层**契约与验证底座已大部就位**，但**“AI + 作者协同生成 `Orchestration`”的中间链路尚未打通**：

| 环节 | 已有资产（已落代码） | 当前缺口 / 阻塞点 |
| :--- | :--- | :--- |
| **契约模型与静态校验** | `knowlab-backend/.../formal_method.py`（及导出 `formal_method_generated.py`）已定义 `Orchestration`、`MethodStep`、`StepInput`、`ValueSlot`、`ValidationRule`、`ApprovalRule`，含无环与输出槽匹配校验 | 尚缺多成员角色模型 `MemberRole` 与 `MethodStep.role_id`（对应 [架构再讨论-gemini.md](./架构再讨论-gemini.md) §4.1） |
| **依赖编译与分类** | `formal_method_compiler.py`（`compile_method`）与 `formal_methods.py`（`_dependencies`）已实现递归 `(method_id, version, digest)` 核验及 `tool`/`expert`/`expert_team` 分类 | 尚未接通 `role_count >= 2` 升类判定，且 `formal_methods.py:619` 强制 `Orchestration` 仅限 `visibility="private"` |
| **AI 孵化工作流底座** | `knowbot_incubation.py` + `incubation.py` + `knowbench/.../packs.py`（`INCUBATE`）已实现作者发起、费用上限、并发锁、`Handback(sources, gaps, suggestions, self_check)` 与「接受/改了再接受」 | `knowbot_incubation.py:326` 明确拦截 `body.formal_method is not None`；`IncubationRequestV1` 缺少已冻结积木目录，且只认旧 `WorkdraftBody.steps` |
| **前端编排编辑器** | `formal-method-editor.tsx` 已实现加载草稿、展示 `FormalOrchestrationSummary`、触发测试/冻结 | 目前只能通过 `<input type="file">` **导入 `.json` 文件**构建 `Orchestration`，仅支持编辑标题/用途/`instructions` 文本，无法可视化编排或接收 AI 建议 |
| **运行时展开与门禁** | `formal_method_plan.py`、`formal_orchestration_execution.py` 与 `formal-orchestration.ts` 已跑通最小确定性链路 | `formal-orchestration.ts` 限制单候选/`max_replans===0`/全必做/`source!=='resource'`；`formal_method_plan.py` 只允许展开无模型轮次的 `mcp` 叶子 |

---

## 二、总体架构：四段式构建闭环

理想路径的核心原则是：**“积木目录先投影 $\rightarrow$ AI 结构起草 + 编译器有界自修 $\rightarrow$ 作者带溯源审定保存 $\rightarrow$ 覆盖变化测试冻结”**，不让 AI 凭空编造方法引用，也不把未经编译校验的残缺图交给作者。

```text
  [1. KnowLab 可用积木目录投影]
     已冻结的 tool / expert 方法 (method_id, version, digest, slots, access_requirements)
                │
                ▼
  [2. AI 第一次编排起草 (KnowLab ↔ KnowBench INCUBATE)]
     生成 FormalMethodDraft 变更建议 (roles / steps / depends_on / inputs / exports / rules)
     缺方法 → 禁编造，转 Gap(missing_method)；缺业务判断 → 转 Gap(judgment)
                │
                ▼
  [3. 确定性校验与有界自修闭环 (Compiler-in-the-Loop)]
     Schema(Orchestration.valid) → MemberRole一致性 → _dependencies & compile_method
     └─ 不通过？→ 携带精确路径报错退回 AI 自修（最多 N 轮，受预算管控）
     └─ 通过！  → 输出带 sources 溯源的 Handback
                │
                ▼
  [4. 人话作业清单审定工作面 (formal-method-editor.tsx)]
     AI 图级提议包直接在清单上 Diff 高亮（整包接受 / 改后接受 / 拒绝）+ 缺口待办处理 → 保存工作稿
     （Stage B 起按需展开轻量只读拓扑图，用于核对并行/分支/隔离边界与测试排错）
                │
                ▼
  [5. 验证、允许变化测试 (FormalTestSuite) 与版本冻结]
```

---

## 三、核心设计一：可用积木目录投影与缺口规则

由于 `formal_methods.py._dependencies` 强制要求编排里引用的每个子方法都具备真实的 `(method_id, version, digest)`，AI 起草前必须拿到确定的“积木清单”。

### 1. `MethodCatalogEntry`（投喂给孵化轮次的只读目录投影）
KnowLab 在发起编排轮次前，从 `FormalMethodService.listing`（以及平台/作者已有已准入且已注册的正式方法）投影出一份紧凑目录，随孵化请求下发：

```python
class MethodCatalogEntry(Strict):
    method_id: UUID
    version: int = Field(ge=1, strict=True)
    digest: Digest
    method_kind: Literal["tool", "expert", "expert_team"]
    title: Text
    purpose: Text
    applies_when: tuple[Text, ...]
    excludes: tuple[Text, ...]
    inputs: dict[Name, ValueSlot]       # 仅投影接口契约（schema_ / meaning / required）
    outputs: dict[Name, ValueSlot]
    access_requirements: tuple[Name, ...]  # 所需资源角色摘要
    allowed_callers: tuple[Literal["host", "model"], ...]
```

* **体积控制**：目录仅投影接口声明与 `ValueSlot`（不展开子方法内部步骤源码），确保不撑爆 `MAX_REQUEST_BYTES`；同时附带 `catalog_digest` 指纹，防止审定期间引用的方法池漂移。
* **可见性过滤**：只投影**作者本人私有可用**及**已获准引用的公共方法**；未冻结草稿、已撤回版本不进入目录。

### 2. 缺口（`Gap`）与反编造规则
1. **严禁伪造引用**：AI 在 `MethodStep.candidates` 中填入的任何 `(method_id, version, digest)` 必须严格命中本轮传入的 `method_catalog`；任何不在目录内的 ID 一律在校验层拦截。
2. **缺少底层工具/子方法时的正规出口**：若种子需求需要某个能力但 `method_catalog` 中没有合适积木，AI **不得**在 `Orchestration` 里塞黑盒自由文本蒙混过关，而必须生成一条缺口：
   * 新增/扩展 `Gap` 类型或分类标签（如 `kind: Literal["judgment", "missing_method"]`）；
   * 在 `question` / `proposal` 中写清：**“缺少执行 `<某能力>` 的已冻结方法（建议先孵化一个 `tool` 方法，或确认是否改用目录中的基础 `skill_instruction` 方法 `<X>` 暂代）”**。
3. **业务判断继续转 `Gap`**：沿用 `INCUBATE_METHOD` 铁律——凡涉及财务口径、阈值、假设、验收容差或外部副作用审批范围，一律转为 `Gap` 由作者拍板，不替作者写进规则。

---

## 四、核心设计二：升级 `knowbot-incubation` 协议与自修闭环

不需要另起炉灶重写一套异步孵化队列、计费和回执机制，直接在既有 `knowbot_incubation.py` + `incubation.py` + KnowBench `INCUBATE` 链路之上演进即可。

### 1. 解除拦截并按草稿模式分流
* 在 `knowbot_incubation.py`（约第 326 行）解除对 `body.formal_method is not None` 的一刀切拦截，改为依据请求类型分流：
  * `legacy_steps`：走现有 `knowbot-incubation/v1`；
  * `formal_method`：走升级后的正式方法孵化契约（建议定义为 `knowbot-incubation/v2`，或通过独立可选载荷字段向后兼容）。
* KnowBench 侧 `incubations.py` 与 `packs.py` 新增对应正式方法编排的系统提示与结构校验环节（`INCUBATE_FORMAL`），继续复用同一套作者电脑沙箱、费用上限与 `Task/Attempt` 账本。

### 2. 正式方法孵化请求与交回扩展
* **请求新增输入**：
  * `formal_draft: FormalMethodDraft | None`（当前 `workdraft.body.formal_method`，首次起草时可为 `None`）；
  * `method_catalog: tuple[MethodCatalogEntry, ...]`；
  * `catalog_digest: Digest`；
  * `target_profile: Literal["static_subset", "full"]`（用于阶段 A 约束是否仅生成当前运行时已可跑的静态子集，见第六节）。
* **AI 必须产出的结构要素（对应 `Orchestration` 与五要素）**：
  1. `roles`：声明 `MemberRole`（`id`, `name`, `responsibility`, `isolated_context`）；单视角常规流程可留空或单角色，多视角分析/独立复核流程必须声明 `>= 2` 个角色；
  2. `steps`：按业务语义拆分步骤，绑定 `role_id`、从 `method_catalog` 匹配 `candidates`、梳理无环 `depends_on`；
  3. `inputs` 连线：显式映射到 `CallerValue` / 上游 `StepValue` / 角色范围参数 `LiteralValue` / `ResourceValue`；
  4. `select_when` / `required_when` / `always_required` 与 `exports`；
  5. `how_to_validate`（`ValidationRule`）与 `what_requires_approval`（`ApprovalRule`）。
* **建议路径规范与图级提议包（`ProposalBundle`）**：
  底层改动仍沿用 `op: Literal["set", "add", "remove", "move"]` 与 `SourceEntry(idea / answer / proposal)`：
  * `capability_declaration` / `capability_declaration/<field>`
  * `procedure/instructions`
  * `procedure/roles` / `procedure/roles/<role_id>`
  * `procedure/steps` / `procedure/steps/<step_id>` / `procedure/steps/<step_id>/<role_id|candidates|depends_on|inputs|outputs|select_when|required_when|always_required|on_failure>`
  * `procedure/exports/<export_name>`
  * `how_to_validate/<promise_id>` / `what_requires_approval/<requirement_id>`

  **注意（跨节点关系绑定）**：由于编排存在跨步骤依赖、`StepValue` 连线与角色归属等交叉约束，前端审定**不能**按单个格子拆碎接受/拒绝，而必须把耦合的原子操作打包成**内部自洽的图级提议包**（例如“新增步骤 B + 调整下游 C 的 `depends_on`/输入连线 + 更新导出”），保证接受或拒绝任意提议包都不会破坏图的不变量。

### 3. 确定性校验与有界自修闭环（Compiler-in-the-Loop）
在把 AI 生成的建议打包进 `Handback` 返回作者之前，**必须先构造临时应用后的 `FormalMethodDraft` 快照**，连续通过四道确定性检查：

1. **契约与 DAG 自检**：调用 `FormalMethodDefinition.model_validate` 与 `Orchestration.valid()`，确保无环、所有 `StepValue` 引自已声明的 `depends_on` 且 `schema_` 与 `meaning` 匹配、可选输出不满足必选输入、`always_present` 导出必达。
2. **成员角色与隔离一致性自检**（对齐 [架构再讨论-gemini.md](./架构再讨论-gemini.md) §4.1）：
   * `step.role_id` 必须命中 `Orchestration.roles`；
   * 若 `len(roles) >= 2`，非汇出步骤须声明 `role_id` 且不存在未被任何步骤引用的“空壳角色”；
   * 隔离角色之间的数据引用仅通过正式 `StepValue` 槽传递。
3. **目录真实性与编译器核定**：
   * 核验每个 `MethodRef` 的 `(method_id, version, digest)` 与传入的 `method_catalog` 完全一致；
   * 核验 `StepInput` 的 `slot` 类型/含义与被调子方法声明的 `inputs[name]` 兼容；
   * 调用 `compile_method()` 预判最终分类（`"expert"` / `"expert_team"`）及依赖图深度/节点上限。
4. **可执行子集门禁（Stage A 可选开启）**：若当前 `target_profile == "static_subset"`，同步检查是否满足当前 KnowBench 执行器支持范围（提示/修正不支持的高级字段）。

**自修循环规则**：
* 任一检查失败 $\rightarrow$ 将精确的**校验报错路径、错误原因、预期契约**喂回 AI 在同一轮孵化内修正（有界重试，默认 `max_repairs = 3`，受本轮作者 `budget` 上限保护）；
* 超过重试上限仍无法通过 $\rightarrow$ 若仅局部步骤有争议，把冲突点降级为 `Gap`（保留其余合法步骤建议）；若整体结构无法收敛，则如实标记失败原因返回，绝不把非法 `Orchestration` 塞给前端。

---

## 五、核心设计三：前端形态——「人话作业清单主工作面 + 按需轻量只读拓扑图」

结合行业教训（Coze 企业版收缩与社区对 Dify 手工拖线画布的反思：**“生成与修改靠自然语言/结构化清单，核对结构与故障靠只读图”**）以及 KnowLab 面向非开发者的定位，改造 [formal-method-editor.tsx](file:///home/zymun/worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/formal-method-editor.tsx)（保留 `.json` 导入/导出作为调试兜底）。页面收敛为以下设计，**不做 Dify 式拖线画布、不做常驻“双视图编辑器”，也不另设独立的 AI 建议文字列表区**：

1. **顶部 AI 起草与积木目录条**：
   * 展示作者当前可用的已冻结方法积木池（按 `tool` / `expert` 分类，可搜索查看各自输入输出契约）；
   * 提供 **「AI 起草编排」**（空白草稿时）与 **「让 AI 修改编排」**（支持指定某一步 `step_id` 附带修改指令，并勾选是否附带最近测试报告），复用现有孵化轮询与费用展示逻辑。
2. **唯一主工作面：人话作业清单（兼具编辑、Diff 审定与角色分组）**：
   * **结构呈现**：按拓扑顺序（标明并行组）展示每一步的**业务语义**——做什么、选用哪个积木方法、条件（`select_when` / `required_when`）、需要谁审批，以及人话标明的输入来源（如“来自用户提问 / 来自第 1 步《营收结构》”）；启用专家团 `roles` 时，直接在同清单内按**成员角色泳道/标签**分组展示，一眼看清职责与 `isolated_context` 开关。
   * **AI 提议包直接 Diff 叠加**：AI 起草或修订返回的图级提议包，**直接以视觉 Diff 高亮叠加在作业清单上（绿增 / 黄改 / 红删）**，每条变动附来源角标（`idea` 创意原句 / `answer` 作者答复 / `proposal` AI 提议，悬停查看原文）；作者以自洽提议包为单位点 **「整包接受 / 改后接受 / 拒绝」**，告别“左边看卡片文字、右边脑补图变动”的割裂感。
   * **行内微调与即时门禁**：手工增删步骤、切换 `candidates` 或选择上游输出连线时，直接用清单行内表单/下拉选择器完成，并实时运行前端结构预检标红提示不匹配输入或空壳角色。
3. **轻量缺口待办栏（`Handback.gaps`）**：
   * 专门承接“清单与图上画不出来”的问题：业务判断类问题就地填写选项或自由答复；`missing_method` 缺口提供直达入口引导先去孵化缺失的基础工具方法，完成后点「让 AI 改」刷新提议包。
4. **按需展开的「轻量只读拓扑图」（Stage B 随分支与测试排错上线）**：
   * **定位边界**：收在右上角「查看结构图」开关与 `FormalTestSuite` 测试结果详情中，平时不占主屏版面（3～6 步线性流程直接看作业清单更清晰）；遇到并行汇合、条件分支、多角色 `isolated_context` 隔离边界或测试失败排查时再展开核对。
   * **工程边界**：**严格只读**（严禁节点拖拽、画线或弹窗改字段），由 `Orchestration` 使用纯分层 DOM/SVG 自动排版（不引入 React Flow 等重型画布库，不存储坐标）；仅支持点击节点高亮定位到对应作业清单行，并在测试执行后标出节点状态（通过 / 条件跳过 / 失败）。

---

## 六、核心设计四：与 KnowBench 运行时及测试的分阶段联动

为避免“KnowLab 已经能编排出复杂 `Orchestration`，但 KnowBench 运行器还跑不起来”的两张皮问题，实施拆为三个衔接阶段：

| 阶段 | 构建侧（KnowLab）交付 | 运行与测试侧（KnowBench）联动解除的限制 |
| :--- | :--- | :--- |
| **Stage A（M2a：打通自建编排生成）** | 1. 完成 `MethodCatalogEntry` 投影<br/>2. 打通 `knowbot_incubation` 正式方法模式与 4 道确定性校验自修闭环<br/>3. 上线「人话作业清单 + 提议包 Diff 叠加 + 缺口待办」主工作面（此时先不做拓扑图），告别手写 JSON | 默认开启 `target_profile="static_subset"` 辅助校验，使生成的图可立即兼容当前 `formal-orchestration.ts` 与 `formal_orchestration_execution.py` 跑通回归验证 |
| **Stage B（M2b：放开完整编排语义与只读图）** | 1. 放开 `select_when` / `required_when` 多分支与多候选 `candidates` 生成<br/>2. 要求 `FormalTestSuite` 用例覆盖基准主干与允许变化分支（对应孵化模板 §4.5）<br/>3. 上线**按需展开的轻量只读拓扑图**（展示并行/分支与测试节点红绿状态） | 1. 解除 `formal_method_plan.py` 仅允许 `mcp` 且 `max_model_turns == 0` 的限制，允许展开 `skill_instruction` 模型叶子<br/>2. 放宽 `formal-orchestration.ts` 对 `max_replans`、多候选、条件必做与 `ResourceValue` 的一刀切门禁<br/>3. 运行器支持条件分支跳过与汇合判定 |
| **Stage C（M3：专家团隔离与市场放开）** | 1. 正式合入 `MemberRole` 与 `role_id` 契约及 `role_count >= 2` 升类编译；作业清单与只读拓扑图同步展示隔离边界分组<br/>2. 补齐公开上架前覆盖率与来源审计检查 | 1. 升级 KnowBench 任务 Runtime（原 `advisor.py` / `FormalModelExecution` 等），按 `isolated_context` 分配独立 `codex_thread_id` 与隔离目录，落实“向下穿透分流规则”<br/>2. 解除 `formal_methods.py:619` 对 `Orchestration` 仅限 `visibility="private"` 的限制 |

---

## 七、待所有者拍板的 3 个工程决策点

1. **孵化自修循环放在哪一端执行？**
   * **选项 A（推荐）**：放在 KnowBench 的孵化执行任务内部（由运行方调用本地校验器对生成的 JSON 做多轮闭环修正，修过后再交回一个干净的 `Handback` 给 KnowLab），减少 KnowLab ↔ KnowBench 跨服务往返轮次，且费用统一计入本轮 `budget`。
   * **选项 B**：每次 AI 吐出草稿都回传 KnowLab 校验，不通过再由 KnowLab 自动重开下一轮委托（跨服务调度开销略高）。
2. **`knowbot-incubation` 契约演进方式？**
   * **选项 A（推荐）**：新增 `knowbot-incubation/v2`（或 `formal-incubation/v1`），与旧 `WorkdraftBody.steps` 的 `v1` 明确隔离，旧版下线后整套清理，不污染 `v1` 的校验逻辑。
   * **选项 B**：在 `v1` 内叠加可选字段兼容两套结构。
3. **Stage A 首期生成的 `Orchestration` 是否默认限制在当前可执行子集？**
   * **建议**：**是**。在 Stage B 尚未放开 `skill_instruction` 叶子和多候选运行时支持前，默认提示并生成当前可跑通的子集（或清晰标注“需等运行时 Stage B 升级的节点”），保证做出来的第一个自建编排方法就能直接跑通端到端测试。
