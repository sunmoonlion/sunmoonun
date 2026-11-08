# link 0.5.6：出包、Windows 实测文件操作耗时（发布另授权）

- 类型：验证（第三节是发布，要所有者另外明确授权才做）
- 状态：待接手
- 发起身份：qwen（使用 Opus）
- 执行身份：luna
- 主工位：**本地** `~/worktrees/qwen`（Windows 实测在所有者那台 Windows 测试机上）
- 仓与分支：sunmoon-link，qwen
- 待验版本：`795d5f831076e87d6b352b79601ac64e476ac2d2`（0.5.6，只改了版本号；它的父提交 `5c41d1fba9af0526af9a26a802a140dba6dd77a6` 是账 187「Windows 一次探测失败就一直坏」的修复；已发的 0.5.5 包是 `c75d0fd`，不含这个修复）
- 回执：replies/luna.md

## 目标与范围

1. 从 `795d5f8` 出 Windows 包和 Linux 包，在 Windows 测试机上装好、配对通过。
2. **实测文件操作耗时**（opus-qwen 第 19 条）。0.5.5 起，Windows 上**每个文件操作都新起一个沙箱辅助进程**（`agent/src/windowsRuntime.ts` 第 155 行附近），以前是一个常驻进程。要量出来这样到底慢多少，所有者据此决定要不要改回常驻进程。
3. 顺带确认账 187：探测失败一次以后，下一次文件操作会重新探测，不会一直坏。

**不在范围内**：改 link 的代码；跑会花模型费的对话；动 knowbench 的部署。

## 依据与前提

- opus-qwen 第三节第 18、19 条（`sunmoonun/docs/总纲/opus-qwen.md`）；账 187（`docs/design/pending-after-migration.md`）。
- 出包与发版的做法：`sunmoonun/docs/project-guide/repos/sunmoon-link.md`「发版」一节。
- 现成的 Windows 探针：`sunmoon-link/probe/windows-agent-contract.mjs`。它在 Windows 本机上直接调用 `WindowsFiles`，只建自己的临时目录，不读模型或会合点的凭据。
- 开工前：所有者已经推了远程的 qwen。本地先跑 `./sunmoonun/docs/sync-cowork/sync/sync.sh pull`，确认 sunmoon-link 的 HEAD 是 `795d5f8`。

## 允许的动作

- 第一、二节：出包、在 Windows 测试机上装、配对；照 `probe/windows-agent-contract.mjs` 的写法写一个计时探针。探针放在本地工作目录，不进仓；要进仓，在回执里提。只在探针自己建的临时目录里读写。
- **第三节（发布）**：只有所有者在本请求的处理记录里写了「准发 0.5.6」以后才做。
- 不跑模型对话，不动别的仓；回执验证提交后按最新默认规则推送。

## 一、出包与安装

照 `sunmoon-link.md`「发版」一节在本地构建 Windows（`windows-x64`）和 Linux（`linux-x64`）两个包，在 Windows 测试机上装 0.5.6、配对通过。记下：包名、SHA-256、安装用了多久、有没有报错。

## 二、计时（Windows 本机，探针直接调用 `WindowsFiles`）

在探针自己建的临时目录里，各做 3 轮，每一项记中位数和最大值（毫秒）：

| 项 | 做法 |
| --- | --- |
| a | 查 1 个文件的元数据（`fs/getMetadata`），连做 50 次 |
| b | 读 20 个 4 KB 的小文件 |
| c | 列一个有 500 个条目的目录 |
| d | 写 10 个 4 KB 的文件 |
| e | 同样的 a–d，用 Node 自带的 `fs` 直接做，作为对照（看沙箱开销） |

另外照实写上：Windows 版本、有没有开 Defender 实时扫描、CPU 和磁盘大概是什么配置。

**账 187 顺带验**：探测阶段的执行服务还没起来时，先调一次文件操作，让它失败；等服务起来以后再调一次，要能成功。

## 三、发布（要所有者在处理记录里写「准发 0.5.6」才做）

照 `sunmoon-link.md`「发版」：改 `agent-releases/config.yaml` 的版本、ZIP 与清单摘要、对象名 → `make -C infrastructure agent-release-verify` 和 `agent-release-upload` → 按发布链部署 knowbench。knowbench 后端现在带着没发的改动（0050、0051 和 11-08 的修复），**不能单发**。要先和所有者确认是随 knowbench 那一批一起发，还是只更新安装包。

## 验收与交回

- 回执 `replies/luna.md`：实际用的提交、包的摘要、计时表（含对照组）、账 187 的结果、环境信息、没做成的项和原因。
- 结论只写量到的数，不替所有者下「要不要改回常驻进程」的结论；可以给建议。
- 只提交 `replies/luna.md`（还有证据文件，要的话放 `sunmoon-link/scripts/results/`）。提交后推送后报告提交号及各推送端结果。

## 处理记录

| 日期 | 事项 | 处理 |
| --- | --- | --- |
| 2026-11-08 | 发起 | qwen 在远程把版本号升到 0.5.6（`795d5f8`），本地执行 |

> 2026-11-08 推送规则更新：所有者改为助手验证、提交后默认推送，临时指令优先。本卡其他动作范围、发布和付费调用条件保持原有记录。
