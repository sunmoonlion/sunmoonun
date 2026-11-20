# 评审回执：正式方法市场获取与依赖交付复核

- 请求：[request.md](../request.md)
- 轮次：1
- 核对提交：
  - 工作位置：本地（`wsl-dev`，`/home/zymun/worktrees/luna`，分支 `luna`；KnowBench 后端按 `56cdbcb` 干净导出快照实测）
  - KnowLab：`778c023`（后端，基线 `eb22655`）、`66e7d14`（网页，基线 `e488d06`）、`c47e190`（应用及提供方契约，基线 `a498ed0`）
  - KnowBench：`56cdbcb`（后端，基线 `f3268ee`）、`5daf4bc`（应用及孵化契约锁，基线 `5999c3e`）
  - KnowMart：`090da88`（后端，基线 `b5f83b2`）、`bbc1405`（应用，基线 `f1b5653`）
- 结论：**通过（无阻断项，附 3 条代码完善建议）**。待办第 5 项（接入方案 §17.6 第 7 项）的指定版本上架审核、买方唯一获取、回环跨服务字节级 Skill 交付与嵌套私有权限隔离已完整打通，满足本地开发候选标准。

## 发现

### F01 [info] 4 项复验范围核查结果

1. **包身份去耦与四次独立核权**（`knowbench-backend/app/app/domain/workbench/skill_package.py:160-170+`、`formal_methods.py:234-340`、`knowmart-backend` `services/market.py`）
   - `skill_manifest_digest(files)` 对按 `path` 排序后的 `(path, size, sha256, media_type)` 生成 `sha256:` 内容清单摘要，与 ZIP 压缩时间戳及条目顺序无关，同一组文件按不同顺序压缩后资产 `digest` 不同但方法 `source.digest` 一致。
   - `delivery_files(files, contents)` 按清单逐文件路径、字节长度与 SHA-256 严格比对底层 `workbench_skill_files` 字节；篡改 1 字节或任意路径即拒绝交付。
   - 申请上架（`submit_formal`）、运营审核（`review_formal`）、买方获取（`acquire_formal`）与内部交付（`/formal-methods/listings/{listing_id}/delivery` -> `FormalMethodDelivery` -> `market_delivery`）均实时复查来源许可（含 `rights.deliver` 与 `expires_at`）、冻结版本、`delivery_digest`、作者所有权与停用/撤权/主体/类目资质。

2. **验证回执、来源交付条款与嵌套权限边界**（`knowlab-backend` `services/formal_methods.py`、`domain/knowbots/formal_method_admission.py`；`knowbench-backend` `formal_method_catalog.py`、`formal_methods.py`）
   - KnowLab 在提交冻结与模型校验阶段要求公开 Skill 方法必须带有非 `pending` 的 `delivery_terms` 且存在真实 `execution` 回执；KnowBench `FormalExecutions` 与 `FormalMethodCatalog` 仅在全部用例通过且匹配未过期的 `BusinessCoverageReview` 时签发 `business` 检查并清空 `uncovered`。
   - 嵌套私有方法仍不可直接通过市场交付路径放行（`test_nested_qualified_methods_preserve_each_call_and_private_registration` 验证仅持私有执行记录时 `delivery` 拒绝）；真实宿主运行 MCP 样例的审批、封存及公开候选登记已由 `test_market_candidate_uses_real_execution_and_current_review` 实测覆盖。

3. **并发唯一获取、普通撤架 vs 运营驳回/资质失效与字节级原文保真**（`knowmart-backend` `20261120_0015_formal_method_acquisition.py`、`services/market.py`、`repositories/market.py`、`domain/market.py`、`external/formal_method_delivery.py`）
   - `formal_method_listing` 以 `(owner_subject, method_id, version)` 建唯一约束，买方获取表 `formal_method_acquisition` 以 `(listing_id, buyer_subject)` 为复合主键并通过 `ON CONFLICT DO NOTHING` 保证并发幂等唯一性。
   - 普通 `withdrawn` 停止浏览器新买方获取，允许已购买方继续内部取包（`allowed_states = ("listed", "withdrawn") if runtime else ("listed",)`）；运营驳回（`rejected`）、关店或主体/类目失效则立即阻断取包；浏览器端获取响应明确剔除 `"package"`，仅返回版本引用与 `skill_dependencies` 的来源/许可声明。
   - `FormalDeliveryIn` 与 `DeliveryDocument` 显式配置 `str_strip_whitespace=False` / 未裁剪空白，通过 `scripts/local-integration/formal_market_delivery.py` 在双后端独立 PostgreSQL 16 + 回环 HTTPS 上验证：`SKILL.md`、`NOTICE`（精确保留尾部 `\n` `"原声明\n"`）与 `assets/demo.bin`（`bytes([255, 0])`）逐字节无损交付。

4. **0015 迁移与提供方/消费者契约同步**（`knowlab-web-frontend/app/contracts/formal-methods.ts`、`knowlab-backend` & `knowbench-backend` `test_kernel_invariants.py`）
   - KnowMart `20261101_0014 -> 20261120_0015 -> 20261101_0014 -> 20261120_0015 (head)` 升降级往返通过；KnowLab 提供方 Schema 与 KnowBench 消费锁、KnowLab 网页 Schema 已同步对齐。

## 代码合理性评价与完善建议（非阻断）

整体架构边界清楚、契约校验严谨，尤其对表单裁剪导致 `NOTICE` 尾换行丢失的规避与容器摘要/内容摘要解耦做得很到位。提出以下 3 条非阻断完善建议：

1. **KnowMart `services/market.py`（`submit_formal` / `review_formal` / `acquire_formal`）在持有数据库事务与 `FOR UPDATE` 行锁期间等待跨服务 HTTP 请求（建议在待办第 12 项/高并发前重构）**：`submit_formal`、`review_formal` 与面向买方的 `acquire_formal` 在调用 `self.repo.formal_listing(listing_id)`（内部使用 `.with_for_update()`）之后，直接在同一个 `async with self.repo.transaction():` 块内通过 `await self._formal_version(...)` 请求 KnowBench HTTP。特别是 `acquire_formal`（即使读/获取同一方法也加排他行锁）会将并发买方请求完全串行化在跨服务网络 RTT 上，一旦 KnowBench 抖动还会长时间占用 DB 连接池。建议改为：先无锁读取快照并完成 KnowBench 远端核验，再开启短事务加锁复核上市状态与 `delivery_digest` 未变并落库获取记录。
2. **KnowBench `formal_methods.py` `business_review` 存在重叠有效配置时静默返回 `None`**：`return matches[0] if len(matches) == 1 else None` 在配置里出现两条未过期的同一 `(subject, method_id, definition_digest, source_digest, suite_digest)` 审核记录（例如续期配置交叠窗口）时，不会报错或择新，而是静默返回 `None` 导致公开方法被当成缺少业务审查而拒绝交付。建议像 `SourceLicenseCatalog` 在配置加载阶段校验唯一性（重复即显式失败），或明确按最新截止时间/记录版本择一并留痕。
3. **KnowBench `formal_methods.py:289-324` `skill_dependencies` 输出顺序与摘要锁定排序统一**：`locks` 计算使用了 `sorted(documents, key=lambda m: (m.reference.method_id, m.reference.version))`，但 `skill_dependencies`（315-324 行）直接遍历 `documents` 的 DFS 序。虽然去重正确、内容无误，仍建议同样按 `(method_id, version)` 排序输出，确保任意拓扑遍历顺序改动都不会扰动交付清单列表顺序。

## 验证结果与范围边界

- **双服务回环 HTTPS + 独立 PG 16 集成验证（`KB 56cdbcb` + `KM 090da88`）**：
  - `python3 scripts/local-integration/formal_market_delivery.py`：**`Verified one acquisition and three byte-identical Skill files.`**（审核前 404 -> 审核 -> 买方获取与幂等重复获取 -> 跨买方 404 -> `SKILL.md` / `NOTICE` / `assets/demo.bin` 原样字节核对全部通过）。
- **KnowLab（`778c023` / `66e7d14`）**：
  - 后端 `.venv/bin/python -m pytest -q tests/test_formal_method_service.py tests/test_formal_expert_visibility.py tests/test_knowbot_incubation_contract.py`：**`24 passed in 0.85s`**；`tests/test_kernel_invariants.py`：**`5 passed in 0.03s`**；Ruff `All checks passed!`；Pyright `0 errors, 0 warnings, 0 informations`。
  - 网页 `pnpm typecheck`、`pnpm lint`、`pnpm check:i18n`（1327 键）、`pnpm test`（**`321 passed (42 files)`**）均通过。
- **KnowMart（`090da88`）**：
  - 后端 `.venv/bin/python -m pytest -q tests/test_market_db.py tests/test_market_routes.py tests/test_kernel_invariants.py`：**`40 passed in 12.60s`**；Ruff `All checks passed!`；Pyright `0 errors, 0 warnings, 0 informations`。
  - Alembic 迁移：`20261101_0014 -> 20261120_0015 -> 20261101_0014 -> 20261120_0015 (head)` 升降级往返通过。
- **KnowBench（`56cdbcb` 干净导出快照 + 独立 PG 16 tmpfs）**：
  - `.venv/bin/python -m pytest -q tests/test_formal_method_admission_db.py tests/test_formal_execution_db.py tests/test_formal_method_routes.py tests/test_formal_recursive_db.py tests/test_knowbot_incubation_lock.py`：**`75 passed, 3 skipped in 169.76s`**（3 项 skipped 因独立快照目录外侧不含 `contracts/knowlab-incubation-lock.json` 与 `knowlab-app`；在完整工作区目录单独重跑 `tests/test_knowbot_incubation_lock.py` -> **`5 passed in 1.55s`**，及 `tests/test_kernel_invariants.py` -> **`6 passed in 0.23s`**）。
  - Ruff `All checks passed!`；Pyright `0 errors, 0 warnings, 0 informations`。
- **范围边界**：使用本地测试身份与测试夹具回执；真实 Skill 孵化执行（第 11 项）、市场分区与普通委托（第 12 项）、线上迁移与服务身份 `method-delivery` 注册仍按计划留在后续里程碑和发布窗口执行。
