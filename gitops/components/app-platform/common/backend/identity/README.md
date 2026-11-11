# 浏览器身份与公开注册

Web 与 Admin 的 OIDC 身份由 `provision.py.j2` 校验。Web 用户属于 `sunmoonai`，管理端属于 `built-in`；客户端密钥、精确回调、单点登录和令牌交换的现有校验不变。

## 邮箱验证码注册

所有者 2026-11-10 选择公开注册：不需要邀请码，邮箱验证码通过后才建号。入口是 KnowBench 登录页中的注册链接；已有的 `/api/auth/web/signup` 继续承担 OIDC 注册跳转，不另建账号库。

配置真源在 [KnowBench 后端配置](../../../knowbench-app/knowbench-backend/config.yaml) 的 `public_signup`。只有 KnowBench 可以声明这个开关，其它网页端与所有管理端继续关闭独立注册。新账号沿用普通用户组织和各应用已有的单点登录。

选择阿里云华东 1（杭州）邮件推送，SMTP 地址 `smtpdm.aliyun.com`、端口 465、隐式 TLS。用户名与发件人相同，配置为 `noreply@notify.sunmoonai.com`。发信域名验证和 SMTP 密码由所有者在阿里云控制台维护。

`signup.py` 只通过 Casdoor API 配置：

- 关闭 `app-built-in` 自带的管理员组织注册。
- 创建本应用专属 SMTP 提供方，限定用于 `signup` 发码；不接管名称不同的已有提供方。
- 注册项为邮箱、用户名、密码与确认密码。邮箱必填且启用验证码；没有邀请码和手机号项。验证码校验、过期、一次性使用与用户创建由 Casdoor 执行。
- 保持密码登录和现有 SSO，显示登录页的注册链接；不开放验证码登录。
- Casdoor 同一邮箱重发间隔为 60 秒。公网边缘对发码接口额外采用每 IP 每分钟平均 1 次、突发 3 次限流；管理 API 和直接发送邮件 API 仍不对公网开放。

API 字段按 [Casdoor v4.12.0](https://github.com/casdoor/casdoor/tree/v4.12.0) 的 `controllers/account.go`、`controllers/verification.go`、`object/application_item.go`、`object/email.go` 核对；实际运行镜像仍以平台物料锁为准。离线检查不能代替锁定镜像上的真实浏览器验收。

## 私有输入与部署

SMTP 密码是专用密码，不是阿里云登录密码或 AccessKey。文件只有一行密码，允许编辑器留下的末尾换行；不能带空格。只在部署机保存：

- 主文件：`{{ services_config_dir }}/casdoor-smtp-password`。
- 备份：`{{ services_backup_dir }}/casdoor-smtp-password`。
- 两份必须为 root 所有、权限 `0600` 的普通文件，不接受符号链接；已有两份必须逐字节相同。缺少主文件时可从备份恢复，两份都缺少时停止，不生成密码。

目录从站点配置派生，不能把开发站点路径直接当作生产路径。当前 kind 站点主文件为 `/etc/sunmoon/services/sunmoon-kind/casdoor-smtp-password`。`signup-prepare.yaml` 在渲染前读取并创建不覆盖的独立备份；涉及口令的任务均为 `no_log`。

口令只进入现有 `<app>-identity-provision` 的 SOPS Secret（键 `smtp-password`），仅挂载给身份初始化 Job，不注入应用 API、前端或公共 ConfigMap。Job 会写入 Casdoor 提供方的持久配置，因此 Casdoor 数据库备份也必须按凭据处理。API 会屏蔽返回密码，重跑会重新写入明确提供的密码，不把 `***` 当成一致性的证据。

发布仍走 `infrastructure/Makefile` 的原生入口：`platform-stage OBJECT=app-platform/knowbench-app/knowbench-backend` 准备声明，审阅后按既有 Flux 发布流程发布并晋级；公网入口另用 `edge-deploy` 更新。不能只更新其中一端。

身份 Job 使用代次 `v7`；没有密码时不能完成正式 stage。2026-11-11 已在 kind 开发站点完成私有输入准备、原生 stage、Flux 候选发布与晋级，以及公网边缘更新。邮件接口返回成功，所有者确认测试邮箱实际收到验证码；新账号在浏览器完成注册及跨应用登录仍待人工验收。部署与检查边界见 [发布回执](../../../../../../scripts/results/qwen-public-signup-20261111.json)。其它站点不能据此视为已部署。

本次完整后端 stage 同时生成了此前未发布的业务开关、TLS 和安装包配置差异。审阅后仅提交 renderer 生成的两份 identity 文件，其余本次生成的 runtime 差异恢复到发布前状态。本次渲染一致性验证范围为身份文件；整个组件的渲染一致性仍需在处理既有差异后检查。以后完整 stage 仍须审阅这些已有差异，不能随邮件配置顺带发布。

发信依赖 Casdoor 到 `smtpdm.aliyun.com:465` 的可用 TLS 路径。此次 Windows FlClash 全局模式下，WSL 和 Casdoor 解析到 Fake-IP，TLS 握手返回 EOF；所有者切换规则模式后公网注册发码成功。排查时先检查出站路径，不关闭证书验证，也不把诊断时查到的公网 IP 固定进 SMTP 配置。

上线须实走：注册页可达、验证码邮件送达、空/错验证码被拒、正确验证码建号且邮箱已验证、重复邮箱被拒、无需邀请码、普通账号跨应用登录、管理组织注册被拒、快速重复发码受限。应从公网浏览器走同一 OIDC 流程，确认没有被边缘拒绝的必需路径；只补实测必要路径，不开放整个 `/api/`。回执 `smtp_delivery_verified: false` 明确表示初始化 Job 没有发送真实测试邮件。

## 关闭与密码轮换

关闭时保留 `public_signup`，将 `enabled` 改为 `false`，递增 `identity_revision`，重新 stage 和发布。Job 会关闭注册并卸下该应用的邮件提供方（只关 `enableSignUp` 不能保证发码接口停用）；同名 NetworkPolicy 更新为空出站规则。不会删除用户、邮件提供方或历史记录，现有用户仍能登录。不能直接删除整个配置字段来回退，否则专门的关闭逻辑不会执行。

密码轮换时，先在阿里云设置新 SMTP 密码，再同步更新主备文件、递增身份 Job 代次并重新 stage、发布；只更新 Secret 不会更新 Casdoor 的持久配置。轮换期间发码可能短暂不可用。

## 离线验证

使用平台锁定的 Python 工具环境，在仓根串行执行：

```bash
python -m unittest discover -s gitops/components/app-platform/common/backend/identity/tests -v
python -m unittest discover -s infrastructure/edge/tests -v
```

覆盖注册与管理员边界、缺口令时停止、提供方失败不首次启用注册、重复执行与口令更新、关闭注册及卸下提供方、发码限流、KnowBench Job 换代、另外五个应用身份清单逐字节不变。测试使用合成凭据与模拟 API，不发送真实邮件。
