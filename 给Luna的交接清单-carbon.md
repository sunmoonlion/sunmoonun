# 给 Luna 的收尾交接清单（Carbon · `agy` 独立基准版）

> **工作位置说明**：本轮 `PR-1 ~ PR-6` 重构、交接前边界加固、测试回归与 Git 提交均在 **本地（`wsl-dev`）** `/home/zymun/worktrees/agy` 工位完成，未推送远端，未改动 `luna` 工位。Luna 可直接从下列 `agy` 分支精确提交号建立隔离副本独立复验。

---

## 一、怎样重建这一版？（分支、提交号、迁移与契约锁）

### 1. 涉及仓库与 25 个组件确切提交（全部位于 `agy` 分支，工作区 `dirty=0`）

| 仓库路径（相对 `/home/zymun/worktrees/agy/`） | 分支 | 本轮前基线 SHA | 收尾固化 HEAD SHA | 本轮变更说明 |
| --- | --- | --- | --- | --- |
| `sunmoonun` | `agy` | `208d2de575b544b1c14c691768bf8960ec4bf168` | 见本清单提交（前序代码门禁提交 `ab11f48d6dbb2731da5bd3b3c7b77899e7be08ed`） | `ci/verify-contracts.py`（`W10` 晋级窗口诊断提示、管理端 i18n 对称门禁）、重构方案与本交接清单 |
| `knowlab-app` | `agy` | `7c18a9e6bc915639c1006652dd2d9bace065437e` | `3c6f75744ccff64b0895df6fa39edb6666ad60e7` | `contracts/formal-method/v1/*`、`contracts/knowbot-incubation/v1/*` 及前后端子仓 gitlink |
| `knowlab-app/knowlab-backend` | `agy` | `7d518645992d2ce26930db5a6cf43ad8082c6172` | `5c1ad30d02951f8768135ed73c41d1042b635dc0` | 五要素 + 双视图契约 `MethodDraftV2`、槽位词表、出处确认工作台接口、缺口移交 v2、迁移 `20261126_0030` |
| `knowlab-app/knowlab-web-frontend` | `agy` | `b681780fdcf8446900516e1a2d8f19802aac0eee` | `36c13daea4a3204da629481016985525668be5c2` | 左侧栏 4 主项 + 历史归档折叠、`/studio` 五要素方法工作室、`/methods` 统一目录、生成前端契约锁 |
| `knowlab-app/knowlab-admin-frontend` | `agy` | `89fe3ac1f6178018186584db7542f11102896381` | `89fe3ac1f6178018186584db7542f11102896381` | 未改动 |
| `knowbench-app` | `agy` | `53ebdca24a34643f5ada0f425cf36419a8cb584f` | `7db654728697a89860584a593b228f158669dc3c` | `contracts/dynamic-methods/*`、`contracts/knowlab-incubation-lock.json` 及前后端子仓 gitlink |
| `knowbench-app/knowbench-backend` | `agy` | `984fd50157cef2a77752e853628adf72bf45760d` | `2ec1c338c2f1b3941c44f55470fa50a4f887c040` | 包络预授权、局部前沿条件门禁与透镜归集、单层及递归根/子专家 V0 核验、HTN/立项批量降级、迁移 `20261126_0063` |
| `knowbench-app/knowbench-web-frontend` | `agy` | `6c96e4386477ec2aa08e509b157a4de0752ac428` | `88514dd74794aa03e87f60ff07e2fdab23b8eaf1` | `/workbench/methods` 三视图收敛（折叠诊断）、立项包络预授权与缺口移交 v2 界面、跨应用 snake_case 目标 |
| `knowbench-app/knowbench-admin-frontend` | `agy` | `33559e926c3ebb7570716d5bb318b5a014e0d645` | `33559e926c3ebb7570716d5bb318b5a014e0d645` | 未改动 |
| `knowmart-app` | `agy` | `1a849d7498632dad1b1c25774ebdd9667d2630cd` | `812f9995b8847fc4610542ddc5f12fff90bdbbcf` | 后端、Web、Admin 三子仓 gitlink |
| `knowmart-app/knowmart-backend` | `agy` | `fbf1e4d1bd0c3c7951338985cff442b2c5c93cc1` | `fd162a5db8dc05eb2cfa6474ece319908ae9f7cd` | 正式工具/专家统一上架、资质类目与目录细类解耦、成交与需求闭环、否定子句防误报 C-L5 扫描、迁移 `20261126_0021` |
| `knowmart-app/knowmart-web-frontend` | `agy` | `b55591d55b2bb666ee55792424d596dd8036af9b` | `7bafcc75bad99acbf90c8e03f06badbf98c0284b` | `/knowbots/formal/[listingId]` 五栏公开契约详情页、`MyShop` 正式供给合并、`W09` 目录搜索修复 |
| `knowmart-app/knowmart-admin-frontend` | `agy` | `5f109118ffbaca623a732ed33eaea61a2905241a` | `6badf80be1d4aecd831bd02581f2af45300c4445` | 运营端 `formalListings` 正式方法待审队列与风险词徽标审核 |
| `knowbase-app` | `agy` | `00b59ec8b5391fbf3fa54bfd9ebf4d7fc2a5e54a` | `00b59ec8b5391fbf3fa54bfd9ebf4d7fc2a5e54a` | 未改动 |
| `knowbase-app/knowbase-backend` | `agy` | `a30b375fc4850dacf163820290bf1454497ff8d2` | `a30b375fc4850dacf163820290bf1454497ff8d2` | 未改动 |
| `knowbase-app/knowbase-web-frontend` | `agy` | `884d235418f63676a88002978bf99bd99112cdb1` | `884d235418f63676a88002978bf99bd99112cdb1` | 未改动 |
| `knowbase-app/knowbase-admin-frontend` | `agy` | `f2f6df3163a01c71be13efdd20b87187b63693ec` | `f2f6df3163a01c71be13efdd20b87187b63693ec` | 未改动 |
| `knowfeed-app` | `agy` | `a60f63a25ece47dbf87dd38ba5ac06e1082bc71a` | `a60f63a25ece47dbf87dd38ba5ac06e1082bc71a` | 未改动 |
| `knowfeed-app/knowfeed-backend` | `agy` | `1ed7151b14ced67161869834d7a62583512f4324` | `1ed7151b14ced67161869834d7a62583512f4324` | 未改动（见第四节数据链待办单列） |
| `knowfeed-app/knowfeed-web-frontend` | `agy` | `f49953404ed46fa007a4db40ae5c7b7519af3419` | `f49953404ed46fa007a4db40ae5c7b7519af3419` | 未改动 |
| `knowfeed-app/knowfeed-admin-frontend` | `agy` | `1bdcbcd042a45a0d19de1787778fd78f96cf49b6` | `1bdcbcd042a45a0d19de1787778fd78f96cf49b6` | 未改动 |
| `tpl-app` | `agy` | `6d78e4cb110289c2490e62063c2bb4769bff6f51` | `6d78e4cb110289c2490e62063c2bb4769bff6f51` | 未改动 |
| `tpl-app/tpl-backend` | `agy` | `09779706aa9ae28b3f89aa325663b3d056a7fddf` | `09779706aa9ae28b3f89aa325663b3d056a7fddf` | 未改动 |
| `tpl-app/tpl-web-frontend` | `agy` | `ab68ebc5d6d6afe8a80ab4178554b61f388a4fc6` | `ab68ebc5d6d6afe8a80ab4178554b61f388a4fc6` | 未改动 |
| `tpl-app/tpl-admin-frontend` | `agy` | `722c6b80e849d6352f28abbdd7362e1151191c14` | `722c6b80e849d6352f28abbdd7362e1151191c14` | 未改动 |

### 2. 数据库迁移、存量回填与契约生成位置

1. **Alembic 数据库迁移头（3 个后端新增迁移）**：
   - `knowlab-backend`：`app/alembic/versions/20261126_0030_method_draft_v2_and_slot_domains.py`（建 `method_drafts` 表并为 `knowbot_workdrafts` 增补 `draft_contract` 列）。
   - `knowbench-backend`：`app/alembic/versions/20261126_0063_safe_capability_vector.py`（`pg_trgm` 与可选 `pgvector` 安全回退初始化，未装 `vector` 扩展的普通 Postgres 实例亦可正常升级）。
   - `knowmart-backend`：`app/alembic/versions/20261126_0021_formal_market_unification.py`（`formal_listings` 增补 `domain_tags` GIN、`public_contract` JSONB、`ck_formal_incubation_tool_only` 工具专属孵化授权约束，以及 `trades.kind` 正式工具/专家成交枚举）。
2. **存量数据回填脚本**：
   - `knowmart-backend/app/scripts/backfill_formal_method_kinds.sh`：迁移后按需执行，为存量 `formal_listings` 补齐 `method_kind` 与 `public_contract`（仅对 `status IN ('listed', 'pending')` 缺失项阻塞报错，历史已撤回/下架条目仅输出 `WARNING`）。
3. **生成契约与锁文件（均已导出并纳入上述提交）**：
   - KnowLab 提供方导出脚本：`knowlab-backend/app/scripts/export_formal_method.py`（同步生成 `knowbench-backend/app/app/domain/workbench/*_generated.py`、`knowbench-backend/app/contracts/formal-method-lock.json` 与 `knowlab-web-frontend/app/contracts/formal-method-provider/lock.json`）。
   - 跨仓契约总校验：`python3 sunmoonun/ci/verify-contracts.py`（校验全部跨应用 JSON Schema、契约锁哈希及 6 应用 Web/Admin 中英文 i18n 键对称，当前返回码 `0`）。

---

## 二、用户从哪里进？（三条主入口、前置条件与 `sig-am` 存量稿承接）

### 1. 作者入口：从一句声明到确认、试跑与冻结（含 `sig-am` 存量迁移路径）

- **新建五要素方法入口（推荐新流程）**：
  - 路由：KnowLab Web `/[locale]/studio` -> 选择 `S1–S4` 工程样板（或空白工具/专家草稿）创建 -> 进入 `/[locale]/studio/[methodId]`。
  - 关键交互：编辑五要素（能力声明、访问上限、过程绑定、验证规则、审批分类）-> 对 AI 预填建议逐项点击确认以清空 `unconfirmed_paths` -> 右侧实时查看 `project_contract_state` 派生的对客输入/返回双视图、`missing_promise_sources`（未绑定来源的承诺项）与闭环检查 -> 发起试跑并冻结不可变版本。
- **存量工作稿承接入口（`sig-am` 的申请 `89a22950-0521-4913-971a-8feea6b2885f`）**：
  - 账号：`sig-am`。
  - 路由：KnowLab 左侧导航栏展开底部折叠组 **「历史兼容归档」 -> 「申请」**（`/[locale]/applications`），点击申请 `89a22950-0521-4913-971a-8feea6b2885f` 进入 `/[locale]/names/89a22950-0521-4913-971a-8feea6b2885f/workdraft` 与 `/[locale]/names/89a22950-0521-4913-971a-8feea6b2885f/formal-method`。
  - 承接保证：`knowbot_board.py` 仅过滤“只有退役 `knowbot-manifest/v2` 草稿且无活动工作稿”的历史空壳；凡工作稿含 `steps`、`method_refs`、`method_template`、`planning`、`formal_method` 或 `draft_contract` 的申请一律完整保留。`sig-am` 可原样读取修订 4 的承诺原文、负基数业务口径、采纳依据及已冻结的四项引用（`F1 v1`、`F2 v1`、`F4 v1`、报告成稿 `v2`），在补齐 `F3` 自用冻结后重拟根图、试跑并冻结自用。
- **前置条件**：
  - 账号已在 KnowBench 绑定在线环境（`environment.status = "online"`）与沙箱；
  - 所引用的直接工具源（本地直接脚本/指令、已安装 Skill、MCP/A2A 连接器或受管数据函数）已在 KnowLab `/[locale]/methods` 或 KnowBench `/[locale]/workbench/methods` 登记且具备有效 `SourceLicense`。

### 2. 工作台入口：从具体问题到匹配/即时编排、立项授权与正式运行

- **路由**：KnowBench Web `/[locale]/workbench?mode=expert` 或项目内 `/[locale]/workbench/projects/[projectId]/expert/new`（支持自然语言直接提问，或携带 `?formal_method=<method_id>@<version>` 点名调用）。
- **流转步骤**：
  1. 提交问题触发 `FIND_EXPERT`（profile v5）检索当前获权目录；
  2. **命中候选**：在候选对比卡片确认专家版本 -> 进入执行准备页（`formal-expert-preparation`），绑定 KnowBase 受管资料版本、为多步连接器选择对应本地连接资产（`slot_sources`）、预览立项包络预授权（`envelope_approved`，仅限非写操作）与单步外发审批项 -> 启动 `FormalOrchestrationExecution` 正式运行，产出 `expert_delivery` 交回物与确定性 `v0_checks` 核验记录；
  3. **目录无匹配（`no_match`）**：可在项目内发起有界即时编排（`temporary_planning`，最多 3 轮目录检索/澄清），或通过 `formal-handoff`（v2 载荷）把缺口草稿种入 KnowLab `/[locale]/studio/[methodId]` 转正式孵化。
- **前置条件**：当前会话已归属具体项目、项目机器在线；若步骤读取受管资料则需在 KnowBase 持有 `live` 资料授权；若含单轮指令推理步骤则需具备活跃模型凭证、费率表与充足案例预算。

### 3. 市场入口：自用登记、公开上架、运营审核与买家获取/请用

- **作者自用登记**：KnowLab Web `/[locale]/methods` -> 选择已冻结的正式工具或专家版本点击「登记自用」-> 经 KnowBench 提取试跑样本做轻审（`output_findings`）后写入 KnowMart `scope="self"` 条目。
- **卖家公开上架与孵化授权**：KnowMart Web `/[locale]/shop`（「我的小店」统一管理正式专家与正式工具）-> 选择受监管资质类目（如 `tools.calculator` / `finance.securities_advisory`）与发现目录细类（如 `financial.reconciliation` / `analysis.statements`）提交公开审核；公开在架的正式工具可单独设置孵化引用许可（`none` / `acquired` / `platform`）。
- **运营审核队列**：KnowMart Admin `/[locale]/market/listings` -> 在「正式方法上架审核」栏核对五要素公开契约摘要与 C-L5 风险词提示，执行通过、驳回或违规下架（违规下架同步将历史成交标为 `revoked`）。
- **买家获取与调用**：KnowMart Web `/[locale]/knowbots`（切换专家/工具目录）-> `/[locale]/knowbots/formal/[listingId]`（查看能力声明、输入返回、访问权限、验证摘要、评价五栏详情，不暴露私有步骤）-> 点击获取（幂等写入成交并自动关单已选需求响应）-> 点击「请这位专家」经 `formal_summon_return` 跳回 KnowBench 工作台。
- **前置条件**：跨用户体验公开市场需开启配置 `PUBLIC_MARKET_ENABLED=true`；卖家小店为 `open` 且发布主体实名审核通过（金融持牌类目另需有效未过期证照）。

---

## 三、你已经证明了什么？（分批验证明细、三个核心架构问题核实与代表性样例）

### 1. `PR-1 ~ PR-6` 完成范围与实跑验证结果

| 验证层级与目标 | 在 `wsl-dev` 执行的命令 | 实跑结果 | 验证性质说明（真入口 vs 领域/替身） |
| --- | --- | --- | --- |
| **KnowLab 后端**（`PR-1/2/3` 五要素契约、出处工作台、移交 v2、看板过滤） | `cd knowlab-app/knowlab-backend/app && uv run --no-sync pytest -q tests/test_five_element_contract_v2.py tests/test_pr2_drafts_provenance_board.py tests/test_pr3_handoff_v2_and_selection_guidance.py tests/test_author_selection.py tests/test_kernel_invariants.py` | **27 passed** | 含 FastAPI 路由级接口测试（`method_drafts` 创建/确认/冻结门禁、移交 v2）与领域编译器/不变式测试；底层存储使用内存替身，未连真 Postgres |
| **KnowBench 后端**（`PR-2/3/4` 委派锁、HTN 规划、条件前沿与透镜归集、单层及递归根 V0 门禁、立项批量降级） | `cd knowbench-app/knowbench-backend/app && uv run --no-sync pytest -q tests/test_pr2_delegation_delivery_vector.py tests/test_pr3_htn_sealed_budget_and_directory.py tests/test_pr4_envelope_v0_frontier_and_intake.py tests/test_hierarchical_planning.py tests/test_formal_orchestration_admission.py tests/test_kernel_invariants.py` | **87 passed** | 覆盖编排驱动器状态机、递归 `settle_ancestors`、封存证据重算与立项应用服务；存储层使用轻量替身，真库 `@pytest.mark.db` 用例待注入 Postgres 复跑 |
| **KnowMart 后端**（`PR-5` 正式工具/专家统一市场、类目解耦、否定防误报、回填脚本） | `cd knowmart-app/knowmart-backend/app && uv run --no-sync pytest -q tests/test_pr5_formal_market_unification.py tests/test_expert_catalog.py tests/test_expert_routes.py tests/test_market_routes.py tests/test_kernel_invariants.py` | **36 passed, 2 skipped** | FastAPI 路由测试（`test_expert_routes.py`、`test_market_routes.py`）走真实 HTTP 路由层；`test_pr5` 中 2 条 `ShopWorld` 真库集成测试因本地未设 `DELIVERY_TEST_DATABASE_URL` 自动跳过，另 2 条非 DB 单测（工具细类预检、否定子句防误报、回填脚本语法与活跃门禁）直接通过 |
| **KnowLab Web 前端**（`PR-6` 左侧栏、`/studio`、`/methods`、跨应用链接） | `cd knowlab-app/knowlab-web-frontend/app && pnpm run typecheck && pnpm run check:i18n && pnpm exec vitest run` | **43 suites / 372 passed**（1816 对称键） | React Testing Library 组件交互与路由跳转实测 |
| **KnowBench Web 前端**（`PR-6` 三栏方法中心、包络授权、移交 v2） | `cd knowbench-app/knowbench-web-frontend/app && pnpm run typecheck && pnpm run check:i18n && pnpm exec vitest run` | **66 suites / 488 passed** | React 组件交互测试 + `feature-boundaries` 架构边界门禁 |
| **KnowMart Web & Admin 前端**（`PR-5` 五栏详情页、`MyShop`、`W09` 搜索、正式方法审核台） | `knowmart-web-frontend` 与 `knowmart-admin-frontend` 分别执行 `typecheck && check:i18n && vitest run` | Web **21 suites / 144 passed**；Admin **13 suites / 51 passed** | React 组件级渲染、筛选重置（`W09`）与运营审批请求实测 |
| **跨仓契约与翻译对称门禁** | `python3 sunmoonun/ci/verify-contracts.py` | **exit 0** | 真实扫描全仓 Schema、契约锁哈希与 6 应用 Web/Admin 翻译键对称 |

### 2. 对三个核心架构问题与三项中途观察的核实说明

1. **`B03`（两项独立交付能否完整成图，缺一项时确认前指出哪项承诺无来源）**：
   - 在 KnowLab 五要素草稿中声明两项独立交付（如 `detail_table` 明细表 + `reconcile_check` 核对结果）并由两个工具分别产出时，根 `Orchestration.exports` 可同时导出两项结果；
   - 若过程图只绑定其中一步，确认/冻结前 `project_contract_state` 返回 `ready_to_freeze: False`、`closure_checks.deliverables_aligned: False`，并通过新增的 `missing_promise_sources` 字段精确列出尚未绑定有效输出源的 `promise_id`（见 `test_five_element_contract_v2.py` 中 `test_b03_two_independent_deliverables_identify_missing_promise_source`）。即时编排侧（`temporary_planning`）的现场大模型成图表现留待双方按同一题实测比对。
2. **`B410`（市场回执究竟证明了哪个版本）**：
   - KnowLab `FormalMethodService.list_for_self` 与前端 `submitSelfListing` 均严格比对回执 `result["reference"] == {method_id, version, digest}`、`scope == "self"` 及有效 UUID `listing_id`，缺版本或摘要不符直接拒绝（抛 `BadGatewayError`），作者状态不会变为成功；
   - KnowMart `submit_formal_listing` 按 `(owner_subject, method_id, version, scope)` 唯一键幂等写入，相同摘要重试只保留同一条有效交付，不同摘要冲突返回 `formal_listing_conflict`。
3. **递归根专家是否验收自己的承诺（交接前已定位并补齐）**：
   - 交接前复查确认：此前单层编排专家在收口时执行了根 `export_outputs` 与 `evaluate_v0_checks`，但含子专家的递归组合计划（`recursive_plan(snapshot) == True`）在 `settle_ancestors` 收口时未执行中间子专家与根专家的 `evaluate_v0_checks`；
   - 本版已在 `knowbench-backend` 的 `formal_recursive_runtime.py`（`settle_ancestors`）与 `formal_orchestration_execution.py`（`finish`）补齐该验收门：当所有叶子各自通过，但根报告缺少必交导出或违反根声明的确定性业务断言（`v0_checks`）时，根 `Task` 确定性转为 `TaskState.FAILED`（`reason.code` 区分 `export_validation_failed` 与 `v0_validation_failed`，`message` 指明具体 `promise_id`），已完成叶子的 `Attempt`、产物与实耗费用完整保留，未完成祖先调用收口为 `failed`；试跑 `record_case` 亦保留该精确失败原因（见 `test_pr4_envelope_v0_frontier_and_intake.py` 中 `test_recursive_root_expert_enforces_root_v0_checks_and_exports`）。
4. **三项中途观察的处理状态**：
   - **工具目录细类在 KnowMart 上架预检被拒**：已修复。原 `submit_formal` 预检调用 `resolve_formal_categories(..., method_kind=None)` 时误将候选集固定为专家目录表，现 `method_kind=None` 预检阶段接纳工具与专家全集，待拉取冻结定义 `method_kind` 后再按精确类型复核。
   - **否定句“不做投资买卖评级”被标为含“评级”**：已修复。`knowmart-backend` 的 `flagged()` 已改为按句逗分句识别否定免责前缀（支持顿号并列否定如“不提供荐股、目标价或收益承诺”，同时对“不做评级，但保证收益翻倍”转折子句和“并非不做买入评级”双重否定照常标出），且运营队列不再对整段 `public_contract` 做裸 JSON 字符串拼接。
   - **剩余预算不足时运行中熔断与供应方最后结算可能给出不同结果**：本轮未改动 `ledger.py` / `instruction_requests.py` 现有预留（`quote["maximum"]`）与迟到账单（`record_late_cost`）结算口径，留待 Luna 在本收尾版上实测复核后再定是否调整。

### 3. 最能代表本轮成果的完整业务样例

- **代表性样例：`S1 / M02` 财报三表勾稽核验（工具 -> 组合专家 -> 市场 -> 委托人运行）**
  1. **孵化**：作者在 KnowLab `/studio` 选 `S1` 核算核验样板，声明两项交付承诺（科目勾稽明细表、恒等容差核验回执）及否定边界“不做投资买卖评级”，逐项确认 AI 建议清零未确认路径，绑定勾稽计算工具并配置 `NumericIdentityCheck`（资产 = 负债 + 权益容差核对）与 `ProhibitedTermsCheck`；
  2. **试跑与冻结**：经 KnowBench 跑过正反测试集生成封存证据后冻结为 `v1`；
  3. **市场流转**：在 KnowLab `/methods` 一键登记自用，或在 KnowMart `/shop` 以 `financial.reconciliation` / `analysis.statements` 目录细类公开上架，运营在管理端看到“不做投资买卖评级”不再误报风险词并审过；
  4. **委托执行**：获权用户在 KnowBench 工作台点名或提问命中该专家，在准备页完成包络预授权后一键跑完，最终拿到 `expert_delivery` 产物、叶子工具调用链证据及根级 `v0_checks` 全绿核验单（若篡改输出破坏资产负债恒等或混入荐股词，根任务确定性判 `v0_validation_failed` 失败）。

---

## 四、还有什么不确定？（已知边界、发布依赖与第 16–18 项数据链待办）

### 1. 待真库/真机现场复验项与已知边界

1. **真库集成测试待注入 `DELIVERY_TEST_DATABASE_URL` 复跑**：
   - 本地收尾验证未注入共享或临时 PostgreSQL 连接串，因此三端带 `@pytest.mark.db` / `db` 夹具的真库测试（包括 `knowmart-backend/app/tests/test_pr5_formal_market_unification.py` 中的 2 条 `ShopWorld` 全链路事务用例）在本次本地回归中处于 `skipped` 状态，请 Luna 在隔离 Postgres 副本上打开 `DELIVERY_TEST_DATABASE_URL` 实测。
2. **`B30` 用户手动翻目录分页的标签读取路径尚未下推**：
   - AI 规划查候选已走有界窗口（`planning_window` / `shared_tools` 最多 5 页 500 项），但用户手动浏览目录使用的 `knowbench-backend/app/app/application/workbench/directory_browse.py` 为保持全量类目计数语义（见存量真库测试 `test_planning_window_recall_db.py`），翻页时仍按 100 条批次循环向 KnowMart 拉取 `directory_labels`。该项留作下一阶段 587 台账的跨服务聚合优化项。
3. **运行器当前明确拒绝或受限的编排图形**：
   - 不支持运行期动态重规划（`Orchestration.max_replans` 必须为 `0`）；
   - 不支持根级 `object_batch` 与步骤级局部 `step_batch` 在同一张编排图中混用；
   - 独立盲审与返工（`collaboration` + `ReviewComparison`）仅支持单层根编排图（`max_reworks <= 2`），不支持作为递归子专家内嵌在深层子树中；
   - 立项包络预授权（`envelope_approved`）严格排除一切 `effect == "write"` 的外部动作，外部写发步骤在运行期仍强制弹出逐次单步审批。

### 2. 数据库迁移、回填与契约锁发布顺序

1. 按顺序执行数据库升级：`knowlab-backend`（至 `20261126_0030`） -> `knowbench-backend`（至 `20261126_0063`） -> `knowmart-backend`（至 `20261126_0021`）。
2. 若目标库存在历史 `formal_listings` 记录，执行 `knowmart-backend/app/scripts/backfill_formal_method_kinds.sh` 回填 `method_kind` 与 `public_contract`。
3. 开发分支校验执行 `python3 sunmoonun/ci/verify-contracts.py`；待候选通过评审准备向共享环境提请发布卡时，同步更新 `sunmoonun/infrastructure/applications/sources.yaml` 中的父子仓 SHA，并执行 `python3 sunmoonun/ci/verify-contracts.py --pinned` 做晋级锁校验（`W10`）。

### 3. 另行跟踪的数据链待办现状单列（第 16–18 项）

按《给 Carbon 的建议》第五节要求，单独列出 `agy` 工位当前在数据链三项待办上的真实状态（本轮 `PR-1 ~ PR-6` 聚焦专家孵化、编排与市场重构，未改动 `knowfeed-app` 与 `knowbase-app`）：

| 待办编号 | `agy` 当前提交与代码现场 | 本轮是否改动 | 后续完成判定基准 |
| --- | --- | --- | --- |
| **16 · Wind 财务数据口径与预匹配 v2（SDD 0051）** | `knowfeed-backend` 停在 `1ed7151b14ced67161869834d7a62583512f4324`（含早期 `d0552d1` 0051 §2.3 需求项接收与 `3390ee5` Wind 令牌整理） | **未改动（沿用原实现，保留为数据链待办）** | 用留存错回包做回归：请求单季却回累计值时拒绝登记为单季事实并验证转巨潮取回原行；核对 MCP 初始化通知与工具目录缓存；按 0051 §2.5 第 6 步输出有序候选渠道、取法与许可档统一契约 |
| **17 · 旧采集与入库链清理** | `knowfeed-backend` 中 `app/app/interfaces/endpoints/info_routes.py` 与 `app/app/application/messaging/delivery_handlers.py` 仍在调用 `info_crawl_service` | **未改动（保留为数据链待办）** | 梳理全部调用者、旧检索身份与替代路径，按清单迁移清理并从 API 发起采集验证到投递、入库与重试，回执列明已移除与保留项 |
| **18 · 数据链修复的跨应用交付** | 当前无覆盖上述 16、17 项的最终跨仓锁版与发布回执 | **未涉及（待 16、17 项实施后单列交付）** | 在 16、17 项落地后固定 KnowFeed、KnowBase、KnowBench 等消费方版本与契约锁，交回归证据由 Luna 复审汇总发布卡、Cursor 部署、Luna 现场业务验收 |
