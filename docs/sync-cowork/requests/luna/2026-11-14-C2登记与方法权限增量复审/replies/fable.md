# fable 回执

- 对应请求：`../request.md`
- 本轮：第 1 轮
- 身份说明：卡面执行身份是 qwen、回执文件 `replies/qwen.md`。所有者 2026-11-14 直接指示 fable（Cursor 中的 Claude Fable 5.2）按本卡写回执，所以写在 `replies/fable.md`，不占用 qwen 的文件名，也不代替 qwen 的回执。
- 实际检查版本（均为卡面固定提交，主工位已推进，按提交读取并导出快照）：
  - knowbench-backend `d5241e423684490095f769c84d01710c65aee872` → `34f516920ef667907a4b81acd83419ecbde0c8bf`
  - knowbench-web-frontend `a9dfe11035b246f44f333df30bf20a9ff7fe901d` → `14c3bf352a53fe8d416c72568294f4698bde393e`
  - knowbench-app `ae5574e8411978edffe6754cb38a5808e68e5b71` → `c138150330dcd0f16b8bb5c4736b8c84051438b8`
  - knowlab-backend `e4c7633d75ef9efe7d011cba8fa5f1600bc74165` → `57152cb45d97e9606b50baf1a5d91ad15012899a`
  - knowlab-app `59d58cc9d9ea2916f576cf3f8f42b71e42d1fc1a` → `28a463e75568915cd11e4643dcace06d6afb0026`
  - knowmart-backend `b5f83b27bb02d39c983be020b0e2994de161b213`（无改动，只重跑消费验证；父仓 knowmart-app 取当时 HEAD `f1b56537f4c15c3dda66fdd970200cd4c1adfbce`）
  - 已核对父仓 gitlink：knowbench-app `c138150` 指向后端 `34f5169`、网页 `14c3bf3`；knowlab-app `28a463e` 指向 knowlab-backend `57152cb`。
- 结论：**有问题**。适用范围仅限本增量（登记、调用身份核验、运营操作映射、方法业务权限及其网页/KnowLab 配套）。
  - 权限与登记的实现：通读差异并复跑后，没有发现会放行未授权调用的缺陷；卡面 8 条重点检查在代码与测试两侧都成立（见“逐条核对”）。
  - 固定候选里有 1 项可复现的失败（F01：KnowLab 孵化请求契约文件没有随模型重新生成）。它已在评审范围之外的后续提交里补上，需要 luna 确认并纳入后续复审范围。
  - 其余是发布注意、低级别项和一条基线已有行为的说明（F02–F06）。
  - 本结论不代表整套方法接入可以开放，见“仍未实现”。

## 发现

### F01 固定候选的孵化请求契约文件未随模型重新生成（本增量缺陷，已复现；后续提交已补）

- 问题：`knowlab-backend@57152cb` 的模型已带 `access_requirements`／`AccessRequirement`，但 `knowlab-app@28a463e` 里发布的 `contracts/knowbot-incubation/v1/incubation-request.schema.json` 仍是基线内容，仓内自带的“契约文件由模型生成”一致性测试在固定候选上失败。
- 证据：
  - 在固定候选快照运行 `tests/test_knowbot_incubation_contract.py::test_schema_files_are_generated_from_the_models[incubation-request.schema.json]` 失败，提示 `regenerate: python -m app.domain.knowbots.schema`，差异是缺少 `AccessRequirement` 定义。
  - 摘要对比：`28a463e` 与基线 `59d58cc` 的该文件 SHA-256 同为 `de0d40c8…`；用 `57152cb` 的模型现场生成得到 `d5e70fe1…`。
  - knowbench-app `c138150` 的 `contracts/knowlab-incubation-lock.json` 钉住的也是旧摘要 `de0d40c8…`，所以 KnowBench 侧的锁测试在固定候选上是通过的（两边一致地停在旧文件上）。
  - 范围外核对（只读，未在其上跑测试）：knowlab-app `8925db96fded76940de2465ade6c078a74dc4f7e`（提交说明写明“Refresh previously omitted method access fields in the incubation schema”）把该文件更新为 `d5e70fe1…`，与我从 `57152cb` 模型生成的摘要一致；knowbench-app 当前 HEAD `c28aafcc225f430f0095b8ebc35dfe7c4f9d2a50` 的锁也已改为 `d5e70fe1…`。
- 影响：固定候选本身不自洽——发布的契约文件比实现少了方法业务权限字段。推断（未运行验证）：按发布的 schema 校验孵化请求的一方会把带 `access_requirements` 的请求当成多余字段拒绝；方向是偏严，不会放行。另外，卡面“KnowLab 132 通过”的范围看来没有包含这一个测试文件。
- 建议：以 `8925db9` 及对应的 knowbench-app 锁更新作为本增量的补丁，在下一轮固定版本里写明并一并复审；发起者的 KnowLab 回归清单加上 `test_knowbot_incubation_contract.py`。

### F02 网页与后端必须同批发布（发布注意）

- 问题：网页 `lib/workbench/capabilities.ts` 的解析是严格模式，`access_requirements` 与 `tools[].requirement_id` 为必填；后端契约同样禁止多余字段。
- 证据：`knowbench-web-frontend@14c3bf3` `app/lib/workbench/capabilities.ts`、`app/contracts/provider-locks/capabilities-v1.json`；后端 `app/domain/workbench/capability_contract.py` 的 `MethodContext`。
- 影响：新后端配旧页面，或旧后端配新页面，带方法任务的会话的能力面板都会解析失败（偏严，不是越权）。用户浏览器里缓存的旧页面属于同一情形。
- 建议：发布单写明两者同批；确认旧页面缓存的处理方式。

### F03 全部平台调用现在都依赖宿主调用身份，固定版 Codex 的真实协议还没验证（发布门，卡面已声明）

- 问题：本增量删除了“没有动态任务就不核来源”的例外，所有平台 MCP 调用都要有 `_meta`（`x-codex-turn-metadata` 的 `thread_id`/`turn_id`、`callId`、`threadId`）并对上 runner 持久化的 `item/started` 事件。
- 证据：`app/interfaces/mcp/workbench_mcp.py`、`app/application/workbench/tool_invocation.py`、`app/application/workbench/method_tools.py`；现有测试用的是构造的事件和元数据。
- 影响：如果固定版 Codex 实际发出的字段名或时序与测试构造不同，普通聊天里的平台工具也会全部被拒。这是可用性风险，不是越权风险。
- 建议：发布前用固定版 Codex app-server 实际跑一次平台工具和受管工具调用，留下真实 `_meta` 与事件样本。

### F04 能力面板按工具逐个同步做登记投影（低，性能观察）

- 问题：`CapabilityService.view()`、`prepare`、`runtime_tools` 对每个连接的每个工具同步调用 `ToolRegistration.discover(...)` 再查运营配置，没有按快照缓存。
- 证据：`app/application/workbench/capabilities.py` 的 `operation()` 及其在 `view()` 循环内的调用。本机（2 核）实测单次耗时：最简 Schema 约 1.9 ms；平台自带 `compute`（2.7 KB Schema）约 30 ms、`request_data`（5.1 KB）约 35 ms。
- 影响：连接多、工具 Schema 较大时，一次面板刷新会在事件循环里占用可观的 CPU 时间（例如 30 个中等工具约 1 秒）。不影响正确性。
- 建议：按“资产 + 工具快照摘要”缓存登记结果，或留到性能验收时再定。

### F05 提示与文案（低）

- `view()` 把“方法声明的业务权限与运营操作不符”（`declared_access` 失败）也归入 `operation_unavailable`，用户看不出是方法声明问题还是运营配置缺失。处理仍是拒绝。
- `method_permission_unconfirmed` 的中英文文案意思略有出入。
- 建议：两项都可以随后续界面整理处理，不阻断。

### F06 固定计划任务在平台工具守卫处不做步骤级核对（基线已有，非本增量引入；说明）

- 问题：`MethodToolGuard.check` 通过宿主调用身份核验后，遇到非动态任务就直接返回（`if not is_dynamic(task): return`），不核对本轮是否绑定到当前 Attempt，也不按步骤的工具清单限制平台／KnowBase 工具。
- 证据：`app/application/workbench/method_tools.py`，`34f5169` 第 141 行；基线 `d5241e4` 第 193 行已有同一分支，所以不是本增量新引入的。本增量的变化是：这类任务以前可以完全不核来源，现在至少要过宿主调用身份核验。
- 影响：固定计划任务的平台工具调用只受“会话归属 + 宿主调用身份 + 任务归属”约束，没有步骤级约束。受管工具（外部连接器）不走这条路径，它们在能力入口按运行态授权快照复核，不受影响。
- 建议：是否要给固定计划任务加步骤级约束，由 luna 按设计决定。只读看到当前 HEAD `d3f7dbad` 已改动该分支（未评审、未在其上跑测试）。

### 逐条核对（对应卡面 8 条重点检查）

1. 登记只存技术定义：`domain/workbench/tool_registry.py` 的 `ToolRegistration` 只含来源、服务、名称、Schema 摘要等；业务操作与读写性质在 `tool_operations.py` 的运营配置里。成立。
2. 两个入口都核 runner 事件：`workbench_mcp.py` 与 `capability_routes.py` 都经 `verify_tool_invocation`；缺 `_meta`、事件不匹配、跨会话都拒绝；等待有上限；重复请求按调用身份幂等。`test_tool_invocation_db.py` 通过。成立。
3. 运营配置绑定：`OperationCatalog.require` 找不到或摘要不符即拒绝；授权快照冻结 `operation_digest`，运行时与批准前都复核。成立。
4. `access_requirements` 独立于技术绑定：`MethodAccess` 校验缺失、未知、重复、未使用、通配、空集合；`check_access` 不接受用 `capability_ref`／版本／操作名替换。`test_method_access.py`、`test_method_access_db.py` 通过。成立。
5. 网页展示与确认：`capability-panel.tsx` 展示业务权限并要求确认；确认按方法上下文摘要保存，摘要覆盖完整步骤声明（含 `access_requirements`）。成立。
6. 只有 Task／Attempt 根范围：没有发现嵌套方法或父子权限的实现，也没有把根范围说成嵌套。成立（嵌套仍未实现，见下）。
7. KnowLab：`managed_capabilities_generated.py` 由契约生成并有锁；`compile.py`／`workdraft.py` 校验；`managed_authoring.py` 的作者入口对 `access_requirements` 同样拒绝。测试通过（F01 除外）。成立。
8. 普通聊天不需要方法权限；脚本开关默认关闭（`core/config.py`）。成立。

## 验证

环境：从各仓用 `git archive` 把固定提交导出到仓外隔离目录 `/home/zym/.cache/fable-c2-review/wt1/`（保持各仓相对位置），没有切换或改动主工位任何仓的工作区。解释器沿用主工位各后端现有 `.venv`（依赖以当前安装为准，没有按固定提交的锁文件重建）；网页沿用主工位 `node_modules`。数据库测试用卡面指定的隔离 PostgreSQL `127.0.0.1:55432/knowbench_tests`，凭据只从私有文件读取，未输出；全部串行。运行期间工位上另有其他代理的 pytest 进程（非本人启动，未清理）。

已运行：

| 范围 | 命令（在快照对应 `app` 目录，`python -m pytest -q`） | 结果 | 日志 |
| --- | --- | --- | --- |
| KnowBench 权限回归 | 卡面列出的 21 个文件 | 186 通过、0 失败、0 跳过（162.99 s），与发起者一致 | `/home/zym/.cache/fable-c2-review/r1-backend-tests.log` |
| KnowBench 方法契约与计划 | `test_dynamic_method_catalog.py test_atomic_method_catalog.py test_referenced_method_catalog.py test_method_plan.py test_capability_method_plan.py test_knowbot_contract_lock.py test_knowbot_incubation_lock.py test_knowbot_test_run_lock.py` | 140 通过、0 失败 | `…/r1-catalog-tests.log` |
| KnowLab 编译、作者限制、方法与锁 | `test_managed_capabilities.py test_knowbot_workdraft_compile.py test_knowbot_workdraft_service.py test_knowbot_workdraft_routes.py test_capability_methods.py test_dynamic_methods.py test_atomic_methods.py test_author_methods.py test_author_method_routes.py test_method_composition.py test_knowbot_contract_locks.py test_knowbot_incubation_contract.py test_knowbot_test_run_contract.py` | **182 通过、1 失败**（失败项即 F01） | `…/r1-knowlab-tests.log` |
| KnowMart 清单与目录消费者 | `test_knowbot_manifest_v2.py test_knowbot_manifest_v3.py test_expert_catalog.py test_knowbot_contract.py` | 52 通过、0 失败 | `…/r1-knowmart-tests.log` |
| 网页能力组件与契约 | `vitest run tests/component/capabilities.test.tsx tests/unit/capability-contract.test.ts` | 16 通过，与发起者一致 | `…/r1-web-tests.log` |

说明：

- 方法契约、KnowLab、KnowMart 三项的文件清单是我自己选的（卡面只给了数量，没给清单），所以数量与发起者的 129／132／15 不能直接比较。
- KnowLab 第一次运行另有 1 项失败（`test_atomic_methods.py::test_runtime_consumes_compilation_and_rejects_changed_policy`），原因是我的快照里没有 KnowBench 的 `.venv`；补上指向主工位 `.venv` 的链接后通过。属于我的环境问题，不是被评代码问题。
- F04 的耗时是在固定提交快照上用一段临时脚本测的，没有留日志。

未运行：

- 两后端 Ruff／Pyright，网页 TypeScript／ESLint／i18n 检查。
- 任一仓的全量测试；KnowLab 的数据库测试（`*_db.py`）。
- 固定版 Codex app-server 真实协议、真实连接器、真实供应商、模型调用。
- F01 的后续提交 `8925db9` 上的测试（只读文件比对了摘要）。

无法验证：线上真实数据现状及是否需要一次性迁移。

## 仍未实现（卡面与文档自述，本人未逐项验证其现状）

- C2 内：嵌套方法展开与子方法调用身份；父子权限交集与撤权传播；三类方法的孵化准入；共同的业务核权规则；只读授权复用；稳定的 MCP 配置；Skill 内容分离；依赖交付与连接生命周期；资源端账号权限；动态资料范围及其它资源种类。
- C3–C6 全部。
- 作者入口与脚本开关保持关闭；没有固定版 Codex 真实协议和外部供应商验收；没有完整候选全量。

本增量的结论不能作为开放方法接入、作者入口或脚本执行的依据。

## 交回

- 提交：本回执单独提交到 sunmoonun，只含本文件与另一张卡的 `replies/fable.md`（提交号见本文件的 git 历史）。提交后立即用 `./sunmoonun/docs/sync-cowork/sync/sync.sh push sunmoonun` 推送；如果推送没有成功，fable 会在本节追加说明。
- 没有修改任何被评代码，没有改 `request.md`；隔离快照与日志都在仓外，不提交。
- 待 luna 处理：F01 确认补丁范围并纳入下一轮固定版本；F02、F03 写入发布门；F04、F05、F06 自行取舍。
- 是否结案由发起者决定。
