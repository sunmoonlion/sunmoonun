# knowbase-app：资料库

> 最后更新：2026-10-29 ｜ 按 qwen 分支代码重写 ｜ 骨架继承 [`tpl-app.md`](tpl-app.md)，本文只写它多出来的 ｜ 总览见 [`../overall-architecture.md`](../overall-architecture.md)

**层与线**：第 6 层应用层；第 7 层数据线（knowfeed → knowbase）的终点（[架构总纲](../../总纲/架构总纲.md)第二节）。按 [数据拓扑](../../总纲/数据拓扑.md) 第四版，它是云端来源数据唯一的真源。

knowbase 替用户存数据，并管「谁能读」。云端的资料、内容版本、读法、使用权、同意依据、运行授权、读数留痕，都以它为准；公开披露也存在这里，只存一份。knowfeed 采来的交给它，knowbench、knowlab、knowmart 要用数据都来问它，它自己不调别的应用。模型在委托里读数据，走它的数据 MCP。用户管自己数据的 web端（SDD 0044）还没有页面，后端接口已经有了（见文末）。

## 一、谁来做什么

**用户**（本人在各应用页面上点，应用后端凭本人令牌转交）：
- 上传资料、传新版本、改描述、改许可档、删、下载（后端接口有，现在没有页面调）。
- 点展示：给 knowbench、给 knowlab、交给 knowmart 待上架、绑给名下专家；可以批量；第一次点「新数据默认展示给我的全部应用」这个开关，点过才生效。
- 在 knowbench 委托页、knowlab 测试集上确认数据清单：knowbase 记一条确认，7 天有效。
- 开委托、开会话、孵化时签运行授权（在应用里点开跑，与钉住同时完成）。
- 选平台孵化、平台测试时留下平台过程的依据，可以撤回。
- 把一份产出「转为数据」；看一份资料谁读过。
- 跨全市场查公开原件抽出的事实（受平台总开关管）。

**作者**：把自己的数据绑给自己名下的专家；交付时由 knowlab 把绑定冻结在那一版上。**请专家的人**：委托里读作者绑定的数据，读数留痕里作者是内容所有者、请的人是受益人。

**平台人员**（管理端，admin 或 operator）：看旧链的知识入库作业、改状态、重试，查 RAGFlow 配置。禁用资料、清除内容只有后端服务方法，管理端没有入口。

**别的应用**（系统替用户做的事）：
- knowbench 替用户解析委托第 0 步提出的数据描述、数据齐了凭本人那次确认续签授权、凭授权读；模型经 knowbench 中继调数据 MCP。
- knowlab 替作者签测试授权与平台过程授权、结束平台过程、重解析测试集。
- knowmart 成交后请 knowbase 给买家建使用权，读卖家「交给 knowmart」的那一栏。
- knowfeed 交来公开原件、给提了需求的用户记引用、受理前核确认、领加工授权写回读法与事实。
- knowbase 自己：按描述查、解析、裁决授权（解析器不签）、每次读留痕。

## 二、页面与流程

**web端**（`knowbase.<站点域名>`，sunmoonai 组织登录）：只有模板页。
- 首页：一句「这里没有给你看的页面」。
- 工具箱：模板的前端组件参考页。
- 0044 定的总栏、资料详情、上传、直达上传、产出转为数据、给平台的授权、设置，都还没有页面。

**管理端**（`knowbase-admin.<站点域名>`，built-in 组织，admin 或 operator）：
- 治理控制台：模板首页。
- 知识入库：旧链的入库作业列表、改状态、重试、RAGFlow 配置检查。
- 设置：界面的主题、密度、语言。CRUD 参考、富能力参考：模板样例页。
- 用户资料用量、词表维护、禁用资料的处理（0044 第四节）都没有页面。

**流程一：请专家时拿数据**（knowbench 委托；knowlab 测试集同一套接口）
1. 用户在 knowbench 选专家、写问题；knowbench 凭本人令牌在 knowbase 建一张空的解析清单。
2. 委托第 0 步，用户自己的模型按「一样数据的描述」（契约 `data-request/v1`）提出要哪些；knowbench 以服务身份交给 knowbase，清单出新修订。
3. knowbase 逐样解析，每样一个结果：已定、你有没放开、待确认、采不来、有歧义、等数据、不能用。公开原件优先于上传的；只认确认过的描述。
4. 用户在委托页确认（可以换、改、去掉、加）。knowbench 凭本人令牌交 knowbase，knowbase 记确认并回入口分支：已有的直接用；公开原件层已有内容与读法的，当场在用户名下建引用；缺的由 knowbench 带确认编号交 knowfeed，knowfeed 受理前向 knowbase 核这个编号。
5. 开跑：knowbench 凭本人令牌签委托授权，钉住输入组合（内容版本、读法版本、各自摘要）。要等补采的，数据齐了 knowbench 请重解析，再凭那次确认续签（决定 ⑫）。
6. 运行中：模型调工作台 MCP 上的数据工具，knowbench 当场签一张 5 分钟的令牌转给 knowbase `/api/mcp/data`；knowbase 按 `run` 找有效授权、逐项核、留痕，回的每个数、每段文字都带出处。
7. 结束：knowbench 交还这件事签过的全部授权。

**流程二：公开披露入库**
1. knowfeed 取到原件，交给 knowbase：同一渠道同一编号只存一份，归保留编号 `public:disclosure`；内容变了记新的内容版本。
2. knowfeed 给提了需求的用户各记一条引用（取得依据「引用」的使用权）。
3. knowfeed 领加工授权，写回正文、按页文字；抽好的表写成一批事实行（原样层、标准化层），会计恒等式质检照实记在读法上，不改数。

**流程三：上传与加工**（后端已有，没有页面）
1. 本人上传：PDF、Excel、CSV、文本、Markdown，单份 50 MB，一个账号 1 GB。建资料、第 1 版、取得依据「上传」的使用权；勾了确认的描述才参与解析。
2. 默认展示开关开着、而且本人点过，自动展示给 knowbench、knowlab。
3. 勾了加工就记一条加工依据，这一版进「待加工」清单（`/processing/pending`）；加工授权只限这一版、3 天。knowfeed 代码现在只给自己交来的公开原件领加工授权，还不来领上传的。

**会话**：knowbench 发消息时登记会话（24 小时，范围是展示给 knowbench 的）；模型第一次读某一份，knowbase 当场签一条小授权，读到 50 份提示一次。

## 三、后端

代码在 `knowbase-backend/app/app/`。用户资料的接口都在 `/api/internal/v2/user-data`，只认集群内地址。

| 块 | 代码 | 说明 |
| --- | --- | --- |
| 资料库 | `domain/user_library.py`、`application/services/user_library_service.py`、`interfaces/endpoints/user_library_routes.py` | 资料、内容版本、使用权、展示（同意依据）、账号默认、名下专家影子表、订阅范围、平台过程依据、公开原件与引用、成交建使用权 |
| 描述与词表 | `domain/vocabulary.py` | 第 2 版：类型分大类（发布者）与细类，主体、期间、版本形态进键，事项、行业等只筛选 |
| 按描述查与解析 | `domain/user_resolution.py`、`user_resolution_service.py`、`user_resolution_routes.py` | 按描述查（只认进键的维度，不列不浏览）、解析清单与修订、确认（7 天）、偏好（只读） |
| 运行与读 | `domain/user_runs.py`、`user_run_service.py`、`user_run_routes.py` | 运行授权（委托、会话、孵化、测试、平台过程、加工）、会话登记、凭授权读、读法、产出区、转为数据、谁读过、禁用与清除（只有服务方法） |
| 科目表与事实 | `domain/chart_of_accounts.py`、`domain/user_facts.py`、`user_fact_routes.py` | 科目表第 2 版（一般企业，对上 2015 版通用分类标准元素；银行一组随银行专家再填）、指标定义；写回事实、按运行查、跨全市场查 |
| 数据 MCP | `interfaces/mcp/data_mcp.py` | `/api/mcp/data`；工具 `list_inputs`、`read_input`、`query_facts`、`query_metric`、`read_facts`、`describe_items`、`search_evidence`、`lookup`、`list_library`；`search_evidence` 现在是在按页文字里按关键词找 |
| 身份 | `infrastructure/security/user_token.py`、`relation_auth.py`、`interfaces/http/internal/host_guard.py` | 本人令牌（应用经令牌交换换来，`azp` 记代办的应用）；六种服务关系；内部接口公网来的一律 404 |
| 对象存储 | `infrastructure/storage/user_objects.py` | 原件、读法对象 |
| 旧入库与检索 | `knowledge_routes.py`、`knowledge_ingestion_service.py`、`knowledge_retrieval_service.py`、`provider_delivery.py`、`infrastructure/external/ragflow*.py` | knowfeed 交文档进 RAGFlow、按数据集检索；发件箱只有这条链在用 |

## 四、自己存什么

- **PostgreSQL（`user_data_*`）**：资料 `user_data_item`、内容版本、读法、使用权 `holding`（含第二区引用）、同意依据 `use`、改动记录 `material_log`、账号设置、名下专家影子、产出、输入组合、运行授权及其各项、会话、读数留痕 `read`、删除事件、解析清单、确认、偏好；事实分原样层 `fact_raw` 与标准化层 `fact`。
- **PostgreSQL（旧入库链）**：`knowledge_ingestion_job`、`knowledge_provider_operation`、`knowledge_document`、`knowledge_document_version`；模板的发件箱、收件箱与 `auth_user`。
- **对象存储**：桶 `knowbase-originals`，前缀 `users/`，按用户编号的摘要分目录；原件按资料与内容版本存，正文、按页文字读法也存成对象；公开原件同在这个桶，所有者是 `public:disclosure`。
- **只读别人的桶**：旧入库链用账号 `knowbase_source_reader` 读 `knowfeed-originals`。
- **RAGFlow**：旧入库链的数据集 `sunmoon-kind-knowbase-default`，派生、可重建。Redis 前缀、RabbitMQ vhost 照模板。
- **已删的旧东西**（⑰）：SQLite 数据集登记 `knowledge_dataset`、语义层引擎、旧知识 MCP `/api/mcp/knowledge`、`user-data/v1` 与它的同意依据、授权四张表、成交复制。

## 五、和别的应用

| 对方 | 怎么连 |
| --- | --- |
| knowbench | 本人令牌（`azp` 为 knowbench）：建与改解析清单、确认、签委托与会话授权、登记会话、交还。服务关系 `user-data-read`（scope `knowbase:user-data-read`，knowbench 调）：替运行中的专家提新需求、重解析、凭确认续签、凭授权读、按运行查事实。数据 MCP：knowbench 中继，令牌由 knowbench 签（ES256，`aud` 为 `knowbase-data`），能读什么由 knowbase 按授权核。`user-data-output`（写产出区）：knowbase 已收、部署已开，knowbench 代码还没调 |
| knowlab | 本人令牌（作者）：测试集的解析与确认。`user-data-grant-test`（knowlab 调）：签与撤测试授权、平台过程授权，结束平台过程。`user-data-read`：重解析。`user-data-directory`（推名下专家名录、交付时冻结绑定）与 `user-data-output`：knowbase 已收、部署已开，knowlab 代码还没调 |
| knowmart | 本人令牌：读卖家「交给 knowmart」那一栏（`/columns/knowmart`）。`user-data-purchase`（knowmart 调）：成交给买家建使用权，同一交易只建一条 |
| knowfeed | `user-data-supply`（knowfeed 调）：核确认编号、交公开原件、记引用、领待加工与加工授权、写回读法与事实行。旧链：服务身份 `knowbase:ingest` 交契约 `knowfeed-knowbase-artifact` v1，进 RAGFlow（knowfeed 旧采集线还在调） |
| 跨应用链接 | 配置了去 knowfeed 的地址；认来自 knowbench（带回跳地址）、knowfeed 的链接。web端还没有页面用 |
| 契约（本仓 `contracts/` 是真源） | `data-request/v1`：一样数据的描述，附词表、科目表；knowbench、knowlab 锁 schema 摘要，knowfeed 锁词表与科目表。`user-data/v2`：全部用户资料接口。`artifact/v1`、`retrieval/v1`：旧入库与检索（knowbench 还留着检索的锁，代码已不调）。做法见 [契约](../topics/contracts.md) |

knowbase 不调别的应用，只出站到对象存储和 RAGFlow。

## 六、照什么做的

| 块 | 决定 | 设计 |
| --- | --- | --- |
| 总的：一份真源、两区、展示即同意、运行授权、读数留痕 | [decisions](../../design/decisions.md)「数据第四版开工中的讨论」；平台也是用户（数据拓扑第二节） | [数据拓扑](../../总纲/数据拓扑.md)、[0043](../../design/SDD/modules/0043-data-v4.md)；令牌交换与留痕沿用 [0042](../../design/SDD/modules/0042-knowledge-bases.md) |
| web端 | — | [0044](../../design/SDD/modules/0044-knowbase-web.md) |
| 公开原件存成资料、科目表、原样层与标准化层、跨全市场查、平台总开关 | 同上 ①②⑥⑦⑧⑨⑪ | [0047](../../design/SDD/modules/0047-public-disclosures-facts-search.md) |
| 数据 MCP、令牌、会话首读小授权 | — | [0048](../../design/SDD/modules/0048-model-data-tools.md) |
| 描述的维度与类型树 | 同上 ⑬ | [0049](../../design/SDD/modules/0049-document-types.md) |
| 第 0 步提数据、`data-request/v1`、偏好按描述 | 同上 ⑭ | [请专家方案设计](../../总纲/请专家方案设计.md)、0043 第三节 |
| 等数据后凭确认续签 | 同上 ⑫ | 0043 第 2.7 节 |
| 删旧数据集、语义层、旧 MCP、`user-data/v1` | 同上 ⑰ | — |
| 银行、保险、证券的科目以后再填 | 同上 ⑱ | 0047 第十节 |
| 加工、订阅、需求状态 | — | [0045](../../design/SDD/modules/0045-knowfeed-supply.md) |
| 平台过程授权 | 10-29「孵化第 5 步的三件」① | [0046](../../design/SDD/modules/0046-knowlab-self-service.md) |
| 叫法 | 10-29 叫法 | [叫法](../叫法.md) |

## 七、部署

`gitops/components/app-platform/knowbase-app/`（Fable 工位为准）：

- `knowbase-backend/database`：建 `knowbase` 库与运行、迁移两个账号。
- `knowbase-backend/migration`：用迁移身份跑一次性迁移。
- `knowbase-backend/redis`、`rabbitmq`：独立的 Redis 账号与前缀、RabbitMQ vhost。
- `knowbase-backend/identity`：注册 Web、管理端回调；建本人令牌的目标应用（令牌交换的 `aud`）。
- `knowbase-backend/storage`：建桶 `knowbase-originals` 与它的存储账号。
- `knowbase-backend/provider`：在 RAGFlow 建数据集，开 knowfeed 桶的只读身份（旧入库链用）。
- `knowbase-backend/runtime`：API、Worker、Scheduler；各服务关系的接收绑定、本人令牌认的三个应用、数据 MCP 令牌的签发方、两个桶的地址等配置。
- `knowbase-backend/samples`：Olist 样例数据集的登记脚本（旧数据集的遗留，已列进交 Fable 的清理单）。
- `knowbase-web-frontend`、`knowbase-admin-frontend`：两个前端。

删旧兼容以后 gitops 还剩要清的（`user-data-import` 接收绑定、`USER_DATA_READER_APPS_JSON`、`KNOWBASE_DATASET_*`、`KNOWBASE_SEMANTIC_*`、knowfeed 桶只读前缀放宽、样例脚本），见 [待你决定](../../总纲/数据拓扑重构/待你决定.md) 第 6 节第 2 条，交 Fable 排；目录里的 README 还写着「Knowfeed 原文仍是权威」，是旧说法。

## 代码和设计对不上的

1. **web端没有页面**：`knowbase-web-frontend` 只有登录、首页、工具箱三页，首页文案还写「数据在 knowbench 里问专家或代理就有；数据目录在管理后台」（`messages/zh-CN.json:88`，管理端的数据目录 ⑰ 已删）。[0044](../../design/SDD/modules/0044-knowbase-web.md) 定 web端是用户管数据的唯一入口（总栏、上传、展示按钮等），数据拓扑第 7.1 节定上传只在 knowbase web端；现在哪个应用都没有上传入口，knowbench 解析结果「采不来」却提示用户「到 knowbase 上传」。
2. **本人令牌只认三个应用**：`core/config.py:678` 只许 `USER_TOKEN_APPS_JSON` 映射到 knowbench、knowlab、knowmart。0043 第十节写「knowbase 的 `user_token_apps` 登记 knowfeed」，订阅范围同意要由 knowfeed 凭本人令牌转交（0045 第 2.1 节）；按现在的校验 knowfeed 进不来，订阅接口没人能调。knowbase web端自己也没有走到这些本人接口的路。
3. **正文、按页文字存在哪**：`application/services/user_run_service.py:664` 把这两种读法各存成对象存储里的一个对象，读法表只记对象键；0043 第五节与数据拓扑第 16.2 节写的是放 knowbase 的 PostgreSQL（正文每个读法版本一行、按页文字每页一行）。表格读法已按设计落成 PostgreSQL 的事实行。
4. **全市场读只有一道门**：公开原件全市场可读、跨全市场查事实，代码只核平台总开关 `PUBLIC_ACCESS_ENABLED`（`user_run_service.py:270`、`:799`、`:1262`），没有资格、权限的检查；0047 第二、四、五节与决定 ⑪ 写的是「资格、权限、平台总开关」同一道门。
5. **旧知识文档表还在用**：`knowledge_document` 两张表与 `knowbase:ingest` 入库链仍在（`infrastructure/models/knowledge.py:72`），knowfeed 旧采集线（`info_crawl_service.py:1301`）还在调；0047 第 2.4 节定这两张表退役，改为一个资料版本对应一个 RAGFlow 文档（排在 0043 块 9）。
6. **`user-data-read` 的调用方**：代码认 knowfeed 也能凭授权读（`interfaces/endpoints/user_run_routes.py:72`），`contracts/README.md:62` 也这样写；部署只给 knowbench、knowlab 开了这条关系，knowfeed 代码也不调。
