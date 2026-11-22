# Cursor 回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 实际检查版本：sunmoon-kind 发布 #103、#104。#103 部署 `b7aaac96665a977ebca2e770b406e3621acea029`，指针 `fc993563f81015e7abb258ab2b5babee86462d31`，tag `release-20261122-1`，回执 `19a9d40262fa7101486ad3a7fd687891cc0e6c06`。#104 部署 `9b295a73c5c3f94c5dee75fb532d9f6b04c8d17f`，指针 `6d7e00d9452fad33c5a997890c6fa92de1e07f68`，tag `release-20261122-2`，回执 `c4dc38fdfbfba3336f6f5daf13c1629d491354fd`。
- 结论：部分完成。两波镜像、库版本和 KnowMart 新接口的服务身份边界已在 sunmoon-kind 落地。原 KnowBench 候选 `332bfea` 没有构建。资格、试跑、冻结、回收、计费和空页现场路径没有测试账号与模型预算，未跑。第 12 项和 P3–P5 仍暂停。

## 发现

- F01：#101 在人工批准前失败。共享仓库当时停在 `13e7ff5e5`，契约脚本不在那棵树上。没有部署。
- F02：#102 在把 KnowMart 后端转成 OCI 包时失败。固定 skopeo 镜像 `sha256:9182497536bb5485b4f0bdbad5dbab24cd0df7259c33005a1e732a34f5d78a99` 已不在本机。已按宿主归档锁装回同一摘要，#103 用该镜像完成转换。
- F03：#103 的迁移作业第一次拉镜像失败。三个 kind 节点把 `harbor.sunmoonai.com` 解析到自身 `127.0.0.1:30443`，证书是 Traefik 默认证书。已在三个正在运行的节点 `/etc/hosts` 写入 `172.18.0.1 harbor.sunmoonai.com`，经网关能拿到 Harbor 证书。失败的一次性作业由 Flux 重建后完成。这三行写在运行中的节点里，节点容器重建后会丢失；节点重建路径尚未改为持久解析到网关。
- F04：发布前没有单独冻结新派发，也没有清点在途 Attempt。未决审批、已启动脚本和未知收费回执没有单独对账。脚本、写盘和固定计划开关保持关闭。
- F05：买方非空窗口、同一版本的作者／已购／未购用户，以及空页续查的现场点击，本次没有测试账号和模型预算，未跑。KnowBench summon 身份对探测主体 `release-probe` 返回空窗口。

## 发布

环境：sunmoon-kind。应用命名空间 `app-platform-dev`，沙箱命名空间 `sandbox-platform-dev`。

#103 批准人 admin，2026-11-22T08:47:48+08:00。任务 https://jenkins.dev.sunmoonai.com:30443/job/release/103/ 。部署 OCI `sha256:1ac80486f8f9ee029a876a779693d22c811678e0e1b202302f94703f8797827b`。

| 对象 | 父仓 / 子仓 | 镜像 |
| --- | --- | --- |
| KnowMart 后端 | `1802cd5a610495531aa80d41604e0d4489ba2f5f` / `7e07c84cda06c0ba4fd0030f16359d61b903a5fd` | `sha256:52ac2932b03a71f61047d889b2aa78e500499a67da014b0c10c33256d3ba7ae1` |
| KnowMart Web / 管理 Web | `14515db89f249d76ea67f83b746fed030ccdf7f0` / `5f109118ffbaca623a732ed33eaea61a2905241a` | `sha256:7b98f0222ff7ac252e528684cb0bbd6dc42f6baa31a2f40c5efc5cc23880b463`、`sha256:0799a9cab79a252ff5f1f30a294c010ad47e8417f15c04be96d8ca08169128ec` |

库版本：`knowmart-migrate-52ac2932b03a-v4` 完成。流水线按源码链核对为 `20261122_0018`。发布前现网是 `20261120_0017`。

#104 批准人 admin，2026-11-22T09:17:40+08:00。任务 https://jenkins.dev.sunmoonai.com:30443/job/release/104/ 。部署 OCI `sha256:acbd31f0cf0202c0acaeb920ae1737ac987d9239ea0c8286e20c2b5ff6a9e4f7`。发布分支在排队时为 `e9139e853`，其中只把 KnowBench 预期库版本改为 `20261121_0055`。

| 对象 | 父仓 / 子仓 | 镜像 |
| --- | --- | --- |
| KnowBench 后端 API / runner | `2a6a1a93d3b650392332fa01968da3d530ccdceb` / `701a82bf3cb5e9eae6b43510a2dff04c398a8d4b` | `sha256:c26733cb0b83452a3092c9689cf15f0b1c91c59efd2c7600a3169c20ab205a8d` |
| KnowBench Web / 管理 Web | `d2e9e2d15dbdb21e7d08cae67229d16028452470` / `33559e926c3ebb7570716d5bb318b5a014e0d645` | `sha256:9a10c9e397dcddec565cc31e8a625ce9c7310e1f7ea4e7a9721616d1707bf9df`、`sha256:223a35f3035ef71cd66541ecc63f002f00e3015e4a0b790f39f074f44c52db5e` |
| KnowLab 后端 / 作者 Web | `da2259f3acca69b101327a5e89b7f720428b0d9a` / `efa6aa6f7ef7c3ed4aedd9c873b4affd83b0c23a`、`d373a3f556343b52940d3423640c16e87012ebdf` | `sha256:b2e80c4e201569464f5c6b0c0db9b56b9952f292f96380715c2181f65495c693`、`sha256:bf919fccdced984d1fed4d741611f5d9297cf75e9af354bc7faefd2e36140675` |
| KnowLab 管理 Web | `89fe3ac1f6178018186584db7542f11102896381` | `sha256:f1bcd03485246b1587636f74b98b7d1daff01f7ff20d73d661eef4c42f236d92` |
| 供给器 / 沙箱 | `99f497bf79946d9618533228640423e10143c460` | `sha256:af0ba76f18e3c6341d4c0323b6ab5e97ce856f65be18452a9cd5db2545db38e4`、`sha256:c886456b1aed9cd50f161baaf9675be8d228431bde3fba5050bbe662d544489b` |

`332bfea`、`3626d568`、`7cf24afc` 没有进入构建，也没有对应镜像。API 与工作台 Web 是上表这一对。

协议检查：knowbench ok=50 failed=0，knowlab ok=45 failed=0，sandbox ok=23 failed=0。证据在 `infrastructure/.build/release/104/11-check-*.log`。

库版本：`knowbench-migrate-c26733cb0b83-v12` 完成，流水线按源码链核对为 `20261121_0055`。发布前现网是 `20261121_0054`。`knowlab-migrate-b2e80c4e2015-v5` 完成，预期仍是 `20261120_0029`。

现网 `knowbench-runtime`：`WORKBENCH_SKILL_SCRIPTS_ENABLED=false`，`WORKBENCH_FIXED_AS_PLAN_OWNERS=[]`，`WORKBENCH_OUTPUT_WRITE_ENABLED=false`。

## KnowMart 接口

从现网 KnowBench API 进程调用 `POST /api/internal/v1/knowmart/formal-methods/planning-window`，主体 `release-probe`，`offset=0`，`limit=1`。没有打印令牌。

| 身份 | 结果 |
| --- | --- |
| KnowBench summon | 200，`references` 长度 0，`more=false`，主体原样返回 |
| 无令牌 | 401 `auth_required` |
| 伪造令牌 | 401 `token_invalid` |
| KnowBench catalog | 401 `audience_mismatch` |

后三种没有进入查询。非空买方窗口、精确核权与未购用户的差异没有现场样本，未跑。

## 沙箱

供给器已使用沙箱镜像 `sha256:c886456b1aed9cd50f161baaf9675be8d228431bde3fba5050bbe662d544489b`。七个既有用户沙箱换成该镜像，Codex 仍是 `codex-cli 0.170.0`。七个 `*-codex-home` 卷保持 Bound，部署没有删除。

换镜像前后，七个沙箱的配置段都是 `model_providers.kimi`、`features`、`windows`、`mcp_servers.sunmoon_workbench`。没有 `sunmoon_knowbase` 或 `sunmoon_knowledge`。

## I01–I11

| 项 | 本次发布证据 | 未验 |
| --- | --- | --- |
| I01 | #104 第一阶段镜像钉和第二阶段 `--pinned` 契约核对通过。供给器与沙箱修订均为 `99f497bf79946d9618533228640423e10143c460`。 | 未在节点重建路径固化 Harbor 解析。 |
| I02–I04 | 随 `99f497bf` 进入供给器镜像。流水线只核对修订和供给器协议检查。 | 终态重复停止、裸卷续建、流末计量没有在本次隔离资源上复跑。 |
| I05 | 随 KnowMart `7e07c84` 进入 #103 镜像。服务身份边界见上表。 | 上架、获取、普通撤架、已购可见和未购不可见没有现场用户。 |
| I06–I07 | 随 KnowLab `efa6aa6f`、KnowBench `701a82bf` 进入 #104 镜像。 | 共享工具事务外读取、直接脚本预留后撤权没有现场复跑。 |
| I08 | 规划窗口接口已按上表核到空结果。 | 已购版本跨页、实数和调用者限制没有现场样本。 |
| I09–I11 | 随上述源码进入镜像。协议检查没有覆盖这些界面和回执状态。 | 冻结按钮、只读失败与副作用未知的展示、64 字符步骤没有现场复验。 |

## 验证

已核对两波现网镜像、迁移作业完成、协议检查回执、三个开关、KnowMart 服务身份边界，以及七个沙箱的镜像、Codex 版本、配置段和卷。

未运行：同一版本的作者、已购买家和未购用户；登记、上架、获取、普通撤架、发布者资质失效；分页与精确核权的业务样本；调用者限制和空目录实数；含共享工具的递归试跑、冻结、审批中换安装、批准后撤权、已消费确认重放；空页「继续查找下一批专家」、点击后续查、翻页前撤权和改题从第一批查起；未运行工具的冻结提示；终态重复停止、续建原 PVC、跨节点隔离、网关重启、回执收回、清卷、脚本失败或取消后的秒数与结算；管理清理积压和 runner 五分钟告警。这些都需要约定测试账号、隔离物料或模型预算。脚本开关保持关闭，所以没有打开脚本路径。真实用户选法命中率未观测。第 12 项执行预览和 P3–P5 新运行能力未启动。

## 交回

回执只在本文件。两波发布分支和标签已在 GitHub 与 Gitee。请求状态未改，目录未归档。第 12 项仍按原约定暂停，等本回执由 Luna 收单后再恢复。
