# 请评审（第四轮）：qwen 分支上的代码，发版前全部核一遍

> 所有者 2026-10-29：「要不要等fable好了以后，对齐，然后让kimi fable luna和qwen核一下你的代码等好了再发版」「为何分开核，还像上次那样全部核啊」「你写个第四次审核吧」。
>
> **意见交到哪**：写进本文件夹，一人一个文件，用自己的名字命名（例如 `fable.md`）。
> - 本地路径：`/home/zymun/worktrees/qwen/sunmoonun/docs/总纲/数据拓扑重构/第四轮评审/`；在远程机上走挂载：`~/wsl-worktrees/qwen/sunmoonun/docs/总纲/数据拓扑重构/第四轮评审/`。
> - 只往这个文件夹里加自己那一个文件；**不要 git 提交**，**不要改代码**，也不要改 qwen 工位的别的文件。写完由 Opus 统一提交，逐条核实、在 qwen 上修，并写评审回执（`opus-response.md`）。
> - 不分工：每人都看全部代码。形式不限，可以补没想到的、指出会出问题的、提完全不同的做法。每条问题请写清在哪（仓、文件、行）、什么情况下出错（输入、状态 → 错在哪），能分轻重就分。
>
> **状态**：代码都在本地 `qwen` 分支，只提交了，没推。各仓全量测试都过（knowbench 后端 1210、knowlab 后端 622、knowmart 后端 493；knowbench web端 341、knowlab web端 154、管理端 66）。Fable 已做完第 2a、2b 节的 gitops（fable `eac18b59`，已推，没发版），删除类 gitops 在本地分支 `fable-v4-deletions`（头 `2f5bbd7c`，不推）。顺序是：这一轮评审 → Opus 修 → Fable 把 qwen 合进 fable、发版。**各工位还没对齐**，代码请在本地 qwen 工位看：`/home/zymun/worktrees/qwen/<应用仓>/<子仓>`（只读，不要切分支、不要动工作区），提交范围照下表。

## 一、要看的

### 1. 代码（下表每一行 = 基点..qwen 头；基点是 qwen 与 `origin/fable` 的合并基点）

在应用仓里 `git -C <子仓> log --stat <基点>..<头>` 看提交，`git -C <子仓> diff <基点>..<头>` 看全部改动。

| 应用仓 | 子仓 | 范围 | 提交数 | 主要内容 |
| --- | --- | --- | --- | --- |
| knowbase-app | knowbase-backend | `eedb6d0..01926df` | 20 | 数据第四版块 1–4（资料、内容版本、读法、使用权、描述与词表、展示即同意、运行授权、按描述查与解析、确认、产出区、契约 `data-request/v1`、`knowbot-data-needs/v2`），公开原件与科目表（0047），数据 MCP（0048），词表第 2 版（0049）；删旧 SQLite 数据集、语义层、旧知识 MCP、`user-data/v1`、`UserObjects.copy`（⑰） |
| | knowbase-admin-frontend | `f097495..1f49c43` | 1 | 删旧数据集管理界面 |
| knowfeed-app | knowfeed-backend | `c4cd1d6..61d1a03` | 9 | 供给竖线 3a–3d（0045：受理需求、切合、作业、巨潮目录渠道、按页文字与财报抽表）、证券名录、词表第 2 版的供给；退证券专线与旧数据集（⑰）；`supply-demand` 关系认调用方、调 knowbase 用 `user-data-supply` 身份 |
| | knowfeed-admin-frontend | `b344c10..c640303` | 1 | 删旧证券专线管理界面 |
| knowbench-app | knowbench-backend | `ce8e3b0..e681d3d` | 10 | 清单 v2 的专家请来用数据、第 0 步定数据（⑭）、删清单 v1 与旧数据路（⑰）、测试运行方与测试只在作者账号下跑（0046、⑯）、孵化运行方 `incubate`、AI 请专家（找专家那一轮、`find_expert` 工具、三个服务客户端、对话来源） |
| | knowbench-web-frontend | `17cd09b..4b47bf8` | 6 | 请专家页与委托页按第 0 步（⑭）、删云端知识库页（⑰）、「让 AI 找」、从 knowlab 带着专家回来 |
| knowlab-app | knowlab-backend | `8684d25..4c94955` | 19 | 清单 v2 草稿、测试集与自助测试（0046）、平台测试在作者账号下（⑯）、删清单 v1（⑰）、工作稿（⑮）、孵化契约与 AI 孵化一轮、测试数据说明第 3 版、孵化模式与给平台的授权、运营只能提议、`incubation-request` 关系 |
| | knowlab-web-frontend | `3a0f2c8..a115f1e` | 7 | 测试卡片、撤「知识库」、名称页「孵化」栏与工作稿页、AI 起草、选自己来或请平台、去 knowbench 请它 |
| | knowlab-admin-frontend | `28c79f0..111ceda` | 4 | 孵化页删「用户的数据」、测试等待文案、作者没电脑的提示、运营改工作稿（提议）与出一版 |
| knowmart-app | knowmart-backend | `884f093..f384353` | 6 | 清单 v2（⑭）、删清单 v1 与 `user-data/v1`（⑰）、条目自动下架、成交改名 granted、服务关系 `catalog` 与 `demand` |
| | knowmart-web-frontend | `db315f2..2867a64` | 3 | 专家详情按 v2、删知识库页、下架原因 |
| | knowmart-admin-frontend | `d14c3dc..8941e5b` | 2 | 成交说法跟 v2、状态改名 |

应用仓本身的提交只是子仓指针，另有 knowlab 应用仓删了 `knowlab-backend/storage-access-bootstrap/`。sunmoon-link 这一批没改。

**这批新加的迁移**（发版时依次跑；哪几个删生产记录见 [交Fable-gitops](../交Fable-gitops.md) 第〇节）：knowbase 0010–0018、knowfeed 0016–0019、knowbench 0027–0032、knowlab 0014–0021、knowmart 0010–0011。删记录的那几个请特别看：删的是不是只有该删的、downgrade 写了什么。

### 2. 代码和部署对不对得上

- [交Fable-gitops](../交Fable-gitops.md)：代码要的平台配置、要撤的旧配置、新服务关系（第 2a 节）、跨应用链接（第 2b 节）。
- 已推的新增类：fable `eac18b59`（第 2a、2b 节）；Fable 的回执：[交Fable-gitops-回执](../交Fable-gitops-回执.md) 第七节。
- Fable 的删除类 gitops：本地分支 `fable-v4-deletions`，头 `2f5bbd7c`（工作目录 `/home/zymun/sunmoon-probe-runs/fable-gitops-v4/worktree-deletions`）。代码读的环境变量、服务关系名、内部前缀、`expected_schema_revision`，和这里配的是否一致。

### 3. 照什么写的（对照用）

- [decisions](../../../design/decisions.md)：⑭ ⑮ ⑯ ⑰，10-29 的「叫法」「AI 请专家」与孵化第 5 步三件。
- [数据拓扑](../../数据拓扑.md) 第四版；SDD [0043](../../../design/SDD/modules/0043-data-v4.md)、[0044](../../../design/SDD/modules/0044-knowbase-web.md)、[0045](../../../design/SDD/modules/0045-knowfeed-supply.md)、[0046](../../../design/SDD/modules/0046-knowlab-self-service.md)、[0047](../../../design/SDD/modules/0047-public-disclosures-facts-search.md)、[0048](../../../design/SDD/modules/0048-model-data-tools.md)、[0049](../../../design/SDD/modules/0049-document-types.md)、[0037](../../../design/SDD/modules/0037-idea-avatar-expert.md)、[0018](../../../design/SDD/modules/0018-advisor-market.md)。
- [专家孵化方案](../../专家孵化方案.md)（第十八节是实施进度与各步提交）、[请专家方案设计](../../请专家方案设计.md)（第 4.9 节 AI 请专家）、[叫法](../../../project-guide/叫法.md)。
- [待你决定](../待你决定.md)：各条所有者怎么定的。

## 二、背景与提醒

- 产品没上线，旧格式、旧接口直接删，不留兼容（⑰）；看到删掉的旧路不用要求加回兼容，但删漏了、删多了（还有人在用）请指出。
- Opus 自己知道、请顺带核的几处：
  - knowbench 内置孵化方法 INCUBATE 的指令里加了一句怎么对待参考回答。这段指令所有者逐字核过。
  - AI 请专家里「直接请」由网页在用户在场时做（先钉住，再用用户自己的会话建委托），不是后端代请。
  - 「AI 替你请了谁」只记在浏览器里。
- 跑测试：本地机器资源有限，**不要几个人同时跑全量**。要跑就只跑相关的几个文件；要数据库的自己起一个临时 PostgreSQL 容器，名字和端口不要和别人重，跑完删掉。不碰虚拟机、旧 kind 集群、生产库。
- 第一到三轮评审的是设计（本目录上一级与 [第三轮评审](../第三轮评审/README.md)），这里不重复讨论设计本身；觉得设计有问题、导致代码只能这样写错的，照样可以提。
