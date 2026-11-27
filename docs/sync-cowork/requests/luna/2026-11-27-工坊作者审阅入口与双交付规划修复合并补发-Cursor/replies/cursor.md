# Cursor 回执

## #131（已终止）

- 构建：[release #131](https://jenkins.dev.sunmoonai.com:30443/job/release/131/)，结果 **ABORTED**。旧两镜像分支不作废重跑。

## 中间失败（已由 #134 接上）

- [release #132](https://jenkins.dev.sunmoonai.com:30443/job/release/132/) ABORTED：host 执行器被卡住的 render-check/幽灵占用。
- [release #133](https://jenkins.dev.sunmoonai.com:30443/job/release/133/) FAILURE：Jenkins 工作区残留 #131 半成品 gitops 脏文件（`工作区不干净`）。已 `reset --hard` 清场后重排队。

## 三端合并发布（#134 SUCCESS）

- 回执时间：2026-11-27T22:57:09+08:00
- 构建：[release #134](https://jenkins.dev.sunmoonai.com:30443/job/release/134/)，结果 **SUCCESS**。批准人 admin，2026-11-27T22:48:21+08:00。**非 #131**。
- 平台基线 `ec4b22da856b5c3a611cc6a9d0b4bf29475e0432`，发布分支 `combined-130-studio-cleanup-20261127`（另含迁移头升版）；排队尖端 `6808c58d1`；部署提交 `fe2481696672de75de96594a70eba180c4e317df`；指针 `d42f6c38a14c5b63cd68a2c17a2aeb3f40d64beb`；标签 `release-20261127-4`。
- 参数：`APPS=knowlab knowbench knowmart`，`PIN=heads`。流水线回执 `scripts/results/release-134.20261127-225709.md`。部署 OCI `sha256:38956bcf478b5e78936d3bab4082d05b9f72b7c837302797e3a65f4a37f97b67`。GitHub 与 Gitee 均已收到分支与标签。

### 迁移前复核与备份

现场只读计数与卡面一致：KnowLab 待清空工作稿 12 / 总数 70；`knowbot_amendment` 1 行；`reference_answer` 非空 0；KnowBench 两旧表各 0 行。库版本迁移前为 `20261126_0030` / `20261126_0063`。

备份目录：`/home/zymun/backups/db/pre-combined-130-20261127-222013`（含两端全库 `-Fc` 与受影响表 schema/data SQL，以及 `impact-counts.txt`）。

### 七个变更镜像

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web / 管理端 | `e3b0eb6` / `f53aad1` / `4e0f8d4` / `e4d87c5` | 后端 `sha256:de8ec1c748cf…4264`，Web `sha256:13b6f33e4f41…44aef`，管理端 `sha256:1cc62f952ee5…241d` |
| KnowBench 父仓 / 后端 / Web | `09b15e9` / `bc43a07` / `8334027` | 后端 `sha256:dd585e3d2996…3da3`，Web `sha256:7e4f0ccd2933…cbfc6` |
| KnowBench 管理端 | 沿用现场 | 未重建 |
| KnowMart 父仓 / 后端 / Web | `de4e816` / `5f2ecd1` / `7c63629` | 后端 `sha256:154b6b113d50…5249`，Web `sha256:36f937cc8597…de010` |
| KnowMart 管理端 | 沿用现场 | 未重建 |

跨仓契约 `--pinned` 通过。平台 `expected_schema_revision`：KnowLab `20261127_0031`、KnowBench `20261127_0064`、KnowMart `20261127_0022`（本轮无变）。

### 迁移与就绪

- 迁移作业完成：`knowlab-migrate-de8ec1c748cf-…`、`knowbench-migrate-dd585e3d2996-…` → Complete（KnowLab `0030→0031`，KnowBench `0063→0064`）；KnowMart 迁移作业随晋级完成，库版本仍为 `20261127_0022`。
- Flux `platform` Ready，修订 `sha256:38956bcf…`。三端 API / Web / worker / scheduler（及 KnowBench runner）均为 1/1，镜像摘要与上表一致。
- `application-check` 对 knowlab / knowbench / knowmart 均通过。

### 可访问时间

约 2026-11-27T22:57+08:00 起可体验。入口：

- [KnowLab 五要素工坊](https://knowlab.dev.sunmoonai.com:30443/zh-CN/studio)
- [KnowBench 方法与技能](https://knowbench.dev.sunmoonai.com:30443/zh-CN/workbench/methods)
- [KnowMart](https://knowmart.dev.sunmoonai.com:30443/)

业务验收由 Luna 按本卡现场条目接手。若要回退，先停消费，再把指针退回 `release-20261127-3` 并按现有规程应用；库回退可用上述备份目录。
