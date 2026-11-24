# Cursor 回执

- 对应请求：../request.md
- 构建：[release #117](https://jenkins.dev.sunmoonai.com:30443/job/release/117/)，结果 SUCCESS。回执时间 2026-11-24T10:47:24+08:00。
- 分支 `m02-catalog-fix-20261124`，从 #116 回执 `9316239d5` 起。部署 `9e6515a82`。晋级指针 `3c4761985`。标签 `release-20261124-2`。流水线回执 `e7d0ce0d6`，正文 `scripts/results/release-117.20261124-104724.md`。
- 发布状态：只更新了 KnowLab 后端及其 API、worker、scheduler。三者均为 1/1 就绪。前端、KnowBench、库版本、Kimi 路由、请专家名单和脚本报价沿用 #116。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 | `a46c632` / `4bb3f27` | `sha256:a0a41bca6c688b7201a95f649a0061b052287c8f656af8b1babb739bbe5728df` |
| KnowLab Web | `9f65b6b`，与 #116 相同 | `sha256:1b798e84ed4606b9d235d380634b264c7a2d44d42db8ff452604410f8f459433`，未重建 |
| KnowBench 后端 / Web | `0eb40f0` / `b54f2ba` | 仍是 #116 的 `sha256:ee09225cd1ee…` 与 `sha256:d00a974e3e5f…` |

KnowLab 迁移作业 `knowlab-migrate-a0a41bca6c68-v5` 完成，库版本仍是 `20261120_0029`。KnowBench 仍是 `20261123_0061`。现场 `WORKBENCH_SKILL_SCRIPTS_ENABLED=true`，报价修订 1，试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`。
