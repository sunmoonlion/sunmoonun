# Sandbox provisioner

默认关闭。源码 `infrastructure/applications/component-images/sandbox-platform/provisioner`，2026-10-06 起按新体系参数化：命名空间（`SANDBOX_NAMESPACE`、`APP_NAMESPACE`、`RELAY_NAMESPACE`）与会合点地址从环境变量来，拉起的沙箱 Pod 满足 restricted PSS，Pod 带标签 `sunmoonai.com/sandbox=true`（knowbench、knowbase 的入站策略按它放行）。镜像经 `make platform-build OBJECT=sandbox-platform/provisioner` 重建、锁改写成 `platform/sandbox-provisioner` 后，把 `services_sandbox_provisioner_enabled` 打开。

沙箱镜像是另一个只构建的对象 `sandbox-platform/sandbox`，锁在 `../sandbox/image.lock.yaml`。工作台经内网调供给器，不暴露公共 hostname；会合点地址由 config 注入（沙箱从 2026-10-18 起不再连 knowbase，待办账 111，KNOWBASE_MCP_URL 已撤）；工作台记录工具服务的地址与令牌由工作台在每次拉起时随规格给。

## 单轮纯指令执行单元

供给器按所有者和根 Task 预留一对独立 Pod。入口前缀为 `/v1/instruction-executions/{owner}/{task}`，使用已有的供给器服务鉴权。运营配置 `sandbox_instruction_control_origin` 为空时预留返回 503。启用时填写 KnowBench 的集群内 HTTPS 源。网关访问控制接口时使用平台公开 CA，访问供应商时使用系统信任库。

| 宿主动作 | 供给器接口 | 持久状态与重试 |
| --- | --- | --- |
| 预留并取得实例身份 | `POST /prepare` | 返回 apiserver 分配的网关 Pod UID。并发预留返回同一实例，原 UID 保存在回执卷声明上。 |
| 开启 Attempt 后绑定 | `PUT /{uid}/binding` | 宿主提交 `attempt`、`model` 和短期 `ticket`。网关核对自身 UID 后启动。相同绑定可续票。 |
| 查询网关、取得执行连接 | `GET /{uid}`、`PUT /{uid}/worker` | 网关就绪后才允许创建执行 Pod。宿主等到执行 Pod 就绪再用返回的 IP、47800 端口和本次专用令牌连接 Codex。重复获取沿用同一执行 Pod 与令牌。 |
| 允许本轮首个模型请求 | 再次 `PUT /{uid}/binding` | 宿主从真实 `turn/start` 回参取得 `turn` 后补入。第一次模型 POST 等待票据卷投影更新，最多 90 秒。续票保留已绑定轮次。 |
| 取消执行、核销用量 | `POST /{uid}/stop` | 宿主先在 KnowBench 取消并阻止新请求，再停执行 Pod。网关继续收取和补交原始回执。已放行请求的用量未知时保留预留和证据。 |
| 回收已结算实例 | `DELETE /{uid}`，待实例消失后 `DELETE /{uid}/proof` | 宿主依据 KnowBench 账本终态提交查询参数 `settled_attempt`。无绑定的空预留可省略。供给器核对 UID、绑定、停机与回收标记后才受理清卷。卷的实际释放时间由存储控制器决定。 |

Codex 的临时工作目录与 WebSocket 访问令牌只属于本次执行。供应商凭据、控制票据和回执卷都挂在网关内。执行 Pod 的出站策略只允许本次网关的 47801 端口。网关将终结用量持久化后向 KnowBench 交回，同一 Pod 内网关进程重启可补交。整个网关 Pod 丢失时保留回执卷和原绑定供核查。

供给器生命周期联调可在独立回环 kube-apiserver 上运行 `provisioner/tests/test_instruction_units.py`。设置 `INSTRUCTION_KUBE_TEST_PORT` 和 `INSTRUCTION_KUBE_TEST_DIR`，后者包含该临时服务的 `ca.crt`、`client.crt` 和 `client.key`。测试创建独立命名空间并注入就绪状态。集群网络验收另行实测执行 Pod 能连本次网关、不能直连供应商、其他任务网关和 DNS，并验证 runner 的入站连接以及停止后补收用量。
