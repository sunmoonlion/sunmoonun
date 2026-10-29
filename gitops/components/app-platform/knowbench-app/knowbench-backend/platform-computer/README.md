# 平台电脑

集群里的 Linux「电脑」：跑与用户同一份代码的本地代理（Linux 包，sunmoon-link 仓 `build-linux.mjs` 打出，版本与摘要钉在 [agent-releases 配置](../agent-releases/config.yaml) 的 `linux` 一节），一人一台配给名单里的平台人员账号（叫法 10-29：账号不分类型，电脑配给账号）。原来叫「分身测试的测试电脑」（[SDD 0027](../../../../../../docs/design/SDD/modules/0027-knowbot-first-path.md) §3.4），只有一台、配给 knowbot-tester；平台测试改在作者的账号与电脑上跑（decisions ⑯）之后这台不撤，改作平台电脑，仍配在 knowbot-tester 上，名单第一项就是它。

配置是[后端 config](../config.yaml) 的 `platform_computers`：一份模板加名单 `computers`，名单里几个开几台，每台一个 Deployment、各自的持久卷。

| 名单字段 | 含义 |
| --- | --- |
| `name` | 进对象名：Deployment `knowbench-platform-computer-<name>`，代理在工作台里登记的机器名也用它（第一次 `agent init --name`） |
| `account` | 配给谁；只进配对提示，配对本身由那位用自己的账号在工作台「接入电脑」里确认 |
| `claim`（可选） | 沿用的持久卷名；不写就建 `knowbench-platform-computer-<name>`。原测试电脑那台写 `knowbench-test-computer` |

- **取包**：初始化容器用发行包的只读身份（`knowbench_release_reader`，只有 GetObject）从私有桶取包，核归档摘要，解到持久卷，再用包里的 `installer/verify-linux.mjs` 按清单逐字节核对。包要先上传并读回核对（`make -C infrastructure agent-release-linux-upload AGENT_LINUX_TGZ=/绝对路径.tar.gz`，回执 `knowbench-agent-release-linux-published.json`），否则 stage 停下。
- **运行**：镜像复用沙箱镜像（钉好的 Node 24.21.0 与 Codex），非 root、只读根文件系统、不提权；代理不开外层沙箱（容器本身就是隔离）。工作区 `/workspace`，代理配置在持久卷 `/data/home`。
- **配对**：第一次启动没有凭据时，容器日志里显示连接码，配给的那位用自己的账号在工作台「接入电脑」里确认；凭据落在持久卷上，重启不用再配。**换了卷就要重新确认连接码**，所以原来那台在名单里写 `claim: knowbench-test-computer`，沿用原卷。
- **网络**：只放行 DNS、对象存储（取包）和公网边缘 `relay.sunmoonai.com` / `knowbench.sunmoonai.com` 的 30443（像用户家里的电脑一样经边缘连进来，用系统信任的证书）。模型不在这里调（在该账号的云端沙箱里），所以没有别的外网出口。
- **清理**：每小时删一次工作区里 7 天前的底稿目录（`/workspace/底稿/对话-*`）与 7 天没动的 `runs/*`；委托与交回物由 knowbench 自己 7 天后删。
- **一台一次只跑一个测试**（待你决定第 8 条第 3 项）：开跑前会清掉 `runs/` 下别的目录，同一台上并发会互相删目录；排队由 knowbench 做，这里不管。

本目录的 `workload.yaml`、`download.sops.yaml`、`kustomization.yaml` 由 stage 生成，不手改。

## 从测试电脑改过来那一次发布

集群是 prune: false，旧对象不会自动删；而同一个 RWO 卷在同一节点上两个 Pod 都挂得上，旧的 Deployment 不停，两份代理会抢同一份配置。所以晋级前先精确删旧对象（PVC `knowbench-test-computer` **照留**，新的 Deployment 接着用它）：

```bash
K="kubectl -n app-platform-dev"
$K scale deployment knowbench-test-computer --replicas=0
$K delete deployment knowbench-test-computer --ignore-not-found
$K delete configmap knowbench-test-computer-scripts --ignore-not-found
$K delete secret knowbench-test-computer-download --ignore-not-found
$K delete networkpolicy knowbench-test-computer-egress --ignore-not-found
kubectl -n flux-system delete kustomization knowbench-test-computer --ignore-not-found   # 旧阶段；deletionPolicy Orphan，不动它管过的对象
$K get pvc knowbench-test-computer   # 必须还在
```

发完要看到：`knowbench-platform-computer-knowbot-tester` `1/1 Running`，日志里没有新的连接码（配对凭据还在原卷上），knowbot-tester 的「我的电脑」里它仍在线。
