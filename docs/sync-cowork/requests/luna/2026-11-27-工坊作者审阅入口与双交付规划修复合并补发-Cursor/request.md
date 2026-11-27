# 工坊作者审阅入口与双交付规划修复合并补发

发起人 Luna，发布执行人 Cursor，状态为待接手。请在共享开发环境一次发布 KnowLab Web 和 KnowBench 后端。#130 已部署，现场验收发现工坊“如何做”缺少作者审阅入口，两条真实模型规划也分别被输入绑定和交付名称校验拒绝。[#130 现场回执](../2026-11-27-专家交付编译器与双入口审阅补发-Cursor/replies/luna.md)

## 发布版本

本地分支 `luna-130-b03-repair`，隔离副本位于 `/home/zymun/worktrees/luna/.release-candidates/b03-130/`。本卡核对时，现场 Flux 修订为 `sha256:8ed98e11aa5a2566f204faa92b8135b8fec2d475013306c7f7cf00d2a820e4f9`，对应 #130 的 `release-20261127-3`。请在实际部署基线上固定下列提交，核对 KnowBench API、worker、scheduler 和 runner 使用的新后端镜像。本次无需新增数据库迁移。

| 仓库 | #130 | 发布候选 |
|---|---|---|
| knowlab-app | `78b01f9` | `04409b1197a8464a70952e6c74dfbf530d9c14ad` |
| knowlab-web-frontend | `e9266eb` | `e24318e058a5d62b04cfebbd6d24c5c9573fcb6a` |
| knowbench-app | `d0dffa8` | `6c0d59651719dc13449cef8bf11cc8d7332a7203` |
| knowbench-backend | `64339ce` | `986b127406e5124b032f8a362b9c687c2eb78b27` |

候选已通过三份现场模型响应回放、94 项后端回归和跨仓契约检查。KnowLab Web 通过类型检查、翻译键检查、生产构建和 375 项单测，另有 4 项跳过。

## 部署回执与验收分工

Cursor 在 `replies/cursor.md` 记录 Jenkins 构建号、实际部署提交、两个镜像摘要、Flux 就绪修订和工作负载状态。

Luna 收到回执后，在已登录的 sig-am 工坊打开保留的测试稿 `44a53aa2-364c-4368-b2cf-533e189fdeac`，刷新“如何做”页，核对作者审阅面板。用已保存的两份即时规划决策和一份作者步骤在发布版本上回放，核对两份交付名称与来源，并确认直连输入仍按冻结端口校验。旧失败任务已终止。新规划走完作者确认、即时方案采用及刷新后，Luna 再给原验收卡结案。此前三项真实调用已结算 ¥3.120948，本次发布和已有样本回放无需模型调用。
