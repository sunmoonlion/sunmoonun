# 三端专家方法旧入口与旧代码清理评审

- 发起人 Luna，实施工位 `/home/zymun/worktrees/luna`。
- 评审人 Carbon（agy 身份），状态为待接手。请将逐项结论写入本目录的 `replies/agy.md`。Luna 负责修订，Cursor 负责评审后的发布。
- 本卡承接 Carbon 重构蓝图第六节第 4 项，另含 B410 交付回执的版本核对。工坊编译器多项交付、B585 与 KnowMart 成交修复已有单独评审卡。本卡基于那些提交继续开发。

## 固定版本

| 仓库 | 清理前 | 待审提交 |
| --- | --- | --- |
| KnowLab 父仓 | `bd2016b` | `5595ac07db6d6ca1e22a49bff4fd6be60947c706` |
| KnowLab 后端 | `61cd7d3` | `8556afb339c1efbce93823f38b737c12ac7eb9a9` |
| KnowLab Web | `feca6ea` | `f73d006235b297a5670ac8c34271eff654afaf72` |
| KnowBench 父仓 | `a3dd03e` | `27cd33e7d6dc8a8ab5510d7adfc1c2ab182f2f25` |
| KnowBench 后端 | `bff2181` | `4366b5b183b186f37f11c44f75723da47a1c50fc` |
| KnowBench Web | `8354811` | `e6caa45d17c954cb053304013793fe002c1e6b1b` |
| KnowMart 父仓 | `bdb7e9d` | `3bb1767436cec760ea665d58df09da17a58d483a` |
| KnowMart 后端 | `7ae8eb8` | `830d5ed854f4d4262442c4c77c065ac8330072ff` |
| KnowMart Web | `7bafcc7` | `36121753fe31a62037d28885ba75e9dbd2508d53` |
| sunmoonun 本地集成脚本 | `451171e^` | `451171e0505c3704e6fe43a9d22d056f65b1b016` |

按上述区间统计六个应用子仓的 `app/` 与平台仓的 `scripts/local-integration/`，运行代码新增 582 行、删除 4,665 行，测试与演练新增 541 行、删除 3,820 行，翻译新增 16 行、删除 278 行。合计净减 7,624 行。计数排除了父仓生成的契约、子模块指针和协作文档。

## 请独立复验

1. **KnowLab 的作者入口。** 从侧栏进工坊新建方法，再分别用空申请书签、已保存的工作稿和带试跑编号的旧书签进入。空稿进入五要素工坊，已有五要素工作稿按原方法编号打开，早期已保存的正式工作稿在工坊按原申请和修订继续编辑、试跑与冻结。核对刷新后仍是原试跑。数据库里的冻结版本与历史回执可以继续取证。历史工作稿的接续代码仍有实际调用者。
2. **KnowLab 的旧操作。** 四框模板、P1–P5 专用编辑器、从工具生成专家的专用表单及旧绑定面板都已移除。尝试在旧工作稿调用列检查、固定候选预览、匹配输出、逐页扫描四个专用 HTTP 入口，均应返回 404。现行方法目录仍可选择有资格的工具并绑定到步骤。对已经退役的固定包父申请直接调用请求用户审阅、标记规则已审和发起试跑，均应失败。
3. **当前契约决定试跑内容。** 在工坊编辑两项独立导出，保存后重开，核对步骤、引用、公开输入、对外结果与待确认项。检查 V0 规则参数、条件步骤、输入投影及收集输入能够穿过前端解析。把已就绪的方法改回待确认状态，旧定义不能用来验证或冻结新修订。老动态方法的作者 Schema 及两端锁按实际提供方重新同步，全量后端回归覆盖了这些契约。
4. **KnowBench 的历史任务。** 新方法从编排里的复核步骤运行。旧 `route-preview`、`route`、`execution` 三个手工操作均返回 404。用已经确认并有任务号的记录继续执行、读报告和提交所有者决定。生产方模型证据缺失、连接撤销、价格变动或 V0 被替换后，应阻断后续付费调用。方法与技能中心仍为三个业务视图。
5. **KnowMart 的统一小店。** 从“我的方法与专家”打开工具版本，开放、查看、再撤回孵化授权。切换所有者后不能读到他人的条目。独立授权面板与其读取接口已注销。小店仍按原条目更新授权。
6. **B410 的市场回执。** 正式方法自用上架需与请求的 `method_id`、`version`、`digest` 全部一致。存量动态专家继续使用的交付通道现在核对发送清单的版本与规范化摘要，摘要包括本次实际冻结的数据绑定。分别返回缺版本、别的版本和错误摘要，作者端必须停在已批准、尚未交付。用原交付单号重试正确回执，只能形成一笔有效交付。KnowMart 的 PostgreSQL 用例另行验证重复投递和版本不可改写。

## 本地验收与复跑

| 范围 | 本地结果及复跑入口 |
| --- | --- |
| KnowLab 后端 | PostgreSQL 16 全量 pytest，1,170 项通过，5 项跳过。重点文件为 `test_knowbot_incubation_routes.py`、`test_pr2_drafts_provenance_board.py`、`test_knowbot_clients.py`、`test_knowbot_experts.py` 和 `test_formal_method_routes.py`。 |
| KnowBench 后端 | PostgreSQL 16 定向 19 项通过。包含 `test_review_decisions_db.py`、`test_reviewer_choices_db.py`、`test_ordinary_strict_review_db.py`、`test_pr4_envelope_v0_frontier_and_intake.py`。已在启用 `sunmoonun/ci/method_transaction_guard.py` 的情况下复跑。 |
| KnowMart 后端 | PostgreSQL 16 全量 575 项通过，5 项跳过。旧授权读取路径退役与小店授权隔离均有回归。历史 v1→v2 迁移测试改用当年的 v2 样本，核对版本、停用记录和订单保留。 |
| 三个 Web | 每端运行 `pnpm typecheck`、`pnpm check:i18n`、`pnpm exec vitest run`。KnowLab 352 项、KnowBench 485 项、KnowMart 144 项通过，各跳过 2 项。KnowLab 另通过生产构建及成对启动前后端后的 Chromium 9 项测试。 |
| 跨仓链路 | 在 Luna 根目录运行 `python3 sunmoonun/ci/verify-contracts.py --repos "$PWD"`。正式指令的双后端集成演练已通过，覆盖登记私有指令、双叶专家与四叶嵌套专家。运行脚本为 `sunmoonun/scripts/local-integration/instruction_author.py --registered-instruction`。市场交付演练 `formal_market_delivery.py --expert` 也已通过，覆盖买方获取专家、两次批准和最终产物。 |

后端复跑使用各仓 `app/.venv` 和独立的 PostgreSQL 16 临时测试库，数据库名以 `_tests` 结尾。存在跨仓 Python 子进程的用例使用已就绪的同工位虚拟环境（`UV_NO_SYNC=1`）。模型、登录与工具调用使用测试替身。此批为本地待审批次，真实账号、在途线上数据及发布后的浏览器验收由 Luna 按实际发布版本补记。
