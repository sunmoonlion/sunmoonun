# 远程 qwen 工位测试基线（2026-11-08）

> Opus 在远程 `VM-0-13-ubuntu`（43.153.135.74）的 `~/worktrees/qwen` 上跑，对应 `docs/总纲/opus-qwen.md` 第七节第 1 步。目的是在动手修之前记下现在的状态：只跑测试，没改任何代码。

## 测试环境（怎么起、怎么关）

- **数据库**：Docker 容器 `sunmoon-remote-test-pg`，镜像 `postgres:16-alpine`（本机原有）。
  - 只绑 `127.0.0.1:55432`，内存上限 512M，`--restart no`，数据放在卷 `sunmoon-remote-test-pg`。
  - 测试库：`knowbase_tests`、`knowfeed_tests`、`knowbench_tests`、`knowbench_agent_tests`、`knowlab_tests`、`knowmart_tests`、`tpl_tests`。
  - 账号是 `tester`，密码只存在远程 `~/.config/sunmoon-remote-test/pg.env`（权限 600），不进仓。
  - 停：`docker stop sunmoon-remote-test-pg`；起：`docker start sunmoon-remote-test-pg`。
  - 边缘的 `sunmoon-edge-traefik-1`、`sunmoon-edge-frps-1` 两个容器不碰。
- **Python**：各后端在 `app/` 下执行 `uv sync --frozen`。
- **两个地址的写法不一样**，写错了会成片报错：
  - `DELIVERY_TEST_DATABASE_URL=postgresql+asyncpg://tester:…@127.0.0.1:55432/<应用>_tests`。knowfeed 有一个测试会另起子进程、直接用这个地址，必须带 `+asyncpg`。
  - `AGENT_TEST_DATABASE_URL=postgresql://tester:…@127.0.0.1:55432/knowbench_agent_tests`。knowbench 的工作台测试会自己把它换成 `+psycopg` 去跑迁移；带了 `+asyncpg` 会报 595 个 `MissingGreenlet`。
- **跑法**：一个仓一个仓地跑，依次是 `ruff check .`、`pyright`、`pytest -q`，不并发。

## 结果

| 仓 | 提交 | ruff | pyright | pytest |
| --- | --- | --- | --- | --- |
| knowbase-backend | `3b23eb5` | 过 | **13 个错误** | 780 过，9 跳过 |
| knowfeed-backend | `d0552d1` | 过 | 0 | 1107 过，13 跳过（1 个先失败，原因是地址没带 `+asyncpg`；改了以后该文件 10 个全过） |
| knowbench-backend | `d625700` | 过 | 0 | 2043 过，9 跳过，**2 个失败** |
| knowlab-backend | `3f16dc2` | 过 | 0 | 931 过，5 跳过 |
| knowmart-backend | `3248562` | 过 | 0 | 546 过，5 跳过 |
| tpl-backend | `c7cc3f4` | **1 处** | 0 | 373 过，5 跳过，**1 个失败** |
| sunmoonun `scripts/test_switch_test_sync.py` | — | — | — | 28 过（unittest） |

**失败和错误的明细**：

1. **knowbase 的 pyright 13 个错误**：全部出在还没上线的 0051 代码里，涉及 `user_resolution_service.py`、`user_resolution_routes.py`、`fact_needs.py:202`、`user_resolution.py:398`。新加的 `AnyNeed`/`FactKey` 没有贯通各函数签名；`fact_keys` 的返回类型标错了；`expand` 把 `FactSlot` 当成了 key。11-02 那次 pyright 还是 0 错。
2. **knowbench 的 2 个失败**：
   - `tests/test_run_data_contract_db.py::test_actual_http_response_matches_nonempty_data_contract`：返回里步骤的序号 `index` 期望是 1，实际是 0；
   - `tests/test_workbench_expert_routes.py::test_asking_an_expert_from_the_expert_entry`：期望回 `{'step': 1, 'of': 7, 'left': 7, 'title': '定范围'}`，实际回 `None`。

   两条都跟「第几步」的显示有关，和 agy 报告的 KB-BENCH-4 一致。根因修的时候再查。
3. **tpl 的失败**：`tests/test_kernel_invariants.py::test_one_linear_canonical_migration_chain`。账 175 加了迁移 `20261025_0004_auth_user_by_subject.py`，没有同步改迁移文件名清单。ruff 那 1 处是同一个测试文件里的一行超长注释。两处都是 10-25 就有的。

**没跑的**：
- 各前端：要用的时候再装依赖；
- sunmoon-link：要先装 Node 依赖，agy 说的 LINK-2 因此还没核。
