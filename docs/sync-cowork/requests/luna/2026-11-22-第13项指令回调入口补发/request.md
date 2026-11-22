# 第 13 项指令回调入口补发

**执行者为 Cursor，目标为 sunmoon-kind。优先处理。** 本卡交付内部入口及不计费的路由复验。L105、三道原题和业务复核沿用[第 13 项原卡](../2026-11-22-第13项请专家入口与回炉验收/request.md)。如下一批尚未启动，可把 `traefik` 并入其同一发布窗口；若已启动，单发此目标即可。

## 发布依据与范围

11 月 22 日 19:05，Luna 在运行中的集群核实，供给器已配置内部 HTTPS 地址和 CA。为该主机服务的唯一 Ingress 只有 `knowbot-runtime` 与 `method-skill-center/functions` 两个前缀。经同一 CA 验证 TLS 后，无凭据 POST 到 `/api/internal/v1/instruction-control/claim` 和 `/receipt` 均为 Traefik 404。直接核对内部 KnowBench API 上对应的两个 POST 都为 401，两条 GET 都为 405。这证明当前入口无法把网关请求送达处理程序。历史尝试的原始异常未留存。

1. 从已晋级的 #108 基线上准备发布分支，核对其实际指针及镜像锁。内部路由声明来自 `a01916894`（#108 的发布分支源码已含此前缀）；带入本次平台发布目标与暂存校验 `116dfd3ab`。单发使用 `APPS="traefik"`、`PIN=keep`，常规 Jenkins 人批。合发则在原目标中显式加 `traefik`。无需调整用户的模型连接和报价。
2. 查看第 4 阶段的差异，确认 `knowbench-service-access` 在原有规则旁新增 `/api/internal/v1/instruction-control`，类型 `Prefix`，后端 `knowbench-api:http`，沿用原内部主机和证书。若 Jenkins 报无差异，须用下方现场检查核实实际状态。候选中若出现意料之外的其他共享入口或凭据变更，在人批前核对来源。
3. 发布完成后先核对 Flux 摘要、Traefik Ready 和实际 Ingress。再使用下面的不计费探针。第一段在可信工位开本机端口转发，第二段在另一终端执行。使用目标集群的 kubeconfig，端口被占用时两处一起替换。

```sh
kubectl -n ingress-platform-dev port-forward --address=127.0.0.1 svc/traefik 18443:443
```

```sh
(
  set -eu
  ca=$(mktemp)
  trap 'rm -f "$ca"' EXIT
  kubectl -n sandbox-platform-dev get configmap instruction-control-ca -o 'jsonpath={.data.ca\.crt}' > "$ca"
  host=knowbench-tls.app-platform-dev.svc.cluster.local
  for operation in claim receipt; do
    status=$(curl --noproxy '*' --silent --show-error --max-time 8 --cacert "$ca" \
      --connect-to "$host:443:127.0.0.1:18443" -o /dev/null -w '%{http_code}' \
      -H 'Content-Type: application/json' --data '{}' \
      "https://$host/api/internal/v1/instruction-control/$operation")
    printf '%s %s\n' "$operation" "$status"
    test "$status" = 401
  done
)
```

4. 将 Jenkins 号、晋级摘要、实际 Ingress 前缀和两条 HTTP 状态写到本卡 `replies/cursor.md`。两条均为 401 后，回原卡按手册用 sig-am、原申请和有效报价重试一笔。同步记录网关到控制面的 claim、供应商用量、receipt、运行号和业务输出；只记录元数据。若仍失败，按时间线记录最先失败的环节及状态码、Pod 终止原因与重启次数，保留原尝试并交回。无凭据的请求返回 401 只验证路由与认证边界，实际试跑另看 L105 与结算。
