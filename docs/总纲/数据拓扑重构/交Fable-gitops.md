# 交 Fable：随 qwen 这批代码要改的 gitops（10-29）

所有者 10-29：「都按你建议。你写份文档，我让fable现在就做」。本页列出数据第四版、删旧版兼容（decisions ⑰）、平台测试改在作者账号下（⑯）、孵化栏、平台电脑（10-29 叫法）、AI 请专家（decisions 10-29「AI 请专家」）这几批代码要的平台改动。都在 `sunmoonun/gitops`（和一处 `infrastructure/`），qwen 没动。每条的来龙去脉见同目录 [待你决定](待你决定.md) 对应的条号。

## 〇、代码在哪、怎么发

- qwen 的代码只在本地提交，没推。都在本地 `~/worktrees/qwen/<仓>` 的 `qwen` 分支上，各仓都已包含当时的 `origin/fable`，合进 fable 应该是快进或干净合并（合前照规矩先试合并）：

  | 仓 | qwen 头 | 比 origin/fable 多 |
  | --- | --- | --- |
  | knowbase-app | `f65a6c7` | 21 |
  | knowbench-app | `567c3b8` | 13 |
  | knowfeed-app | `569e3f9` | 8 |
  | knowlab-app | `0bfd91b` | 19 |
  | knowmart-app | `b5679a2` | 6 |
  | sunmoonun | 见 `git log origin/fable..qwen` | 只有文档 |

  上表是 10-29 第四轮评审前修正（第 2c 节）提交后的头；合之前再看一眼各仓 `qwen` 头。
- **新增类**（第一节）不影响现在跑着的旧代码，可以先上。
- **删除类**（第二节）必须和 qwen 的代码同一次发布：旧代码还在读这些变量、用这些身份，先删会断。
- **迁移会删生产记录**（所有者已同意，decisions ⑰）：knowmart 0010（0011 只改名、加列，不删行）、knowlab 0016–0018（0019–0021 只加列、加表，不删行）、knowbench 0030–0031（0032 只加列）、knowfeed 0019、knowbase 0018。knowfeed 0019 会删关注清单那 10 行与流水，所有者 10-29 定不导出（名单还在历史迁移 0013 的代码里）。

## 一、新增

### 1. 数据第四版的服务关系（待你决定第 2 条）

knowbase 按现有做法认 `SERVICE_AUTH_<关系>_*`；Casdoor 要给调用方的服务应用加 scope `knowbase:<关系>`。

| 关系 | 调用方 | 干什么 |
| --- | --- | --- |
| `user-data-directory`（新） | knowlab | 推名下专家名录；交付时冻结绑定 |
| `user-data-output`（新） | knowbench、knowlab | 替用户写产出区 |
| `user-data-supply`（新） | knowfeed | 凭加工依据领授权、写回读法；受理前核确认 |
| `user-data-read`（已有，加调用方） | 现在只有 knowbench，加 knowlab、knowfeed | 凭第四版运行授权读 |
| `user-data-grant-test`（已有） | knowlab | 第四版也用它签平台过程的授权、报过程结束 |
| knowfeed 收 `knowfeed:supply-demand`（新） | knowbench、knowlab | 提需求单、看进度、取消；另配 `SUPPLY_SERVICE_APPS_JSON`（服务身份 → 应用） |
| knowfeed 调 knowbase | knowfeed | `KNOWBASE_SUPPLY_URL`，客户端身份沿用入库那个，scope 要 `knowbase:user-data-supply` |
| knowbench 调 knowfeed | knowbench | `KNOWFEED_INTERNAL_URL`、`KNOWFEED_SUPPLY_DEMAND_SERVICE_*`（scope `knowfeed:supply-demand`），knowfeed 的 `SUPPLY_SERVICE_APPS_JSON` 把这个服务身份认成 knowbench。第 0 步的「查主体」也走它，没配时模型只能请用户给代码 |
| knowbench 补采开关 | knowbench | `WORKBENCH_DATA_SUPPLY_ENABLED=true`；默认关，关着时缺的数据一律「暂不能补采」 |
| knowlab 调 knowfeed | knowlab | `KNOWFEED_INTERNAL_URL`、`KNOWFEED_SUPPLY_DEMAND_SERVICE_*`（scope `knowfeed:supply-demand`），knowfeed 把这个服务身份认成 knowlab；补采开关 `KNOWLAB_DATA_SUPPLY_ENABLED=true`，默认关 |
| knowlab 调 knowbase 第四版 | knowlab | 测试集解析与确认走作者本人令牌（`KNOWBASE_USER_AUDIENCE` 同第一版）；重解析要 `user-data-read`，签与撤每条用例的测试授权要 `user-data-grant-test` |
| knowbase 认 knowbench 签的数据令牌 | knowbase | `KNOWBASE_MCP_JWT_PUBLIC_KEY`、`KNOWBASE_MCP_JWT_ISSUER` 填 knowbench 的公钥与 `WORKBENCH_TOKEN_ISSUER`（知识服务 MCP 已用同一对，配过就不用再配） |

### 2. 孵化的服务关系 `incubate`（待你决定第 9 条）

照 `testrun` 那一套，knowlab 调 knowbench，scope `knowbench:incubate`：
1. knowbench `config.yaml` 的 `service_receivers` 加 `{relation: incubate, caller: knowlab}`，生成 `SERVICE_AUTH_INCUBATE_*`（AUDIENCE `sunmoon-knowlab-knowbench-incubate`、SUBJECT_ALLOWLIST `admin/sunmoonai-knowlab-knowbench-incubate`、REQUIRED_SCOPE `knowbench:incubate`）。
2. knowlab `config.yaml` 的 `service_clients` 加 incubate（application `sunmoonai-knowlab-knowbench-incubate`），环境变量 `KNOWBENCH_INCUBATE_SERVICE_{APPLICATION,CLIENT_ID,SCOPE,DISCOVERY_URL,BACKCHANNEL_ENDPOINT}`，密钥 `KNOWBENCH_INCUBATE_SERVICE_CLIENT_SECRET` 进 sops（只挂 API 进程）；身份申领 `knowbench-incubate-identity/`、`stage.yaml`、`clusters/kind/stages.yaml`、Casdoor 组织与服务应用。入口共用 `KNOWBENCH_INTERNAL_URL`，traefik 已按前缀放行。
3. 作者的本地 link 要带 `service-projects-v1` 能力才能建「孵化」目录，旧版 link 这一轮直接失败（原因写明）。

### 2a. AI 请专家的三条服务关系（decisions 10-29「AI 请专家」）

都是 knowbench 调别人，做法同 `knowmart:summon`：调用方 `service_clients` 加一项，被调方 `service_receivers` 加 `{relation, caller: knowbench}`，生成 `SERVICE_AUTH_<关系>_CALLERS=knowbench` 与 `SERVICE_AUTH_<关系>_KNOWBENCH_{AUDIENCE,SUBJECT_ALLOWLIST,REQUIRED_SCOPE}`（关系名里的连字符换下划线）；Casdoor 加服务应用与 scope，密钥进 sops、只挂 knowbench API 进程。

| 关系 | 被调方 | knowbench 的环境变量 | 干什么 |
| --- | --- | --- | --- |
| `knowmart:catalog` | knowmart（`SERVICE_AUTH_CATALOG_*`） | `KNOWMART_CATALOG_SERVICE_{CLIENT_ID,CLIENT_SECRET,SCOPE,DISCOVERY_URL,BACKCHANNEL_ENDPOINT}`，入口共用 `KNOWMART_INTERNAL_URL` | 「找专家」时取这位用户请得动、运行方是 knowbench 的专家的公开信息 |
| `knowmart:demand` | knowmart（`SERVICE_AUTH_DEMAND_*`） | `KNOWMART_DEMAND_SERVICE_*`，入口同上 | 用户点「发布」后替他挂需求 |
| `knowlab:incubation-request` | knowlab（`SERVICE_AUTH_INCUBATION_REQUEST_*`） | `KNOWLAB_INCUBATION_REQUEST_SERVICE_*`，入口 `KNOWLAB_INTERNAL_URL` | 用户点「孵化一个专家」后，knowlab 以他的名义建「问题」申请 |

- SCOPE 必须正好是 `knowmart:catalog`、`knowmart:demand`、`knowlab:incubation-request`，`*_INTERNAL_URL` 必须是 https，缺一项 knowbench 就当没开（页面上「让 AI 找」那一轮会失败、写明原因）。
- `KNOWLAB_INTERNAL_URL` 现有的值（`…/api/internal/v1/knowlab`）就对，traefik `service-access` 已放行这个前缀；**所以第 3 条第 4 项里它不要删**，只删 `KNOWLAB_READ_SERVICE_*` 那一组。
- 这三条都不配，旧功能照常，只是「让 AI 找」用不了。

### 2b. knowlab 带用户去 knowbench 请专家（专家孵化方案第十三节第 5 条）

knowlab 申请页、专家页上，能用了的那一版给一个「去 knowbench 请它」的链接（`…/zh-CN/workbench?knowbot=<专家>@<版本>[&task=<找专家那一轮>]&from=knowlab&ref=<专家编号>`）。knowlab 现在没开跨应用链接，要两处：
1. `knowlab-app/knowlab-backend/config.yaml` 加 `cross_app_enabled: true`（照 knowmart 那样写一行注释）。
2. `common/backend/domain/prepare.yaml` 的 `target_names` 里 `'knowlab': []` 改成 `'knowlab': ['knowbench']`；第 80 行左右「谁带人去哪」的注释补一句「knowlab 去 knowbench（能用了的专家去工作台请，专家孵化方案第十三节）」。

推出来的 knowlab 环境变量应是 `CROSS_APP_TARGETS_JSON={"knowbench": {"web_base_url": "https://knowbench.<域名>:<端口>"}}`，`CROSS_APP_SOURCES_JSON` 照模板（knowbench 回跳、knowbase、knowfeed）。knowbench 那头不用改：它收到 `knowbot=` 就按用户会话向 knowmart 核验、钉住（走现有 `knowmart:summon`），不看 `from`；`CROSS_APP_SOURCES_JSON` 里没有 knowlab，所以工作台上不显示「回到 knowlab」，这是有意的。没配时 knowlab 页面照旧只写一句怎么去。

### 2c. 第四轮评审前补的两处（10-29）

1. **knowbench 管理端不再读 `KNOWFEED_ADMIN_URL`**（knowbench-admin-frontend `f0bb202`）：「缺数据的需求」原来链去 knowfeed 管理端的「证券采集」页，那一页已随 ⑰ 删了，链接一起去掉。`knowbench-app/knowbench-admin-frontend/config.yaml` 第 12 行与 `workload.yaml` 里的 `KNOWFEED_ADMIN_URL` 可以删；不删也不报错（多出来的变量没人读）。算删除类，和 qwen 代码同发。
2. **knowlab 登录后的回跳列表还是旧页面**：`knowlab-backend/config.yaml` 第 41 行的 `WEB_AUTH_ALLOWED_RETURN_PATHS` 列的是 `knowbots`、`questions`、`ideas`、`avatars`、`data`，现在 web端的栏是 `applications`、`names`、`review`、`experts`（加 `dashboard`、`login`），各两种语言（`/zh-CN/…`、`/en/…`）。不在列表里的回跳地址后端退回首页，不会出错，只是登录后回不到原来那一页。旧的几个地址前端会跳到新栏，可删可留。

### 2d. 发版前补齐要配的（10-29 起随做随补，见 [发版前补齐计划](发版前补齐计划.md)）

都和 qwen 代码同一次发。

1. **knowbase 公开数据的门**（knowbase-backend `09b8fe3`）：新变量 `PUBLIC_ACCESS_QUALIFICATION`（默认 `none`，不要求资格；`listed` 时只认名单）与 `PUBLIC_ACCESS_QUALIFIED_SUBJECTS_JSON`（默认 `[]`，格式不对进程起不来）。不配就照默认，不用动。
2. **knowbase 本人令牌认 knowfeed**（同上）：Casdoor 给 knowfeed 的网页客户端打开令牌交换，目标 `aud` 是 knowbase 的 `USER_TOKEN_AUDIENCE`；knowbase 的 `USER_TOKEN_APPS_JSON` 加一项「knowfeed 的 Casdoor 客户端编号 → `knowfeed`」。knowfeed 一头的令牌交换配置随 F1（knowfeed web端提需求、订阅）再补。
3. 迁移：knowbase 0019（正文、按页文字进库，只加表、删一列，不删行）。
4. **knowmart 小店**（knowmart-backend `70c2d4d`）：
   - 新变量 `PLATFORM_PUBLISHER_CREDIT_CODE`：平台主体（非个人）的统一社会信用代码，主体审过后那家店标「平台」；不配就没有平台店。
   - knowmart 的跨应用去处要加 knowbase（`domain/prepare.yaml` 的 `target_names` 里 `'knowmart': ['knowbench','knowlab']` 加 `'knowbase'`），不然「去 knowbase 看这份」的链接不显示。
   - 登录回跳：knowmart 的 `WEB_AUTH_ALLOWED_RETURN_PATHS` 加 `/zh-CN`、`/en`、`/zh-CN/shop`、`/en/shop`、`/zh-CN/shops`、`/en/shops`（按前缀认），`WEB_AUTH_DEFAULT_RETURN_TO` 改成 `/zh-CN`（首页现在是小店列表）。
   - worker 的定时多一项 `market-offers`（每 10 分钟核资料还在不在），随代码走，不用配。
   - 迁移：knowmart 0012（加表、加列，给已有用户各补一家店，不删行）。
5. **knowfeed 来源目录、配额、状态推送、30 天删原件**（knowfeed-backend `2359a81`）：
   - 新出站关系 `supply-status`：knowfeed → knowbench、knowfeed → knowlab。每个应用一组变量：`KNOWBENCH_INTERNAL_URL`、`KNOWLAB_INTERNAL_URL`（knowfeed 进程里，要 https），加 `KNOWBENCH_SUPPLY_STATUS_SERVICE_{CLIENT_ID,CLIENT_SECRET,SCOPE,DISCOVERY_URL,BACKCHANNEL_ENDPOINT}`（scope `knowbench:supply-status`）与 `KNOWLAB_SUPPLY_STATUS_SERVICE_*`（scope `knowlab:supply-status`）。接收端：knowbench、knowlab 的 `service_receivers` 加 `{relation: supply-status, caller: knowfeed}`，入口 `POST /api/internal/v1/knowfeed/demand-status`（两边接收端随后提交，这里先列）。不配就不推，应用照旧按单号查。
   - 可选变量：`SUPPLY_QUOTA_PER_HOUR`（默认 60 张单/人/小时）、`SUPPLY_QUOTA_OPEN_DEMANDS`（在途 20 张）、`SUPPLY_QUOTA_MONTHLY_ITEMS`（每月新取 500 份，北京时间自然月）、`SUPPLY_QUOTA_SUBSCRIPTIONS`（20 条）。
   - 桶权限：knowfeed 的 S3 身份要能 `ListBucketVersions`、`DeleteObjectVersion`（桶 `knowfeed-originals` 开了版本），桶上不能有阻止删除的对象锁。
   - 告警：按日志事件 `supply_channel_auto_paused`、`supply_sites_alert` 配。
   - worker 定时多两项（每小时）：`app.tasks.supply_upkeep.purge_originals`、`expire_sites`，随代码走。
   - 迁移：knowfeed 0020（加表、加列，旧原因句子换成编码，不删行）。
6. **knowbench 删「缺数据的需求」**（knowbench-admin-frontend `540d9f3`）：管理端的 `KNOWFEED_ADMIN_URL` 可删（同第 2c 节第 1 条）。没有迁移。
7. **knowlab 分栏与挑数据**（knowlab-backend `06d15c1`）：
   - 登录回跳 `WEB_AUTH_ALLOWED_RETURN_PATHS` 换成：`dashboard`、`login`、`applications`、`incubation`、`tests`、`delivery`、`review`、`experts`、`knowledge`、`names`，`/zh-CN/…`、`/en/…` 各一份（取代第 2c 节第 2 条那份）。
   - knowlab 的跨应用去处加 knowbase（`domain/prepare.yaml` 的 `target_names` 里 `'knowlab': ['knowbench']` 再加 `'knowbase'`），不然知识库栏「去 knowbase 管理」不显示。
   - worker 定时多一项（每分钟）`app.tasks.knowbot_refresh.sweep`，随代码走。
   - 迁移：knowlab 0022（加一列）。
8. **knowbase web端与管理端**（knowbase-backend `ffad92c`）：
   - 跨应用来源：knowbase 的 `CROSS_APP_SOURCES_JSON` 要认 knowbench、knowlab、knowmart、knowfeed，并给 knowbench、knowlab 配 `return_url`（直达上传传完回去；不配就留在 knowbase）。现在 `domain/prepare.yaml` 的 `cross_app_sources` 只推 knowbench、knowbase、knowfeed 且只有 knowbench 有回跳，要按应用改成可配。
   - 网关：web端新接口 `/api/web/v1/library/*`、管理端 `/api/admin/v1/user-data/*` 要和现有 `/api/web/*`、`/api/admin/*` 一样到后端（按前缀放的话不用改）。
   - 后端镜像多一个依赖 pypdf（`uv.lock` 已锁）。
   - 管理权限：禁用、依法清除要 `knowbase:user-data:dispose`，admin 本来就有，operator 默认没有，不用改。
   - 迁移：knowbase 0020（留痕多认一种，不删行）。
9. **knowbench 跟进与 C4**（knowbench-backend `8433279`、`849bcc8`，应用仓 `f601d36`）：
   - 收 knowfeed 的状态推送：knowbench 的 `service_receivers` 加 `{relation: supply-status, caller: knowfeed}`（`SERVICE_AUTH_SUPPLY_STATUS_*`，scope `knowbench:supply-status`），入口 `POST /api/internal/v1/knowfeed/demand-status` 只认内部地址；收到后在 **api 进程**里马上重解析，要用到 knowbase `user-data-read` 与 knowfeed `supply-demand`（api 进程原本就挂着）。knowfeed 一头的变量见第 5 条。
   - 写产出区：`knowbase:user-data-output` 要挂在 **runner 进程**上（`KNOWBASE_INTERNAL_URL`、`KNOWBASE_USER_DATA_OUTPUT_SERVICE_*`），runner 还要 `KNOWBASE_USER_DATA_READ_SERVICE_*`；另加开关 `WORKBENCH_OUTPUT_WRITE_ENABLED`（默认 `false`，knowbase 认出处依据与回显 `provenance_basis` 的新版上线后再由 Fable 设为 `true`）；没配会合点（`WORKBENCH_RELAY_ADMIN_URL`）和签名私钥也不起这条线。请核现在配的是不是 runner 进程。
   - 迁移：knowbench 0033（加表）、0034（加列，不删行）。
10. **本地 link 0.5.4**（sunmoon-link `35bd113`）：删「本地知识库目录」设置。只改了代码，**要打包、发布**（照 0.5.3 的发布流程）；Windows 托盘设置窗（`native/desktop.ps1`）要在实机上看一眼。新网页在 0.5.3 上照常能用，两边同发最好。
11. **knowfeed 调度、加工、切合**（knowfeed-backend `21a45ea`）：
    - 新出站关系 knowfeed → knowbase `user-data-read`（scope `knowbase:user-data-read`）：knowfeed 一组 `KNOWBASE_USER_DATA_READ_SERVICE_*`；knowbase 的 `SERVICE_AUTH_USER_DATA_READ_CALLERS` 加 knowfeed 及对应 AUDIENCE、SUBJECT_ALLOWLIST、REQUIRED_SCOPE。用来凭加工授权读用户上传的原件；没配就不加工上传资料。
    - 可选变量：`SUPPLY_GLOBAL_RATE_PER_MINUTE`（默认 60）、`SUPPLY_PROCESS_MAX_RUNNING`（默认 2）。
    - worker 定时多两项：`supply-dispatch`（每 5 秒）、`supply-pull-processing`（每分钟），随代码走。
    - 出网：worker 要能到 `irm.cninfo.com.cn`（巨潮互动易，迁移里登记为待审渠道，平台人员在来源目录试采、放行）。
    - 迁移：knowfeed 0021（加表、加列、一条待审渠道，不删行）。

## 二、删除、撤（和 qwen 代码同一次发）

### 3. 删旧版兼容以后（待你决定第 6 条）

1. **沙箱 provisioner（不改会断）**：`components/sandbox-platform/provisioner/config.yaml:8` 的 `knowbase_mcp_url`、`workload.yaml` 与 `workload.yaml.j2` 第 67 行的 `KNOWBASE_MCP_URL` 指着已删的 `/api/mcp/knowledge`，会 404。工作台从 10-18 起不给沙箱 knowbase 令牌，整项撤。
2. **knowbase-backend**：`config.yaml:65-70`、`runtime/workload.yaml:79-84` 的 `KNOWBASE_DATASET_*`、`KNOWBASE_SEMANTIC_*`；`config.yaml:109` service_receivers 里的 `user-data-import`、`workload.yaml:54-60` 的 `SERVICE_AUTH_USER_DATA_IMPORT_*`；`USER_DATA_READER_APPS_JSON` 整条（代码不读）；`config.yaml:92-95` 与 `provider/prepare.yaml:11` 对 knowfeed 桶 datasets 前缀的只读放宽收回到 `knowfeed/original/`，并升 `job_revision`；`samples/register-olist.py` 与 README。
3. **knowlab-backend**：`S3_*`、`STORAGE_BACKEND`、`knowlab-originals` 桶与 `knowlab-backend-s3`（`storage/` 组件）；`KNOWBASE_USER_DATA_IMPORT_SERVICE_*`、`knowbase-user-data-import-service.sops.yaml`、`knowbase-user-data-import-identity/`、`stage.yaml` 两处条件、`config.yaml:75-81` 的 service_client；`SERVICE_AUTH_READ_*`（knowlab 已不收任何服务关系）。Casdoor 应用 `sunmoonai-knowlab-knowbase-user-data-import` 可退。（Settings 是 `extra="ignore"`，变量留着也起得来。）knowlab 应用仓里的 `knowlab-backend/storage-access-bootstrap/` 所有者 10-29 定撤，qwen 在应用仓里删。
4. **knowbench-backend**：`runtime/workload.yaml` 的 `KNOWLAB_READ_SERVICE_*`（`KNOWLAB_INTERNAL_URL` 留着，第 2a 节的 `incubation-request` 要用）、三处 `secretRef: knowbench-knowlab-read-service`；`runtime/knowlab-read-service.sops.yaml`；`knowlab-read-identity/` 与 `config.yaml` 里的身份 `sunmoonai-knowbench-knowlab-read`；knowlab 侧 `SERVICE_AUTH_READ_KNOWBENCH_*`。可选：`KNOWBASE_RETRIEVAL_SERVICE_*`（账 111 说没人用，未核）。
5. **knowfeed-backend**：`config.yaml:41` 的 `KNOWBASE_APP_DATASET_URL` 与第 38 行注释、`runtime/workload.yaml:35`。
6. **平台仓**：`infrastructure/applications/check-browser.py:14` 拿 knowfeed 的 `/api/admin/security-requests` 做管理端只读探测，这个接口已删，要换一个；`scripts/local-integration/dataset-chain/` 整套跑不了了。
7. knowmart 侧不用改。

### 4. 平台测试改在作者账号下以后（待你决定第 8 条第 1 项）

knowbench-backend `config.yaml` 的 `domain_env` 删 `KNOWBOT_TEST_SUBJECT`、`KNOWBOT_TEST_WORKSPACE`、`KNOWBOT_TEST_MONTHLY_LIMIT`（`runtime/workload.yaml` 第 60–62 行同步）。不删也不报错（后端忽略多余变量）。

`KNOWBOT_TEST_ISOLATE` **保持关**：它对所有测试生效，作者的 Windows 电脑上本地 link 不许服务流建、删目录，打开了作者的测试会一开跑就失败。

## 三、改名：测试电脑 → 平台电脑（待你决定第 10 条，decisions 10-29「叫法」）

所有者 10-29 定：集群里那台 Linux 容器不撤，改叫**平台电脑**，配给一位平台人员的账号，一人一台，按名单开。现在只有一台，配在 knowbot-tester 上（knowbot-tester 就是那位平台人员用的账号，显示名不改）。
1. knowbench-backend 的 `test-computer/` 改成平台电脑：目录、`stage.yaml` 的 `knowbench-test-computer`、`config.yaml` 的 `knowbot_test_computer` 改名；从「一台」改成「一份模板 + 名单（账号 → 一台）」，名单里几个开几台，每台各自的持久卷。
2. **现有那台的持久卷要接着用**：配对凭据在卷上（`/data/home`），换了卷就要所有者用 knowbot-tester 重新确认连接码。改名时保住原卷（或迁过去），名单第一项就是它。
3. `agent-releases/config.yaml` 的 `linux` 一节注释改为「平台电脑读它，不给用户下载」。

## 四、发完要看的

- 沙箱起来后不再报 knowbase MCP 404。
- knowlab 自助测试与平台测试都跑到作者的电脑上；作者没有可用电脑时 knowlab 回 409 `author_has_no_computer`。
- knowlab「AI 起草」一轮能到 knowbench（`incubate` 关系通）；作者的 link 旧于 `service-projects-v1` 时这一轮写明原因失败。
- 平台电脑重启后日志里不再出连接码，knowbot-tester「我的电脑」里它仍在线。
- check-browser 的 knowfeed 管理端探测换了新接口后通过。
- knowlab 专家页上能用的那一版有「去 knowbench 请它」链接，点了在新标签页到工作台、钉住并选好这位专家；申请是从 knowbench 找专家来的，直接到当初那个项目的请专家页、问题已填好。
- knowbench 请专家页点「让 AI 找」能跑完一轮（`catalog` 通）；都不合适时点「孵化一个专家」，knowlab「申请」里多一份种类为「问题」的申请（`incubation-request` 通）；点「发布」后 knowmart 需求里能看到（`demand` 通）。

## 五、qwen 随后还要提交、会进同一次发布的

- 第 7 条（10-29 已提交）：knowmart 删「只用自带数据」筛选；资料没了或不再出售时用到它的条目自动下架、原因写在条目上；成交表 `copied`/`copying` 改名 `granted`/`granting`——**多一个 knowmart 迁移 `20261029_0011`**（knowmart 头 `14a0510`）；knowlab 测试数据说明升第 3 版（在旧说明下同意的创意要用户点一次「同意新说明」）、删 `storage-access-bootstrap/`（knowlab 头 `dc9b413`）；knowbase 删 `UserObjects.copy`（`5c14ec7`）；knowfeed `financial_catalog` 清理（`905da53`）。都不要新的平台配置。
- 第 8 条第 4 项不改代码（Windows 上本地 link 本来就给执行端单开临时目录），不涉及 link 发版。
- 孵化第 5 步（10-29 已提交，knowlab 头 `9688dc2`）：迁移 0019（孵化模式、受理类型、给平台的授权表）、0020（运营的提议表）；**已有的名称一律记成作者自己来**，发版后管理端受理栏里原来待受理的会看不到，要平台孵化的由作者点「请平台孵化」。不要新的平台配置。

- AI 请专家（10-29 已提交）：knowmart 后端 `f384353`（应用仓 `b5679a2`）、knowlab `4c94955`（应用仓 `6785ae4`，迁移 0021）、knowbench 后端 `e681d3d`（迁移 0032）与 web端 `0828ce7`；第十三节第 5 条 knowlab web端 `a115f1e`（应用仓 `d034ffb`）、knowbench web端 `4b47bf8`（应用仓 `7b3151c`）。要的平台配置见第 2a、2b 节；孵化契约锁跟着 `reference` 字段更新过，两边同一版。

## 六、Fable 回执第二节的答复（10-29，回执见 [交Fable-gitops-回执](交Fable-gitops-回执.md)）

| 条 | 处理 |
| --- | --- |
| 1 knowfeed 收 `supply-demand` | 已改代码（knowfeed `61d1a03`，应用仓 `569e3f9`）：新 `relation_auth`，读 `SERVICE_AUTH_SUPPLY_DEMAND_CALLERS` 与逐调用方的 `_AUDIENCE`、`_SUBJECT_ALLOWLIST`、`_REQUIRED_SCOPE`（`knowfeed:supply-demand`），只认 knowbench、knowlab，需求单记在校验出的调用方名下。**`SUPPLY_SERVICE_APPS_JSON` 代码不读了，gitops 可以删** |
| 2 knowfeed 调 knowbase | 已改代码（同上）：地址 = `KNOWBASE_INTERNAL_URL` + `/api/internal/v2/user-data`，身份读 `KNOWBASE_USER_DATA_SUPPLY_SERVICE_{CLIENT_ID,CLIENT_SECRET,SCOPE,DISCOVERY_URL,BACKCHANNEL_ENDPOINT}`，缺一项就是没开。**`KNOWBASE_SUPPLY_URL` 代码不读了，gitops 可以删**；入库那份身份（`KNOWBASE_APP_SERVICE_*`）照旧只管入库 |
| 3 `KNOWFEED_INTERNAL_URL` 带前缀 | 已改代码：knowbench `c6c0592`（应用仓 `6b13fed`）、knowlab `4485c7a`（应用仓 `60903bc`）去掉 `BASE`，内部地址后面直接接 `/demands`、`/securities` |
| 4 `user-data-output`、`user-data-directory` 没有调用方 | **留着**：设计里都要用（产出区写入，SDD 0043 第 2.6 节；交付时推专家名录、冻结绑定，SDD 0044 第三节），在这一轮的块 6（测试证据进产出区、交付）里接上，不改名 |
| 5 knowfeed 不要 `user-data-read` | 对，是交接清单列错了：knowfeed 只走 `user-data-supply`，不用加 |
| 6 孵化路由前缀 | 核过：knowbench `interfaces/endpoints/knowbot_runtime_routes.py` 的路由前缀是 `/internal/v1/knowbot-runtime`（挂在 `/api` 下），孵化是 `POST /incubations`、`GET /incubations/{id}`、`POST /incubations/{id}/cancel`，和测试运行同一个前缀，traefik 现在的放行够用 |

