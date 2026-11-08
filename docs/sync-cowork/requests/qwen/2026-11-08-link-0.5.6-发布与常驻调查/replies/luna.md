# Luna 回执：Link 0.5.6 发布与 Windows 常驻调查

- 对应请求：[request.md](../request.md)
- 执行：2026-11-08，本地 qwen 工位，分支 qwen。
- 结论：安装包已发布并完成下载、平台电脑核对；常驻调查已交回。未改 Link 运行代码，未发布待发的 knowbench 业务代码，未调用付费模型。
- 授权调整：发布前发现原 Linux 候选为 dev-kind，与平台电脑的 edge-public 启动方式不相容（SITE_LAUNCH）；且只改输入配置不会使线上渲染产物生效。所有者明确回复“允许修正后继续发布”，批准同源码重建 edge-public Linux 包、更新摘要及必要渲染产物。本回执保留这些偏离原卡的依据。

## 一、发布

### 版本与范围

发布基线 `6778c4c82118b655df83d72a8690258d49cdcc17`；发布前 `flux-source-status` 确认线上实际 revision/digest 与基线相符。

- 发布提交 R：`97f3f32e9e3fbd0f2808638e172dbcec1065bd68`。
- OCI：`oci://harbor.sunmoonai.com:30443/platform/deployments-kind`。
- digest：`sha256:d22793161f6984a48af4f089751350fbc001d8f0a8b7b076811b35dd430ac940`。
- 隔离发布分支晋级记录：`0a7ef42d`；R 合回 qwen 的 merge：`de6b1579e03ac89b33422cb02733285dc6268052`。本回执所在提交同时将 qwen 的 flux-source.yaml 更新为上述 R/digest。

`git diff 6778c4c8 R --stat`：4 文件，33 行新增、33 行删除，全部位于 knowbench-backend 部署目录：

| 文件 | 必要变化 |
| --- | --- |
| agent-releases/config.yaml | Windows/Linux 版本、对象名、大小、包及清单摘要 |
| runtime/agent-releases.sops.yaml | 重新生成下载配置密文 |
| runtime/workload.yaml | 4 处由下载配置触发的配置摘要注解 |
| platform-computer/workload.yaml | Linux 取包地址、摘要、版本目录和脚本摘要 |

解密后只比较键与值是否变化，不输出秘密：唯一改变的明文路径为 `/stringData/WORKBENCH_AGENT_DOWNLOAD`。image.lock.yaml、后端 config.yaml、applications/sources.yaml 相对基线未改。`WORKBENCH_FIXED_AS_PLAN_OWNERS` 和 `WORKBENCH_OUTPUT_WRITE_ENABLED` 没有带入 R；它们仍留在 qwen 待后续整批发布。

### 安装包

源码均为 `795d5f831076e87d6b352b79601ac64e476ac2d2`，Link 0.5.6，Codex 0.155.1。

| 项 | Windows x64（原候选） | Linux x64（修正候选） |
| --- | --- | --- |
| 文件 | sunmoon-link-0.5.6-795d5f8-windows-x64.zip | sunmoon-link-0.5.6-795d5f8-edge-public-linux-x64.tar.gz |
| 字节 | 180990105 | 139189207 |
| SHA256 | d5e2de75c3e0cc165b824121923d7c0955beada841dc5ba728eeedefe896036a | 664748d735f0249c0170c723121a1e7a01523033e13c5643ab59be83b6ff1ccb |
| 清单 SHA256 | 3f32bb7b7e5c5d4f05a18cd91a8ee79a1c26dc1b129f236d4923e59ae60dc0a4 | d00b8cbf1f9e2b047466d789564dfd577d40bb377a8d9e013ca13335ce42ed9d |
| 站点 | dev-kind（Windows 用户电脑） | edge-public（平台电脑） |

Linux 在源码精确为 795d5f8 的隔离目录构建。与旧 dev-kind 包逐文件比对，应用载荷未改，仅 site/site.json 改变、site/ca.pem 移除；按平台电脑 `node --use-system-ca` 启动检查不再报 SITE_LAUNCH。旧候选保留在仓外，未上传替换既有对象。

### 上传、部署与核验

全部通过原生 Make / Ansible / Flux，未手工修改集群对象。

- Windows、Linux verify 分别 `ok=3, changed=0, failed=0`。
- 两次条件上传分别 `ok=18, changed=2, failed=0`；uploaded/readback 均 true；写身份不能读、读身份不能写的反向检查通过；未遇 409/412。
- 回执真源（本机 root 私有目录）：`/etc/sunmoon/services/sunmoon-kind/knowbench-agent-release-published.json`、`knowbench-agent-release-linux-published.json`。
- Stage 成功，flux-release：`ok=30, changed=9, failed=0`。
- flux-source-apply：`ok=38, changed=3, failed=0`；发布后 flux-source-status：`ok=16, changed=0, failed=0`，实际声明与 digest/revision 一致。
- 发布前两次只读查询非终态委托均为 `[]`，没有代停任务。
- API 实际下载描述已为 0.5.6，Windows 包/清单摘要均与上表一致。
- 在 Windows 当前默认浏览器打开正式 `/api/workbench/agent/package` GET，下载得到 `C:\Users\zymun\Downloads\windows-x64.zip`；未读取或导出浏览器凭据。完整文件大小、包 SHA256、清单 SHA256 与上表相同，清单 109 个文件逐个核对，差异 0。此为实际网页下载，不以 S3 读回替代。
- 平台电脑 init 日志：归档 SHA256 OK、verify-linux verified=true；实际 `/data/releases/0.5.6-664748d735f0` 清单摘要一致，133 个载荷文件逐一核对，差异 0。运行日志为 Link 0.5.6、exec-server ready、relay connected；用正确 HOME/SUNMOON_AGENT_HOME 查 status 也为 connected。
- 平台电脑取包流程会额外创建 `.verified`。直接对启动后的目录重跑严格“目录内容完全相同”校验会因该标记拒绝；因此补核所有清单文件和额外文件清单，额外仅 `.verified`，没有删标记或掩盖校验失败。第一次以 `/data/agent` 软链接执行校验也被工具按设计拒绝，后续改用真实目录核对。
- knowbench API/runner 的实际镜像仍为 `sha256:da0a1a48a333b0db34d4124ddb8fed2f7a409f666f6a91e8e420fe303063ebb3`；平台电脑镜像仍为 `sha256:ec14e4a591d7401ad222b579d745fa4c5c6e9292c28055c696b9671661f7823c`。本次只有安装包及配置滚动。

操作诊断：第一次 Linux verify 在 Make 跨 WSL mount namespace 时未保留 AGENT_LINUX_TGZ，上传前即因空路径停止；保留正确环境，在 host mount namespace 内仍以 zymun 调用相同原生 Make 入口后通过。首次 stage 因隔离目录缺并列 knowbench-app 而停止，补仓外只读来源链接后成功；没有改校验器或关闭门禁。

日志在本机 `/tmp/luna-link056-*.log` 及 `/home/zymun/sunmoon-probe-runs/link-056-resident-20261108/`，不含进仓凭据。Windows 已安装 0.5.6 的实例未重装、未重新配对。

## 二、Windows 常驻调查

证据提交：sunmoon-link `087c5c78cfb91894aa5650c2dfb0a9c7d82d0ab1`，目录 `scripts/results/link-0.5.6-resident-20261108/`。已推 GitHub、Gitee；只含原始计时、环境、后验检查和源码摘要，不改运行代码。

环境：Windows 11 家庭中文版 build 26300，AMD RYZEN AI MAX+ 395，KIOXIA KBG60ZNS1T02 SSD；包内 Windows Node 24.19.0 / Codex 0.155.1。Defender 实时防护原状态为 false，本轮未更改。

### 1. 保持输入打开的复现

用真实 windowsHelperArgs 参数和未改 helper，输入保持 30 秒、连发两条请求，两种模式均在 EOF 前返回：普通首次 126.780ms、第二条 127.214ms；提权首次 641.122ms、第二条 641.436ms（从启动开始计时）。随后持续逐条请求也成功。单条后 EOF 对照也完成。

**事实：本机本轮没有复现历史阻塞。未知：11-01 那台机器的历史根因。不能把本次成功说成所有机器恢复，也不能据此直接恢复旧实现。**

### 2. 输入、输出与缓冲

最小脚本启动即写标记，收到输入写第二个标记并立即向 stdout 回包。两模式 2 字节输入即有标记和输出；再分段发 1024、8192、65536、262144 字节（累计 336898）均流式返回，没有观察到凑满 8KiB 或 EOF 才转发。

精确官方 rust-v0.155.1 对应提交 `be2951ea34f0d295ed0becf97079f92fa5f6950e`：[stdio_bridge.rs](https://github.com/openai/codex/blob/be2951ea34f0d295ed0becf97079f92fa5f6950e/codex-rs/windows-sandbox-rs/src/stdio_bridge.rs) 的输入/输出各在线程转发；Read::read 每次有字节就发送，EOF 另行 close_stdin；输出 write_all 后 flush。8KiB 是读缓冲容量，不表示必须填满。debug_sandbox.rs 使用 stdin_open=true 后调用该桥接。**未找到“等 EOF 再转发”的设计，也未能从本次非复现定位历史卡在哪段。** 源码只在本机既有仓读取精确标签，未改 checkout，未去远程开发机下载。

### 3. 替代通道及隔离

- `network={enabled=false}` 下，127.0.0.1 回环连接两种模式均通；没有测试或声称可访问外网。
- 默认 ACL 的 Windows 命名管道两模式均 EPERM，未为实验放宽 ACL；不能推断所有命名管道方案不可行。
- 第一版“socket → 子 helper”适配：普通模式已连接但 RPC 超时，提权模式正常，普通模式原因未明，失败保留。
- 随后“同一受限进程内将 IO 接到 socket，再导入未改 helper”的临时适配器，两模式真实文件 RPC 均通过。中间一次探针转义错误导致 SyntaxError，明确记为探针错误，修正后的记录单列。
- 原生目录外写探针两模式均 OS EPERM。实际 helper 拒绝目录外写、读取探针构造的假 auth.json 和假 .sandbox-secrets。后者属于 helper 路径策略验证，**不等于证明任意沙箱代码都无法读取真实凭据**。未读取、导出任何真实凭据。
- 后验逐一核对 150 个写入文件，均为预期 4096 字节；没有目录外产物，假敏感文件未变。

### 4. 一次收多条再 EOF

每组 3 轮；单位 ms。批次计时从 spawn 到观察到进程退出，每 100ms 轮询退出，带 0–100ms 观测开销。

| 模式 | 条数 | 批次中位/最大 | 折算每条中位/最大 |
| --- | ---: | ---: | ---: |
| 普通 | 10 | 221.948 / 224.981 | 22.195 / 22.498 |
| 普通 | 50 | 221.395 / 224.603 | 4.428 / 4.492 |
| 提权 | 10 | 767.463 / 771.100 | 76.746 / 77.110 |
| 提权 | 50 | 771.181 / 772.648 | 15.424 / 15.453 |

全部请求有响应且无错误。

### 5. 常驻暖态计时

每类 3 轮，metadata 每轮 50 条、read 20 条、write 10 条；以下是单次往返中位/最大 ms，不含首启。

| 通道/模式 | metadata | read | write |
| --- | ---: | ---: | ---: |
| stdio 普通 | 0.510 / 1.054 | 0.675 / 1.112 | 1.146 / 2.775 |
| stdio 提权 | 0.554 / 1.061 | 0.859 / 1.571 | 1.428 / 2.231 |
| 回环 普通 | 0.457 / 1.612 | 0.615 / 1.403 | 1.027 / 2.407 |
| 回环 提权 | 0.491 / 1.287 | 0.783 / 1.376 | 1.384 / 2.418 |

另一轮 stdio 冷首请求普通 111.820ms、提权 683.091ms；空闲 300ms 后第二条约 1.214/1.314ms。上一卡真实 WindowsFiles 封装中 metadata 每条中位普通 561.177ms、提权 1066.344ms，含启动和进程清理。本轮直接 helper 暖态与其测量边界不同，不能用比值宣称用户任务会按同等比例提速。

建议：批量和常驻都有进一步实现价值，但先评审目录授权、并发、取消、回收、断线重连和历史故障回归，再由所有者决定；本轮不替所有者选方案，不直接回退到旧常驻代码。

## 三、一直 running 的后台命令

已核实是上轮升级 PowerShell 已结束后，Linux interop 包装进程仍持有句柄等待；只终止该 Linux 包装 PID 2144205，工具会话以 143 退出。操作前后 Windows Link PID 28412 均在线、relay connected，未杀 Link/托盘或用户任务。本轮探针均已结束，没有遗留常驻探针进程。

## 交回

本回执与晋级记录验证、提交后按默认规则推送 qwen 的 GitHub、Gitee；以随后的实际推送输出为准。远程需 pull qwen 后才可看到，不代发起者结案或归档。
