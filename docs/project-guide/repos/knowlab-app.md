# knowlab-app：造专家

> 最后更新：2026-10-29 ｜ 按 qwen 分支代码重写 ｜ 骨架继承 [`tpl-app.md`](tpl-app.md)，本文只写它多出来的 ｜ 总览见 [`../overall-architecture.md`](../overall-architecture.md)

**层与线**：第 6 层应用层的一个应用；第 7 层专家线（knowlab → knowmart → knowbench）的第一环「造专家」：孵化、测试，过两道门后交给 knowmart（[架构总纲](../../总纲/架构总纲.md) 第二节）。

knowlab 是作者把自己的方法做成专家的地方。一个**产品**从创意起名称一生不变，形态依次是创意、准专家、专家（[叫法](../叫法.md)）：作者交创意，按模式受理，在工作稿上孵化，「出一版」得到准专家，测试通过就是专家，用户同意、平台人员审核后交 knowmart 上架。方法只来自作者（`C-L1`）：作者在工作稿上打的字算原话，AI 和平台人员写的都是提议，作者接受才算。要花模型钱的事（AI 起草一轮、测试）都不在 knowlab 后端跑，而是交 knowbench 在作者的账号、作者的电脑上用作者的 key 跑（decisions ⑯）。knowlab 不运行专家，也不存用户数据：测试要的数据在 knowbase，knowlab 只记测试集钉的是哪几份。

## 一、谁来做什么

**作者（web端）**
- 申请：写创意（六问、一份 skill、一句话问题三选一）、给验收用例、同意测试数据说明（第 3 版）、选孵化模式「我自己来 / 请平台孵化」；改创意出新版本。
- 自助孵化：在工作稿上直接改格子，从知识库栏挑几份数据给 AI 参考（只交格式），点「AI 起草」「让 AI 改…」（设费用上限、选电脑；「让 AI 改…」可以带上最近一次测试的报告），逐条或一步一键接受、改了再接受、不要 AI 的建议；导入专家包或 skill，复制自己的准专家作起点；「出一版」。模型 key 没在 knowbench 填的，发起前就拦。
- 平台孵化：点「请平台孵化」时设平台发起 AI 一轮的每轮上限，就是本人授权；处理平台人员的提议；授权最长 30 天，到期一键续；随时「我自己来」收回。
- 测试：自助测试（选电脑与目录、设上限）；确认专家在第 0 步提出的数据（换一份、改主体或年份、去掉、自己加），定下来记成测试集；把自己出的一版「交平台测」（设上限，没开测前可收回）。
- 待办：答测试中的问题与 AI 列的缺口（可答「按提议」），批准或拒绝自助测试里的工具审批，审核平台孵化的准专家，在用户同意门上定要不要这一版专家。
- 专家：看各版，停用能用的那一版；能用了点「去 knowbench 请它」。
- 知识库：看自己在 knowbase 展示给 knowlab 的资料，链去 knowbase 管。

**平台人员（管理端，权限 admin、operator；受理、孵化、交付这几步另要 `knowlab:release`，现在 operator 也有）**
- 受理：作者请了平台孵化的创意版本，查三样（投资建议类 `C-L5`、测试数据有没有权用 `C-L2`、归不归专家能做的 `C-L1`），写受理单；轻受理作者交平台测的那一位准专家（接或不接）。
- 孵化：在同一套格子里改工作稿，改的存成提议；在作者设的上限内发起 AI 一轮；格子都有作者出处时「出一版」（准专家记模式「平台」）；请用户审核、核出处；做完交还作者。
- 测试：发起平台测试（只填超时，上限用作者授权里设的，跑在作者上次自助测试用过的电脑与目录上）；刷新、看产出、判定卡住；答工具审批，或写理由把跑法问题改派给自己答。
- 交付：交回用户、运营审核（自用，或有资质的公开）、交 knowmart（失败可重试）、停用；「全部专家」看每个名称的每一版。
- 平台人员只看得到作者授权的那几步：纯自助的名称、作者点了「我自己来」的，列表里没有、按编号取也是 404。

**别的应用（系统替用户做的事）**
- knowbench 替作者跑 AI 起草一轮、跑测试（都在作者账号下）；用户在 knowbench 找不到合适的专家、点「孵化一个专家」时，knowbench 以用户的名义在 knowlab 建「问题」申请。
- knowbase 替作者解析测试要的数据、签每条用例的测试运行授权；knowfeed 替作者补采测试集里缺的公开披露。
- knowmart 收上架的版本、停用、记没上架那几版的结局。

## 二、页面与流程

**web端**（左边栏：首页；过程：申请 · 孵化 · 测试 · 交付 · 待办；结果：专家 · 知识库。SDD 0046 第六节；名称页照旧，栏是另一种入口）

| 页面 | 做什么 |
| --- | --- |
| 首页 `dashboard` | 「你的创意『…』测试通过了，去确认」；要我做的、在做的申请、能用的专家各几条 |
| 申请 `applications`（`new`、`[id]/revise`） | 提交、修改创意；右边是各版本与受理没有；旧说明下同意的有「同意新说明」；有能用的专家时给「去 knowbench 请它」 |
| 孵化 `incubation` | 按名称列、按模式分：自己来的给工作稿入口与最近一轮到哪了；平台孵化的是平台视图；两种都有切换按钮 |
| 测试 `tests` | 按名称列（待测 / 在测 / 测过了 / 还没出准专家）：验收用例、测试集第几版、自助测试与交平台测、确认数据、历次测试与结果 |
| 交付 `delivery` | 交回了的各版专家：自用还是公开、审核员授权、审核进度、进没进小店；先是列表与入口的骨架，交付的动作在交付那一块（L1）做 |
| 知识库 `knowledge` | 凭本人令牌现取 knowbase 里展示给 knowlab 的资料（名字、描述、版本、大小），「去 knowbase 管理」 |
| 名称页 `names/[id]` | 顶上一行每个过程最新的一项；「孵化方式」卡（请平台孵化、我自己来、续期）；平台视图（进度、在等你的、平台问过的）；「打开工作稿」；测试卡片（自助测试、交平台测、确认数据、历次结果）；按时间排的记录 |
| 工作稿 `names/[id]/workdraft` | 分格子的编辑器，自动保存（带 revision，别处改过回 409 就重载）；每格小字标出处、核不上的标红；「数据」一栏从知识库栏挑；AI 起草、让 AI 改…（可带测试报告）、导入、复制、预览清单、出一版；AI 建议与平台人员的提议放在格子旁边，一步头上可一键接受这一步的 AI 建议；模型 key 没填时发起框里先拦；底下列待你定的缺口 |
| 待办 `review`（原「审核」） | 测试中的问题与缺口、工具审批、请我审核的准专家、要不要这一版；右边是答过、定过的 |
| 专家 `experts` | 交回了我的各版：新交回 / 你已同意等审核 / 能用 / 停用了 / 没上架；停用；去 knowbench 请它 |

旧地址（`ideas`、`avatars`、`knowbots`、`questions`）都跳到新栏。

**管理端**（左边栏：治理控制台 · 受理 · 孵化 · 测试 · 交付，另有模板自带的参考页与设置）

| 页面 | 做什么 |
| --- | --- |
| 治理控制台 | 四栏各有几条「等我们」 |
| 受理 `acceptance` | 待受理 / 已受理 / 不受理，轻受理的三种并进同一组筛选；写受理单、接或不接平台测 |
| 孵化 `incubation` | 待孵化 / 孵化中（等用户审核）/ 已孵出；读受理了的创意，进工作稿改（提议）、出一版、发起 AI 一轮、请用户审核、核出处、交还 |
| 名称页 `names/[id]`、工作稿 `names/[id]/workdraft` | 同 web端的骨架；工作稿里「提交为提议」要写一句理由；挑数据与「高级」不提议 |
| 测试 `tests` | 待发起 / 排队 / 进行中 / 等用户答 / 已结束；发起、刷新、补取产出、判定卡住；作者没有能测的电脑、没填模型 key 时，说清要作者先去 knowbench 接入或填好 |
| 交付 `delivery` | 待交回 / 等用户同意 / 待运营审核 / 已上架 / 没上架 / 全部专家；交回、审核、交 knowmart、重试、停用 |

**流程一：自助孵化到准专家**
1. 作者在「申请」提交创意（选「我自己来」）→ 后端记创意 v1 和一张「自助（不受理）」受理单。
2. 名称页「打开工作稿」→ 点「AI 起草」，设上限（默认 20 元）、选电脑（默认上次那台）→ knowlab 建孵化记录（第几轮），经 `knowbench:incubate` 交 knowbench；knowbench 在作者电脑的「孵化」目录开一件委托。
3. 页面轮询取回，作者不开页面时后台每分钟也刷一次：建议显示在格子旁边，缺口进「待办」；knowlab 核每条建议的出处（创意原句逐字、答过的缺口），核不上的只能改了再接受。
4. 作者接受、改、自己写，可以再点「让 AI 改…」→ 点「出一版」：方法层每格都要有出处、核得上，编出的清单 v2 过草稿检查与 pack 自检，过了出准专家（模式「自助」）。

**流程二：请平台孵化**
1. 作者申请时选「请平台孵化」，或在名称页点它：确认框写明平台会看到什么、到什么时候、谁出钱，设每轮上限 → 记一张孵化授权（待受理）。
2. 平台人员在「受理」写受理单：受理了授权生效（最长 30 天）；不受理授权结束，名称转回自助。
3. 平台人员在工作稿里提交提议、在上限内发起 AI 一轮 → 作者在 web端工作稿逐条处理，接受了才进稿。
4. 平台人员「出一版」（最新一版创意要正式受理过）→ 请用户审核（作者在「待办」说行或不行）→ 核出处 → 发起平台测试，或「交还」作者自己测。作者点「我自己来」时授权立即撤销，没处理的提议作废。

**流程三：测试到上架**
1. 作者在名称页选电脑、设上限发起自助测试（或平台人员发起平台测试）→ knowlab 经 `knowbench:testrun` 交 knowbench，每条用例一件委托。
2. 第一次测时专家先跑第 0 步，提出的数据报回 knowlab 成一个 `data` 问题 → knowlab 凭作者本人令牌在 knowbase 解析，作者在测试卡片确认；缺的公开披露确认一次交 knowfeed 补采 → 签这条用例的测试运行授权，回答问题，委托接着跑。
3. 通过即出专家第 n 版；作者确认过的数据记成测试集新一版，重测直接钉上、不再跑第 0 步。
4. 平台人员「交回」→ 作者在「待办」定要不要 → 平台人员审核（自用或公开）→ 交 knowmart 上架 → 作者在专家页点「去 knowbench 请它」。

**从 knowbench 来的「问题」申请**：knowbench 经 `knowlab:incubation-request` 来建，种类「问题」、模式自己来、只有本人看得到、建了不花钱；记来源（项目、找专家那一轮的委托），可附「让我的模型直接答」的回答作参考，AI 起草时随孵化契约交给模型、只算提议。这样建的申请没有用例：发起测试回 409 `cases_missing`，作者要先「修改创意」补用例（同时勾同意）、再出一版。同一个幂等钥匙只建一份。

## 三、后端

| 块 | 代码（`knowlab-backend/app/app/`） | 说明 |
| --- | --- | --- |
| 一生的规矩 | `domain/knowbots/lifecycle.py`、`drafts.py` | 版本只增、没有退回；创意三种种类；测试数据说明 `CONSENT_VERSION = 3`；受理三样；准专家版本号 x.y |
| 申请、受理、测试 | `application/services/knowbot_service.py` | 提交与改创意、knowbench 来的问题申请、受理、发起与刷新测试、平台测试用作者的电脑 |
| 模式与授权 | `domain/knowbots/platform_grants.py`、`application/services/knowbot_platform.py`、`knowbot_grants.py` | 孵化授权（最长 30 天可续）、测试授权（轻受理）；依据 `platform:knowlab:<种类>:<编号>` |
| 工作稿 | `domain/knowbots/workdraft.py`、`compile.py`；`application/services/knowbot_workdraft.py` | 方法层格子与每格出处；只增的编辑记录；按格子编出清单 v2（工程层与给模型的指令由程序拼）；导入、复制、预览、出一版 |
| 平台人员的提议 | `application/services/knowbot_proposals.py` | 一格一条，形状同 AI 建议；作者处理时按现稿再套一遍 |
| AI 孵化一轮 | `domain/knowbots/incubation.py`、`incubation_rounds.py`；`application/services/knowbot_incubation.py` | 契约 `knowbot-incubation/v1`；发起（模型 key 没填 409 `model_key_missing`；可带最近一次测试报告，只有每步结果、不带期望值）、轮询与后台刷新取回、出处核对、接受建议（逐条、一步一键）；交给 AI 的是挑数据时记下的格式（描述、读法，不给内容） |
| 知识库栏与挑数据 | `application/services/knowbot_library.py`；`infrastructure/external/knowbase_library.py` | 凭作者本人令牌读 knowbase 的 knowlab 栏与读法；挑的只能是栏里的，格式记在工作稿 `data_formats` |
| 测试中的问题 | `application/services/knowbot_questions.py` | 工具审批、提问、开步前问、`data`、缺口（`gap`）；谁答由路由定 |
| 测试集 | `domain/knowbots/data_plan.py`、`data_request.py`；`application/services/knowbot_test_data.py` | 解析、确认、补采、按用例签授权、记测试集版本 |
| 专家与两道门 | `application/services/knowbot_experts.py` | 交回、用户同意门、运营审核门、交 knowmart、停用、没上架结局补发 |
| 两端的栏与详情 | `application/services/knowbot_board.py` | 各栏大类与数、详情页记录；`operator_view` 按授权裁平台人员看到的 |
| 出站客户端 | `infrastructure/external/knowbot_clients.py`、`knowbase_data_v2.py`、`knowfeed_supply.py` | 见第五节 |
| 接口 | `interfaces/endpoints/knowbot_routes.py`（`/api/web/v1`、`/api/admin/v1`）、`interfaces/http/internal/incubation_requests.py` | 内部入口只认集群内地址 |
| 定时任务 | `tasks/knowbot_outputs.py`（每小时）、`tasks/knowbot_unlisted.py`（每 5 分钟）、`tasks/knowbot_refresh.py`（每分钟） | 测试产出到期清理；没上架结局补发 knowmart；没结束的孵化一轮与在跑的测试各问运行方一次（作者不开页面也更新） |

## 四、自己存什么

- 创意：`knowbot_request`（名称、作者、运行方、孵化模式、来源与参考回答）、`knowbot_request_version`（只插不改）。
- 受理：`knowbot_acceptance`（正式受理 / 自助（不受理））；作者给平台的授权 `knowbot_platform_grant`（孵化、测试两种）。
- 孵化：`knowbot_workdraft`（一个名称一份；`data_formats` 记挑的数据的格式，迁移 0022）、`knowbot_workdraft_record`（编辑、接受、导入、复制，只增）、`knowbot_workdraft_proposal`、`knowbot_incubation`（AI 每一轮）。
- 准专家与测试：`knowbot_draft`（记模式、出自创意第几版）、`knowbot_test`（编号只增、模式、电脑与目录、测试集版本、每条用例的授权）、`knowbot_test_set`、`knowbot_test_output`（成稿与各步交回物，上架或被取代 90 天后清）、`knowbot_question`。
- 专家：`knowbot_expert`（两道门结论、knowmart 回执、停用）。补充方法 `knowbot_amendment` 只读留着。
- 模板自带：`auth_user`、`outbox_message`、`inbox_message`。没有对象存储。
- 已删掉的旧东西（⑰）：清单 v1 的准专家及其测试与专家、用户上传数据的表与 v1 测试同意、给运行方读数据的接口 `knowbot-data/v1`、管理端「贴清单」。

## 五、和别的应用

| 对方 | 怎么连 |
| --- | --- |
| knowbench（knowlab 调） | `knowbench:testrun`：`/api/internal/v1/knowbot-runtime/test-runs`（提交、查、回答、取产出）与 `…/users/{作者}/computers` 列作者接入过的电脑、`…/users/{作者}/readiness` 问模型 key 填了没有（knowbench 那头还没做，404 时 knowlab 不拦）；契约 `knowbot-test-run/v1`，`runner` 必填、只有用户本人。`knowbench:incubate`：`…/knowbot-runtime/incubations`（提交、查、取消），契约 `knowbot-incubation/v1` |
| knowbench（调 knowlab） | `knowlab:incubation-request`：`POST /api/internal/v1/knowlab/incubation-requests`，以用户名义建「问题」申请，新建回 201、同钥匙重来回 200 |
| knowbench、knowbase（跨应用链接） | 「去 knowbench 填模型 key」到 `workbench/settings`、「去 knowbench 接入电脑」到 `workbench/machines`；知识库栏「去 knowbase 管理」到 knowbase `dashboard`。申请页、专家页「去 knowbench 请它」：到 knowbench `workbench`，带 `knowbot=<专家>@<版本>`，从找专家来的再带 `task=<那一轮的委托>`；knowbench 用用户自己的会话向 knowmart 核验、钉住。地址没配时只写一句怎么去 |
| knowmart（knowlab 调） | `knowmart:deliver`：`POST /deliveries`（交付单号幂等，可带 `request_public`）、`…/versions/{v}/stop` 停用、`PUT …/sources/{ref}/unlisted/{v}` 没上架的结局 |
| knowbase（knowlab 调） | 作者本人令牌（Casdoor 令牌交换，audience 是 knowbase）：`/api/internal/v2/user-data/resolutions`、`/confirmations`，在 `app:knowlab` 范围里解析与确认；`/columns/knowlab`、`/materials/{资料}/versions/{版本}/renditions` 列知识库栏、取读法（挑数据）。服务身份 `knowbase:user-data-read`（补采后重解析）、`knowbase:user-data-grant-test`（签、撤每条用例的测试运行授权） |
| knowfeed（knowlab 调） | `knowfeed:supply-demand`：测试集缺的公开披露提需求单、查、取消；开关 `KNOWLAB_DATA_SUPPLY_ENABLED` 默认关 |

契约与锁（父仓 `contracts/`）：knowlab 是 `knowbot-test-run/v1`、`knowbot-incubation/v1` 的真源，由后端模型生成（`python -m app.domain.knowbots.schema`），knowbench 持锁；knowlab 持锁 `knowmart-knowbot-manifest-v2-lock.json`（清单 v2，真源 knowmart）、`knowbase-data-request-lock.json`（`data-request/v1`，真源 knowbase）。

## 六、照什么做的

| 块 | 决定 | 设计 |
| --- | --- | --- |
| 定位与合规 | 10-16 knowlab 新应用；`C-L1`–`C-L5` | [0026](../../design/SDD/modules/0026-knowlab.md)（含第五节合规） |
| 一生、两道门、版本与编号、两端分栏 | 10-20、10-23 栏目与两道门 | [0037](../../design/SDD/modules/0037-idea-avatar-expert.md) |
| 自助与平台、受理类型、切换、测试集、选电脑 | 10-26「knowlab 自助与平台」 | [0046](../../design/SDD/modules/0046-knowlab-self-service.md) |
| 工作稿、出处、AI 一轮、平台人员用同一个编辑器 | ⑮ | [专家孵化方案](../../总纲/专家孵化方案.md) 第五至第十二节 |
| 授权最长 30 天可续、平台出一版、删贴清单 | 10-29「孵化第 5 步的三件」 | 专家孵化方案第十二、十八节 |
| 「问题」申请、去 knowbench 请它 | 10-29「AI 请专家」 | 专家孵化方案第十三节、[请专家方案设计](../../总纲/请专家方案设计.md) 第 4.9 节 |
| 测试集 = 测试问题 + 作者确认的数据 | ⑭ | 0046 第三节、[数据拓扑](../../总纲/数据拓扑.md) 第九节 |
| 测试与 AI 一轮都在作者账号、电脑、key 上 | ⑯ | 0046 第三节、[账号-电脑-link-会合点](../账号-电脑-link-会合点.md) |
| 不留旧版兼容 | ⑰ | — |
| 叫法（作者、平台、产品、动作、待办） | 10-29「叫法」 | [叫法](../叫法.md) |

## 七、部署

`gitops/components/app-platform/knowlab-app/`（Fable 工位为准）：

- `config.yaml`：应用开关、验收读的管理端列表。
- `knowlab-backend/`：后端 config（`service_clients`、`service_receivers`、跨应用、补采开关）；`database/`、`migration/`、`redis/`、`rabbitmq/`、`identity/`、`runtime/` 同模板；每个出站关系一个 `*-identity/`（knowmart-deliver、knowbench-testrun、knowbench-incubate、knowfeed-supply-demand、knowbase 的 user-data-read、grant-test、directory、import、output）；`storage/` 是对象存储桶。
- `knowlab-web-frontend/`、`knowlab-admin-frontend/`：两个前端的域名、端口、客户端。

## 代码和设计对不上的

1. **自助测出的专家没有交付的路**：0046 第五节写自助测的「提交交付即过」、自用轻审、公开重跑。代码交付仍是 0037 那条（管理端交回 → 用户同意 → 运营审核），`application/services/knowbot_board.py:108` `operator_view` 只给平台人员看平台模式与交平台测的准专家，web端「专家」只列交回过的（`domain/knowbots/lifecycle.py:222`，没交回的阶段 `to_return` 不在 web端的大类里）。自助孵化、自助测试通过的专家，作者和平台人员都没有入口把它交出去（文件头注释写「交审随块 6 再放开」）。
2. **自助测的专家进不了交付栏**：交付栏现在列的是交回过的专家（`knowbot-board/experts`），自助测通过、没交回的不在里面；随交付那一块（L1）改。
3. **knowbase 没有本人读表头的接口**：专家孵化方案第 8.2 节写交给 AI 的格式含表名、列标签、行标签；knowbase 只在运行授权下给格式（`run-grants/{授权}/materials/{资料}/format`），本人令牌读不到，契约 `DataFormat.tables` 先空着（`application/services/knowbot_library.py`）。
4. **列作者的电脑走哪条路**：0046 第七节写凭本人令牌向 knowbench 要；代码走 `knowbench:testrun` 带作者编号（`infrastructure/external/knowbot_clients.py:113`）。0046 第九节已记这处差异，第七节正文没改。
5. **gitops 落后于代码**（Fable 工位 `knowlab-backend/config.yaml`）：
   - 还收 `knowlab:read`（`service_receivers` 第 143 行），knowbench 那边也还配着；代码已删这个接口，`infrastructure/security/relation_auth.py` 只认 `incubation-request`。
   - 还配 `knowbase:user-data-import`（注释已写随 qwen 删）、`user-data-directory`、`user-data-output` 三个出站身份和 `object_storage` 桶，代码都不用。
   - `WEB_AUTH_ALLOWED_RETURN_PATHS` 列的是旧页面（`knowbots`、`ideas`、`avatars`、`questions`、`data`；不在列表里的登录后退回首页，不会出错），没有 `applications`、`review`、`names` 与新栏；后端默认值（`core/config.py`）已改成首页、登录与各栏、名称页两种语言；要换的列在[交 Fable gitops](../../总纲/数据拓扑重构/交Fable-gitops.md) 第 2d 节第 7 条。
   - 组件 `README.md` 还写「空应用」「我的数据」「分身」。
6. **文档落后于代码**：[topics/knowbot.md](../topics/knowbot.md)（10-17）还写运营贴清单、「我的数据」、`knowlab:read`。
7. **需求状态推送没接**：0045 第 2.5 节写需求状态由 knowfeed 通知；knowfeed 已经发（契约 `knowfeed-supply-status/v1`，入口 `POST /api/internal/v1/knowfeed/demand-status`），knowlab 没有这个接收端，补采后照旧按单号查进度。
