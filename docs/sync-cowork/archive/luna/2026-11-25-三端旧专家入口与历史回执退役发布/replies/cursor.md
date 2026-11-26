# Cursor 回执

- 对应请求：../request.md
- 构建：[release #123](https://jenkins.dev.sunmoonai.com:30443/job/release/123/)，结果 SUCCESS。批准人 admin，2026-11-25T09:10:57+08:00。回执时间 2026-11-25T09:20:28+08:00。
- 分支 `legacy-expert-retire-20261125`，从 #122 回执 `99423b85d` 起。部署 `6bc2630446c779a05972351251be5421982a1621`。晋级指针 `5ac35b73277f7d02f89cb8ddcc6b5c6c3b7f54f5`。标签 `release-20261125-1`。流水线回执 `15b34d38034bbe5f91e17c33d6b9a0d3f1bf0299`，正文 `scripts/results/release-123.20261125-092027.md`。部署 OCI `sha256:74d6eb3eca7ff9a78533fd02e01d6e0aea0035a973b4e32ce3293d51cf6224`。GitHub 与 Gitee 都已收到分支和标签。
- 重建并晋级三端后端与 Web。三端管理端源码钉和运行镜像保持 #122。库版本仍是 KnowBench `20261124_0062`、KnowLab `20261120_0029`、KnowMart `20261124_0020`。没有新增配置。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowBench 父仓 / 后端 / Web | `53ebdca` / `984fd50` / `6c96e43` | 后端 `sha256:61ab4d84b5ea779f03b30bb140c3172e9e25116933915f73a560bdaa765a908a`，Web `sha256:9aad3a7d30cbee336eb7abb0b277327e060d0850a58df77c56e8a15040f2d718` |
| KnowLab 父仓 / 后端 / Web | `7c18a9e` / `7d51864` / `b681780` | 后端 `sha256:b4317323654158295305c8b976906decd6d79424674d80eeccd38fba1edbd34a`，Web `sha256:b4deb052ef3b06e520f04df1edfccec7e25a3c602b0c1de163a6c9687170e54d` |
| KnowMart 父仓 / 后端 / Web | `1a849d7` / `fbf1e4d` / `b55591d` | 后端 `sha256:7385d4cca18cd776c5b4a7e621a62bb4915334de5238339d391d3bcf61202f2e`，Web `sha256:6e5a70e85fe13877e9fb4ecaa199b1be668aa9ccddd5bdb6b567032bb3fb111b` |
| 三端管理端 | KnowBench `33559e9`，KnowLab `89fe3ac`，KnowMart `5f10911` | 沿用上一版，未重建 |

KnowBench、KnowLab、KnowMart 的 API、worker、scheduler 使用各自的新后端镜像，均为 1/1。KnowBench runner 同样使用新后端镜像，并且仍挂着 `knowbench-knowmart-summon-service`。试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`，请专家全量入口仍关，脚本执行仍开，交付写回仍关。Kimi 指令路由与复核路由仍在。报价环境 `sunmoon-kind`、修订 1、每容器秒 0.01 元。

## 就绪

- 发布前现场 Flux 源是 #122 的 `sha256:df59766469b632d3a9eb53531b6c536d1f6af37f81db61006f92d314a7ce28b9`。三个后端镜像与 #122 回执一致。
- 批准后、新运行负载就绪前，已将 `knowbench-runner`、`knowbench-worker`、`knowlab-worker`、`knowmart-worker` 缩到 0。当时 Celery 没有执行中的任务，只有定时短泵。Flux 按新清单把这些进程恢复为 1/1，API、scheduler 与三个 Web 同时切到新镜像。
- 迁移作业 `knowbench-migrate-61ab4d84b5ea-v16`、`knowlab-migrate-b43173236541-v5`、`knowmart-migrate-7385d4cca18c-v5` 完成。版本代次与 #122 相同，没有新的库版本。
- 三端相关 Flux kustomization 均 Ready，已应用到 `sha256:74d6eb3eca7ff9a78533fd02e01d6e0aea0035a973b4e32ce3293d51cf6224`。三个 `application-check` 均退出 0。
- 声明差异只改了三端后端与 Web 的源码钉、镜像摘要和部署编号。路由、报价、试验名单、服务关系和管理端没有进入本次差异。

业务验收由 Luna 接手。若要回退，先停消费，再把指针退回 `release-20261124-8` 并按现有规程应用。
