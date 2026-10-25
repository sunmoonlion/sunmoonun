# fable-0042-平台-1 回执：Casdoor 身份注册——知识库三应用开令牌交换、网页端令牌 12 小时、knowbase 加 audience 目标应用（Fable 经隧道在本地做，临时 Casdoor 在远程机）

WS=fable，分支 fable，提交 `62c3c1ba`。这是 Opus 10-23 至 10-24 那批（0037、0042、0018、link 0.5.2）上线要的平台配置第 1 步；总清单与对 Opus 的三条代码要求在本地 `~/平台配置-给Opus的接口清单-20261025.md`。本页没有口令、令牌、密文。

## 一、改了什么

| 文件 | 改动 |
| --- | --- |
| `gitops/components/app-platform/common/backend/identity/provision.py.j2` | 网页端 `grantTypes` 按应用加 token-exchange（环境变量 `TOKEN_EXCHANGE_SURFACES`）；网页端 `expireInHours` 1→12（所有者 2026-10-25 定），管理端仍 1；第四种显式迁移 `token_exchange_migrated`：只在现有应用恰为改版前样子（只授权码、1 小时）且差异只在这两项时更新；`AUDIENCE_APPLICATION` 给出时建/核一个只作 audience 的目标应用（用户组织、无回调、不开登录）；回包多四个字段 |
| `identity/workload.yaml.j2`、`prepare.yaml` | Job 加两个环境变量；断言 `identity_token_exchange` 是布尔、`identity_audience_application` 名字按 `sunmoonai-<应用>-user-data` / `<集群>-<应用>-user-data` |
| 六个后端 `config.yaml` | `identity_revision` v5→v6（改了脚本就升代次，C-R11，C2b #11 的教训）；knowbench、knowlab、knowmart `identity_token_exchange: true`；knowbase `identity_audience_application` |
| `platform-stage` 六应用的产物 | `identity/workload.yaml`（v6 名、新环境变量、新脚本）；`runtime/workload.yaml` 只有 `config-sha256`；8 个 sops 文件里 7 个解密明文 sha256 相同（重加密噪声），knowbench `runtime/agent-releases.sops.yaml` 明文变了 1 个键 `WORKBENCH_AGENT_INSTALL_SCRIPT_TEMPLATE`——来源是 Opus `3fdbef6d` 改了安装脚本模板（0.5.2 叫法）没有重新暂存，随 0.5.2 包一起上线 |

## 二、临时 Casdoor 实验（远程机 docker，`casbin/casdoor@sha256:bf84c727d59d…`，与正式同镜像；postgres:16-alpine；独立网络，只听 127.0.0.1:38000；测完容器已删）

脚本与日志：远程 `~/sunmoon-probe-runs/casdoor-lab-20261025/`（`lab-run.sh`、`lab-run.1–4.log`）。注册脚本直接拿模板渲染（只换 `{{ application_name }}` 与两个输入文件路径），不是手写的替身。

| 步 | 做法 | 结果 |
| --- | --- | --- |
| 1 | 旧脚本（fable `69a9971b` 的模板）注册 knowbench、knowbase、tpl 的网页端与管理端（旧样子：只授权码、1 小时） | created web、admin |
| 2 | 新脚本，knowbench `TOKEN_EXCHANGE_SURFACES=["web"]` | `token_exchange_migrated: ["web"]`，created [] |
| 3 | 新脚本再跑 | `token_exchange_migrated: []`（幂等） |
| 4 | 新脚本，tpl 不开交换 | `token_exchange: []`，`token_exchange_migrated: ["web"]`（只迁 12 小时） |
| 5 | 新脚本，knowbase 带 `AUDIENCE_APPLICATION` | 第一次建成后读回与期望不一致：Casdoor 把空的 `grantTypes` 改写成 `["authorization_code"]`；模板按实测改成期望授权码（没有回调、不开登录，这条流程走不通），之后 `audience_created`、再跑核过 |
| 6 | 真换令牌（实验脚手架：临时给两个网页端加 password 授权取用户令牌，测完还原） | 用户令牌 `aud=[knowbench-web]`、12.0 小时；换出的令牌 `aud=["sunmoon-kind-knowbase-user-data"]`、`azp=sunmoon-kind-knowbench-web`、`sub` 同用户、12.0 小时；tpl 换：`unsupported_grant_type`；audience 应用 `client_credentials`、`password` 都 `unsupported_grant_type` |

## 三、本地渲染

`components-render` knowbench-app、knowbase-app 都 failed=0；渲染出的 identity Job 名 `*-identity-provision-v6`，knowbench 环境变量 `TOKEN_EXCHANGE_SURFACES=["web"]`、`AUDIENCE_APPLICATION=null`，knowbase `TOKEN_EXCHANGE_SURFACES=[]`、`AUDIENCE_APPLICATION={name, client_id}`。推送后的 render-check 结果记在第 2 步回执。

## 四、留下的

- 上线时六个应用的身份 Job 都会跑一次（v6）：三家网页端迁出交换授权与 12 小时，另三家只迁 12 小时，knowbase 建 audience 应用。失败就停在那一段，不动别的。
- 所有者 10-25 的两个决定已落：网页端令牌 12 小时；平台配置在对齐之后、发版之前做。
