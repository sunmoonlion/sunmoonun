# agy 回执

- 复核状态：可收口
- 复核人：agy
- 复核日期：2026-11-08
- 审查范围：
  - `knowbase-app/knowbase-backend` 提交 `2ba0fb6bdf0a1bebcc08fe27f8c40153d10dbc96`（及后续同文件排版的 `HEAD` `c7dc805bdbefe2298b3080be65f55769ca6d14cd`）
  - 关联跨仓调用点：`knowlab-app/knowlab-backend/app/app/application/services/knowbot_deliveries.py`、`knowmart-app/knowmart-backend/app/app/application/services/knowbot_service.py`

## 结论

通过。`2ba0fb6b` 准确修复了第 23 条（专家作者绑定已购可转售数据后，因 `_check_item` 的 `frozen_binding` 分支按 `material.owner` 原卖家查询 `user_data_use` 导致永远报 `403 not_bound` 的阻断缺陷）。授权校验现改为按 `(material.id, ref, pin.version_no)` 反查冻结记录的 `(binder, scope)`，再以 `beneficiary != binder` 判定是否向作者以外的人提供服务，同时 `GrantItem.content_owner` 仍保持 `material.owner` 原所有者不变，职责边界清晰。

以下逐项回复复核要点，并附 1 条关于 `binding_states` 在「原卖家删架后对已上架专家巡检影响」的边界观察供参考（不阻塞本单收口）。

---

## 逐项核对结果

### 1. `_check_item` 的 `frozen_binding` 分支（`user_run_service.py:1465-1484`）

- **情况 A（作者绑定自己上传的数据，`binder == material.owner`）**：
  - `self.runs.frozen_binding(material.id, ref, pin.version_no)` 查出 `(ALICE, {"license": ...})`。
  - 作者自测/自用时 `beneficiary == binder`，放行；他人在集市或公开专家调用时 `beneficiary != binder`，要求 `frozen_license >= via_expert`，与原逻辑完全一致。
- **情况 B（作者 `BOB` 绑定从 `ALICE` 买来的可转售数据，`binder == BOB != material.owner`）**：
  - `freeze_binding`（`user_library_service.py:785-844`）在 `BOB` 交付时已通过 `_resolvable_for(BOB, ...)` 校验了 `BOB` 持有覆盖该版本的有效购买使用权（`h.active and h.covers(version_no)`）及 `license == "sale"`，并以 `subject = BOB` 写入 `user_data_use`。
  - 签发运行授权时，`self.runs.frozen_binding` 按 `(material.id, "expert:<id>@<v>", pin.version_no)` 查回 `binder = BOB`、`frozen_license = "sale"`；无论 `BOB` 本人还是第三方用户 `CAROL` 调用均放行。
  - 放行后构造的 `GrantItem`（`user_run_service.py:1519`）中 `content_owner=material.owner` 仍为 `ALICE`，因此后续 `read` / `read_reading` / `search_pages` / `query_facts` 记录 `UserDataRead.owner_subject` 时仍记在原卖家 `ALICE` 名下，符合「原所有者查看自己资料被读取留痕」的语义。
- **情况 C（作者 `BOB` 绑定从 `ALICE` 买来的只许自用数据，`frozen_license == "self"`）**：
  - `BOB` 本人调用（`beneficiary == BOB == binder`）：放行。
  - 第三方 `CAROL` 调用（`beneficiary == CAROL != BOB`）：因 `license_rank("self") < license_rank("via_expert")` 拒绝，报 `403 license_self_only`。
  - 原卖家 `ALICE` 调用 `BOB` 的私人专家（`beneficiary == ALICE != BOB`）：同样满足 `beneficiary != binder`，被 `403 license_self_only` 拒绝——**这一点比旧代码更严谨**（旧代码写的是 `beneficiary != material.owner`，若 `ALICE` 去调 `BOB` 的自用专家反而会被误放行）。

### 2. `SqlUserRunRepository.frozen_binding`（`infrastructure/repositories/user_runs.py:237-257`）

- 查询条件：`UserDataUse.item_id == material_id`、`UserDataUse.use == use`（即 `expert:<id>@<v>`）、`UserDataUse.version_no == version_no`、`UserDataUse.withdrawn_at.is_(None)`。
- **合法情况是否会出现两个不同 `subject`？不会**：
  - `freeze_binding`（`user_library_service.py:800`）先核验 `if expert_id not in {e.expert_id for e in await self.repo.experts_of(author)}: raise not_found("expert")`。
  - 在 `user_data_expert` 表（`infrastructure/repositories/user_library.py:390-416`）中，`expert_id` 是主键，且 `upsert_expert` 对 `row.owner_subject != expert.owner` 强制报 `409 expert_taken`。
  - 因此同一个 `expert:<id>@<v>` 在业务与存储约束下只可能属于唯一作者 `subject`。`if len({subject for subject, _ in rows}) != 1: return None` 是合理的 fail-closed 防御式校验。

### 3. 同一文件与相邻模块是否还有混用 `material.owner` 与 `binder` 的地方？

逐一核查了请求中列出的 4 个方向：

1. **读取（`read` / `read_reading` / `search_pages` / `query_facts`）**：
   - 走授权条目 `GrantItem.version_no` 读取内容，并用 `GrantItem.content_owner`（即 `material.owner`）写 `UserDataRead`。`reads(subject, material_id)`（`user_run_service.py:678`）是给资料原所有者看读取留痕的，保持 `material.owner` 正确。
2. **清除（`purge_material` / `has_frozen_bindings` / `active_grants_for_others`）**：
   - `has_frozen_bindings(material_id)`（`infrastructure/repositories/user_runs.py:1144-1171`）按 `UserDataUse.item_id == material_id`、`use LIKE 'expert:%@%'`、`withdrawn_at.is_(None)` 查询，**不按 `material.owner` 过滤 `subject`**。因此买家作者冻结的专家绑定同样能阻止原卖家在 `personal_info=False` 时物理真删底层对象，逻辑正确。
3. **`void_frozen` 与 `frozen_used_by_others`（`user_run_service.py:490-510`、`infrastructure/repositories/user_runs.py:952-969`）**：
   - `knowlab` 调用 `void_frozen` 时传入的是专家作者 `author`；`frozen_used_by_others(author, frozen)` 检查 `UserDataRunGrant.beneficiary != author`，并在 `withdraw_uses(author, frozen)` 中按 `author` 撤销冻结用途，没有混用 `material.owner`。
   - `grant_by_confirmation`（`user_run_service.py:252-257`）在 `request.basis == "frozen_binding"` 时校验 `request.basis_ref == resolution.consumer` 后统一走 `self._issue` -> `_check_item`，已一并受惠于本次修复。
4. **`knowlab` 与 `knowmart` 调 `binding_states`（`user_library_service.py:505-597`）**：
   - `knowlab`（`knowbot_deliveries.py:698`）与 `knowmart`（`knowbot_service.py:107, 411`）传入的 `owner` 均为专家作者 `owner_subject`。
   - `binding_states` 内部当 `material.owner != owner` 时查 `holdings_of(owner, material.id)` 并取 `named(owner, basis_ref)`，能正确定位到买家作者名下的持有与冻结记录。
   - **【附带观察，供后续确认】**：在 `binding_states`（`user_library_service.py:553-559, 581-585`）中，当 `material.owner != owner`（作者绑的是买来的数据）且 `holding` 有效时，第 556 行仍按原件的 `material.deleted_at` 判定：
     ```python
     state = "deleted" if material.deleted_at is not None else "live"
     ```
     且第 582 行要求 `state == "live"` 才令 `shareable = True`。
     对于**新发公开交付**（`knowlab` `deliver`），原卖家已删架的资料不允许再绑进新公开版本是符合注释（「`deleted` 删了（作者删、卖家删都算，只影响新的公开用途）」）的；但 `knowmart` 的后台巡检 `check_bindings`（`knowmart-backend/app/app/application/services/knowbot_service.py:400-445`）每 10 分钟对**已上架的在售专家**也调用同一个 `binding_states`，一旦 `b.get("state") != "live" or not b.get("shareable")` 就会把已上架的专家自动挂起（`hold_for_binding("binding_not_live")`）。这与 `purchase` 注释（`user_library_service.py:1201`：「卖家后来删、下架、改低许可，都不影响这条使用权」）及 SDD 0043 §2.2/§2.8（「所有者删了的照旧能读（买家、钉住的测试与专家版本照旧可读）」）存在口径张力：原卖家从自己架上删掉资料，是否应当导致买家已冻结并上架的专家被集市巡检挂起？此点不属本次 `_check_item` 修复范围，建议后续与主理人确认 `binding_states` 在 `basis_ref`（已冻结版本）场景下是否应对买家有效持有豁免原卖家的 `material.deleted_at`。

### 4. 测试覆盖（`tests/test_user_runs_db.py:291-368`）

- `test_frozen_binding_of_bought_data_is_checked_against_its_binder` 已覆盖：
  1. 买来的可转售数据（`sale`）被 `BOB` 冻结到 `expert:fb-1@1` 后，第三方 `CAROL` 凭 `frozen_binding` 获签授权并成功读取；
  2. 买来的只许自用数据（`self`）被 `BOB` 冻结到 `expert:fb-2@1` 后，`BOB` 本人可获签并读取，`CAROL`（第三方）与 `ALICE`（原卖家）均被 `403 license_self_only` 拒绝；
  3. 未冻结的 `@2` 版本被 `403 not_bound` 拒绝。
- **可选补强建议（非阻塞）**：若后续顺手补充，可在该测试末尾加两行验证买家冻结绑定的 `void_frozen`：当 `CAROL` 已获签 `expert:fb-1@1` 时，`world.runs.void_frozen("knowlab", BOB, "fb-1", "1")` 报 `409 frozen_in_use`；而仅 `BOB` 自己获签的 `expert:fb-2@1` 调用 `void_frozen("knowlab", BOB, "fb-2", "1")` 可成功撤销。

### 5. 关于不在 `_check_item` 中加 `await self._covers(binder, ...)` 的决定

- **完全赞同不加 `_covers(binder, ...)`**：
  - 按 SDD 0043 §2.2 与 §2.8，已经交付冻结的专家版本（`frozen_binding`），即使原作者后来从资料架删掉自己的资料（此时非购买型的 `owner` 持有因 `deleted_at is not None` 不再 active），已钉住的专家版本仍须照常可读；若在 `_check_item` 里要求 `binder` 当前仍有 active holding，反而会破坏「作者删架不影响已交付专家版本」的不变量。
  - 对于 M2（违规下架/撤销购买使用权），赞同在 M2 实现撤销持有时联动撤回（`withdrawn_at`）依赖该持有的 `user_data_use` 冻结记录（或对违规原件直接置 `disabled_at`，当前 `_check_item` 第 1435 行 `if not material.usable: raise unavailable("material_disabled", ...)` 已对全员熔断）。

---

## 验证

在 `/home/zym/worktrees/qwen/knowbase-app/knowbase-backend/app` 下串行执行：

```text
$ DELIVERY_TEST_DATABASE_URL="postgresql+asyncpg://tester:***@127.0.0.1:55432/knowbase_tests" \
  uv run pytest -q -p no:cacheprovider tests/test_user_runs_db.py
......................                                                   [100%]
22 passed in 27.48s
```
