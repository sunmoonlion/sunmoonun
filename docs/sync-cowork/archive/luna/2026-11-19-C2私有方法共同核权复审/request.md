# C2 私有方法共同核权独立复审

Luna 发起，所有者指定 agy 独立复核。状态为**2026-11-19 已结案**。主工位是本地 `/home/zymun/worktrees/luna`，候选分支为 `luna`。[agy 第一轮回执](replies/agy.md)列出了实际受审提交、复验结果和结论。Luna 已核对回执并归档。

## 受审版本

| 仓 | 固定提交 | 用途 |
| --- | --- | --- |
| knowbench-app/knowbench-backend | `21f14eeb24caf084fc2821c458d41b936bdffe16` | 本轮平台产物授权与冻结证据；与前一版 `e9a3e0ce13c573906444bffc0f47afc6eeee9571` 对比 |
| knowbench-app | `1ab9c1b21b06fcfd7fd68b34d191e07d19fc0916` | 应用固定的后端版本 |
| knowbase-app | `9552fba44565e0a71b5a8f0d9d921b217537bbba` | 核对 KnowBase 资源方授权 |
| knowlab-app | `a498ed059fc45661554c4ca18976c5ff27e7242b` | 核对作者冻结登记、审批展示和消费者契约 |

## 请复核的完成条件

1. 从入口跟到实际交付。用宿主和模型试跑读取同一份已验收的平台产物，核对两次真实调用各自的身份、准许与拒绝、模型实际收到的字段和出处。检查换账号、版本、字段或来源后能否沿用旧许可。结合已有 KnowBase 跨服务用例对照共同准入。
2. 从叶子沿真实调用账查回父专家和根专家，检查冻结版本、输入槽、生产步骤、输出字段、期限及用途。中间层收窄后，后代应在派发前被拒。核对旧待批动作的补授权，以及私有测试任务在普通列表的可见性。
3. 并发批准及恢复应复用本次调用身份。检查适配器已经接收操作、进程丢失回执后，恢复者能否再次发送。结合历史计算及资料读取回执检查追溯关系。
4. 核对作者私有登记、后端与网页消费者锁、逐层产物和独立完成器。修改授权或产物凭据后应无法通过冻结。分别判断待办第 2 项的私有开发候选和接入方案 §17.6 第 3、4 项的完成范围。

## 复验入口和交回

在 KnowBench 后端的 `app` 目录用项目虚拟环境运行以下专项。数据库使用独立、可清理的 PostgreSQL 测试库，配置 `AGENT_TEST_DATABASE_URL` 和 `DELIVERY_TEST_DATABASE_URL`，数据库名以 `_tests` 结束。

```sh
.venv/bin/python -m pytest -q tests/test_formal_artifact_authority_db.py tests/test_task_output_reader_db.py
.venv/bin/python -m pytest -q tests/test_formal_recursive_db.py tests/test_formal_recursive_evidence_db.py tests/test_formal_recursive_runtime_db.py
.venv/bin/python -m pytest -q -c pyproject.toml ../../../sunmoonun/scripts/local-integration/c2_method_read.py
```

本卡授权读取固定代码、在隔离环境复验，并提交本人的回执。使用本地模型协议夹具和合成数据。普通委托与市场、真实供应商及发布另按既定路线推进。发现阻断项时，请注明文件、触发条件和受影响的验收项。

依据见[开发待办第 2 项](../../../../总纲/luna-待办.md)、[接入方案 §17.6](../../../../总纲/mcp和skill接入实施方案.md)与[工位交接](../../../../../CHECKPOINT.md)。

Luna 的[本轮自验明细](https://github.com/sunmoonlion/sunmoonun/blob/30ac0ca8ce515fb7d0c64c520361009c2d5a1782/scripts/results/c2-task-output-authority-20261119.json)记录了全量首轮的一项失败及复跑结果，供 agy 独立判断。

**首轮失败诊断（Luna）** 在固定提交上，以真实 PostgreSQL 行锁延迟第一轮能力记账，计划正文已写入事件账，但 runner 尚未登记本轮接收对象。首次验收收到空正文，返工收到脚本下一条回答，计划验收再次失败转入 WAITING。原回复、字段和改稿断言均沿用原用例。对照组生成 1 条交付记录，延迟组连续 3 次生成 0 条。逐次观测见上方自验明细的 `recheck.diagnosis`。该竞态在上一版后端已存在，当前候选仍可复现，供 agy 判断影响。

## Luna 结案记录 · 2026-11-19

采纳 agy 对 `21f14ee` 的私有候选通过结论。开发待办第 2 项完成。接入方案 §17.6 第 3、4 项的普通委托和市场范围按后续里程碑继续。回执中两项非阻断观察，分别在引入源任务自动清理和 M3 可选分支时复核。

全量首轮暴露的 runner 竞态由 Luna 修复，KnowBench 后端 `ac19fbf`、应用 `b3687cf`。修补在收到成功回包时即登记本轮接收对象。复用诊断的真实行锁时序连续三次成功交付，已增加永久数据库回归。该修补的验证归 Luna，agy 的通过结论对应上表固定的 C2 版本。[修复验收明细](https://github.com/sunmoonlion/sunmoonun/blob/30ac0ca8ce515fb7d0c64c520361009c2d5a1782/scripts/results/runner-turn-receipt-fix-20261119.json)
