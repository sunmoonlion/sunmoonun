# 容器 Opus 交接摘要（2026-11-06 至 11-07）

> 写给接手的本地助手与所有者。远程云端容器里的 Opus 这两天做了什么、做到哪、哪些没上线、哪些等所有者定、在哪里查。所有代码与文档都已提交并推到 `qwen`（sunmoonun 另推到 cursor、fable、kimi、luna、agy 五个工位分支）。
> 详细的每项来由在 [接手计划（历史）](https://github.com/sunmoonlion/sunmoonun/blob/4ca837c7bd90a644e1dfa09a7f4d386ad9a871f9/docs/%E6%80%BB%E7%BA%B2/opus%E6%8E%A5%E6%89%8B%E8%AE%A1%E5%88%92-2026-11-06.md)；审查原文在 [Luna 段逐文件审查（历史）](https://github.com/sunmoonlion/sunmoonun/blob/4ca837c7bd90a644e1dfa09a7f4d386ad9a871f9/docs/%E6%80%BB%E7%BA%B2/luna%E5%BC%80%E5%8F%91%E9%80%90%E6%96%87%E4%BB%B6%E5%AE%A1%E6%9F%A5-2026-11-06.md)；待办账在 [pending-after-migration](../design/pending-after-migration.md)。

## 一、现在各仓的头（都在 `qwen` 分支，本地远端同号）

| 仓 | 头 | 线上（#85）对应的号 | 说明 |
| --- | --- | --- | --- |
| sunmoonun | `ae1db5b2` 及本摘要那一笔 | — | 文档、部署配置、发版卡 |
| knowbase-app | `582efeaa` | `cb1cb10a` | 多了 SDD 0051（要哪些数）与契约加法，**未上线** |
| knowbase-backend | `3b23eb52` | `bf59f85d` | 同上 |
| knowfeed-app | `56ed9df0` | `67638eb9` | 多了 0051 收要数的需求项、user-data 锁，**未上线** |
| knowfeed-backend | `d0552d13` | `4b5d9ac3` | 同上 |
| knowbench-app | `915e31c4` | `6049c865` | 多了 0050 固定专家新路、0051 第 0 步按指标要数、K29 只认列、目录模型修正、契约退役表，**未上线** |
| knowbench-backend | `d6257003` | `c7d3d14d` | 同上 |
| knowbench-web-frontend | `c8f70622` | `7026bfea` | 数据清单认要数的条目，**未上线** |
| knowlab-app | `30e2ae8c` | `43d2192f` | 只跟了契约锁、退役表、逐字段比对测试，行为不变，**未上线** |
| knowlab-backend | `3f16dc2f` | `614da0ab` | 同上（加了一个还没用到的 FactRequest 模型） |
| knowlab-web-frontend | `25772149` | `25772149` | 不变 |
| sunmoon-link | `5c41d1fb` | 未发 | 账 187 已改，随下一版 link 出包 |

**knowbench 的 `qwen` 头已带着未上线的一批**：这期间 knowbench 要急修，不能单发（会把 0051 带上去，而线上 knowbase、knowfeed 不认要数的需求，第 0 步会失败），要么三个应用一起发，要么把修复单独拆出来。

## 二、同步与提交的规矩（这两天定的）

- 叫法：所有者 WSL 是**本地**，云端容器是**远程**。
- **提交即推**：做完一项就提交并推；应用仓先子仓、后父仓；sunmoonun 推到能快进的全部工位分支。推不上去（不能快进）就停下说，**不 rebase、不强推**。
- 工位分支已统一为同名（`qwen` 等七条），`work/*` 已归档（本地清理，`7d3d8e58`）。
- `human-remote.sh`（账 64，所有者 11-06 定「停」）：提交、推送之前一次查完各仓，远端有本地没有的提交就整次停下；只有本地改动时提示先跑 `human-local.sh` 拉下来，两边分叉时把输出贴给远程助手。远程用 26 个假仓跑过六种情况。
- 不报提交号、做完说「推好了」；中文回答；密码表照 AGENTS.md 不显示、不代填。

## 三、做完并已上线的（#85，`release-20261106-1`）

按卡 [qwen-018](../sync-cowork/requests/qwen/2026-11-06-qwen-018-next-batch/request.md)，四个应用成组发；回执 [qwen-018](../../scripts/results/qwen-018.20261106-2049.md)。#84 失败一次：knowbench 加了迁移 0039，部署声明的期望版本没改（我写卡时漏了），Qwen 改了声明后 #85 成功。**以后后端加迁移，同一批改部署声明的 `expected_schema_revision`。**

| 账 | 修了什么 |
| --- | --- |
| 184（高） | knowfeed 派发把 `daily_cap=0` 当成用完，Wind 确认后的查询派不出去；改成和领域层同一个判断 |
| 180 | knowbase 版本表格式接口上线，knowlab 挑数据不再必 404 |
| 186 | 一份表格读不出表轴整次挑数据失败：CSV 先 UTF-8 再 GB18030、xlsx 缺 `r` 按顺序推列；knowlab 把读不出的那份按「表轴未知」带过去 |
| 185 | 清除资料不再删冻结给专家的数据 |
| 188 | PDF 首页识别超时真正起作用 |
| 190 | knowbase 一条断言跟上「确认不等于在取」 |
| 182 | knowlab 登录回跳补上网页各栏、去掉 `/data`；删两份孤立密文（`knowbase-user-data-import-service.sops.yaml`、`storage.sops.yaml`） |
| 183 | 一步 30 分钟没有可见进展时在时间线提醒（不停、不改时限） |
| K29 | knowlab 测试由本人管理（迁移 0039） |

上线后 Qwen 核过：四个应用正常、迁移 0039 完成、K29 两项对账 0、日志无错。**还差所有者的页面验收**（作者挑表格与 GBK 的 CSV、knowlab 停测试、各栏重新登录回原处）与真实 Wind 取数验收。

## 四、做完、未上线的

### 4.1 SDD 0050：固定和动态的计划用同一种格式，交给同一套执行

- 设计：[0050](../design/SDD/modules/0050-fixed-expert-as-plan.md)。所有者 11-07 指正了两处说法，已改：固定专家本身就是计划，只是换成同一种格式记一份；**排计划也是执行**——动态专家的执行 = 排计划 + 按计划做，收成一路的只是「按计划做」。
- 做法：固定专家受理通过时，平台按作者顺序写一份计划回执（`knowbench/fixed-plan/v1`，不调模型、不开尝试、不进时间线），之后「按计划做」只认回执；成果名仍是作者起的名字。
- 开关是账号名单 `WORKBENCH_FIXED_AS_PLAN_OWNERS`（没有单独测试环境，所有者定先只放本人），部署声明里已写所有者本人的 subject。名单外、动态专家、已在跑的委托都不受影响。
- 等价验收：十二个场景开关前后逐项相等（模型每轮输入逐字、尝试、成果、状态、事件、问题、交回），连跑八次稳定，故意改坏会失败。
- **还没完全同一套**：「按计划做」里还有 10 处固定、动态分开走（为了等价刻意留：缺输入怎么停、第 0 步没数据工具、收尾指向与交回字段 4 处；「覆盖」验收取上游、工具调用核元数据、工具审批收紧 5 处；测试取值 v1/v2 1 处）；另 13 处是新老路判断，旧路退役后消失。要真正一套，得逐条定固定专家改不改成动态的做法。
- 代码：knowbench-backend `372ce8e`（生成与读回）、`a912a918`（执行核心与开关）、`5e2ceaf5`（十二场景）、`38c6c1f1`（改成名单）。

### 4.2 SDD 0051：数据需求只说要什么，取法归供给端

- 设计：[0051](../design/SDD/modules/0051-source-order.md) 第二节；决定见 [decisions](../design/decisions.md) 11-07 那条。所有者原话：「需求和供给不一致，应该不是一个好的做法」「需求不能决定取法，到了供给端才分」；口径不写默认当期原始披露；不另建抽数引擎（0047 已有抽表）；取回的先进 knowbase、再照现有状态通知让需求方来取。另 11-06 定 Wind 优先、公告原件保底。
- 需求写：主体、期间、科目表编码（如 `IS.REVENUE`）、口径（合并/母公司、全年/半年/单季/年初至今、当期原始披露/最新调整后）。不写渠道、不写怎么取。
- 已写：
  - knowbase：`data-request/v1` 加 `FactRequest`（契约文件改成 oneOf 两种，加法）；解析时在本人能用的资料的表格读法里找口径对得上的标准化层行，按披露版本挑，挑不出不猜，缺的交 knowfeed；确认入口分支认要数的键；`user-data/v2` 跟着加法重生成。knowbase-backend `d8ee10b8`、`3b23eb52`。
  - knowfeed：需求项照用户确认的原样留住键，自己推「落在哪份定期报告里」给渠道匹配；巨潮照常认那份报告；Wind 只认渠道配置 `fact_fields` 里有对照的科目（现在没有，所以不认）；要数的项必须要表格读法。端到端测过（假渠道）。knowfeed-backend `d0552d13`。
  - knowbench：第 0 步 `request_data` 收 `metrics`（科目编码，查 `describe_items`）；提示不再叫模型先找供应商、点名 Wind；存下来读回、用户改过都认两种；网页数据清单认要数的条目（这一版只能确认或去掉，不能改主体期间）。knowbench-backend `d6257003`、网页 `c8f70622`。
  - 三个消费方的契约锁都跟上（knowbench、knowlab 照提供方加了 FactRequest 模型，锁测试逐字段比）。
- **没做**：
  - **Wind 的指标对照与回包解析**。W0 查明 Wind 财务工具 `get_stock_fundamentals` 按自然语言问（`question`），回包结构、单位、重述历史都没核实；所以对照不是「科目 → 字段码」一张表，要「科目 → 问法」＋把回包解析成数，得等核实后才写得准。
  - **prematch v2**：现在要数的条目不显示预计渠道与时间。

### 4.3 SDD 0052：跨应用契约三条做法

- [0052](../design/SDD/modules/0052-contract-hygiene.md)。
- K29 浏览只认标记列（#85 后对账 0 才动）：knowbench-backend `7299b88`。
- 调用方模型与提供方 schema 逐字段比对：比对辅助 `tests/schema_parity.py`（knowbench、knowlab 各一份）；当场查出 knowbench 目录模型「接什么」比 knowmart 严（会拒掉合法目录条目），已改成 `DirectoryScope`（`e9cf02f9`）；knowlab 四样一致（`186c3720`）。
- 契约退役表：写进 knowbench、knowlab、knowfeed 三个父仓 `contracts/README.md`；现在没有能直接退的（几版按专家形态并存）；dynamic-methods v1、v2 是可退候选。

## 五、发版卡的状态

| 卡 | 状态 |
| --- | --- |
| [qwen-018](../sync-cowork/requests/qwen/2026-11-06-qwen-018-next-batch/request.md) | 已发（#85） |
| [qwen-019](https://github.com/sunmoonlion/sunmoonun/blob/614763f985a74ddbb2c8109391feb2af211a22a0/docs/sync-workertree/inbox/qwen/2026-11-06-qwen-019-fixed-expert-as-plan.md) | 作废，由 qwen-020 取代 |
| [qwen-020](../sync-cowork/requests/qwen/2026-11-07-qwen-020-facts-and-fixed-plan/request.md) | **暂不发**（所有者 11-07：「那就没有必要发这版啊」）。等 Wind 指标对照做好后，knowbase、knowfeed、knowbench 三个一起发；卡里的号到时要重核 |

## 六、等所有者定的

1. **要不要写本地卡核实 Wind 的回包**：让 Qwen 用本地 Wind 问茅台保底题的营业收入、归母净利润、经营现金流 2023—2025，把回包原样记下来（结构、单位、口径、重述）。有了这个，远程才能写 Wind 的对照与解析，0051 才有用。
2. **「按计划做」里那 10 处**（4.1）：逐条定固定专家改不改成动态的做法。
3. **账 191**：作者设了动态规划后改不回固定，撤回时各方法的选择条件是删还是留作草稿。
4. **dynamic-methods v1、v2 退不退**：前提是新的动态专家一律写能力声明（v3）。
5. **0050 旧路退役**：名单放开、线上没有走旧路的委托、你批了再删。
6. **#85 的页面验收**（第三节末）。

## 七、远程环境的坑（下次在容器里做要知道）

- 各后端测试环境装在 `app/.venv-remote`（锁文件指向清华源，远程连不上，按锁的版本从 PyPI 装；没改锁）。knowbench 的 pyright 要用临时配置指向 `.venv-remote`。
- 测试库是容器里自装的 PostgreSQL 16（端口 55432，数据在 `/var/lib/postgresql/remote-test`）。**容器一重启它就不在了**，要先 `pg_ctl ... start`；连接串：knowfeed、knowbase 用 `DELIVERY_TEST_DATABASE_URL=postgresql+asyncpg://t@127.0.0.1:55432/<x>_tests`，knowbench 用 `AGENT_TEST_DATABASE_URL=postgresql://t@127.0.0.1:55432/knowbench_tests`。
- 远程 Node 是 v22（包要 24），网页的检查分步跑：`tsc --noEmit`、`eslint`、`node scripts/check-i18n.mjs`、`vitest run`、`next build`。
- 远程一直失败、和改动无关的几条：knowbench 2 条（run data contract 快照、专家入口进度）；knowbase 2 条（对象存储 CA、knowbench recheck 消费方）；knowlab 要别的解释器或 `uv run` 的几条；sunmoon-link 6 条 cli（要先构建 dist）。
- 推 tag、删远端分支会被代理拒（403）；要删分支只能在本地做。

## 八、接手第一步建议

1. 本地 `~/worktrees/qwen/sunmoonun/docs/sync-cowork/sync/sync.sh pull` 把这批拉下来。
2. 看第六节，先定第 1 条（Wind 回包核实）——它决定 0051 什么时候能发。
3. 不要单发 knowbench（第一节末）。
