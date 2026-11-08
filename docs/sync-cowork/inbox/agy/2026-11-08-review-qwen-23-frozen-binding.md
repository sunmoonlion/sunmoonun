# 审查：冻结绑定按冻结它的作者核（opus-qwen 第 23 条 / 你的 KB-BASE-1）

> 发卡：Opus（远程 qwen 工位），2026-11-08。执行：agy。**只审不改**：不在 qwen 工位改文件，也不在你的 agy 分支上改同一批文件。

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

## 交回

- 审查结论写在你自己的工位：`~/worktrees/agy/sunmoonun/scripts/results/agy-review-qwen-23.20261108.md`。每条写：结论（对 / 有问题 / 建议）、依据（文件:行）、建议的改法。
- 在 agy 分支提交，向所有者报「已提交、未推送」。
- 这张卡由 Opus 收到结论、处理完以后移进 `done/`。
