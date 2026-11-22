# Cursor 合并发布与验收单（第 13、14 项及增量审查修复）

**#112 已发布，第 13 项由 Luna 直接验至第 4 轮，整体验收未通过。** sig-am 的空目录受理、重开、结束重放、拒绝旧修订、改题另建，以及跨应用新孵化和返回原委托已在现场通过。三道原题均已实测，获权目录为空，尚无模型规划或业务交付。zymun 的独立业务复核待办。[Luna 现场验收](replies/luna.md) · [逐题记录](replies/第4轮盲测记录.json)

**剩余阻塞。** 第 3 轮 L105 已领取但没有用量回执，Luna 在第 4 轮复查原运行仍失败、已用 0 元、预留 21.790720 元。21:45 Luna 已用原网关绑定凭据核实，Moonshot 对同一端点返回 401 incorrect_api_key_error。恢复该账号的供应商鉴权后再验试跑和冻结，原尝试的预留按原时段的受理与用量对账。有可用正式版本后续验命中、成功规划与复用、原作者修订和买方提需。第 14 项业务现场验收按原约定后置。[Cursor 原始回执](replies/cursor.md)

方法撤回由[下一版独立发版单](../2026-11-22-方法撤回独立发版与Q01-Q04验收/request.md)承接。

## 本次候选与发布顺序

| 对象 | 候选和依赖 |
| --- | --- |
| 平台内部入口 | 内部路由声明 `a01916894`，Jenkins 的 Traefik 发布目标与候选校验 `116dfd3ab` |
| 沙箱和供给器 | 两个镜像的构建输入钉至 `7798c101b`，清单与契约校验 `59648dd9c`。先提供新版预留回收接口，再更新使用该接口的 runner |
| KnowBase | 父仓 `00b59ec`，后端 `a30b375`。提供成稿可用性查询，沿用 `knowbase:user-data-output` 身份及 `GET /api/internal/v2/user-data/outputs/available` |
| KnowLab | 父仓 `c2ed6b9`，后端 `d728475`，Web `b125fc5`。包含 P3 作者回炉、公开 Schema 与作者界面修复 |
| KnowBench | 父仓 `af29b72`，后端 `b16d9cd`，Web `0ba5de9`，已包含第 14 项。先落实 KnowBase 接口与数据库迁移 `20261122_0059`，再更新 API、runner 和 Web |

将表中修订纳入同一发布分支。从已核对的 #108 指针与镜像锁出发，把三个应用的发布分支对齐表中父仓与子仓修订，以 `APPS="knowbase knowlab knowbench sandbox traefik"`、`PIN=heads` 暂存同一候选。核对 `sources.yaml` 的父仓和子仓钉版，执行 `python3 ci/verify-contracts.py --images-only` 和 `python3 ci/verify-contracts.py --pinned`，按现有 Jenkins 人批流程晋级。远程工位约 3.7 GiB，重任务串行；并行构建和测试用本地大内存工位。

## 试验范围与配置

工作台全量开关 `EXPERT_UNIFIED_ENTRY_ENABLED=false`，试验范围为 sig-am 的真实 OIDC subject。后台和 runner 均使用同一份相应配置。脚本运行须有核定报价；#108 时没有有效脚本报价或第二模型家族，且共享写回开关会推进其他账号的存量产出。涉及写回的验收在同版本隔离部署中开启，缺少的提供方、授权或报价逐项记入回执。

| 能力 | Cursor 发布时设置并验证 |
| --- | --- |
| Kimi 指令试跑 | 在 KnowBench API 和 runner 装载 `WORKBENCH_INSTRUCTION_ROUTES`。沿用 sig-am 的 Kimi 连接、`kimi-k3`、规范地址和现有 CNY 价目；按供应商实际上下文上界、所需最大输出计算单轮预留。核对供给器的 `INSTRUCTION_CONTROL_ORIGIN`、内部 TLS、签名与回执路径。 |
| 独立复核 | 同批装载 `WORKBENCH_REVIEW_ROUTES`，核对模型家族、价目、目标地址与报价。默认 Kimi 走账号已有授权；涉及另一个已核定模型或地址时，配上相应的 `WORKBENCH_REVIEW_MODEL_GRANTS`。只有 Kimi 可用时可以验同家族允许的复核，强制跨家族场景记录实际缺少的第二家族。 |
| 脚本、固定计划与交付写回 | 在验收环境开启 `WORKBENCH_SKILL_SCRIPTS_ENABLED=true`，核实隔离脚本供给和有效的 `WORKBENCH_SCRIPT_TARIFF` 报价可用；将 sig-am 的真实 subject 加入 `WORKBENCH_FIXED_AS_PLAN_OWNERS`；开启 `WORKBENCH_OUTPUT_WRITE_ENABLED=true`，用已授权的测试产物验证 KnowBase 写回。核对资料读取所需的 `WORKBENCH_DATA_SUPPLY_ENABLED` 和本人资料授权。若部署级开关会推进其他账号的存量写入，使用同版本隔离部署验收该开关。 |
| 外部 A2A 测试连接 | 为 #105 第 15 项装载获准的测试 OAuth/A2A 提供方与操作范围，使用合成服务核对一次提交、查询、取消及丢响应后的恢复。 |
| 工作台入口 | 将 sig-am 的真实 subject 加入 `EXPERT_PLANNING_OWNERS`，为该账号开启统一入口。全体用户切换沿用 zymun 业务复核后的决定。 |

<a id="callbacks"></a>

## 发布后先验内部回调

11 月 22 日 19:05，Luna 在运行中的集群核实，供给器已配置内部 HTTPS 地址和 CA。为该主机服务的唯一 Ingress 只有 `knowbot-runtime` 与 `method-skill-center/functions` 两个前缀。经同一 CA 验证 TLS 后，无凭据 POST 到 `/api/internal/v1/instruction-control/claim` 和 `/receipt` 均为 Traefik 404。直接核对内部 KnowBench API 上对应的两个 POST 都为 401，两条 GET 都为 405。这证明当前入口无法把网关请求送达处理程序。历史尝试的原始异常未留存。

1. 查看第 4 阶段的差异，确认 `knowbench-service-access` 在原有规则旁新增 `/api/internal/v1/instruction-control`，类型 `Prefix`，后端 `knowbench-api:http`，沿用原内部主机和证书。若 Jenkins 报无差异，须用下方现场检查核实实际状态。候选中若出现意料之外的其他共享入口或凭据变更，在人批前核对来源。
2. 发布完成后先核对 Flux 摘要、Traefik Ready 和实际 Ingress。再使用下面的不计费探针。第一段在可信工位开本机端口转发，第二段在另一终端执行。使用目标集群的 kubeconfig，端口被占用时两处一起替换。

```sh
kubectl -n ingress-platform-dev port-forward --address=127.0.0.1 svc/traefik 18443:443
```

```sh
(
  set -eu
  ca=$(mktemp)
  trap 'rm -f "$ca"' EXIT
  kubectl -n sandbox-platform-dev get configmap instruction-control-ca -o 'jsonpath={.data.ca\.crt}' > "$ca"
  host=knowbench-tls.app-platform-dev.svc.cluster.local
  for operation in claim receipt; do
    status=$(curl --noproxy '*' --silent --show-error --max-time 8 --cacert "$ca" \
      --connect-to "$host:443:127.0.0.1:18443" -o /dev/null -w '%{http_code}' \
      -H 'Content-Type: application/json' --data '{}' \
      "https://$host/api/internal/v1/instruction-control/$operation")
    printf '%s %s\n' "$operation" "$status"
    test "$status" = 401
  done
)
```

3. 将 Jenkins 号、晋级摘要、实际 Ingress 前缀和两条 HTTP 状态写到本卡 `replies/cursor.md`。两条均为 401 后，按[现场手册](Cursor现场验收手册.md)用 sig-am、原申请和有效报价重试一笔。同步记录网关到控制面的 claim、供应商用量、receipt、运行号和业务输出；只记录元数据。若仍失败，按时间线记录最先失败的环节及状态码、Pod 终止原因与重启次数，保留原尝试并交回。无凭据的请求返回 401 只验证路由与认证边界，实际试跑另看 L105 与结算。

<a id="expert-entry"></a>

## 第 13 项与 #105 余项

原申请的 [L105 定义](L105-方法定义.json)、表单、断言、五份年报位置和三道原题见[现场手册](Cursor现场验收手册.md)。沿用 [#105 原编号与验收记录](../../../archive/luna/2026-11-22-作者草图和普通专家委托合并发版/replies/luna.md)核对第 1–17 项。入口探针通过后使用 sig-am 已配置的 Kimi，核对实际输出、用量和结算后继续冻结与交付。空目录受理、刷新和结束未匹配可先验。

1. 使用 `sig-am` 的独立测试项目，复核新入口、匹配成功及零候选，刷新原委托。结束未匹配委托后重开，核对原问题、已查范围和唯一回执。重复确认应返回原回执，旧修订应被拒绝，改题应另起委托。结束操作的新增模型轮次、业务调用和费用均为零。空目录完成受理应无模型轮次；选择拟计划后才可产生规划费，拟好后查看计划、必交字段、需补资料、账号及报价。未确认前业务调用为零。
2. 现场具有获权版本时，执行、保存，并在新委托复用计划，重核输入及权限。对未知字段批准一次指定版本及列的探查，再明确恢复。对超出当前能力的问题核查停止原因。记录已用、撤回、过期资格及运行器变更所产生的实际结果。
3. 在原委托送 KnowLab，分别核对新孵化、原作者修订和买方提需的去向、发送字段与返回链接。作者试跑、冻结、登记新版后通过正常市场流程重新获取，核对旧版与已有交付。买方反馈只记其提交的缺口。原始草图和私有绑定留在原委托。发布所得镜像与拆分环境的真实行为分别留证。
4. 所有者已批准 `sig-am` 按需要做有限付费测试。用[首轮约定与审计步骤](../../../../../scripts/results/第二轨联调/2026-11-22-即时自组盲测/验收约定.md)和同目录的输入清单运行。在正式工具缺失时，先查本人是否能获取合适的已发布版本，记录资格窗口和处理结果。合成测试和此前财务专家的历史结果单列。第 4 轮起由 Luna 汇总新任务号、已获权的资料版本和结账金额，交 zymun 独立审阅业务产物。独立业务意见由 zymun 给出后再决定全量开放。

<a id="review-fixes"></a>

## R01–R08 工程验收

1. 在大内存本地工位将 `AGENT_TEST_DATABASE_URL` 与 `DELIVERY_TEST_DATABASE_URL` 指向隔离 PostgreSQL 测试库（库名以 `_tests` 结尾）。平台仓运行 `make -C infrastructure verify-method-transactions`。它会建测试数据，包括 KnowLab 已冻结 P3 样例、长期职责的成稿及 KnowMart 资格目录。完整数据库测试另有 `verify-db-transactions` 入口。
2. 沙箱使用隔离命名空间和本次镜像。按 provisioner 的 `tests/test_instruction_units.py::test_instruction_unit_lifecycle` 构造带原始 proof UID、未绑定网关的预留 PVC。停止准备新单元后触发终态回收。记录回收前后 Pod/PVC UID、runner 的清理状态与重复回收结果。期望无新 Pod，错误 proof 不能删除，原 PVC 消失后清理完成。用 KnowBench 的 `tests/test_instruction_runner_db.py` 复跑 runner 状态转换。独立 API 的端口、临时证书和环境变量见[供给器联调说明](../../../../../gitops/components/sandbox-platform/provisioner/README.md)。
3. 用获准的作者测试身份打开已冻结的 P3 协作专家并发起作者回炉。物料结构见 KnowLab 的 `test_runtime_method_demand_db.py::test_author_handoff_reopens_collaboration_in_its_editable_cell`。确认新工作稿可打开，协作角色和步骤可编辑，原冻结摘要可核对。回炉页同一版本用于不同步骤时应逐行显示。复核页应只显示一次状态提示。
4. 工作台使用 `test_temporary_plan_db.py` 和 `test_ordinary_strict_review_db.py -k two_sources` 的样例复跑探查、成稿与长期职责。探查授权后模拟资料读取失败，再换坐标应被拒绝；同坐标并发请求应共用回执。并发放行同一成稿应只写一次；写入途中撤回后，迟到回执不能让该成稿获得下期使用权。
5. 召回物料见 `test_planning_window_recall_db.py::test_authorized_top_eight_before_and_after_catalog_growth`。先排 96 个获权工具，再排 1 个获权专家，搜索专家首屏应命中；另验证第二窗高匹配专家排名领先、撤权后不可选。隔离库可用上述测试直接生成目录。共享市场没有对应物料时，在回执中分列本地结果与现场实测范围。

<a id="long-term"></a>

## 第 14 项长期职责与回炉版本采用

在本地大内存工位，取表中工作树和本单所在的 `sunmoonun/luna` 修订。KnowLab、KnowMart、KnowBench 后端使用各自的 `app/.venv`。将 `AGENT_TEST_DATABASE_URL` 和 `DELIVERY_TEST_DATABASE_URL` 指向环回地址的两个独立临时 PostgreSQL 测试库（库名以 `_tests` 结尾），运行以下命令。脚本自行创建隔离 schema、临时证书、原题、试题、测试账号和受控工具；无须提供真实账号凭据。

```sh
python3 sunmoonun/scripts/local-integration/formal_market_delivery.py --expert --roundtrip
```

同一批本地用例包括工作台后端的 `test_ordinary_strict_review_db.py -k two_sources` 及 `test_ordinary_metered_tools_db.py -k live`。后者在两个独立 Codex 容器中执行，设置 `RUN_CODEX_INSTRUCTION_PROBE=1` 和 `CODEX_INSTRUCTION_TEST_IMAGE` 为现场对应的已缓存 sandbox 镜像；本地验证镜像为 `sunmoon-build/sandbox:edd9b00f569a-8852d509a0e7`。这些是开发用例，无需 Kimi 计费。回到约 3.7 GiB 的远程工位时重任务串行。

### 后续现场验收

1. 用 `sig-am` 在试验项目完成一个已获使用权、带明确交接输出的双角色专家委托。记录该专家的方法 ID、版本、摘要、原委托和执行编号，核对两方的线程、工作目录、各自可见材料和交接前后的读取结果。本卡的 L105 是单条指令的物料，双角色场景要选用已验证的编排专家。若现场尚无合适版本，可按本单的回炉路径先在私有项目孵化，再从自己的目录获取。
2. 在交付页打开「长期职责」，填写长期交代、间隔和要放行的输出，保存后单独批准写入 KnowBase。首次到期前应无新委托。固定间隔最短一小时；现场等正常到期，本地用可控时钟验证重放。记录上期成稿的资料 ID、版本和 SHA-256、职责和新委托编号。新委托应显示同一专家版本和该份成稿，执行前再次确认。选了资料输入的场景，在 KnowBase 将成稿转为数据，并在准备页选该副本的第一版。另以单独的测试委托验证未放行、撤回放行、失去使用权及暂停，预期不会继续生成委托。
3. 从「请专家」原委托提交确切缺口。目录为空时验新孵化；已有 v1 时，用原作者验新修订、用仅有运行权的买方验提需。缺工具时先孵化并试跑工具，再在专家工作稿中引用精确版本。冻结 v2 后通过适用目录交付。买方获取前应看不到可采用的 v2；获取后在**原委托**打开「核对已获取的孵化版本」，展开能力、输入、输出或权限变化，明确确认后再选用并执行。记录 KnowLab 申请与冻结回执、KnowMart 的获取回执和两个工作台运行编号。重试应共用同次回执，v1 原运行和成稿仍可打开。
4. 用本卡已约定的真实账号与获准物料。只在安排现场验收后调用真实模型，记录实际模型、耗时、费用和产物版本。用本单 `replies/cursor.md` 交回集群构建、两条路径的运行与偏差。业务盲测继续由 `zymun` 单独复核。

第 14 项本地验证的触发来源为定时。邮件和 KnowFeed 订阅属于连接器方案中的其他触发来源。

## 交回与结案

Cursor 的[发布与前三轮回执](replies/cursor.md)保留构建号、晋级摘要、各组件修订、探针状态与试跑编号。Luna 从第 4 轮起在[亲验回执](replies/luna.md)记录运行、产物、费用和缺项。标明现场通过、仅本地验证和待补项目。第 14 项现场排期与 zymun 业务意见继续在此跟踪。现场若需回退入口，先关闭试验名单和全量开关，保留存量委托、工作稿和实际费用。
