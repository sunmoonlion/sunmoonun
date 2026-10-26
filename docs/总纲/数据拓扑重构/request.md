# 请评审：数据拓扑第四版与它的落地 SDD（0043、0044、0045）

> 所有者 2026-10-26：「改好后再新建一个数据拓扑重构目录放审核需求和评审回执」。
>
> **意见交到哪**：写进本文件夹，一人一个文件，用自己的名字命名（例如 `fable.md`）。
> - 本地路径：`/home/zymun/worktrees/qwen/sunmoonun/docs/总纲/数据拓扑重构/`；在远程机上走挂载：`~/wsl-worktrees/qwen/sunmoonun/docs/总纲/数据拓扑重构/`。
> - 只往这个文件夹里加自己那一个文件；**不要 git 提交**，也不要改 qwen 工位的别的文件。写完由 Opus 统一提交，并写评审回执（`opus-response.md`）。
> - 形式不限。这是一次思想风暴：不设题目，自由发挥，目的是把方案想全、想好。可以补没想到的、指出会出问题的、提完全不同的做法。
>
> **状态**：只有文档，没改任何代码。数据拓扑第四版所有者已定稿；0043–0045 是设计稿，还没实施。落地时间按架构总纲第六节第 10 条第五版：现在这批验完打 `kind-flux-final` 以后另起一轮。

## 一、要看的

1. [数据拓扑](../数据拓扑.md)：第四版（2026-10-26 重写）。
2. SDD [0043 数据第四版落地](../../design/SDD/modules/0043-data-v4.md)：knowbase 数据模型、按描述查与解析、各应用怎么改、迁移、实施分块。
3. SDD [0044 knowbase web端](../../design/SDD/modules/0044-knowbase-web.md)：总栏、展示按钮、上传。
4. SDD [0045 knowfeed 供给](../../design/SDD/modules/0045-knowfeed-supply.md)：确认清单受理、请求与作业、渠道审核、拆旧线。
5. 跟着改的：[constraints](../../design/rules/constraints.md) 的 C-L2（新口径）；SDD [0042](../../design/SDD/modules/0042-knowledge-bases.md)、[0037](../../design/SDD/modules/0037-idea-avatar-expert.md)、[0018](../../design/SDD/modules/0018-advisor-market.md)、[0026](../../design/SDD/modules/0026-knowlab.md)、[0019](../../design/SDD/modules/0019-local-library-collect-memory.md) 开头的标注；[架构总纲](../架构总纲.md) 第六节第 10 条第五版；[decisions](../../design/decisions.md)「已定」第一条。

## 二、背景

- 第四版是怎么定下来的：所有者与 Opus 逐条讨论的九条、上一轮四家（Fable、Kimi、Luna、Qwen）对重构大纲的评审与 Opus 处置、重构大纲，都在提交 `149d6353` 的 `docs/总纲/数据拓扑重构/`（那一版目录已删，`git show 149d6353:<路径>` 可看）。所有者原话都在讨论记录里。
- 第三版（被取代的）：提交 `5d533d7b` 的 `docs/总纲/数据拓扑.md`。
- 代码在本地 `/home/zymun/worktrees/qwen/` 下：knowbase、knowfeed、knowbench、knowlab、knowmart 各应用仓与子仓，sunmoon-link；0042 那一版已随发布 #28、#29 上线。
- 生产现状（10-26 只读查）：knowbase 只有 10 条上传资料，没有成交、授权、读数留痕；knowbench 没有钉住的委托数据。
