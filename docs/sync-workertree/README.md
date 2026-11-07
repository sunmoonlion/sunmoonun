# 本地与远程协作

## 日常只做三件事

本地和远程在**各自的机器**执行，工位和分支同名。以 qwen 为例，先进入 `~/worktrees/qwen`；master 则进入 `~/master`：

```bash
# 开工：拉取已推送的代码
./sunmoonun/docs/sync-workertree/five-repos-sync/sync-five-repos.sh pull

# 修改、测试后：自己检查 diff，逐仓提交；子仓先提交，再提交父仓 gitlink

# 收工：推送已经提交的内容
./sunmoonun/docs/sync-workertree/five-repos-sync/sync-five-repos.sh push
```

查看当前机器状态（不联网）：

```bash
./sunmoonun/docs/sync-workertree/five-repos-sync/sync-five-repos.sh status
```

推送更新 GitHub/Gitee，不更新对方的工作目录。对方下次开工自己 `pull`。不需要同步程序 SSH 登录对方，也不会在日常操作里同时更新所有工位。

日常只保留上面的统一入口。原 `~/switch-test/` 两个转发脚本已退役，无需再安装或复制。

脚本根据自身所在目录识别工位，配置和实现均在仓内；拉取后立即使用新版。不再安装家目录入口，也不需要传工位名。

## 速度与保护

- 拉取：先检查所有工作区，再每仓 fetch 一次（默认最多 4 仓并行）；全部通过后，串行 `merge --ff-only`。不再先 fetch 又 pull，也不额外拉两个后端。
- 子仓严格跟随父仓 gitlink，并接回同名分支；子仓分支有独有提交、需要倒退时停止，不覆盖它。新增/移除子模块或尚未初始化的仓需先单独处理。
- 推送：并行核对每个推送端，已一致的不再 push；确有提交时先推子仓再推父仓。GitHub 与 Gitee 分别核对，不能因 GitHub 已有就漏掉 Gitee。
- **不自动 add、commit、stash、rebase、reset 或强推。**未提交内容先由开发者处理；分叉或网络错误明确停止，不把连接失败当成“远端没有分支”。
- 跨仓推送不具备整体事务性；某仓推送失败时明确停止，已经成功的推送保留，父仓不会越过失败子仓。检查并处理后可重跑。
- `SYNC_JOBS=1` 可串行；默认 4，允许 1–16。`SYNC_TIMEOUT=120` 为单次 Git 命令超时秒数，超时须核对现场，不自动重试。
- 同一工位已有同步运行时第二次启动会被拒绝。同步期间两端不要同时改同一工位，不能以脚本代替协作。

## 分工与交接

- **远程**：`zym@43.153.135.74:1022`，家目录 `/home/zym`；Opus 主导开发、测试、任务卡与发布卡。
- **本地**：所有者 Windows 上的 WSL，家目录 `/home/zymun`；本地助手按交接执行本机、集群与发布验证，提供证据和回执。
- **所有者**：决定方向、发布与业务审批；需要网页登录、确认数据或付费测试时由所有者操作，不能代点。
- 当前工位为 cursor、fable、kimi、luna、qwen、agy；[本轮统一基线](../../scripts/results/station-align-qwen-20261107.md)已对齐，后续各工位仍独立开发，不自动跨工位合并。

两个助手通过 Git 中的任务卡和结果交接。任务卡放 `inbox/<执行助手>/`，注明工位、仓与提交、命令、前提、预期结果及回执路径；本地按指定卡执行，不从其他箱子自行领活。回执放被测仓 `scripts/results/`，写清通过/失败/未验证及退出码，完成后提交并推送。只有验收完成的卡移入 `done/`，暂停的放 `hold/`；浏览器或真实调用未验证就保留说明。

## 配置与维护分开

工位管理工具统一放在 `~/toolboxes/Vlinux/utils/set-up-tools/model-switch/`，`mb` 指向其中的 `model-branch.sh`；工位名单在 `layout.conf`，注册仓列表在 `repos.conf`。本目录不再保存副本，避免多份配置混淆。

- 创建工位的名单仍由 model-switch 管理；日常同步不依赖外部 layout.conf。
- 唯一运行目录：[five-repos-sync/](five-repos-sync/)。其中 `config.sh` 保存仓列表，`sync-five-repos.sh` 是可执行入口，`workstation_sync.py` 是实现。
- master 和各工位均随本仓维护这三份文件；无需复制安装。旧的参考目录已升级为正式运行目录，过时副本从当前树移除，Git 历史仍可追溯。
- 日常目录不再保留旧的跨机/全工位对齐脚本；特殊维护需另按具体授权处理，不能用日常 pull 代替跨工位合并。

回归测试使用临时 Git 仓库，不访问业务环境：

```bash
python3 -m unittest discover -s scripts -p test_switch_test_sync.py -v
```

旧协作约定和旧脚本在 Git 历史中保留；本页的 2026-11-07 简化规则优先。

## 目录内容

- `five-repos-sync/`：当前同步工具。
- `inbox/`：未完成任务；`hold/`：暂停任务；`done/`：今后已验收任务。

旧任务、旧审读日志和作废发布卡已从当前目录移除，可从 Git 历史追溯。Windows hosts 工具归入 [运维工具](../ops/tools/windows_hosts_add.ps1)。
