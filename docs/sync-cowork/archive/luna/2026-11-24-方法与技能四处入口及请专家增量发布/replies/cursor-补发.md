# Cursor 补发回执

- 对应请求：../request.md
- 构建：[release #120](https://jenkins.dev.sunmoonai.com:30443/job/release/120/)，结果 SUCCESS。批准人 admin，2026-11-24T21:25:19+08:00。回执时间 2026-11-24T21:31:02+08:00。
- 分支 `method-entry-release-20261124`，从 #119 回执 `806b4ded0` 起。部署 `a99c64d1cb0ecff645d65774526e35de111e8696`。晋级指针 `e070aed3256fca8df8520e5f3a3d9f4af45bdd1f`。标签 `release-20261124-6`。流水线回执 `86c7ff65d1b22eaa4ee7c4235739e3412e56f4bb`，正文 `scripts/results/release-120.20261124-213047.md`。部署 OCI `sha256:8187750a2cc7a8d965d67378c74d47bbe9b1c4d4df6d8fb3f86172de0c1ff188`。GitHub 与 Gitee 都已收到分支和标签。
- 只重建并晋级 KnowBench 后端。Web、管理端、KnowLab、KnowMart 的源码钉和运行镜像保持 #119。没有新的库版本。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowBench 父仓 / 后端 | `7f78810` / `47cce65` | 后端 `sha256:9f4f214bbb15607f9d3afe545f47d7a4e1d73a00f7ffdfdf0fb5d8214926376f` |
| KnowBench Web / 管理端 | `56a5f7d` / `33559e9` | Web 仍是 `sha256:1be8c33b29c31274fbfb7f96fab50a0fabc7c40307c6a743715adc8f794063cc`，管理端未重建 |
| KnowLab 后端 / Web | `f85f3d2` / `db5870a` | 仍是 #119 镜像 |
| KnowMart 后端 / Web | `410fc46` / `db4cbd0` | 仍是 #119 镜像 |

KnowBench 的 API、worker、scheduler、runner 都已换成这次后端镜像，部署均为 1/1。runner 仍挂着 `knowbench-knowmart-summon-service`。试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`，请专家全量入口仍关，脚本执行仍开，交付写回仍关。Kimi 指令路由与复核路由仍在。报价环境 `sunmoon-kind`、修订 1、每容器秒 0.01 元。

## 就绪

- 发布前现场 Flux 源是 #119 的 `sha256:470c70d0b53ad1ede8283b7afc7cbe7ac93bdca7a2828c4973c65fcd227c6a83`，对应部署 `08e2365ea`。库版本已是 `20261124_0062`。
- 迁移作业 `knowbench-migrate-9f4f214bbb15-v16` 完成，读回的库版本仍是 `20261124_0062`。KnowLab、KnowMart 没有新的迁移作业。
- KnowBench 相关 Flux kustomization 均 Ready。`application-check APP=knowbench` 退出 0。
- 声明差异只改了后端镜像摘要和部署编号。Web、路由、报价和其他应用没有进入本次差异。

业务复验由 Luna 接手。若要回退，先停消费，再把指针退回 `release-20261124-5` 并按现有规程应用。
