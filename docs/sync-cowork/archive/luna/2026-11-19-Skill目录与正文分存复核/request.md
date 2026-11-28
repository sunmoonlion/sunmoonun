# Skill 目录与正文分存复核

Luna 发起，范围为待办第 4 项、接入方案 §17.6 第 6 项。独立复核人待指派，Luna 负责修复。请按审查到的版本和实际复验结果将回执交回本目录的 `replies/`。

## 固定版本

| 仓 | 比较基线 | 受审提交 |
| --- | --- | --- |
| KnowBench 后端 | `de6e586fc6cc97ef2cabc7ff3a4f538bcf478465` | `f3268eeffd9725a234e442d588b0f258ab859e31` |
| KnowBench 网页 | `d1e58d8352077dac2e4a3e107f86ee2e7d666970` | `5bb7f294603929562f2813aa6781c737dfa2ab48` |
| KnowBench 应用 | `69ca442bdb81ff3a37cedd364f35366b82d3475b` | `5999c3e2b00df790f2bc28500ed573af40e1d1f6` |

## 请复核

1. 从旧格式的纯指令和 ZIP 升级 0046。核对拥有者、资产 ID、修订、包摘要、选用引用及每条文件路径、原始字节和 SHA-256。检验旧主文件副本与清单不一致时的事务回滚、降级再升级，以及安装中途失败后相同请求并发重试。
2. 通过设置页和真实目录路由核对只传元数据。展开说明只读本人指定的主文件。停用保留安装者查看权限，卸载关闭说明入口。模型另走当轮宿主调用核验，验证换轮、停用和跨账号时读不到正文，列文件不载入内容。
3. 核对相对路径、Unicode 分页、图片和二进制返回。已批准的脚本可以取得同一包的文件；重放、拒绝或失效的批准不得再次派发。核对消费锁和网页 ZIP 导入的请求形态。
4. 在专用 PostgreSQL 测试库中复跑相同样本的目录查询。分别核 SQL 次数、数据库结果字段字节、HTTP 正文字节、P50 和 P95，用逐文件摘要对账。实测口径和结果见[验证记录](https://github.com/sunmoonlion/sunmoonun/blob/30ac0ca8ce515fb7d0c64c520361009c2d5a1782/scripts/results/skill-catalog-0046-20261120.json)。
5. 全量回归暴露了既有的专家原生交互时序问题，修复在后端 `f3268ee`。请复核同一宿主 turn 刚启动就收到审批或提问时，交互必须等待该 Attempt 绑定成功。绑定失败、任务取消、旧轮已被替换时不得沿用旧等待。运行 `tests/test_capability_runner.py`、`tests/test_method_tools_db.py` 及 `tests/test_workbench_runner_db.py` 核对。

从对应的后端 `app` 目录运行。性能脚本使用当前目录中的代码与测试依赖。先在基线运行 `seed`、`before`，备份该测试库，再在候选运行 `migrate`、`after`。独立复验可在备份副本重复。设置 `AGENT_TEST_DATABASE_URL` 指向专用的空 `*_tests` 库，`MEASURE` 指向[性能脚本](../../../../../scripts/local-integration/skill_catalog_measure.py)的绝对路径。

```sh
.venv/bin/python "$MEASURE" seed
.venv/bin/python "$MEASURE" before
# 切到候选后端 app 目录或使用同一备份恢复出的测试库
.venv/bin/python "$MEASURE" migrate
.venv/bin/python "$MEASURE" after
.venv/bin/python "$MEASURE" instructions
```

候选专项可运行 `.venv/bin/python -m pytest -q tests/test_skill_package.py tests/test_skill_package_db.py tests/test_skill_execution_db.py tests/test_calls_db.py tests/test_capabilities_db.py tests/test_capability_routes_db.py tests/test_skill_dependencies_db.py tests/test_skill_installation_db.py tests/test_kernel_invariants.py`。网页在前端 `app` 目录运行 `pnpm test`，设置 `WEB_INTERACTION_CONSUMER_VECTORS` 为同一工位 tpl-app 的 `contracts/web-interaction-v1.consumer-vectors.json`。

## Luna 结案

已核对 agy 的受审提交、复跑范围和结论，接受本地候选复核。后续完善建议保留在[独立回执](replies/agy.md)。
