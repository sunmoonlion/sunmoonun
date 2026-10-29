# 交 Fable：随 qwen 这批代码要改的 gitops（10-29）

所有者 10-29：「都按你建议。你写份文档，我让fable现在就做」。本页列出数据第四版、删旧版兼容（decisions ⑰）、平台测试改在作者账号下（⑯）、孵化栏、平台电脑（10-29 叫法）这几批代码要的平台改动。都在 `sunmoonun/gitops`（和一处 `infrastructure/`），qwen 没动。每条的来龙去脉见同目录 [待你决定](待你决定.md) 对应的条号。

## 〇、代码在哪、怎么发

- qwen 的代码只在本地提交，没推。都在本地 `~/worktrees/qwen/<仓>` 的 `qwen` 分支上，各仓都已包含当时的 `origin/fable`，合进 fable 应该是快进或干净合并（合前照规矩先试合并）：

  | 仓 | qwen 头 | 比 origin/fable 多 |
  | --- | --- | --- |
  | knowbase-app | `5c14ec7` | 20 |
  | knowbench-app | `6b13fed` | 9 |
  | knowfeed-app | `569e3f9` | 8 |
  | knowlab-app | `9688dc2` | 16 |
  | knowmart-app | `14a0510` | 5 |
  | sunmoonun | 见 `git log origin/fable..qwen` | 只有文档 |

  这之后 qwen 还会接着提交（第 7 条的几处小改、孵化第 5 步），合之前看一眼各仓 `qwen` 头。
- **新增类**（第一节）不影响现在跑着的旧代码，可以先上。
- **删除类**（第二节）必须和 qwen 的代码同一次发布：旧代码还在读这些变量、用这些身份，先删会断。
- **迁移会删生产记录**（所有者已同意，decisions ⑰）：knowmart 0010（0011 只改名、加列，不删行）、knowlab 0016–0018（0019、0020 只加列、加表，不删行）、knowbench 0030–0031、knowfeed 0019、knowbase 0018。knowfeed 0019 会删关注清单那 10 行与流水，所有者 10-29 定不导出（名单还在历史迁移 0013 的代码里）。

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

## 二、删除、撤（和 qwen 代码同一次发）

### 3. 删旧版兼容以后（待你决定第 6 条）

1. **沙箱 provisioner（不改会断）**：`components/sandbox-platform/provisioner/config.yaml:8` 的 `knowbase_mcp_url`、`workload.yaml` 与 `workload.yaml.j2` 第 67 行的 `KNOWBASE_MCP_URL` 指着已删的 `/api/mcp/knowledge`，会 404。工作台从 10-18 起不给沙箱 knowbase 令牌，整项撤。
2. **knowbase-backend**：`config.yaml:65-70`、`runtime/workload.yaml:79-84` 的 `KNOWBASE_DATASET_*`、`KNOWBASE_SEMANTIC_*`；`config.yaml:109` service_receivers 里的 `user-data-import`、`workload.yaml:54-60` 的 `SERVICE_AUTH_USER_DATA_IMPORT_*`；`USER_DATA_READER_APPS_JSON` 整条（代码不读）；`config.yaml:92-95` 与 `provider/prepare.yaml:11` 对 knowfeed 桶 datasets 前缀的只读放宽收回到 `knowfeed/original/`，并升 `job_revision`；`samples/register-olist.py` 与 README。
3. **knowlab-backend**：`S3_*`、`STORAGE_BACKEND`、`knowlab-originals` 桶与 `knowlab-backend-s3`（`storage/` 组件）；`KNOWBASE_USER_DATA_IMPORT_SERVICE_*`、`knowbase-user-data-import-service.sops.yaml`、`knowbase-user-data-import-identity/`、`stage.yaml` 两处条件、`config.yaml:75-81` 的 service_client；`SERVICE_AUTH_READ_*`（knowlab 已不收任何服务关系）。Casdoor 应用 `sunmoonai-knowlab-knowbase-user-data-import` 可退。（Settings 是 `extra="ignore"`，变量留着也起得来。）knowlab 应用仓里的 `knowlab-backend/storage-access-bootstrap/` 所有者 10-29 定撤，qwen 在应用仓里删。
4. **knowbench-backend**：`runtime/workload.yaml` 的 `KNOWLAB_INTERNAL_URL`、`KNOWLAB_READ_SERVICE_*`、三处 `secretRef: knowbench-knowlab-read-service`；`runtime/knowlab-read-service.sops.yaml`；`knowlab-read-identity/` 与 `config.yaml` 里的身份 `sunmoonai-knowbench-knowlab-read`；knowlab 侧 `SERVICE_AUTH_READ_KNOWBENCH_*`。可选：`KNOWBASE_RETRIEVAL_SERVICE_*`（账 111 说没人用，未核）。
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

## 五、qwen 随后还要提交、会进同一次发布的

- 第 7 条（10-29 已提交）：knowmart 删「只用自带数据」筛选；资料没了或不再出售时用到它的条目自动下架、原因写在条目上；成交表 `copied`/`copying` 改名 `granted`/`granting`——**多一个 knowmart 迁移 `20261029_0011`**（knowmart 头 `14a0510`）；knowlab 测试数据说明升第 3 版（在旧说明下同意的创意要用户点一次「同意新说明」）、删 `storage-access-bootstrap/`（knowlab 头 `dc9b413`）；knowbase 删 `UserObjects.copy`（`5c14ec7`）；knowfeed `financial_catalog` 清理（`905da53`）。都不要新的平台配置。
- 第 8 条第 4 项不改代码（Windows 上本地 link 本来就给执行端单开临时目录），不涉及 link 发版。
- 孵化第 5 步（10-29 已提交，knowlab 头 `9688dc2`）：迁移 0019（孵化模式、受理类型、给平台的授权表）、0020（运营的提议表）；**已有的名称一律记成作者自己来**，发版后管理端受理栏里原来待受理的会看不到，要平台孵化的由作者点「请平台孵化」。不要新的平台配置。

## 六、Fable 回执第二节的答复（10-29，回执见 [交Fable-gitops-回执](交Fable-gitops-回执.md)）

| 条 | 处理 |
| --- | --- |
| 1 knowfeed 收 `supply-demand` | 已改代码（knowfeed `61d1a03`，应用仓 `569e3f9`）：新 `relation_auth`，读 `SERVICE_AUTH_SUPPLY_DEMAND_CALLERS` 与逐调用方的 `_AUDIENCE`、`_SUBJECT_ALLOWLIST`、`_REQUIRED_SCOPE`（`knowfeed:supply-demand`），只认 knowbench、knowlab，需求单记在校验出的调用方名下。**`SUPPLY_SERVICE_APPS_JSON` 代码不读了，gitops 可以删** |
| 2 knowfeed 调 knowbase | 已改代码（同上）：地址 = `KNOWBASE_INTERNAL_URL` + `/api/internal/v2/user-data`，身份读 `KNOWBASE_USER_DATA_SUPPLY_SERVICE_{CLIENT_ID,CLIENT_SECRET,SCOPE,DISCOVERY_URL,BACKCHANNEL_ENDPOINT}`，缺一项就是没开。**`KNOWBASE_SUPPLY_URL` 代码不读了，gitops 可以删**；入库那份身份（`KNOWBASE_APP_SERVICE_*`）照旧只管入库 |
| 3 `KNOWFEED_INTERNAL_URL` 带前缀 | 已改代码：knowbench `c6c0592`（应用仓 `6b13fed`）、knowlab `4485c7a`（应用仓 `60903bc`）去掉 `BASE`，内部地址后面直接接 `/demands`、`/securities` |
| 4 `user-data-output`、`user-data-directory` 没有调用方 | **留着**：设计里都要用（产出区写入，SDD 0043 第 2.6 节；交付时推专家名录、冻结绑定，SDD 0044 第三节），在这一轮的块 6（测试证据进产出区、交付）里接上，不改名 |
| 5 knowfeed 不要 `user-data-read` | 对，是交接清单列错了：knowfeed 只走 `user-data-supply`，不用加 |
| 6 孵化路由前缀 | 核过：knowbench `interfaces/endpoints/knowbot_runtime_routes.py` 的路由前缀是 `/internal/v1/knowbot-runtime`（挂在 `/api` 下），孵化是 `POST /incubations`、`GET /incubations/{id}`、`POST /incubations/{id}/cancel`，和测试运行同一个前缀，traefik 现在的放行够用 |

