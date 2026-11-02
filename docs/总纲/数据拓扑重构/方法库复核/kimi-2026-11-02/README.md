# kimi 方法库整改复核（2026-11-02）

结论：有有效整改，但本候选仍不能作为可实战的方法库合入发版。未合并 kimi 分支、未改 kimi 应用代码、未改 qwen 发版候选。此前 knowmart 的 20 张演示卡片只是展示，与本批方法验收无关。

## 对象与范围

- knowlab-app：`6ce0ec412d64d59e50ccf8474c8d1d6dc2bc764e`
- knowlab-backend：`f0fd3e2e8aa4014c7977bf0a2c84701240856190`
- knowlab-web-frontend：`5b1eb358ba83212c63229bc540e9490c9f570229`
- kimi 所用 knowbench-backend：`24b6415aeaa36e4cf9a6dc4ed113232607ac9859`
- 交叉验证使用当前 Luna knowlab-backend `7a54c10790794461ae82afcbb0b0df9176d7d73d`、knowbench-backend `15643e299ab0e0a6a6c9df2ab700bf95d2be7800`。

通过 git archive 固定上述候选到 `/tmp/luna-kimi-method-review-2los8azd`。kimi 的 knowlab 三仓检查时干净；knowbench 父仓已有 web gitlink 修改，未触碰。后端相对双方作者基线 c5bf886 的变化仍只有 tests、夹具、文档与 CHECKPOINT；前端相对 a54e26c 只有测试夹具变化。它不是已经导入正式数据库的 20 项资产，也没有新分类检索服务。

本文不否定方法笔记中记录的所有者授权代定；本轮阻塞来自代码和可复现验收结果。来源标题及财务口径本身未在本轮逐条外部查证，不将代码审核表述为专业审定。

## 已确认修复

- golden 现已完整 `assert manifest == golden`，并有篡改内容必失败的用例；普通测试不覆写文件。
- 跨仓验收在子进程运行，不再污染 `app.__path__`。
- M01 增加非空约束，原“全空三表”反例已拦截；这是该反例修复，不等于每一行的全部口径、期间、来源均已验证。
- 两步直接成稿绕过仍被拒绝，完整依赖计划能通过结构检查。
- 候选自带四个测试文件 **33 passed**；ruff 全目录通过，pyright 0 errors/0 warnings（隔离目录无本地 .venv 的配置提示保留）。没有重复运行整个前后端测试集。
- 独立隔离 PostgreSQL 的通用方法生命周期与作者路由 **13 passed**（10.03 秒），含不可变历史、并发与 owner/CSRF；这是现有方法工程验证，不是这 20 个财务方法已经持久化。
- 方法出处/口径说明更完整；仍保留 SYNTHETIC 标记，未把示例文件叫作正式入库资产。

## 仍阻断实战的发现

### P1-1：当前 Luna 编译器拒绝 M20；自身 M04 正例也接不上 M20

位置：`app/tests/financial_author_method_fixtures.py` 的 M20 outputs/checks（1485、1516 附近）；`app/tests/test_financial_acceptance_verdicts.py` 的 M04/M20 正例。

M20 的 evidence_audit_trail 仍只声明 `type=list`、无 items，生成 `["string"]`，但 covers 需要对象的 metric 字段。当前 Luna 编译器明确报：

> covers evidence_audit_trail must declare objects containing metric

kimi 沿用旧编译器时自身 33 项全绿，不能代表已对齐 Luna 第 13 节基线。
另将其 M04 正例实际产物原样交给 M20：M04 的证据是 `{metric,value,compute_id}` 对象列表，M20 covers 未给 source_field，逐个把整个对象与下游 metric 字符串比较，正常对应的清单仍失败。其 M20 测试另造的是字符串列表，避开了真正串接的问题；M04 自身声明又是 `["string"]`，正例与声明也不符。

整改：统一上游证据对象、下游条目字段与 source_field，使用同一份真实已验 M04 产物做 M20 正例及缺项/多项/重复反例，并在当前编译器无错误的前提下跑完整链。不得放宽编译器或 covers 语义。

### P1-2：M02 仍会把 999999 元差额判为“平衡”

位置：夹具 M02 checks（195–212 附近），测试的 `test_m02_unbalanced_balance_sheet_difference_must_fail`。

独立用例提供符合规则算式的期末和期初两个计算记录，两者真实差额都为 999999；交回对应的 compute_id/left_id/right_id，以及非空审计清单。真实 judge + judge_numbers **全部通过**。

原因：computed 证明“差额确实这样算出来”，identity 只证明两个记录结果相等，都没有证明差额接近零；`passed=True` 又由模型自行填写。原坏样本同时给空 audit_reconciliations，并断言失败原因包含该空清单，不能证明差额约束正确。

整改：各恒等式的两侧、零差额容限及凭证绑定必须独立校验。保留其余字段合法，只改变勾稽差额的反例必须失败。若既有规则无法表达，明确交给 Luna 补通用规则，不以自报 passed 代替。

### P1-3：M13 的“两季度三情景”仅写在正文；空预测表仍通过

位置：夹具 M13 outputs/checks（961–981 附近）。

三张预测表全为 `[]`，balance_sheet_plug_zero.value=999999，left_id/right_id 指向同一计算记录，真实验收仍通过。规则只有 required 和 identity，没有期数、季度、三情景、区间上下界或非空行要求。

整改：将可执行输出明确为季度×情景×科目，验最低覆盖、上下界、基准关系和真实配平；加入完整正常样本，以及空表/少季度/缺情景/上下界颠倒/残差非零反例。不能把“表行结构待接数据后定形”的现状称为原题预测已覆盖。

### P1-4：M18 仍可不读原文就通过

位置：夹具 M18 quoted（1314–1319 附近）。

quoted 仅在 matter 精确等于“收入确认与应收账款减值”时强制引文。把标题换成合法的另一事项“商誉减值”，传 `quotes=[]`、`page=0`，真实验收通过；audit_opinion_type 也仅检非空，无引文规则。

整改：每个需作结论的 KAM 和审计意见都要验证引文；页码必须是实际引用中的物理页码并读原文核对。覆盖多种事项标题，以及缺引文/错误页码/错误原文/来源错配反例，不把自由文本标题作为唯一强制引用开关。

### P1-5：20 个方法的“不接范围/转交去向”未保存进冻结定义

位置：夹具 make_author_method_definition（1565–1590 附近），方法冻结模型 MethodDefinition。

这些内容放在临时工作稿的全局 `scope.does_not/elsewhere`，目标 step 只放 does/why/两条通用 rules。freeze 仅保存 step/input_schemas，组装后的专家 scope 又是另写的总描述。实测 20 项完整边界文字均未进入对应冻结定义（见 current-compiler-and-scope.json）。因此笔记里新增的金融企业不适用、亏损 PE 不适用等范围不能靠该字段传到运行方法。

整改：把每个方法的适用/排除/转交条件放到会被冻结、绑定、发布并交给规划/执行器的字段中，验证完整往返；不得只补 Markdown。若需要通用方法元数据扩展，由 Luna 统一设计契约，不另造财务专用接口。

### P2：M20 三条“有来源风险”仍可全部为空

位置：夹具 M20 risk_factors（1507–1513 附近）。

`[{"text":"","source":""}, ...]` 三项仍通过。list_min 只数个数，each_has 只核键，不能证明内容非空或来源有效。需核具体内容、来源关联并用空值/不存在来源反例验证。

其他明确缺口：当前成稿仅核杜邦覆盖，不核勾稽/估值等上游覆盖。可以先分别设索引与多条现有 covers 规则表达，再判断是否真的需要新机制；不要默认把所有内容整改都归因于“运行器缺功能”。M12 所述不可计算 CAGR 也尚无明确的交回分支与正反例。本轮未穷尽审核其余 20 方法的所有业务语义。

## 证据与复跑

- [精确版本](revisions.json)
- [候选自带测试：33 passed](candidate-tests.txt)
- [独立业务回归：5 failed](independent-guards.txt)：四个应拒绝的坏产物误过，一个前后衔接的正例误拒。使用真实 judge/judge_numbers 与合成记录仓，未用真实模型、Wind 或生产数据。
- [独立回归脚本](review_business_guards.py)：文件刻意不命名 test_，不混入平台日常测试；按下方命令显式运行。
- [当前编译器和范围丢失探针结果](current-compiler-and-scope.json)、[探针脚本](probe_compiler.py)。manifest 内容仍可能返回并与 golden 相同，**必须同时要求 errors 为空**，不能只看 JSON 相等。
- [数据库回归：13 passed](database-tests.txt)。第一次辅助脚本的隔离库名缺少 `_tests` 后缀，被测试安全守卫阻断，修正库名后通过；首轮日志保留 `/tmp/luna-kimi-method-review-2los8azd/database-tests-first.log`，不算候选代码缺陷或通过。
- [ruff](ruff.txt)、[pyright](pyright.txt)。前端只有夹具差异，本轮未重跑前端全量。

在 Luna knowbench-backend/app 目录，用该仓已锁 Python 环境运行（可通过 METHOD_REVIEW_MANIFEST 指向固定版本的隔离快照；缺省为 kimi 当前夹具）：

```sh
PYTHONPATH=. .venv/bin/python -m pytest -q -s /home/zymun/worktrees/luna/sunmoonun/docs/总纲/数据拓扑重构/方法库复核/kimi-2026-11-02/review_business_guards.py
```

在 Luna knowlab-backend/app 目录，核新编译器与冻结范围：

```sh
PYTHONPATH=. .venv/bin/python /home/zymun/worktrees/luna/sunmoonun/docs/总纲/数据拓扑重构/方法库复核/kimi-2026-11-02/probe_compiler.py /home/zymun/worktrees/kimi/knowlab-app/knowlab-backend/app/tests/financial_author_method_fixtures.py
```

下一步应先统一 M04→M20 契约、对齐当前编译器，再做 M02/M13/M18 的单变量业务反例及方法范围往返。通过这些之前不合并整批候选为可实战资产，不变更现有发版和演示任务。
