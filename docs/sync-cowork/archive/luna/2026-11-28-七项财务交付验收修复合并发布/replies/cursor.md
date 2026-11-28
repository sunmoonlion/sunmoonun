# Cursor 发布回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 结论：现场已晋级到候选十八组件；Jenkins 账面 #136 为 FAILURE（第 11 阶段 KnowBase 域集成），根因已修并完成六应用 `application-check` 补跑；Git 晋级提交与标签已补推。
- Luna 首轮现场验收（`replies/luna.md`，2026-11-28）：18 组件源码/镜像、31 角色、六库 head、12 登录页 200、七项财务合成 138/138 与跨镜像 0.99/1 探针均通过；卡仍开放，待登录后业务链路、M02 普通委托及其余编号证据。

## 发布结果

- Jenkins：https://jenkins.dev.sunmoonai.com:30443/job/release/136/  
  官方结果 **FAILURE**（2553 s）。描述：后半段停下——集群可能已是新版而 Git 还没推；提交曾留在代理克隆 `abandoned/release-136`。
- 分支 `luna-release-587`，候选平台钉 `c22be711ddb283227dcc5ca61ba047924ae4c283`，`PIN=keep`，APPS=`tpl knowfeed knowbase knowbench knowlab knowmart`。
- 部署提交 `dc6eb7cecdff21a507ff34f7de3cc40d7d07b465`。  
  晋级指针提交 `c93e7c204d777f139003ef26c8fdc5935f863ab5`。  
  校验修复提交 `0b8b2b185`（KnowFeed 投递验收改用 `ServiceTokenProvider`）。  
  标签 `release-20261128-2`（已推 origin；mirror 尽力推送）。
- GitOps / Flux：`oci://harbor.sunmoonai.com:30443/platform/deployments-kind`  
  digest `sha256:23f213da2bf5a9737f6c595d42a5082411b3838f69ac792832658433b4f3077f`  
  revision `dc6eb7cecdff21a507ff34f7de3cc40d7d07b465`  
  现场 OCIRepository `platform` 已钉该 digest。
- 批准：admin @ 2026-11-28T20:15:00+08:00。

## 失败与补救

1. 第 10 阶段 Flux apply / wait 成功；tpl、knowfeed 的 application-check 通过。
2. knowbase 域集成失败：`provider/verify-info-http.py` 仍 `import get_knowbase_app_client`，而 KnowFeed 钉 `cf0d52d64`（含 `d1a10a5`）已删除该包装（封闭退役分发链路）。私密证据：`ImportError` / `error_class=ImportError`。
3. 补救：将验收改为同仓仍保留的 `ServiceTokenProvider` + `knowbase_app_ingest_url`（投递 URL 现场仍启用）。提交 `0b8b2b185`。
4. 补跑 `application-check`（工作树对齐现网 digest）：knowbase / knowbench / knowlab / knowmart 均 `failed=0`。knowbase 域断言 `passed: true`。

## 十八组件源码与镜像

与候选 `sources.yaml` / 构建锁一致；后端现网抽验：

| 组件 | 源码钉（短） | 镜像 digest |
| --- | --- | --- |
| tpl-backend | `65db1cd6f` | `sha256:3d3e571b87e2726b26587fdaa6440c69814f2221d9316696c7208e85292d9665` |
| tpl-web | `d87b31669` | `sha256:f043a3b1f828995536742cdd8fe6c68587787894d4c80599cbef9538ccfeef44` |
| tpl-admin | `849805014` | `sha256:d46c500549e7e9bf037ccdf13c98909fa41e1d8ff1e2efa414c4eff62eba78b0` |
| knowfeed-backend | `cf0d52d64` | `sha256:a1d7cb5b7506b335fcb7bd44c37232399d041891aad9724ec6f15eb9fd729b0b` |
| knowfeed-web | `188010e23` | `sha256:d2aa5999d75e7f0b87b0b2c6c840debe3d70da2fac520283606baba5f2ac8e20` |
| knowfeed-admin | `51cb6030c` | `sha256:1feb3531e35394f902d72b0e1c99ec301f8e58715d436b8ce5a45912ffdeb52c` |
| knowbase-backend | `288dc831b` | `sha256:3f8d581373d454dd164b0ef62101450263315597f87ee91468dcc4db7340f8f9` |
| knowbase-web | `e10d22628` | `sha256:ee7787f25f1acf986acb5ef16d60c753e88457b1437d73c581e8bd8ddfa103c9` |
| knowbase-admin | `da9d62cd2` | `sha256:4b1db137a4ba3af247a6d1c01102f8dbce1f9d2d9da09fc8c0e210edb867f545` |
| knowbench-backend | `17021f8e7` | `sha256:ccee0b0c43c8190de48ba284e6903d043fbbbbe33790e082f79ab565a6b9857c` |
| knowbench-web | `f8f25b461` | `sha256:f12f7061824621a9a0cb6442e7b2fdb8ca29443d2b3ed8d296f9c7ffc33d4b9a` |
| knowbench-admin | `75085a8e6` | `sha256:9fdeda7072c3729bd62e0ba9e15d3ae80df21c57005cfc873aaf21d002a3140f` |
| knowlab-backend | `10a173a26` | `sha256:dbd5eadfddd93a2c57ac976d256ad9935377525a6ab039f65f85914bd513113d` |
| knowlab-web | `7a1e043fc` | `sha256:b84e5e90729b6179a96f5fa23502de15b2c34c61bc2db143d6edae6192757c8a` |
| knowlab-admin | `ec6b2e135` | `sha256:d0fc0fb29a1376a6dbbca2f3a37191cb812dc9d4c170c7354b171472e27e5512` |
| knowmart-backend | `8d3e97a0e` | `sha256:f352e5d0eeeb9244e030312ca12b9c60425453cb6f6e43956f5e900c31552545` |
| knowmart-web | `631aad605` | `sha256:27d074ccd7e1c018fe8084467509593ccb8135d2b221da78f60e249dce1fd52c` |
| knowmart-admin | `52322c426` | `sha256:a2079f1e6999edb5239cd1ce0367fc87b0f3f03c4c5951dc6f7fa0d10cbdb1dc` |

完整父子仓 SHA 见候选 `infrastructure/applications/sources.yaml` 与构建产物 `infrastructure/.build/release/136/3-image-locks.txt`。

## 数据库目标 head（配置 / 检查口径）

| 库 | 目标 head |
| --- | --- |
| tpl | `20261025_0004` |
| knowfeed | `20261128_0027` |
| knowbase | `20261128_0027` |
| knowbench | `20261128_0073` |
| knowlab | `20261128_0033` |
| knowmart | `20261128_0025` |

迁移 Job 已随各应用 kustomization Ready；application-check 含 schema 验收。沙箱 / 供给器本轮未重建（仍为既有锁）。

## 角色就绪

第 10 阶段 wait：六应用相关 kustomization 均 condition met（含 migration / runtime / web / admin / identity 等）。六后端 API Deployment 镜像摘要与上表一致。

## 与候选的差异

- 官方流水线未写出 SUCCESS 回执文件；以本卡回执 + 补推 Git（`0b8b2b185`）为准。
- 平台 gitops 校验脚本相对候选构建点多了投递验收修复提交；应用十八组件源码钉未变。

## Luna 首轮验收对照

已读 `replies/luna.md`：与本回执 Flux digest `sha256:23f213da…` / revision `dc6eb7ce…`、十八组件钉及角色就绪一致；财务合成与跨镜像探针由 Luna 现场跑通。本侧无新部署动作。

## 开放项（Luna）

1. 登录后六应用业务链路、KnowLab M02 普通委托、其余台账编号逐号证据（卡保持开放）。  
2. 结案归档仍待上述业务验收完成。

## Harbor 清理（已执行）

- 范围：仅 18 个应用组件仓；不动基础设施 / sandbox / `deployments-kind` OCI。
- 保留：现场集群引用 ∪ #135 gitops ∪ #136 gitops（应用组件 40 个 digest，删后抽验均仍在）。
- 删除：361 个未保留制品（清单口径约 35.8 GiB）；失败 0。清单与结果见 `harbor-delete-manifest-136.json`、`harbor-delete-result-136.json`。
- GC：已触发 Manual（job 以现场为准）；构建缓存此前已清零（`buildx prune --all`，41.51 GiB）。
