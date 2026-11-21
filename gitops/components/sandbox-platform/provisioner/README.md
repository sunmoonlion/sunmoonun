# Sandbox provisioner

默认关闭。源码 `infrastructure/applications/component-images/sandbox-platform/provisioner`，2026-10-06 起按新体系参数化：命名空间（`SANDBOX_NAMESPACE`、`APP_NAMESPACE`、`RELAY_NAMESPACE`）与会合点地址从环境变量来，拉起的沙箱 Pod 满足 restricted PSS，Pod 带标签 `sunmoonai.com/sandbox=true`（knowbench、knowbase 的入站策略按它放行）。镜像经 `make platform-build OBJECT=sandbox-platform/provisioner` 重建、锁改写成 `platform/sandbox-provisioner` 后，把 `services_sandbox_provisioner_enabled` 打开。

沙箱镜像是另一个只构建的对象 `sandbox-platform/sandbox`，锁在 `../sandbox/image.lock.yaml`。工作台经内网调供给器，不暴露公共 hostname；会合点地址由 config 注入（沙箱从 2026-10-18 起不再连 knowbase，待办账 111，KNOWBASE_MCP_URL 已撤）；工作台记录工具服务的地址与令牌由工作台在每次拉起时随规格给。

## 单轮纯指令执行单元

新建 Attempt 通过 `/v1/instruction-executions/{owner}/{task}/attempts/{attempt}` 预留一对 Pod 和专属回执卷。同一根 Task 下的不同 Attempt 各自持有独立 UID、绑定和清理记录。旧 Attempt 继续通过原前缀 `/v1/instruction-executions/{owner}/{task}` 恢复和清理。两种入口均使用已有的供给器服务鉴权。运营配置 `sandbox_instruction_control_origin` 为空时预留返回 503。启用时填写 KnowBench 的集群内 HTTPS 源。网关访问控制接口时使用平台公开 CA，访问供应商时使用系统信任库。

| 宿主动作 | 供给器接口 | 持久状态与重试 |
| --- | --- | --- |
| 预留并取得实例身份 | `POST /prepare` | 返回 apiserver 分配的网关 Pod UID。并发预留返回同一实例，原 UID 保存在回执卷声明上。 |
| 查询上次预留 | `GET /reservation` | 响应丢失后仅查本所有者和任务的原网关 UID，支持从回执卷声明识别原实例。查询不创建 Pod 或卷。 |
| 绑定已预留预算的 Attempt | `PUT /{uid}/binding` | 宿主提交 `attempt`、`model` 和短期 `ticket`。网关核对自身 UID 后启动。相同绑定可续票。 |
| 查询网关、取得执行连接 | `GET /{uid}`、`PUT /{uid}/worker` | 网关就绪后才允许创建执行 Pod。宿主等到执行 Pod 就绪再用返回的 IP、47800 端口和本次专用令牌连接 Codex。重复获取沿用同一执行 Pod 与令牌。 |
| 允许本轮首个模型请求 | 再次 `PUT /{uid}/binding` | 宿主从真实 `turn/start` 回参取得 `turn` 后补入。第一次模型 POST 等待票据卷投影更新，最多 90 秒。续票保留已绑定轮次。 |
| 取消执行、核销用量 | `POST /{uid}/stop` | 宿主先在 KnowBench 取消并阻止新请求，再停执行 Pod。网关继续收取和补交原始回执。已放行请求的用量未知时保留预留和证据。 |
| 回收已结算实例 | `DELETE /{uid}`，待实例消失后 `DELETE /{uid}/proof` | 宿主依据 KnowBench 账本终态提交查询参数 `settled_attempt`。新入口要求该编号与路径中的 Attempt 相同；旧入口的空预留可省略。供给器核对 UID、绑定、停机与回收标记后才受理清卷。卷的实际释放时间由存储控制器决定。 |

Codex 的临时工作目录与 WebSocket 访问令牌只属于本次执行。供应商凭据、控制票据和回执卷都挂在网关内。执行 Pod 的出站策略只允许本次网关的 47801 端口。网关将终结用量持久化后向 KnowBench 交回，同一 Pod 内网关进程重启可补交。整个网关 Pod 丢失时保留回执卷和原绑定供核查。

供给器生命周期联调可在独立回环 kube-apiserver 上运行 `provisioner/tests/test_instruction_units.py`。设置 `INSTRUCTION_KUBE_TEST_PORT` 和 `INSTRUCTION_KUBE_TEST_DIR`，后者包含该临时服务的 `ca.crt`、`client.crt` 和 `client.key`。测试创建独立命名空间并注入就绪状态，覆盖同一根任务下的两个执行实例、不同回执卷、错误绑定被拒、单独停止和回收。升级时先提供新版供给器接口，再更新 runner。

### 集群网络和回执卷验收

在工位根目录设置测试集群的 kubeconfig，选择该集群可用、含本次 `instruction_*.py` 和 Codex 0.170.0 的沙箱镜像。指定的节点需能拉取或已预载测试镜像。以下命令建立两个临时命名空间，完成后回收：

```sh
knowbench-app/knowbench-backend/app/.venv/bin/python \
  sunmoonun/scripts/local-integration/instruction_cluster.py \
  --context "$TEST_CONTEXT" --image "$TEST_SANDBOX_IMAGE" \
  --node "$TEST_GATEWAY_NODE" --worker-node "$TEST_WORKER_NODE"
```

该用例加载候选基础网络策略、runner 的出站规则及供给器生成的任务策略。在沙箱命名空间，基础 DNS 策略排除 `app=instruction-worker`，网关仍可解析接入地址。记录同任务与跨任务连接，以及 DNS 的 TCP、UDP 结果。回执阶段用合成数据向网关写入一份待补交账单，控制端先返回 503。停止执行 Pod、重启原网关进程后允许补交，核对原卷 UID，并等待 PVC 和动态配置的 PV 删除。执行 Pod 有 900 秒上限，网关由宿主按账本结算状态回收。
