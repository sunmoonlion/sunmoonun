# 回执 opus-052-5：Windows 上 Codex 命令默认走提权沙箱（账 168）

> Opus 2026-10-23，本地 qwen 工位，只提交、不推、不发版。所有者 10-23：「那现在直接解决吧」。
> 每个仓都试合并进 fable：无冲突。

## 一、为什么

- 远程目录实测时发现：Codex 的 Windows 沙箱在普通模式（unelevated）下拦写不拦删，只读档也删掉了 `%LOCALAPPDATA%` 下的测试文件（SDD 0041 第四节）。
- 读 Codex 0.155.1 源码确认：普通模式的令牌带 `WRITE_RESTRICTED`（`windows-sandbox-rs/src/token.rs`），只在写时查限制，删除不算写；Codex 自己也写明更严的限制要用提权模式（`lib.rs` 里 deny-read 那段）。在普通模式里修不了：沙箱用的是用户本人的身份，要拦它删除就得连用户一起拦。
- OpenAI 文档：提权模式（独立的低权限沙箱账户）是首选，普通模式是退路。
- 本地 link 早就支持提权模式（有设置就用），但安装时从不设置；所有者照 README 手动跑 `sandbox-setup --elevated`，设置成功、探测却不过：`%LOCALAPPDATA%\Programs` 带保护 ACL（断了继承），沙箱账户读不到本地 link 自带的 `node.exe`（`CreateProcessAsUserW failed: 5`）；所有者的 Python 也装在那里。Codex 只给用户目录第一层授读（`setup.rs` 的 `profile_read_roots`，0.164 仍如此），在权限档里加「读」路径也会被「全盘可读」吞掉，不生效。

## 二、改了什么

| 仓 | 提交 | 改了什么 |
| --- | --- | --- |
| sunmoon-link | `5bc283a` | `windowsSandboxRead.ts`：给 `CodexSandboxUsers` 补授读与执行（子项继承）——本地 link 的 `node`、`app` 目录和用户目录下 PATH 里的目录，排除 `.ssh` 等 Codex 排除的目录与本地 link 的控制目录、codex-home，先查后授；提权探测前、每次以提权模式启动时做。`sandbox-upgrade`：停下本地 link → 提权设置 → 再起来，失败也起回来。托盘：第一次见普通模式问一次（`sandbox-offer.json`），「这台电脑上的设置」显示命令隔离模式、普通模式有「提高安全」。`/presence` 多报 `windows_sandbox`。`distribution/README.md` 改写两种模式的说明 |
| knowbench 网页 | `aef3233` | 工作台顶上提示：甲 = 乙且报普通模式时，说「白名单外写不进，但能删文件」，叫到托盘里提高 |
| knowbench 父仓 | `969dad1` | 指向网页 |

## 三、核过

- 所有者 Windows（提权设置已由所有者做过一次），用本地 link 的 exec-server 与权限档实测：
  - 只读档：白名单内能读、写不进；白名单内外都删不掉。
  - 可写档：白名单内能写、能删；白名单外写不进、删不掉。
  - 先撤掉手工授的读，再用新代码补授（经 `\\wsl.localhost` 跑 qwen 新建的 dist）：第一次授 9 个目录约 1 秒，第二次全部已有、0.3 秒；之后 node、python 都能在提权沙箱里起，本地 link 的提权探针（同 `runSandboxProbe`）通过。
- sunmoon-link：typecheck 通过；全量 vitest 347 过、33 跳过（Windows 专用）；新测 6 条（补授目录的取舍 3、权限判断与先查后授 2、presence 报模式 1）。
- 托盘脚本：Windows PowerShell 解析 0 错误，BOM 保留。
- knowbench 网页：tsc、eslint、改过文件的 prettier 通过；vitest 321 过、2 跳过（新 3 条）。

## 四、没验的、要知道的

- 托盘里的「问一次」和「提高安全」按钮没在真机上点过；要装上 0.5.2 后由所有者点一次（会弹管理员确认）。
- 没经本地 link 真跑一轮 Codex 工作对话（提权模式下的 Windows 文件助手、私有桌面），要发版后在所有者机器上跑一轮。
- 所有者机器上已经给这些目录授了沙箱组读（实测留下的，与新代码要授的相同）：本地 link 的 `node`、`app`，Python313 及其 `Scripts`、Python Launcher、`WindowsApps`、VS Code / Cursor / Qoder 的 `bin`。撤回：`icacls <目录> /remove:g CodexSandboxUsers`。
- 所有者的本地 link 现在仍是普通模式（0.5.1 的配置没改）。在 0.5.1 上重跑 `sandbox-setup --elevated` 现在也能过（读已补好），但 0.5.1 启动时不会补新装程序的读，建议等 0.5.2。
- 用户后来往用户目录里新装的程序，要本地 link 重启一次才补授。
- 0.5.2 发版顺序不变；这一条不改后端、会合点。
