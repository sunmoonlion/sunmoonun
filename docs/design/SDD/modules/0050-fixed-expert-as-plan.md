# 固定专家也表示成一份计划（0050）

> 状态：**草案，等所有者看**（Opus 2026-11-06 写；[接手计划](../../../总纲/opus接手计划-2026-11-06.md)第 8 项，[审查](../../../总纲/luna开发逐文件审查-2026-11-06.md) A1）。所有者看过、第七节三条定了再动代码。
> 上位决定：[方法架构 11-03](../architecture/methods.md#2026-11-03-最新决定保留固定财务专家统一执行体系)——固定计划与动态计划长期共用执行体系；固定顺序是「完全约束的计划，不需要额外模型规划，也不允许模型自行删改作者指定步骤」；等价迁移验收通过后才清旧执行代码；不静默改钉正在执行的任务。落实账 [K31](../../knowbot-todolist.md#k31-执行与验收)。

## 一、现在的样子（knowbench-backend，2026-11-06 头 `c7d3d14d`）

`ExecutionPlan(pack, receipt)` 已经是一个视图，状态机、账本、尝试、产出只有一套。但「有没有计划回执」本身成了开关：固定专家 `receipt=None`，动态专家带模型规划出来、用户接受过的回执。下面这些地方按它分两路：

| 文件 | 处数 | 分开做的事 |
| --- | --- | --- |
| `application/workbench/advisor.py` | 7 | 受理时取包还是取目录；要不要先规划；取输入（固定按名字取最新版本，动态 `open_method_step` 按已接受的谱系）；开尝试（固定 `meta={"reworks":n}`，动态 `_meta`）；验收后复核计划没变；第 0 步没有数据工具时（固定照做，动态失败）；收尾（固定取最后一步的产出、列全部 artifact，动态按 `final_outputs`、列已接受的结果） |
| `application/workbench/expert_desk.py` | 5 | 页面的步骤、计划历史、最终产出、方法阶段 |
| `application/workbench/test_runs.py` | 2 | 测试取值（v1 按名字，v2 按方法实例） |
| `application/workbench/runner.py` | 2 | 工具策略来源；当前尝试是不是 `method_step` |
| `application/workbench/method_tools.py` | 2 | 工具调用要不要核 turn 元数据（只有动态核） |
| `application/workbench/acceptance_numbers.py` | 1 | 「覆盖」类数值验收的上游（固定取最新，动态取本次尝试的输入） |
| `application/workbench/execution_plan.py` | 6 | `current_artifacts`、`final_results` 等对固定返回空或另取 |

固定专家有两种来源：内置包（`SMOKE`、`INCUBATE`、`FIND_EXPERT`，`find_pack` 取，委托上没有快照）与 knowmart 交付的 `knowbot-manifest/v2` 分身（财务分析与预测就是这种，`pack_from_manifest` 解出 `ExpertPack` 存进 `pack_snapshot`）。knowlab 编译 v2 时已保证每步产出名等于步骤 id、`input_refs` 只指前面的步骤、`back_to` 只指前面的步骤（`knowlab-backend/app/app/domain/knowbots/compile.py` 170、1002、1012 行）；内置包也都满足。knowbench 自己的 `ExpertPack` 不核这一条。

## 二、做法：平台替作者写一份「固定计划」回执

**固定专家受理通过时，平台按作者的顺序确定性地生成一份计划回执，之后执行只认回执，不再问是哪种专家。**

| 项 | 固定计划 | 对照：动态计划 |
| --- | --- | --- |
| 契约 | `knowbench/fixed-plan/v1`（新，和 `method-plan/v1`、`v2` 并列进 `AnyMethodPlan`） | `knowbench/method-plan/v1`、`v2` |
| 谁写 | 平台，按 `pack.workflow` 顺序；不调模型、不花预算 | 规划模型，用户接受 |
| 步骤 | 每步 `instance_id = method_id = step_id`，`tools = step.tools`，`reason` 写「作者指定的第 n 步」 | 模型选 |
| 输入 | `input_refs` 里每个名字绑到**前面最近一步产出它的**那一步 | 模型按槽绑 |
| 最终产出 | `{最后一步 step_id: 最后一步 step_id}` | 作者 `final_units` |
| 改计划 | 不许：`max_replans = 0`，回执只有第 1 版 | 按作者上限 |
| 留痕 | 同动态：`__method_plan__` 第 1 版 artifact + 一次 `step_id=__method_plan__` 的平台尝试（预留与花费都是 0、没有 turn），保持「每份回执都有一次尝试」 | 规划尝试 |

**产出名不变。**执行时取产出名一律读 `view.pack.workflow[i].output_artifact`，不再直接拼 `output_name(instance_id)`。动态的 `project_plan` 本来就把 `output_artifact` 设成 `output_name(instance_id)`，所以动态不受影响；固定的产出仍叫作者起的名字（如 `plan`、`answer`），knowlab 测试里按名字写的断言、页面、报告都不用改。

**固定专家不做投影。**`ExecutionPlan.pack` 就是原包，`ask_before`、`output_file`、`tool_policy`、`dossier`、`max_backs` 这些动态目录不支持的字段照旧生效。固定计划不走 `validate_composition`（那是给目录里的方法单元用的，要求必有的三条验收、产出名等于 id，固定包不一定满足），另写 `validate_fixed_plan(pack, plan)`：步骤与 workflow 一一对应、输入都绑到前面的步骤、`back_to` 在输入里。

`ExecutionPlan.dynamic` 改成 `planned_by: Literal["author", "model"]`，只在**页面要不要显示计划栏**和**要不要规划**两处用；执行、验收、收尾、测试取值都走回执一路。

## 三、两路收成一路后，固定专家行为上的变化

按 11-03「等价迁移」的要求，逐条列出来，第七节请所有者定能不能接受。

| # | 地方 | 现在固定专家 | 改了以后 | 判断 |
| --- | --- | --- | --- | --- |
| 1 | 取输入 | 按名字取**最新版本** | 按已接受的前缀谱系：上一步最后一次成功尝试的那一版 | 正常路径一样；返工、退回后多出的旧版本不会被误取。**更严** |
| 2 | 工具调用 | 不核 turn 元数据 | 核（`method_tools.py` 现在只对动态核） | 沙箱照常带元数据时一样；不带就拒。**更严**，要在等价验收里跑真沙箱 |
| 3 | 第 0 步没有数据工具 | 跳过数据确认，照做 | 不变：改按包上的「数据确认可不可省」判断，不再按动态与否 | 一样 |
| 4 | 交回的「已核实」清单 | 委托下全部 artifact | 已接受的各步结果 | 清单变短、不再含旧版本与数据确认件。**用户看得到** |
| 5 | 页面 | 没有计划栏 | 不变（`planned_by="author"` 不显示） | 一样 |
| 6 | 测试取值 | v1 按名字 | 不变：产出名没变，按名字取的仍是同一份 | 一样 |
| 7 | 开尝试的 `meta` | `{"reworks": n}` | `_meta` 加上 `reworks` | 一样（多几项可查的字段） |

## 四、切换与迁移

- **只对新委托。**进行中的固定委托没有回执（`accepted_plan_version` 为空），照旧路走到结束；不给它们补回执（补了会改钉正在执行的任务）。
- **开关**：后端配置 `WORKBENCH_FIXED_AS_PLAN`，默认关；关时一切照旧。开了以后新受理的固定委托生成回执。
- **生成不了就走旧路**：老的 v2 分身里 `input_refs` 指向没有哪一步产出的名字、或 `back_to` 不在输入里，生成失败时记一条告警、这件委托照旧路，不让它失败（替代路径未验收前保持原产品可用）。
- **几处要放宽成两种回执都认**：`validate_receipt` 现在会调 `catalog_for_task`（固定专家没有目录）；`pack_digest` 内置包委托上没有，生成时按包的 JSON 算一个存进委托；`accepted_results` 的 `_meta` 比对改按回执的契约取。
- **旧路退役**：开关打开后，线上已没有无回执的进行中固定委托，且第五节验收通过，所有者批准后，删旧路（advisor 等里面 `receipt is None` 的分支、`is_dynamic` 改名或删）。

## 五、等价验收（K31 列的五项）

真库测试用假的驾驶器（同 `test_step_progress_db.py` 的做法），同一位固定专家、同一道题，开关前后各跑一次，比对：

| 项 | 比什么 |
| --- | --- |
| 等价执行 | 步骤顺序、每步输入的名字与版本、返工与退回次数、每步验收结论、最终产出的名字与内容摘要 |
| 授权取数 | 第 0 步数据确认的提法、确认后取到的引用、运行授权 |
| 报告 | 交回内容（除第三节 #4 的清单外逐字段一致）、成稿文件、页面步骤视图 |
| 手选 | 用户指定这位专家时受理、开跑一样 |
| AI 匹配 | 找专家（声明选择 v4）选中它时一样 |

另跑：返工一次、退回一次、开步前提问、用户中途停下、预算用尽、链路断开恢复，各一条。线上再用财务分析与预测跑一道保底题（本地卡）。

## 六、不做的

不改 `knowbot-manifest/v2` 与 knowlab 编译；不让固定专家调规划模型；不改产出名；不给已有委托补回执；不改动态计划。

## 七、请所有者定

1. 第三节 #4：固定专家交回的「已核实」清单变成「已接受的各步结果」，能不能接受。
2. 开关打开的时机：等价验收在远程真库跑通后，随下一批发版开；还是先在测试环境开一段。
3. 旧路退役条件按第四节最后一条，可不可以。

## 八、做的顺序

1. 领域层：`fixed-plan/v1` 模型、`fixed_plan(pack)` 生成、`validate_fixed_plan`；产出名改读 `pack.workflow`。
2. 应用层：受理通过时生成回执（开关）；`validate_receipt`、`accepted_results` 认两种回执。
3. 把第一节各处的分支改成按回执走（每改一处，开关关时的现有测试全过）。
4. 第五节等价验收测试。
5. 本地卡：测试环境开开关，跑保底题。
