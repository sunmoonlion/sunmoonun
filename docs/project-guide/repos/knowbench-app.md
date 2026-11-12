# knowbench-app：工作台

> 最后更新：2026-11-01 ｜ 按 qwen 分支代码重写 ｜ 骨架继承 [`tpl-app.md`](tpl-app.md)，本文只写它多出来的 ｜ 总览见 [`../overall-architecture.md`](../overall-architecture.md)

**层与线**：第 6 层应用层；第 7 层专家线 knowlab → knowmart → knowbench 的最后一环「使用」（[架构总纲](../../总纲/架构总纲.md) 第二节）。它同时是 knowlab 的**运行方**：knowlab 的测试和孵化的一轮都交给它跑。它的后端是平台层沙箱供给器与会合点的使用方。

用户用**自己的模型**做事的地方：聊天、工作、请专家。模型是用户在设置里登记的 key，跑在云端替这个账号拉起的沙箱里（Codex），经会合点到用户电脑上的本地 link 干活；knowbench 后端自己不调收费模型（[decisions](../../design/decisions.md) ⑯）。专家来自 knowmart（清单 `knowbot-manifest/v2`），请来时钉住一版；委托开跑先走第 0 步「定数据」，由用户的模型按问题提出要哪些数据、用户确认，再经 knowbase 第四版读、缺的交 knowfeed 补采（⑭）。用户也可以「让 AI 找」专家：找到就请，找不到就让自己的模型直接答，或去 knowlab 孵化一个。旧的内置专家包、经 knowlab 读数据、云端知识库页、本地知识库页、knowbase 检索都已删掉（⑰、decisions「数据拓扑第四版」①）。叫法照 [叫法](../叫法.md) 与 [账号-电脑-link-会合点](../账号-电脑-link-会合点.md)。

## 一、谁来做什么

**用户**（在 web端）
- 在设置「模型」登记模型 key，在「电脑与沙箱」下载安装本地 link、拉起沙箱；颁发令牌、配对照 [账号-电脑-link-会合点](../账号-电脑-link-会合点.md) 第二节。
- 建项目（选电脑、选工作区，建文件夹或拉仓库），在项目里开聊天、工作；聊天也可以不挂项目。
- 请专家：自己选一位，或点「让 AI 找」；写问题；确认第 0 步提出的数据（看预切合的预计时间与许可档，换一份、改主体或期间、去掉、自己加，采不来的去 knowbase 直达上传后再重查）；答专家的反问与审批；看步骤、底稿与花费，随时停。
- 从 knowmart「我的分身」选专家带回来，或从 knowlab 申请页、专家页点「去 knowbench 请它」带回来。
- 管长期记忆。

**作者**（是用户；在 knowlab 发起，在 knowbench 跑，用作者自己的账号、电脑、key）
- 自助或平台测试的每条用例、孵化的每一轮（「AI 起草」「让 AI 改…」），都在作者的工作台里建委托，作者看得到委托和花了多少钱（⑮⑯）。

**平台人员**
- 管理端：只有模板带的几页，没有 knowbench 自己的功能页。缺的数据由用户在委托里确认、knowfeed 替用户采；采不来的汇总在 knowfeed 管理端的缺口清单。
- 以平台身份当用户干活时，用配给自己账号的**平台电脑**（现在一台，配在 `knowbot-tester`），在 web端和普通用户一样用（[叫法](../叫法.md)）。

**别的应用（系统替用户做的事）**
- knowlab 经 `knowbench:testrun` 交来测试（含查就绪、取消）、经 `knowbench:incubate` 交来孵化一轮；knowbench 在作者账号下跑，跑到要人回答的地方报回 knowlab。
- knowfeed 经 `knowbench:supply-status` 推来需求单状态变化，knowbench 收到后马上重解析并接着跑。
- knowbench 替用户：向 knowmart 取清单与目录、挂需求；向 knowlab 建孵化申请；向 knowbase 解析数据、写回换过的偏好、签与交还运行授权、中继数据工具、把交付的成稿写进产出区（`knowbase:user-data-output`）；向 knowfeed 问预切合、提补采需求单、查证券名录。

## 二、页面与流程

### web端（`knowbench-web-frontend/app/features/`，地址在 `lib/workbench/routes.ts`）

| 页面 | 代码 | 做什么 |
| --- | --- | --- |
| 工作台首页 | `home/` | 三种开始：聊天、工作、专家；专家模式里直接挑一位或「去 knowmart 选专家」；顶上列「待我决定」。带着专家回来（`knowbot=`）或从 knowbase 直达上传回跳（`?ref=<委托编号>`）也落在这里 |
| 聊天 | `chat/` | 一问一答；直接答开的对话顶上标「不是专家」，可接着「孵化一个专家（附这份回答）」（`direct-answer-note.tsx`） |
| 工作 | `work/` | 看模型干活的时间线、随时插话、批准命令、答反问；右边是改了哪些文件 |
| 项目列表 / 项目页 | `projects/` | 按电脑 → 工作区分组；新建项目（`new-project-dialog.tsx`）；项目里的对话、专家交回、看板（排队、在跑、等你、等别人、完成、没成，卡片写等谁、等什么，等你确认数据的在卡片上直接确认） |
| 专家首页 | `expert/expert-home-screen.tsx` | 等我决定、进行中、有哪些专家（用户请过、钉住的那些）、最近交回 |
| 请专家 | `expert/ask-expert-screen.tsx`、`find-expert-panel.tsx` | 选专家、写问题；不填数据、不填预算（花多少实时显示）；「让 AI 找」的三种结果 |
| 专家处理中 | `expert/expert-run-screen.tsx`、`review-panel.tsx` | 步骤轨、每步交回与逐条验收、委托单；数据面板（`components/workbench/task-data-panel.tsx`，含预切合、去 knowbase 直达上传、「传好了，重新查」、没存进产出区的成稿原因）；停下来问人的审查面；AI 替你请的标明谁、理由，可「换一位」 |
| 设置 | `settings/` | 三项：个人偏好、模型（key、接入地址、新对话默认、长期记忆入口）、电脑与沙箱（下载安装包、本地 link 状态与「这台电脑上的设置」、沙箱就绪与拉起、配对） |
| 长期记忆 | `memory/` | 几条关于用户的事实，每段对话开头带上 |
| 框架 | `shell/`、`usage/` | 侧栏（电脑 → 工作区 → 项目 → 对话）、打开工作台时的核对提示（[账号-电脑-link-会合点](../账号-电脑-link-会合点.md) 第五节）、输入框下的花费 |

### 管理端（`knowbench-admin-frontend/app/`）

| 页面 | 做什么 |
| --- | --- |
| 研究运行时（`/research/runtime`） | 模板留下的占位页，没有功能 |
| 治理控制台、CRUD 参考、富能力参考、设置 | 模板自带 |

### 流程一：用户自己请专家（⑭，[请专家与执行](../../总纲/专家方案设计/专家使用方案/opus/请专家与执行.md) 第五节）

1. 用户在请专家页选一位、写问题，点交 → 后端新建一段专家对话和一件委托；专家这一版的清单快照写进委托，之后编排、验收只读快照。作者挑选的数据（冻结的绑定）由用户本人当场签运行授权、钉住，页面只说「专家自带 N 份」。
2. 第 0 步「定数据」：沙箱里用户的模型读专家逻辑和问题，用 `find_subject` 按名字查证券代码，用 `request_data` 提出要哪些数据（一次最多 20 样）→ knowbase 在用户能用的范围里解析 → 面板对「待确认」项向 knowfeed 问一次预切合（能不能取、预计多久、哪一档许可，`knowfeed-supply-prematch/v1`）→ 委托停在步骤之间，等用户确认。
3. 用户在委托页或看板卡片上确认，可换一份（确认后按 `expert:<id>` 写回 knowbase 偏好）、改主体或期间、去掉、自己加一样，采不来的可点「去 knowbase 上传」传好后再点「传好了，重新查」；也可以都不要 → 齐的本人签授权（运行授权 ref 由服务端生成 `knowbench:run:<uuid4>`）、钉住，委托接着跑；缺的把供给条件快照一并存进 knowbase 确认，再经 `knowfeed:supply-demand` 提需求单，委托进「等数据」。
4. runner 里的等数据线按单号查需求单（knowfeed 办完也会经 `knowbench:supply-status` 推送过来，两边用 `checking_until` 领用期限防并发）；办完了请 knowbase 重解析、凭用户那次确认续签（7 天内）、钉住、自动接着跑（⑫）；有没取到的，停下问用户：照现有的接着做（只有必需项缺了才记「数据不全」）还是取消。委托结束时按授权 ref 一次交还（`GrantReleaser`）。
5. 第 1 步起照专家的步骤做，每步确定性验收；运行中还要数据，同一个 `request_data`，照样等用户确认。成稿写进项目文件，底稿在电脑上的项目目录里；交付那一刻统一取成稿的 sha256，runner 里的写产出线（`OutputWriter`，受 `WORKBENCH_OUTPUT_WRITE_ENABLED` 开关控制）按原样字节核对 sha256（取不到指纹的看修改时间不晚于交付），带 `grant_ref`、委托起止时间、`incomplete` 替用户写进 knowbase 产出区并核回显 `provenance_basis`，没写进的在委托页显示原因。

### 流程二：让 AI 找（decisions 10-29「AI 请专家」，[请专家与执行](../../总纲/专家方案设计/专家使用方案/opus/请专家与执行.md) 第 4.2、4.3 节）

1. 用户写好问题点「让 AI 找」→ 后端在这个项目里开一段专家对话和一件内部小委托（方法包 `FIND_EXPERT`，这一轮费用上限默认 2 元），用户的模型调 `find_expert` 取 knowmart 目录（`knowmart:catalog`，只有公开信息：名称、一句话、`scope` 三项、版本、价格、免不免费），只按专家自己写的范围匹配，平台不排序。
2. 页面每 3 秒取一次结果；后端按目录再核一遍（目录里没有的候选丢掉，说免费的核不上就退成候选），回三种结果之一：
   - **直接请**：网页在用户在场时先钉住这一版、再用用户自己的会话建委托，进流程一的第 0 步；处理中那页顶上写「AI 替你请了某某，理由……」，可换一位。
   - **候选**：最多 3 位要付钱的，写理由和价格，用户点「请这位」才请。
   - **都不合适**：一张卡，两件都不自动做、可以都点，推荐的那件高亮并写一句理由——「让我的模型直接答」（项目里开一段聊天，对话记来源 `direct_answer`，页面标「这是你的模型直接答的，不是专家，方法没经过测试」）；「孵化一个专家」（经 `knowlab:incubation-request` 以用户名义建种类「问题」的申请，先直接答过的附上那份回答作参考）。同一张卡上还有挂需求：描述是模型拟的、用户可改，点「发布」才经 `knowmart:demand` 挂出，30 天后截止。

### 流程三：带着专家回来（`KnowbotArrival`）

1. 链接带 `knowbot=<分身>@<版本>`：从 knowmart「我的分身」选定的，或 knowlab 里能用了的那一版。
2. 后端按用户的登录会话向 knowmart（`knowmart:summon`）核一次、钉住；伪造的、别人的一律 404。
3. 链接还带 `task`（当初找专家那一轮）时，取回当初的问题和项目，直接到那个项目的请专家页，问题填好、这位选好，用户点了才交；取不到就回专家首页选好这一位。

### 流程四：作为运行方替 knowlab 跑

- **测试**（`testrun`，契约 `knowbot-test-run/v1`）：只在作者的账号下、作者接入的电脑和白名单里的根目录上跑（⑯），用作者的沙箱与 key（另有 `GET /readiness` 查这位用户有没有在用的模型 key）；同一台电脑同一根目录一次一个，其余排队。每条用例开一段专家对话、用草稿快照建委托；用例带了测试集就钉上（记 knowlab 的授权 ref `<run_id>:<case_id>`）、不跑第 0 步，没带的跑第 0 步，提出的数据报成待回答问题，作者在 knowlab 确认后带着测试集回答。审批与反问报给 knowlab，答完代作者回答接着跑；knowlab 调 `POST /test-runs/{run_id}/cancel` 时停下在跑的用例委托、交还授权、记已花费用。测试产出 7 天后删。
- **孵化一轮**（`incubate`，契约 `knowbot-incubation/v1`）：在作者选的根目录下建固定的「孵化」子目录与同名项目，每一轮用内置方法 `INCUBATE` 建一件委托；交给模型的只有契约列的材料；交回物先过验收再逐条核契约，到上限停下记超预算；电脑不在线就停在「等你接入电脑」。

## 三、后端（`knowbench-backend/app/app/`）

| 块 | 代码 | 说明 |
| --- | --- | --- |
| 对话与项目 | `application/workbench/session_service.py`、`project_service.py`；`domain/workbench/projects.py` | 三种对话：聊天、工作、专家（[0017](../../design/SDD/modules/0017-three-kinds-of-conversation.md)）；工作区是电脑上的根目录，项目是其下子目录；对话可记来源 `origin` |
| 专家从哪来 | `application/workbench/catalog.py`；`domain/workbench/knowbots.py`；`infrastructure/external/knowmart_client.py` | 钉住 knowmart 来的分身（只增）；建委托时把专家包快照、清单摘要、冻结的绑定写进委托；只认清单 v2；分身的工具范围只能比平台更严 |
| 内置方法包 | `domain/workbench/packs.py` | 只剩三份，都不给用户列：`SMOKE`（测机制）、`INCUBATE`（孵化一轮）、`FIND_EXPERT`（找专家） |
| 编排与验收 | `advisor.py`、`acceptance.py`、`acceptance_numbers.py`、`deliverable_check.py` | 逐步给用户的 Codex 发一轮、按预算扣、确定性验收、返工或交人；第 0 步「定数据」不进步骤游标；交付时统一取成稿的 sha256 |
| 请专家与数据 | `delegation.py`、`expert_data.py`、`grant_release.py`、`outputs.py`；`domain/workbench/data_plan.py`、`data_request.py`、`supply_prematch.py` | 建委托、第 0 步与运行中的提出、预切合、用户确认、写回偏好、签与按 ref 交还授权、钉住、交 knowfeed、收推送与等数据线（`DataWaiter`）自动接着跑、成稿写进 knowbase 产出区（`OutputWriter`） |
| AI 请专家 | `find_expert.py`；`infrastructure/external/ai_summon_clients.py` | 开「找专家」那一轮、按目录核结果、挂需求、建孵化申请 |
| 运行方 | `test_runs.py`、`test_folders.py`、`incubations.py`、`interactions.py`；`interfaces/endpoints/knowbot_runtime_routes.py` | `/api/internal/v1/knowbot-runtime`：就绪检查（`readiness`）、测试（提交、查、取消、取产出、答问题）、用户接入过的电脑列表、孵化（收、查、取消）；只认 knowlab 的服务身份，孵化在代码里写死只许 knowlab |
| 账与记录 | `ledger.py`、`runner.py`、`records.py`、`run_files.py`、`expert_desk.py` | 委托与 Attempt、预算硬停、交互（待我决定）、看板、专家首页 |
| 给沙箱的工具 | `interfaces/mcp/workbench_mcp.py`（`/api/mcp/workbench`）、`application/workbench/data_relay.py`、`knowbot_compute.py` | 自己的工具：读本项目别的对话与底稿、`find_subject`、`request_data`、`find_expert`、`compute`；knowbase 数据 MCP 的读工具（`list_inputs`、`read_input`、`query_facts`、`query_metric`、`read_facts`、`describe_items`、`search_evidence`、`lookup`、`list_library`）照原样挂出，把 `task`/`conversation` 换成运行授权或会话（专家在做的对话不收 `conversation`），每次当场签一张只许这个工具的 `knowbase-data` 令牌转过去（[0048](../../design/SDD/modules/0048-model-data-tools.md)） |
| 对话里读数据 | `expert_data.py` 的 `ensure_data_session` | 用户在对话里发消息时用本人令牌在 knowbase 登记会话（24 小时，范围是放开给 knowbench 的加公开原件），登记不成不挡聊天 |
| 沙箱与令牌 | `provisioning.py`、`tokens.py` | 拉起沙箱（解密 key → 签会合点身份 → 调供给器）；签各种 ES256 令牌，公钥经 `/api/workbench/token-keys` 发 |
| 本地 link | `agent_onboarding.py`、`agent_download.py`、`agent_service.py`、`agent_reports.py`、`machines.py` | 安装包下发、颁发令牌、按设备编号登记、连没连着；远程登录 link 的电脑看文件、建项目走 `/environments/{id}/remote/*` |
| runner 进程 | `bootstrap/runner.py` | 比模板多的运行角色：连各沙箱、驱动委托，同进程里还有等数据线、授权交还、成稿写产出区（开关开时）、交付检查、电脑同步、测试与孵化的推进 |

## 四、自己存什么

| 块 | 表（PostgreSQL，前缀 `workbench_`） |
| --- | --- |
| 项目与对话 | `projects`、`sessions`（含 knowbase 会话编号、来源 `origin`）、`session_events`、`commands`、`approval_log`、`tool_grants` |
| 委托与账 | `tasks`、`attempts`、`artifacts`、`budget_ledger`、`interactions`、`task_outputs`（待写/已写进 knowbase 产出区的成稿与交付时的 sha256） |
| 专家与数据 | `knowbot_pins`（钉住的分身，只增）、`task_resolution`（一件委托一行：knowbase 清单编号、修订、确认编号、授权 ref、需求单号、等什么、领用期限 `checking_until`、按 ref 交还状态）、`task_data`（钉住的几份，来源只认 `knowbase`） |
| 运行方 | `test_runs`、`test_cases`、`test_answers`、`incubations` |
| 电脑与沙箱 | `environments`、`sandboxes`、`sandbox_leases`、`relay_identities`、`agent_pairings`、`agent_install_credentials`、`agent_audit_events` |
| 用户设置 | `credentials`（加密的模型 key）、`user_prefs`、`memories` |

另有模板的 `auth_user`、`outbox_message`、`inbox_message`；对象存储桶 `agent-releases` 放本地 link 安装包。

已删掉的旧东西（⑰）：清单 v1 与它的分支、`workbench_session_data`（对话里逐份选的云端知识库）、钉住来源 `cloud`/`local`、经 knowlab 读数据（`knowlab_data_client`）、旧数据集工具、云端知识库页与选数据弹框、内置的「问数」「财报体检」「财务分析与预测」。按 decisions「数据拓扑第四版」①（10-26）删了本地知识库页面、侧栏入口、设置里的目录（配套本地 link 0.5.4 删 `libraryDir`）。另按 decisions「发版前补齐」①（10-29）删了「没有数据」卡片、步骤的 `missing_data` 与管理端「缺数据的需求」，由 knowfeed 管理端的缺口清单取代；`workbench_session_events` 里旧的 `data.missing` 事件留着，代码不读。库里还留着代码已不读的旧表：`workbench_library_items` 与最早一批 `agent_*`（`agent_runs`、`agent_sessions`、`agent_pilot_*` 等），迁移里没删。

## 五、和别的应用

| 对方 | 怎么连 |
| --- | --- |
| knowmart | 服务关系 `knowmart:summon`：按用户会话取某一版清单、钉住；`knowmart:catalog`（只 api）：「找专家」取这位用户请得动、运行方是 knowbench 的专家公开信息；`knowmart:demand`（只 api）：用户点「发布」后代挂需求。跨应用链接：去 knowmart「我的分身」（`knowmart.knowbots`），选定后带 `knowbot=` 回来。锁 `contracts/knowmart-knowbot-manifest-v2-lock.json` |
| knowlab | 收：`knowbench:testrun`（契约 `knowbot-test-run/v1`，含 `readiness`、`cancel`，锁 `contracts/knowlab-test-run-lock.json`）、`knowbench:incubate`（契约 `knowbot-incubation/v1`，锁 `contracts/knowlab-incubation-lock.json`），都是 knowlab 调 knowbench。发：`knowlab:incubation-request`（只 api）：以用户名义建「问题」申请。跨应用链接：knowlab 申请页、专家页「去 knowbench 请它」带 `knowbot=`、`task=` 进来 |
| knowbase | 本人令牌（Casdoor 令牌交换换来）：解析、重解析、确认（带供给条件快照）、写回偏好（`consumer` 按 `expert:<id>` 不带版本）、签运行授权、登记会话；服务关系 `knowbase:user-data-read`：等数据时重解析、凭确认续签、按 ref 交还授权；服务关系 `knowbase:user-data-output`（runner，受 `WORKBENCH_OUTPUT_WRITE_ENABLED` 开关控制）：替用户把交付的成稿写进产出区并查重；数据 MCP 中继用 knowbench 签的 `knowbase-data` 令牌。契约 `user-data/v2`；锁 `contracts/knowbase-data-request-lock.json`（`data-request/v1`，一样数据的描述）。跨应用链接：采不来的条目去 `knowbase.upload` 直达上传，传好带 `?ref=<委托编号>` 回来 |
| knowfeed | 发：服务关系 `knowfeed:supply-demand`（api、worker、runner）：问预切合（契约 `knowfeed-supply-prematch/v1`，锁 `contracts/knowfeed-supply-prematch-lock.json`）、提需求单、按单号查、取消；第 0 步「查主体」查证券名录；补采与预切合受开关 `WORKBENCH_DATA_SUPPLY_ENABLED` 管，没开或没配一律「暂不能补采」。收：`knowbench:supply-status`（契约 `knowfeed-supply-status/v1`，锁 `contracts/knowfeed-supply-status-lock.json`，入口 `POST /api/internal/v1/knowfeed/demand-status`） |
| 会合点、供给器（平台层） | 集群内：供给器 `:8080`、会合点管理通道 `:47100`；交给本地 link 的是公网地址；runner 连各沙箱的 `47800` |
| 本地 link（[sunmoon-link](sunmoon-link.md)） | 经会合点；令牌由本应用签、会合点就地验；在装有本地 link 的电脑上网页直连回环口 |
| 模型厂商 | 不经本应用：key 只进用户自己的沙箱，由沙箱里的 Codex 调 |

## 六、照什么做的

| 块 | 决定 | 设计 |
| --- | --- | --- |
| 叫法 | 10-29「叫法：账号不分类型……」 | [叫法](../叫法.md)、[账号-电脑-link-会合点](../账号-电脑-link-会合点.md) |
| 三种对话、设置三项、侧栏 | — | [0017](../../design/SDD/modules/0017-three-kinds-of-conversation.md)、[0021](../../design/SDD/modules/0021-settings-three-kinds.md)、[0016](../../design/SDD/modules/0016-sidebar.md)、[0024](../../design/SDD/modules/0024-new-project.md) |
| 专家从 knowmart 请、钉住 | ⑰（只认 v2） | [0027](../../design/SDD/modules/0027-knowbot-first-path.md) P4、[0018](../../design/SDD/modules/0018-advisor-market.md) |
| 第 0 步定数据、预切合、用户确认、等数据、写产出区 | ⑫ ⑭ | [请专家与执行](../../总纲/专家方案设计/专家使用方案/opus/请专家与执行.md) 第五、八节（原《请专家方案设计》第 4.3、4.8 节），[0043](../../design/SDD/modules/0043-data-v4.md) 第 2.6、2.7、3、4.1 节，[0045](../../design/SDD/modules/0045-knowfeed-supply.md) |
| 数据工具中继 | — | [0048](../../design/SDD/modules/0048-model-data-tools.md)、[0030](../../design/SDD/modules/0030-knowbot-compute.md)（`compute`） |
| AI 请专家 | ⑭ 晚补、10-29「AI 请专家」 | [请专家与执行](../../总纲/专家方案设计/专家使用方案/opus/请专家与执行.md) 第 4.2、4.3 节，[专家孵化方案](../../总纲/专家方案设计/专家孵化方案/opus/专家孵化方案.md) 第十三节、第十八节第 6 步 |
| 运行方：测试 | ⑯ | [0027](../../design/SDD/modules/0027-knowbot-first-path.md) 第 3.4 节、[0046](../../design/SDD/modules/0046-knowlab-self-service.md) 第三节 |
| 运行方：孵化一轮 | ⑮ ⑯ | [专家孵化方案](../../总纲/专家方案设计/专家孵化方案/opus/专家孵化方案.md) 第八节、第十五节第 3 步 |
| 删旧的 | ⑰、10-26「数据拓扑第四版」 | [0043](../../design/SDD/modules/0043-data-v4.md) 第 4.1 节、[数据拓扑](../../总纲/数据拓扑.md) |
| 平台电脑 | 10-29 叫法 | [账号-电脑-link-会合点](../账号-电脑-link-会合点.md) 第八节 |

## 七、部署

`gitops/components/app-platform/knowbench-app/`（Fable 的工位为准）：

- `knowbench-web-frontend/`、`knowbench-admin-frontend/`：两个前端；web端 `knowbench.<站点域名>`，管理端 `knowbench-admin.<站点域名>`。
- `knowbench-backend/database`、`migration`、`redis`、`rabbitmq`、`identity`：模板共有的库、迁移、缓存与消息、登录。
- `knowbench-backend/runtime`：起 api、worker、scheduler、runner 四个角色，带各服务身份的凭据。
- `knowbench-backend/agent-releases`：本地 link 安装包上传与核对。
- `knowbench-backend/platform-computer`：平台电脑，名单在后端 `config.yaml` 的 `platform_computers`，现在一台配给 `knowbot-tester`。
- `knowbench-backend/knowmart-summon-identity`、`knowmart-catalog-identity`、`knowmart-demand-identity`、`knowlab-incubation-request-identity`、`knowbase-user-data-read-identity`、`knowbase-user-data-output-identity`、`knowfeed-supply-demand-identity`：出站服务身份，各一条关系。
- `knowbench-backend/service-identity`（旧 `knowbase:retrieve`）、`knowlab-read-identity`：还在部署里，代码不用（见下节）。
- 收的三条关系 `testrun`、`incubate`（调用方 knowlab）与 `supply-status`（调用方 knowfeed）写在后端 `config.yaml` 的 `service_receivers`。

## 代码和设计对不上的

1. **部署里还配着代码已不用的关系**（已列入 交Fable-gitops（`docs/总纲/数据拓扑重构/交Fable-gitops.md`，2026-11-09 已删，原文见本仓提交 `cd049767f`） 第二节，随发版删）：后端 `config.yaml` 的 `knowlab:read`（⑰ 删了经 knowlab 读数据）、`knowbase_service`（`knowbase:retrieve`）、`KNOWBOT_TEST_SUBJECT`/`KNOWBOT_TEST_WORKSPACE`/`KNOWBOT_TEST_MONTHLY_LIMIT`（⑯ 后测试在作者账号下跑），代码里都没有读的地方；应用仓 `contracts/knowbase-retrieval-provider-lock.json` 也还在，没有调用方。
