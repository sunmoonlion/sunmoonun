# MCP 稳定配置与每轮授权复核

由 Luna 发起，主工位为 Luna。当前状态为待独立复核，复核人待指派。开发与缺陷修复由 Luna 承担。

## 固定版本

KnowBench 后端受审提交 `de6e586fc6cc97ef2cabc7ff3a4f538bcf478465`，其中订阅与逐轮授权提交为 `9548ca90a3f478e1f6b4d09b0eab25a9ec95fa76`，比较基线 `ac19fbf95e16aa713f0357363f4a6e21dabe4ca1`。KnowBench 应用 `69ca442bdb81ff3a37cedd364f35366b82d3475b`。对应 Luna 待办第 3 项、接入方案 §17.6 第 5 项。

## 验收与交回

1. 在同一线程连续发两轮，再改变可发现工具，核对实际的解除订阅、恢复次数与逐轮授权记录。使用同一个网关凭据切换可读 Skill 时，两轮应各自读到当前选择的包。
2. 将旧轮的目录或正文请求延迟至新轮取得行锁，核对宿主观察事件、参数和读取结果。让第一轮启动回包迟于下一次准备，检查该回包无法登记到下一轮的范围。
3. 区分正常结束后尚在时限内的精确审批与取消、换轮、接管、重连后的旧审批。覆盖停止早于启动回包、旧停止指向其他轮次，确认旧网关和旧批准各自在什么时刻失效。
4. 固定版本 Codex 的离线探针使用本地合成 Responses/MCP。开发基线已切换到 0.170.0。请核对私有试跑关闭新版默认的 `view_image`、精确握手与历史证据配对。沙箱源码 `5b11c85639cba4c7dedfd09f97bc39db8e14ee59`，Link 两端 0.5.9 组包源码 `318f79e54cfe2be27fc9ceb722d172a8e757d975`。

从 `knowbench-app/knowbench-backend/app` 以项目虚拟环境运行下列专项，两个数据库变量分别指向可清理的 PostgreSQL 测试库。全量结果、探针运行边界与提交见[工位交接](../../../../../CHECKPOINT.md)。

```sh
.venv/bin/python -m pytest -q tests/test_capabilities_db.py tests/test_capability_runner.py tests/test_tool_invocation_db.py tests/test_skill_package_db.py
.venv/bin/python -m pytest -q tests/test_method_capabilities_db.py tests/test_method_permission_runner_db.py tests/test_workbench_usage_db.py
```

复核人按实际检视的提交、复验结果及阻断项在本目录的 `replies/` 下交回回执。Luna 核对后更新待办与交接，归档本请求。
