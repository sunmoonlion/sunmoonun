# Cursor 发布回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 结论：**已发布并生效**。[#141](https://jenkins.dev.sunmoonai.com:30443/job/release/141/) **SUCCESS**。Luna 可按本卡复验本人订阅链路。

## 发布结果

| 项 | 值 |
| --- | --- |
| Jenkins | https://jenkins.dev.sunmoonai.com:30443/job/release/141/ |
| 分支 | `luna-release-587` @ 配置尖端 `819066db4` |
| 参数 | `APPS=knowfeed knowbase`，`PIN=keep` |
| 批准 | admin @ 2026-11-28T22:49:00+08:00 |
| 部署提交 | `42171f4cfaeeeaa8d8e79ef11c1a7c40042b62a9` |
| 晋级指针 | `dfa223e1f9ad41d6c4e2a22d1fb68f799be0b88d` |
| 标签 | `release-20261128-4`（GitHub / Gitee 已推） |
| Flux OCI digest | `sha256:55dacd58f241046b52d2d53e88f26621af417b4c6b76e641faa2a59bfea00a3d` |
| 流水线回执 | `infrastructure/.build/release/141/release-141.20261128-225535.md` |

## 生效核验（现场）

| 检查 | 结果 |
| --- | --- |
| `knowfeed-identity-63689a74f1e2-v10` | Complete；`token_exchange: ["web"]`，`token_exchange_migrated: ["web"]` |
| Flux `knowfeed-identity` / `knowfeed-runtime` / `knowbase-runtime` / `platform` | Ready，同上 digest |
| `knowfeed-runtime` `KNOWBASE_USER_AUDIENCE` | `sunmoon-kind-knowbase-user-data` |
| `knowbase-runtime` `USER_TOKEN_APPS_JSON` | 含 `sunmoon-kind-knowfeed-web → knowfeed`，原三应用保留 |
| `application-check` knowfeed / knowbase | `failed=0`（knowbase 域断言 `passed: true`） |
| 库迁移 | 无（本轮仅配置 / 身份） |

## 前置失败与修复（摘要）

| 构建 | 结果 | 原因 |
| --- | --- | --- |
| #137 | ABORTED | 误用默认 `RELEASE_BRANCH=fable` |
| #138 | FAILURE | 独立分支名在应用仓不存在 |
| #139 | ABORTED | 身份 v9 Job 失败：交换迁移只认 `expireInHours==1`，KnowFeed 已是 24h → Flux 空等 |
| #140 | FAILURE | 代理仓残留在 `fable`，缺 `ci/verify-contracts.py` |
| #141 | SUCCESS | 放宽迁移为 `(1,12,24)` + `identity_revision` v10 |

配置提交：`e76133048`（audience / 交换开关 / apps JSON）。修复提交：`819066db4`（provision 迁移 + v10）。

## Luna

请用 sig-am 在真实订阅页重试原五粮液公告订阅（同幂等键），并回写 [#136 业务验收卡](../../2026-11-28-七项财务交付验收修复合并发布/replies/luna.md)。
