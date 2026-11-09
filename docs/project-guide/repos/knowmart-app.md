# knowmart-app：供需市场

> 最后更新：2026-11-01（M3 收清单硬查所绑数据与待处理版本、M5 交付带类目） ｜ 按 qwen 分支代码重写 ｜ 骨架继承 [`tpl-app.md`](tpl-app.md)，本文只写它多出来的 ｜ 总览见 [`../overall-architecture.md`](../overall-architecture.md)

**层与线**：第 6 层应用层；专家线 knowlab → knowmart → knowbench 的中间一环（专家在这里存放、上架、被请）；同时是用户之间买卖资料的地方，资料本身的真源在 knowbase。

knowmart 是专家与知识的供需市场。专家从 knowlab 交来，一版一版存在这里，作者定只自用还是申请公开、标每次请的价格；用户在专家目录里挑专家，回 knowbench 去请。知识是用户在 knowbase 里交给 knowmart 的资料，写成条目上架，别人买下后 knowbase 给买家建使用权，不复制。用户还能发需求、响应别人的需求。要公开专家、上架知识，先要过发布主体与资质审核（`C-L4`）。每个用户一家小店，自己的供给与需求都放进小店，首页是小店列表。本期标价、记成交，不接真实支付。叫法照 [叫法](../叫法.md)。

## 一、谁来做什么

**用户**

- 店主：在「我的小店 › 店主资料」改店名（默认取昵称，不能含「荐股」「推荐」之类，改了留痕）；看小店在不在首页列表上、被平台暂停的理由；点「看别人眼里的小店」。
- 作者：在「我的小店 › 我的专家」给 knowlab 交来的专家标每次请的价格，选「只自用」，或选类目后「申请公开」；在售版本所绑数据失效时转「待处理」（别人请不了、作者照样能请），小店里看得到原因，数据恢复后自动回在售。
- 作者：停用某一版要到 knowlab 停；详情页上停用一栏给的是「到 knowlab 停用」的链接。
- 卖家：先在 knowbase 总栏把资料「交给 knowmart」，再在「我的小店 › 我的知识」选资料写条目（名称、类目、说明、样张、权利声明、允不允许转卖、价格），交审核，或下架。
- 卖家：资料在 knowbase 里没了或不再出售时，用到它的条目自动下架（后台每 10 分钟核一遍，卖家打开「我的知识」时也核），原因写在这一条上。knowbase 连不上，这一轮就整轮不核；某一批被 knowbase 拒了，那几份这一轮不下架，记一条 `offer_check_batch_refused` 告警，下一轮再核。
- 入驻：在「我的小店 › 店主资料」登记个人或非个人主体，传证件照片，加证照，交运营审。一店一主体，主体改了要重审、留变更历史，成交上标当时卖的主体。
- 请专家的人：在「专家」目录看自己的专家和别人公开的专家，看详情；从工作台跳来时点「请这位」回工作台，不是从工作台来的点「去工作台请」。
- 逛市场的人：首页是小店列表（只列有在架供给或公开需求、没被停的店；按店名、类目找，按时间或店名排，不做推荐）；点进小店详情页看店主、在架的专家与知识、公开的需求、评价。条目、专家详情上链到所在的小店。
- 买家：在「找知识」或小店里找、点「买下」，资料进买家 knowbase 总栏的「买来的」。
- 需求方：在「需求大厅」发需求（要专家还是知识、要解决什么、要什么资料、期限、预算可空；「公开到我的小店」默认不勾，勾了才显示在小店页上），看响应（带响应的卖家的店）、选一家、结束需求。需求在大厅里匿名，卖家响应了才见到需求方的店。
- 卖家响应需求：写方案、报价、几天做好，可附自己已有的条目，也可做好上架后再补附。
- 成交双方：在「我的小店 › 交易记录」看买入、卖出的成交，每行带直达链接（买来的知识去 knowbase「买来的」那一份，请过的专家去 knowbench「专家」，卖出的知识去自己 knowbase 里那份）和条目现在的状态（在架 / 已下架 / 不可请）；买家评一次分（1–5 分加一句话），卖家回复一次；需求下公开留言，响应下双方私下留言；谁都能举报。

**平台人员（管理端）**

- 条目审核：审知识条目与申请公开的专家，页面标出禁止类的词（荐股、目标价、评级、收益承诺），通过或不通过（不通过写理由）。
- 资质审核：审发布主体与证照，看证件照片；已审过的主体或某张证照可撤销（写理由），相关公开专家即刻改回自用、在架知识下架。
- 举报处理：核实就下架（专家、知识、需求、响应、留言），或驳回。
- 驻场规则：改全文，出一个新版本，旧的留着。
- 成交记录：看全部成交，含还没办完的。
- 小店处置：按店名或店主找，停店、恢复（都写理由，留痕）。停店是持久的：停着时这家店不在首页列表，条目不能交审、审核转公开、被买、被请，需求不进大厅、不能被响应，店主也不能交审、申请公开、发需求、响应；条目自己的状态不动，恢复后被单独下架的照旧下架；已成交的照旧。

**别的应用与后台（系统替用户做的事）**

- knowlab 替作者交付用户同意、运营审过的一版专家（契约 `knowbot-delivery/v1`，可带「申请公开」与运营选定的类目；同一版自用转公开重查许可），停用某一版，收回某一版的公开（转公开撤回撞上已收下时），查已交各版的状态（在售 / 待处理及原因 / 停用），报没上架那一版的结局（用户不要 / 审核没过）。
- knowbench 替请专家的人取清单并钉住；AI 请专家时替用户查目录，用户点了「发布」后替用户挂需求。
- knowbase 列出卖家交给 knowmart 的资料；成交后给买家建使用权；核知识条目与专家所绑数据的状态与许可。
- knowmart 后台每小时扫一遍：证照到期前 30 天记提醒；过期的，相关公开专家改回自用、在架知识下架；审过满一年的证件照片清掉内容。
- knowmart 后台每 10 分钟以服务身份问 knowbase：一是待审、在架条目里的资料还交给着 knowmart、还卖不卖（`market-offers`），没了或不再出售的自动下架；二是在售专家版本所绑的数据还能不能经专家给别人用（`knowbot-bindings`），失效的转「待处理」、好了自动回在售。

## 二、页面与流程

**web端**（页头一行栏目：小店 · 找专家 · 找知识 · 需求大厅 · 我的小店 · 驻场规则）

| 页面（地址） | 在上面做什么 |
| --- | --- |
| 小店（首页）`/` | 登录了是小店列表：店名、平台店标、发布主体、资质标识、在架专家 / 知识 / 公开需求各几样、供给类目；按店名、一级类目找，按最近更新或店名排；没登录是公开介绍页 |
| 小店详情 `/shops/<编号>` | 店主（店名、发布主体、资质、平台店标）、在架的专家与知识、公开的需求、评价；停了的店只说「已暂停营业」 |
| 找专家 `/knowbots` | 专家目录：类目树（照腾讯 WorkBuddy 的服务类目）、搜名称或一句话、按更新时间筛、按最近更新或名称排，每页 24 位 |
| 专家详情 `/knowbots/<编号>` | 能做什么（接什么 / 不接什么 / 不接的去哪问；方法步骤只有主人看得到）、需要的数据（按你的问题定数据，专家自带几份）、交回什么、版本记录（含空号，没上架的原因只给主人看）、发布主体；价格与评价；停用 |
| 找知识 `/knowledge`、`/knowledge/<编号>` | 在架知识条目，按关键词、类目找；详情有说明、几份、样张、权利声明、能不能转卖、发布主体、所在小店、评价，买下、举报 |
| 需求大厅 `/demands`、`/demands/<编号>` | 收响应中的需求（匿名），发布需求（「公开到我的小店」默认不勾）；详情里响应、选一家、结束、留言；需求方看得到响应的卖家的店，响应了的卖家看得到需求方的店 |
| 我的小店 `/shop` | 页头：店名、在不在首页列表上或被暂停的理由、评分、「看别人眼里的小店」。六个页签：我的专家（价格、只自用、申请公开与类目、上架状态）、我的知识（写、改、交审核、下架、自动下架原因）、我的需求、我的响应、交易记录（买入的、卖出的；直达链接、条目状态、卖的主体、卖家的店；评价与回复）、店主资料（店名与留痕；发布主体与资质：主体资料、证件照片、证照） |
| 驻场规则 `/rules` | 最新一版规则 |

`/dashboard`、`/toolkit` 还是模板原样；页头的 knowmart 字样链到首页（小店列表）。

**管理端**（左侧导航六项，都在 `market/` 下）：条目审核 `listings` · 资质审核 `qualifications` · 举报处理 `reports` · 小店处置 `shops` · 驻场规则 `rules` · 成交记录 `trades`。后端另有「平台直接下架」和「手动扫一遍」（资质到期、照片清理、核资料）两个接口，管理端页面没接，下架现在只经举报处理。

**流程一：专家从交付到被请**

1. 作者在 knowlab 提交交付、过自用轻审或公开完整审核 → knowlab 后端调交付接口（契约 `knowbot-delivery/v1`）。knowmart 只收清单 v2（`knowbot-manifest/v2`），核外层，并向 knowbase 硬查所绑数据的状态与许可（不通过回 409 `binding_*`，没配或不可达回 503）；同一交付单号重发内容一样回原结果、不一样回 409；版本号照清单记（可有空号）；同一版自用转公开时重查许可并放开公开。交付带了类目的记在专家上。
2. 交付带「申请公开」的：卖家主体审过、类目要的证照也有，这一位才进条目审核；否则留自用，回包写明原因（没选类目 `category_needed`，资质不够 `not_qualified`，小店被平台停着 `shop_suspended`）。
3. 运营在「条目审核」通过 → 专家公开。别人看得到、请得到要同时满足：总开关 `PUBLIC_MARKET_ENABLED` 开着、专家公开、主体实名审过、类目要证照的有有效证照，且只限 knowlab 审成公开且在售（非待处理、非停用）的那几版。
4. 用户在 knowbench 点「请我的分身」→ 来到 `/knowbots`（带着来源与 `ref`）→ 选一版点「请这位」→ knowmart 后端核：是自己的或可请的公开专家、这一版没停用、运行方是 knowbench → 带 `knowbot=<编号>@<版本>` 回工作台 → knowbench 以 `summon` 关系取清单原文与摘要钉住。
5. 请的是别人的专家，记一笔成交（价格照条目，本期不收钱）。同一用户同一版只记一次：网页「请这位」和 knowbench 取清单（含 AI 替用户请）都走这一处。买家有一条已选定的需求、选中的响应附的正是这位专家时，成交记在那条需求上，需求随之结束。

**流程二：AI 请专家时 knowmart 这一头**

1. knowbench 的「找专家」调 `catalog`：回这个用户请得动、运行方是 knowbench 的专家，各取最新一版能请的——名称、一句话、类目、`pack.scope` 三项（接什么、不接什么、不接的去哪问）、版本、价格、免不免费（作者是本人、没标价或价格为零、请过这一版）。只按名称排，不排序、不加权。
2. 选定后照流程一第 4、5 步钉住、记成交。
3. 都不合适、用户在 knowbench 看过描述点「发布」→ knowbench 调 `demand`，需求记在这个用户名下，和在需求大厅自己发的一样。

**流程三：卖知识、买知识**

1. 卖家在 knowbase 总栏把资料「交给 knowmart」。
2. 在「我的小店 › 我的知识」写一条：后端凭卖家本人的令牌读 knowbase 里交给 knowmart 的那一栏，核每份是卖家自己的、许可是「可以出售」、不是买来又不许转卖的同样内容（按摘要比）。
3. 交审核要主体审过（类目要证照的还要证照）→ 运营审过上架。
4. 买家点「买下」：先记一笔「办理中」，逐份请 knowbase 建使用权（只到成交那一版，不复制，带转卖标记）；都建好记成交，有需求就结束需求。带幂等键，重来接着办，不会多建。
5. 卖家那份资料没了或不再出售：这笔记「没买成」（已建好的几份照旧归买家），条目自动下架。后台每 10 分钟、卖家打开「我的知识」时也会核一遍待审、在架的条目，原因（资料不在 / 不再出售）写在条目上。

## 三、后端

| 块 | 代码（`knowmart-backend/app/app/` 下） | 说明 |
| --- | --- | --- |
| 专家的存放与请 | `application/services/knowbot_service.py`；`interfaces/endpoints/knowbot_routes.py`；`domain/knowbots/delivery.py` | 交付（含硬查绑定、自用转公开、记类目）、停用、收回公开、查来源各版状态、空号结局、取清单；`catalog`、`demand` 两个内部接口；web端停用与「请这位」 |
| 清单 v2 | `domain/knowbots/manifest.py`、`schema.py` | 只核外层：名字、版本、运行方、`bindings`（作者挑选、交付时冻结的资料引用）、`rule_sources`；`pack` 只核骨架；摘要 |
| 专家目录 | `application/services/expert_catalog.py`；`interfaces/endpoints/expert_routes.py`；类目 `domain/knowbots/catalog.py` | 谁看得到只在这里判；筛、排、分页、详情；给 knowbench 的目录 |
| 供需市场 | `application/services/market.py`（用户一侧 `MarketService`、运营一侧 `MarketAdmin`）；`domain/market.py`；`interfaces/endpoints/market_routes.py` | 小店（列表、详情、我的小店、店名、处置）、主体与资质、专家上架与价格、知识条目、买、需求与响应、成交、评价、留言、举报、驻场规则 |
| 调 knowbase | `infrastructure/external/knowbase_user_data.py` | 契约 `user-data/v2`：列资料、建使用权、后台成批核知识资料与专家绑定 |
| 服务关系 | `infrastructure/security/relation_auth.py` | `deliver`、`summon`、`catalog`、`demand` 四种；按部署下发的配置认调用方，没配的关系一律拒 |
| 定时活 | `tasks/market.py`；`worker.py` 里的 `market-sweep`（每小时）、`market-offers`（每 10 分钟）、`knowbot-bindings`（每 10 分钟） | 重复跑不多做 |
| 跨应用跳转 | `domain/cross_app.py`；`interfaces/http/web/cross_app.py` | 回跳地址只从本应用配置查，不用链接里带的 |

## 四、自己存什么

- 库 `knowmart`、Redis 前缀 `knowmart:*`、RabbitMQ vhost `knowmart`（模板一套）；没有对象存储桶。
- 专家：`knowbot`（名称、一句话、主人、来源引用、当前版本、类目、可见范围、发布主体、价格、上架状态与审核说明）、`knowbot_version`（清单原文与摘要、状态 `active`/`held`/`stopped`、待处理原因与时间、允许公开）、`knowbot_unlisted_version`（空号那一版的结局）。
- 主体与资质：`publisher`（个人 / 非个人；身份证号只存遮住的样子和带钥匙的摘要）、`publisher_license`（证照）、`publisher_document`（证件照片存在库里，审过满一年清掉内容）。
- 小店：`shop`（一个用户一家：店名、处置状态与说明）、`shop_event`（改店名、停店、恢复的留痕）；`publisher_change`（主体变更历史，只记名称与个人 / 非个人）。
- 市场：`knowledge_listing`（只记资料引用、名字与摘要，内容在 knowbase；带自动下架原因）、`demand`（带「公开到我的小店」）、`demand_response`、`trade`（要建的几份、建好的几份、状态、幂等键、成交那一刻卖的主体）、`trade_request_alias`、`trade_review`、`market_message`、`house_rules`、`market_report`。
- 模板的 `auth_user`、`outbox_message`、`inbox_message`。
- 已删掉的旧东西（⑰）：清单 v1 的专家版本（只剩 v1 的专家连同空号结局一起删，订单历史不动）、knowmart 知识库页与 `user-data/v1` 调用、「复制」的叫法（成交表改叫 granted）、「只用自带数据」筛选。

## 五、和别的应用

内部接口的路径前都有 `/api`，并只认内部入口来的请求。

| 对方 | 怎么连 |
| --- | --- |
| knowlab | 关系 `deliver`（scope `knowmart:deliver`，只认 knowlab）：`POST /internal/v1/knowmart/deliveries` 交付（契约 `knowbot-delivery/v1`）；`POST …/owners/{用户}/knowbots/{编号}/versions/{版本}/stop` 停用（只停 knowlab 交来的）；`POST …/owners/{用户}/knowbots/{编号}/versions/{版本}/withdraw-public` 收回公开；`GET …/owners/{用户}/sources/{引用}/versions` 查已交各版状态；`PUT …/owners/{用户}/sources/{引用}/unlisted/{版本}` 报没上架的结局 |
| knowlab（链接） | 专家详情「到 knowlab 停用」→ knowlab web端「专家」栏 |
| knowbench | 关系 `summon`（`knowmart:summon`）：`GET …/owners/{用户}/knowbots/{编号}@{版本}` 取清单原文与摘要，请别人的专家时记成交 |
| knowbench | 关系 `catalog`（`knowmart:catalog`）：`GET …/owners/{用户}/catalog`，替用户找专家 |
| knowbench | 关系 `demand`（`knowmart:demand`）：`POST …/owners/{用户}/demands`，替用户挂需求 |
| knowbench（链接） | knowbench「请我的分身」→ knowmart `/knowbots`；「请这位」回 knowbench 工作台（回跳地址登记在 knowmart 的配置里）；不是从工作台来时「去工作台请」→ knowbench 工作台的「专家」 |
| knowbase | knowmart 调：`GET /api/internal/v2/user-data/columns/knowmart`（卖家本人令牌，向 Casdoor 换给 knowbase 的令牌）；`POST /api/internal/v2/user-data/purchases`（服务关系 `knowbase:user-data-purchase`）建使用权；`POST /api/internal/v2/user-data/service/market-offers/check`（同一关系，后台成批核知识条目里的资料还在不在、还卖不卖）；`POST /api/internal/v2/user-data/service/expert-bindings/check`（同一关系，收清单时硬查与每 10 分钟定时核在售专家所绑数据许可） |
| knowbase（链接） | 小店「交易记录」→ knowbase web端总栏那一份（去处 `knowbase.library`：`/library?category=purchased|uploaded&material=<编号>`，路径以 knowbase web端落地为准）；部署的去处里还没配 knowbase |
| knowbench（链接） | 小店「交易记录」里请过的专家 → knowbench「专家」`/workbench/expert`（去处 `knowbench.experts`） |
| knowbase、knowfeed | 跨应用来源里登记了，没配回跳地址 |
| 契约 | knowmart 是清单 `knowbot/v2` 与交付请求 `knowbot-delivery/v1` 的提供方，真源在父仓 `contracts/`；knowlab 持 `knowmart-knowbot-manifest-v2-lock.json` 与 `knowmart-delivery-v1-lock.json`，knowbench 持 `knowmart-knowbot-manifest-v2-lock.json`。`contracts/README.md` 只写了 knowlab 那几个接口，`summon`、`catalog`、`demand` 没写 |

## 六、照什么做的

| 块 | 决定 | 设计文档 |
| --- | --- | --- |
| 供需市场、小店 | decisions「knowmart 每个用户一家小店」（10-26）、「knowmart 供需市场的做法」（10-23 晚）、「三个应用相互独立……knowmart 改为专家与知识的供需市场」（10-23） | [0018](../../design/SDD/modules/0018-advisor-market.md) 第十、十一节（含第 7 之二小节） |
| 专家只经 knowlab、两道门、空号、停用在 knowlab | decisions「交付由用户定」「公开不再锁死，按资质定」（10-20） | [0037](../../design/SDD/modules/0037-idea-avatar-expert.md) 第五、六、十二、十八之二节；[0027](../../design/SDD/modules/0027-knowbot-first-path.md) |
| 公开按资质、类目、总开关 | decisions「对标腾讯 WorkBuddy」（10-18）、`C-L4`（10-20）、「总开关在开发站点开着」（10-25） | 0018 第十一节第 5 小节 |
| 专家目录 | decisions「都叫专家」（10-18） | [0032](../../design/SDD/modules/0032-knowmart-storefront.md) |
| 清单 v2、删旧版 | decisions ⑭、⑰ | [0043](../../design/SDD/modules/0043-data-v4.md) 第三、四节 |
| 买卖 = 使用权、卖资料 | decisions「数据拓扑第四版」（10-26） | [数据拓扑](../../总纲/数据拓扑.md) 第十一节；0043 第 4.3 节 |
| AI 请专家（`catalog`、`demand`、同一版只记一次） | decisions ⑭ 的 10-28 晚补、「AI 请专家（孵化第 6 步）的做法」（10-29） | [请专家方案设计](../../总纲/专家方案设计/专家使用方案/opus/请专家方案设计.md) 第 4.9 节；[专家孵化方案](../../总纲/专家方案设计/专家孵化方案/opus/专家孵化方案.md) 第十三节 |
| 资料没了自动下架 | 所有者 10-29 定（「数据拓扑重构/待你决定」第 7 条，没进 decisions；那份文件 2026-11-09 已删，原文见本仓提交 `cd049767f`） | 数据拓扑第十一节「卖家把许可档改低」一条 |

决定都在 [decisions](../../design/decisions.md)。

## 七、部署

`gitops/components/app-platform/knowmart-app/`（Fable 工位为准）：

- `knowmart-backend/`：`database`、`migration`、`redis`、`rabbitmq`、`identity`（模板一套）；`knowbase-user-data-purchase-identity`（knowmart 调 knowbase 建使用权、后台核资料用的服务身份）；`runtime`（API、worker、scheduler；`PUBLIC_MARKET_ENABLED`、`PLATFORM_PUBLISHER_CREDIT_CODE`（平台主体的统一社会信用代码，小店标「平台」用；没配就没有平台店）、跨应用来源与去处、身份证号摘要的钥匙）。
- 后端 `config.yaml` 的 `service_receivers` 写收哪几种关系：`deliver` 认 knowlab，`summon`、`catalog`、`demand` 认 knowbench。
- `knowmart-web-frontend/`、`knowmart-admin-frontend/`：两个前端。

## 代码和设计对不上的

1. **平台下架不收回买家的使用权；紧急撤回没做**。`application/services/market.py` 的 `MarketAdmin.take_down` 下架知识条目时「买家那份照旧在」，管理端举报页的说明也这样写（`knowmart-admin-frontend/app/messages/zh-CN.json:89`）；全仓没有「紧急撤回连在跑的也停」。数据拓扑第十一节、0043 第 4.3 节写的是「平台因违规下架，收回买家的使用权，留痕」；0018 第十一节第 9 小节第 3 项写了紧急撤回。
2. **过时的说明**：gitops（Fable 工位）`knowmart-app/knowmart-backend/config.yaml` 里调 knowbase 那段注释还写「契约 user-data/v1、复制进买家选的知识库」，`knowmart-app/README.md` 还写「只做私有模式」。
