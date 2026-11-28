# 十八组件合并发布与 587 项缺陷处置验收

**已结案。** #136 合并发布已交回。剩余专项现场验收转入 Luna 待办跟踪。 [Luna 验收回执](replies/luna.md)

在 `sunmoon-kind` 开发环境一次晋级本轮六个应用的后端、Web 和管理端。Cursor 负责构建、迁移、部署并交发布回执，Luna 亲自进行业务验收后结案。目录沿用原卡，最后七项财务断言随整轮发布。

587 个编号的本地结论为 544 项定向通过、21 项原入口退役后复验、15 项已有修复、4 项旧入口退役、2 项与其他编号同项、1 项保留原架构。各编号的验收依据见[逐号验收记录](replies/136-逐号验收.md)。发布以组件为单位。

## 发布基线和构建清单

Luna 在 #135 将现场就绪 Pod 的镜像摘要与发布锁、发布源码及本地父仓的组件指针逐项对照。18 个组件均有源码差异。下表列出纳入此次构建的版本，完整父子仓 SHA、现网镜像摘要、对应部署角色、分叉和契约文件见[18 组件发布对照](18组件发布对照.json)。源码位于本机 `/home/zymun/worktrees/luna`。Cursor 开工时重读现场晋级指针；若已前进，先重做差异核对。

| 组件 | #135 源码 | 最终构建源码 | 整合结果 |
| --- | --- | --- | --- |
| tpl-backend | `75482b260` | `65db1cd6f` | 已合并 |
| tpl-web-frontend | `6f46aef4b` | `d87b31669` | 已解决 3 个冲突并合并 |
| tpl-admin-frontend | `722c6b80e` | `849805014` | 快进 |
| knowfeed-backend | `0fa4b9e9b` | `cf0d52d64` | 已合并 |
| knowfeed-web-frontend | `5ef58d640` | `188010e23` | 已合并 |
| knowfeed-admin-frontend | `1bdcbcd04` | `51cb6030c` | 快进 |
| knowbase-backend | `a30b375fc` | `288dc831b` | 快进 |
| knowbase-web-frontend | `884d23541` | `e10d22628` | 快进 |
| knowbase-admin-frontend | `f2f6df316` | `da9d62cd2` | 快进 |
| knowbench-backend | `6fdfc7c8a` | `17021f8e7` | 快进 |
| knowbench-web-frontend | `83340277c` | `f8f25b461` | 快进 |
| knowbench-admin-frontend | `33559e926` | `75085a8e6` | 快进 |
| knowlab-backend | `f53aad14a` | `10a173a26` | 快进 |
| knowlab-web-frontend | `4e0f8d4f2` | `7a1e043fc` | 快进 |
| knowlab-admin-frontend | `e4d87c5df` | `ec6b2e135` | 快进 |
| knowmart-backend | `5f2ecd1f6` | `8d3e97a0e` | 快进 |
| knowmart-web-frontend | `7c6362929` | `631aad605` | 快进 |
| knowmart-admin-frontend | `6badf80be` | `52322c426` | 快进 |

Luna 已在本地合并四个分叉并锁定六个父仓。现场独有的九个提交在候选历史中均有等价补丁。模板 Web 逐文件保留会话恢复与切换、当前运行 ID 校验、引文显示及事件流重连；所有十八个最终提交的源码树逐一与已回归的 Luna 源码树比对相同。模板和 KnowFeed 两个 Web 回归分别通过 124、128 项，各跳过 2 项，类型与中英文键检查通过；对应后端身份与权限回归分别通过 68、65 项。

## 数据库、契约与部署顺序

| 数据库 | #135 现场实读 | 目标单一 head | 向前迁移数 |
| --- | --- | --- | ---: |
| tpl | `20261025_0004` | `20261025_0004` | 0 |
| knowfeed | `20261030_0022` | `20261128_0027` | 5 |
| knowbase | `20261119_0022` | `20261128_0027` | 5 |
| knowbench | `20261127_0064` | `20261128_0073` | 9 |
| knowlab | `20261127_0031` | `20261128_0033` | 2 |
| knowmart | `20261127_0022` | `20261128_0025` | 3 |

**Cursor 构建起点**为本机 `/home/zymun/worktrees/luna/.release-candidates/587/platform` 的 `luna-release-587` 提交 `c22be711ddb283227dcc5ca61ba047924ae4c283`。应用 Git 对象在 `/home/zymun/worktrees/luna/<应用>-app` 及其组件仓。新建的四个组件合并提交和两个父仓提交均有同名本地分支。发布流程如从远程检出，先使清单中的父子仓 SHA 可获取，再写入晋级记录。现场指针若自 #135 前进，在最新回执上合入此候选的配置与源码锁增量。

1. 六个父仓及十八个组件已钉入候选 sources.yaml；工作树契约校验与 `--pinned` 校验均通过。五库目标 head 与迁移任务代次已写入配置，KnowLab 已补中英文 studio 和 methods 登录返回路径。使用候选提交构建 18 个镜像，再以实际镜像摘要通过原生发布流程渲染运行和迁移资源。
2. Luna 已用六个 #135 后端的精确源码在独立 PostgreSQL 16 创建旧库结构，分别备份、还原到新库，并从恢复点升级至表列目标。五库 24 步通过，六库第二次执行升级后 head 均正确。KnowFeed 旧链使用平台数据库具备的 uuid-ossp 扩展。演练使用空业务库；现场在只读事务内核对六个数据计数，KnowFeed 待隔离披露、KnowMart 重复专家交易组和待撤销购买、KnowBase 待回填冻结记录、缺失呈现内容、待纠正摘要均为 0。
3. Cursor 在发布窗口核对在途任务并暂停受影响写入和消费，取得当时的实际数据备份和可恢复点，按新镜像执行迁移、核对记录数与目标 head，再开放对应服务。
4. 先就绪消费新契约的运行端，再开放产生新定义的作者端；待跨服务依赖、API 与后台消费角色就绪后开放 Web 和管理端。若迁移后需回退，先停新写入及消费，按演练结果恢复兼容的应用和数据库，核对在途任务与交易。
5. Cursor 在本卡 `replies/cursor.md` 记录发布号、GitOps 指针、六个父仓与十八个最终组件 SHA 和镜像摘要、六库实际 head、迁移回执、附件所列角色就绪情况、时间及与候选的差异。以此交 Luna 做现场业务验收。

## Luna 发布后现场验收

先将现场 Pod 和数据库逐项与 Cursor 回执比对。以下每组使用隔离测试数据，留存实际入口、版本、期望与观察结果。回执区分现场复现、同镜像回归、本地证据和待验编号，逐号关联台账。跳过或受条件限制的场景注明原因。

| 应用 | 现场业务路径与通过条件 |
| --- | --- |
| tpl | Web 登录返回原页，账号切换正确，管理端会话按配置有效；提交交互后断线重连能恢复相应运行的进度。 |
| KnowFeed | 创建带目标和主题的订阅，经提交、重试到投递只产生预期交付；在管理端核对归属不明的回执已隔离。 |
| KnowBase | 授权账户能读取指定版本和对应引文；撤权后新读取受限，已冻结的绑定与披露凭证可按约定核对。 |
| KnowBench | 通过请专家入口拟计划，核对目录分页和选定版本；使用已授权沙箱试跑，核对产出摘要、费用、重试和交付断言。 |
| KnowLab | 作者工作稿保存、回读、冻结、试跑均引用预期版本；从普通委托复验 #135 的 M02，并核对结果证据。 |
| KnowMart | 核对发布版本的交付选项；相同交易重复提交只计一次，撤销购买后按权限规则检查可用目录及交易记录。 |

各应用均从 Web 和管理端登录并打开受影响页面。Luna 将现场观察、实际覆盖和未通过项写入本卡 `replies/luna.md`，通过后归档。台账列有六后端及十二前端本地通过与跳过数，可据其回归路径复查。

### 最后七项的额外验证

在最终 KnowLab 后端 app 运行 `tests/test_financial_methods_assembly.py`、`tests/test_financial_acceptance_verdicts.py`、`tests/test_knowbot_incubation_contract.py`，使用同版相邻 KnowBench 解释器；在 KnowBench 运行 `tests/test_delivery_assertions.py`。本地已核对 138 个合成业务期望。部署后 Luna 再执行下面跨镜像探针并按逐题口径核验。

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

## 七项财务断言的验收口径

| 编号 | 应通过 | 应拒绝 |
| --- | --- | --- |
| B389 | 合成 M02 差 0.99 元报平衡，差 1 或 2 元如实报检出 | 正好 1 元仍报平衡；伪计算回执 |
| B390 | M12 非正端点给绝对变动和理由；M15 亏损用有依据的 PB 或 PS | 编造 CAGR、盈利时无故省略 PE、亏损缺理由或伪造盈利事实 |
| B404 | Z = 1.81 和 2.99 分级均为中，指标与证据逐项一致 | 分值、等级、证据任一处矛盾 |
| B405 | 两个季度三种情景均与对应季度区间一致 | 即使算式凭证有效，换季度或用另一组区间也拒绝 |
| B406 | 完整的 WACC × 增长率网格 | 空表、单轴、缺角、重复坐标、缺每股估值 |
| B407 | 有引文的事项明细与总数相同；零项有明确披露依据 | 声称零项但有明细，或没有零项披露依据 |
| B583 | 完整窗口两期时说明原因并交空预测；三期起有预测 | 资料不足却外推，或窗口足够却交空表 |

B389 的严格小于一元为旧合成方法的作者口径。sig-am 自用 M02 使用自己的冻结版本及作者容差。分组件测试结果见[发布源码测试汇总](replies/136-发布源码测试汇总.json)。
