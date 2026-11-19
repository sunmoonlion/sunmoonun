# 专家与专家团架构再讨论（收敛共识版：角色定义、三类判据与正式方法契约对齐）

> **日期**：2026-11-16（吸收多轮讨论与代码走查修正后的共识讨论稿）  
> **对照依据**：[方法主稿](../专家孵化方案/luna/专家方法孵化与递归编排方案.md)，以及 `knowlab-app` / `knowbench-app` 正式方法契约源码（`formal_method.py`、`formal_method_generated.py`、`formal_method_compiler_generated.py`、`formal_method_plan_generated.py`、`advisor.py`）。  
> **状态**：讨论记录，不是现行方案。所有者尚未做最终拍板，本文**未改动正式方案或代码**。

---

## 一、前期讨论误区修正与核心边界收敛

经核对 `knowbench-app/knowbench-backend/app/app/domain/workbench/formal_method_generated.py` 与 `formal_method_compiler_generated.py` 源码，对讨论过程中出现的 **4 处偏差予以修正并收敛**：

1. **修正代码层落点（从运行期 `PlannedStep` 修正为冻结期 `FormalMethodDefinition`）**：
   - 上一版误把角色定义和三类判据挂在早期动态路径的运行期临时计划 `method_plan.py:PlannedStep` 上。
   - **事实**：方法类别（`tool` / `expert` / `expert_team`）在孵化冻结版本时即固定，真正执行分类的是 KnowLab 导出的 `formal_method_compiler_generated.py:classify_dependencies`，其输入是正式方法契约 `formal_method_generated.py` 中的 `Orchestration` 与 `MethodStep`。运行期 `PlannedStep.instance_id` 仅承载单次任务的调用实例映射，不是方法分类与角色定义的真源。
2. **修正分类判据（将“上下文隔离”从类别定义降为“必须声明成员角色的强制触发条件”）**：
   - 上一版直接用“开启独立上下文的实例数 $\ge 2$”定义专家团方法，存在三个漏洞：①“主上下文分析 + 1 个独立上下文复核”若只数非主上下文会漏判；② 同一专家对 10 个对象按项展开时，若为控制上下文长度开临时线程会被误升格为专家团；③ 纯确定性（无模型轮次）的跨专业分工无模型线程可数。
   - **修正后**：以**“冻结基准图中声明了 $\ge 2$ 个成员角色，或直接调用了已有专家团方法”**作为专家团方法的定义；同时把**“双盲独立分析 / 独立复核需隔离过程上下文”**作为**强制声明不同成员角色的触发条件**。
3. **如实标注运行时多上下文物理隔离的工程现状**：
   - 当前顾问主路径（`advisor.py`）与 `formal_model_execution.py` 均向单一 `task["thread_id"]` 发送轮次；为不同成员角色分配独立 `codex_thread_id` 属于**待单独立项实现的运行时新能力**，不能表述为“现有代码零成本加一个字段即可运行”。
4. **移除未立项的“群聊”夹带，恢复主稿 §2.8.3 原有四选项**：
   - 群聊（前台 `@角色` 点名直调、跨轮持久角色线程）不在现行方案范围内，且跨轮持久角色线程与现有“记忆归沙箱与职责、委托一次一结”的边界冲突，从本方案移除（是否立项由所有者另行决定）。
   - 二次编排或执行超出边界触发回炉时，当前委托的处置恢复为主稿 §2.8.3 原有的四个选项（等待、按明确标识的用户修改计划继续、接受允许的部分交付、结束）。

---

## 二、收敛后的核心概念：身份、成员角色与执行上下文

采用“方法身份 / 成员角色 / 执行上下文”三分法（命名用“成员角色”以避开主稿 §1.6 已有的 `resource_role` 资源角色）：

| 概念 | 定义与归属 | 生命周期与判别标准 |
| :--- | :--- | :--- |
| **1. 方法身份**<br/>（Method Identity） | 方法不随调用场合改变的静态定义：`method_id`、`version`、`digest`、作者、名称与五要素两视图。“专家”“专家团”是方法身份面向用户的称呼。 | **跨方法独立存在**：换一个上层方法它依然存在，有自己的版本，可独立上架、被请用或被多个上层方法引用。 |
| **2. 成员角色**<br/>（Member Role） | 上层组合方法在冻结基准图（`Orchestration`）中声明的一个**职责位置**，规定在本次组合中由哪类方法承担、负责什么范围、可见哪些上游产物、是否要求隔离过程上下文。 | **仅在声明它的上层方法内存在**：随上层方法版本一起冻结，没有独立商品 ID，不能单独上架或被外部直接点名调用。 |
| **3. 执行上下文**<br/>（Execution Context） | 运行时资源（如沙箱中的 `codex_thread_id` 与工作目录），由 KnowBench 执行端根据成员角色的隔离要求在运行期分配。 | **纯运行时资源**：不出现在静态方法定义中，也不直接按运行时线程开启次数决定方法类别。 |

---

## 三、三类方法的严格判据与强制声明规则

### 3.1 三类方法定义与编译器判据

| 方法类别 | 定义与编译器核定规则 | 执行路径 |
| :--- | :--- | :--- |
| **工具方法**（`tool`） | 在平台可治理的方法调用边界内**不调用任何其它注册方法**，做法为 `ToolProcedure`（固定实现绑定）。 | 直接派发到实现 |
| **专家方法**（`expert`） | 做法为 `Orchestration`（至少调用一次下层方法），且冻结基准图中**声明的成员角色数 $\le 1$，同时未调用任何专家团方法**。 | 统一编排执行 |
| **专家团方法**（`expert_team`） | 做法为 `Orchestration`，且满足以下任一条件：<br/>① 冻结基准图中**声明了 $\ge 2$ 个成员角色**；<br/>② 任意步骤的候选方法（`candidates`）中包含已有的**专家团方法**。 | 与专家方法共用同一编排引擎 |

### 3.2 什么情况下必须声明不同的「成员角色」？（堵住纯自愿声明漏洞）

为防止作者在应当分角色时漏标、或在纯串行步骤上随意虚标角色操纵类别，规定以下**客观触发与约束规则**：

1. **强制声明触发条件（满足任一条，必须在基准图中声明为不同成员角色）**：
   - **条件 A（双盲 / 独立分析隔离）**：步骤 A 与步骤 B 在分析阶段要求互不见对方的未定稿结论与过程上下文；
   - **条件 B（独立复核隔离）**：步骤 B 负责对步骤 A 的产出进行复核/质询，且要求复核方不得看到被复核方的中间推理上下文（仅能通过 `StepValue` 接收 A 已验收的正式产出）；
   - **条件 C（跨专业分工声明）**：上层方法对外能力声明中承诺了多个不同专业职责的分工协同。
2. **禁止虚标约束**：
   - 两个成员角色之间必须存在明确的**职责分工、独立分析汇合或复核/质询关系**；无分工关系的纯顺序工具调用不得拆标为多个成员角色。
   - **按项展开不增加成员角色**：同一成员角色对 $N$ 个对象执行有界按项展开（或仅为控制上下文长度开启临时线程），在定义中仍只是 **1 个成员角色**，方法类别仍为**专家方法**。

### 3.3 典型场景判例对照表

| 场景 | 原主稿判据（数不同专家 `method_id`） | 收敛方案判据（数冻结成员角色） | 判定理由 |
| :--- | :--- | :--- | :--- |
| 1. 读数工具 $\rightarrow$ 计算工具 $\rightarrow$ 成稿工具（同上下文） | 专家方法 | **专家方法** | 无多成员角色分工（0 或 1 个默认角色）。 |
| 2. 两个工具方法分支各自独立分析（双盲隔离）$\rightarrow$ 第三步交叉复核 | 专家方法（误判） | **专家团方法** | 命中触发条件 A 与 B，须声明 $\ge 2$ 个成员角色。 |
| 3. 同一个财务专家方法分饰“正方”与“反方”双盲对抗 $\rightarrow$ 汇总 | 专家方法（误判） | **专家团方法** | 虽复用同一 `method_id`，但命中条件 A 声明了正方、反方 2 个成员角色。 |
| 4. 主分析角色产出初稿 $\rightarrow$ 独立复核角色隔离过程上下文做复核 | 若复用同一方法则误判为专家方法 | **专家团方法** | 命中触发条件 B，包含主分析与独立复核 2 个成员角色。 |
| 5. 同一财务专家处理 10 家公司（即使运行时各开临时线程省上下文） | 专家方法 | **专家方法** | 仅 1 个成员角色按项展开 10 个实例，不增加成员角色数。 |
| 6. 财务专家角色 + 法律专家角色分工分析后再汇总 | 专家团方法 | **专家团方法** | 声明了财务与法律 2 个成员角色。 |
| 7. 调用一个已有专家团方法后再调用成稿工具方法 | 专家团方法 | **专家团方法** | 直接依赖中包含 `expert_team`，向上传播。 |

---

## 四、对齐 `formal_method_generated.py` 的精确契约设计与穿透规则

### 4.1 为什么不需要在 `MemberRole` 里重复定义 `candidates / inputs / outputs`？

核查 `formal_method_generated.py`（第 148–165 行）现有的 `MethodStep` 模型：

```python
class MethodStep(Strict):
    id: Name
    candidates: tuple[MethodRef, ...] = Field(min_length=1, max_length=100)
    select_when: Text
    required_when: Text
    always_required: bool = Field(strict=True)
    depends_on: tuple[Name, ...] = Field(max_length=100)
    inputs: dict[Name, StepInput] = Field(max_length=100)   # 已支持 CallerValue | StepValue | LiteralValue | ResourceValue
    outputs: dict[Name, ValueSlot] = Field(min_length=1, max_length=100)
    on_failure: Literal["pause", "fail"]
```

可以看到：
- **承担者候选**已经在 `MethodStep.candidates` 上；
- **负责范围参数（如立场字面量 `LiteralValue`）与可见上游成果（`StepValue`）**已经在 `MethodStep.inputs` 与 `depends_on` 上；
- **交付物**已经在 `MethodStep.outputs` 上；
- 而且在编排中，**同一个成员角色往往需要连续执行多个步骤**（例如“主分析员角色”先执行步骤 1 读取转换，再执行步骤 2 测算撰稿；然后交给“独立复核员角色”执行步骤 3 复核）。

因此，在 KnowLab 正式方法契约（`formal_method_generated.py`）中最干净、零重复的落点是：**在 `Orchestration` 上声明轻量的 `roles: tuple[MemberRole, ...]`，并在 `MethodStep` 上通过 `role_id` 引用所属成员角色**：

```python
class MemberRole(Strict):
    id: Name                                # 本方法定义内唯一的成员角色 ID（如 "bull_analyst", "independent_reviewer"）
    name: Text                              # 面向用户与看板展示的角色名称（如 "正方财务分析员"）
    responsibility: Text                    # 该成员角色在本次组合中的职责范围说明
    isolated_context: bool = Field(strict=True)  # 是否要求在独立于其它成员角色的执行上下文中运行

class MethodStep(Strict):
    id: Name
    role_id: Name | None = None             # 【新增】本步骤归属的成员角色 ID（引用 Orchestration.roles[].id）
    candidates: tuple[MethodRef, ...] = Field(min_length=1, max_length=100)
    select_when: Text
    required_when: Text
    always_required: bool = Field(strict=True)
    depends_on: tuple[Name, ...] = Field(max_length=100)
    inputs: dict[Name, StepInput] = Field(max_length=100)
    outputs: dict[Name, ValueSlot] = Field(min_length=1, max_length=100)
    on_failure: Literal["pause", "fail"]
```

并在 `Orchestration.valid()` 与 `formal_method_compiler_generated.py` 中增加三条静态校验：
1. **引用存在性**：若 `step.role_id` 非空，必须命中 `Orchestration.roles` 中已声明的 `MemberRole.id`；若 `len(roles) >= 2`，则每个步骤（或所有非纯汇出步骤）必须显式标明 `role_id`，且每个声明的 `MemberRole` 至少被一个步骤引用（防止声明空壳角色凑数升类）。
2. **可见范围与隔离墙一致性**：归属 `role_id = R_B`（且 `isolated_context = True`）的步骤，其 `inputs` 中的 `StepValue` 只能引用已声明在 `depends_on` 中的前序步骤正式输出槽；运行时执行端保证 `R_B` 不会共享 `R_A` 的模型会话上下文。
3. **编译器分类替换（`classify_dependencies`）**：
   ```python
   def classify_dependencies(
       implementation: Literal["direct", "orchestration"],
       dependencies: tuple[tuple[UUID, Kind], ...],
       role_count: int = 0,
   ) -> Kind:
       if implementation == "direct":
           if dependencies:
               raise ValueError("A tool method cannot call another method")
           return "tool"
       if not dependencies:
           raise ValueError("An orchestrated method must call at least one method")
       if any(kind == "expert_team" for _, kind in dependencies) or role_count >= 2:
           return "expert_team"
       return "expert"
   ```

### 4.2 角色参数与独立上下文的「向下穿透分流规则」（保留共识项）

当某个步骤绑定了成员角色 `role_id`、并通过 `StepInput(binding=LiteralValue(...))` 传入了角色立场/范围参数（如 `stance="conservative"`）时：
1. **立场参数必须走被调方法显式声明的输入槽（`ValueSlot`）**：使被调方法内部的 `required_when` 条件分支与 `ValidationRule`（`how_to_validate`）随该输入参数合法联动，禁止用未声明的自由提示词强行覆盖静态必做校验。
2. **确定性计算工具严禁被角色立场污染**：当该成员角色调用的下层方法展开子图时，角色专属的独立 `codex_thread_id` 与立场参数**仅作用于二次编排规划轮及 `implementation.kind == "skill_instruction"`（指令型模型推理工具方法）**；而 `platform` / `skill_script` / 确定性查数与公式计算工具方法不切私有模型线程、不接收立场倾向，确保客观数据与算术结果在任何角色下 100% 一致。

---

## 五、分阶段落地清单（严格区分“契约/文档修订”与“运行时新能力建设”）

| 阶段 | 修改位置 | 具体工作内容 |
| :--- | :--- | :--- |
| **第一阶段：主稿修订** | [专家方法孵化与递归编排方案](../专家孵化方案/luna/专家方法孵化与递归编排方案.md) | 1. 在 §1.1 前新增“方法身份、成员角色与执行上下文”定义；<br/>2. 修改 §1.1 专家团方法判据为“声明 $\ge 2$ 个成员角色或调用已有专家团方法”，写入强制声明触发条件与示例表（本文 §3.1–3.3）；<br/>3. 在 §2.1 步骤定义中增加 `role_id` 引用，在 §2.10.1 中将上下文隔离要求挂接到 `MemberRole.isolated_context` 及向下穿透分流规则；<br/>4. 写明“预先冻结步骤图”的架构取舍（换取可预期、可审计，越界走 §2.8.3 回炉與四选项）。 |
| **第二阶段：正式方法契约与编译器更新（M0）** | `knowlab-app` 导出源 $\rightarrow$ `knowbench-app` `formal_method_generated.py` & `formal_method_compiler_generated.py` | 1. 在 KnowLab 正式方法 Schema 的 `Orchestration` 中增加 `roles: tuple[MemberRole, ...]`，`MethodStep` 增加 `role_id`；<br/>2. 更新 `classify_dependencies` 按 `role_count >= 2` 或含 `expert_team` 依赖判类；<br/>3. 运行 `scripts/export_formal_method.py` 同步生成契约与编译器代码（严禁手改生成物）。 |
| **第三阶段：运行时多角色物理隔离能力建设（M3）** | `knowbench-app`（`advisor.py`、`formal_model_execution.py` 等） | 单独立项实现：按 `MemberRole.isolated_context` 为不同成员角色分配并管理独立的沙箱 `codex_thread_id` 与工作目录隔离。**在该能力实现并验收前，主稿 §2.10.1 的物理上下文隔离标记为待实现，不声称现有运行器已具备。** |
