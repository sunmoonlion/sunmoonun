# Codex 逐步骤工具范围验证

日期：2026-11-13。对应[接入实施方案](../../../../mcp和skill接入实施方案.md)。用户要求实际验证能否在同一个 thread 中切换步骤工具。本记录区分二进制实测和仍未接入项目的部分。

## 1. 结论

**固定版 Codex 0.155.1 可以在同一 thread 内切换 MCP 工具白名单；本次测试的接口不能替换已创建线程的 dynamicTools。**

可用顺序：当前 turn 完成且无未决调用 → `thread/unsubscribe` → `thread/resume` 带 `mcp_servers.<服务名>.enabled_tools` → 下一轮。线程 ID 保持不变，实际模型请求中保留之前的用户消息；另一个已加载线程的工具集合没有被改变。不是每一步新建 thread，也不是修改全局配置。

当前 runner 已有类似的解除订阅／恢复机制用于搜索范围，见 knowbench 后端 `app/app/application/workbench/runner.py` 的 `configure_search_scope()`。本次没有修改该代码，通用 MCP 工具范围接线仍需开发。

## 2. 环境与可复跑材料

- 脚本：[codex_step_scope_probe.py](codex_step_scope_probe.py)，仅允许在一次性、无外网容器中运行。
- 固定二进制报告：`codex-cli 0.155.1`。
- 二进制 SHA-256：`0753dfe1d8b87a52436deb13eb1c549661ef4c84fee2c5aa688385eebeccb761`。
- 探针 SHA-256：`f2794d6ef1631cfc398abe6caedc9f698037b27c51a374d085a0b0db7c2ad732`。
- 使用本机已有沙箱镜像短 ID `a3193b655b59`，没有下载或构建镜像。只借用其 Python 环境，固定二进制单独只读挂载，不假定镜像自带二进制版本。
- Docker：`--network none`、只读根、丢弃 capabilities、禁提权、512 MiB 内存与交换总上限、1 CPU、128 进程上限。
- `/tmp`、`/root`、`/data` 使用临时文件系统，不挂用户 HOME、凭据或业务资料。容器结束删除。
- Responses 与 MCP 均为 Python loopback 合成服务，无真实模型、外部账号或费用。

在本仓根目录可按以下形式复跑；镜像与二进制须已经存在，变量仅用于本次测试路径：

```sh
probe_codex_bin=/absolute/path/to/codex-0.155.1
probe_python_image=a3193b655b59
probe_scope_script="$PWD/docs/总纲/专家方案设计/专家使用方案/luna/验证/codex_step_scope_probe.py"
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --memory 512m --memory-swap 512m \
  --cpus 1 --pids-limit 128 --user 0 \
  --tmpfs /tmp:size=128m --tmpfs /root:size=32m --tmpfs /data:size=128m \
  -v "$probe_codex_bin:/probe/codex:ro" \
  -v "$probe_scope_script:/probe/probe.py:ro" \
  --entrypoint python3 "$probe_python_image" /probe/probe.py
```

上述镜像已声明 `CODEX_HOME=/data/codex`；换用其他测试镜像必须确保 Codex 使用探针配置目录。脚本通过容器内部 `/tmp/evidence` 保存临时请求与日志，随容器删除，交回证据为输出案例及断言。需要保留原始合成请求时应另行配置受控取证方式，不把它当作现成业务日志采集方案。

## 3. 方法与观察点

探针启动一个真实 Codex app-server，使用 stdio RPC；项目线上使用 WebSocket，本轮没有验证网络重连。创建两个动态工具名称 `probe_alpha`、`probe_beta`；模拟 MCP 提供 `read_a`、`read_b`。每轮捕获 Codex 发往模拟 Responses 服务的真实请求，解析 `tools` 中的函数与 namespace，检查是否含指定工具。

模拟模型还分别请求允许的 `read_b` 和已移除的 `read_a`，检查 MCP 服务收到的 `tools/call`。这些工具不产生实际副作用；合成服务声明只读，使测试能够在 `approvalPolicy=never` 下区分工具范围问题与审批阻止。该声明不代表产品可相信任意远端的只读声明。

每个 turn 使用唯一输入标记，切换后确认第一轮标记仍存在于实际模型请求历史中。对照线程先后发出请求，检查范围不受影响；不是同时并行运行两个 turn 的压力测试。

## 4. 最终通过的 15 个场景

| 案例 | 操作 | 实际模型请求中的测试工具／执行结果 |
| --- | --- | --- |
| D1 | 新线程创建时传 alpha | alpha 存在 |
| D2 | 同线程 `turn/start` 附加 beta 的 dynamicTools | 仍为 alpha，beta 没有生效 |
| D3 | `thread/settings/update` 附加 beta 的 dynamicTools | 仍为 alpha |
| D4 | 已装载线程 `thread/resume` 附加 beta | 仍为 alpha |
| D5 | 解除订阅后 `thread/resume` 附加 beta | 仍恢复原 alpha；历史保留 |
| D6 | 新建另一线程，创建时传 beta | beta 存在，作为正对照 |
| M1 | MCP 白名单设为 read_a | 只有 read_a |
| M2 | 对照线程白名单为 read_a、read_b | 两者都存在 |
| M3 | 原线程不解除订阅，直接 resume 改 read_b | 仍为 read_a，修改未生效 |
| M4 | 原线程解除订阅后 resume 改 read_b | 只有 read_b；同 thread ID、历史保留 |
| M8 | 在 M4 范围内，模拟模型调用 read_b | 服务收到一次 read_b 调用，结果回给模型 |
| M9 | 同范围内，模拟模型强行请求 read_a | 没有新增 MCP 服务端调用，未执行被移除工具 |
| M5 | 再运行对照线程 | 仍可见 read_a、read_b |
| M6 | 原线程解除订阅后 resume 设置空白名单 | 两个业务 MCP 工具均不在请求中；历史保留 |
| M7 | 原线程解除订阅后 resume 恢复 read_a | 只有 read_a；历史保留 |

最终运行退出码 0，输出：

```text
PASS: dynamic tools immutable through tested RPCs; same-thread MCP allowlist switch, history, peer isolation, allowed and denied model calls
```

最终运行共 15 个模型 turn、17 次合成 Responses HTTP 请求（两次工具请求各多一次结果续推），只有一次 MCP `tools/call` 到达合成服务。主 MCP 线程 ID 在 M1、M3、M4、M8、M9、M6、M7 中均为 `01a1d2f6-9360-72d0-8bea-7570803dfa78`；它是本次临时测试线程，不是用户任务。

不支持的 dynamicTools 字段在上述请求中被接受但未改变工具集合。由此不能用 RPC 成功返回证明工具更新成功，集成必须验证实际生效。

## 5. 探针调试记录

第一次运行已完成 13 个范围观察，但向挂载证据目录写文件失败，退出码非 0；未计为最终通过。改为容器临时目录后，第二次新增调用验证受模拟服务缺少只读注解影响，断言失败；增加明确只读的合成工具注解后，最终 15 个场景全部通过。没有修改真实 MCP 服务或关闭业务授权来使测试通过。

## 6. 结论的边界

1. 这不是对全体工具的隔离证明。业务 MCP 白名单为空时，资源枚举／读取、目标管理、提问等基础工具仍出现在请求里，必须另行按步骤约束。
2. 捕获还显示新建与恢复后的请求中 Skill 工具集合存在差异，本轮没有探测其原因和 Skill 加载语义；不得从 MCP 结论推导 Skill 已隔离。
3. 移除工具描述不会清除旧消息和工具结果；独立复核或数据隔离仍可能需要新线程。
4. 没有测试真实模型选择质量、用户数据、收费、写操作、长审批、WebSocket 中断、进程重启恢复、多订阅者或并发 turn。现有全套授权与账本仍须接线验收。
5. 同 thread 的重载不是活跃推理中的热切换。须等待空闲并持有执行权，完成解除订阅与恢复，再发下一轮；完整有效配置与任务绑定不能遗漏。
6. 白名单只说明客户端当前暴露和分发；服务端仍须核对连接、操作、资源和任务授权。禁止将白名单作为外部账号访问凭据。
7. 固定版本应持续受控升级；升级候选必须重新跑探针和集成测试。不将这次二进制行为视为永久协议保证。

## 7. 对方案的修正

优先扩展现有工作台 MCP：API 提供受管工具入口，runner 从注册记录生成步骤白名单并恢复同一 thread，Codex 发现和暴露后经 MCP 回到 API 的统一调用检查。程序直接调用仍可由 runner 执行同一业务模块；动态工具回调保留给工具集合固定的线程。

这使“一任务一主线程，必要时分支”有了可验证的 MCP 路径，不必为了换工具而默认每步建线程。此处是方案修订与协议证据，不是已上线实现。
