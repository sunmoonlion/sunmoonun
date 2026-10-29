# 数据第四版 gitops 第一、三节发布（release #30）回执 — Fable，2026-10-29 12:07

依据：`docs/总纲/数据拓扑重构/交Fable-gitops.md`（Opus 10-29）第一节（新增）、第三节（平台电脑）；所有者 10-29「发版」。发布回执在同目录 `release-30.20261029-120520.md`（流水线生成）。

## 发了什么

| 提交 | 内容 |
| --- | --- |
| 204daab3 | knowbase 收 user-data-read(+knowlab)/directory/output/supply；knowbench 出 user-data-output、knowfeed:supply-demand，收 incubate；knowlab 出五条；knowfeed 出 user-data-supply、收 supply-demand；traefik knowfeed 入口 + knowbase v2 前缀；test-computer → platform-computer（名单制，第一台沿用原卷） |
| 0a7e811f | 平台电脑模板换行小修 |
| de22b6c4 | 手工 stage：traefik service-access、整张阶段图（九个新阶段） |
| c6ee5c83 | 撤 knowfeed 的 KNOWBASE_SUPPLY_URL、SUPPLY_SERVICE_APPS_JSON（Opus 答复后代码不读） |
| 71891c32 / 6eff0fb8 / 7a2d0252 | 流水线：deploy、晋级、回执 |

render-check #817、#819 SUCCESS。release #30：排队 10 分钟（render-check #821 占执行位），1–7 阶段约 17 分钟，人批 6 秒，10 部署 913 秒，11 检查 369 秒，12 推送 7 秒，SUCCESS。

## 发完核到的

- 九个身份申领 Job 全部 Complete（各 5 秒）；18 个新 Secret（provision + service 各九）在位。
- knowfeed 内部入口：Ingress `knowfeed-service-access`（host knowfeed-tls，路径 /api/internal/v1/supply）、Secret `service-access-knowfeed-tls`、Service `knowfeed-tls` 都在；knowbase 入口三个前缀（v1 knowledge、v1 user-data、v2 user-data）。
- 平台电脑 `knowbench-platform-computer-knowbot-tester` 1/1 Running（03:59 起稳定），挂的卷是原来的 `knowbench-test-computer`，最近 15 分钟日志里没有连接码，会合点上该账号只剩一份连接。
- 五个 application-check 由流水线第 11 阶段跑过（SUCCESS）。
- 前端 Pod 的重启计数（非本次造成，附带记录）：knowbase-admin-5bcc9f8dfb-rrnmn                                   6     2026-10-26T01:25:16Z;knowbase-web-748c5486cc-8z5xb                                     6     2026-10-26T01:25:16Z;knowbench-admin-5f5bc8fb69-l5cmb                                  6     2026-10-26T01:25:16Z;knowbench-web-fbdd89c5f-hs9hx                                     1     2026-10-26T01:25:16Z;knowfeed-admin-664ddc5744-vmz95                                   6     2026-10-26T01:25:16Z;knowfeed-web-6fb7f68f87-jjnpv                                     6     2026-10-26T01:25:16Z;knowlab-admin-7dd7b964c5-skzvn                                    1     2026-10-26T01:25:15Z;knowlab-web-5447d49696-wxtwm                                      1     2026-10-26T01:25:15Z;knowmart-admin-9cbf57fff-r4rgt                                    1     2026-10-26T01:25:15Z;knowmart-web-d56bdc65f-46dkp                                      1     2026-10-26T01:25:16Z;tpl-admin-7bb84f854b-7rgct                                        1     2026-10-26T01:25:16Z;tpl-web-c895bb65b-7889r                                           1     2026-10-26T01:25:15Z;

## 两次现场处理（都在第 10 阶段）

1. **旧测试电脑被 Flux 拉回来**：发版前我先 `suspend` 旧阶段 `knowbench-test-computer`、再删 Deployment 等四个对象，但一次正在进行的调和把四个对象又建了回来，于是新旧两个 Pod 挂同一个 RWO 卷、用同一个账号连会合点，互相踢（relay 日志 `agent replaced` 12 次，新 Pod 以退出码 3 重启 6 次）。处理：删旧 Deployment、ReplicaSet、Pod 与三个附属对象，PVC 照留。此后稳定。
2. **第 10 阶段等一个已不存在的阶段**：发版脚本按名字前缀等所有 `knowbench-*` Flux 阶段 Ready，旧阶段对象还在（源里已无该目录，永远不 Ready）。删掉后 `kubectl wait` 已在盯着它，于是临时建了一个同名、同 spec（指向 platform-computer 目录、prune false、Orphan）的阶段让它 Ready，第 10 阶段随即过；发布结束后已删（Orphan，不动对象）。

**教训**（已写进平台电脑 README 的做法要改）：删一个被 Flux 管着的阶段，顺序必须是 **先删 Flux Kustomization 对象（Orphan），再删它管的对象**；或者改在晋级之后删。suspend 挡不住正在进行的那一次调和。

## 未做 / 后续

- 交接第二节（删除类）在本地分支 `fable-v4-deletions`，等 qwen 代码合进 fable 后一起发；那次还要手工 stage provisioner、traefik 与阶段图。
- `user-data-output`、`user-data-directory` 的身份已建、代码这一轮块 6 再接（Opus 10-29 答复）。
