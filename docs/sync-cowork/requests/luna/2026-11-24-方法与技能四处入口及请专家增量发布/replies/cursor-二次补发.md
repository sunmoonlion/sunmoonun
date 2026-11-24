# Cursor 二次补发回执

- 对应请求：../request.md
- 构建：[release #121](https://jenkins.dev.sunmoonai.com:30443/job/release/121/)，结果 SUCCESS。批准人 admin，2026-11-24T22:05:34+08:00。回执时间 2026-11-24T22:13:00+08:00。
- 分支 `method-entry-release-20261124`，从 #120 回执 `86c7ff65d` 起。部署 `4ae4bd18065691493a1b6ffbea26555902da4cd1`。晋级指针 `5c65b49a28e89a38c518c1add9eae16b37a43587`。标签 `release-20261124-7`。流水线回执 `bf3bb01f050d45b63543692aeefa28112069814e`，正文 `scripts/results/release-121.20261124-221139.md`。部署 OCI `sha256:f492656842d56a47445c1845912c08edcaf336dc0ebad4cfad0a5598ffca8fb3`。GitHub 与 Gitee 都已收到分支和标签。
- 只重建并晋级 KnowBench 后端。Web、管理端、KnowLab、KnowMart 的源码钉和运行镜像保持 #119。没有新的库版本。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowBench 父仓 / 后端 | `370d07b` / `d26859c` | 后端 `sha256:578b1de58136101144e96f0b10573446f368147cabeecea786ba51818fe31873` |
| KnowBench Web / 管理端 | `56a5f7d` / `33559e9` | Web 仍是 `sha256:1be8c33b29c31274fbfb7f96fab50a0fabc7c40307c6a743715adc8f794063cc`，管理端未重建 |
| KnowLab 后端 / Web | `f85f3d2` / `db5870a` | 仍是 #119 镜像 |
| KnowMart 后端 / Web | `410fc46` / `db4cbd0` | 仍是 #119 镜像 |

KnowBench 的 API、worker、scheduler、runner 都已换成这次后端镜像，部署均为 1/1。runner 仍挂着 `knowbench-knowmart-summon-service`。试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`，请专家全量入口仍关，脚本执行仍开，交付写回仍关。Kimi 指令路由与复核路由仍在。报价环境 `sunmoon-kind`、修订 1、每容器秒 0.01 元。

## 就绪

- 发布前现场 Flux 源是 #120 的 `sha256:8187750a2cc7a8d965d67378c74d47bbe9b1c4d4df6d8fb3f86172de0c1ff188`，对应部署 `a99c64d1c`。库版本已是 `20261124_0062`。
- 迁移作业 `knowbench-migrate-578b1de58136-v16` 完成，读回的库版本仍是 `20261124_0062`。KnowLab、KnowMart 没有新的迁移作业。
- KnowBench 相关 Flux kustomization 均 Ready，已应用到 `sha256:f492656842d56a47445c1845912c08edcaf336dc0ebad4cfad0a5598ffca8fb3`。`application-check APP=knowbench` 在流水线第 11 阶段退出 0。
- 声明差异只改了后端源码钉、镜像摘要和部署编号。Web、路由、报价和其他应用没有进入本次差异。

业务复验由 Luna 接手。若要回退，先停消费，再把指针退回 `release-20261124-6` 并按现有规程应用。
