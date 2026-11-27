# 方法模板（五要素+两视图）、递归编排引擎与三端市场全栈重构定稿方案（Carbon 代码实证完整版）

- **工作位置**：本地 `wsl-dev`（本地路径 `/home/zymun/worktrees/luna/sunmoonun/专家方法孵化和编排重构-carbon.md`，远程挂载路径 `/home/zym/wsl-worktrees/luna/sunmoonun/专家方法孵化和编排重构-carbon.md`）
- **审视深度与覆盖基线**：基于 `luna` 工位四套应用全栈源码（`knowlab-backend`、`knowlab-web-frontend`、`knowbench-backend`、`knowbench-web-frontend`、`knowmart-backend`、`knowmart-web-frontend`、`knowmart-admin-frontend`、`knowbase-backend`、`provisioner` 及 `sunmoonun/ci/{verify-contracts.py, method_transaction_guard.py}`）逐行精读，并完整吸收合并 [一周代码评审.md](file:///home/zym/wsl-worktrees/luna/sunmoonun/%E4%B8%80%E5%91%A8%E4%BB%A3%E7%A0%81%E8%AF%84%E5%AE%A1.md) 查实的 `W01–W10` 生产级缺陷与 `#121/#122/#123` 现场根因后重铸定稿；本文档严格保持只读审计与设计输出，未修改任何业务源码或分支状态。

---

## 零、 顶层本体论、三端全域版图与平台红线锚定

### 0.1 结构正本清源：“整体与局部”本体统一 + “孵化—运行—市场”三端闭环

本次全栈重构绝不是单点修补编排器，而是围绕**同一份正式方法契约生命体（五要素 + 两视图）**，在**本体结构（整体与局部）**和**产品平面（KnowLab ⇄ KnowBench ⇄ KnowMart 左边栏与市场全链路）**两个维度同时完成彻底重铸：

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│        【统一契约本体：方法模板（五要素 + 程序自动派生两视图）】—— 工具方法与专家方法同构          │
│                                                                                                    │
│  ① 能力声明 (capability_declaration) ── 解决什么问题、适用/排除边界、具名承诺与预期语义槽          │
│  ② 所需权限 (access_requirements)    ── 四类受管能力域、字段收窄、条件生效 (when_selected) 与委派  │
│  ③ 如何做   (procedure)              ── ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│                                          ┃ 【局部核心实现机制】                                   ┃ │
│                                          ┃ • 工具方法：固定实现绑定 (ToolProcedure)               ┃ │
│                                          ┃ • 专家方法：四正交控制原语 + 正交治理属性              ┃ │
│                                          ┃   (sequence / parallel_join / branch /                 ┃ │
│                                          ┃    bounded_loop + 盲审隔离/包络审批/缺项策略)          ┃ │
│                                          ┃   的五要素制导 HTN 递归规划与受控前沿惰性执行引擎      ┃ │
│                                          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│  ④ 如何校验 (how_to_validate)        ── 可执行 V0 确定性核验算子 + 盲审门禁 + 试跑断言覆盖         │
│  ⑤ 什么要批 (what_requires_approval) ── 立项包络一次预授权 (envelope) vs 外部写/发逐次批准         │
│ ────────────────────────────────────────────────────────────────────────────────────────────────── │
│  【由五要素纯函数实时派生的两视图（严禁手工双写，创作—编译—运行—市场展示全程双向守恒）】           │
│   📥 视图 A：对外输入视图 (public_inputs)             📤 视图 B：对外返回视图 (what_to_return)     │
└───────────────┬───────────────────────────────────┬────────────────────────────────────┬───────────┘
                ▼                                   ▼                                    ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐   ┌────────────────────────────┐
│  平面 A：KnowLab 作者孵化端   │   │  平面 B：KnowBench 消费运行端 │   │ 平面 C：KnowMart 供需市场端│
│ • 4 栏精简左边栏导航          │   │ • 左边栏底部「方法与技能」    │   │ • 终结旧 v3 与正式方法双轨 │
│ • /studio 一体化五要素工作坊  │◄─►│   重构为 3 栏清晰消费/环境视图│◄─►│ • 公开五要素+两视图详情页  │
│ • /methods 统一作者方法与源   │   │ • 隐藏裸 SHA256 与底层协议词  │   │ • 双层类目解耦 + 店铺合一  │
│   （内联代理登记脚本/指令源） │   │ • formal-handoff/v2 直生五要  │   │ • 接入定价/成交/评价/需求单│
│ • 一键自用同步或送审公开市场  │   │   素草稿或带契约跳市场发需求  │   │ • 补齐后台审核/撤证/下架   │
└───────────────────────────────┘   └───────────────────────────────┘   └────────────────────────────┘
```

1. **明确废弃的两条历史弯路**：
   - **不搞“多级变量逐层固化动态继承树 `T = (D, V, C)`”**：逐变量多级模板继承在真实工程中过度抽象且维护失真（对齐主稿 [专家方法孵化与递归编排方案.md](file:///home/zym/wsl-worktrees/luna/sunmoonun/docs/%E6%80%BB%E7%BA%B2/%E4%B8%93%E5%AE%B6%E6%96%B9%E6%A1%88%E8%AE%BE%E8%AE%A1/%E4%B8%93%E5%AE%B6%E5%AD%B5%E5%8C%96%E6%96%B9%E6%A1%88/luna/%E4%B8%93%E5%AE%B6%E6%96%B9%E6%B3%95%E5%AD%B5%E5%8C%96%E4%B8%8E%E9%80%92%E5%BD%92%E7%BC%96%E6%8E%92%E6%96%B9%E6%A1%88.md#L1575) §4.3 结论）；
   - **不搞“领域步骤/工作流模板库（如 `C01–C15`、`T-A~T-P` 或 `P1–P5`）”**：局部步骤组合已被**四正交控制原语 + 递归规划/执行**彻底替代，且平台内置金融步骤模板直接触碰 `C-L1` 合规红线。
2. **本次全栈重构必须闭环解决的四大核心任务**：
   - **任务一（重构整体——五要素+两视图方法模板）**：推翻残缺锁死的 `checked_delivery/v1` 四文本框假模板与重复的 `RequestForm` 创意六问，落地**【静态契约基座（`S1–S4` 纯工程起草样板）+ 受控跨要素动态联动（`project_contract_state` 纯函数实时双向守恒）+ 结构化 `C-L1` 出处账本】**；
   - **任务二（有机整合整体与局部——五要素统摄要素 ③ 递归规划与执行）**：解除四正交原语与内核 `strict_plan` 盲审的全局互斥锁，落地主稿 §2.2 四项封闭值处理、五要素契约自顶向下制导 HTN 规划、分形缺口原位派生回填、包络预授权与受控前沿惰性执行；
   - **任务三（重构 KnowLab 与 KnowBench 左边栏及“方法与技能”中心）**：厘清作者孵化台与消费运行环境的职责边界（`C-T1`），消除 9 栏旧申请单与 6 页签底层调试倾倒场带来的跨端折返跑，统一三端 `CrossAppLink`（`destinations.ts`）与 `formal-handoff/v2`；
   - **任务四（重构 KnowMart 前后端全链路）**：终结旧 `Knowbot (SCHEMA_V3)` 与 `FormalListing` 的严重双轨割裂，补齐正式方法公开五要素+两视图契约投影、目录卡片/详情页/请专家/获取工具闭环、资质类目与发现类目解耦、小店展示与卖家中心合一、需求大厅响应与成交评价留痕，以及 `knowmart-admin-frontend` 审核台与资质撤销/过期/违规下架合规闭环。

### 0.2 平台硬约束逐条对齐检查表（对照 [`constraints.md`](file:///home/zym/wsl-worktrees/luna/sunmoonun/docs/design/rules/constraints.md#L1-L185)）

| 规则编号 | 平台硬约束核心要求 | 本定稿方案的底层落点（确保零违背） |
| :--- | :--- | :--- |
| **`P0` / `C-D11`** | 状态机严格保持 `Task / Attempt` 两层，不得新增状态词；账房在 PostgreSQL | **零新增 `TaskState` / `AttemptState` 枚举值**；前沿调度游标与跳过节点集作为结构化字段存于任务/调用账本 |
| **`C-T1`** | 四套应用职责边界清晰：KnowLab 管孵化测试、KnowBench 管使用与运行环境、KnowMart 管市场与资质、KnowBase 管资料 | KnowBench 左边栏“方法与技能”聚焦**消费使用与本地运行环境源管理**；KnowLab 聚焦**五要素创作、测试与冻结**（通过受控服务边界代理读写作者源，不越界存运行凭证）；KnowMart 聚焦**公开契约展示、资质核验、供需撮合与交易留痕**（绝不暴露私有要素 ③ 内部步骤与提示词） |
| **`C-A9`** | 后端/Supervisor 绝不直调大模型；语义规划与判断一律派沙箱 Codex `Attempt` | 5ms 逆向超图可达性与 V0 核验算子均为**纯确定性 Python 代码**；HTN 规划与指令叶子均在用户沙箱/受控路由内作为 `Attempt` 执行 |
| **`C-A10`** (`AT-12`) | 首期策略关闭同一 `Task` 下多活跃并行 `Attempt`（`active_attempt_id` 唯一），预算硬停进 `WAITING(RESOURCE)` | **严守单 `Task` 单 `active_attempt_id` 账房不变量**！采用拓扑确定性就绪前沿（`FrontierState`）+ `SKIPPED_BY_GUARD` 惰性剪枝 + `$O(1)$` 产物索引，补齐 `INCUBATE / FIND_EXPERT` 流式预算硬熔断 |
| **`C-D6 / C-D7` + 跨服务事务铁律** | 每个 App 单链线性 Alembic 迁移并同步登记 `test_kernel_invariants.py`；严禁持 DB 事务锁发起跨服务 HTTP（[`method_transaction_guard.py`](file:///home/zym/wsl-worktrees/luna/sunmoonun/ci/method_transaction_guard.py)） | KnowLab、KnowBench、KnowMart 各走单链线性 `expand` 迁移（JSONB 生成列全加 `jsonb_typeof` 防御），保留 `source_workdraft_id` 外键；所有跨端源代理、目录核权、上架同步与成交留痕一律在事务块外调 HTTP |
| **`C-C3..C-C5` / `C-C10`** | 真源在提供方仓，消费方持生成副本与锁，DTO 一律 `extra="forbid"`，双端同测 | 严格通过 [`export_formal_method.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/scripts/export_formal_method.py#L31-L187) 与 [`export_method_capabilities.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/scripts/export_method_capabilities.py#L1-L50) 生成消费端代码/Schema/锁，通过 [`verify-contracts.py`](file:///home/zym/wsl-worktrees/luna/sunmoonun/ci/verify-contracts.py#L47-L187) 门禁 |
| **`C-L1 / C-L4 / C-L5`** | 平台只供工程结构不带投资逻辑/阈值；**每条规则来源留记录**；公开按资质审核、撤证/过期即刻下架；禁违规词 | `S1–S4` 样板零金融判断阈值；逐要素结构化出处账本防未确权建议入库；补齐 KnowMart `FormalListing` 的运营审核台、`flagged()` 违禁词扫描、撤证/过期自动回撤与违规下架留痕 |

---

## 一、 全栈四仓底层源码逐行深审：34 项真实代码级病灶清单（`M01–M08` + `R01–R08` + `X01–X08` + `W01–W10`）

经对 KnowLab、KnowBench、KnowMart、KnowBase 四仓前后端核心实现逐行核查，并融合 [一周代码评审.md](file:///home/zym/wsl-worktrees/luna/sunmoonun/%E4%B8%80%E5%91%A8%E4%BB%A3%E7%A0%81%E8%AF%84%E5%AE%A1.md) 实证结果，现行系统存在以下 **34 项精确到文件、函数与行号的底层机制冲突与运行缺陷**：

### 1.1 整体层（五要素 + 两视图 + 出处与核权账本）八大底层硬伤（`M01–M08`）

1. **`M01` — 静态模板退化为 4 个裸字符串的 `checked_delivery/v1` 残壳，锁死编辑且与 `KnowbotRequest` 四重撞车**
   - **代码实证**：[`workdraft.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/workdraft.py#L357-L385) 中 `MethodTemplate` 仅硬编码 `template: Literal["checked_delivery/v1"]` 与 `goal / deliverable / check / evidence` 四个裸字符串；[`formal_methods.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/application/services/formal_methods.py#L915-L936) 一旦检测到 `body.method_template` 非空即锁死 `purpose` 与 `template_delivery`（稍作修改即抛 `method_template_locked`，逼作者调 `clear_method_template` 连同已编排的 `formal_method` 一并销毁）。同时前端仍保留 [`request-form.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/request-form.tsx#L365-L480) 创意六问让作者重复填写同一业务目标。
2. **`M02` — 局部反噬整体：`selection.py:expand()` 竟直接克隆最后一个子工具的五要素定义给父专家**
   - **代码实证**：[`selection.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/selection.py#L453-L511)（及生成副本 [`incubation_selection.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/incubation_selection.py#L453-L511)）写死 `final = tools[tail.method].definition; doc = final.document()`，把末尾子工具的整份五要素定义拷作根专家底稿，`exports` 仅导出末尾步骤产出；当 `len(selection.steps) > 1` 且带 `template` 时清空子步承诺与校验，不带 `template` 时（如 [`temporary_plan.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/temporary_plan.py#L107-L130)）直接把末尾局部工具的适用边界当成整包专家的边界。
3. **`M03` — 单一 `FormalMethodDefinition` 造成“先有要素 ③ 才能填要素 ①④”的鸡生蛋死锁**
   - **代码实证**：[`formal_method.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/formal_method.py#L617-L657) 的 `consistent()` 强校验 `conditions[p].input_slots <= views["inputs"]` 且 `ValidationRule.outputs <= views["outputs"]`，而 `views` 只能由要素 ③ 算出。结果在要素 ③ 编排出来前无法实例化合法定义，迫使 [`formal-method-editor.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/formal-method-editor.tsx#L700) 用 `{definition ? (...) : null}` 将要素 ①②④⑤ 全部隐藏。
4. **`M04` — `C-L1` 出处校验绑死扁平文本格与脆弱字符偏移，且 `knowbot_method_version` 强外键依赖 `knowbot_workdraft`**
   - **代码实证**：[`models/knowbots.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/infrastructure/models/knowbots.py#L928-L931) 中 `KnowbotMethodVersion.source_workdraft_id` 持有指向 `knowbot_workdraft.id` 的 `RESTRICT` 非空外键；[`formal_methods.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/application/services/formal_methods.py#L830-L845) 在校验与冻结前必调 [`workdraft.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/workdraft.py#L518-L870) `source_problems()` 核对 `knowbot_workdraft_record` 或 `idea:<ver>:<start>+<len>` 切片。必须原位结构化升级 `knowbot_workdraft` 而非断链另起炉灶。
5. **`M05` — 要素 ② 权限目录残缺、委派深度硬锁 `1` 跳，且存在致命“公私叶子交付死锁”**
   - **代码实证**：
     - ① [`method_capabilities.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/method_capabilities.py#L138-L196) 导出的 `AuthorCapabilityCatalog` 漏掉运行时已支持的 `knowbase:read_method_input` 与 `isolated-script:execute`，且 `AccessRequirement` 锁死 `required_when="always"`，[`formal-method-editor.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/formal-method-editor.tsx#L902-L926) 要素 ② 面板只读不可编；
     - ② [`resource_delegation.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/resource_delegation.py#L43-L93) 硬锁 `max_delegation_depth: le=1` 且未适配正式方法多跳调用树；
     - ③ **公私叶子交付死锁**：KnowLab [`formal_methods.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/application/services/formal_methods.py#L1118-L1137) 与 KnowBench [`formal_methods.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_methods.py#L788-L807) 强制所有 `registered_script`、`service_function`（含 `knowbase.read_method_input`）与 `is_instruction`（指令叶子）只能以 `visibility == "private"` 冻结；但冻结/注册 `public` 专家时，KnowLab 第 775 行与 KnowBench 第 832–838 行（调 `check_delivery_source(..., market=True)` 第 441 行）却写死子依赖必须 `frozen.visibility == "public"`！**导致任何含自写脚本、KnowBase 资料读取或指令成稿/复核叶子的专家在数学上永远无法作为 `public` 专家发布上架！**
6. **`M06` — 要素 ④ `ValidationRule` 只是两行不执行的死文字，运行期零确定性业务核验**
   - **代码实证**：[`formal_method.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/formal_method.py#L572-L577) 仅有纯文本 `check / evidence`；[`formal_orchestration_execution.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_orchestration_execution.py#L566-L573) 与 `export_outputs`（第 815 行）仅验 JSON Schema，完全不跑确定性业务核验算子。
7. **`M07` — 要素 ⑤ 审批失灵：`FormalHostCalls.request` 无视立项确认回执，对每步零外发脚本强弹单步审批**
   - **代码实证**：[`formal_host_calls.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_host_calls.py#L680-L750) 无视 `ConsumerPlan` 已签署的 `CONFIRMED` 立项确认回执，对每个纯计算脚本、只读资料读取与单轮指令叶子均强开 `tool_approval` `Interaction` 阻塞等待人工点击，且 [`formal_evidence.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_evidence.py#L339-L426) 强验单步 `interaction_id`（导致 6 步零外发专家要连点 6 次弹窗）。
8. **`M08` — 槽位裸敲 JSON Schema 与空 `meaning: {}`，数据库误建 `HASH` 索引，两视图在创作全程隐身**
   - **代码实证**：[`tool-slot-editor.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/tool-slot-editor.tsx#L113-L119) 让作者手敲裸 JSON Schema，[`delivery-template.ts`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/lib/knowbots/delivery-template.ts#L80) 默认塞空 `meaning: {}`；[`20261120_0028_method_graph_indexes.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/alembic/versions/20261120_0028_method_graph_indexes.py#L20-L21) 建了无法支持前缀协变的 `HASH` 索引；两视图在 [`formal-method-editor.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/formal-method-editor.tsx#L1094-L1110) 仅对已冻结版本可见。

---

### 1.2 局部与整合层（要素 ③ 递归规划、编译与递归执行）八大底层硬伤（`R01–R08`）

1. **`R01` — 四正交原语与内核 `strict_plan` 盲审被硬编码为全局互斥锁，禁止嵌套组合**
   - **代码实证**：[`selection.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/selection.py#L220-L235) 硬锁 `object_batch` 必须整图仅 2 步且互斥其他原语、`independent_review` 禁有前驱或与分支共存；[`formal_method_plan.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/formal_method_plan.py#L74-L135) 硬锁盲审整图 2/3 步且第 238 行只准无前驱指令步做生产者；[`selection.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/selection.py#L607-L620) 与 [`ordinary_expert.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/ordinary_expert.py#L80-L84) 禁止父专家调用含批量/分支/复核的嵌套子专家。
2. **`R02` — 规划器缺失五要素契约制导，回溯清空 `self.shown` 失忆，终局校验失败直接炸毁整棵已解树**
   - **代码实证**：[`hierarchical_planning.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/hierarchical_planning.py#L261-L343) 未注入父草稿要素 ① 目标输出槽与要素 ② 权限上限；第 405 行 `reset()` 每次回溯清空 `self.shown = []`；第 657–661 行 `finish("ready")` 若 `check_proposal` 报错直接 `self.reset(root, "")` 清零整棵树。
3. **`R03` — 跨子方法合并权限/审批 ID 碰撞崩溃 + 内部节点号 `n1_2_` 泄漏污染公开输入视图**
   - **代码实证**：[`selection.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/selection.py#L432-L441) 直接按局部 `requirement_id` 合并字典导致不同子工具同名即抛 `selection_permission_conflict`；[`hierarchical_planning.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/hierarchical_planning.py#L585-L591) 拼接 `(node.id + "_" + binding.name)` 将 `n1_2_1_` 泄漏进 `public_inputs`。
4. **`R04` — 主稿 §2.2 封闭四项值处理未落地：强制端口 Schema 字节全等，误禁常量绑定**
   - **代码实证**：[`formal_method.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/formal_method.py#L535-L540) 要求上下游 Schema 字节全等（缺 `ProjectionLens` 裁剪/重命名与 `CollectPack` 多路归集），[`selection.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/selection.py#L368) 误禁 `LiteralValue` 常量绑定。
5. **`R05` — `unique_plan` 静态锁死第 0 步单图，封杀“基于前驱已验产物的受控条件分流与惰性展开”**
   - **代码实证**：[`formal_method_plan.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/formal_method_plan.py#L497-L561) 仅支持开跑前按 `caller` 入参精确相等裁单图，无法按初检步骤已验输出决定是否展开深层核查分支。
6. **`R06` — 盲审复核双轨割裂（内核 `strict_plan` vs 外部 `branch_review_dispatch.py`），且试跑禁返工**
   - **代码实证**：[`formal_review_rework.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_review_rework.py#L44) 写死非 `ConsumerPlan` 禁返工，阻断试跑验证；同时 [`branch_review_dispatch.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/branch_review_dispatch.py#L137-L181) 又另搞手工跳页外部任务复核。
7. **`R07` — 同工具跨步禁绑不同账号 + `$O(N^2)$` 祖先重查 + 准备页全槽误挂资料下拉框**
   - **代码实证**：[`ordinary_expert_execution.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/ordinary_expert_execution.py#L57-L60) 按 `reference` 去重禁绑多账号；[`formal_recursive_runtime.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_recursive_runtime.py#L156-L276) 递归重扫全部已完成节点；[`formal-expert-preparation.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/features/expert/ui/formal-expert-preparation.tsx#L149-L187) 给所有普通参数槽都错误渲染 KnowBase 资料下拉框。
8. **`R08` — 缺口子方法靠 `sessionStorage` 断链 + 双管线冷启动且流式预算/单轮时限失守**
   - **代码实证**：[`selection-panel.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/selection-panel.tsx#L200-L206) 靠浏览器 `sessionStorage` 传缺口，冻结后无法回填父树；`FIND_EXPERT` `v5/v7` 分两次冷启动沙箱，`INCUBATE` 缺 `thread/tokenUsage/updated` 硬熔断（`#121`），`v7` 缺单轮 60s 独立收口（`#122`）。

---

### 1.3 左边栏“方法与技能”（KnowLab ⇄ KnowBench）四项跨端割裂病灶（`X01–X04`）

1. **`X01` — KnowBench 左边栏“方法与技能”（`MethodSkillCenterSection`）沦为 6 页签底层调试倾倒场，且创作与运行入口跨 3 处折返跑**
   - **代码实证**：[`sidebar.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/features/shell/ui/sidebar.tsx#L365-L386) 左边栏底部 `FOOT` 的 `methods`（“方法与技能”）打开 [`method-skill-center-section.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/features/methods/ui/method-skill-center-section.tsx#L87-L412)，直接平铺 `formal / planning / sources / installed / native / activity` 6 个生硬工程页签：
     - `formal` 页签向终端用户裸露 `workbench_formal_methods` 的 `sha256:...` 摘要，不展示五要素能力边界与输入/返回两视图；
     - `planning` 页签（[`planning-methods.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/components/workbench/planning-methods.tsx#L91-L261)）与 `formal` 重复列方法，却不能查看两视图槽位规格或一键带参跳转请专家；
     - `sources` 页签（[`method-skill-center-sources.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/features/methods/ui/method-skill-center-sources.tsx#L120-L238)）把**作者侧登记脚本/指令源码**塞在消费端工作台里，而 MCP 连接与 Skill 包安装却又要跳去 `/workbench/settings#connections` 与 `/workbench/settings#skills`，`native` 页签更直接把 Codex 内部协议字符串摊给普通用户。
2. **`X02` — KnowLab 左边栏 9 栏新旧双轨错位，且“方法栏”(`/methods`) 混排历史旧原子方法与正式方法、缺本地源内联代理**
   - **代码实证**：[`navigation.ts`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/lib/navigation.ts#L17-L56) 左边栏硬铺 9 栏（`总览 / 申请 / 孵化 / 测试 / 交付 / 待办 / 专家 / 方法 / 知识库`），其中 `申请 / 孵化 / 测试 / 交付 / 待办 / 专家` 全部绑死旧 `SCHEMA_V3` `KnowbotRequest / KnowbotExpert`（[`lab-columns.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/lab-columns.tsx#L320-L410)）；正式方法作者在 [`method-directory.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/method-directory.tsx#L140-L235) 与 [`knowbot_routes.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/interfaces/endpoints/knowbot_routes.py#L2037-L2061) 看到同一页混排旧 `KnowbotMethodService` 非正式原子方法与新 `FormalMethod`，且登记脚本/指令源必须跳去 KnowBench `sources` 页签操作后再跳回 KnowLab 绑定。
3. **`X03` — 三端 `CrossAppLink` 路由注册表（`destinations.ts`）指向旧轨与死链，`formal_handoff` 丢失五要素与推荐编排树**
   - **代码实证**：KnowBench [`destinations.ts`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/lib/cross-app/destinations.ts#L8-L12) 的 `'knowlab.createIdea'` 与 `'knowlab.incubation'` 全跳向旧 `/applications/new` 与 `/incubation`；KnowLab [`destinations.ts`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/lib/cross-app/destinations.ts#L11-L26) 仍指向即将清退的 `'knowbench.review'`；KnowMart [`destinations.ts`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/lib/cross-app/destinations.ts#L12) `'knowlab.experts'` 跳去旧 `/experts`；KnowBench [`formal_handoff.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_handoff.py#L43-L157) 虽已算出即时编排 `suggested_plan`，却只往旧创意申请流塞文本，无法直接生成带要素 ① 预期交付槽与要素 ③ 初稿树的 `MethodDraftV2`，也无法转为带两视图规格的 KnowMart 需求单。
4. **`X04` — 正式方法跨端交付契约失真：KnowLab `list_for_self` 只传标题与目的，丢失公开五要素边界与两视图规格**
   - **代码实证**：[`formal_methods.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/application/services/formal_methods.py#L169-L181) `list_for_self()` 向 KnowMart 同步时仅传 `title / purpose / method_kind / review_findings`，导致 KnowMart `formal_method_listing` 表（[`models/market.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/infrastructure/models/market.py#L298-L345)）完全没有该版本的公开两视图（`public_inputs / what_to_return`）、适用/排除边界、所需消费端授权摘要与 V0 核验透明标签，下游市场根本无从展示五要素契约。

---

### 1.4 KnowMart 前后端（Web + Admin + Backend）与双端联动四项结构性断层（`X05–X08`）

1. **`X05` — KnowMart 公开目录与详情页严重残缺：`FormalListing` 无详情页、无“请专家/获取工具”按钮，且在小店首页与店铺页彻底隐身**
   - **代码实证**：
     - [`expert-catalog.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/knowbots/expert-catalog.tsx#L316-L347) 对旧 `Knowbot` 渲染完整 `<ExpertCard>`（可点进 [`expert-detail.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/knowbots/expert-detail.tsx#L27-L141) 并一键 `summon` 请回工作台），对 `FormalListing`（`'listing_id' in item`）却只画一个**无详情链接、无任何操作按钮、直接裸露 `method_id · sha256`** 的死卡片；[`expert_catalog.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/expert_catalog.py#L252-L325) `detail()` 根本不支持查 `FormalListing`；Web 端甚至没有任何按钮调用后端已实现的 `POST /formal-methods/listings/{id}/acquisitions` 获取共享工具/专家使用权！
     - [`market.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/market.py#L340-L372) `shops() / shop()` 与 [`shops.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/shops.tsx#L192-L214) 只统计和展示旧 `knowbots` 表，作者公开发布的正式专家与工具在自家小店卡片与店铺主页上数量恒为 `0`！
2. **`X06` — KnowMart 三套类目表硬编码打架：`submit_formal` 误拒工具类目与分析子类目，`MyShop` 拆成三处碎片页签且 `incubation_scope` 误放行专家**
   - **代码实证**：
     - [`catalog.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/domain/knowbots/catalog.py#L26-L89) 并存 `CATEGORIES`（资质准入类目 `BY_CODE`）、`EXPERT_DIRECTORY_CATEGORIES`（含 `analysis.*`）与 `TOOL_CATEGORIES`（`financial.reconciliation` 等），而 [`market.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/market.py#L833) `submit_formal()` 强验 `check_category(body.category)`（仅认 `BY_CODE`），导致工具类目与 `analysis.*` 提交公开审核时直接报 `invalid_category` 400 错误！
     - [`my-shop.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/my-shop.tsx#L38-L47) 将卖家供给拆成 `'experts'`、`'formalMethods'`（[`my-formal-methods.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/my-formal-methods.tsx)）与 `'incubation'`（[`incubation-permissions.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/incubation-permissions.tsx)）三套割裂界面；且 `author_incubation_listings` 未限制 `method_kind == 'tool'`，把不允许作为跨作者孵化积木的 `expert` 也暴露在孵化共享权限表里（与 KnowBench [`registry_catalog.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/registry_catalog.py#L551) 直接冲突）。
3. **`X07` — KnowMart 定价、成交留痕、评价与需求大厅响应（`Demand / Offer / Trade`）完全未接入 `FormalListing`**
   - **代码实证**：`FormalListing` 无 `price` 字段；`OfferIn`（响应需求单挂接现成供给）、`add_trade`（获取使用权记账留痕）与 `TradeReview`（评价星级）仅支持旧 `knowbots` 与 `knowledge_listing`，正式方法无法响应 [`demands.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/demands.tsx) 中的需求悬赏，获取使用权时也无 `Trade` 记录与评价闭环。
4. **`X08` — KnowMart 运营后台（`knowmart-admin-frontend`）漏掉正式方法审核台，且撤证/过期清扫/违规下架全部漏管 `FormalListing`（`C-L4 / C-L5` 合规缺口）**
   - **代码实证**：
     - [`market-admin.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-admin-frontend/app/components/market-admin/market-admin.tsx#L151-L203) `ListingReview` 只渲染 `knowledge` 与旧 `experts`，**管理后台前端完全没有审核 `pending_formal` 的界面**，导致作者提交的公开正式方法永远卡在 `pending`！且 `pending_formal` 未做 `flagged()` 违规词扫描（`C-L5`）；
     - [`market.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/market.py#L2304-L2318) `_withdraw()`（撤销发布主体/证照）、第 2494–2516 行 `sweep()`（定时清扫过期证照）、第 2369–2429 行 `take_down()`（运营强制/违规下架与举报核实处置）**全部漏掉了 `formal_method_listing`**（表约束甚至没有 `'taken_down'` 状态）！

---

### 1.5 吸收合并《一周代码评审》10 项生产级缺陷与现场故障根因（`W01–W10` 全量归口）

[一周代码评审.md](file:///home/zym/wsl-worktrees/luna/sunmoonun/%E4%B8%80%E5%91%A8%E4%BB%A3%E7%A0%81%E8%AF%84%E5%AE%A1.md) 查实的 `W01–W10` 与本次重构改动面高度重合，若不随本次重构一并根治，将直接引发大目录 HTTP 风暴、JSONB 迁移崩溃与 `#121/#122/#123` 现场故障复发：

| 评审编号 | 级别 | 精确底层根因定位 | 在本定稿方案中的归口落点 |
| :---: | :---: | :--- | :--- |
| **`W01`** | **P1** | [`registry_catalog.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/registry_catalog.py#L261-L269) `planning_versions` 命中类目词时 `while more` 拉取买方全量市场授权页，使本地 GIN 索引分批核权 `if more:` 沦为死代码；`shared_tools`（L608–678）无上限翻页且循环内逐条开事务重查 `capability_assets`（N+1） | 并入 **§3.2 & §4.2（PR-3）**：删除 `if topics: while more:` 统一走 GIN 索引 + 100 条分批核权；循环外预缓存 `capability_assets` 并设分页硬上限 |
| **`W02`** | **P1** | [`20261124_0062_capability_search.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/alembic/versions/20261124_0062_capability_search.py#L13-L48) `workbench_capability_vector(jsonb)` 未判 `jsonb_typeof`，遇显式 JSON `null` 抛 `SQLSTATE 22023` 导致写入或迁移崩溃 | 并入 **§2.4 & PR-2**：KnowBench 线性迁移重建 `workbench_capability_vector`，全部包裹 `jsonb_typeof` 守卫并纳入 `domain_id` 词元索引 |
| **`W03`** | **P1** | [`runner.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/runner.py#L904-L935) `lookup` 仅判 `FIND_EXPERT`，使 `INCUBATE` 漏挂 `LookupGuard(remaining)`（`#121` 3 元上限跑出 3.219660 元且丢弃成稿根因），且 `turn_plan`（L2998）违反 `SEALED_INPUT` 向孵化线程注入本地目录与用户私人 `memory_note` | 并入 **§3.2 & PR-3**：统一提炼 `is_sealed_planning(task)`（覆盖 `SEALED_INPUT`），强制纯净无记忆 `chat` 线程 + 全程挂载 `LookupGuard(remaining)` |
| **`W04`** | **P1** | [`knowbot_board.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/application/services/knowbot_board.py#L326-L357) `_assemble` 退役 v2 专家时仅剥离子项而保留空壳父 `request` 及旧缺口提问，使已完结旧申请 `5814331f-...` 逆向变为 `"working"` 且详情仍回 200（`#123` 根因） | 并入 **§4.1 & PR-2**：落地 `is_retired_v2_only_request` 统一剔除纯退役 v2 空壳申请及关联缺口提问，看板与详情一致回 404 |
| **`W05`** | **P1** | [`task_runtime.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/task_runtime.py#L350-L370) `FIND_EXPERT` v7 以 `attempts[0].created_at` 硬卡 150s 总挂钟，末轮仅剩数秒仍强发 `turn/start` 随即超时腰斩（`#122` 工作台 6/16 根因） | 并入 **§3.2 & PR-3**：首轮 Top-K 契约直注砍掉多余 `inspect` 轮次 + 发起 turn 前校验 `remaining >= MIN_HTN_TURN_SECONDS(25s)` + 分层推进时限 |
| **`W06`** | **P2** | [`hierarchical_planning.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/hierarchical_planning.py#L340-L342) `stale_edit` 未在调模型前短路（白跑一轮 LLM 扣费后在 L688 丢弃）；点名方法 `mode="method"` 首轮未预披露 `chosen_method()` 契约多耗一轮 `inspect` | 并入 **§3.2 & PR-3**：`TaskRuntime._execute_next` 遇 `planner.stale_edit` 零 Token 宿主直返；初始化/重置时自动 `disclose(chosen_method)` |
| **`W07`** | **P2** | [`formal_expert_intake.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_expert_intake.py#L196-L253) 对未选推荐项逐个串行核权（N+1），任一未选候选撤架即令整张匹配页（含 `ENDED` 历史轮）抛 HTTP 404 | 并入 **§3.2 & PR-4**：改为单次批量 `planning_definitions` 核权，失权未选项标 `unavailable: True`，仅在点选确认时返 409 |
| **`W08`** | **P2** | [`backfill_formal_method_kinds.sh`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/scripts/backfill_formal_method_kinds.sh#L38-L51) 未进发布流水线且遇单条已撤回孤立记录即 `RAISE EXCEPTION` 整表回滚 | 并入 **§5.1 & PR-5**：收窄硬校验至在架 `('listed','pending')` 记录、容错跳过孤立历史行，上架自动落盘初始 `directory_category` |
| **`W09`** | **P3** | [`expert-catalog.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/knowbots/expert-catalog.tsx#L68-L75) 点筛选 Chip `X` 清除 `q` 时未同步清空输入框本地 `words` 状态 | 并入 **§5.2 & PR-5**：重构 `<FormalMethodCard>` 目录页时在 `go(next)` 与 URL 监听中同步重置 `words` |
| **`W10`** | **P3** | [`sources.yaml`](file:///home/zym/wsl-worktrees/luna/sunmoonun/infrastructure/applications/sources.yaml) 应用仓指针窗口期未同步导致 `verify-contracts.py --pinned` 报错 | 并入 **§6 & PR-6**：增强 `verify-contracts.py --pinned` 窗口期诊断提示，并在晋级收口时同步校验 `sources.yaml` |

---

## 二、 任务一：彻底重构整体——“方法模板（五要素+两视图）”静态基座与受控动态联动设计

### 2.1 核心机制定型：【静态契约基座 + 受控跨要素动态联动 + 结构化 `C-L1` 出处账本】

1. **静态契约基座（Static Contract Base & Engineering Archetypes `S1–S4`）**：
   - 所有正式方法（无论 `tool` 还是 `expert`）共享唯一恒定的外部契约骨架：**五要素（① 能力声明、② 所需权限、③ 如何做、④ 如何校验、⑤ 什么要批）+ 两视图（`public_inputs`、`what_to_return`）**。
   - 新建草稿时提供 **4 套纯工程治理起草样板（`S1–S4`，零投资判断/零行业阈值，100% 严守 `C-L1`）**。样板**仅在初始化草稿时生成待作者确认的五要素结构骨架**，落稿后不存在任何锁死字段的模板枷锁，零模板继承树、零 `method_template_locked` 报错。
2. **受控跨要素动态联动（Reactive Cross-Element Invariants）**：
   - 前后端共用确定性纯函数 `project_contract_state(draft)`，实时维护五要素与两视图之间的数学投影关系：**要素 ① 确立预期交付语义槽 ──▶ 制导要素 ③ 规划与对齐 `exports` ──▶ 要素 ③ 自动派生 `public_inputs / what_to_return` 两视图并按路径命名空间上卷要素 ② 权限与要素 ⑤ 审批 ──▶ 要素 ④ 将每项承诺绑定至可执行 V0 确定性核验算子与试跑正/反向用例 ──▶ 冻结与上架时自动提取公开安全契约 `PublicMethodContract` 投送 KnowBench 与 KnowMart**。

### 2.2 四套纯工程静态起草样板（`S1–S4`，彻底取代 `RequestForm` 创意六问与 `checked_delivery/v1`）

| 样板 ID 与工程定位 | ① 能力声明初始结构 | ② 所需权限初始结构 | ③ 如何做初始入口 | ④ 如何校验初始算子 | ⑤ 审批策略初始结构 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S1 · 确定性核验与计算交付`**（脚本核算、表格勾稽、结构化转换） | 1..N 条具名必交承诺（选受控词表槽位预设，作者自填适用前提与排除边界） | 工具绑 `isolated-script(execute)`；专家由子步自动上卷 | 默认选 `工具固定实现`（脚本）或 `专家四原语编排` | 默认挂载 `schema_and_range` + `numeric_identity` V0 算子槽（容差等参数须作者填写确认） | `envelope`（立项/委托包络一次确认，运行期零单步弹窗） |
| **`S2 · 授权取数与多条件承诺交付`**（资料读取、按条件分流、允许缺项说明） | 支持 `always` / `conditional` / `partial_allowed` 多承诺声明 | 预置 `knowbase(read_method_input)` 或只读 `connector` 权限槽 | 默认进入 `专家四原语编排`（含按需读取与 `branch` 分支） | 默认挂载 `sourced_citation` + `collection_coverage` V0 算子槽 | `envelope`（准备页锁定资料 `sha256` 与只读连接范围，运行免重弹） |
| **`S3 · 隔离盲审与交叉复核交付`**（主笔产出 + 独立盲审 / 双主笔仲裁） | 区分“业务主产出承诺”与“复核比对披露承诺” | 上卷主笔与复核路由权限，强制进程/会话隔离 | 在目标步骤挂载局部 `ReviewSubgraph`（复用泛化后的 `ReviewPhaseStep`） | **V0 算子必过门禁** ──▶ 放行 V1 隔离/异模型家族盲审 | 包络预授权首轮及预算内有界返工（`0..2` 轮）；路由变更或分歧未消触发 `CHANGE_ROUTE / ADJUDICATE` |
| **`S4 · 受控外部写/外发动作交付`**（外部消息投递、写回外部连接器） | 明确分离“成稿承诺”与“外部动作回执承诺” | 预置 `connector` `write/send` 权限槽，必填 `data_transfer` 外发字段与目的 | 前序计算/生成步骤与末尾外部写/发步骤显式解耦 | 外发步骤执行前强制先过前序产物 `prohibited_terms` 与完整性 V0 检查 | **强制生成 `per_action` 审批规则**（单步挂起展示完整账号、目标资源、正文摘要与附件供逐次批准） |

---

### 2.3 结构化五要素出处账本（`ElementProvenanceLedger`）——严守 `C-L1` 且零破坏演进 `knowbot_workdraft`

针对 `M04`（`KnowbotMethodVersion.source_workdraft_id` 非空外键 + `source_problems()` `C-L1` 强校验）：

1. **平滑演进 `knowbot_workdraft` 与 `knowbot_workdraft_record`，绝不断裂外键链**：
   - 在 `knowlab-backend` 做单链线性 `expand` 迁移：将 `knowbot_workdraft.request_id` 改为 `NULLABLE`，新增 `method_id UUID NULL`（新工作坊草稿直绑 `KnowbotMethod.id`，不再强建冗余 `KnowbotRequest` 行；既有历史行 100% 原样保留，`knowbot_method_version.source_workdraft_id` 外键分毫无损）；
   - 新增列 `draft_contract JSONB`（存放宽进态五要素草稿 `MethodDraftV2`）、`htn_state JSONB`（持久化 HTN 规划树与披露缓存）、`parent_gap JSONB`（分形缺口父节点引用）。
2. **结构化语义路径出处核验（取代脆弱字符偏移 `idea:<ver>:<start>+<len>`）**：
   - 对 `MethodDraftV2` 中每一条含业务判断的要素单元（`capability.purpose`、`capability.applies_when[i]`、`capability.excludes[i]`、`capability.promises[pid]`、`validation.rules[pid]`、`approval.action_rules[rid]`、`procedure.steps[sid].task`），在 `knowbot_workdraft.sources` 中按稳定语义键记录出处并写入 `knowbot_workdraft_record`：
     - `kind = "edit"`（`actor_role = "author"`）：作者亲手输入或修改保存；
     - `kind = "accept"`（`actor_role = "author"`，`suggestion_ref = "ai:<incubation_id>:<semantic_key>:<sha256>"` 或 `"preset:<archetype_id>:<semantic_key>:<sha256>"`）：AI 起草建议或样板初始提示**一律处于待作者确认态**，仅当作者显式点击采纳或编辑保存后才落入已确权账本；
     - `kind = "copy" / "import"`：从作者名下既有版本 `v_k` 克隆升版时，未改动条目继承原版本确权记录链。
   - 冻结前 `_prepare_v2()` 逐项核验 `element_source_problems()`：**任何仍含 `unconfirmed_suggestion` 的草稿一律拒绝准入校验与冻结**。

---

### 2.4 五要素 + 两视图底层契约精确升级规范（`knowlab/formal-method` 提供方模型）

为遵守 `C-C10` 与 `C-D14`（既有已冻结 `v1` 版本 `digest()` 100% 字节级不变），在 [`formal_method.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/domain/knowbots/formal_method.py) 中采用 `exclude_if` 向后兼容扩展，并新增宽进草稿模型 `MethodDraftV2` 与公开安全投影 `PublicMethodContract`：

1. **受控层级语义词表 `SlotMeaningCatalog` 与槽位预设 `SlotPreset`（根治 `M08`）**：
   - 新增 `slot_vocabulary.py`（由 `export_formal_method.py` 同步导出至 KnowBench、KnowMart 与前端，对齐 KnowBase [`vocabulary.py`](file:///home/zym/wsl-worktrees/luna/knowbase-app/knowbase-backend/app/app/domain/vocabulary.py#L1-L120)）：规范化 `ValueSlot.meaning` 为 `{"domain_id": "fin.statement.row", "vocab_version": "1", ...}`，提供 6 类工程槽位预设构造器 `SlotPreset`（`monetary_amount`、`ratio_or_rate`、`structured_record`、`tabular_rows`、`check_receipt`、`cited_markdown`）；
   - `method_version_slots` 迁移：删除失效 `HASH` 索引 `ix_method_version_slots_meaning`，改建 `btree ((meaning->>'domain_id') text_pattern_ops)`（原生支持子类型前缀协变匹配）与 `gin (meaning jsonb_path_ops)`。
2. **要素 ① `ExpectedDeliverableSpec` 独立成稿（破解 `M03` 死锁）**：
   - `MethodDraftV2` 要素 ① 直接持有 `expected_deliverables: tuple[ExpectedDeliverableSpec, ...]`（含 `promise_id`、`summary`、`expected_domain_id`、`expected_schema`、`delivery_mode: always | conditional | partial_allowed`），无需等待要素 ③ 编排即可独立保存并预览目标返回视图；冻结编译时自动对齐要素 ③ `exports`。
3. **要素 ② 全量受管能力目录、`1..4` 跳委派与公私内部叶子准入打通（根治 `M05`）**：
   - 扩展 [`method_capabilities.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/method_capabilities.py#L46-L196) 导出 `service_functions`（`knowbase:read_method_input`）与 `isolated-script:execute`，扩展 `AccessRequirement.required_when: Literal["always", "when_selected"]`；
   - 升级 [`resource_delegation.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/domain/workbench/resource_delegation.py#L43-L98) 新增 `FormalTreeDelegationBinding(kind="formal_call_tree")`，放宽 `max_delegation_depth` 至 `1..4` 跳；
   - **解开公私内部叶子交付死锁**：保持 `registered_script`、`service_function` 与 `is_instruction` 不可单独作为 `public` 工具裸卖；**但当它们作为同一作者（`dep.owner_subject == root.owner_subject`）名下已完成真实运行取证（`dep.validation.execution is not None`）且合规（`skill_instruction` 具 `delivery_terms`、脚本为纯隔离容器执行、`service_function` 为平台标准受管读取）的内部叶子被封装在 `public` 专家（`Orchestration`）内部时**，准许随父专家整体通过公开准入与 KnowMart 上架交付！
4. **要素 ④ 可执行 `V0` 确定性核验算子（根治 `M06`）**：
   - 在 `ValidationRule` 上扩展 `v0_checks: tuple[V0CheckSpec, ...]`，封闭 5 类纯确定性无模型算子（`numeric_identity`、`schema_and_range`、`sourced_citation`、`collection_coverage`、`prohibited_terms`），在 [`formal_orchestration_execution.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_orchestration_execution.py) 单步完成与根 `export_outputs` 处强制执行 `evaluate_v0_checks`。
5. **要素 ⑤ 包络预授权 `EnvelopeAuthorization` 与外部写/发逐次强批双轨制（根治 `M07`）**：
   - `ApprovalRule` 区分 `scope: Literal["envelope", "per_action"]`：外部 `write/send` 操作编译期强制要求 `per_action` 规则；纯隔离脚本、已锁定 `sha256` 的 KnowBase 读取、预算上限内单轮指令默认归入 `envelope`；
   - 升级 [`formal_host_calls.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_host_calls.py#L676-L750) 与 [`formal_evidence.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_evidence.py#L339-L505)：对已验 `CONFIRMED` 回执（或带作者试跑包络签名的非拒止测试例）的 `envelope` 步骤直接签发不可委派叶子授权并记录 `envelope_approval_ref`，**彻底消除零外发步骤连环弹窗**，同时 100% 保留 `per_action / write / send` 的单步 `tool_approval` `Interaction` 拦截与取证。

---

## 三、 任务二：有机整合整体与局部——五要素统摄下的要素 ③ 四原语递归规划与执行

1. **编译期整合（根治 `M02 + R01 + R03 + R04 + R06`）**：
   - **重写 `selection.py:expand()`**：根专家的要素 ①④ 严格取自父草稿 `MethodDraftV2` 作者确权内容（严禁倒抄末步工具定义），支持任意子步骤联合导出至根 `exports`；子步权限与审批上卷自动加确定性路径前缀 `<step_id>__<id>`，同语义外部入参自动归并，消灭权限重名冲突与 `n1_2_` 节点号泄漏；
   - **落地封闭四项值处理**：新增无副作用 `ProjectionLens`（宽度字段裁剪 `pick_fields` + 字段重命名 `rename_fields`）、多路结果归集 `CollectPack`，放开经作者确认的 `LiteralValue` 常量绑定及指令方法 `max_model_turns: 1..3`；
   - **解除四原语与 `strict_plan` 盲审互斥硬锁**：局部化 `MapStep`（`bounded_loop`，解除整图 2 步硬锁，支持嵌套调用含批量/分支/复核的子专家）；将 `ReviewPhaseStep`（`source → blind → comparison → revision`）泛化为可挂载于图内任意步骤（含通过 V0 核验的脚本/子专家产出）的局部盲审子图，对试跑 `FormalTaskSnapshot` 开放预算内自动返工验证，清退外部手工派单的 `branch_review_dispatch.py`。
2. **规划期、封存隔离与大目录检索整合（根治 `R02 + R08 + W01 + W02 + W03 + W05 + W06 + W07`）**：
   - **五要素自顶向下制导 `HierarchicalPlanner` 与零浪费交互**：
     - 注入父草稿要素 ① `target_deliverables` 与要素 ② `allowed_capabilities`，纯 Python 5ms 逆向超图可达性剪枝 + **首轮 Top-K（如前 5~12 项且 `<= 16KB`）高相关候选及用户显式点名的 `chosen_method()` 自动预置入 `self.shown` 预披露契约**（省去 1–2 轮 `inspect`，使 80%+ 题目 1–2 轮直出 `hit/split`） + KnowBase [`table_format.py`](file:///home/zym/wsl-worktrees/luna/knowbase-app/knowbase-backend/app/app/domain/table_format.py#L29-L35) 只读表轴摘要直注；
     - 在 `TaskRuntime._execute_next` 调模型前短路 `planner.stale_edit`（零 Token 宿主侧直返澄清，根治 `W06`）；修复 `reset()` 保留 `self.shown`（超 `DISCLOSURE_BYTES` 时 LRU 淘汰）+ 节点 `tabu_signatures` + `resolve()` 实时增量守卫（删除 `finish()` 炸树）；
   - **统一 `SEALED_INPUT` 封存线程隔离、盘中预算熔断与分层时限守卫**：
     - 在 [`runner.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/runner.py) 提炼统一谓词 `is_sealed_planning(task)`（覆盖 `FIND_EXPERT` 与 `INCUBATE`），强制使用 `directory=None`、零 `memory_note / data_session_note` 注入、禁用非授权 MCP Server 的纯净只读线程，并统一挂载 `LookupGuard(remaining)` 监听 `thread/tokenUsage/updated` 盘中硬熔断（彻底根治 `W03 / #121`）；
     - 合并 KnowBench `v5 + v7` 单快照渐进匹配编排；在 [`task_runtime.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/task_runtime.py#L350-L370) 分离单轮时限与推进总预算，发起新 turn 前强制校验 `remaining >= MIN_HTN_TURN_SECONDS (25s)` 严防末轮剩几秒空耗扣费腰斩（根治 `W05 / #122`）；
     - 在 [`formal_expert_intake.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_expert_intake.py#L196-L253) `review()` 中改为单次批量调用 `registry.planning_definitions` 核权，未选推荐项下架时仅标 `unavailable: True` 而不令整页抛 404（根治 `W07`）；
   - **修复大目录 GIN 全文索引死代码与 JSON `null` 崩溃**：
     - 在 KnowBench 新增线性迁移升级 `workbench_capability_vector(jsonb)`，为全部 `jsonb_each* / jsonb_array_elements*` 加上 `jsonb_typeof` 类型防御并索引 `domain_id` 语义词元（根治 `W02`）；
     - 在 [`registry_catalog.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/registry_catalog.py#L261-L269) 删除 `if topics: while more:` 全量拉取循环，恢复本地 GIN 索引 + 100 条分批 `planning_formal_refs` 核权路径；在 `shared_tools` 循环外一次性预取缓存 `capability_assets(owner)` 并加最大扫描页数上限（`partial: True`，根治 `W01`）；
   - **分形缺口原位派生与冻结回填**：HTN 树节点停在 `gap` 时，后端 `spawn_gap_child(parent_workdraft_id, node_id)` 自动带目标槽规格与权限上界创建子 `knowbot_workdraft`（记录 `parent_gap`）；子方法冻结后调 `bind_gap_resolution` 原位回填父树节点并重算父两视图，淘汰 `sessionStorage`。
3. **执行期整合（严守 `P0 / C-A10`，根治 `R05 + R07`）**：
   - 编译期 `verify_envelope_graph` 静态求所有可达分支并集（验无环、深度 `<= 4`、总权限包络与最坏费用上界）；运行期维护确定性 **`FrontierState`**（`$O(1)$` `outputs_index` + `VerifiedArtifactGuard` 受控惰性展开，未命中分支整棵子树标 `SKIPPED_BY_GUARD` 免开 `Attempt`、免扣费）；
   - `ConsumerPlan` 升级按路径 `slot_sources: dict[str, FormalMethodSource]` 支持同工具跨步绑不同业务账号；`formal_expert_preparation.py` 精确返回 `material_slots`，准备页仅对真实 KnowBase 资料槽渲染资料选择器。

---

## 四、 任务三：重构 KnowLab 与 KnowBench 左边栏“方法与技能”及三端跨应用协同链路（根治 `X01–X04`）

严格遵循 `C-T1` 边界（**KnowLab = 作者孵化与方法工程台**；**KnowBench = 消费者使用与本地运行环境台**），彻底重构双端左边栏与“方法与技能”模块：

### 4.1 KnowLab 左边栏、旧 v2 退役收口与 `/methods`（作者侧“方法与技能”）重构
1. **左边栏从 9 栏旧申请单流精简为 4 栏正式方法优先导航，并彻底收口旧 `knowbot-manifest/v2` 空壳申请（根治 `X02 + W04 / #123`）**：
   - 在后端 [`knowbot_board.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/app/application/services/knowbot_board.py#L326-L357) 落地统一判定 `is_retired_v2_only_request(request, drafts, workdraft)`：凡历史上仅产生过已退役 `knowbot-manifest/v2` 产物且无正式方法草稿（`formal_method / draft_contract`）或 v3 准专家的旧申请，在 `_assemble` 中连同其关联 `questions/gaps` 一并剔除（申请看板不展示、详情接口一致返回 404，彻底消除旧财务申请 `5814331f-...` 逆向变成 `"working"` 的 `#123` 故障）；仍在有效期内的 `SCHEMA_V3` 记录在前端 [`navigation.ts`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/lib/navigation.ts) 与 [`web-shell.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/shell/web-shell.tsx) 收折进底部折叠组 `历史兼容归档`，主导航精简为 4 栏：
   - **`📊 概览 (/dashboard)`**：在孵五要素草稿进度、待作者确权项（`C-L1`）、试跑结果与 KnowMart 审核回执总览；
   - **`🛠️ 方法工坊 (/studio)`**：在孵五要素草稿管理与 `/studio/[methodId]` 四步一体化创作主舞台（Step ① 契约立项 `S1–S4` ──▶ Step ② 如何做三栏四原语画布 ──▶ Step ③ 实测与钉断言 ──▶ Step ④ 冻结/回填/送审，底部常驻实时 `public_inputs / what_to_return` 两视图与 8 项闭合诊断条）；
   - **`🧩 方法与技能 (/methods)`**（升级 [`method-directory.tsx`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/components/knowbots/method-directory.tsx)）：彻底告别混排旧非正式原子方法与跨应用折返跑，重构为清晰的 **3 个作者内聚页签**：
     1. **`我的正式方法`**：按 `专家方法 / 工具方法` 筛选展示本人已冻结方法，卡片直接渲染**五要素摘要 + 输入/返回两视图槽位芯片 + 最新版本 + KnowMart 在架状态（未同步 / 自用 / 公开待审 / 公开在架）**，支持一键 **`[基于此版升版 v+1]`**、**`[同步自用 / 提交公开上架]`**、**`[去工作台试用 ↗]`**；
     2. **`已获权共享工具`**：展示从 KnowMart 获取（`FormalAcquisition`）及平台共享的可编排工具积木（仅限合法的 `mcp / a2a / skill_script` 工具），原地完成与本人已安装连接器/Skill 资产的绑定；
     3. **`执行源与技能包`（新增受控服务边界内联代理，终结折返跑！）**：在 `knowlab-backend` 新增作者源代理端点 `PUT/DELETE /api/web/v1/method-directory/sources/{source_id}/versions/{version}`（底层通过已认证 `RuntimeTestClient` 转发至 KnowBench `MethodSkillCenter` 源账本），让作者**在 KnowLab `/methods` 及 `/studio` Step ② 内即可原地上传/编辑 `registered_script` 与 `registered_instruction`、查看已就绪 MCP/A2A 连接与 Skill 包（含 `delivery_terms` 状态）并一键 `[以此源新建工具方法]`**！
   - **`📚 授权资料 (/knowledge)`**：查看本人在 KnowBase 授权给 KnowLab 调测的资料及 `TableFormat` 只读表轴预览。

### 4.2 KnowBench 左边栏底部“方法与技能”（`/workbench/methods`）重构
保留 [`sidebar.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/features/shell/ui/sidebar.tsx#L365-L386) 左边栏底部 `FOOT` 的 **`方法与技能`（`/workbench/methods`）** 一级入口，但彻底重写 [`method-skill-center-section.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/features/methods/ui/method-skill-center-section.tsx#L87-L412)，将原先令人困惑的 **6 个底层工程页签（`formal / planning / sources / installed / native / activity`）收敛重塑为面向用户的 3 个清晰页签**：
1. **`可用专家与工具`（合并升级原 `planning` + `formal`）**：
   - 统一展示当前工作台可直接调用的全部正式专家与工具（含本人自用及从 KnowMart 获取/平台公开在架项）；
   - **用“五要素能力卡 + 两视图槽位规格”取代裸 `sha256` 展示**：展开即可看清它解决什么问题、需要哪些输入槽与资料/连接器授权、返回什么交付物、有几项确定性 V0 核验；
   - **一键行动闭环**：专家卡片带 **`[请这位专家]`**（直入 `expert` 模式准备页绑定资料开跑）；本人名下方法带 **`[去 KnowLab 升版 ↗]`**；页头带 **`[去 KnowMart 选更多专家与工具 ↗]`** 与 **`[去 KnowLab 孵化新方法 ↗]`**。
2. **`本地技能与连接器`（合并打通原 `installed` + `sources`）**：
   - 一屏闭环管理本运行环境的 **MCP / A2A 连接器**（内联直通连接新增/授权与启停开关，不再让人迷失跳锚点）、**已安装 Skill 技能包**（醒目标出是否具备公开交付条款 `delivery_terms`）、以及**本地登记脚本/指令源**；
   - 每个就绪源旁提供 **`[去 KnowLab 封装为正式工具 ↗]`**（通过 `CrossAppLink` 携带 `source_kind & source_id` 直达 KnowLab `/studio/new` 自动预填要素 ②③）。
3. **`调用与授权记录`（升级原 `activity`，收折 `native` 协议细节）**：
   - 按会话与调用树可视化展示正式方法的执行历史、包络预授权回执 vs 单步写动作审批记录、V0 核验通过状态（同时升级会话侧栏 [`formal-method-panel.tsx`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/components/workbench/formal-method-panel.tsx) 展示结构化两视图产出与 V0 核验勾号而非裸 JSON 块）；原 `native`（Codex 底层协议动作列表）收折进页底“开发者协议诊断”折叠栏。

### 4.3 三端 `CrossAppLink`（`destinations.ts`）对齐与 `formal-handoff/v2` 升级
1. **统一刷新三端 `destinations.ts`**（[`knowlab`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-web-frontend/app/lib/cross-app/destinations.ts)、[`knowbench`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-web-frontend/app/lib/cross-app/destinations.ts)、[`knowmart`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/lib/cross-app/destinations.ts)）：
   - 新增标准目的地：`knowlab.studio`（`/studio`）、`knowlab.studioNew`（`/studio/new`，支持 `archetype / source_kind / source_ref / handoff` 参数）、`knowlab.methodDetail`（`/methods`，支持 `method_id / version`）、`knowbench.methods`（`/workbench/methods`）、`knowbench.summonFormal`（`/workbench?mode=expert&formal_method=...`）、`knowmart.formalDetail`（`/knowbots/formal/[listingId]`）、`knowmart.demands`（`/demands/expert`）；
   - 清退失效目的地：`knowbench.review`（随 `branch-route-screen.tsx` 一并退役）。
2. **升级 [`formal_handoff.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/app/application/workbench/formal_handoff.py) 为 `knowlab/formal-handoff/v2`**：
   - 当 KnowBench `FIND_EXPERT` 未命中现成专家，或用户在 `TemporaryPlanning` 即时编排试跑成功后点击“沉淀为正式专家方法”时：
     - **流向 A（去 KnowLab 自己孵化）**：将用户问题、识别到的输入/输出语义槽及 `suggested_plan`（即时编排已跑通的 `Selection` 树）打包送入 KnowLab `POST /api/web/v1/method-drafts/from-handoff`，直接生成一份预填好待确认要素 ① `ExpectedDeliverableSpec` 与要素 ③ 四原语树的 `MethodDraftV2` 草稿（待作者一键确权后即可试跑冻结）；
     - **流向 B（去 KnowMart 发悬赏需求）**：携带问题摘要与期望输入/返回槽规格直跳 KnowMart 专家需求发布框，供持牌卖家以正式方法接单。

---

## 五、 任务四：重构 KnowMart 前后端（Backend + Web + Admin）——终结双轨割裂，打通五要素市场全闭环（根治 `X05–X08`）

围绕 `PublicMethodContract`（五要素公开安全投影 + 两视图规格，**100% 保护卖家私有要素 ③ 内部步骤拓扑、脚本源码与指令提示词不外泄**），将 `FormalListing`（正式专家方法与工具方法）提升为 KnowMart 全链路一等公民：

### 5.1 KnowMart 数据模型与双层类目体系升级（单链线性 Alembic 迁移）
在 [`models/market.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/infrastructure/models/market.py#L298-L356) 上执行向后兼容 `expand` 迁移（同步更新 `knowmart-backend/tests/test_kernel_invariants.py`）：
1. **扩展 `formal_method_listing`（`FormalListing`）**：
   - 新增 `public_contract JSONB NOT NULL DEFAULT '{}'`：由 KnowLab `list_for_self` 与 KnowBench `formal_delivery_review` 同步写入公开五要素投影（① `applies_when / excludes / promises / conditions`、② 消费端所需连接器类型/时机与资料槽数、④ V0 核验算子类型数与盲审标识、⑤ 包络/逐次审批摘要、以及 **`public_inputs` 与 `what_to_return` 两视图槽位规格列表**）；
   - **解耦“资质准入类目”与“目录发现类目”（根治 `X06` 类目报错）**：
     - 保留 `category String(64)` 作为 **`C-L4` 监管资质准入类目**（校验 `CATEGORIES / BY_CODE` 与 `PublisherLicense`，如证券投资咨询类须持对应有效牌照，通用计算工具走非牌照通用工程类目）；
     - 新增 `directory_category String(64) NULL` 与 `domain_tags JSONB NOT NULL DEFAULT '[]'`（提取两视图槽位 `domain_id` 前缀）：承载 `EXPERT_DIRECTORY_CATEGORIES`（含 `analysis.statements` 等）与 `TOOL_CATEGORIES`（`financial.reconciliation` 等）检索分面！`submit_formal_self` 与 `submit_formal` 入库时若尚无人工指定细类，自动将 `suggested_tool_category / suggested_expert_category` 作为初始默认细类落盘（消除未手选细类时的按类检索盲区），并分别校验 `category`（管牌照准入）与 `directory_category`（管目录展示），彻底消除 `invalid_category` 400 阻断！
   - **加固 `method_kind` 历史回填容错与巡检（根治 `W08`）**：升级 [`backfill_formal_method_kinds.sh`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/scripts/backfill_formal_method_kinds.sh#L38-L51)，仅对仍在架记录 `status IN ('listed', 'pending')` 执行硬阻断核查，对已 `withdrawn / rejected` 的孤立历史记录容错跳过并打印告警（不再整表 `RAISE EXCEPTION` 回滚），同时在启动巡检中监测 `status = 'listed' AND method_kind IS NULL`；
   - 新增 `price Numeric(12, 2) NULL`（每次调用/获取使用权的参考标价，`NULL` 为免费，延续平台当前“记账留痕、不扣资金”原则）、`delist_reason String(32) NULL`、`created_at / updated_at`；
   - 升级检查约束 `ck_formal_listing_status`：`status IN ('pending', 'listed', 'withdrawn', 'rejected', 'taken_down')`；新增约束 `ck_formal_incubation_tool_only`：`incubation_scope = 'none' OR method_kind = 'tool'`（从数据库层彻底封堵误将 `expert` 设为跨作者孵化积木！）。

### 5.2 KnowMart Web 前台重构：公开目录、五要素+两视图详情页、小店合一与需求/成交闭环
1. **升级 `/knowbots` 公开目录（[`expert_catalog.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/expert_catalog.py) + [`expert-catalog.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/knowbots/expert-catalog.tsx)）**：
   - 将 `FormalListing` 的死文本 `<article>` 升级为完整交互卡片 `<FormalMethodCard>`：整卡可点进详情页 `/[locale]/knowbots/formal/[listingId]`，展示标题、用途、两视图核心交付槽标签、参考价格/免费标识与所属小店，不再在目录卡片上裸贴冗长 `sha256`；同时在 `go(next)` 中同步重置搜索框 `words` 状态（修复点筛选 Chip `X` 后输入框残留旧词的 `W09`）；
   - **主操作按钮直通双端**：
     - 若从 KnowBench 带着 `return_url` 来请专家：卡片直接提供 **`[请这位专家]`**（未获权的公开专家自动幂等写入 `FormalAcquisition + Trade` 留痕后，按受控回跳地址带 `formal_method=<method_id>@<version>` 返回 KnowBench 直接进入该正式专家准备页！）；
     - 独立逛市场时：专家方法提供 **`[获取并去工作台请他]`**，工具方法提供 **`[获取工具使用权]`**（调 `POST /formal-methods/listings/{id}/acquisitions`，获取后显示 **`[去 KnowBench 使用 ↗]`** 与 **`[去 KnowLab 编排引用 ↗]`**）。
2. **新增正式方法详情页 `/knowbots/formal/[listingId]`（后端新增 `GET /api/web/v1/knowmart/formal-methods/listings/{listing_id}`，前端复用并扩展 [`expert-detail.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/knowbots/expert-detail.tsx) 京东式规格布局）**：
   - 顶部商品主区：方法名、用途、类别徽章、版本选择器（展示该 `method_id` 可见各版）、参考价格、星级评分、所属小店 `ShopLink`、以及主行动按钮（请专家 / 获取工具使用权 / 本人跳 KnowLab 管理）；
   - 底部 **5 个标准页签（由 `public_contract` 驱动，严守私密实现零泄露）**：
     - `能做什么`（要素 ① 适用前提、排除边界、具名承诺与条件规则）；
     - `输入与所需授权`（**视图 A `public_inputs` 槽位名称/语义类型/必填说明** + 要素 ② 所需资料/连接器权限 + 要素 ⑤ 包络/单步审批透明说明）；
     - `交付物与核验保障`（**视图 B `what_to_return` 槽位名称/语义类型** + 要素 ④ V0 确定性核验项与盲审复核标识）；
     - `版本谱系`（在架与历史版本状态；所有者显示 `[去 KnowLab 方法与技能管理]`）；
     - `发布主体与评价`（实名主体与有效行业证照列表、`TradeReview` 买家评价列表）。
3. **打通小店首页、店铺详情与卖家中心合一（[`market.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/market.py) + [`shops.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/shops.tsx) + [`my-shop.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/my-shop.tsx)）**：
   - **店铺可见性补齐**：`shops()` 供给统计 `_activity()` 与 `shop(shop_id)` 店铺详情页同步纳入该店主公开在架且证照有效的 `FormalListing`（展示在架专家数、在架工具数、在架知识数），点击直达 `/knowbots/formal/[listingId]`；
   - **卖家中心 `MyShop` 三合一收口**：将原先碎片化的 `'formalMethods'` + [`my-formal-methods.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/my-formal-methods.tsx) + `'incubation'`（[`incubation-permissions.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/incubation-permissions.tsx)）合并为统一的 **`我的方法与专家`** 主面板（旧 `SCHEMA_V3` 专家仅当存在历史记录时作为兼容折叠区展示）：同一张卡片一站式完成**目录类目设置、监管资质类目+参考价提交公开审核、撤回上架、以及（仅限合规 `tool` 方法）设置跨作者孵化共享范围 `none | acquired | platform`**！
4. **打通需求大厅响应、成交留痕与买家评价（[`market.py`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/market.py) + [`demands.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-web-frontend/app/components/market/demands.tsx)）**：
   - 卖家响应需求大厅（`DemandResponse` / `attach_offer`）支持挂接已公开在架的 `formal_expert` 或 `formal_tool`；
   - 买家获取公开 `FormalListing`（或选定需求响应成交）时，在同一数据库事务中幂等写入 `FormalAcquisition` 与 `Trade`（`kind = "formal_expert" | "formal_tool"`，快照保存当时的 `seller_publisher` 与 `price`），自动打通买家 `TradeReview` 评价与卖方回复闭环！

### 5.3 KnowMart 运营管理后台（`knowmart-admin-frontend` + `MarketAdmin`）合规全闭环（根治 `X08`）
1. **补齐正式方法公开上架审核台（[`market.py:queue/decide_formal`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-backend/app/app/application/services/market.py#L2125-L2210) + [`market-admin.tsx`](file:///home/zym/wsl-worktrees/luna/knowmart-app/knowmart-admin-frontend/app/components/market-admin/market-admin.tsx#L151-L203)）**：
   - `MarketAdmin.queue()` 直接返回待审 `formal_listings` 列表，自动运行 **`flagged()` 违禁词扫描（`C-L5`）** 覆盖 `title`、`purpose` 与 `public_contract` 全部公开文本，并附带发布主体实名与对应 `category` 证照有效性状态；
   - 在 `market-admin.tsx` 的 `ListingReview` 页面新增 **`正式方法（专家与工具）上架审核`** 区块：向审核员清晰展示申请公开的方法类型（专家/工具）、监管类目与目录类目、参考价格、五要素公开能力声明、两视图槽位规格及红色违禁词高亮，审核员一键填写意见执行通过/驳回（调 `POST /formal-methods/listings/{id}/decision`）！
2. **补齐资质撤销、证照过期定时清扫与运营强制/违规下架闭环（严守 `C-L4 / P2-8`）**：
   - **`_withdraw()`（主体或证照撤销）**：当运营撤销发布主体或某类目证照且无其他有效证照时，同一事务内将该主体名下（或该类目下）所有 `scope = 'public'` 且 `status in ('listed', 'pending')` 的 `FormalListing` 即刻回退为 `status = 'withdrawn', incubation_scope = 'none', delist_reason = 'qualification_revoked'` 并写明 `review_note`；
   - **`sweep()`（每日证照过期清扫）**：证照过期未续期时，同步将该类目在架公开 `FormalListing` 置为 `status = 'withdrawn', incubation_scope = 'none', delist_reason = 'license_expired'`；
   - **`take_down()` 与举报核实（`decide_report`）**：新增支持 `kind == "formal_method"`，运营下架后置 `status = 'taken_down', incubation_scope = 'none'`（新买家不可再获取或请用，已在跑的任务不受影响跑完；若勾 `violation=True` 违规下架，同步将该 `listing_id` 关联 `Trade` 标记 `failure = 'violation_taken_down'` 留痕）。

---

## 六、 跨仓契约导出、锁同步与废旧代码精确清退总表

1. **KnowBench ──▶ KnowLab（受管能力契约）**：更新 `knowbench-backend/app/app/domain/workbench/method_capabilities.py`，运行 [`export_method_capabilities.py`](file:///home/zym/wsl-worktrees/luna/knowbench-app/knowbench-backend/app/scripts/export_method_capabilities.py) 刷新 `knowlab-backend/.../managed_capabilities_generated.py`、`managed-capabilities-v1.lock.json` 与 `knowbench-backend/contracts/method-capabilities-v1.json`。
2. **KnowLab ──▶ KnowBench、KnowMart & KnowLab Web（正式方法与公开契约）**：更新 `knowlab-backend/app/app/domain/knowbots/{formal_method.py, slot_vocabulary.py, formal_method_compiler.py, formal_method_plan.py, formal_method_admission.py, formal_method_execution.py, selection.py}`，运行 [`export_formal_method.py`](file:///home/zym/wsl-worktrees/luna/knowlab-app/knowlab-backend/app/scripts/export_formal_method.py) 同步刷新消费端生成代码、Schema 与锁文件，确保 [`verify-contracts.py`](file:///home/zym/wsl-worktrees/luna/sunmoonun/ci/verify-contracts.py#L47-L187) 全绿；同时优化 `--pinned` 对晋级窗口期新增锁文件的提示，并在晋级收口时同步更新 [`sources.yaml`](file:///home/zym/wsl-worktrees/luna/sunmoonun/infrastructure/applications/sources.yaml) 确保 `verify-contracts.py --pinned` 通过（根治 `W10`）；全部跨服务调用必须通过 [`method_transaction_guard.py`](file:///home/zym/wsl-worktrees/luna/sunmoonun/ci/method_transaction_guard.py)“禁持 DB 事务发 HTTP”门禁。
3. **多语言与跨端目的地对齐**：同步更新 `knowlab-web-frontend`、`knowbench-web-frontend`、`knowmart-web-frontend`、`knowmart-admin-frontend`（及 `knowlab-admin-frontend`）的 `messages/{en,zh-CN}.json` 与 `lib/cross-app/destinations.ts`，确保中英键集合 `100%` 对称。
4. **废旧代码精确清退表（新链路切换就绪后清理）**：
   - `knowlab-web-frontend`：清退 `method-template.tsx`（4 文本框假壳）、`p1-predecessor.tsx`、`p2-join.tsx`、`p4-comparison.tsx`、`p5-choice.tsx`、`expert-from-tool.tsx`、`expert-input-binding.tsx`、`delivery-template.ts`；`/methods` 隐藏旧非正式原子方法新建入口；
   - `knowbench-backend / knowbench-web-frontend`：清退外部手工建任务的 `branch_review_dispatch.py` 与 `branch-route-screen.tsx`；清退 `method-skill-center-section.tsx` 旧 6 页签裸 SHA256/协议倾倒视图；
   - `knowmart-web-frontend`：将 `my-formal-methods.tsx` 与 `incubation-permissions.tsx` 收敛并入 `my-shop.tsx` 统一的“我的方法与专家”面板，消除三页签割裂。

---

## 七、 本地 `agy` 工位六批次可验证实施路线图（`PR-1 ~ PR-6`）

经你审阅拍板后，先在本地 `wsl-dev` 将各工位安全对齐至 `luna` 基线（`luna` 未提交文档原样保留不动），随后**全部在本地 `/home/zymun/worktrees/agy` 工位**分 6 个可独立测试验收的批次推进：

| 批次 | 核心目标 | 精确落地文件范围与门禁验证命令 |
| :--- | :--- | :--- |
| **PR-1：五要素+两视图契约底座与四原语编译器重构** | 重塑整体契约模型、公开安全投影与局部正交编译内核 | 1. 升级 `method_capabilities.py` 并运行 `export_method_capabilities.py`；<br>2. 在 KnowLab 落地 `slot_vocabulary.py`（受控词表 + 6 类 `SlotPreset`）、`MethodDraftV2`、`PublicMethodContract`、`S1–S4` 工程样板、可执行 `V0CheckSpec`、分级 `ApprovalRule(envelope/per_action)`、`ProjectionLens`、`CollectPack`、`VerifiedArtifactGuard`、局部 `MapStep` 与局部化 `ReviewPhaseStep`（解除 2/3 步及嵌套互斥硬锁），重写 `selection.py:expand()` 根除倒抄末步与权限重名冲突，落地 `project_contract_state` 与 `verify_envelope_graph`；<br>3. 运行 `export_formal_method.py` 同步双端锁，通过领域单测与 `ci/verify-contracts.py`。 |
| **PR-2：双仓数据库迁移、结构化 `C-L1` 出处账本、旧 v2 收口与公私叶子准入打通** | 打通五要素草稿持久化、JSONB 生成列加固、旧申请清理与公开准入 | 1. KnowLab & KnowBench 单链 Alembic 迁移：扩展 `knowbot_workdraft`（`request_id` 可空 + `method_id / draft_contract / htn_state / parent_gap`）与 `method_version_slots`（删 `hash` 索引，建 `domain_id` `btree` + `gin` 索引）；在 KnowBench 重建 `workbench_capability_vector(jsonb)` 全量加 `jsonb_typeof` 守卫与模糊属性单测（根治 `W02`），同步更新双仓 `test_kernel_invariants.py`；<br>2. 在 `knowbot_board.py` 落地 `is_retired_v2_only_request` 剔除纯退役 v2 空壳申请及旧缺口提问（根治 `W04 / #123`）；落地 `MethodDraftService`（逐要素 `C-L1` 出处写入/核验、分形缺口派生回填、`formal-handoff/v2`）与事务外内联源登记代理（严过 `method_transaction_guard.py`）；<br>3. 修复公私内部叶子交付死锁（同作者 `registered_script / service_function / is_instruction` 已验叶子随父公开专家交付），放宽 `ResourceDelegation` 支持 `1..4` 跳委派；跑通双仓准入测试。 |
| **PR-3：五要素制导 HTN 规划、`SEALED_INPUT` 预算护栏与大目录 GIN 检索修复** | 打通五要素制导规划，根治 `#121/#122` 及大目录 HTTP 风暴 | 1. 注入要素 ① 目标槽与要素 ② 权限上限至 `SelectionService` 与 `HierarchicalPlanner`，落地 5ms 逆向超图剪枝、首轮 Top-K 候选及 `chosen_method()` 契约自动预披露、KnowBase `table_format` 只读表轴直注；<br>2. 调模型前宿主短路 `planner.stale_edit`（根治 `W06`），修复 `reset()` 保留 `self.shown` + `tabu_signatures` + `resolve()` 实时增量守卫（删 `finish()` 炸树）；<br>3. 在 `runner.py` 统一 `is_sealed_planning(task)`（纯无记忆封存线程 + `LookupGuard(remaining)` 盘中熔断，根治 `W03 / #121`）；在 `task_runtime.py` 增设 `MIN_HTN_TURN_SECONDS(25s)` 防末轮超时腰斩并合并 `v5+v7` 单快照流程（根治 `W05 / #122`）；<br>4. 修复 `registry_catalog.py` 删除 `if topics: while more:` 恢复本地 GIN 分批核权、消除 `shared_tools` N+1 事务（根治 `W01`）；跑通规划器与目录检索单测。 |
| **PR-4：包络预授权、V0 确定性门禁与受控前沿惰性执行引擎** | 打通五要素与两视图运行期执行、核验与免连环弹窗闭环 | 1. 严守 `P0` 与 `C-A10`（单 `Task` 单 `active_attempt_id`），在 `formal_orchestration_execution.py` 与 `formal_recursive_runtime.py` 落地 `FrontierState`、`VerifiedArtifactGuard` 惰性剪枝（`SKIPPED_BY_GUARD`）、`$O(1)$` `outputs_index`、强制执行 `evaluate_v0_checks` 及试跑/正式统一的 `ReviewPhaseStep` 有界返工；<br>2. 升级 `FormalHostCalls.request` 与 `formal_evidence.py` 落地 `EnvelopeAuthorization` 包络免弹窗直通与 `per_action/write/send` 单步强批双轨验真；<br>3. 升级 `formal_expert_intake.py` 批量 `planning_definitions` 核权容忍未选项下架（根治 `W07`），升级 `ConsumerPlan`、`formal_expert_preparation.py` 支持按路径 `slot_sources` 绑多账号、精准 `material_slots` 识别与 KnowMart 正式专家召唤解析；跑通 KnowBench 执行取证与 `test_kernel_invariants.py`。 |
| **PR-5：KnowMart 前后端（Backend + Web + Admin）全链路统一重构** | 终结 KnowMart 双轨割裂，补齐市场展示、交易需求与后台合规审核 | 1. KnowMart Alembic 线性迁移：扩展 `formal_method_listing`（`public_contract / directory_category / domain_tags / price / delist_reason` + `'taken_down'` 状态 + `tool` 专属孵化共享约束），加固 `backfill_formal_method_kinds.sh` 孤立历史行容错（根治 `W08`），同步更新 `knowmart-backend/tests/test_kernel_invariants.py`；<br>2. 升级 `knowmart-backend`：解耦监管类目与目录类目并自动落盘初始默认细类，新增 `FormalListing` 详情接口，纳入 `shops / shop` 供给展示，接入 `FormalAcquisition + Trade + TradeReview` 与 `Demand` 响应挂接，补齐 `MarketAdmin` 的 `queue()` 待审正式方法（含 `flagged` 扫描）、`_withdraw()` 撤证回撤、`sweep()` 过期回撤与 `take_down("formal_method")`；<br>3. 升级 `knowmart-web-frontend`（目录 `<FormalMethodCard>` + 修复搜索框 `words` 同步 `W09`、五要素+两视图详情页、店铺页、`MyShop` 三合一面板）与 `knowmart-admin-frontend`（`ListingReview` 正式方法审核台）；跑通 KnowMart `pytest` 与双前端 `tsc / build`。 |
| **PR-6：KnowLab & KnowBench 左边栏“方法与技能”与一体化工作坊前端重构及全栈联调** | 收口双端左边栏、方法与技能中心与创作/运行体验，完成四仓总验收 | 1. KnowLab Web：落地 4 栏精简左边栏、`/studio` 四步五要素一体化工作坊（常驻实时两视图底栏 + 三栏四原语画布 + `SlotPreset` 选择器 + 试跑钉断言 + 分形缺口面包屑栈）与 `/methods` 三合一作者“方法与技能”中心（内联登记脚本/指令源、共享工具绑定、一键送审 KnowMart），清退 `method-template.tsx` 与 `P1–P5` 旧面板；<br>2. KnowBench Web：重构左边栏 `方法与技能`（`/workbench/methods`）为 3 个用户视图（可用专家与工具五要素卡、本地技能与连接器合一管理、调用与授权记录），升级精准资料槽准备页、零手填表头即时编排与树形运行页，清退 `branch-route-screen.tsx`；<br>3. 统一三端 `destinations.ts` 与全部前端 `en / zh-CN` 词条，优化 `verify-contracts.py --pinned` 晋级诊断（`W10`），全量通过四仓 `pytest`（含 `method_transaction_guard.py`）、前端 `tsc / test / build`、`ci/verify-contracts.py` 及跨三端端到端验收。 |

---

## 八、 定稿核心重铸对照小结（全栈深读带来的关键架构闭合）

| 审视维度 | 深读底层代码前的盲区或风险 | 深读四仓全栈源码后的精确工程闭合方案 |
| :--- | :--- | :--- |
| **五要素模板与 `C-L1` 外键链** | 拟另建脱离 `knowbot_workdraft` 的草稿表，会撞断 `source_workdraft_id` 外键并绕开出处门禁 | 原位兼容扩展 `knowbot_workdraft`（`request_id` 可空 + `method_id / draft_contract`）+ 逐要素结构化出处账本（`edit / accept / copy`），外键零破坏且数学级守住 `C-L1` |
| **执行并发、审批与公私叶子** | 拟同 `Task` 开多活跃 `Attempt` 撞 `C-A10`；未发现六连弹窗与内部私有叶子禁公开专家两处死锁 | 严守单 `Task` 单 `active_attempt_id`，采用 `FrontierState` + `SKIPPED_BY_GUARD` 惰性剪枝；落地 `EnvelopeAuthorization` 免连环弹窗；放行同作者已验内部私有脚本/取数/指令叶子随父公开专家整体交付 |
| **KnowLab & KnowBench 左边栏「方法与技能」** | 未覆盖左边栏 9 栏旧流与工作台 6 页签裸 SHA256/协议倾倒场，作者写脚本需跨端折返跑 | KnowLab 收敛为 4 栏导航并在 `/methods` 提供内联源登记代理；KnowBench 左边栏 `方法与技能` 重构为“可用专家与工具（五要素两视图卡）/ 本地技能与连接器 / 调用与授权记录”3 栏，统一三端 `destinations.ts` 与 `formal-handoff/v2` |
| **KnowMart 前后端与市场合规闭环** | 未察觉 `FormalListing` 在市场无详情页、无获取/请专家按钮、不在小店显示、工具类目送审报 400、且 Admin 缺审核界面与撤证/过期/下架联动 | 扩展 `PublicMethodContract`（五要素公开投影+两视图，零泄露内部步骤），解耦监管牌照类目与目录类目，补齐公开详情页、请专家/获取工具、店铺展示、`MyShop` 三合一、需求/成交/评价及 `knowmart-admin-frontend` 审核台与撤证/过期/违规下架全闭环 |
