# 专家方法重构三端体验发版

2026-11-27，所有者要求先发版查看重构后的界面。**#128 已发布，2026-11-27 结案。Luna 已用现场账号验收三个用户页面与运营审核页，并复查 #124 退役行为。** [Cursor 发布回执](replies/cursor.md) · [Luna 现场验收](replies/luna.md)。目标是现有 `sunmoon-kind` 开发体验环境。Luna 从本地 `/home/zymun/worktrees/luna` 发起本单并负责发布后验收。Cursor 在本卡 `replies/cursor.md` 记录构建、晋级结果、迁移版本及可访问时间。

## 候选和现场基线

Luna 发单时读到 Flux `platform` 为 `sha256:f16889a9a3b7719008db57aa5292bbc0b5b96c45935772822193eb45ccc55276`，对应 #124；三端 API、Web 与 KnowBench runner 各有一个就绪副本。请从实际最新晋级线整合下表增量。提交可在 Luna 的对应本地仓读取。

| 应用 | 功能父仓 | 后端 | Web | 管理端 |
| --- | --- | --- | --- | --- |
| KnowLab | `3c6f75744ccff64b0895df6fa39edb6666ad60e7` | `5c1ad30d02951f8768135ed73c41d1042b635dc0` 与现场 #124 的 `8ddff9028ff360c106597e645f74c9ae86ed9c99` 合入同一版本 | `36c13daea4a3204da629481016985525668be5c2` | 沿用现场 |
| KnowBench | `7db654728697a89860584a593b228f158669dc3c` | `2ec1c338c2f1b3941c44f55470fa50a4f887c040` | `88514dd74794aa03e87f60ff07e2fdab23b8eaf1` | 沿用现场 |
| KnowMart | `bdb7e9d79beebc4eae423c510f0587c17cb63c08` | `7ae8eb8c089d4f57b49deacaa017fcbd468ed080` | `7bafcc75bad99acbf90c8e03f06badbf98c0284b` | `6badf80be1d4aecd831bd02581f2af45300c4445` |

三端界面取 Carbon 收尾版。KnowMart 增带 Luna 的 0022 数据库修复，使正式方法响应、成交可落库；已在独立 PostgreSQL 16 通过 72 项回归，Carbon 评审仍在进行。Luna 后续编译器提交留在独立评审卡。尚待处理的旧入口清理另批交付。[KnowMart 修复评审](../../../requests/luna/2026-11-27-KnowMart正式方法需求响应与成交修复评审/request.md)

## 发单前实测

按上述组合核对本地跨仓契约通过。KnowLab 将 #124 与 Carbon 后端作临时合并，Git 树为 `d1471d6a0da6fe8ef7a494fdd7e58c89f56249ae`。在独立 PostgreSQL 16 上，#124 的旧父申请仓储回归和 Carbon 的出处、看板回归共 4 项通过。此结果来自候选源码测试；实际部署状态以 Cursor 的发布回执和现场修订为准。

## 发布与验收

1. 从 #124 或更新现场整合，保留 #124 已发布的 KnowLab 仓储过滤。Carbon 的 `5c1ad30` 历史不含 `8ddff902`。发布父仓钉到实际合并后的后端。平台取 Carbon 对跨仓门禁的代码增量 `ab11f48d6`，在候选指针上核对 `ci/verify-contracts.py --pinned`。
2. 使用项目现有发布流程走迁移、构建、晋级。核对 KnowLab 至 `20261126_0030`、KnowBench 至 `20261126_0063`、KnowMart 经 `20261126_0021` 至 `20261127_0022`。核实当前库状态、迁移任务及镜像就绪，再开放体验。现场账号、已有数据和服务配置沿用。
3. Cursor 将实际源码与父仓指针、Jenkins 构建、Flux 修订、镜像、迁移结果和就绪状态写入回执。如遇晋级或审批阻塞，请注明停在哪一步及现场实际版本。
4. Luna 按实际晋级修订复核登录后的五要素工坊、工作台方法中心、卖家小店和运营审核页，并复查 #124 退役入口。把亲验结果写在 `replies/luna.md`，随后通知所有者。

体验入口为 [KnowLab 五要素工坊](https://knowlab.dev.sunmoonai.com:30443/zh-CN/studio)、[KnowBench 方法与技能](https://knowbench.dev.sunmoonai.com:30443/zh-CN/workbench/methods)、[KnowMart 我的小店](https://knowmart.dev.sunmoonai.com:30443/zh-CN/shop) 和 [KnowMart 运营条目审核](https://knowmart-admin.dev.sunmoonai.com:30443/zh-CN/market/listings)。
