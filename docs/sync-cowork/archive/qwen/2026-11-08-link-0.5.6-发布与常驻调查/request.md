# link 0.5.6 发布，及 Windows 常驻辅助进程调查

- 类型：发布（第一节）＋ 验证（第二节）
- 状态：已结案（2026-11-08）
- 发起身份：qwen（使用 Opus）
- 执行身份：luna
- 主工位：**本地** `~/worktrees/qwen`；第二节在所有者的 Windows 测试机上做
- 仓与分支：sunmoonun（部署配置）、sunmoon-link（只读），都是 qwen
- 发布的 link 版本：sunmoon-link `795d5f831076e87d6b352b79601ac64e476ac2d2`（0.5.6），包用上一张卡已出好的两个候选包（摘要见下）
- 线上基线：sunmoonun `6778c4c82118b655df83d72a8690258d49cdcc17`（release #85，`infrastructure/environments/kind/flux-source.yaml` 记的 revision）
- 回执：replies/luna.md
- 前一张卡：[archive/qwen/2026-11-08-link-0.5.6-windows实测](../../../archive/qwen/2026-11-08-link-0.5.6-windows实测/request.md)（出包与计时，已结案）

两节互不依赖，可以先做哪节都行。

## 一、发布 link 0.5.6

### 目标

把线上下载的 Windows 安装包和平台电脑用的 Linux 包从 0.5.5 换成 0.5.6。0.5.6 只比 0.5.5 多账 187 的修复（Windows 上执行服务没起来时第一次文件操作失败，之后就一直坏）。

**这只是换安装包，不是 knowbench 发版**：后端镜像（`image.lock.yaml`）不动，0050、0051 等没发的后端代码不会上线。

### 包

| 平台 | 文件 | 包 SHA-256 | 清单 SHA-256 |
| --- | --- | --- | --- |
| Windows x64 | `sunmoon-link-0.5.6-795d5f8-windows-x64.zip`（180990105 字节） | `d5e2de75c3e0cc165b824121923d7c0955beada841dc5ba728eeedefe896036a` | `3f32bb7b7e5c5d4f05a18cd91a8ee79a1c26dc1b129f236d4923e59ae60dc0a4` |
| Linux x64 | `sunmoon-link-0.5.6-795d5f8-linux-x64.tar.gz`（139190711 字节） | `ecad34eb057e6440a2fddb6105a967797baebb99a26f522a5f37b8c1a5096391` | `8a58ab0a6deabbdc80c7278945f135b207a58cc615a82c8d1c76501fc418018f` |

产物在本地 `/home/zymun/sunmoon-probe-runs/link-056-20261108/`。用之前先核摘要和上表一致；不一致就停下报告，不重新出包。

### 唯一要注意的：发布内容只能比线上多安装包这几行

qwen 分支上，线上（`6778c4c8`）以后部署配置只多了 `knowbench-backend/config.yaml` 里两个开关：`WORKBENCH_FIXED_AS_PLAN_OWNERS`（SDD 0050）和 `WORKBENCH_OUTPUT_WRITE_ENABLED`（要和 knowbase `7875a8b` 同批）。它们要等 knowbench 那一批发，**这次不能带上线**。所以不能直接从 qwen 的最新提交发。做法：

1. 以 `6778c4c8` 为底做一个发布提交 R，**只改** `gitops/components/app-platform/knowbench-app/knowbench-backend/agent-releases/config.yaml`：Windows 和 `linux` 两节的 `version`、`source_revision`、`object_key`、包摘要、清单摘要、`size_bytes`（照 0.5.5 那次 `b861470f2` 的改法）。
2. 发布前核：`git diff 6778c4c8 R -- gitops` 只出现这一个文件。多一行都不发。
3. 照 `docs/project-guide/repos/sunmoon-link.md`「发版」和 `agent-releases/README.md` 的顺序：`agent-release-verify` → `agent-release-upload`（Windows）；`agent-release-linux-verify` → 对应的 Linux 上传 → 读回核对 → 从 R 走现有的 stage、`flux-release`、晋级、`flux-source-apply`。
4. 晋级 `flux-source.yaml` 指向 R 以后，把 R 合进 qwen（`git merge`，预计没有冲突，因为 qwen 在线上以后没动过这两个文件），再在 qwen 上提交晋级记录，推送 qwen。这样 R 留在 qwen 的历史里，下次 knowbench 发版从 qwen 发时，安装包是 0.5.6，两个开关照原计划跟那一批走。

先用 `flux-source-status` 核线上实际的 revision 是 `6778c4c8`。不是的话停下报告，不换基线。发布链拒绝从 R 发（比如要求必须是分支最新提交）时，也停下报告，不绕过。

### 发布前后

- 发布前看一眼有没有正在跑的委托：配置一变 API 会按发布链重启，正在跑的会受影响。有的话等它跑完，或者报告所有者。
- 发布后核：
  - 登录后 web端下载接口回 0.5.6 和上面的摘要；完整下载一次，核两个摘要。
  - 平台电脑按现有检查起来，读到的是 Linux 0.5.6。
  - 你那台 Windows 测试机已经装好 0.5.6，不用重装。

### 停止条件

摘要不符、上传 412/409、读回失败、`diff` 多出别的文件、线上 revision 不是 `6778c4c8`：任何一项发生就停，不覆盖、不删桶里的对象、不自动重试，照实写进回执。

## 二、Windows 常驻辅助进程调查（不改 link 代码）

### 背景

link 在 Windows 上每做一次文件操作，都在用户电脑上用包里自带的 Codex 起一次本机沙箱（`codex sandbox --permission-profile sunmoon_files ... -- node native/helper.mjs`，`agent/src/windowsRuntime.ts` 的 `windowsHelperArgs`），在沙箱里起一个 Node 辅助进程，只做这一件事，然后退出。上一张卡量到：提权模式每次约 1.07 秒，普通模式约 0.57 秒，Node 直接做不到 1 毫秒。

0.5.5 以前是常驻：辅助进程只起一次，管道一直开着，连续收多条请求。11-01 在新机器上发现，在提权沙箱里管道开着时，辅助进程 30 秒都不回；发完请求把输入关掉，立刻就回（sunmoon-link `新机器安装linkbug.md`，第 128–157 行）。0.5.5 只好改成每次新起、发一条就关输入。所以直接退回常驻不行，要先弄清下面几件事，所有者才能定改法。

### 要回答

1. **复现**：用 0.5.6 包里的 Codex（0.155.1）和 `helper.mjs`，照现在的参数起辅助进程，管道一直开着，连发 2 条请求。提权、普通两种模式下各会不会卡？再和"发一条就关输入"对照。
2. **卡在哪一段**：辅助进程到底收没收到输入？可以让探针在沙箱里起一个最小的 Node 脚本（不用 `helper.mjs`），一收到数据就往自己的临时目录写个标记、往 stdout 回一行。分三种情况：
   - 根本没收到（Codex 沙箱在 EOF 前不转发 stdin）；
   - 收到了但输出出不来（stdout 不刷新，或者 Codex 不转发）；
   - 写够一定字节数以后才放行（缓冲阈值）。

   Codex 是开源的，可以对照 0.155.1 源码里 Windows 沙箱转发 stdin/stdout 的那段（openai/codex 仓）看是不是这样设计的。查到的写出处，没查到的写"没查到"。
3. **换一条线行不行**：辅助进程在沙箱里，能不能和 link 用别的通道常驻通信？比如 link 开一个 Windows 命名管道，或者只监听 127.0.0.1 的端口，辅助进程连回来。现在的权限配置是 `network={enabled=false}`，要实测这两种通道在两种模式下通不通。通的话，再核隔离还在：辅助进程照样写不了允许目录以外的地方、读不了 `.sandbox-secrets` 和 `auth.json`。
4. **一次办多件**：一个辅助进程一次收 10 条、50 条请求再关输入，平均每条要多少毫秒（两种模式，各 3 轮，记中位数和最大值）。
5. **常驻能快多少**：在第 1–3 条里找到的任何一种能常驻的做法下，量单次文件操作的耗时，和上一张卡的表对照。

### 允许的动作

- 只在 Windows 测试机上，在探针自己建的临时目录里读写。探针放仓外，要进仓在回执里提。
- 不改 link 代码，不改已装 link 的配置，不触发新的 UAC，不读也不导出凭据，不跑模型对话。
- 看 Codex 源码只读，不往远程下包。

## 验收与交回

- 回执 `replies/luna.md`，分两节：
  - 发布：发布提交 R 的提交号和 `git diff 6778c4c8 R --stat`；上传和读回回执；flux digest 和晋级记录；下载核对；平台电脑核对；合回 qwen 的提交号。
  - 调查：第 1–5 条逐条写结论，标明事实、推断、没核实；附计时表和 Windows 环境信息。
- 第二节只给事实和建议，不替所有者定改不改、怎么改。
- 证据放 `sunmoon-link/scripts/results/link-0.5.6-resident-20261108/`（只有计时和日志，不含凭据）。
- 提交后推送，报告各仓提交号和推送结果。

## 处理记录

| 日期 | 事项 | 处理 |
| --- | --- | --- |
| 2026-11-08 | 发起 | 所有者在 qwen 会话里定：0.5.6 可以单发（发 link 就是换安装包，和 knowbench 发版无关），并让把 0.5.6 发布和常驻进程调查合成一张卡交本地。发布授权依据就是这句；前一张卡第三节「knowbench 后端带着没发的改动，不能单发」写错了，以本卡为准 |
| 2026-11-08 | luna 回执第一节（[replies/luna.md](replies/luna.md)）：0.5.6 已发布，发布提交 R = `97f3f32e9`，合回 qwen `de6b1579e`，晋级记录 `c9c6ea9c6` | 采纳。发起者核过 R 相对 `6778c4c8` 只动 knowbench-backend 4 个文件：安装包配置、下载配置密文、4 处配置摘要标注、平台电脑取包几行；镜像不变；两个开关仍只在 qwen |
| 2026-11-08 | 本卡两处写错：Linux 包用了 `dev-kind` 站点的旧候选（平台电脑要 `edge-public`）；「只改一个文件」漏了 stage 生成、要一起提交的渲染文件 | 发起者的错。luna 发现后经所有者「允许修正后继续发布」，用同一源码重出 `edge-public` 包、提交渲染文件，处理正确 |
| 2026-11-08 | luna 回执第二节（证据 sunmoon-link `087c5c7`）：本机没复现 11-01 卡死；Codex 0.155.1 源码没有「等 EOF 才转发」；回环通、默认命名管道不通；50 条一批提权每条约 15 ms；常驻暖态每次约 0.5–1.4 ms | 采纳。所有者 11-08 定：改常驻。qwen 在远程改 sunmoon-link：常驻走 stdio，首条超时退回每次新起，再交 Windows 实机验收 |
| 2026-11-08 | 结案 | 发布和调查都已交付；常驻改造另起 |

> 2026-11-08 推送规则：助手验证、提交后默认推送，临时指令优先。

> 2026-11-08 归档：发起者 qwen 已在上述处理记录结案，整包移入 archive。
