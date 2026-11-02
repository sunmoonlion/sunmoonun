# 内部关系HTTPS

为Casdoor关系token和Knowledge内部摄入/检索提供cluster-local HTTPS transport，主机名由config的service_access_hosts引用app_namespace。运行调用者通过专用网络标签与CA验证，不能复用浏览器/管理员令牌。

knowbase 内部入口还精确路由 `/api/mcp/data` 到 knowbase-api；工作台中继数据读工具时走同一 HTTPS 主机，使用独立的短期 `knowbase-data` JWT。该路径由 knowbase 校验签名、调用身份与每次读取的授权范围，不经过 Casdoor 服务关系换票。不应靠开放整个 `/api` 或绕过网络策略直连 HTTP 恢复工具发现。

修改入口模板后必须由原生 components-render → 审查 → components-stage → 发布晋级生成并发布声明；只构建应用镜像不会更新路由。离线回归：`python3 -m unittest discover -s infrastructure/services/tests -v`（仓根执行）。发布检查须从真实工作台后端发起带短期 JWT 的 `tools/list`，确认数据目录完整；HTTP 200 本身不代表 JSON-RPC 成功，无凭据收到 401 也只证明已到达鉴权入口。

## 身份与责任

TLS私钥由prepare生成/备份后SOPS发布，仅Traefik消费；客户端只挂公共CA。域名、SAN、service/route与网络策略必须一起更新，不能把service_access_enabled=false当关闭现有route。

浏览器公网HTTPS、现有应用Casdoor HTTP backchannel和这里的关系服务HTTPS是不同调用路径，手册不把所有历史backchannel宣称mTLS。关系调用实际身份验收见common/backend/service-identity及Knowledge provider说明。

## 配置字段

当前值以[config.yaml](config.yaml)为准，手册维护字段职责，不再复制一套默认值。

| 字段 | 类型 | 维护条件 |
|---|---|---|
| `service_access_enabled` | 开关 | 部署/渲染准入；不代替停止、卸载或删除数据。 |
| `service_access_hosts.casdoor` | 文本/表达式 | 与客户端、TLS、入口/Service及网络策略联动；既有节点端口映射不能热改。 |
| `service_access_hosts.knowbase` | 文本/表达式 | 与客户端、TLS、入口/Service及网络策略联动；既有节点端口映射不能热改。 |
| `service_access_routes.<应用>` | `host`、`path` | 应用的内部入口（SDD 0027）：host 必须是 `<应用>-tls.<app_namespace>.svc.cluster.local`，path 是 `/api/internal/v1/<名>`，只路由到 `<应用>-api` 的这个前缀。每条一张独立证书（私有目录 `service-access-<应用>`，密文 `tls-<应用>.sops.yaml`），不动 casdoor、knowbase 共用的那张；共用证书已签发后不会重签，所以新入口不能加进 `service_access_hosts`。调用方的 `service_clients` 按 target 找这里。 |

## 部署、检查与退回

共同平台操作走[services维护](../../../../../infrastructure/services/README.md)的候选→审阅→stage/提交→发布晋级→bootstrap/check；组件没有另一套部署入口。版本/摘要取[物料锁](../../../../../infrastructure/artifacts/README.md)，运行namespace取共享site。关闭开关不会自动停服或清数据。

配置、身份或卷不符时保留现场；退回固定源的方法见[Flux维护](../../../../../infrastructure/flux/README.md)，schema/账号/持久数据不随Git自动回滚。日期结果与未覆盖范围在验收边界（已删，Git 历史 `53767f6a:docs/platform/verification.md`）。
