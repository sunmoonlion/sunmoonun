# Cursor 三次补发回执

- 对应请求：../request.md
- 构建：[release #122](https://jenkins.dev.sunmoonai.com:30443/job/release/122/)，结果 SUCCESS。批准人 admin，2026-11-24T23:02:12+08:00。回执时间 2026-11-24T23:09:53+08:00。
- 分支 `method-entry-release-20261124`，从 #121 回执 `bf3bb01f0` 起。部署 `4411a9b17c4b58016a4e6069328f53c2468510e7`。晋级指针 `7ee45ca5088140379bc751c9bf25eadacff73232`。标签 `release-20261124-8`。流水线回执 `99423b85d92d112ad5ab952985cff833b2bbfc41`，正文 `scripts/results/release-122.20261124-230735.md`。部署 OCI `sha256:df59766469b632d3a9eb53531b6c536d1f6af37f81db61006f92d314a7ce28b9`。GitHub 与 Gitee 都已收到分支和标签。
- 只重建并晋级 KnowBench 后端。Web、管理端、KnowLab、KnowMart 的源码钉和运行镜像保持 #119。没有新的库版本，也没有新增配置。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowBench 父仓 / 后端 | `c14eca8` / `644ca9b` | 后端 `sha256:f4c409e506d43947ed7f1cdbd84816c51d31ff6801d9d0d752cc02eeb9d1d614` |
| KnowBench Web / 管理端 | `56a5f7d` / `33559e9` | Web 仍是 `sha256:1be8c33b29c31274fbfb7f96fab50a0fabc7c40307c6a743715adc8f794063cc`，管理端未重建 |
| KnowLab 后端 / Web | `f85f3d2` / `db5870a` | 仍是 #119 镜像 |
| KnowMart 后端 / Web | `410fc46` / `db4cbd0` | 仍是 #119 镜像 |

KnowBench 的 API、worker、scheduler、runner 都已换成这次后端镜像，部署均为 1/1。runner 仍挂着 `knowbench-knowmart-summon-service`。试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`，请专家全量入口仍关，脚本执行仍开，交付写回仍关。Kimi 指令路由与复核路由仍在。报价环境 `sunmoon-kind`、修订 1、每容器秒 0.01 元。

## 就绪

- 发布前现场 Flux 源是 #121 的 `sha256:f492656842d56a47445c1845912c08edcaf336dc0ebad4cfad0a5598ffca8fb3`，对应部署 `4ae4bd180`。库版本已是 `20261124_0062`。
- 迁移作业 `knowbench-migrate-f4c409e506d4-v16` 完成，读回的库版本仍是 `20261124_0062`。KnowLab、KnowMart 没有新的迁移作业。
- KnowBench 相关 Flux kustomization 均 Ready，已应用到 `sha256:df59766469b632d3a9eb53531b6c536d1f6af37f81db61006f92d314a7ce28b9`。`application-check APP=knowbench` 在流水线第 11 阶段退出 0。
- 声明差异只改了后端源码钉、镜像摘要和部署编号。Web、路由、报价和其他应用没有进入本次差异。

业务复验由 Luna 接手。若要回退，先停消费，再把指针退回 `release-20261124-7` 并按现有规程应用。
