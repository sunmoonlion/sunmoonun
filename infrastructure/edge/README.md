# 公网边缘（东京 VM）

> 所在层：2 站点层——公网边缘（东京 VM 上的 frps 与 Traefik）（[总览表](../README.md)）

设计见 `docs/design/SDD/modules/0013-edge.md`。只在边缘机上运行；集群侧的 frpc 不在这里。

| 命令（在 `infrastructure/` 下） | 作用 |
| --- | --- |
| `make edge-plan` | 只显示将要的配置，不改任何东西 |
| `make edge-smoke` | 本机冒烟：临时令牌 + 临时 frpc + 替身后端，14 项检查，结束后全部清理；不对外、不用真令牌。和现网同一个单元名，`sunmoon-edge.service` 在跑就拒绝运行（边缘上线后别在边缘机上跑） |
| `make edge-deploy` | 渲染 `/etc/sunmoon/edge/` 并启动 `sunmoon-edge.service`（Traefik + frps，开机自启）。需要 root 0600 的 `/etc/sunmoon/edge/frp-token.yaml` |
| `make edge-deploy EDGE_EXTRA='--extra-vars edge_tls_mode=acme'` | 从 Let's Encrypt 测试环境切到正式证书（先在 staging 跑通，DNS 已指向本机、安全组已放行 80） |
| `make edge-status` / `edge-stop` | 看状态 / 停 |
| `make edge-firewall` | 只加 ufw 放行（1022、80、30443、7000），不启用；`EDGE_EXTRA='--extra-vars edge_firewall_enable=true'` 才启用默认拒绝。**先确认 1022 在放行列表里** |

文件：`config.yaml`（公开参数、镜像摘要、按域名的路径放行清单 `edge_path_allowlist`——键是短名如 `casdoor`，域名 = 短名.`site_domain`；`edge_domains`、`edge_https_port` 从站点文件的 `site_domain`、`public_port` 拼出，`edge_public_ip` 在站点文件里；make 的 edge 目标和 `smoke/run.sh` 都先加载 `SITE`）、`service.yaml`（Ansible）、`templates/`、`smoke/`。令牌、`frp.env`、`acme.json` 只在 `/etc/sunmoon/edge/`（root 0700/0600），不进 Git。访问日志关闭（安装凭证在 URL 路径里）。

**casdoor 只放行登录路径**：`edge_path_allowlist` 列了的域名只放行列出的路径，其余 403；casdoor 公网只留 OAuth 登录要用的页面、静态资源和三个接口，管理界面与管理接口不对公网（所有者本机经 hosts 直连本地集群，不受影响）。清单是实走登录录下来的，升级 Casdoor 或打开注册、找回密码、MFA 时要重录（做法与脚本见 [`scripts/results/opus-65-edge-casdoor-paths.20261016-1655.md`](../../scripts/results/opus-65-edge-casdoor-paths.20261016-1655.md)）。

## 增加公开应用域名

声明中的公开域名为 knowbench、knowmart、casdoor、relay。knowmart 是 2026-11-03 外部演示机商城 404 修复新增项；部署完成与否以发布回执为准。用户登录身份、电脑配对和沙箱令牌不决定 Host 是否有公网路由。

同时修改 `config.yaml` 的 `edge_domains` 与 `../../gitops/components/ingress-platform/frpc/config.yaml` 的 `frpc_domains`，并同步该组件 `prepare.yaml` 的域名范围断言。在集群宿主用 `make -C infrastructure components-stage OBJECT=ingress-platform/frpc` 生成并提交声明；域名参与 Pod 滚动摘要，不能只改 ConfigMap 而漏掉 Deployment。再由发布流程晋级 Flux 候选，并在边缘机对同一修订执行 `make -C infrastructure edge-plan`、`edge-deploy`。只发布应用镜像不会更新边缘路由。

`edge-deploy` 配置变化时会重启边缘服务，影响共用该入口的连接；在发布维护窗口内执行。不要在开发电脑运行 `edge-deploy`，也不要在现网边缘运行 `edge-smoke`。可在开发工位运行不访问网络、不使用凭据的模板回归：

```sh
infrastructure/.venv/bin/python -m unittest discover -s infrastructure/edge/tests -v
```

发布后从公网 DNS 路径检查新增域名的证书、HTTPS 页面、OAuth 回跳以及已有三个域名；Casdoor 管理接口仍应被拒绝，未开放的域名仍无路由。最后由演示机实际登录验收，不能用本机 hosts 直连成功替代。
