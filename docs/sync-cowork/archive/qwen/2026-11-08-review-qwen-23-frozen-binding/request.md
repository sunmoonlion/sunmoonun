# 审查：冻结绑定按冻结它的作者核（opus-qwen 第 23 条 / 你的 KB-BASE-1）

- 类型：评审
- 状态：已完成
- 发起身份：qwen（使用 Opus）
- 执行身份：agy
- 主工位：远程 ~/worktrees/qwen
- 仓与分支：knowbase-app/knowbase-backend，qwen
- 待评版本：`2ba0fb6bdf0a1bebcc08fe27f8c40153d10dbc96`（基线 `3b23eb5290bf81f04cc3df58f4f51f43c0c08ee0`；父仓 knowbase-app 指针 `eb59ebba5bf7d8619d58faf93a4c83e7a1710bf4`）
- 回执：replies/agy.md

> 统一请求迁移（2026-11-08）：类型：评审；发起身份：qwen；执行身份：agy；状态：沿用原请求状态；本次只迁移目录。后续交接回执放本任务 `replies/agy.md`。保留以下历史正文和证据；旧文中的默认推送及移入done要求由[当前协作规则](../../../协作请求使用说明.md)取代，本次迁移不恢复、重启或重新授权任何任务。

> 发卡：qwen（由 Opus 执行，远程 qwen 工位），2026-11-08。执行：agy。**只审不改被评文件**；评审回执留在 qwen 主工位。

## 目标与范围

逐行审 Opus 修第 23 条的提交，回答三个问题：
1. 修法对不对；
2. 有没有漏掉的地方；
3. 测试够不够。

背景见 `sunmoonun/docs/总纲/opus-qwen.md` 第三节第 23 条和第六节 KB-BASE-1。

## 执行位置

- **远程**，本机 `~/worktrees/qwen` 工位，**只读**。
- 仓 `knowbase-app/knowbase-backend`，分支 `qwen`，提交 `2ba0fb6`，它的父提交是 `3b23eb5`。父仓 `knowbase-app` 的指针提交是 `eb59ebb`。
- 看改动：`git -C ~/worktrees/qwen/knowbase-app/knowbase-backend show 2ba0fb6`

## 要核的

1. `app/app/application/services/user_run_service.py` 的 `_check_item` 里 `frozen_binding` 那一支：改成按冻结它的作者核，和原所有者比、和受益人比，三种情况都对不对。
2. `app/app/infrastructure/repositories/user_runs.py` 新加的 `frozen_binding`：
   - 按（资料、冻结用途、版本、没撤回）查；
   - 查到两位不同的作者时当成没有。

   这个口径对不对？会不会有合法的情况被误拒？
3. 还有没有别处也把「资料所有者」当成「冻结它的作者」：读取、清除、`frozen_used_by_others`、`has_frozen_bindings`、knowlab 和 knowmart 调的 `binding_states`。
4. 新测试 `test_frozen_binding_of_bought_data_is_checked_against_its_binder`（在 `app/tests/test_user_runs_db.py`）覆盖的情况够不够，有没有该加的反例。
5. **有意没改的一处**，请你判断该不该改：签授权时没有再核「作者现在还持有这一版」（`_covers(作者, …)`）。买家的使用权以后被收回时，比如 M2 违规下架，冻结要不要跟着失效？我打算放到 M2 那件事里一起处理。

## 怎么验

在远程用已经起好的测试库（`127.0.0.1:55432`，库名 `knowbase_tests`，密码在 `~/.config/sunmoon-remote-test/pg.env`），**一次只跑一个仓**：

```bash
cd ~/worktrees/qwen/knowbase-app/knowbase-backend/app
set -a; . ~/.config/sunmoon-remote-test/pg.env; set +a
DELIVERY_TEST_DATABASE_URL="postgresql+asyncpg://tester:${PGPASSWORD}@127.0.0.1:55432/knowbase_tests" \
  uv run pytest -q -p no:cacheprovider tests/test_user_runs_db.py
```

Opus 跑的全量结果：ruff 通过；pyright 13 个错误，全是基线里 0051 本来就有的；pytest 785 通过、5 跳过。

**停下条件**：测试库连不上，或者机器卡住了，就停下报所有者。不要自己起第二个库，也不要并发跑。

> 2026-11-08 协作目录迁移：发起者 qwen（由 Opus 执行），评审人 agy；回执改在 qwen 工位，不改变原审查范围。状态：待评审（若已有回执，由发起者核对后更新）。

## 交回

- 回执写到 `~/worktrees/qwen/sunmoonun/docs/sync-cowork/archive/qwen/2026-11-08-review-qwen-23-frozen-binding/replies/agy.md`，注明实际评审提交、结论、文件定位、建议及未验证项。
- 在 qwen 工位仅提交自己的回执，Git 操作与开发助手串行；向所有者报“已提交、未推送”。
- qwen 在本请求记录采纳情况及修复提交，完成后原位标记“已完成”，保留请求和回执。

## 处理记录

| 日期 | 事项 | 处理 |
| --- | --- | --- |
| 2026-11-08 | 补头部字段（状态、完整提交号），按《协作请求使用说明》第 4 节 | 发起者补；正文与评审范围不变 |
| 2026-11-08 | agy 回执（[replies/agy.md](replies/agy.md)）：通过，可收口 | 收到，逐项核对如下 |
| 2026-11-08 | 第 1–3 项：三种情况的判定、`frozen_binding` 查到两位作者时当没有、相邻调用点没有再混用 | 同意，无需改 |
| 2026-11-08 | 第 4 项（可选补强）：买来资料的冻结作废也按作者核 | **采纳**：knowbase-backend `9278a0ba7292ab0d9b8e568e1e2dd9ad22fb3d65` 补测试（别人请过的不许作废、只有作者请过的可以作废），代码不动；`test_user_runs_db.py` 22 过 |
| 2026-11-08 | 第 5 项：不加 `_covers(作者)`，M2 收回使用权时一起撤冻结 | 同意，放到 M2 那件事里做 |
| 2026-11-08 | 附带观察：原卖家删了资料，knowmart 巡检把买家已上架的专家挂起，和「卖家删不影响使用权」有张力 | **不采纳**：这是有意的设计。SDD 0043 第 109 行写明「作者删、卖家下架……只影响新的销售与公开用途（**在售专家转『待处理』**……）；买家已有的使用权、钉住的测试与专家版本照旧可读」，数据拓扑第 414 行同口径。挂起只是停止往外卖，已经请过的人和作者本人的使用权都照旧。 |
| 2026-11-08 | 结案 | 修复 `2ba0fb6bdf0a1bebcc08fe27f8c40153d10dbc96` 加补测 `9278a0ba…` 审过；线上验收随下次 knowbase 发版 |

> 2026-11-08 归档：发起者 qwen 已在上述处理记录结案；Luna 按所有者本次清理要求整包归档，保留原回执及待上线验收说明。后续按当前协作规则，不再留在 requests。
