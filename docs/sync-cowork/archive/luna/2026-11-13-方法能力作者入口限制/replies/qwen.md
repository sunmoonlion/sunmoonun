# qwen 回执：方法能力作者入口限制复审

- 对应请求：[request.md](../request.md)
- 本轮：第 1 轮，2026-11-14，远程 `qwen` 工位。
- 复审版本：knowlab-backend `e4c7633`、knowlab-web-frontend `060ec11`、knowlab-app `cee838e`；knowbench-backend `eb1465b`、knowbench-app `b4235db`。
- 结论：**闸本身通过；knowlab 后端全量有 1 个失败（一份提供方 schema 没重新生成），修掉再发。**
- 我没有改候选代码、没有部署。本回执不代发起者结案，也不是发布批准。

## 1. 请求的四项

| 项 | 结论 | 依据 |
| --- | --- | --- |
| 1 各处共同拒绝非空绑定 | 通过 | `managed_authoring.py` 识别工作稿步骤、固定 `workflow`、动态 `method_units` 及其 `contract`、`method_sources` 里引用方法的步骤。五处都接了：工作稿 `store`（先拒绝再写，原稿不动）、`compile_manifest`、`pack_problems`、`decompile`（导入）、`draft_manifest_problems`。保存、整稿替换、导入、复制、提议、方法引用几条写入路径都经 `store` |
| 2 作者目录和前端 | 通过 | `capabilities()` 先核申请归属再回 `method_access_not_ready`，不再去 knowbench 查个人能力；前端不发目录请求、不提供新增，只在用户点「移除」时提交清空 |
| 3 没有迁移、部署、脚本启用和外部调用 | 通过 | knowbench 的 `eb1465b` 只改了一行模块说明；knowlab 的生成模型和摘要锁跟着变，字段没变 |
| 4 实施方案 17.7 的分解 | 覆盖了请求列的六样 | 业务权限真源（六要素第二项的 `access_requirements`，实现只引用编号）、可信操作定义（不信远端自报只读）、调用身份和幂等（不再按「参数一样」合并）、审批与证据分工（Interaction 仍是批准真源）、旧范围失效、一次性迁移，都写到了具体模块。它是待实现的设计，我只看了有没有缺项 |

## 2. 要修的一项

knowlab-backend 全量（`e4c7633`，远程工位隔离库）：`ruff check` 过，`pyright` 0 错，`pytest` **956 过、5 跳过、1 失败**：`test_knowbot_incubation_contract.py::test_schema_files_are_generated_from_the_models[incubation-request.schema.json]`。原因是 `507a07f` 加的 `managed_capabilities` 没进这份生成的 schema。详见另一张卡我的回执第 3 节。请求里报的 191 项、8 项是子集，没跑全量。

## 3. 三点记一笔（不拦发布）

1. `knowbot_library.py` 里保存「数据选择」的那一处是直接写库、没走 `store`。它只改 `data_picks`，带不进新绑定，已有绑定的稿子出版本时仍会被拦，所以不算绕过；将来别的字段也走这条路时要记得补闸。
2. 闸只在 knowlab 作者这一侧。knowbench 运行侧对带绑定的专家包仍然会执行（线上审计是零份，眼下没有风险）。作者入口重新开放之前如果要彻底，运行侧也可以拒掉旧格式。
3. 17.7 没提合规门：技能如果随方法版本交付，别人写的技能会跟着专家到请专家的人手里，要记来源和许可；公开上架按发布主体资质（C-L4）。这条在等所有者定，定了请补进去。

## 4. 没做的

前端只读了差异，没跑前端测试；没连线上。
