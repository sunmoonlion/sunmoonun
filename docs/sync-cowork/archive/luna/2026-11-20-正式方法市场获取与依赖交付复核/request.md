# 正式方法市场获取与依赖交付复核

Luna 发起，覆盖待办第 5 项和接入方案 §17.6 第 7 项。所有者决定先接通正式方法的最小市场获取链路，市场分区和普通用户委托在待办第 12 项继续开发。请将独立结论和复验范围存入本目录的 `replies/`，Luna 负责修复。

| 仓 | 基线 | 候选 |
| --- | --- | --- |
| KnowLab 后端 | `eb22655` | `778c023` |
| KnowLab 网页 | `e488d06` | `66e7d14` |
| KnowLab 应用及提供方契约 | `a498ed0` | `c47e190` |
| KnowBench 后端 | `f3268ee` | `56cdbcb` |
| KnowBench 应用及孵化契约锁 | `5999c3e` | `5daf4bc` |
| KnowMart 后端 | `b5f83b2` | `090da88` |
| KnowMart 应用 | `f1b5653` | `bbc1405` |

## 复验范围

1. 同一组 Skill 文件以不同顺序压缩，核对 ZIP 摘要不同、方法清单摘要一致。变更一字节或一个路径，检查交付核对。对照申请、审核、获取和内部取包四次核权，检查停用、撤权、到期、错误版本、另一作者或另一买方的结果。
2. 对照签发的业务验证回执、来源许可、主体实名和类目证照。检查申请待审和审核后失去资格时的结果。核对运营后台读取待审对象的权限。运行真实宿主孵化的 MCP 样例，通过后检查冻结版本与回执。嵌套私有方法的执行许可不得自动覆盖叶子交付。
3. 在真实 PostgreSQL 上并发获取同一版，检查买方获取记录的唯一性。普通撤架后，新买方获取停止，已有买方继续按当前许可申请内部交付。复核运营限制和主体、来源许可失效。浏览器只能取得版本、来源和必要声明。请在运行侧逐字节比较 NOTICE 与二进制附件，特别留意前后空白、尾换行和包内路径。
4. 核查 0015 迁移、KnowLab 提供方和两个契约消费者。旧 ZIP 摘要、聊天安装、业务覆盖核验材料和市场获取记录各有独立用途。公开候选登记仍须经过市场审核，账号和数据授权由后续运行核验。

## 本地复跑

准备两个独立的本机 PostgreSQL 空测试库，库名以 `_tests` 结尾。分别设置 `AGENT_TEST_DATABASE_URL` 和 `DELIVERY_TEST_DATABASE_URL`，从 sunmoonun 运行：

```sh
python3 scripts/local-integration/formal_market_delivery.py
```

脚本分别启动两个后端的测试环境，经回环 HTTPS 使用专门的服务关系，在真实迁移创建的临时 schema 验证审核前拒绝、审核后获取、重复获取、跨买方拒绝及三份文件的原始字节。身份提供方及 Skill 的执行回执使用测试夹具。当前正式 Skill 执行适配器仍待第 11 项实测，MCP 的真实宿主执行、审批、封存和公开候选登记由 KnowBench 的 `test_market_candidate_uses_real_execution_and_current_review` 单独覆盖，使用合成外部 MCP 服务。

分项回归可在各后端 `app` 目录运行：

- KnowBench 的 `tests/test_formal_method_admission_db.py`、`tests/test_formal_execution_db.py`、`tests/test_formal_method_routes.py`、`tests/test_formal_recursive_db.py`、`tests/test_knowbot_incubation_lock.py`。
- KnowMart 的 `tests/test_market_db.py`、`tests/test_market_routes.py`、`tests/test_kernel_invariants.py`。
- KnowLab 的 `tests/test_formal_method_service.py`、`tests/test_formal_expert_visibility.py`、`tests/test_knowbot_incubation_contract.py`。

发布时还需要登记 KnowMart → KnowBench 的 `method-delivery` 工作负载身份，应用 KnowMart 的 0015 迁移，并用目标环境核验服务认证和发布资格。当前仅使用隔离测试环境。独立回执与发布验收分别记录。
