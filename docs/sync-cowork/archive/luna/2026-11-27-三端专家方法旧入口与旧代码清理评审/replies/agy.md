# agy 回执

- 对应请求：../request.md
- 本轮：第1轮
- 实际检查版本：
  - `knowlab-app`：`5595ac07db6d6ca1e22a49bff4fd6be60947c706`（清理前 `bd2016b`）
  - `knowlab-app/knowlab-backend`：`8556afb339c1efbce93823f38b737c12ac7eb9a9`（清理前 `61cd7d3`）
  - `knowlab-app/knowlab-web-frontend`：`f73d006235b297a5670ac8c34271eff654afaf72`（清理前 `feca6ea`）
  - `knowbench-app`：`27cd33e7d6dc8a8ab5510d7adfc1c2ab182f2f25`（清理前 `a3dd03e`）
  - `knowbench-app/knowbench-backend`：`4366b5b183b186f37f11c44f75723da47a1c50fc`（清理前 `bff2181`）
  - `knowbench-app/knowbench-web-frontend`：`e6caa45d17c954cb053304013793fe002c1e6b1b`（清理前 `8354811`）
  - `knowmart-app`：`3bb1767436cec760ea665d58df09da17a58d483a`（清理前 `bdb7e9d`）
  - `knowmart-app/knowmart-backend`：`830d5ed854f4d4262442c4c77c065ac8330072ff`（清理前 `7ae8eb8`）
  - `knowmart-app/knowmart-web-frontend`：`36121753fe31a62037d28885ba75e9dbd2508d53`（清理前 `7bafcc7`）
  - `sunmoonun`：`451171e0505c3704e6fe43a9d22d056f65b1b016`（`scripts/local-integration/`）
- 结论：通过（三端旧入口与死代码清理、在途历史任务与历史工作稿接续、当前五要素契约验收及 `B410` 市场回执版本与摘要核对均在指定固定提交上独立复验通过）

## 发现

- F01（无阻塞问题，KnowLab 作者入口收拢、旧接口退役与存量工作稿接续核查通过）：核查 `names/[requestId]/formal-method/page.tsx`、`studio/page.tsx`、`studio/[methodId]/page.tsx`、`formal-method-editor.tsx`、`method-studio.tsx` 与 `knowbot_routes.py`（`71507db`、`f73d006`）：
  1. 旧书签携带 `workdraft / method / run / revision / version / execution` 重定向至 `/studio`，含 `studio_method_id` 的五要素草稿直接打开 `MethodStudioEditor` 并恢复原试跑页签，空工作稿（`revision === 0` 且无保存内容）进入 `MethodStudioHome`，早期已保存的正式工作稿继续按原申请和修订编辑、试跑与冻结，历史冻结版本与回执取证不受影响；
  2. 四框模板、P1–P5 专用编辑器、`expert-from-tool`、`expert-input-binding` 及 `column-check`、`candidate-preview`、`matching-outputs`、`scan-outputs` 四个专用 HTTP 入口均已注销并返回 `404`；对已退役固定包父申请直接请求用户审阅、标记规则已审及发起试跑均被拦截。
- F02（无阻塞问题，当前五要素契约决定试跑内容及前端 Schema 同步核查通过）：核查 `FormalMethodService._prepare` 与 `MethodDraftService._view`、`method-studio.tsx`、`contracts/formal-methods.ts`，当工作稿存在 `draft_contract` 时，试跑与验证强制核对 `MethodDraftV2.to_definition().digest()` 与 `formal_method` 一致，将已就绪草稿改回待确认或变更内容后旧定义与旧回执无法用于验证或冻结新修订；前端 Zod 契约完整解析五类 `V0` 算子参数、`artifact_guard`、`step_batch`、`lens` 输入投影及 `collect_pack` 收集输入。
- F03（无阻塞问题，KnowBench 手工复核派发退役与历史在途任务保留核查通过）：核查 `workbench_routes.py`、`branch_review_route.py` 与 `workbench/review/page.tsx`（`4366b5b`、`e6caa45`），已移除 `branch_review_dispatch.py`、`branch-route-screen.tsx` 及 `/api/workbench/reviews/{run_id}/route-preview`、`/route`、`/execution` 三个手工接口（返回 `404`），同时保留 `review_projection`、`selected_quote` 与 `/workbench/review?task={uuid}` 供已有任务号的在途确认记录继续执行、读取报告和提交所有者决定，并在生产方模型证据缺失、连接撤销、价格变动或 `V0` 替换时阻断后续付费调用；方法与技能中心保持三个业务视图。
- F04（无阻塞问题，KnowMart 独立孵化授权面板退役与统一小店归口核查通过）：核查 `market_routes.py`、`market.py` 与 `incubation-permissions.tsx`（`3a4b9b9`、`830d5ed`、`3612175`），独立授权面板及其读取接口 `GET /formal-methods/incubation-permissions` 已注销（返回 `404`），统一由小店 `owner_formal_listings` 与 `PUT /formal-methods/listings/{listing_id}/incubation-permission` 管理工具孵化授权开放、查看与撤回，跨账号严格隔离；`test_drop_manifest_v1_db.py` 改用历史 v2 样本准确验证迁移与订单保留。
- F05（无阻塞问题，`B410` 市场回执版本与规范化摘要核对通过）：核查 `formal_methods.py` 与 `knowbot_clients.py`（`8556afb`），正式方法自用上架在核对 `method_id / version / digest` 基础上补充 `type(version) is int` 防止布尔值类型混淆；存量动态专家 `KnowmartDeliveryClient.deliver` 新增 `_market_manifest_digest`（与 KnowMart `ManifestEnvelope.canonical()` 对齐默认 `tagline` 及含实际冻结数据 `bindings` 的规范化 JSON 摘要），回执缺少版本、版本不符或摘要不一致时均抛出 `knowmart_contract_invalid`（HTTP `502`），作者端保持已批准未交付状态，使用原 `knowlab-delivery-{id}` 交付单号重试正确回执仅形成一笔有效交付。
- F06（跨工位现场顺手提醒，不属于本卡固定提交问题）：本次按协作规范在独立脱离工作树验证 `8556afb3` 全部通过；同时注意到主工位 `/home/zymun/worktrees/luna/knowlab-app/knowlab-backend` 当前工作区正在继续推进新改动（在 `FormalMethodService._prepare` 新增了 `if current.draft_contract is None: raise BadRequestError("A studio draft is required")`）。提醒 Luna 留意：若该未提交改动旨在拦截已删除的工坊草稿，建议判据限定为 `current.retired_studio_draft`（即 `current.method_id is not None and current.draft_contract is None`），否则 `method_id is None` 的历史正式工作稿接续、`test_formal_methods_db.py` 及 `instruction_author.py --registered-instruction` 会一并被 `400` 拦截。

## 验证

- 验证环境：本地 `wsl-dev`，通过 `git worktree add --detach` 在 `/tmp` 精确检出本卡表格全部固定提交，连接本机独立 PostgreSQL 16 容器临时测试库（`agy_card5_knowlab_tests`、`agy_card5_knowbench_tests`、`agy_card5_knowmart_tests`、`agy_card5_int_kl_tests`、`agy_card5_int_kb_tests`，验证后销毁）。
- 已执行并通过：
  1. `knowlab-backend`（`8556afb339c1efbce93823f38b737c12ac7eb9a9`）：`.venv/bin/ruff check .` 通过；独立 PostgreSQL 16 下 `pytest -q tests/test_knowbot_incubation_routes.py tests/test_pr2_drafts_provenance_board.py tests/test_knowbot_clients.py tests/test_knowbot_experts.py tests/test_formal_method_routes.py tests/test_formal_methods_db.py tests/test_knowbot_creation_service.py tests/test_knowbot_test_outputs.py` **130 项全部通过（8.99s）**。
  2. `knowbench-backend`（`4366b5b183b186f37f11c44f75723da47a1c50fc`）：改动文件 `.venv/bin/ruff check` 通过；启用 `sunmoonun/ci/method_transaction_guard.py` 插件在独立 PostgreSQL 16 下运行 `pytest -q -p method_transaction_guard tests/test_review_decisions_db.py tests/test_reviewer_choices_db.py tests/test_ordinary_strict_review_db.py tests/test_pr4_envelope_v0_frontier_and_intake.py` **19 项全部通过（147.26s）**。
  3. `knowmart-backend`（`830d5ed854f4d4262442c4c77c065ac8330072ff`）：`.venv/bin/ruff check .` 通过；独立 PostgreSQL 16 下 `pytest -q tests/test_market_routes.py tests/test_market_db.py tests/test_pr5_formal_market_unification.py tests/test_drop_manifest_v1_db.py tests/test_shop_db.py` **56 项全部通过（29.72s）**。
  4. 三端 Web（均执行 `pnpm run typecheck`、`pnpm run check:i18n`、`pnpm exec vitest run --maxWorkers=3`）：
     - `knowlab-web-frontend`（`f73d006235b297a5670ac8c34271eff654afaf72`）：typecheck 通过，i18n `1716` 键通过，Vitest **43 个文件、352 项通过、2 项跳过**；
     - `knowbench-web-frontend`（`e6caa45d17c954cb053304013793fe002c1e6b1b`）：typecheck 通过，i18n `1764` 键通过，Vitest **66 个文件、485 项通过、2 项跳过**；
     - `knowmart-web-frontend`（`36121753fe31a62037d28885ba75e9dbd2508d53`）：typecheck 通过，i18n `512` 键通过，Vitest **21 个文件、144 项通过、2 项跳过**。
  5. 跨仓门禁与双后端本地集成演练（基于本卡固定提交 `8556afb3` + `4366b5b1` + `830d5ed8` + `451171e0` 组装的临时隔离工作树，`UV_NO_SYNC=1`）：
     - `python3 sunmoonun/ci/verify-contracts.py`：通过；
     - `instruction_author.py --registered-instruction`：通过（输出登记私有指令、双叶专家与四叶嵌套专家三项冻结摘要）；
     - `formal_market_delivery.py --expert`：通过（输出自用上架工作会话核验及买方两次获取、两次批准与最终产物核验通过）。
- 未运行与依赖条件：真实账号、线上在途数据及发布后的浏览器验收按请求约定归实际发布版本后补记。

## 交回

- 评审性质：只读代码评审与隔离环境全链路复验，未修改任何被评代码，未切换主工位分支。
- 尚待处理项：本卡固定提交无阻塞问题，可进入发布准备；主工位正在继续编辑的工作区改动请参考 `F06` 顺手核对。
- 提交与同步状态：本回执已提交本地 `wsl-dev` 的 `luna` 分支、未推送（执行 `sync.sh push sunmoonun` 时因 `sunmoonun` 工作区另有他人未提交改动被脚本预检拦停，按协作规范未夹带他人改动；待主工位处理未提交项后推送，另一端尚未更新）。
