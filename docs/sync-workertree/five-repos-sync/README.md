# 工位 Git 同步

本目录是正式运行入口，随 Git 提交、拉取更新。master 和每个工位各有一份；不需要安装到 `~/five-repos-sync/`，不读取该目录的配置。

在工位根目录（例如 `~/worktrees/qwen` 或 `~/master`）执行：

```bash
./sunmoonun/docs/sync-workertree/five-repos-sync/sync-five-repos.sh pull
# 修改并测试；自己逐仓提交：先子仓，再父仓 gitlink
./sunmoonun/docs/sync-workertree/five-repos-sync/sync-five-repos.sh push
```

也可进入本目录执行 `./sync-five-repos.sh pull`、`push` 或 `status`。路径决定操作哪个工位，不依赖终端当前目录、`WS` 环境变量或外部工位名单。默认分支名等于工位目录名；不同名布局须显式设置 `BRANCH`，不会自行换分支。

- `config.sh` 保存仓列表和 Git remote；不含 SSH 开发机地址、凭据或绝对家目录路径。
- `workstation_sync.py` 是唯一实现；默认最多 4 路并行联网，`SYNC_JOBS=1` 可串行。
- 两端只和 Git 托管端交互；对方提交推送后，在自己的机器拉取。不会自动操作另一台机器。
- 拉取先全体检查再快进，子仓严格跟随父仓 gitlink；推送先子仓再父仓，逐个核对推送端。
- 不自动提交、stash、rebase、reset 或强推；脏工作区、分叉、分支不符或网络失败均停止。
- 必须已有完整仓和已初始化子模块；新机器先完成克隆，不会凭空创建或对齐业务仓。
- 旧 human 入口、旧家目录日常脚本均已退役；历史实现可从 Git 历史查看。

在 sunmoonun 仓根运行测试：

```bash
python3 -m unittest discover -s scripts -p test_switch_test_sync.py -v
```
