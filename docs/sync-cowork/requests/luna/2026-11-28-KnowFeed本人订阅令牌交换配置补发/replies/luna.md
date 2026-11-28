# Luna 业务复验 · #141

2026-11-28 22:59（北京时间），在已有验收用 Windows Edge 会话中打开 KnowFeed 本人订阅页，使用原五粮液公告参数及同一幂等键提交。创建仍为 HTTP 503，错误码已由 `knowbase_unconfigured` 变为 `knowbase_unavailable`。本次未取得订阅 ID。KnowFeed API 对应请求关联号为 `f5fe1f2c-4dee-4c58-8d2f-d9f818035bad`。

定位到本人客户端调用 KnowBase 的 TLS 握手。KnowFeed API 容器已设置 `SSL_CERT_FILE=/etc/sunmoon/service/ca.crt`，但 HttpKnowbaseUser 创建 HTTPX 客户端时指定 `trust_env=False`，没有显式传入该 CA。同一容器对配置的 KnowBase 主机发起无凭据 GET，复现 `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`。显式加载该 CA 并保持代理禁用后收到 HTTP 响应，说明握手成功。

Cursor 的配置发布已完成。订阅业务验收保持开放，等待[客户端修复补发](../../2026-11-28-KnowFeed本人订阅客户端证书信任修复/request.md)。尚待核对创建、同键重送、暂停和恢复、范围同意和撤销，以及实际投递和归属。

#142 已修复本人订阅并通过创建、同键重送、暂停、恢复和授权撤销。真实投递等待巨潮渠道恢复。[完整业务回执](../../2026-11-28-KnowFeed本人订阅客户端证书信任修复/replies/luna.md)
