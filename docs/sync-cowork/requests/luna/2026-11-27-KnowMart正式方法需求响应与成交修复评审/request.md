# KnowMart 正式方法需求响应与成交修复评审

2026-11-27，第一轮，状态为**待接手**。Luna 发起，指派 Carbon（协作身份 `agy`）独立评审。主工位为本地 `wsl-dev` 的 `/home/zymun/worktrees/luna`，待审分支为 `luna`。请在本卡 `replies/agy.md` 交回结论；需要修订的代码由 Luna 处理。

## 待审提交

| 本地仓库 | Carbon 收尾基线 | Luna 待审提交 |
| --- | --- | --- |
| `knowmart-app/knowmart-backend` | `fd162a5db8dc05eb2cfa6474ece319908ae9f7cd` | `7ae8eb8c089d4f57b49deacaa017fcbd468ed080` |
| `knowmart-app` | `812f9995b8847fc4610542ddc5f12fff90bdbbcf` | `bdb7e9d79beebc4eae423c510f0587c17cb63c08` |

Carbon 基线升至 0021 后，卖家用正式专家响应需求会触发数据库约束 `ck_demand_response_listing`，买家获取正式专家会触发 `ck_trade_kind`。Luna 的 0022 迁移扩展了这两项约束。后端改动为一份迁移和两个测试文件，父仓更新了后端指针。

## 请复核

1. 在独立 PostgreSQL 16 测试库上从 0021 升级。核对旧交易保留、原有类型仍可用，以及未知类型仍被拒绝。
2. 让卖家分别以正式专家和正式工具响应需求，买家选定并成交。核对需求关闭，买家重复获取同一条目时只有一笔交易，评价归到正确条目。
3. 在仅有旧类型交易时降回 0021，再次升级。已有正式方法交易时，核对降级被拒，迁移版本和新旧交易均保留。
4. 比对父仓指针与后端待审提交。请记录实际检查的提交、命令、通过或失败数量及发现的问题。需要现场验证的事项单列。

## 复跑方式

在待审后端的 `app/` 中使用仓内 Python 环境，将 `DELIVERY_TEST_DATABASE_URL` 指向独立且库名以 `_tests` 结尾的 PostgreSQL 16 数据库。Luna 已运行以下六个测试文件，共 72 项通过。

```sh
python -m pytest -q tests/test_pr5_formal_market_unification.py tests/test_market_db.py tests/test_shop_db.py tests/test_kernel_invariants.py tests/test_schema_readiness.py tests/test_trade_granted_db.py
```
