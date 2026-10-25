# fable-0042-平台-2/3/4 回执：knowbase 用户资料的平台配置与四条服务关系、会合点与测试电脑两处配置、本地 link 0.5.2 出包上传、发版卡（Fable 经隧道在本地做）

WS=fable，分支 fable。提交：`7ead9067`（第 2、3 步）、`84cd544d`（第 4 步）、`24bdaef2`（发版卡）、`b1407722`（断言补齐）。第 1 步见 `fable-0042-platform-1.20261025-1300.md`。本页没有口令、令牌、密文。

## 一、第 2 步：knowbase 用户资料（SDD 0042）要的平台配置

对着 Opus 代码核出的三处契约缺口（写在本地 `~/平台配置-给Opus的接口清单-20261025.md`，要 Opus 改代码）之外，平台这边补了四件 Opus 的发版清单里没有的：

| 缺口 | 平台的改法 |
| --- | --- |
| 关系名带连字符（`user-data-read`），通用服务身份机制只认 `^[a-z][a-z0-9]{1,15}$`，环境变量名也会带着连字符 | `service-client/prepare.yaml` 关系名放宽到 `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`（≤32）；`runtime/workload.yaml.j2`、运行时 Secret 的键统一 `upper` 后 `-`→`_`，与应用侧 `service_client.py` 的 `_key` 一致 |
| 一个应用对同一目标有两条关系时 `<目标>_INTERNAL_URL` 会写两遍（knowlab → knowbase） | 一个目标只写一次；目标是共用证书上的 knowbase（没有自己的 `service_access_routes`）时用 `service_access_hosts` 的主机名；`ALLOWED_HOSTS` 同理并去重 |
| 集群内到 knowbase 的入口只放行 `/api/internal/v1/knowledge`，用户资料接口 `/api/internal/v1/user-data` 路由不到 | `traefik/service-access` 的 knowbase-tls 加第二个前缀 |
| knowbase 的 `S3_*` 被知识源只读身份占着，自己的桶没地方放；三处断言禁止并存 | `storage` 机制加 `object_storage.env_prefix`（knowbase 用 `USER_DATA_`，变量与 Secret 键带前缀，不再要求 `STORAGE_BACKEND`）；`common/backend/prepare.yaml`、knowbase `provider/prepare.yaml`、`applications/deploy.yaml`、`verify.yaml` 四处断言改成「带前缀才许并存」 |

配置：knowbase `object_storage {knowbase_storage, knowbase-originals, v1, env_prefix USER_DATA_}` 与新阶段 `knowbase-storage`；`service_receivers` 四条（read←knowbench、grant-test←knowlab、import←knowlab、purchase←knowmart）；`domain_env` 的 `USER_TOKEN_AUDIENCE`、`USER_TOKEN_APPS_JSON`、`USER_DATA_BUCKET`、`USER_DATA_PREFIX`、`USER_DATA_READER_APPS_JSON`。knowbench `service_clients` 加 knowbase/user-data-read（api、worker、runner）；knowlab 加 user-data-grant-test（api、worker）、user-data-import（api）；knowmart 加 user-data-purchase，`PUBLIC_MARKET_ENABLED=true`（开发站点先开，待所有者确认）、`PUBLISHER_ID_HASH_KEY` 随机进 SOPS、跨应用链接表加 knowlab；三家 `KNOWBASE_USER_AUDIENCE`。四个 `stage.yaml` 加身份阶段与运行时依赖、资源。

## 二、第 3 步：会合点与测试电脑

relay `RELAY_MAX_SERVICE_STREAMS_PER_USER=6`（原镜像默认 2，评审 P2-13）；test-computer `TMPDIR=<工作区>/runs/.tmp`，启动时建、7 天兜底清理跳过它（P2-14）。

## 三、暂存与核对

- 跑的顺序与撞上的：第一次六个对象全停在阶段图检查（新阶段目录要先存在）→ 建目录；第二次四个停在「未选中的阶段声明不一致」（改了 stage.yaml 要先 `topology-stage OBJECT=all`）、knowbase 停在并存断言、knowmart 停在跨应用链接表没有 knowlab、traefik 的对象名应是 `ingress-platform/traefik`；逐一改后 topology + traefik + relay + knowbench + knowlab + knowmart 过；knowbase 又停在 provider 的断言与 `ALLOWED_HOSTS` 的 `service_access_routes[knowbase]`，改后过。knowfeed、tpl 再暂存零差异（共用模板改动对它们字节不变）。
- 产物核对：knowbase 运行时多 `USER_DATA_S3_*`、`USER_TOKEN_*`、`USER_DATA_*`、四条 `SERVICE_AUTH_USER_DATA_*_CALLERS` 及各调用方一组；三家各多 `KNOWBASE_INTERNAL_URL`（一次）、`KNOWBASE_USER_DATA_<关系>_SERVICE_*`、`KNOWBASE_USER_AUDIENCE`；knowmart 多 `PUBLIC_MARKET_ENABLED`、`CROSS_APP_TARGETS_JSON` 含 knowlab、出站策略加 worker；拓扑多 5 个阶段；入口多一条路径；relay 多一个环境变量；test-computer 的 TMPDIR 与脚本。
- sops：新建 6 个密文（4 条关系的客户端秘密、knowbase 的 `USER_DATA_S3_*` 身份、knowmart 的 `PUBLISHER_ID_HASH_KEY`），已有 sops 文件没有明文变化（解密 sha256 对比）；gitops 里没有 PRIVATE KEY 字样。
- render-check：第 1 步推送后 #336 SUCCESS、diff 0 行；第 2–4 步推送后 #338、#339 FAILURE——`applications/deploy.yaml`、`verify.yaml` 自己那份并存断言没跟着改（我漏的），`b1407722` 补齐、本地 `application-deployment-plan APP=knowbase` 过；`b1407722` 推送后 **render-check #340 SUCCESS、diff.txt 0 行**：committed 的 gitops 与整树重新渲染逐字节一致。

## 四、第 4 步：本地 link 0.5.2（sunmoon-link `4f36a06`）

| 包 | 做法 | 结果 |
| --- | --- | --- |
| Windows | 第一次用 Opus 账 128 的一条命令 `release-windows.mjs`（WSL 上跑，用 Windows 官方 node.exe 24.19.0，自检复制到 Windows 临时目录）：`git archive` → pnpm 10.24.0 冻结安装 win32/x64 → 组包 → 编码探针（ps1 2、ascii 5、parsed 2）→ 包内 node.exe 自检 pass → 确定性 zip → 回执 | 110 个文件；zip `10bca1dc…`、180989843 字节；manifest `eef0b3d6…`；40 秒 |
| Linux | `build-linux.mjs`，站点 edge-public（新域名）；`verify-linux` | 134 个文件；tarball `1dbce103…`、139189087 字节；manifest `464d138d…`；verified |
| 上传 | `agent-release-verify/upload`、`linux-verify/upload` 四个都 0 | 两份 uploaded、readback_verified、writer_read_denied、reader_write_denied；私有目录两份新回执；旧对象不动 |
| 配置 | knowbench `agent-releases/config.yaml` Windows、Linux 各 6 行；platform-stage 后 `agent-releases.sops.yaml` 明文只变 `WORKBENCH_AGENT_DOWNLOAD`，test-computer 下载脚本换到 0.5.2 | 装了 0.5.1 的电脑装 0.5.2 走升级，配对保留 |

## 五、发版卡

`docs/ops/发版卡-0042批次.md`（`24bdaef2`）：前提清单、四个库期望版本号与钉同一提交（值已算好：knowbase `20261023_0008`、knowbench `20261023_0025`、knowlab `20261024_0012`、knowmart `20261024_0008`）、knowlab 备份命令（Secret 键与 pg_dump 18.6 已核）、分五次人批各看什么、发完要做的、回退、发版期间不做的。

## 六、留下的

- 等 Opus：三处代码改动；knowfeed 完善；合并对齐。然后按发版卡发。
- 要所有者定：knowmart `PUBLIC_MARKET_ENABLED` 开发站点开着对不对。
- 我漏的两处记进教训：改 `stage.yaml` 要先建目录、先 `topology-stage OBJECT=all`；共用模板的断言在 `applications/deploy.yaml`、`verify.yaml` 还有副本。
