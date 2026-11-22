# 第 14 项长期职责与回炉版本采用

执行者为 Cursor。第 13 项已随 #106 晋级。本单是 #106 之后的独立候选，供后续排期。用户要求把现场验收留到后续，本轮没有启动付费模型。第 13 项的盲测仍在原卡交回。

## 发布范围

| 仓 | Luna 候选 |
| --- | --- |
| KnowBase 父仓、后端 | `00b59ec`、`a30b375` |
| KnowBench 父仓、后端、Web | `da32240`、`cfe5e55`、`b1047ad` |

先发布 KnowBase 的成稿可用性查询，再升级 KnowBench 数据库至 `20261122_0059`，最后更新 KnowBench API、runner 和 Web。KnowLab 和 KnowMart 沿用现有接口。KnowBase 的新接口复用 `knowbase:user-data-output` 身份；服务路由须允许 KnowBench 的 `GET /api/internal/v2/user-data/outputs/available`。沿用 #106 的试验账号、市场资格、模型和正常的业务逐次批准。`WORKBENCH_OUTPUT_WRITE_ENABLED=true` 同时作用于 API 和 runner。已在运行的全量入口策略沿用 #106。

## 准备与本地复跑

在本地大内存工位，取表中工作树和本单所在的 `sunmoonun/luna` 修订。KnowLab、KnowMart、KnowBench 后端使用各自的 `app/.venv`。将 `AGENT_TEST_DATABASE_URL` 和 `DELIVERY_TEST_DATABASE_URL` 指向环回地址的两个独立临时 PostgreSQL 测试库（库名以 `_tests` 结尾），运行以下命令。脚本自行创建隔离 schema、临时证书、原题、试题、测试账号和受控工具；无须提供真实账号凭据。

```sh
python3 sunmoonun/scripts/local-integration/formal_market_delivery.py --expert --roundtrip
```

同一批本地用例包括工作台后端的 `test_ordinary_strict_review_db.py -k two_sources` 及 `test_ordinary_metered_tools_db.py -k live`。后者在两个独立 Codex 容器中执行，设置 `RUN_CODEX_INSTRUCTION_PROBE=1` 和 `CODEX_INSTRUCTION_TEST_IMAGE` 为现场对应的已缓存 sandbox 镜像；本地验证镜像为 `sunmoon-build/sandbox:edd9b00f569a-8852d509a0e7`。这些是开发用例，无需 Kimi 计费。回到约 3.7 GiB 的远程工位时重任务串行。

## 后续现场验收

1. 用 `sig-am` 在试验项目完成一个已获使用权、带明确交接输出的双角色专家委托。记录该专家的方法 ID、版本、摘要、原委托和执行编号，核对两方的线程、工作目录、各自可见材料和交接前后的读取结果。原卡的 L105 是单条指令的物料，双角色场景要选用已验证的编排专家。若现场尚无合适版本，可按本单的回炉路径先在私有项目孵化，再从自己的目录获取。
2. 在交付页打开「长期职责」，填写长期交代、间隔和要放行的输出，保存后单独批准写入 KnowBase。首次到期前应无新委托。固定间隔最短一小时；现场等正常到期，本地用可控时钟验证重放。记录上期成稿的资料 ID、版本和 SHA-256、职责和新委托编号。新委托应显示同一专家版本和该份成稿，执行前再次确认。选了资料输入的场景，在 KnowBase 将成稿转为数据，并在准备页选该副本的第一版。另以单独的测试委托验证未放行、撤回放行、失去使用权及暂停，预期不会继续生成委托。
3. 从「请专家」原委托提交确切缺口。目录为空时验新孵化；已有 v1 时，用原作者验新修订、用仅有运行权的买方验提需。缺工具时先孵化并试跑工具，再在专家工作稿中引用精确版本。冻结 v2 后通过适用目录交付。买方获取前应看不到可采用的 v2；获取后在**原委托**打开「核对已获取的孵化版本」，展开能力、输入、输出或权限变化，明确确认后再选用并执行。记录 KnowLab 申请与冻结回执、KnowMart 的获取回执和两个工作台运行编号。重试应共用同次回执，v1 原运行和成稿仍可打开。
4. 用原卡已约定的真实账号与获准物料。只在安排现场验收后调用真实模型，记录实际模型、耗时、费用和产物版本。用本单 `replies/cursor.md` 交回集群构建、两条路径的运行与偏差。业务盲测继续由 `zymun` 单独复核。

第 14 项本地验证的触发来源为定时。邮件和 KnowFeed 订阅属于连接器方案中的其他触发来源。
