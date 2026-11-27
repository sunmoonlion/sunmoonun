# Cursor 回执

- 对应请求：../request.md
- 构建：[release #129](https://jenkins.dev.sunmoonai.com:30443/job/release/129/)，结果 SUCCESS。批准人 admin，2026-11-27T20:55:50+08:00。回执时间 2026-11-27T21:05:00+08:00。
- 分支 `studio-match-hotfix-20261127`，从 #128 尖端 `7316e3a54` / 现场 OCI `sha256:36fc3381…` 拉出。跨仓契约 `--pinned` 通过。部署 `ea4f89b537aaba604594f1b3779ff6c53991175d`。晋级指针 `ed7ef33e1eb3585d317021c2c8c9b21b6ed07952`。标签 `release-20261127-2`。流水线回执正文 `infrastructure/.build/release/129/release-129.20261127-210209.md`。部署 OCI `sha256:a36b4fd8edc1e21029367c163f24ad1a93cd263d8d4352a7e0b6558552d2ca67`。GitHub 与 Gitee 都已收到分支和标签。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web | `7c42f27` / `b089eb1` / `d5b9477` | 后端 `sha256:e36be3c8666904aac2b6805624ffecd4431babf89ccf42dbcbcfe97519556325`，Web `sha256:a3d88158fca704cca191c8ad584d6020b349b5eab4a302c46534432811bd9249` |
| KnowLab 管理端 | `89fe3ac` | 沿用现场，未重建 |
| KnowBench 父仓 / Web | `4b37b64` / `ecc32a1` | Web `sha256:b3a18979fa6ef1be6f6ceb64bb3accca5dd279386424069078f69631d0b4b4e0` |
| KnowBench 后端 | `2ec1c338` | 沿用 #128 `sha256:24f874af5f99375ee50620c655eea282b9dc440be52025007f259d0c2d18cb36` |
| KnowBench 管理端 | `33559e9` | 沿用现场 `sha256:74c0a17b57aa11feda8adec69f3d18865515388987c237f3886edcd44dcc2725` |

KnowLab 库版本仍为 `20261126_0030`，无新迁移。本轮 `APPS=knowlab knowbench`，`PIN=heads`。

## 迁移与就绪

- 迁移作业完成：`knowlab-migrate-e36be3c86669-v5` → Complete。KnowBench 后端未重建，迁移未重跑。
- Flux `platform` Ready，修订 `sha256:a36b4fd8…`。KnowLab API / Web / worker / scheduler 与 KnowBench API / Web / worker / scheduler / runner 均为 1/1，镜像摘要与上表一致。两端管理端仍为上一版副本。
- `application-check` 对 knowlab / knowbench 均通过。

## 可访问时间

约 2026-11-27T21:02+08:00 起可体验。入口：

- [KnowLab 五要素工坊](https://knowlab.dev.sunmoonai.com:30443/zh-CN/studio)
- [KnowBench 方法与技能](https://knowbench.dev.sunmoonai.com:30443/zh-CN/workbench/methods)

业务验收由 Luna 按本卡现场条目接手。若要回退，先停消费，再把指针退回 `release-20261127-1` 并按现有规程应用。
