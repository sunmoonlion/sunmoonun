# 跨应用契约的三条做法：不手抄、只认存下来的、版本要退役（0052）

> 状态：**草案，等所有者看**（Opus 2026-11-06 写；[接手计划](../../../总纲/opus接手计划-2026-11-06.md)第 10 项，[审查](../../../总纲/luna开发逐文件审查-2026-11-06.md) A4、A5、A6）。三条都不单开一轮，**随相关改动做**；这里先定做法，免得每次各做各的。
> 上位：[架构总纲](../../../总纲/架构总纲.md)第三节「应用与应用之间只经有版本的契约：提供方放 schema，调用方持锁」；[契约专题](../../../project-guide/topics/contracts.md)。

## 一、调用方的模型不手抄（A4）

**现在**：`PublicCapability` 在 knowlab（`domain/knowbots/workdraft.py` 200 行）、knowmart（`domain/knowbots/directory.py` 16 行）、knowbench（`domain/workbench/method_catalog.py` 112 行）各写一份；`PublicExpert` 在 knowmart、knowbench 各一份。锁测试核 schema 摘要，再拿**一份样例**过提供方 schema。样例测不出长度、必填、正则、枚举这些约束有没有走偏：调用方比提供方松，会收下提供方不会发的东西；比提供方严，会拒掉合法的。

**做法**：锁测试加一条**逐字段比对**。把调用方的 pydantic 模型 `model_json_schema()` 与提供方 schema 里对应的那一段都化成同一种形状，逐个属性比下面这几项，有一项不同就失败，失败信息写出哪个字段、哪一项：

| 比的项 | 说明 |
| --- | --- |
| 属性集合 | 两边字段名一样多、一样名 |
| 必填 | `required` 一样 |
| 类型 | `type`（含可空）一样 |
| 约束 | `minLength`、`maxLength`、`pattern`、`enum`、`minimum`、`maximum`、`minItems`、`maxItems` 一样 |
| 多余字段 | `additionalProperties` 一样（都 `extra="forbid"` 时为 false） |

- 不引代码生成器、不加新工具链（`C-R13`）；比对函数写一份放在各后端的测试辅助里（三个仓各一份，几十行，不跨仓共享代码）。
- 先覆盖 `PublicCapability`（三处）、`PublicExpert`（两处）、清单 v3 外层（三处校验）；以后新契约的锁测试照这个写。
- 提供方确实要放宽或收紧时，先改提供方 schema 出新版本，调用方跟锁，比对随之更新——比对失败就是提醒「这次是契约变化，不是随手改模型」。

## 二、K29 只认存下来的列（A5）

**现在**：测试的标记存成了列（`workbench_tasks.pack_source = 'knowlab-test'`、`workbench_sessions.origin = 'knowlab-test'`，新建时写，迁移 `20261106_0039` 回填），浏览查询里又每次现算一遍（knowbench `infrastructure/workbench/repository.py` 98–103 行的 `_test_task`、`_test_session`，用 `EXISTS` 查 `workbench_test_cases` 与会话下的委托）。两个来源迟早对不上，而且是拼 SQL 字符串。

**做法**：分两步。

1. qwen-018 发了以后，本地跑一次对账（只读），看列和现算有没有对不上的：

   ```sql
   select count(*) from workbench_tasks t
   where coalesce(t.pack_source,'') <> 'knowlab-test'
     and exists (select 1 from workbench_test_cases tc where tc.task_id = t.id);
   select count(*) from workbench_sessions s
   where coalesce(s.origin,'') <> 'knowlab-test'
     and exists (select 1 from workbench_tasks tt where tt.session_id = s.id and tt.pack_source = 'knowlab-test');
   ```

   两个都是 0，才做第 2 步；不是 0 就先查是哪些、为什么回填漏了。
2. 两个函数改成只看列（`coalesce(x.pack_source,'') = 'knowlab-test'`、`coalesce(x.origin,'') = 'knowlab-test'`），删掉 `EXISTS`；写测试的地方（建测试委托、建测试会话）各补一条断言「建出来就带标记」，保证以后只有这一个来源。

## 三、契约版本要写退役（A6）

**现在**：调用方持锁的数量 knowbench 15、knowlab 9、knowfeed 4。knowbench 同时持着 author-method v1/v2/v3、test-run v1/v2、manifest v2/v3 等，没有哪一版写了什么时候停；每多一版，提供方、调用方都多一套校验与测试。

**做法**：各父仓 `contracts/README.md` 末尾加一张表，每个持着的锁一行：

| 契约与版本 | 提供方 | 本仓谁在用（代码位置） | 启用 | 退役条件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 例：`knowlab author-method/v1` | knowlab | `…/method_sources.py` | 10-xx | 本仓不再收 v1 的请求，且线上没有钉着 v1 的进行中委托与测试 | 在用 / 可退 / 已退 |

- **退役条件**统一写成两句：① 所有使用方的代码不再读写这一版；② 线上没有还钉着这一版的进行中数据（委托、测试、确认快照）。第 ② 句要写出查哪张表、怎么查。
- **退役顺序**：先各使用方删锁和读写这一版的代码并发版，最后提供方删 schema 和入口；反过来会让使用方的锁测试先坏。
- 提供方出新版本时，在同一笔提交里把旧版那一行的退役条件写上。
- 第一轮先把表填出来（只读整理，不删东西）；哪几版可退，列给所有者批。

## 四、请所有者定

1. 第一节比对放在各仓自己的测试里（三份几十行的辅助函数），不做跨仓共享包，可不可以。
2. 第二节第 1 步的对账随 qwen-018 发后那张卡一起跑，还是另开卡。
3. 第三节的表先由远程整理一版交所有者看。
