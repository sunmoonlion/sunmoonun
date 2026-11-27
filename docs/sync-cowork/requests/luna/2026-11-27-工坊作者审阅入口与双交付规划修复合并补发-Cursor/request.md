# 工坊作者审阅、双交付规划与三端旧入口清理合并补发

## 当前执行项 · 撤回 #134 中的 Luna 递归规划内核

所有者已要求立即撤回。#134 发布完成，线上 KnowBench 后端为 `bc43a07`。发布执行人 Cursor 可从以下已固定的版本继续本卡。此前依赖独立交付规划动作的现场验收条目随该动作撤回。

| Jenkins 参数或版本 | 值 |
|---|---|
| BRANCH | `rollback-134-carbon-planner-20261127` |
| APPS / PIN | `knowbench` / `keep` |
| 平台提交 | `a4c73e2563b6091c88d76281efdbe631e8642597`，基于线上 #134 标签提交 `d42f6c38a14c5b63cd68a2c17a2aeb3f40d64beb` |
| KnowBench 父仓 | `99eac3037deb27dce2aa82699ba6508cdca74f72` |
| KnowBench 后端 | `6fdfc7c8add6fe2df3120fa22770fb268813856e` |

相对 #134，后端只改动 `app/app/domain/workbench/hierarchical_planning.py` 和它的单元测试。两份文件与 Carbon `2ec1c338c2f1b3941c44f55470fa50a4f887c040` 逐字节相同。递归执行驱动文件与 Carbon 一致。保留已发布的编译器和编排数据读取契约。KnowBench 库版本为 `20261127_0064`，本次无数据库迁移。平台清单只更新 KnowBench 父仓与后端修订。

本地 53 项规划和临时图回归通过，另有 6 项隔离 PostgreSQL 双入口及嵌套调用测试通过。平台固定版本跨仓契约检查通过。切换前只读查询显示，保存过 `delivery_goals` 快照的未结束任务为 0；部署时请复核，以免新产生的在途规划中断。

请通过原发布流水线执行，回执续写本卡 `replies/cursor.md`，记录实际构建、Flux 修订、API / worker / scheduler / runner 镜像；核对已部署镜像内的规划器源码与 Carbon 相同。保留 #134 既有迁移与其他镜像。

## #134 已发布记录

以下为 #134 当时的范围和验收计划。[Cursor 发布回执](replies/cursor.md)

## 一次发布的固定版本

线上基线为 `release-20261127-3`，平台提交 `fc85c18d30d32ba33e39d5d140cf39e27e661ef8`，Flux 摘要 `sha256:8ed98e11aa5a2566f204faa92b8135b8fec2d475013306c7f7cf00d2a820e4f9`。本地平台分支 `luna-130-consolidated-20261127` 的提交为 `ec4b22da856b5c3a611cc6a9d0b4bf29475e0432`，隔离目录为 `/home/zymun/worktrees/luna/.release-candidates/combined-130/platform`。相对线上平台只改了 `infrastructure/applications/sources.yaml`。三端应用与子仓对象在 `/home/zymun/worktrees/luna`。Cursor 执行时先使 CI 能取到下表的固定提交，再核对父仓 gitlink 和平台清单；若流水线按分支取头，请核对实际读取的 SHA。

| 应用 | 父仓 | 后端 | Web | 管理端 |
|---|---|---|---|---|
| KnowLab | `e3b0eb6d8334b7dc9ed70b8b9f4a003a450b559d` | `f53aad14ac4c6c00493fd5962e73ce48da9a6270` | `4e0f8d4f272f4f01f8a70064453a3477c450696f` | `e4d87c5df89b237806bf4aec64bc7585422820f3` |
| KnowBench | `09b15e938ab0d656502da57a1cf2d3da3d07b179` | `bc43a07b27a92b6cbc19b88f86ca3d39611bfc94` | `83340277ca542bfe0e71c0340e17769d6bd20dc0` | 沿用 #130 |
| KnowMart | `de4e816343e07275f092a3e25bef12180e29088c` | `5f2ecd1f6a91ee2e0f71d788a25ffb5344c228bd` | `7c6362929bc983d77417ad416cb3aaf65bbb3e35` | 沿用 #130 |

## 数据库切换

11 月 27 日在 #130 数据库执行了只读计数。切换前请复核受影响行数，留存可恢复的备份，并协调仍使用旧列或旧表的工作负载退出。降级脚本能重建结构，已清理的内容需要从备份恢复。

| 应用 | 迁移 | #130 现场影响 |
|---|---|---|
| KnowLab | `20261126_0030 → 20261127_0031` | 清空 12 份旧工作稿的正文、来源、数据格式、规划状态和父缺口，保留工作稿行。删除含 1 条记录的旧补充表，移除旧参考答案列，其中非空值为 0。 |
| KnowBench | `20261126_0063 → 20261127_0064` | 删除旧复核决定表和旧路由确认表，两表各 0 条记录。 |
| KnowMart | 沿用 `20261127_0022` | 本次无新增迁移。 |

## 本地验收

- 三端后端针对本次改动的 PostgreSQL 回归通过。KnowLab 43 项、KnowBench 100 项、KnowMart 73 项，合计 216 项。
- 四个变更前端通过类型检查、翻译键检查和生产构建。单测通过 891 项，套件标记跳过 6 项。合并候选的固定版本跨仓契约检查通过。
- 四项 Chromium 场景使用生产构建、配套测试会话和受控样本。KnowLab 登录后直开旧 `formal-method`、`workdraft` 书签均返回 404；新工坊打开“如何做”，作者能查看规划、编辑步骤、确认并刷新查看已确认结果。KnowBench 登录后旧 `/workbench/review` 返回 404。KnowMart 给出作者拥有、仍在售且来自 KnowLab 的版本，打开版本记录可见该版本，页面没有停用按钮或指向旧管理页的链接。
- 两份真实即时规划响应回放后，两项命名交付均对应用户原文。另一份真实作者响应保留了步骤的 `check → opening_evidence` 映射，规划推进到下一节点。此次回放使用既有样本，新增费用为零。此前三项真实调用共 ¥3.120948。

## 发布与现场验收

Cursor 在本卡现有 `replies/cursor.md` 续记新构建号、实际部署提交、七个变更镜像摘要、迁移前后版本、Flux 就绪修订和工作负载状态。KnowBench API、worker、scheduler 和 runner 须核对实际使用的后端镜像。

Luna 在部署后用 sig-am 账号从新工坊打开测试稿 `44a53aa2-364c-4368-b2cf-533e189fdeac` 的“如何做”，刷新后核对作者审阅。复验两个旧编辑书签、旧复核页和市场所有者操作，再在部署版本上回放已有样本，核对直连输入的冻结端口、两份交付名称和各自来源。现场分别记录作者确认、即时方案采用和刷新后的结果，复验辅助输出显式选择、漏填映射提示及单输出自动绑定，再结本卡。旧失败任务已终止。
