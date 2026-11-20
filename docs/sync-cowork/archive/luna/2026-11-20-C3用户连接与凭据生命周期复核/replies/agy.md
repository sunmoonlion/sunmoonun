# 评审回执：C3 用户连接与凭据生命周期复核

- 请求：[request.md](../request.md)
- 轮次：1
- 核对提交：
  - 工作位置：本地（`wsl-dev`，`/home/zymun/worktrees/luna`，分支 `luna`；前后端分别从固定提交干净快照导出实测）
  - `knowbench-app/knowbench-backend`：`6993698`（比较基线 `56cdbcb`）
  - `knowbench-app/knowbench-web-frontend`：`c506cda`（比较基线 `5bb7f29`）
  - `knowbench-app`：`1fc0b2c`（比较基线 `5daf4bc`）
- 结论：**通过（无阻断项，附 4 条代码完善建议）**。待办第 6 项（接入方案 §17.6 第 8 项）的按账号 OAuth 连接、PKCE 一次性回调、并发单次刷新占位、凭据密钥独立轮换、A2A `GetTask` 及方法连接预览在本地全链路测试环境均已实测闭环；真实供应商联调按约定留待具备真实应用注册、回调与账号条件时进行。

## 发现

### F01 [info] 4 项本地复跑与核对要点全覆盖（第 5 项真实供应商待专用条件单独记录）

1. **OAuth 发起、一次性 PKCE 回调、跨账号保护与日志/引用头脱敏**（`20261120_0047_connection_oauth.py`、`domain/workbench/connection_oauth.py`、`application/workbench/connection_oauth.py` `ConnectionOAuth.start` / `ConnectionOAuth.finish`、`sensitive_paths.py`、`capability_routes.py` `start_connection_oauth` / `finish_connection_oauth`）
   - `workbench_connection_oauth` 存储 SHA-256 摘要 `state_hash`、绑定发起人 `owner_actor_id`、`provider_id` 及 Fernet 加密后的 PKCE `verifier`，回调通过 `DELETE FROM workbench_connection_oauth ... RETURNING` 单次原子消费；校验 `iss`、配置快照摘要 `binding` 与固定 HTTPS `redirect_uri`。
   - 回调响应设置 `Cache-Control: no-store` 与 `Referrer-Policy: no-referrer`，`redact_sensitive_path` 剥离回调 URL 查询串避免 `code`/`state` 落日志；续授权（指定 `connection_id` 与 `revision`）若供应商返回不同 `account_id`，立即撤销新换凭据并拒绝，旧授权修订保持完整。
   - `OAuthProvider` 配置强校验固定 HTTPS 端点、同源 `account_url`、MCP 必带 `resource_indicator`、工具范围子集约束，且 OAuth 服务不再允许降级为手填 bearer 接入（`_discover` 与 `_dispatch_call` 均拦截）。

2. **并发刷新竞争、撤权/断开竞态、密钥独立轮换与未知认证结果**（`application/workbench/connection_oauth.py` `same_credential` / `credential` / `disconnect` / `call`、`infrastructure/workbench/connection_keys.py`、`infrastructure/workbench/capability_mcp.py:100-112`、`scripts/rotate_connection_keys.py`）
   - `credential` 在网络刷新前先持资产行锁写入加密占位 `"refresh_started"`，不递增修订；第二个并发请求等待当前刷新完成并复用结果；若期间用户断开（`disconnect` 优先清空本地 `secret` 标 `disconnected`，再尽力远端撤权并标记 `external_revocation_unconfirmed` / `provider_revoked`）、供应商返回 400 `invalid_grant` / 401 或换回的账号/`scopes` 变化，均撤销或置 `reauth_required` 并关闭 `default_selected`。
   - `ConnectionKeys` 基于 `MultiFernet` 将 `WORKBENCH_CONNECTION_KEYS` 与工作台其他密钥拆分，支持多钥轮换及移除旧钥后继续加解密；`RemoteMcp` 区分握手阶段 401/403（`CapabilityReauthRequired`）与 `tools/call` 已发出后 401（`CapabilityAuthOutcomeUnknown`），确保调用账保留 `unknown` 且不重发；旧调用批准严格绑定 `revision` 与 `account_id`，不随续授权转移到其他账号。

3. **MCP 与 A2A 双协议贯通及回环 HTTPS 实测**（`infrastructure/workbench/connection_oauth.py:13-140`、`application/workbench/connection_oauth.py` `ConnectionOAuth.call`）
   - `OAuthProvider(protocol="a2a")` 仅开放 `a2a_get_task` 并校验返回 `jsonrpc="2.0"`、匹配 `id` 及目标任务 `id` 与 `status.state`，裁剪其余多余字段，避免注入扩展负载。
   - `tests/test_connection_oauth_db.py` 已覆盖自签回环 TLS 服务（真实证书、SNI、表单参数、账号接口、刷新、A2A `GetTask` 与撤销）及 `rotate_connection_keys` 数据库实测。

4. **方法目录连接预览、消费者锁与网页 Chromium 实测**（`formal_method_catalog.py:843-890`、`connection_preview`、`method-connection-preview.tsx`、`capabilities-section.tsx`）
   - `connection_preview` 沿冻结候选静态展开，区分必须连接（`required`）、按选定步骤/候选变化的条件连接（`conditional`）以及未完全解析时的显式提示（`complete=False`），不自动绑定账号也不替代运行时批准；消费者锁、设置页组件及带 `selected account revision` 参数的 Chromium OAuth 跳转均在本次独立实测中通过。

## 代码合理性评价与完善建议（非阻断）

整体安全性与状态机闭环度很高（先本地原子脱密失效再尽力远端撤权、先占刷新锁防双刷、先判未知认证防重发均属最佳实践）。提出以下 4 条非阻断完善建议，推荐在接入真实供应商前或下一迭代改进：

1. **`application/workbench/connection_oauth.py` (`ConnectionOAuth.credential`) Access Token 过期判定缺少提前刷新余量（Clock Skew Leeway）**：当前判定 `creds["expires"] > now` 未保留提前缓冲窗口（如 30 秒）。若令牌在即将到期的几百毫秒内通过检查并在网络传输期间于外部网关过期，MCP `tools/call` 收到 401 后会触发 `CapabilityAuthOutcomeUnknown` 将外部调用标为未知结果并要求人工核查重授权。建议为 `creds["expires"]` 引入固定提前刷新缓冲（如 `now + 30`）。
2. **`application/workbench/connection_oauth.py` (`ConnectionOAuth.credential`) 等待并发刷新的 100ms 固定高频 DB `FOR UPDATE` 轮询压力**：当多个请求同时命中正在刷新的连接，其余协程在最坏 60 秒超时窗口内每 100ms 反复开启 DB 事务并对同一资产行加 `FOR UPDATE` 锁（单协程最多 600 次锁事务）。建议结合指数退避/抖动与进程内并发通知事件（Single-flight / `asyncio.Event` 唤醒）降低高并发下的 DB 行锁争用。
3. **`application/workbench/connection_oauth.py` (`ConnectionOAuth.finish`) Re-auth 发生修订变更时未对新换出的令牌调用 `revoke`**：在 `finish()` 中，若授权过程中用户在外部触发过连接刷新（仅 `revision` 变化、`status` 仍为 `active` 而非 `disconnected`），当前仅在 `asset["status"] == "disconnected"` 时执行 `await self.revoke(p, creds)`，会导致这批被丢弃的新凭据继续在供应商侧保持活跃。建议只要 `changed` 为真（新 `creds` 未入库生效），即统一尽力调用 `await self.revoke(p, creds)` 清理孤儿令牌。
4. **`infrastructure/workbench/connection_oauth.py:59-77` `AttributeError` 过宽捕获易掩盖代码缺陷**：`if response.status_code == 400: if json.loads(payload).get("error") == "invalid_grant":` 直接假定 `json.loads(payload)` 返回 `dict`，靠外层 `except (..., AttributeError, ...)` 兜底非对象 JSON。过宽捕获 `AttributeError` 可能掩盖开发期属性拼写错误，建议先解出局部变量并显式判断 `isinstance(err_body, dict)`，外层仅捕获精确的 `json.JSONDecodeError` / 网络异常。

## 验证结果与范围边界

- **KnowBench 后端（`6993698` 干净快照 + 独立 PG 16 tmpfs `127.0.0.1:55441`）**：
  - `.venv/bin/python -m pytest -q tests/test_connection_oauth_db.py tests/test_capability_routes_db.py tests/test_capability_mcp.py tests/test_formal_method_routes.py tests/test_method_capabilities_db.py tests/test_capability_runner.py`：**`96 passed in 34.21s`**。
  - Ruff（`56cdbcb..6993698` 涉及全部 Python 文件）：**`All checks passed!`**；Pyright（应用代码）：**`0 errors, 0 warnings, 0 informations`**。
  - Alembic：`20261119_0046 -> 20261120_0047 -> 20261120_0048 -> 20261120_0047 -> 20261115_0045 -> 20261120_0048` 升降级往返通过。
- **KnowBench 网页（`c506cda` 干净快照）**：
  - `pnpm check`（`tsc --noEmit`、`eslint .`、`check:i18n` 1373 键、`vitest run` **`500 passed (66 files)`**、`next build`）：**全部通过**。
  - Playwright Chromium（隔离端口 `PORT=3209 NEXT_PORT=3208 PAIR_FIXTURE_PORT=18280`，使用配对测试身份与合成供应商地址）：`CI=1 pnpm exec playwright test -g 'selected account revision'` -> **`1 passed (3.4s)`**（`rendering.e2e.ts:121` 通过）。
- **第 5 项真实供应商联调边界**：本地未接入真实第三方 OAuth 供应商（GitHub/Google/Slack/Notion/A2A 实端）的已登记回调与账号凭证，相关真实供应商（allowlist scope 交集、刷新轮换与撤权回执格式、`account_field` 稳定性）尚待专用测试凭据与回调域名就绪后补充验收记录。
