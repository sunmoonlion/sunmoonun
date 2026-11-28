# 七项财务交付验收修复合并发布

目标为 `sunmoon-kind` 开发验收环境。本卡由 Luna 在本地准备；进入发布流程后由 Cursor 构建和晋级，Luna 负责业务验收。发卡时只读观察到的 Flux 修订为 `sha256:50ac03f7f101cd665b12cbc344975a1057c101dc2484656015c12fc8118ee5d2`。发布时从实际最新晋级指针整合。

## 发布材料

| 应用 | Luna 父仓 | 后端 | 相对本批前态的增量 |
| --- | --- | --- | --- |
| KnowBench | `75385d4` | `17021f8`（前态 `c8101f7`） | 执行冻结的交付断言，校验 JSON 字段、集合及数值关系；同步消费方契约锁 |
| KnowLab | `f475636` | `10a173a`（前态 `bc455b6`） | 作者方法编译、保存及回读交付断言；同步作者方法、孵化请求与动态方法契约 |

源码在 `/home/zymun/worktrees/luna` 的对应仓。父仓已有本轮之前的工位提交，整合前比较现场已有的源码与契约基线，逐项记录实际采用的提交。两端契约和镜像同批晋级，先就绪能读新断言的 KnowBench 运行端，再开放能生成断言的 KnowLab 作者端。按平台现有角色更新共享同一后端镜像的服务。本卡的文件增量没有迁移、前端、模型路由、报价或账户配置。合成包只在测试中使用，现场验收使用本轮的隔离样例及作者流程。

## 本地验证结果

最终源码已按本地完整用例集复验，KnowBench 后端 3240 项通过、16 项跳过（4 个独立 PostgreSQL 库，共收集 3256 项）；KnowLab 后端 1207 项通过、5 项跳过。冻结清单跨进程核对 138 个合成业务期望，两端 Ruff、源码契约预检、作者与运行端语法一致性检查均通过。

## 发布前与发布后

1. 在候选上检查 `python3 sunmoonun/ci/verify-contracts.py --repos <并列仓根目录>`；更新实际源码指针后再检查 `--pinned`。同时核对两端父仓的动态方法、作者方法和孵化请求 schema 与消费方 SHA-256。
2. 从 KnowLab 后端 `app` 运行 `tests/test_financial_methods_assembly.py`、`tests/test_financial_acceptance_verdicts.py` 和 `tests/test_knowbot_incubation_contract.py`。这组测试实际启动相邻的 KnowBench 解释器，使用合成证据对冻结清单逐条判分。KnowBench 后端另运行 `tests/test_delivery_assertions.py`。本地使用与锁文件一致的 uv 索引（含结尾斜杠）。
3. Cursor 在 `replies/cursor.md` 留下实际发布号、两端源码及镜像摘要、晋级指针、就绪状态和时间。回退时成对回退作者与运行端；若试验中已产生使用新断言的冻结版本，先停止该试验版本的新调用，并保留精确版本记录。
4. Luna 核对现场版本后，用下面的只读探针从已部署的 KnowLab 容器编译作者检查，把得到的同一条规则直接交给已部署的 KnowBench 判分。完整七项使用与现场镜像对应的源码、合成证据和冻结清单复验。把实际入口、版本、输入、期望、结果及现场覆盖范围记入 `replies/luna.md`，供结案。

### 已部署镜像的只读探针

在 Bash 中使用现场开发环境的 kubeconfig。第一段的标准输出通过管道传原始规则，第二段在 KnowBench 容器中从标准输入读取同一份 JSON。命令成功时输出 `[True, False]`，对应 0.99 和 1 元两个交付。探针用于区分候选源码跑通与实际发布镜像生效。

```bash
set -o pipefail
k=(kubectl --kubeconfig "$HOME/.kube/sunmoon-kind.config" -n app-platform-dev)
"${k[@]}" exec deploy/knowlab-api -- python -c '
import json
from app.domain.knowbots.compile import check_rule
from app.domain.knowbots.workdraft import CheckCell, StepCell
step = StepCell.model_validate({"id": "inspect", "outputs": [{"name": "observed", "type": "number"}]})
check = CheckCell(template="assertion", params={"path": "observed", "expression": "num(\"observed\") < 1"})
rule, error = check_rule(check, step, {})
assert not error, error
print(json.dumps(rule))
' | "${k[@]}" exec -i deploy/knowbench-api -- python -c '
import json, sys
from app.application.workbench.acceptance import judge
from app.domain.workbench.packs import AcceptanceRule
rule = AcceptanceRule.model_validate(json.load(sys.stdin))
results = [judge(json.dumps({"observed": n}), (rule,)).ok for n in (0.99, 1)]
assert results == [True, False], results
print(results)
'
```

## Luna 验收口径

| 编号 | 应通过 | 应拒绝 |
| --- | --- | --- |
| B389 | 合成 M02 差 0.99 元报平衡，差 1 或 2 元如实报检出 | 正好 1 元仍报平衡；伪计算回执 |
| B390 | M12 非正端点给绝对变动和理由；M15 亏损用有依据的 PB 或 PS | 编造 CAGR、盈利时无故省略 PE、亏损缺理由或伪造盈利事实 |
| B404 | Z = 1.81 和 2.99 分级均为中，指标与证据逐项一致 | 分值、等级、证据任一处矛盾 |
| B405 | 两个季度三种情景均与对应季度区间一致 | 即使算式凭证有效，换季度或用另一组区间也拒绝 |
| B406 | 完整的 WACC × 增长率网格 | 空表、单轴、缺角、重复坐标、缺每股估值 |
| B407 | 有引文的事项明细与总数相同；零项有明确披露依据 | 声称零项但有明细，或没有零项披露依据 |
| B583 | 完整窗口两期时说明原因并交空预测；三期起有预测 | 资料不足却外推，或窗口足够却交空表 |

B389 的严格小于一元为旧合成方法的作者口径。sig-am 自用 M02 使用自己的冻结版本及作者容差。全量本地测试记录见[处置台账](../../../../总纲/587项缺陷处置台账.md)。
