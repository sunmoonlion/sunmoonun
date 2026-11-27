# agy 回执

- 对应请求：../request.md
- 本轮：第1轮
- 实际检查版本：
  - `knowmart-app`：`bdb7e9d79beebc4eae423c510f0587c17cb63c08`（基线 `812f9995b8847fc4610542ddc5f12fff90bdbbcf`，子模块 `knowmart-web-frontend` `7bafcc75bad99acbf90c8e03f06badbf98c0284b` 与 `knowmart-admin-frontend` `6badf80be1d4aecd831bd02581f2af45300c4445` 不变）
  - `knowmart-app/knowmart-backend`：`7ae8eb8c089d4f57b49deacaa017fcbd468ed080`（基线 `fd162a5db8dc05eb2cfa6474ece319908ae9f7cd`）
- 结论：通过（数据库迁移 `20261127_0022`、需求响应与成交回归及升降级约束保护均独立复验通过）

## 发现

- F01（无阻塞问题，父仓指针与单一线性迁移链核查通过）：核对 `knowmart-app`（`bdb7e9d79beebc4eae423c510f0587c17cb63c08`）仅更新 `knowmart-backend` 指针至 `7ae8eb8c089d4f57b49deacaa017fcbd468ed080`；`20261127_0022_formal_market_trade_kinds.py` 的 `down_revision` 精确指向 `20261126_0021`，并在 `test_kernel_invariants.py` 纳入线性迁移链守卫。
- F02（无阻塞问题，需求响应、成交幂等、评价归属与降级原子阻断核查通过）：`0022` 迁移将 `trade.ck_trade_kind` 与 `demand_response.ck_demand_response_listing` 的允许值统一扩展为 `'expert', 'knowledge', 'formal_expert', 'formal_tool'`（同时保持 `demand_response` 无挂牌时两列同空、带挂牌时两列同时非空的完整性约束），与 `0021` 已建的部分唯一索引 `ix_trade_buyer_formal_ref` 闭合一致；卖家以 `formal_expert` 或 `formal_tool` 响应需求、买家选定并获取后，需求关闭、重复获取同一条目仅保留一笔交易、评价准确归属到被获取的正式条目；`downgrade()` 依赖 PostgreSQL 事务型 DDL 对存量行执行检查约束校验，存在 `formal_expert` / `formal_tool` 记录时拒绝降级并原子回滚。

## 验证

- 验证环境：本地 `wsl-dev`，使用 `git worktree add --detach` 检出 `7ae8eb8c089d4f57b49deacaa017fcbd468ed080`，在本机 PostgreSQL 16 容器建立两个独立临时测试库（`agy_card3_knowmart_pytest_tests` 与 `agy_card3_knowmart_mig_tests`，凭据取自本地测试容器环境变量，验证后销毁）。
- 已执行并通过：
  1. `.venv/bin/ruff check .`：全部通过；
  2. `DELIVERY_TEST_DATABASE_URL=<独立 PostgreSQL 16 *_tests 库> .venv/bin/python -m pytest -q tests/test_pr5_formal_market_unification.py tests/test_market_db.py tests/test_shop_db.py tests/test_kernel_invariants.py tests/test_schema_readiness.py tests/test_trade_granted_db.py`：**72 项全部通过（39.67s）**，参数化覆盖正式专家（`29.00`）与正式工具（`12.50`）响应需求、选定成交、需求关闭、重复获取单笔幂等及评价归属；
  3. 独立迁移演练库复验四项要求：先执行 `alembic upgrade 20261126_0021` 并插入存量 `knowledge` 交易 → 执行 `alembic upgrade 20261127_0022`，核实旧交易保留且插入未知类型 `invalid_kind` 被 `ck_trade_kind` 拒绝 → 在仅有旧类型交易时执行 `alembic downgrade 20261126_0021` 再 `alembic upgrade 20261127_0022` 往返成功 → 插入 `formal_expert` 交易后执行 `alembic downgrade 20261126_0021`，核实降级报错中止、`alembic_version` 仍为 `20261127_0022` 且新旧 `2` 笔交易均完整保留。
- 需现场验证事项：后续合入目标运行环境并执行 `20261127_0022` 迁移后，使用已上架正式方法完成一次线上需求响应与获取冒烟核对。

## 交回

- 评审性质：只读代码评审与独立 PostgreSQL 16 真库复验，未修改任何被评代码，未切换主工位分支。
- 尚待处理项：代码层面无待修订缺陷；保留部署升级后的线上冒烟验收。
- 提交与同步状态：本回执已提交本地 `wsl-dev` 的 `luna` 分支、未推送（执行 `sync.sh push sunmoonun` 时因 `sunmoonun` 工作区另有他人未提交改动被脚本预检拦停，按协作规范未夹带他人改动；待主工位处理未提交项后推送，另一端尚未更新）。
