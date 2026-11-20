# 隔离脚本资料与前序产物输入复核

Luna 发起，对应 Luna 待办第 8 项、接入实施方案 §17.6 第 10 项。请独立复核人在本目录 `replies/` 留下所验版本、执行环境、用例结果和需修问题。

| 仓 | 比较基线 | 受审提交 |
| --- | --- | --- |
| KnowBench 后端 | `4fd5942` | `f392957` |
| KnowBench 应用 | `399720f` | `27fcbe6` |
| 平台组件、供给器与联调脚本 | `b7d8b63fa` | `36d980961` |

## 复跑

1. 在独立 PostgreSQL 测试库运行 KnowBench 后端的 `tests/test_script_inputs_db.py`、`tests/test_skill_execution_db.py`、`tests/test_skill_executor.py` 和 `tests/test_calls_db.py`。检查待批时资料读取次数为零；批准后读取指定材料版本和阅读版，容器准备期间撤权、更换正文或取消时不交付。比对当前 Attempt 输入绑定、生产 Attempt 的正式输出记录和实际交付的一个字段。查看 `capability/script_inputs_prepared`，核对引用、文件摘要和字节数，审批及事件中均无需保存资料正文。
2. 从平台仓 `infrastructure/applications/component-images/sandbox-platform/provisioner` 运行 `pytest -q tests`。在隔离测试命名空间，用候选镜像及匹配的 RBAC 运行 `script_probe.py`。检查 Job、Pod、Secret、容器环境和网络策略。在两份供给器实例之间重复交付同一个 Job，领取输入的条件须同时匹配 Job UID 和待领取状态。进程对不完整或校验失败的帧不得启动脚本，已经领取的 Job 不得重发输入。
3. 实测单份 512 KiB、业务输入合计 2 MiB、包合计 4 MiB 及超出边界的请求。取消等输入和正在执行的任务，检查 Pod 终止和 Job 清理。丢失交付响应后，让新 runner 或供给器按原调用 ID 找回结果；核对上传请求次数和持久回执。
4. 用两个本地 `*_tests` 测试库和回环地址的测试供给器运行 `python3 scripts/local-integration/script_inputs.py`。设置 `AGENT_TEST_DATABASE_URL`、`DELIVERY_TEST_DATABASE_URL`、`SCRIPT_TEST_PROVISIONER_URL` 和 `SCRIPT_TEST_PROVISIONER_TOKEN`。脚本创建合成账号与测试资料，经 KnowBase MCP 读取、KnowBench 操作批准、独立执行和账本归档，断言 21 的计算结果为 42。KnowBase 和 KnowBench 均使用真实数据库迁移；此联调的对象存储和外部登录身份使用夹具。

## 开发自验

KnowBench 后端全量收集 2,916 项，逐项对账为 2,910 项通过、6 项跳过（3 项退役样例的空参数组、3 项可选 RabbitMQ 探针）。本项后端专项 29 项、隔离执行组件 23 项通过，后端 Ruff 与 Pyright 通过。在真实 KIND 中，同时交付 4 MiB 脚本包和 2 MiB 业务输入并收回结果。故意损坏输入摘要后，容器在执行前终止；再次交付只取回原失败状态。真实 KIND 测试使用独立临时命名空间与合成材料，已验证 Python、Bash、Node、断网与无凭据、并发领取、停止和回收。运行结果与下一项见[工位交接](../../../../../CHECKPOINT.md)。用户脚本开关继续关闭，发布和专家端到端编排各按后续工作项验收。

## Luna 结案

已核对 agy 的受审提交、复跑范围和结论，接受本地候选复核。后续完善建议保留在[独立回执](replies/agy.md)。
