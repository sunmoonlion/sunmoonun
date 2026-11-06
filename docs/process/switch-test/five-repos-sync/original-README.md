# SunMoonAI 多仓同步工具

本工具通过 Git 远端在本机与公网服务器 `43.153.135.74:1022` 之间同步
SunMoonAI 在 `config.sh` 的 `REPOS` 中配置的仓库，当前为六个：

- `tpl-app`
- `knowledge-app`
- `k8s`
- `info-app`
- `investment-app`
- `runtime`

`desktop-app` 已移出同步清单。工具目录与命令名保留 `five-repos-sync`，同步范围以 `REPOS` 为准。

脚本只同步已经提交的内容，不会传输未提交文件。同步前会检查配置仓库的当前分支和工作区；
任一仓库有未提交内容、目录不存在或分支不匹配时，操作会停止。

## 换机器：先同步，再工作

这是开始工作的前置步骤，不是发生冲突后再补做。2026-09-11 的跨机收敛教训：
不能假定云服务器等于远程仓库，也不能假定 master 包含所有 worktree 的修改。

1. 离开源机器前检查父仓、子模块的未提交内容及 stash；处理本轮修改。
   子仓先提交并推送，再提交父仓 gitlink，最后同步父仓。
2. 开始在目标机器改文件前，先检查两端状态，再按源机器选择同步方向。
   **2026-09-14 所有者约定：换机器默认使用 `-all`，包含 master 和全部配置工位，
   不再只同步当前助手工位。**以下命令在本机控制端执行：

   ```bash
   ~/five-repos-sync/sync-five-repos.sh status -all
   # 接续云服务器上的工作：
   ~/five-repos-sync/sync-five-repos.sh from-remote -all
   # 接续本机上的工作，准备到云服务器继续：
   ~/five-repos-sync/sync-five-repos.sh to-remote -all
   ```

3. 确认同步成功、两端对应分支提交一致且工作树干净后，才开始工作。
   有未提交内容、stash 未处理、分叉或错误时先处理，不边修改边补同步。
4. `-all` 包含 master，但仍是逐工作区同步**同名分支**；工作分支不会自动合入
   master，也不会自动跟随 master 更新。若希望所有工位都以最新 master 为基线，
   需另行授权并核对独有提交/未提交改动，再执行快进或处理分叉，不能用强制覆盖代替。
   已确认云端全部提交推到仓库时，可用 `local-pull -all` 省去重复推送。
   `-all` 不是跨仓事务：中途失败先处理失败项，再重跑，不把部分成功当全部完成。

日常用普通同步。只有明确决定放弃目标端分叉、已确认权威源完整时才使用 `realign`；
不要为绕过分叉临时新增一套日常分支。本地 Opus 工作树可以同步，但不启动 Opus 助手。

## 常用命令

在本机开发并提交后，把配置仓库同步到服务器：

```bash
~/five-repos-sync/sync-five-repos.sh to-remote luna
```

执行顺序为：本地配置仓库先从 Git 远端 `pull --ff-only`，再 `push`，然后远程配置仓库
`pull --ff-only`。App 父仓拉取后会
自动执行 `git submodule sync --recursive` 和 `git submodule update --init --recursive`，
使组件目录与父仓记录的 gitlink 保持一致。

把服务器上的提交同步回本机：

```bash
~/five-repos-sync/sync-five-repos.sh from-remote luna
```

反向同步同样会在本地父仓拉取完成后自动对齐子模块。

`to-remote` / `from-remote` 的源端推送前都会先从 Git 远端快进，接收另一台机器已推送的
测试结果等提交，避免源端落后时报 `fetch first`。Git 远端尚无该分支时直接推送；分叉、
网络或权限错误仍然停止，不自动合并或变基。单独的 `local-push` / `remote-push` 仍只推送。

查看两端配置仓库状态（不推送、不拉取）：

```bash
~/five-repos-sync/sync-five-repos.sh status luna
```

也可以只执行某一步：

```bash
~/five-repos-sync/sync-five-repos.sh local-push luna
~/five-repos-sync/sync-five-repos.sh local-pull luna
~/five-repos-sync/sync-five-repos.sh remote-push luna
~/five-repos-sync/sync-five-repos.sh remote-pull luna
```

命令后的工作区参数可以是 `master`、`cursor`、`kimi`、`luna`、`opus` 或
`qwen`。工作区参数是必填项；脚本不会根据当前目录推断，也没有默认工作区。
缺少参数时会提示可用工作区并直接退出，不执行任何 Git 操作。

同步某一个工作区：

```bash
~/five-repos-sync/sync-five-repos.sh to-remote opus
~/five-repos-sync/sync-five-repos.sh from-remote opus
~/five-repos-sync/sync-five-repos.sh status opus
```

遍历配置中的全部工作区：

```bash
~/five-repos-sync/sync-five-repos.sh to-remote -all
~/five-repos-sync/sync-five-repos.sh from-remote -all
~/five-repos-sync/sync-five-repos.sh status -all
```

也支持把 `-all` 连在命令后面，例如 `to-remote-all`、`from-remote-all` 和
`status-all`。

## 分支删除重建后的强制对齐

普通 `to-remote` / `from-remote` 只允许快进，不会改写分支历史。如果某一端删除
旧分支并从新基线重建了同名分支，应显式使用 `realign` 命令。

本地重建了分支，以本地为权威源：

```bash
~/five-repos-sync/sync-five-repos.sh realign-to-remote opus
```

执行顺序：检查两端配置仓库干净 → 本地以 `--force-with-lease` 更新 Git 远端 →
远程配置仓库 `reset --hard` 到新分支 → 对齐子模块。

如果同一个 remote 配置了多个 push URL（例如同时推送 GitHub 和 Gitee），脚本会
分别读取每个平台上目标分支的实时 SHA，并对每个 URL 使用独立的显式 lease。
因此，一个平台的远端跟踪引用不会被错误地拿去校验另一个平台；若查询后分支又被
别人更新，对应推送仍会因 lease 不匹配而停止。

远程重建了分支，以远程为权威源：

```bash
~/five-repos-sync/sync-five-repos.sh realign-from-remote opus
```

执行顺序：检查两端配置仓库干净 → 远程以 `--force-with-lease` 更新 Git 远端 →
本地配置仓库 `reset --hard` 到新分支 → 对齐子模块。

两条命令都会放弃目标端的分叉历史，因此：

- 必须显式指定一个工作区；
- 不支持 `-all`；
- 禁止用于 `master`；
- 任一父仓或子模块有未提交内容时停止；
- 配置仓库不是事务操作，中途网络失败时修复后用同一命令重跑。

查看帮助：

```bash
~/five-repos-sync/sync-five-repos.sh --help
```

## 修改配置

配置文件是 `~/five-repos-sync/config.sh`：

```bash
REMOTE_HOST="43.153.135.74"
REMOTE_USER="zym"
REMOTE_PORT="1022"
REMOTE_IDENTITY_FILE="$HOME/.ssh/id_rsa"
GIT_REMOTE="origin"
```

### 目录布局（与 mb 共用）

配置仓库目录不再在 `config.sh` 里逐工作区写死。布局只有一份：

`~/toolboxes/Vlinux/utils/set-up-tools/model-switch/layout.conf`

```bash
LAYOUT_MASTER="master"       # 主目录：$HOME/master/<仓>
LAYOUT_WORKTREES="worktrees" # 工位：  $HOME/worktrees/<名字>/<仓>
LAYOUT_WORKSPACES=(cursor kimi luna opus qwen)
```

`mb worktree add <名字>` 和本工具对非 `master` 工作区用同一套规则：
工位名 = 目录名 = Git 分支名。`master` 工作区对应主目录 `$HOME/$LAYOUT_MASTER`。

一次挂出全部具名工位（不要对 luna/kimi/… 各跑一遍）：

```bash
mb worktree add --all --all     # 全部 LAYOUT_WORKSPACES × 全部注册仓
mb worktree add luna            # 只挂 luna
mb worktree add luna k8s        # 只挂 luna 的 k8s
mb worktree add --all k8s       # 全部工位 × 只挂 k8s
```

两个 `--all` 各管一层：工位、仓。只写一个 `mb worktree add --all` 会提示补第二个。
已存在的目录会跳过。远端同样执行一遍即可对齐工位目录。

本机与远端各自展开自己的 `$HOME`（本机 `/home/zymun`，远端 `/home/zym`），
SSH 只传相对家目录的路径，不再写死 `/home/zym/...`。

同步工作区默认是 `master` + `LAYOUT_WORKSPACES`。一般不必在 `config.sh` 再写
`WORKSPACES`；只有要同步子集时才覆盖。

分支名默认等于工作区名。只有两者不同时才在 `config.sh` 里覆盖：

```bash
BRANCHES[opus]="新的分支名"
```

改工位根目录：只改 `layout.conf` 的 `LAYOUT_WORKTREES`，mb 和同步一并生效。
改主目录名：改 `LAYOUT_MASTER`，并同步改 mb 的 `repos.conf`（主仓路径）。

修改配置不会替你创建或切换分支。运行同步前，应先确认本地和远程配置仓库都已经切换到
配置指定的分支；`status` 命令可以用于检查。工位目录用 `mb worktree add <名字>`
或 `mb worktree add --all --all` 创建。

SSH 公网 IP、用户名、端口和私钥分别由 `REMOTE_HOST`、
`REMOTE_USER`、`REMOTE_PORT` 和 `REMOTE_IDENTITY_FILE` 配置；脚本不依赖
`~/.ssh/config` 中的主机别名。

如需临时使用另一份配置或另一份布局，可以指定：

```bash
FIVE_REPOS_CONFIG=/path/to/another-config.sh \
  ~/five-repos-sync/sync-five-repos.sh status luna

LAYOUT_CONF=/path/to/another-layout.conf \
  ~/five-repos-sync/sync-five-repos.sh status luna
```

## 同步限制

- 各配置仓库分别执行 Git 操作，不具备跨仓事务能力；某个仓库网络失败时，修复后重新执行即可。
- 多 push URL 也不是事务操作；某个平台推送成功、另一个失败时，可用同一命令安全重跑。
- 拉取固定使用 `--ff-only`，发现分叉时不会自动合并或变基，需要人工处理。
- `to-remote` 与 `from-remote` 都要求相关工作区干净，避免遗漏或覆盖未提交内容。
- 只有明确的 `realign-to-remote` / `realign-from-remote` 会通过
  `--force-with-lease` 和 `reset --hard` 改写目标端历史。

## 备忘：远程 Codex 依赖本机 CC Switch 代理（与本工具无关）

以下内容与配置仓库同步无关，只是同一台服务器（`43.153.135.74:1022`，ssh 别名
`txy-tokyo`）的使用备忘。

服务器上的 Codex（配置目录 `~/.codex-kimi`，模型 `kimi-k3`）的
`base_url` 是 `http://127.0.0.1:15721/v1`，本身不直接访问大模型 API，
完整链路是：

```
远程 codex → 远程 127.0.0.1:15721
           → SSH RemoteForward（随 ssh 会话建立）
           → 本机 127.0.0.1:15721（CC Switch 桌面应用的本地代理）
           → https://api.moonshot.cn
```

本机 `~/.ssh/config` 中 `Host txy-tokyo` 下配置了
`RemoteForward 127.0.0.1:15721 127.0.0.1:15721`，但**通过 Cursor / VS Code
Remote-SSH 连接时该转发不会生效**（这类工具不使用 config 里的转发配置），
远程 15721 没有监听，codex 会报 `Connection failed: error sending request`
并一直 `Reconnecting... waiting for network`。

解决办法：在本机保持一个带转发的 ssh 会话（CC Switch 应用也要保持运行，
它已通过 `~/.config/autostart/CC Switch.desktop` 开机自启）。

已配置 systemd user 模板服务自动维持转发，登录后自动启动、断开自动
重连，无需手动干预。模板单元文件是
`~/.config/systemd/user/ssh-forward@.service`，按 ssh 别名实例化：

```bash
systemctl --user status ssh-forward@txy-tokyo.service   # 查看状态
systemctl --user restart ssh-forward@txy-tokyo.service  # 手动重连
systemctl --user disable --now ssh-forward@txy-tokyo.service  # 停用
```

### 新增一台远程机器

1. 在本机 `~/.ssh/config` 添加 Host 条目，并带上转发行：

   ```
   Host 新别名
       HostName ...
       User ...
       Port ...
       IdentityFile ~/.ssh/id_rsa
       RemoteForward 127.0.0.1:15721 127.0.0.1:15721
       IdentitiesOnly yes
   ```

2. 用别名启用一个服务实例（不需要新建或修改服务文件）：

   ```bash
   systemctl --user enable --now ssh-forward@新别名
   ```

3. 远程机器上的 Codex 配置（`~/.codex-kimi/config.toml`）保持
   `base_url = "http://127.0.0.1:15721/v1"` 即可，多台远程可共用本机
   同一个 CC Switch 代理；但同一时刻只有一台远程能绑定 15721，
   需要多台时给每台用不同的本地端口（如 15722）并相应修改那台
   远程的 base_url。

手动方式（未使用服务时）：

```bash
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 txy-tokyo
```

挂后台用 `ssh -fN ...`。重复运行第二个会因端口已被占用而报
`remote port forwarding failed`，无害，说明已有会话在工作。

排查命令：

```bash
# 本机：转发会话是否存活、CC Switch 代理日志
systemctl --user status ssh-forward@txy-tokyo.service
tail ~/.cc-switch/logs/cc-switch.log

# 远程：15721 是否监听、端到端是否通（注意要用 -F /dev/null 显式参数
# 连接来验证，否则本次连接自带的转发会污染检查结果）
ssh -F /dev/null -o Port=1022 -o User=zym \
  -o IdentityFile=~/.ssh/id_rsa -o IdentitiesOnly=yes 43.153.135.74 \
  'ss -tln | grep 15721 && curl -sS -m 8 -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:15721/v1/models'
```
