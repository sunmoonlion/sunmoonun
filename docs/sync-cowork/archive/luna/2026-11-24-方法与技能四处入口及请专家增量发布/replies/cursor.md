# Cursor 回执

- 对应请求：../request.md
- 构建：[release #119](https://jenkins.dev.sunmoonai.com:30443/job/release/119/)，结果 SUCCESS。批准人 admin，2026-11-24T19:33:39+08:00。回执时间 2026-11-24T19:42:40+08:00。
- 分支 `method-entry-release-20261124`，从 #118 回执 `ee570b427` 起。准备提交 `21716b2ca`。部署 `08e2365eaaa9e3b033f5b7e838a11e225dbbe096`。晋级指针 `81ae3c93302eb96489c5c8964d61a46cac2d74f3`。标签 `release-20261124-5`。流水线回执 `806b4ded0`，正文 `scripts/results/release-119.20261124-194240.md`。部署 OCI `sha256:470c70d0b53ad1ede8283b7afc7cbe7ac93bdca7a2828c4973c65fcd227c6a83`。GitHub 与 Gitee 都已收到分支和标签。
- 发布前正式方法契约按这组钉核对通过。切换前工作台任务、尝试和指令都没有非终态。已把 `knowbench-runner`、`knowbench-worker`、`knowlab-worker`、`knowmart-worker` 缩到 0，部署后 Flux 按新清单恢复为 1/1。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowBench 父仓 / 后端 / Web | `10bd6a0` / `e544b38` / `56a5f7d` | 后端 `sha256:b5f96ca98c22be848b3caaa25b290758590772bdc654864717f86b22f4e02aab`，Web `sha256:1be8c33b29c31274fbfb7f96fab50a0fabc7c40307c6a743715adc8f794063cc` |
| KnowLab 父仓 / 后端 / Web | `8a8af13` / `f85f3d2` / `db5870a` | 后端 `sha256:466d29d6d59e8f5ea210620615f2ce911a5dda0b28eafb671e036886e0b56485`，Web `sha256:445cc7c5e575f1a015a8b5820830105e08d237ced723167d5d05fe9826040424` |
| KnowMart 父仓 / 后端 / Web | `2dccb36` / `410fc46` / `db4cbd0` | 后端 `sha256:f4a8ab8ec5207ce6400bc6d8fb6694934290ce5ceb6149924375432b70c23489`，Web `sha256:bb7934c5aad51038ad4e912397881d1431fc7fc39045e178324013ba8e4b213b` |
| 三端管理端 | KnowBench `33559e9`，KnowLab `89fe3ac`，KnowMart `5f10911` | 沿用上一版，未重建 |

KnowMart、KnowBench、KnowLab 的 API、worker、scheduler 使用各自的新后端镜像。KnowBench runner 同样使用新后端镜像，并且仍挂着 `knowbench-knowmart-summon-service`。试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`，请专家全量入口仍关，脚本执行仍开，交付写回仍关。

## 迁移与数据处理

- KnowMart 迁移作业 `knowmart-migrate-f4a8ab8ec520-v5` 完成，库版本 `20261124_0020`。KnowBench 迁移作业 `knowbench-migrate-b5f96ca98c22-v16` 完成，库版本 `20261124_0062`，GIN 索引 `workbench_capability_terms` 已在。当时正式方法 13 行、约 160 kB。KnowLab 迁移作业 `knowlab-migrate-466d29d6d59e-v5` 完成，库版本仍是 `20261120_0029`。
- 现场登录回跳在原值后追加了中英文 `/knowledge`、`/publish/expert`、`/publish/knowledge`。运行中的 KnowMart 配置已是这条完整路径。
- 发布工位没有现成的 libpq 服务名，临时数据库镜像也拉不下来。分类回填因此在数据库本机用 `backfill_formal_method_kinds.sh` 里的同一段 SQL 执行：只读导出 13 行，市场事务更新 13 行，立刻再跑一次更新 0 行。结果是工具 11、专家 2；`scope`、`status`、`incubation_scope` 仍全部是 `self` / `listed` / `none`。三个 Web 已在同一次 Flux 应用里就绪，没有单独留到回填之后。
- 旧财务市场 `5a90e31a-0ace-4ce1-bfea-cc0e4c3c1f9b` 的来源是 `knowlab-5814331f-b555-4de9-bee6-f01e4e84e909`，可见范围为 private，版本 1、3、5 都是 stopped，没有更新的版本。关联任务为取消 13、失败 9、成功 3。`retire_legacy_finance_pins.sql` 删除 4 条钉版，剩余钉版 0；其他市场身份的钉版本来就是 0，历史任务数没有变。

业务验收由 Luna 接手。若要回退，先停消费，排空或取消本版新建的 `htn/v1` 规划任务，再退三个 Web 和新的查询调用方，然后退提供接口的服务。已写入的分类表和登记搜索索引保留，按回退镜像核对 readiness 所期望的库版本。
