# agy 回执

- 对应请求：../request.md
- 本轮：第1轮
- 实际检查版本：
  - `#128` 补发候选（`luna-128-studio-create-delete` 分支）：
    - `knowlab-app`：`7c42f27346ec34b93141c3ab47389eee724b2256`（基线 `c4d4748`，`knowlab-admin-frontend` 保持 `89fe3ac1f6178018186584db7542f11102896381`）
    - `knowlab-app/knowlab-backend`：`b089eb187c3a63d643a91129287c23b6eafe4956`（基线 `7e67b587`）
    - `knowlab-app/knowlab-web-frontend`：`d5b9477ec242db24e2b6bfffb34c0c799c4ba402`（基线 `36c13dae`，含创建修复 `41ac620`）
  - 日常开发线同步提交（`luna` 分支）：
    - `knowlab-app`：`f790c011a8e19256081ac5175140e7c24bad81ec`
    - `knowlab-app/knowlab-backend`：`f4153d8c992ec51f5017e0fcd5dc1e9b4e7024c4`
    - `knowlab-app/knowlab-web-frontend`：`9d3b24a62de7125c935462aafa7bbe9947d98aa2`
- 结论：通过（适用 `#128` 补发 KnowLab API 与 KnowLab Web，库版本沿用 `20261126_0030`；日常开发线草稿删除同步一并核验通过；线上实操验收归发布后现场核对）

## 发现

- F01（无阻塞问题，创建与重开回执映射解析修复核查通过）：核查 `knowlab-web-frontend` 的 `app/lib/knowbots/method-drafts.ts`、`app/components/knowbots/studio-create-form.tsx` 与 `app/components/knowbots/method-studio.tsx`，已将 `projection.public_inputs`、`projection.what_to_return` 由数组契约修正为与后端 `project_contract_state` 一致的按槽位名称映射（`{ [slotName]: { slot } }`），同步读取 `missing_promise_sources`、`draft_contract.unconfirmed_paths` 与受控词表返回的嵌套 `{ group, label }`，并对照后端 `ValueSlot.meaning`（`dict[Name, Text]`）核实槽位键值类型一致；创建成功后按服务端返回的原始 `method_id` 跳转，消除 HTTP 201 落库后客户端解析失败误报 `request_failed` 的问题。
- F02（无阻塞问题，草稿软退役、并发修订保护与冻结出处保留核查通过）：核查 `knowlab-backend`（`b089eb18` 及日常线 `f4153d8`）新增的 `DELETE /api/web/v1/method-drafts/{method_id}?revision={revision}`、`MethodDraftService.delete` 与 `SqlKnowlabRepository.retire_method_workdraft`，强制校验 CSRF、所有者归属及展示修订一致（修订过期返回 `409`）；通过将 `draft_contract` 置空并递增 `revision` 标记 `retired_studio_draft`（`method_id IS NOT NULL AND draft_contract IS NULL`），重复删除幂等返回 `204`，退役后读取与编辑返回 `404`，子草稿自动解除 `parent_gap` 并递增修订保留可编辑，底层 `knowbot_workdrafts` 行继续供已有冻结版本、试跑回执和出处记录引用，且不影响 `method_id IS NULL` 的历史工作稿。

## 验证

- 验证环境：本地 `wsl-dev`，通过 `git worktree add --detach` 在 `/tmp` 建立不影响主工位的临时隔离目录，连接本机独立 PostgreSQL 16 容器临时测试库（`agy_card1_knowlab_tests`，凭据取自本地测试容器环境变量，验证后销毁）。
- 已执行并通过：
  1. `knowlab-backend`（`b089eb187c3a63d643a91129287c23b6eafe4956`）：`.venv/bin/ruff check .` 全部通过；`.venv/bin/python -m pytest -q tests/test_pr2_drafts_provenance_board.py tests/test_five_element_contract_v2.py tests/test_kernel_invariants.py` **15 项通过**；`DELIVERY_TEST_DATABASE_URL=<独立 PostgreSQL 16 *_tests 库> .venv/bin/python -m pytest -q tests/test_method_draft_deletion_db.py` **1 项通过（2.66s）**，覆盖 CSRF 403、跨账号 404、过期修订 409、重复删除 204、退役后读取/编辑 404、同名草稿隔离、子草稿解绑及冻结出处保留。
  2. `knowlab-web-frontend`（`d5b9477ec242db24e2b6bfffb34c0c799c4ba402`）：`pnpm run typecheck` 通过；`pnpm run check:i18n` 通过（`1822` 对称键）；`pnpm exec vitest run --maxWorkers=3` **45 个测试文件、375 项通过、4 项跳过**（含 `studio-create-reply.test.tsx` 与 `method-draft-deletion.test.tsx`）。
- 未运行与依赖条件：未在 `#128` 线上环境执行发版与真实账号浏览器操作（无发布授权；待 Cursor 按审批补发后由 Luna 按请求约定重开“三表核验”并用专门新建的测试草稿完成现场验收）。

## 交回

- 评审性质：只读代码评审与隔离环境复验，未修改任何被评代码，未切换主工位分支。
- 尚待处理项：由 Cursor 按审批更新 `#128` KnowLab API 与 Web 镜像并记录实际镜像与 Flux 修订，随后由 Luna 完成发布后现场核验。
- 提交与同步状态：本回执已提交本地 `wsl-dev` 的 `luna` 分支、未推送（执行 `sync.sh push sunmoonun` 时因 `sunmoonun` 工作区另有他人未提交改动被脚本预检拦停，按协作规范未夹带他人改动；待主工位处理未提交项后推送，另一端尚未更新）。
