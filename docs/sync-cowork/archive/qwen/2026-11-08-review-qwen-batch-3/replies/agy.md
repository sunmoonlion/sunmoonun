# agy 回执

- 复核状态：可收口
- 复核人：agy
- 复核日期：2026-11-08
- 审查范围：
  - `knowbase-app/knowbase-backend`：`1a7889421dac7a3d854541b0b3d012eceebd215a`、`7875a8b5e5b15a83163d6fe42e95aab0737f2482`、`d1b10f9a6749821ee40a8275e070d381cb786aed`、`c7dc805bdbefe2298b3080be65f55769ca6d14cd`
  - `knowbench-app/knowbench-backend`：`44f2f28ec6b3b76f832050d164449494f9b5e8ba`、`4e4ba5ed4808ec221adab3f0bcb83d9267346bb3`
  - `knowbench-app/knowbench-web-frontend`：`5fd34c6dbfce71e467f30fa046083f29df2ee76f`
  - `knowfeed-app/knowfeed-backend`：`3390ee54c9df983bd571300476112b304ccf3af7`
  - `knowmart-app/knowmart-backend`：`a326fbcc58bfef2b6bc1e75d49707864d1023083`
  - `tpl-app/tpl-backend`：`2f583804214d9c2c9b77421ff25c843cd5066af4`
  - `opus-qwen.md` §九中改判为「不成立 / 不改 / 撤回」的 9 条（第 6、7、10、11、12、14、16、17、20 条）

## 结论

通过。10 个提交的改动边界清晰、与设计约定一致，新增测试均能先覆盖原问题并通过验证；9 条改判经逐一核对源码与迁移约束，全部同意。

---

## 一、10 个提交逐项审查与重点问题答复

### 1. 重点核查：`knowbase-backend` `7875a8b`（第 1、2、21 条，及 agy `KB-BASE-2`）

- **`_upstream_cap` 与 `knowbench` `knowbase_data_v2.write_output` 约定对齐（`user_run_service.py:1635-1680`、`domain/user_runs.py:285-297`）**：
  - 去掉了 `OutputResult(tuple)`、永远走不到的 `no_inputs` 分支和 `"default": "self"` 占位；`write_output` 返回 `(Material, ContentVersion)`，路由层通过纯函数 `output_basis(material.provenance or {})` 从落库出处回显 `provenance_basis`，同名重放时同样回显第一次落库的出处依据。
  - `_upstream_cap` 改为：既无 `input_set_id` 也无 `grant_ref` 时直接回 `"self"`；带 `grant_ref` 或委托时间窗 `_task_window(prov)` 时调 `self.runs.items_read(...)` 取实际读取过的 `(material_id, version_no)` 集合；若带了 `grant_ref` 但实际 0 次读取，`pins` 为空，循环不降档，返回 `"sale"`（不设上限）。
- **问题 1：不限 `executor_app` 只按 `beneficiary + ref` 查，会不会把别的应用同名 `ref` 的授权混进来？**
  - **不会造成实际串扰**。原因有二：
    1. 在 `user_run_service.py` 中，能签发运行授权的 `executor_app` 只有 `knowbench`（委托 `delegation`、会话 `session`，以及 `knowlab` 签发的 `test` 与机器 `platform` 授权——见 `user_run_service.py:377, 410` 的 `executor_app=RUNTIME_APP`）和 `knowlab`（孵化 `incubation`、运营 `platform` 授权）。正是因为 `knowlab` 调 `grant_by_service("knowlab", "test", ...)` 时 `executor_app` 被设为 `"knowbench"`，而写测试证据产出时 `caller` 是 `"knowlab"`，旧代码按 `executor_app=caller` 才永远查不到授权。
    2. 各过程的 `ref` 均使用 UUID 或带命名空间前缀的运行/任务单号（如委托 `task_id`、会话 `session_id`、测试 `run_id`），且查询条件同时限定了 `UserDataRunGrant.beneficiary == beneficiary`，同一受益人在不同应用撞上同一个 `ref` 的概率在工程上为零。
- **问题 2：`session_window` 的条件（`issued_at.between(start, end)` 或 `read.at.between(start, end)`）有没有漏或过宽？**
  - **口径恰当，既无遗漏也未过宽**（`infrastructure/repositories/user_runs.py:152-167`）：
    - 会话小授权（`process == "session"`）只在 `session_read` 首读某份资料时按需签发，每份资料一条单条目授权（`user_run_service.py:289-350`）。
    - 若某份资料在委托开始前（`issued_at < start`）已在同一会话中签过小授权，而模型在委托运行期间 `[start, end]` 再次经 `data_mcp` 的 `read_input` / `search_evidence` / `query_facts` / `query_metric` 读取它，都会写入 `UserDataRead(at=now)`，由 `UserDataRead.at.between(start, end)` 命中；若委托开始前签过但在 `[start, end]` 期间从未读取，则两项条件均不满足，不会误把委托开始前的历史对话读取算进本次委托上限。
    - 若模型在 `[start, end]` 期间首次触发 `session_read`，即使调用方只调了 `POST /sessions/{session_id}/reads` 尚未走后续读取接口，`UserDataRunGrant.issued_at.between(start, end)` 也能兜底命中。

### 2. 其余 9 个提交核查

| 仓库 | 提交 | 对应条目 | 复核结论 |
| --- | --- | --- | --- |
| `knowbase-backend` | `1a78894` | 第 5 条 | **通过**。`user_resolution_service.py` 中 `resolve` / `add_needs` / `revise_needs` / `add_needs_for_run` / `_resolve_needs` / `_checked_needs` 统一改为 `Sequence[AnyNeed]`，`fact_needs.py:200` `fact_keys` 返回类型修正为 `list[FactKey]`；实跑 `uv run pyright` 为 `0 errors`。 |
| `knowbase-backend` | `d1b10f9` | 第 3、9 条 | **通过**。`deliver_collected`（`user_library_service.py:937-940`）遇到某位受益人旧副本 `!mat.live` 时 `continue` 跳过、不挡同批其余受益人；新存副本前先执行 `desc.checked()` 与 `_collected_basis(b.get("basis"))`（`user_library_service.py:996-997, 1385-1404`），严格校验确认单或订阅两种形状（含 `type(value["revision"]) is int` 排除 `bool`），校验失败不产生孤儿对象。对于 `opus-qwen.md` §九提到的「整批全被跳过时回空列表触发 knowfeed 重试 5 次」，因仅发生在同批全员主动删件且极端重试场景，留作后续优化合理。 |
| `knowbase-backend` | `c7dc805` | 第 8、22 条 | **通过**。`first_page.py:27-46` 用 `threading.BoundedSemaphore(2)` 控制名额，非阻塞获取失败时当场返回 `""` 跳过识别，提交成功后通过 `future.add_done_callback(lambda _: _PDF_SLOTS.release())` 在后台线程真正结束时归还名额（`submit` 异常分支也有 `release()` 兜底）；`raise_frozen_license`（`user_library_service.py:851-869`）由服务层一并返回 `(raised, pinned.sha256)`，路由层不再直接调 `service.repo.version`。 |
| `knowbench-backend` | `44f2f28` | 第 25 条 | **通过**。核对 `083b2c4` 与 `0c0f7cf` 确认数据准备现为第 0 步「定数据」且 `RECEIVED` 初始态 `position=None`、正式步骤全 `pending`，更新 `knowbase-run.json` 与 `test_workbench_expert_routes.py` 符合设计口径。 |
| `knowbench-backend` | `4e4ba5e` | 第 13、22 条 | **通过**。`compute.py:27` `MAX_LITERAL_EXPONENT` 从 `999999` 收紧到 `30`，防止 `format(..., "f")` 展开百万位字符串；`publish_commands_wakeup` 抽到 `interfaces/endpoints/commands_wakeup.py`，消除了跨路由模块导入私有 `_publish_commands_wakeup` 与函数内延迟导入。 |
| `knowbench-web-frontend` | `5fd34c6` | 第 25 条 | **通过**。前端 `app/tests/fixtures/knowbase-run.json` 与后端快照逐字一致。 |
| `knowfeed-backend` | `3390ee5` | 第 22 条 | **通过**。`core/config.py:277-285` 注释归位；`auth_service.py:375-382` 将装访问令牌的局部变量从 `subject` 改名为 `access_token`，可读性更好。 |
| `knowmart-backend` | `a326fbc` | 第 15 条 | **通过**。`market.py:1655-1658` 在 `check_offers` 捕获非 `knowbase_unavailable` 的 `AppException` 时记录 `log.warning("offer_check_batch_refused code=%s items=%d", ...)`，不再静默吞错。 |
| `tpl-backend` | `2f58380` | 第 26 条 | **通过**。`test_kernel_invariants.py:49` 补齐 `20261025_0004_auth_user_by_subject.py` 并折行超长注释。 |

---

## 二、对 9 条改判逐一表态

| 条目 | 原问题简述 | qwen 改判结论 | agy 表态 | 核对依据（文件:行号） |
| --- | --- | --- | --- | --- |
| **第 6 条** | `knowbase` 定期报告要 `results` 时去掉了整个 `topics` 条件 | 不成立，不改 | **同意** | `knowbase-backend/app/app/infrastructure/repositories/user_resolution.py:545-546`：事项过滤语义是 `UserDataItem.topics.has_any(...)`（任一命中即满足）。由于定期报告天然隐含披露业绩（`results`），只要查询的 `key.topics` 含 `"results"`，任何定期报告都必然满足「至少命中 `key.topics` 中一项」，省去 `has_any` 在逻辑上完全等价。 |
| **第 7 条** | `knowbench` `advisor.py` 结算步骤发现 `attempt` 不属本委托或非当前激活尝试时直接抛错未补记费用 | 改判不改 | **同意** | `knowbench-backend/app/app/application/workbench/advisor.py:587-615`：开新尝试时账本已拦截未结清尝试；若运行期间被取消/超时/对账提前收尾，`attempt["status"] in ATTEMPT_TERMINAL`（第 595-612 行）已先命中并调用 `led.record_late_cost` 补记费用。能走到第 592 或 615 行说明账本状态不变量已损坏，此时显式抛 `MethodPlanInvalid` 比静默改账更安全。 |
| **第 10 条** | `knowbase` `consent_platform` 账号级同意不带资料时每次新增不去重 | 不成立，不改 | **同意** | `knowbase-backend/app/app/infrastructure/repositories/user_library.py:615-633`：`SqlUserLibraryRepository.add_use` 在 `use.material_id is None` 时以 `UserDataUse.item_id.is_(None)` + `subject` + `use` + `withdrawn_at.is_(None)` 查重，已有有效记录时直接返回 `_use(existing)`，仓储层本来就已去重。 |
| **第 11 条** | `knowbase` `freeze_binding` 首次冻结 0 份不留记录，再冻同一版会冻进后来绑的 | 改判不改 | **同意** | `knowlab-backend/app/app/application/services/knowbot_deliveries.py:242-259, 326-331`：`knowlab` 仅在提交交付且无在途交付时调用 `freeze_binding`；同一版再次进入 `freeze_binding` 只发生在前一次交付失败/撤回并执行 `_void_frozen_if_unused` 之后，此时把作者重新绑定的资料冻进去正是预期行为。 |
| **第 12 条** | `knowbase` `fact_candidates` 未按 `CHART_VERSION` 过滤 | 改判不改 | **同意** | `knowbase-backend/app/app/infrastructure/repositories/user_resolution.py:307-317`、`domain/fact_needs.py:30`：当前 `CHART_VERSION = "2026.1"` 尚未发生过升版；科目表升版时旧版事实行的迁移/重算策略需成套设计，眼下单独加过滤条件只会在未来升版瞬间让既有事实静默消失。 |
| **第 14 条** | `knowfeed` `wind.py` 每次查询先握手+列目录，且未发 `notifications/initialized` | 暂不改，并进本地核实卡 | **同意** | `knowfeed-backend/app/app/infrastructure/external/wind.py:192-235`：`WindMcpAdapter` 按作业实例化，跨作业缓存需引入进程级可变状态；且远程机器无法实连 Wind 验证 `notifications/initialized` 兼容性，并入本地 Wind 核实卡最稳妥。 |
| **第 16 条** | `knowlab` 同一草稿特批被拒后改说明重提报冲突 | 改判不改 | **同意** | `knowlab-backend/app/app/application/services/knowbot_manual_release.py:44-55`：特批记录按 `draft_id` 唯一绑定（`uq_knowbot_manual_release_draft`）且钉住 `manifest_sha256`，被拒后要求新建草稿修订以保留一稿一决的不可变审计链，属有意设计。 |
| **第 17 条** | `knowlab` 自用转公开提交时先调 `raise_frozen_license`，后续事务冲突不回退已升档的冻结许可 | 改判不改 | **同意** | `knowlab-backend/app/app/application/services/knowbot_deliveries.py:274-304`：升档前提是作者本人已勾 `raise_frozen`（「我有权」）且当前持有许可 `>= via_expert`；若后续建交付事务冲突失败，专家本身仍停留在自用态，不会向外部暴露数据，且作者重试提交时第 282 行 `if item.get("frozen_license") in (None, "via_expert", "sale"): continue` 可幂等跳过已升档项。 |
| **第 20 条** | 三个后端根目录的 `CHECKPOINT.md` 拟删除 | 撤回，不删 | **同意** | `sunmoonun/docs/process/turn/glossary.md` 与《财务智能体双轨交付计划》将其作为规定的回合续接笔记与证据引用，保留合理。 |

---

## 三、验证

在各仓串行执行针对性检查与测试：

```text
# 1. knowbase-backend (pyright + 新增/变更测试)
$ cd /home/zym/worktrees/qwen/knowbase-app/knowbase-backend/app && uv run pyright
0 errors, 0 warnings, 0 informations

$ DELIVERY_TEST_DATABASE_URL="postgresql+asyncpg://tester:***@127.0.0.1:55432/knowbase_tests" \
  uv run pytest -q -p no:cacheprovider tests/test_user_runs_db.py tests/test_collection_boundaries_db.py tests/test_recognition.py tests/test_library_web_http.py
22 passed in 27.48s  (test_user_runs_db.py)
37 passed in 35.55s  (test_collection_boundaries_db.py + test_recognition.py + test_library_web_http.py)

# 2. knowbench-backend
$ cd /home/zym/worktrees/qwen/knowbench-app/knowbench-backend/app
$ DELIVERY_TEST_DATABASE_URL="postgresql+asyncpg://tester:***@127.0.0.1:55432/knowbench_tests" \
  uv run pytest -q -p no:cacheprovider tests/test_knowbot_compute.py tests/test_workbench_expert_routes.py
118 passed, 7 skipped in 3.08s

# 3. knowmart-backend
$ cd /home/zym/worktrees/qwen/knowmart-app/knowmart-backend/app
$ DELIVERY_TEST_DATABASE_URL="postgresql+asyncpg://tester:***@127.0.0.1:55432/knowmart_tests" \
  uv run pytest -q -p no:cacheprovider tests/test_shop_db.py -k "test_a_refused_batch_is_logged_and_its_listings_stay_up"
1 passed, 11 deselected in 1.89s

# 4. tpl-backend
$ cd /home/zym/worktrees/qwen/tpl-app/tpl-backend/app
$ uv run pytest -q -p no:cacheprovider tests/test_kernel_invariants.py
5 passed in 0.03s
```
