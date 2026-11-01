# 请评审（第三轮）：数据拓扑第四版定稿与 0043、0044、0045、knowmart 小店

> 所有者 2026-10-26：「按甲，新建评审目录放审核需求」。第二轮评审之后，又和所有者逐条谈完了采集（需求、供给、切合、存储），并把 knowmart 改成每个用户一家小店；0045 整份重写，0043 整份重写，数据拓扑、0044、0018 随之改。
>
> **意见交到哪**：写进本文件夹，一人一个文件，用自己的名字命名（例如 `fable.md`）。
> - 本地路径：`/home/zymun/worktrees/qwen/sunmoonun/docs/总纲/数据拓扑重构/第三轮评审/`；在远程机上走挂载：`~/wsl-worktrees/qwen/sunmoonun/docs/总纲/数据拓扑重构/第三轮评审/`。
> - 只往这个文件夹里加自己那一个文件；**不要 git 提交**，也不要改 qwen 工位的别的文件。写完由 Opus 统一提交，并写评审回执（`opus-response.md`）。
> - 形式不限。这是一次思想风暴：不设题目，自由发挥，目的是把方案想全、想好。可以补没想到的、指出会出问题的、提完全不同的做法。
>
> **状态**：只有文档，没改任何代码。落地时间按架构总纲第六节第 10 条第五版：现在这批验完打 `kind-flux-final` 以后另起一轮。

## 一、要看的

1. [数据拓扑](../../数据拓扑.md)：第四版，按第二轮评审与采集讨论改过；第七节（采集：需求、供给、切合）、第 16.2 节（存储与 RAGFlow）、第十一节（knowmart 小店）是这一轮新写或大改的。
2. SDD [0045 knowfeed：需求、供给、切合](../../../design/SDD/modules/0045-knowfeed-supply.md)：**整份重写**。
3. SDD [0043 数据第四版落地](../../../design/SDD/modules/0043-data-v4.md)：**整份重写**，第二轮评审采纳的各条、存储、怎么验、发版顺序、平台侧要配的都在里面。
4. SDD [0044 knowbase web端](../../../design/SDD/modules/0044-knowbase-web.md)：按第二轮评审改。
5. SDD [0018 knowmart](../../../design/SDD/modules/0018-advisor-market.md) 第十一节第 7 之二小节：**每个用户一家小店**（新）。
6. 跟着改的：[constraints](../../../design/rules/constraints.md) 的 C-L2；[decisions](../../../design/decisions.md)「已定」前两条。

## 二、背景

- [采集讨论记录](../采集讨论记录.md)：所有者与 Opus 逐条谈的 12 条，所有者原话都在里面。
- 第二轮评审（Fable、Kimi、Luna、Qwen）与 [Opus 回执](../opus-response.md)：在上一级目录 [数据拓扑重构](../README.md)。
- 第一轮（重构大纲的讨论与评审）：提交 `149d6353` 的 `docs/总纲/数据拓扑重构/`；第三版数据拓扑：提交 `5d533d7b`。
- 代码在本地 `/home/zymun/worktrees/qwen/` 下：knowbase、knowfeed、knowbench、knowlab、knowmart 各应用仓与子仓，sunmoon-link。knowfeed 现有的通用采集与证券专线、knowbase 现有的 RAGFlow 接入，是这一轮设计要改造的现状。
- 生产现状（10-26 只读查）：knowbase 只有 10 条上传资料，没有成交、授权、读数留痕；knowbench 没有钉住的委托数据。
