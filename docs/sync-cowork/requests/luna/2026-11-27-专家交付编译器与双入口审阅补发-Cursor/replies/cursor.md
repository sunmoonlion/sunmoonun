# Cursor 回执

- 对应请求：../request.md
- 构建：[release #130](https://jenkins.dev.sunmoonai.com:30443/job/release/130/)，结果 SUCCESS。批准人 admin，2026-11-27T21:18:03+08:00。回执时间 2026-11-27T21:26:00+08:00。
- 分支 `compiler-dual-entry-hotfix-20261127`，从 #129 尖端 `02d421944` / 现场 OCI `sha256:a36b4fd8…` 拉出。跨仓契约 `--pinned` 通过。部署 `c3d41f0510851de21d94827152613eed6c645ad8`。晋级指针 `fc85c18d30d32ba33e39d5d140cf39e27e661ef8`。标签 `release-20261127-3`。流水线回执正文 `infrastructure/.build/release/130/release-130.20261127-212452.md`。部署 OCI `sha256:8ed98e11aa5a2566f204faa92b8135b8fec2d475013306c7f7cf00d2a820e4f9`。GitHub 与 Gitee 都已收到分支和标签。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web | `78b01f9` / `0a2edf3` / `e9266eb` | 后端 `sha256:c123f2f3c39b1e02908fb2e7bafd88e3715e99a6dc9c00389f162f90c69d39e2`，Web `sha256:ab2e7c3329bff54503f23166f5d7e2c280eb5e3902e5a34f35e7c5f8b1f7ec83` |
| KnowLab 管理端 | `89fe3ac` | 沿用现场，未重建 |
| KnowBench 父仓 / 后端 / Web | `d0dffa8` / `64339ce` / `171e1b5` | 后端 `sha256:82f783e0cac9dd27a986935a9e78cb29da2d2c6386fab8c66ec70a4399a37988`，Web `sha256:6b44408730032981e9b1635aad9edef7b9e19846d5f5e4da8840040dc098089f` |
| KnowBench 管理端 | `33559e9` | 沿用现场，未重建 |

KnowLab 库版本仍为 `20261126_0030`，KnowBench 仍为 `20261126_0063`，无新迁移。本轮 `APPS=knowlab knowbench`，`PIN=heads`。

## 迁移与就绪

- 迁移作业完成：`knowlab-migrate-c123f2f3c39b-v5`、`knowbench-migrate-82f783e0cac9-v16` → Complete。
- Flux `platform` Ready，修订 `sha256:8ed98e11…`。KnowLab API / Web / worker / scheduler 与 KnowBench API / Web / worker / scheduler / runner 均为 1/1，镜像摘要与上表一致。两端管理端仍为上一版副本。
- `application-check` 对 knowlab / knowbench 均通过。

## 可访问时间

约 2026-11-27T21:25+08:00 起可体验。入口：

- [KnowLab 五要素工坊](https://knowlab.dev.sunmoonai.com:30443/zh-CN/studio)
- [KnowBench 方法与技能](https://knowbench.dev.sunmoonai.com:30443/zh-CN/workbench/methods)

业务验收由 Luna 按本卡现场条目接手。若要回退，先停消费，再把指针退回 `release-20261127-2` 并按现有规程应用。
