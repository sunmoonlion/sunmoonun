# KnowFeed 本人订阅配置补发

Cursor 负责发布，Luna 负责业务复验。基线为 #136；从实际晋级指针取最新部署配置。

sig-am 在 KnowFeed 订阅页通过本人会话提交一份五粮液公告订阅，两次使用同一幂等键，均为 HTTP 503，业务码 `knowbase_unconfigured`，没有收到订阅 ID。现场 KnowFeed API 的 `knowbase_user_audience` 为空，后台 `supply_relation()` 已配置。用户入口在 `get_web_knowbase_token` 就返回 503，尚未尝试交换令牌。KnowBase API 的 `USER_TOKEN_APPS_JSON` 也缺少 KnowFeed Web 映射。#136 发布声明中的 KnowFeed 身份注册 Job 的 `TOKEN_EXCHANGE_SURFACES` 为空列表。

## 发布内容

1. 在 KnowFeed 后端的部署源配置中，使用现有 KnowBase 用户数据 audience，将 `domain_env.KNOWBASE_USER_AUDIENCE` 对齐为 `sunmoon-kind-knowbase-user-data`。
2. 在同一部署源中启用 Web 用户令牌交换。按当前晋级版创建新的身份配置 Job 修订并核对实际生成物。只对 KnowFeed 的 Web 客户端开通本人令牌交换。
3. 在 KnowBase 后端的 `domain_env.USER_TOKEN_APPS_JSON` 追加 `sunmoon-kind-knowfeed-web → knowfeed`。沿用订阅端点原有调用方限制与本人授权。核对现有应用映射全部保留。
4. 渲染、检查并发布受影响的身份及运行配置，记录 Job 完成、所用版本和应用配置生效的回执。无须为此次配置补发变更数据库或重建业务镜像。沿用现有受众应用与服务身份。

## Luna 复验

用 sig-am 从真实订阅页重试原订阅，核对创建、同键重送只得一个订阅、暂停／恢复、本人范围同意与撤销结果，核对投递与归属。实际跑通后回写原 [#136 业务验收卡](../2026-11-28-七项财务交付验收修复合并发布/replies/luna.md)。

已附基于 #136 部署提交 `dc6eb7cec` 的[两处部署源配置补丁](136-部署源配置.patch)。新身份 Job 修订在此基线为 v9，晋级线若前移须按实际修订渲染。
