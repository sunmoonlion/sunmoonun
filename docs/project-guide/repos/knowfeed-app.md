# knowfeed-app：采集

> 最后更新：2026-10-29 ｜ 按 qwen 分支代码重写 ｜ 骨架继承 [`tpl-app.md`](tpl-app.md)，本文只写它多出来的 ｜ 总览见 [`../overall-architecture.md`](../overall-architecture.md)

**层与线**：第 6 层应用层；第 7 层产品线里**数据线**的第一环（knowfeed → knowbase）。在数据第四版里它是「供给的门」，不是真源。

knowfeed 替用户采公开数据，采到的交给 knowbase。数据第四版（[数据拓扑](../../总纲/数据拓扑.md) 第七节、SDD [0045](../../design/SDD/modules/0045-knowfeed-supply.md)）把它拆成三块：**需求**（谁要什么，只用 knowbase 的统一词表说）、**供给**（渠道、取、加工）、**切合**（把一条需求对到能供它的渠道）。现在代码里通的是一条竖线：精确描述 × 巨潮目录渠道 × 下载、按页文字、财报抽表 × 交 knowbase 拿回执；另有给 knowbench 第 0 步「查主体」用的证券名录；渠道登记在来源目录里，由平台人员在管理端审、启停、排先后。原件只在 knowfeed 留 30 天，真源在 knowbase；knowfeed 不在读数据的路上。旧的证券专线和旧 SQLite 数据集已退（decisions ⑰）；旧的通用采集还在代码里，等着退。

## 一、谁来做什么

**用户**（现在都不直接打开 knowfeed）：

- 请专家的人：在 knowbench 委托第 0 步的数据清单上确认缺的那几样；确认记在 knowbase，knowbench 拿着确认编号来 knowfeed 提单。
- 作者：在 knowlab 测试页确认测试集缺的公开披露；同样由 knowlab 来提单。
- web端没有给用户的页面，用户没法在 knowfeed 自己提需求、看「我的需求」。

**平台人员**（管理端，要 `admin` 或 `operator` 角色）：

- 来源目录：登记渠道、改登记、对一条样例描述试采、审核（放行或审不过，都写凭什么）、在用 / 暂停 / 停用、排先后、看这条渠道的审核记录。巨潮这条渠道是迁移里登记的，也在这里管。
- 待审网站：看哪些网站在等审、各有几个需求项和几个人在等；待审太多或等太久页上告警。
- 缺口清单：「无法满足」的需求项按哪种、哪类汇总，据此补渠道；只写几项、几个人、几个主体，看不出是谁要的。
- 队列监控：各渠道的作业排着、在跑、等重试几个，一天里成败几个和失败原因；看一个作业的每次尝试，把等着的作业马上再排。
- 资讯采集：旧通用采集的一页，给一个网址建采集作业、按关键词和状态翻文档列表。

**别的应用**（系统替用户做的事）：

- knowbench：代用户提需求单、按单号查进度、取消；委托第 0 步模型「查主体」时来查证券名录。
- knowlab：测试集缺的公开披露，凭作者本人的确认提单、查进度、取消。
- knowbase：替 knowfeed 核确认；收公开原件、给需求依据记第二区引用；发加工授权，收按页文字和财报事实行。

**knowfeed 自己**：受理需求单（按归属用户核配额）、切合到渠道、跑作业（列、取、留存、交付、加工）、出回执；需求状态每变一次推给提单的应用；渠道连续失败到次数自动暂停；每小时删一批到期原件的内容、把过了时限没人审的网站上在等的需求项转「无法满足」；每天至多刷新一次证券名录。

## 二、页面与流程

| 端 | 页面 | 做什么 |
| --- | --- | --- |
| web端 | 首页（`/zh-CN/dashboard`） | 只有一句「这里没有给你看的页面」和一句旧说明（见文末第 3 条） |
| web端 | `toolkit` | 模板自带的前端公共能力参考页 |
| 管理端 | 来源目录（`/zh-CN/knowfeed/channels`） | 渠道列表（先后、大类、审核、状态、许可档、限速与日上限、连续失败）；登记渠道；点进一条看详情：改登记、试采、审核、在用 / 暂停 / 停用、审核记录 |
| 管理端 | 待审网站（`/zh-CN/knowfeed/sites`） | 待审的网站、待审起、在等的需求项与人数；告警 |
| 管理端 | 缺口清单（`/zh-CN/knowfeed/gaps`） | 按哪种（这类数据还取不到、渠道里没有这一份、网站审不过或没人审）× 类型汇总 |
| 管理端 | 队列监控（`/zh-CN/knowfeed/queue`） | 各渠道作业数与一天里的成败、失败原因；作业列表、每次尝试、马上再排 |
| 管理端 | 资讯采集（`/zh-CN/knowfeed/crawl`） | 旧通用采集：建采集作业、看文档列表 |
| 管理端 | 治理控制台、CRUD 参考、富能力参考、设置 | 模板自带 |

**流程一：请专家时补采公开披露（knowbench 代提）**

1. knowbench 委托第 0 步，用户自己的模型按专家逻辑和问题提出要哪些数据；knowbase 解析，本人没有的列成「待确认」给请专家的人。
2. 用户点一次确认，knowbase 记下确认编号（7 天内有效）；内容与读法 knowbase 都已有的，knowbase 自己立即建引用，不来 knowfeed。
3. 缺的那几项，knowbench 以服务身份调 `POST /api/internal/v1/supply/demands`：归属用户、提出方（`user`、`app`、`expert`）、代办链、任务编号、确认编号、幂等钥匙、各项（确认里的条目号、描述、要的读法）。一张单最多 50 项。
4. knowfeed 依次核：格式（主体现在只认 A 股代码 `600519.SH` 这种）→ 幂等（同一钥匙内容相同回原结果，不同就拒）→ 问 knowbase 核确认（每项的描述要和确认里那一条一字不差，否则拒）→ 按归属用户核配额（一小时内新提几张单、同时没办完几张、本月新取几份，北京时间自然月），超了回 429。只有真正的新受理才扣，幂等回原结果的不算，当场没有渠道的项不算新取；数是部署可改的环境变量。
5. 切合：按来源目录里的先后，找第一个审过、没停用、能供这个细类（按大类要的展开成细类）的渠道；暂停的渠道照接，作业等它恢复。没有渠道的项直接「无法满足」（原因 `no_channel`，进缺口清单）；有的就建取数作业，同一渠道同一描述跨用户只取一次（已有的就挂上去）；有任务编号的记作第 1 档，没有的第 2 档。
6. worker 跑作业：先看渠道，停用或审不过的，在等的项转「无法满足」；暂停的作业不跑、等恢复。再向巨潮「列」→ 渠道说没有就「无法满足」，不重试；有就「取」（定期报告取最新那一份，其余类型取披露时间窗里的每一份）→ 原件一个字节不改存进桶（按摘要去重）→ 交 knowbase 存成公开原件 → 这一版是新的就领加工授权，写回按页文字，全文定期报告再抽三张合并报表写回事实行 → 给每个在等的需求项在归属用户名下记一条引用 → 原件记「交付后留 30 天」，到期删对象存储里的内容（连各个版本），记录里只留出处与摘要；以后又取到同一份就把内容放回、从头再留 30 天。
7. 需求项按要的读法定状态：都齐了「已就绪」；原件到了、加工没成「部分就绪」。对方 5xx、限流、意外错误按 1 分钟、5 分钟、30 分钟、2 小时重试，最多 5 次，用完转「失败」。渠道每次没取到（限流不算）连续失败次数加一，到次数自动暂停并在日志报 `supply_channel_auto_paused`；答了（有没有都算）就清零。
8. 需求项状态每变一次，knowfeed 在同一个事务里经发件箱排一条通知（契约 `knowfeed-supply-status/v1`），worker 发给提这张单的应用；那个应用的 `supply-status` 关系没配就记日志跳过，不重试。knowbench、knowlab 的接收端还没做，现在仍按单号查；齐了由 knowbench 自己重解析清单、凭本人那次确认续签接着跑（decisions ⑫）。

**流程四：来源目录与审核（平台人员在管理端）**

1. 登记一条渠道：编号、名称、大类（目录型、订阅源、通用网页、搜索）、插件、能供的细类、能给的读法、许可档、每分钟限速与每天上限、网站（通用网页型必填，一个网站一条）、条款链接、能否渲染、守不守 robots。登记后是「待审」，不改代码。
2. 试采：对一条样例描述排一次，worker 跑一遍「列」和「取」（不留存、不交付），结果显示在详情页。现在只有巨潮插件能试采；通用网页插件还没有，这类渠道只能登记和审。
3. 审核：最近一次试采成功、且试采后没改过登记，才能放行，放行时定许可档；也可以记为审不过（包括撤销已放行的）。都要写凭什么。审不过的，没办完的作业取消，在等它的需求项转「无法满足」。
4. 启停：暂停（作业等着）、恢复（等着的作业马上再排）、停用（没办完的作业取消，在等的需求项转「无法满足」）、启用（要已放行）。暂停、停用要写原因。
5. 排先后：切合按这个顺序试。每一次改动都记一条审核记录：谁、何时、做了什么、凭什么。
6. 待审网站：用户给的网址落在没登记的网站上时，自动建一条「待审」的通用网页渠道；过了时限没人审，在等它的需求项转「无法满足」；待审太多或等太久，页上告警并在日志报 `supply_sites_alert`。给网址的需求还没接，现在不会自动建（见文末）。

**流程二：knowlab 测试集补采**：作者在测试页确认后，knowlab 用同一个接口、同一套规矩提单、查、取消；knowlab 不调证券名录。

**流程三：查主体**：knowbench 第 0 步的 `find_subject` 调 `GET /api/internal/v1/supply/securities?q=`，按代码、简称、拼音首字母查，代码对上的在前，回代码与简称，最多 20 条。名录空着或超过一天没刷新时，经发件箱排一次刷新，worker 从巨潮取沪深京 A 股列表整份换掉；这次先回库里现有的。

需求的状态（`domain/supply/models.py`）：已受理、取数中、已就绪、部分就绪、失败、无法满足、已取消、超时，只往前走；需求单状态由各项汇总；取消只摘这张单的项，共享的作业照跑。

## 三、后端

| 块 | 代码（`knowfeed-backend/app/app/` 下） | 说明 |
| --- | --- | --- |
| 内部接口 | `interfaces/http/internal/supply.py`、`internal/host_guard.py` | 提单、查单、取消、查证券；只认集群内地址（`*.svc.cluster.local`、回环），公网来的一律 404 |
| 管理接口 | `interfaces/http/admin/supply.py` | `/api/admin/v1/supply/…`：渠道（列、登记、改、审核、启停、排先后、试采）、待审网站、缺口、队列与作业（看、马上再排）；要管理端的权限 |
| 认调用方 | `infrastructure/security/relation_auth.py` | 关系 `supply-demand`，见第五节 |
| 受理与切合 | `application/supply/demands.py`、`domain/supply/models.py` | 核格式、幂等、确认、配额；选渠道；建或挂作业。需求项结束的原因是稳定的编码（`no_channel`、`channel_has_none`、`channel_disabled`、`site_rejected`、`site_review_expired`、`readings_incomplete`、`cancelled`） |
| 配额 | `domain/supply/quota.py`、`core/config.py` 的 `supply_quota_*` | 按归属用户数，在受理的同一个事务里核；环境变量 `SUPPLY_QUOTA_PER_HOUR`、`_OPEN_DEMANDS`、`_MONTHLY_ITEMS`、`_SUBSCRIPTIONS`（订阅条数还没人核，订阅没做） |
| 来源目录 | `domain/supply/catalog.py`、`application/supply/catalog.py`、`infrastructure/repositories/supply_catalog.py` | 登记的校验、在用 / 暂停 / 停用怎么走、试采（发件箱主题 `knowfeed.supply.channel.trial.v1`，worker 跑）、审核、排先后、待审网站与过时限、审核记录。自动暂停次数、待审时限与告警的数是这里的常量 |
| 缺口与队列 | `application/supply/monitor.py` | 缺口按「哪种 × 类型」汇总（`uncovered`、`absent`、`site`）；队列按渠道数、作业详情、再排 |
| 作业 | `application/supply/jobs.py`、`infrastructure/messaging/delivery_handlers.py` | 发件箱主题 `knowfeed.supply.job.v1`；先看渠道状态，再列 → 取 → 留存 → 交付 → 加工 → 回执，尝试与退避重试，连续失败计数与自动暂停 |
| 状态推送 | `domain/supply/status_event.py`、`application/supply/notify.py`、`infrastructure/repositories/supply_status.py`、`infrastructure/external/app_supply_status.py` | 发件箱主题 `knowfeed.supply.demand.status.v1`；事件模型即契约 `knowfeed-supply-status/v1` 的来源（`python -m app.domain.supply.schema` 生成应用仓 `contracts/supply-status/v1/`）；发到对方 `POST /api/internal/v1/knowfeed/demand-status` |
| 原件留存 | `application/supply/retention.py`、`tasks/supply_upkeep.py`、`infrastructure/storage/object_storage.py` | 每小时删一批到期原件的内容（桶开了版本，各版本都删），记删的时间；同一个任务文件里还有待审网站过时限 |
| 巨潮渠道插件 | `application/supply/cninfo.py` | 描述 → 巨潮分类与查询参数；按标题认版本形态（全文、摘要、英文版）、细类与事项（0049 第四节）；取数走框架给的 Http，不自带网络客户端 |
| 取数边界 | `infrastructure/supply/adapters.py`、`infrastructure/external/crawl_http.py` | 只连公网、限大小与重定向；5xx、超时算可重试，4xx 不重试 |
| 加工 | `application/supply/processing.py`、`application/securities/report_extraction/`、`domain/securities/report_statements.py` | 按页文字（pdfplumber，一页一页取）；年报、半年报、一季报、三季报抽三张合并报表，年报、半年报另抽附注里折旧与摊销四项；原样层逐行写，认出科目的进标准化层（换算到元） |
| 抽表规则 | `domain/securities/financial_catalog.py` | 只剩两样：三张表的字段字典（字段名、来源字段、中文名、单位），给 `labels` 认科目；勾稽规则 R01–R09，给 `checks` 核等式。旧数据集用的行字段、关键科目、口径表、表间关系已删 |
| 词表副本 | `domain/supply/vocabulary.py` | knowbase 词表第 2 版里 knowfeed 用到的部分：细类与大类、定期报告、事项、版本形态 |
| 证券名录 | `application/supply/directory.py`、`infrastructure/repositories/supply_directory.py` | 查与排刷新；刷新任务 `knowfeed.supply.directory.refresh.v1` |
| 调 knowbase | `infrastructure/external/knowbase_supply.py` | 关系 `user-data-supply` 的客户端 |
| 记录 | `infrastructure/repositories/supply.py`、`infrastructure/models/supply.py` | 供给的表 |
| 旧通用采集（还在） | `application/services/info_crawl_service.py`、`application/collectors/`、`interfaces/endpoints/info_routes.py`、`infrastructure/external/knowbase_app.py` | 信息源、采集器、采集作业、文档与版本、分发进 knowbase（旧入库接口）；管理端「资讯采集」用它 |

定时任务：模板的投递泵（每 5 秒）；`supply_upkeep.purge_originals`、`supply_upkeep.expire_sites`（各每小时一次）。供给作业靠可靠投递排队；渠道登记里的限速、日上限有栏位、能在管理端改，作业还没照它排。

## 四、自己存什么

- **供给**（`supply_*`）：`supply_channel`（来源目录：登记的各项、审核结论、在用 / 暂停 / 停用与原因、先后、连续失败次数、网站（有网站的一个网站只能一条）；迁移登记了巨潮一条：目录型、已审、在用，网站 `cninfo.com.cn`，能供四类定期报告和临时公告、招股书、上市公告书、投资者关系活动记录、监管函件，读法原件、按页文字、表，许可档 `via_expert`）、`supply_channel_event`（审核记录：谁、何时、做了什么、凭什么）、`supply_channel_trial`（试采与结果）、`supply_demand`（需求单）、`supply_demand_item`（需求项、原因编码与回执）、`supply_job`（作业）、`supply_attempt`（尝试）、`supply_original`（原件的出处、摘要、对象键、交给 knowbase 后的资料编号与版本、留存到期日、内容删掉的时间）、`supply_security`（证券名录）。
- **对象存储**：自己的桶（部署名 `knowfeed-originals`）。供给的原件键 `supply/originals/<摘要前两位>/<摘要>`，交 knowbase 后留 30 天，到期删内容；旧通用采集的原文在 `knowfeed/original/…`。
- **旧通用采集的表**（还在）：`knowfeed_source`、`knowfeed_collector`、`crawl_job`、`raw_artifact`、`knowfeed_document`、`knowfeed_document_version`、`extracted_content`、`distribution_record`、`delivery_outbox_message_legacy`。
- 模板的：`auth_user`、`outbox_message`、`inbox_message`。
- **已删掉的旧东西**：证券专线整条（采集申请与申请人、关注清单与流水、写死的采集器、采集批次与条目、SQLite 数据集与向 knowbase 的登记）、东方财富 F10 采集（decisions ⑨、⑰，SDD 0045 第六节第 2 条）。

## 五、和别的应用

| 对方 | 怎么连 |
| --- | --- |
| knowbench → knowfeed | 关系 `supply-demand`，scope `knowfeed:supply-demand`。`POST /api/internal/v1/supply/demands` 提单、`GET /demands/{id}` 查、`POST /demands/{id}/cancel` 取消、`GET /securities` 查主体。knowbench 侧客户端 `infrastructure/external/knowfeed_supply.py`，补采受它自己的开关管，查主体不看开关 |
| knowlab → knowfeed | 同一关系、同一 scope；只用提单、查、取消（knowlab 侧 `infrastructure/external/knowfeed_supply.py`） |
| knowfeed → knowbase（供给） | 关系 `user-data-supply`，scope `knowbase:user-data-supply`，用自己单独一份服务身份（不借旧入库那份）。地址 `KNOWBASE_INTERNAL_URL` + `/api/internal/v2/user-data`：核确认 `GET /service/confirmations/{编号}`；交公开原件 `POST /service/public-originals`；记引用 `POST /service/public-originals/{资料}/references`；领加工授权 `POST /processing/grants`（归属 `public:disclosure`）；写回按页文字 `…/renditions/pages`、加工失败 `…/renditions/{读法}`、事实行 `…/facts` |
| knowfeed → knowbench、knowlab（状态推送） | 关系 `supply-status`，每个应用一份服务身份：`<应用>_INTERNAL_URL`（要 https）加 `<应用>_SUPPLY_STATUS_SERVICE_{CLIENT_ID,CLIENT_SECRET,SCOPE,DISCOVERY_URL,BACKCHANNEL_ENDPOINT}`，scope `<应用>:supply-status`，缺一项就是没开、通知跳过。`POST /api/internal/v1/knowfeed/demand-status`，带这张单的汇总状态与每一项。契约 `knowfeed-supply-status/v1` 在应用仓 `contracts/supply-status/v1/`，knowfeed 是真源。对方 5xx、连不上由可靠投递退避重试；4xx 也算没送到，留在死信里给人看 |
| knowfeed → knowbase（旧） | 关系 scope `knowbase:ingest`，旧入库接口 `/api/internal/v1/knowledge/ingestions`；只有旧通用采集的分发在用。契约 `knowfeed-knowbase-artifact` v1 |
| 契约与锁 | `contracts/knowbase-vocabulary-lock.json` 钉 knowbase 的 `data-request/v1/vocabulary.json`，测试核 `vocabulary.py` 与它一致；`knowbase-chart-lock.json` 钉 `chart-of-accounts.json`，抽表写标准化层的科目编码照它；`knowbase-provider-lock.json` 是旧入库契约的锁 |
| 跨应用链接 | 部署配了 knowbench（回跳工作台）、knowbase 能把用户带来，knowfeed 能带去 knowbase；knowfeed web端没有落地的功能页 |

**怎么认调用方**（`relation_auth.py`）：部署给 `SERVICE_AUTH_SUPPLY_DEMAND_CALLERS=knowbench,knowlab`，每个调用方一组受众（调用方的 client_id）、主体白名单（`admin/<调用方服务应用>`）、必需 scope（`knowfeed:supply-demand`），都由部署从调用方的出站配置推出。knowfeed 拿令牌逐个调用方试受众，签名、签发方、有效期每次都核，再核主体在白名单里、scope 对。通过了就知道是哪个应用：需求单记在它名下，查和取消只给它看。代码里写死只认 knowbench、knowlab，部署多配了别的也不认；一组都没配就是关系没开，一律拒。

需求状态推送只认 knowbench、knowlab 两个接收方（`app_supply_status.py` 写死）；两边的接收端还没做，现在应用以按单号查到的为准。

## 六、照什么做的

决定列里带圈的编号都在 [decisions](../../design/decisions.md)「数据第四版开工中的讨论」那一条下（2026-10-27、10-28）。

| 块 | 决定 | 设计 |
| --- | --- | --- |
| 供给的定位、三端分工 | —（所有者 10-26 原话见数据拓扑来源） | [数据拓扑](../../总纲/数据拓扑.md) 第二、三、七节；[0045](../../design/SDD/modules/0045-knowfeed-supply.md) 第一节 |
| 需求单、提出主体、受理、需求一生 | — | 0045 第二节；采集讨论记录（`docs/总纲/数据拓扑重构/采集讨论记录.md`，2026-11-09 已删，原文见本仓提交 `cd049767f`） |
| 入口分支、确认、续签 | decisions ⑫、⑭ | [0043](../../design/SDD/modules/0043-data-v4.md) 第 2.7、3.3 节；数据拓扑第八节 |
| 渠道、适配器、作业、切合 | — | 0045 第三、四节 |
| 公开原件存成资料、第二区引用 | decisions ① | [0047](../../design/SDD/modules/0047-public-disclosures-facts-search.md) 第二节 |
| 描述的维度、巨潮认法 | decisions ⑬ | [0049](../../design/SDD/modules/0049-document-types.md) 第四节 |
| 财报抽表、原样层与标准化层 | decisions ⑥、⑦、⑨（F10 不采）、⑱（银行保险证券不抽） | 数据拓扑第十六节；0047 第四节；[0008-info-statements](../../design/SDD/modules/0008-info-statements.md) |
| 查主体 | decisions ⑭ | [请专家方案设计](../../总纲/专家方案设计/专家使用方案/opus/请专家方案设计.md) |
| 认调用方、单独一份 knowbase 身份 | — | 交 Fable gitops（`docs/总纲/数据拓扑重构/交Fable-gitops.md`，2026-11-09 已删，原文见本仓提交 `cd049767f`） 第六节（答复 Fable 10-29 回执第 1、2 条） |
| 来源目录与审站、缺口清单、队列监控、配额、状态推送、30 天删原件 | decisions「发版前补齐」（10-29，① 缺口清单取代 knowbench「缺数据的需求」） | 0045 第 2.4、2.5、3.1、3.4 节、第四节、第七节块 2、4、7；发版前补齐计划（`docs/总纲/数据拓扑重构/发版前补齐计划.md`，2026-11-09 已删，原文见本仓提交 `cd049767f`） F2、F5、F8 |
| 退证券专线与旧数据集 | decisions ⑰ | 0045 第六节 |
| 叫法 | decisions「叫法」（10-29） | [叫法](../叫法.md) |

## 七、部署

`gitops/components/app-platform/knowfeed-app/`：

- `config.yaml`：应用开关。
- `knowfeed-backend/`：`database`、`migration`、`redis`、`rabbitmq`、`identity`（web端、管理端登录）、`storage`（桶 `knowfeed-originals`）、`runtime`（API、Worker、Scheduler；只有 Worker 能出公网 80、443）、`service-identity`（旧入库身份 `knowbase:ingest`）、`knowbase-user-data-supply-identity`（供给调 knowbase 的身份）。`config.yaml` 的 `service_receivers` 收 knowbench、knowlab 的 `supply-demand`。推需求状态的 `supply-status` 出站身份（knowfeed → knowbench、knowlab）、配额变量、桶上删各版本的权限、两个告警事件，部署里还没有，要配的列在交 Fable gitops（`docs/总纲/数据拓扑重构/交Fable-gitops.md`，2026-11-09 已删，原文见本仓提交 `cd049767f`） 第 2d 节第 5 条；不配时不推状态，配额用代码里的缺省。
- `knowfeed-web-frontend/`、`knowfeed-admin-frontend/`：两个前端。

## 代码和设计对不上的

1. **配置名**：0045 第九节末行、待你决定（`docs/总纲/数据拓扑重构/待你决定.md`，2026-11-09 已删，原文见本仓提交 `cd049767f`） 的平台配置表写 knowfeed 用 `SUPPLY_SERVICE_APPS_JSON` 认调用方、用 `KNOWBASE_SUPPLY_URL` 调 knowbase、身份沿用入库那份；代码（`relation_auth.py`、`knowbase_supply.py`）按 10-29 回执改成 `SERVICE_AUTH_SUPPLY_DEMAND_*` 和 `KNOWBASE_INTERNAL_URL` + `KNOWBASE_USER_DATA_SUPPLY_SERVICE_*`，自己一份身份，两个旧名代码里都不读。fable 工位 knowbench、knowlab 的 `config.yaml` 注释也还写着 `SUPPLY_SERVICE_APPS_JSON`。
2. **旧写入口已关（F3）**：0045 第六节退旧线已关停 `POST /admin/distributions/knowledge` 与分发调度，fail-closed 返回 410 Gone；旧通用文档模型与分发只投 knowbase 休眠声明退役。
3. **web端提需求与订阅管理**：已落地（0045 第一节、数据拓扑第三节）。web端支持用户通过网页直接提需求、查看我的需求进度，以及对持续关注的公开主题/网址进行订阅管理（包含订阅生命周期、暂停、续期与撤销）。
4. **管理端旧页已退（F3）**：旧通用采集「资讯采集」页面与导航项已清理退役；来源目录、待审网站、缺口清单、队列监控四页在用。待审网站页和过时限定时任务就绪，通用网页适配器已接进渠道插件。
5. **「正文文字」读法没人产**：接口收 `text`（`internal/supply.py` 的 `readings`），0045 第 3.4 节有正文抽取加工器；代码只产原件、按页文字、表（`jobs.py`），要了 `text` 的项最多到「部分就绪」（`processing.py:329` 的 `wanted_readings`）。
6. **状态推送链路**：已由 knowbench、knowlab 接收端完全对接闭环（`POST /api/internal/v1/knowfeed/demand-status`）。knowfeed 状态推进后会即刻通知对应业务方触发重解析与推进。
7. **几个数设计里没定**：0045 只写「连续失败 N 次」「N 天没人审」，配额的几个数也没写；代码取了拟值，配额能用环境变量改，自动暂停次数、待审时限与告警的数写死在 `domain/supply/catalog.py`，等定了再改。

其余还没做的（按渠道排队与限速、四档与按用户轮流、预切合与供给条件快照、换下一个渠道、订阅、给网址、按主题找、web端提需求等）0045 第九节、0049 第六节已逐条列出，本页不重复。
