# 本地与远程协作

## 日常只做三件事

本地和远程在**各自的机器**执行，工位和分支同名。以 qwen 为例：

```bash
# 开工：拉取已推送的代码
~/five-repos-sync/sync-five-repos.sh pull qwen

# 修改、测试后：自己检查 diff，逐仓提交；子仓先提交，再提交父仓 gitlink

# 收工：推送已经提交的内容
~/five-repos-sync/sync-five-repos.sh push qwen
```

查看当前机器状态（不联网）：

```bash
~/five-repos-sync/sync-five-repos.sh status qwen
```

推送更新 GitHub/Gitee，不更新对方的工作目录。对方下次开工自己 `pull`。不需要同步程序 SSH 登录对方，也不会在日常操作里同时更新所有工位。

原来的入口继续可用，两端含义相同：

```bash
WS=qwen bash ~/switch-test/human-local.sh   # pull
WS=qwen bash ~/switch-test/human-remote.sh  # push
```

`local-pull` / `from-remote` 是 `pull` 的兼容别名，`local-push` / `to-remote` 是 `push` 的兼容别名。**现在这些日常别名也不会 SSH 操作另一台机器。**

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
- 当前工位为 cursor、fable、kimi、luna、qwen、agy；[本轮统一基线](../../../scripts/results/station-align-qwen-20261107.md)已对齐，后续各工位仍独立开发，不自动跨工位合并。

两个助手通过 Git 中的任务卡和结果交接。任务卡放 `inbox/<执行助手>/`，注明工位、仓与提交、命令、前提、预期结果及回执路径；本地按指定卡执行，不从其他箱子自行领活。回执放被测仓 `scripts/results/`，写清通过/失败/未验证及退出码，完成后提交并推送。只有验收完成的卡移入 `done/`，暂停的放 `hold/`；浏览器或真实调用未验证就保留说明。

## 配置与维护分开

- 工位名单：两端各自 `~/toolboxes/Vlinux/utils/set-up-tools/model-switch/layout.conf`。
- 仓列表和 Git remote：`~/five-repos-sync/config.sh`；`BRANCH` 可显式覆盖同名分支，`BRANCHES` 映射仍支持。两端各自展开 `$HOME`，不复制凭据或代理配置。
- 日常实现：[workstation_sync.py](workstation_sync.py)；[安装入口](sync-five-repos.sh)复制到 `~/five-repos-sync/sync-five-repos.sh`。两个 human 脚本也使用同一实现，不维护两套同步逻辑。
- 工位创建仍用 model-switch；明确要求的跨机/强制对齐保留在 [maintenance-sync.sh](maintenance-sync.sh)，安装到 `~/five-repos-sync/maintenance-sync.sh`。此入口保留旧维护行为，必须按具体授权使用；日常入口不调用它、不支持 `-all`。
- [five-repos-sync/](five-repos-sync/) 仍只是历史参考副本，不是执行入口。

回归测试使用临时 Git 仓库，不访问业务环境：

```bash
python3 -m unittest discover -s scripts -p test_switch_test_sync.py -v
```

旧协作约定和旧脚本在 Git 历史中保留；本页的 2026-11-07 简化规则优先。
