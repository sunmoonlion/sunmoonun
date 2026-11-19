# Orchestration 全生命周期设计方案（Hydrogen 稿）：第一次孵化 $\rightarrow$ 第二次剪枝 $\rightarrow$ 即时编排 $\rightarrow$ 回炉再造

> **日期**：2026-11-17。工作位置：本地 `wsl-dev`（`/home/zymun/worktrees/luna/`）。  
> **继承与演进基础**：在 [orchestration设计方案.md](./orchestration设计方案.md) 的底座上，吸收全链路源码核查结论，并与总纲 [专家方法孵化与递归编排方案.md](../专家孵化方案/luna/专家方法孵化与递归编排方案.md) §3（方法模板 `T = (D, V, C)`）衔接，补齐**“方法模板与双路赋值（人工选方法 / AI 选方法）$\rightarrow$ 第一次孵化 $\rightarrow$ 第二次剪枝执行 $\rightarrow$ 边界内即时编排 $\rightarrow$ 回炉再造”**全生命周期工程设计。  
> **技术路线声明**：经核对 `/home/zymun/repo/Agently`（`4.1.3.7`）与 `knowlab-app` / `knowbench-app` 源码，本方案**完全基于自有契约、编译展开器与数据库事务账本自建**，不引入 Agently，不做 Dify 式拖线画布。

---

## 一、现状盘点：设计目标 vs `wsl-dev` 现存源码事实

截至当前 `wsl-dev` 检出，静态契约骨架与测试跑道已搭起，但打通全生命周期仍有 5 类核心缺口：

| 层次 | 已有资产（已落代码） | 现存缺口 / 工程阻塞点 |
| :--- | :--- | :--- |
| **1. 契约与编译** | `formal_method.py` / `formal_method_generated.py` 已定义 `Orchestration`、`MethodStep`、`StepInput`、`ValueSlot`、`ValidationRule`、`ApprovalRule`；`formal_method_compiler.py` 已实现 `_step_interface`、`_permission_ceiling` 与 `classify_dependencies`；`formal_method_plan.py` 已有 `_validate_slots` 校验 | ① `Orchestration` 尚缺 `MemberRole` 与 `step.role_id`；② 尚无“模板变量（`Variable`）”与“草图 $\rightarrow$ 确定性展开器”代码；③ `formal_methods.py:619` 强制编排方法仅限 `visibility="private"` |
| **2. 孵化起草底座** | `knowbot_incubation.py` + `incubation.py` + `knowbench/.../packs.py`（`INCUBATE`）已实现作者发起、费用上限、并发锁、`Handback(sources, gaps, suggestions, self_check)` 与审定流 | ① `knowbot_incubation.py:326` 直接拦截 `body.formal_method is not None`；② `IncubationRequestV1` 缺少可用积木目录投影；③ `FormalMethodService.listing` 仅返回作者本人方法，缺平台基础积木、共享 `meaning` 词表及 AI 扫描 MCP/Skill 自动起草 `ValueSlot` 的逻辑 |
| **3. 前端编排页** | `formal-method-editor.tsx` 已支持加载工作稿、展示 `FormalOrchestrationSummary`、选择 `ToolProcedure` 实现源、触发测试与冻结 | ① 目前仅支持 `<input type="file">` **导入 `.json`** 与改标题/用途/`instructions`，无 AI 起草、Diff 审定或人话清单编辑；② **整个前端组件目录尚无任何增删/编辑 `ValueSlot`（`schema`、`meaning`、`required`、`on_missing`）及模板变量的设置界面** |
| **4. 运行时入口与叶子** | `formal_execution.py`、`formal_orchestration_execution.py`、`formal_recursive_runtime.py`、`formal_method_plan.py` 已跑通最小确定性链路 | ① `formal_host_calls.py:165-239` 强耦合 `test_run_for_task`（仅 KnowLab 测试单），未接 KnowBench 用户任务；② `formal_method_plan.py:90` 限制叶子只能是 `mcp` 且 `max_model_turns == 0`，未合流 `TurnDriver` 跑 `skill_instruction` 模型步 |
| **5. 分支、重排与授权** | `method_authorization.py` 已建立严格的 `PermissionGrant` / `MethodAuthorization` 范围比较；`Ledger` 支持 `Task/Attempt/Artifact` 持久化 | ① `select_when` / `required_when` 为自由文本；`accepted_outputs` 与 `resolve_leaf` 假定定长下标全步必跑必成，不支持 `skipped`；② `PermissionGrant` 禁止用户单次确认向下二次委托，即时编排需专用叶子确认与 `Plan v1/v2` 快照机制 |

---

## 二、全生命周期总体闭环（四段一核）

四段流程**共用同一套内核**：`MethodCatalogEntry`（积木目录）+ `OrchestrationSketch`（薄草图）+ `elaborate()`（确定性展开器）+ `Ledger`（数据库事务账本与不可变 `Plan` 快照）。

```text
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 第一段：KnowLab 第一次孵化编排（模板/创意 → 基准图 + 允许变化）       │
  │  方法模板 T=(D,V,C) + 积木目录投影 + 共享词表                        │
  │  ├─ 入口 A：作者手工选方法给模板赋值 ──┐                            │
  │  └─ 入口 B：AI 从目录选方法起草/赋值 ──┴─→ 同一 Sketch → elaborate() │
  │  → 人话作业清单 Diff 审定 & 缺口处理 → FormalTestSuite 冻结版本       │
  └───────────────────────────────┬─────────────────────────────────────┘
                                  │ 发布 / 私有可用 (MethodRef + digest)
                                  ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 第二段：KnowBench 第二次剪枝执行（基准图及允许变化内按题定型）         │
  │  按具体问题裁剪可选分支、选定候选、绑定入参与资源                      │
  │  → 同一展开器生成本次执行计划 → 运行器按节点就绪度推进（MCP + Codex）   │
  └───────────────┬───────────────────────────────┬─────────────────────┘
                  │ 覆盖不了 / 无合适专家           │ 用得好且已改结构 / 缺能力
                  ▼                               │
  ┌───────────────────────────────────────┐       │
  │ 第三段：KnowBench 边界内即时编排        │       │
  │  显式退出原专家承诺（标记自组/自改计划） │       │
  │  AI 出临时 Sketch → elaborate() 校验   │       │
  │  → 叶子级权限交集确认 → 落 Plan v1/v2 快照执行 ──┘
  └───────────────────────────────────────┘       │
                                                  ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 第四段：回炉再造（KnowBench → KnowLab 正式定型闭环，主稿 §2.8.3）     │
  │  沿现有孵化请求通道传回：原方法版本 + 需求 + Sketch 差异 + 缺口诊断    │
  │  按权限分流（原作者新修订 / 派生者新稿 / 使用者提需或另起）→ 重测冻结   │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## 三、第一段：KnowLab 第一次孵化编排（生成并冻结基准图）

### 3.0 方法模板前置与双路赋值入口（与总纲 §3 衔接）
对照总纲 [专家方法孵化与递归编排方案.md](../专家孵化方案/luna/专家方法孵化与递归编排方案.md) §3.1，方法创作的完整起点是**方法模板 `T = (D, V, C)`**（含固定骨架、待定变量 `V` 与变量约束 `C`，例如 §3.3 的财务方法模板候选 C01–C15）。将模板收敛为具体 `Orchestration` 时，系统同时支持两条同源汇流的入口：

1. **人工选方法赋值模板**：作者选定一个方法模板后，直接在工作台从积木目录中挑方法、填变量约束，手工收敛形成草图 `OrchestrationSketch`。
   * **人工挑方法时，方法之间的关系如何确定**（不引入画布拖线）：
     * **有模板骨架时**：步骤先后与上下游数据交接关系已在模板 `D` 中预设，作者只需在对应槽位“换积木”，`elaborate()` 自动核对所选方法与上下游接口是否兼容；
     * **从零手动挑方法或增删步骤时**：① **数据依赖与连线**由作者在清单排好顺序后交由 `elaborate()` 按 `schema_ + meaning` 自动匹配（唯一匹配自动连，多匹配在行内弹出下拉二选一写入 `wires`，无匹配归入 `CallerValue`/固定值或提示缺口径转换方法）；② **无数据传递的纯先后顺序（`after`）**在清单行内勾选前置步骤（未勾且无数据依赖的默认可并行）；③ 也可直接挑好积木后点击 **「让 AI 梳理顺序与导出」**，由 AI 补齐 `after`、`wires` 与 `exports` 再核对。
2. **AI 选方法赋值（本方案重点展开）**：作者给出创意或选定半成品模板，由 AI 读取积木目录投影（`MethodCatalogEntry`）与模板约束，自动挑选匹配的下层方法、填充变量并生成/修改 `OrchestrationSketch`（缺方法转 `Gap(missing_method)`，缺口径转 `Gap(judgment)`）。
   * **针对只有 `idea` 的小白作者的无感引导流**：① AI 先从一两句 `idea` 提取目标并**后台隐式匹配现成模板**（未命中则直接拆 3～5 个中文步骤，缺失关键口径转为 2～3 道带选项的 `Gap` 选择题）；② 后台按三层漏斗自动给每步配好积木（找不到确定性工具时，常规分析配基础 `skill_instruction`，真缺外部能力报 `Gap(missing_method)` 并附暂代选项）；③ `elaborate()` 自动连线与补全接口，遇连线歧义转为人话单选；④ 全程不向小白暴露 `Sketch` / `ValueSlot` / `CatalogKey` 等术语。

两条入口**不造两套后台**：无论作者手工赋值还是 AI 选方法赋值，最终产出的都是同一份 `OrchestrationSketch`，交由同一个 `elaborate()` 展开验证，并进入同一套人话作业清单审定与 `FormalTestSuite` 测试冻结。

### 3.0.1 如何确定积木（`tool` 方法的粒度标准与三条生成路径）
编排只是“拼装”，前提是先要有高质量的可拼装积木（冻结的 `tool` 方法）。依据 [原20个财务方法的工具方法提炼.md](../专家孵化方案/luna/原20个财务方法的工具方法提炼.md) 与 `knowbench/.../formal_methods.py` 的 `_sources()` 机制，确定积木须遵循以下标准并打通三条生成路径：

1. **确定一块合格积木的四条标准**：
   * **职责完整且粒度适中**：既不把加减乘除拆成方法，也不把“读数+核对+预测+成稿”全包成一个黑盒；应像“CAGR 计算”“资产负债平衡核验”“审计意见识别”这样能独立声明输入、处理边界与可验证产出。
   * **输入封闭、内部不越界**：所需事实与数据全部在 `inputs` 中显式声明，严禁在内部隐藏“再去搜集资料”或私自调用其他注册方法。
   * **载体与业务语义分离**：先定“吃什么、算/判什么、怎么验”，再绑定具体实现载体（`platform` 公式、`mcp` 工具、`skill_script` 脚本或 `skill_instruction` 有界模型判断）。
   * **出入口对齐共享 `meaning` 词表**：新积木的 `ValueSlot.meaning` 必须遵循平台统一词表，否则在 `Orchestration` 中无法与上下游自动连线。
2. **工程上“积木从哪来”的三条生成路径**：
   * **路径 A：平台自上而下提炼基础积木（解决冷启动）**：平台按高频领域（如从《原 20 个财务方法的工具方法提炼》拆出的读数、口径转换、勾稽核验、核心计算、成稿等）孵化通用 `tool` 方法，冻结进全平台可见目录。
   * **路径 B：现有 `MCP` / `Skill` 资产自下而上封装孵化**：复用 `formal_methods.py` 现成的 `_sources()` 扫描能力（识别 `connection` 下的 MCP tool，以及 `skill` 下的 `SKILL.md` 指令与 `.py/.sh/.js` 脚本），在 KnowLab 提供封装向导——由作者选中源资产、AI 辅助补齐五要素、`ValueSlot` 映射与正反例测试集，冻结升级为正式积木。
   * **路径 C：`Gap(missing_method)` 倒逼按需制砖并回流**：无论 KnowLab 编排还是 KnowBench 即时编排，当目录里缺少某块积木时，AI 除了产出 `Gap(missing_method)`，还需附带**“缺失积木的接口需求草案”**（建议的 `inputs`/`outputs` 槽位与建议载体）；作者点直达入口跳往 Tool 孵化流绑定载体并测通冻结后，新积木自动回流进当前 `MethodCatalogEntry` 目录，接续完成原编排。

### 3.1 积木目录投影（`MethodCatalogEntry`）与海量积木三层选择机制
为满足 `formal_methods.py._dependencies` 对真实 `(method_id, version, digest)` 的强核验，同时防止积木数量增长后撑爆上下文或导致误选，投影与选择按以下机制协同：

```python
class MethodCatalogEntry(Strict):
    catalog_key: Name                     # 本轮短别名，避免 LLM 拼写 UUID/sha256 出错
    method_id: UUID
    version: int = Field(ge=1, strict=True)
    digest: Digest
    method_kind: Literal["tool", "expert", "expert_team"]
    implementation_kind: Literal["platform", "mcp", "skill_instruction", "skill_script"] | None
    title: Text
    purpose: Text
    applies_when: tuple[Text, ...]
    excludes: tuple[Text, ...]
    inputs: dict[Name, ValueSlot]         # 仅投影契约接口，不展开子方法实现源码
    outputs: dict[Name, ValueSlot]
    access_requirements: tuple[Name, ...] # 所需资源角色摘要
    allowed_callers: tuple[Literal["host", "model"], ...]
```

* **冷启动积木供给**：改变目前 `FormalMethodService.listing` 仅见作者本人方法的现状，由平台先孵化并开放一批通用基础方法（数据读取、口径转换、核对计算、成稿等）进入所有作者的目录投影。
* **共享 `meaning` 规范**：`Orchestration.valid()` 要求连线两端 `ValueSlot.schema_` 与 `meaning` 逐字相等。平台须建立通用 `meaning` 键名与单位/期间等取值词表，确保跨批次方法可自动连线；口径确实不同时，显式插入口径转换工具方法，严禁隐式转换。
* **体积与防漂移**：仅投影接口摘要并附带 `catalog_digest` 指纹；未冻结草稿与已撤回版本不入目录。
* **海量积木下的三层选择漏斗**（解决“积木很多时怎么选对、不撑爆上下文”）：
  1. **第一层（确定性硬过滤）**：后端先按**权限与可用性**（自有私有 + 平台基础 + 已购/获准 KnowMart 方法，且环境满足 `access_requirements`）、**接口签名兼容度**（匹配模板槽位或上下游 `schema_ + meaning`）与**版本收敛**（同一 `method_id` 默认只投最新推荐冻结版）筛掉不合规候选；
  2. **第二层（Top-K 召回与二次检索确认）**：
     * **手工挑**：编辑器目录按领域、关键词及“与当前上下游 `meaning` 直接兼容度”排序展示；
     * **AI 选**：先按需求文本、模板约束与关键 `meaning` 召回 **Top 20～50 个 `MethodCatalogEntry`** 投影入轮（不塞全库）；若首轮未命中，允许 AI 以精确关键词或目标 `inputs/outputs` `meaning` 发起一次目录检索确认，确认确实无合适积木后再产出 `Gap(missing_method)`，避免因漏召回误报缺口；
  3. **第三层（同类多积木排序与拍板）**：多个候选接口均兼容时，固定按**① 确定性实现（`platform`/`mcp`/`skill_script`）优先于模型推理（`skill_instruction`） $\rightarrow$ ② 已有授权/免新配连接优先 $\rightarrow$ ③ `meaning` 直连无需插转换器优先 $\rightarrow$ ④ 官方基础积木与高测试覆盖/高复用优先**排序；若属于业务口径取舍（如不同数据源），则并入 `SketchStep.candidates` 多候选或转 `Gap(judgment)` 由人拍板。

### 3.2 「薄草图 + 确定性展开器」代替 AI 裸写完整 JSON
因为 `_step_interface`（槽位逐字照抄）、`_permission_ceiling`（权限覆盖集）、`StepValue` 唯一匹配与限额下限均可通过程序确定性推导，**不让大模型直接生成全量 `Orchestration` JSON 再靠编译器报错反复重试（花作者钱且在 `INCUBATE` 无文件权限沙箱内难收敛）**，而是采用两层结构：

* **AI 只产出薄草图 `OrchestrationSketch`**：
  ```python
  class SketchStep(Strict):
      id: Name                                 # 稳定节点 ID
      title: Text
      purpose: Text
      candidates: tuple[CatalogKey, ...]        # 必须命中目录投影
      after: tuple[Name, ...] = ()              # 仅纯顺序依赖；数据依赖由连线推出
      wires: dict[Name, WireChoice] = {}        # 仅歧义时由作者/AI 指定
      fixed: dict[Name, JsonValue] = {}         # 固定字面量（LiteralValue）
      select_when: Text
      required_when: Text
      select_expr: dict[str, Any] | None = None # 可选机读分支谓词（Stage B 启用）
      always_required: bool
      on_failure: Literal["pause", "fail"]
      role: Name | None = None                  # 随 MemberRole 进契约后启用
  ```
* **纯函数展开器 `elaborate(sketch, resolved_catalog)`**：
  1. 照抄被调候选方法的 `inputs[*].slot` 与 `outputs`（多候选时核验所用槽位接口一致）；
  2. 按 `schema_ + meaning` 在可达上游中自动连线 `StepValue`：唯一匹配自动连；多匹配报“连线歧义”转表单下拉选择；无匹配报“需外部 `CallerValue` / 固定值 / 缺失口径转换积木”；
  3. 自动计算 `depends_on`、权限覆盖上界 `access_requirements` 与子树规模限额；
  4. 调用 `FormalMethodDefinition`、`Orchestration.valid()` 与 `compile_method()` 作为最终确定性断言兜底。
* **可逆性**：配套 `decompile(Orchestration) -> OrchestrationSketch`，保留 `.json` 导入导出能力，导入即反解为草图进入同一页面审阅。

### 3.3 升级 `knowbot-incubation` 孵化协议与图级提议包
* **解除拦截与分流**：在 `knowbot_incubation.py:326` 取消对 `body.formal_method` 的一刀切拒绝，按 `legacy_steps`（`v1`）与 `formal_method`（建议 `knowbot-incubation/v2`）分流；KnowBench 新增内部包 `INCUBATE_FORMAL`，沿用作者电脑沙箱、费用上限与取消/轮询机制。
* **图级提议包（`ProposalBundle`）**：由于编排图存在跨节点 `depends_on`、`StepValue`、`exports` 与角色归属耦合，禁止按旧版单个格子拆碎接受/拒绝。AI 交回的改动必须打包为**内部自洽的提议包**（每包配套节点、连线、角色与导出变化），附 `SourceEntry(idea / answer / proposal)` 出处；草图自身格式错误在宿主确定性验收内有界返工重答一次。
* **缺口分类与测试用例同期起草**：判断类问题转 `Gap(judgment)`；目录无合适积木禁止编造 ID，必须转 `Gap(missing_method)`。同一孵化回合内，AI 为基准路径及每个允许变化（可选步骤、备选候选）起草 `FormalTestSuite` 输入用例，期望答案由作者填写。

### 3.4 前端交互：「统一小白与职业开发者的渐进式工作台」
改造 `formal-method-editor.tsx`，**放弃 Dify 式拖线画布、常驻双视图编辑器及独立建议列表区**，并且**不区分两套页面、不靠猜测用户身份切换 UI**，而是用“默认极简人话态 + 就地展开工程参数”统一所有作者：

1. **顶部起步区（大输入框 + 安静次级入口）**：
   * 主视野为一个自然语言输入框 + 主按钮 **「AI 生成步骤 / 让 AI 修改」**（小白自然从这里开始，也可指定某一步或附带最近测试报告）；
   * 主按钮旁安静并列三个次级文字入口：**「从模板选」**、**「手动加步骤」**、**「导入 JSON」**（职业开发者可直接跳过 AI 起草，导入 `.json` 自动 `decompile` 进同一工作面）。
2. **唯一主工作面：人话作业清单（默认折叠态 + `[显示工程参数]` 开关）**：
   * **默认折叠态（面向所有人默认干净展示）**：每步卡片默认只展示 3 行人话摘要（步骤标题与所用积木名称、数据从哪来、产出什么）；多角色时同清单内按 `MemberRole` 泳道分组；
   * **原地展开态（面向职业开发者精调）**：点击单步卡片的 **「展开详情」** 或右上角全局 **`[显示工程参数]`** 开关，原地展开 `CatalogKey` 精确版本、多候选 `candidates`、纯顺序 `after`、`select_expr` 分支谓词、`on_failure`、`wires` 以及每个 `ValueSlot`（`schema_`、`meaning`）明细与 `isolated_context` 开关；
   * **Diff 与歧义交互**：`ProposalBundle` **直接以 Diff 高亮（绿增 / 黄改 / 红删）叠加在清单上**，附 `idea / answer / proposal` 出处角标，支持整包接受/改后接受/拒绝；连线歧义永远**人话单选框在上、技术接口校验详情折叠在下**；
   * 侧栏/底栏挂轻量 **缺口待办（`Gaps`）**，处理判断问题与直达孵化缺失积木。
3. **右上角辅助入口（按需展开的轻量只读拓扑图 + JSON 兜底）**：
   * **轻量只读拓扑图（Stage B 上线）**：收在右上角「查看结构图」及测试结果详情页，平时不占主屏（线性流程无需看图）；采用纯分层 DOM/SVG 自动排版（零重型画布依赖），**严格禁止拖拽或改字段**，仅用于核对并行汇合、分支走向、`MemberRole` 隔离边界与测试红绿状态高亮。
   * **导入 / 导出 JSON**：收在右上角菜单供本地调试与批量迁移使用。

---

## 四、第二段：KnowBench 第二次剪枝执行（基准图及允许变化内）

用户在 KnowBench 选用已冻结的专家/专家团方法后，在**不突破基准图与允许变化边界**的前提下按具体问题生成当次执行计划：

1. **复用同一内核按题具体化**：在冻结草图/定义上裁剪不触发的可选分支、选定候选 `candidates`、绑定当次 `CallerValue` 与 `ResourceValue`，再跑一次 `elaborate()` 校验所有必做项与 `always_present` 导出仍成立，保存基准方法摘要、节点映射与差异来源。
2. **解除 `skill_instruction` 模型叶子与静态测试单绑定（关键工程改造）**：
   * **拆分用户任务运行路径**：在 `FormalTaskSnapshot` / `FormalHostCalls` 中解除仅查 KnowLab `test_run_for_task` 的限制，区分测试任务与工作台正式任务。
   * **双路径叶子分发合流**：改造 `FormalOrchestrationExecution` 与 `formal_method_plan.py`——`mcp`/`platform`/`skill_script`（`max_model_turns == 0`）继续走 `request_host_call`；`skill_instruction`（`max_model_turns > 0`）合流 `TurnDriver` 对 Codex thread 发有界模型轮次并落统一 `Artifact("formal-step:" + step.id)`。
   * **支持条件分支与 `skipped` 图账本**：为步骤提供结构化条件谓词或有界分支决策轮（输出 `take | skip` + 理由），改造 `accepted_outputs` / `accepted_children` 支持合法 `skipped` 状态及 `on_missing`，以基于拓扑就绪度的动态图调度取代 `expanded_plan.leaf_nodes[current_step]` 定长数组下标。
   * **多角色隔离执行**：M3 落地 `MemberRole.isolated_context` 时，为不同隔离角色分配独立 `codex_thread_id` 与隔离目录，落实“向下穿透分流规则”（仅规划轮与 `skill_instruction` 穿透隔离上下文与立场参数，确定性叶子分流隔离执行）。

---

## 五、第三段：KnowBench 边界内即时编排（超出基准或临时自组）

当现有上架/私有方法均无法直接满足新需求，或用户在已有专家基础上强行增删必做项、引入范围外方法时，按以下工程闭环安全实现即时编排：

1. **明确退出原专家承诺（对齐主稿 §2.8.2）**：
   * 一旦突破原方法允许变化范围或为全新临时组合，系统强制标记并向用户明示：**「用户自组/自改临时计划，未按正式专家完整承诺执行」**，保留原方法版本与修改差异记录，严禁冒充原专家承诺交付。
2. **复用内核现场出图并落 `Plan v1` 不可变快照**：
   * KnowBench 运行时投影**当前用户有权调用的已冻结积木目录**给 AI，AI 输出 `OrchestrationSketch`，由展开器现场校验编译并生成当次 **`Plan v1` 快照**落库，再交由 `FormalOrchestrationExecution` 按 `Task/Attempt/Artifact` 账本驱动，**绝不在内存里无记录改图**。
3. **遵守 `method_authorization.py` 的叶子级授权确认**：
   * 由于即时生成的临时根图没有 KnowLab 准入回执，且 `PermissionGrant` 严禁普通用户单次确认向下二次委托（`delegable=True` 必须绑定 `resource_authority` 与精确 `method_ids`），因此运行前必须由展开器汇总该临时图实际调度的**全部叶子方法与所需连接**（与用户已有权限求交集），弹出**叶子级授权与风险动作确认单**由用户一次性确认后锚定授权。
4. **版本化快照重排（`Plan v1` $\rightarrow$ `Plan v2`）**：
   * 若运行中途因中间结果或缺口触发有界重排（`replan_count < max_replans`），冻结已完成步骤的 `Attempt` 与 `Artifact` 谱系，仅针对未执行部分展开生成 **`Plan v2` 快照**（`step_identity` 锚定“步骤稳定 ID + 计划版本号”而非全图总下标）；
   * 若 `Plan v2` 新引入了原确认单未覆盖的子方法或数据源连接，必须暂停进入 `WAITING` 重新申请用户确认，绝不静默沿用旧授权。
5. **诚实边界**：即时编排虽可安全跑通，但因未经过 `FormalTestSuite` 多用例测试与作者业务口径复核，仅作为用户自审自担的当次临时方案（缺底层工具时仍报 `missing_method` 缺口）。

---

## 六、第四段：回炉再造（KnowBench $\rightarrow$ KnowLab 正式定型闭环）

无论是第二段剪枝解决不了的问题、第三段即时编排跑通后希望长期复用的有效方案，还是运行中暴露的缺口与失败诊断，**一律不另建“沉淀复用”旁路，全部通过主稿 §2.8.3 的「回炉孵化」回到 KnowLab 正门**：

1. **沿既有孵化请求通道回传（不新建独立回炉服务）**：
   * 由 KnowBench 向 KnowLab 发送回炉孵化请求，经用户确认授权脱敏范围后，附带传递：原方法身份与版本（若有）、本次用户需求、运行期间形成的 `OrchestrationSketch` / 计划差异、以及结构化缺口诊断或失败证据。
2. **严格按权限分三条回炉去向**：
   * **原作者**：在原方法工作稿建新修订版本，展开器合入草图差异，如有未发布本地改动先做合并确认，不覆盖原已发布旧版；
   * **获准派生者**：创建带来源追溯的派生工作稿，重核跨方法接口、权限天花板与受影响承诺；
   * **仅有运行使用权者**：向原作者提交结构化改进需求单，或仅携带自己的问题需求与公开基础积木在 KnowLab 另起孵化（**严禁复制或泄露原方法作者的私有步骤正文与内部实现**）。
3. **重测冻结形成闭环**：进入 KnowLab 后沿第一段流程由作者审定清单、补齐 `FormalTestSuite` 测试覆盖并重新获取运行时验证回执，冻结发布为新版本；旧版在用任务不被强行中断，新任务经权限与预算复核后选用新版。

---

## 七、分阶段实施路线（Stage 0 $\rightarrow$ Stage 3）

| 阶段 | 核心工程交付 | 阶段验收标准 |
| :--- | :--- | :--- |
| **Stage 0：底座与积木前置** | 1. 平台基础积木提炼冻结（含读取/口径转换/核对计算/成稿）与共享 `meaning` 词表规范落地<br/>2. 基于 `formal_methods._sources()` 打通 MCP/Skill 封装成 `tool` 积木的向导（含前端 `ValueSlot` 可视化设置表单与 AI 自动起草槽位）<br/>3. `FormalOrchestrationExecution` 合流 `TurnDriver`，解除 `formal_method_plan.py` 对 `skill_instruction` 叶子与 `caller=="host"` 的硬限 | 平台基础积木与已封装 Skill/MCP 进入目录，无需手写 JSON 即可配置积木 `ValueSlot`；一个“MCP 取数 $\rightarrow$ 大模型分析 $\rightarrow$ MCP 计算”三步正式编排可完成测试并冻结为私有版本 |
| **Stage 1：第一段孵化闭环** | 1. 落地 `MethodCatalogEntry`、`OrchestrationSketch`、`elaborate()` / `decompile()`<br/>2. 打通 `knowbot-incubation` 正式方法通道与 `ProposalBundle`；支持 `Gap(missing_method)` 输出接口草案并回流制砖<br/>3. 上线「人话作业清单 + Diff 叠加 + 缺口待办」（暂不上图） | 以新财务专家为试点，从模板/创意起草、缺口补齐积木到测试冻结全程告别手写 `.json` |
| **Stage 2：第二/三段（剪枝、分支、即时编排与只读图）** | 1. `FormalTaskSnapshot` / `FormalHostCalls` 拆分用户任务通道<br/>2. 支持结构化/判定分支、`skipped` 账本与动态拓扑就绪调度<br/>3. 实现即时编排叶子级授权确认与 `Plan v1/v2` 快照重排<br/>4. 上线按需展开的**轻量只读拓扑图** | 正式方法支持条件分支与多候选剪枝；边界内即时编排可安全试跑且崩溃可续；只读图可定位分支与测试红绿状态 |
| **Stage 3：第四段回炉与专家团完善** | 1. 打通 KnowBench $\rightarrow$ KnowLab **回炉孵化**通道（含三种权限分流）<br/>2. 合入 `MemberRole` / `role_id` 契约，落实独立 `codex_thread_id` 与向下穿透分流规则<br/>3. 补齐覆盖率与来源审计后解除 `formal_methods.py:619` 仅限私有约束 | “第一次孵化 $\rightarrow$ 第二次剪枝 $\rightarrow$ 即时编排 $\rightarrow$ 回炉再造”四段全通；多角色专家团物理隔离可从执行记录核实并支持公开上架 |

---

## 八、待所有者拍板的 4 个关键决策

1. **即时编排开关节奏**：是否在 Stage 2 如期开放用户侧“边界内即时编排”，还是先仅用同一套图账本改造承接 Stage 2 的“正式专家多分支剪枝”，待试点稳妥后再对用户开放即时自由组合？
2. **条件分支判定方式**：`select_when` / `required_when` 是要求作者在草图阶段尽量配成确定性结构化谓词（推荐，零模型开销且可重放），还是默认允许宿主在遇到条件节点时调一轮有界模型做 `take / skip` 判定？
3. **共享 `meaning` 词表治理**：由平台制定受控 `meaning` 键值词表并作为工具方法入库门禁（推荐），还是只做宽松提示（会导致积木间难以自动连线）？
4. **平台基础积木归属**：Stage 0 开放给全平台作者引用的基础读取/计算/转换/成稿方法，由哪类平台官方账号孵化并承担维护升级？
