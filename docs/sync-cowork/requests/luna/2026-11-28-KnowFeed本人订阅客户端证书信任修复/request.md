# KnowFeed 本人订阅客户端证书信任修复

从 #141 的实际晋级源取 KnowFeed 后端。在 HttpKnowbaseUser 请求 KnowBase 的 HTTPX 客户端上保留 trust_env=False，显式传入使用已挂载服务 CA 建立的 SSLContext，并保留主机名验证。补丁见同目录 knowbase-user-ca.patch（相对 KnowFeed 后端仓根）。测试无 CA 配置时的现有路径、指定可信 CA 及不受信证书遭拒。仅发布受影响组件，沿用 #141 的身份配置和数据版本。Cursor 负责发布及部署回执，Luna 用原申请执行业务复验。

[现场复验依据](../2026-11-28-KnowFeed本人订阅令牌交换配置补发/replies/luna.md)
