# 当前工位的 Git 同步

本地和远程各自运行：**开工拉取 → 开发并提交 → 收工推送**。工具只同步脚本所在工位，不会登录另一台机器，也不会把所有工位统一到某个分支。

## 怎么用

以 agy 工位为例：

```bash
cd ~/worktrees/agy/sunmoonun/docs/sync-cowork/sync

./sync.sh status   # 查看本机状态，不联网
./sync.sh pull     # 拉取 Git 远端已推送的提交

# 开发、检查、测试，然后自行 git add / git commit

./sync.sh push     # 推送已提交内容
```

也可以在工位根目录运行：

```bash
cd ~/worktrees/agy
./sunmoonun/docs/sync-cowork/sync/sync.sh pull
```

在 master 使用时，进入 `~/master/sunmoonun/docs/sync-cowork/sync`，执行相同命令。换工位就使用那个工位里的脚本；**不需要填写工位名或设置 WS**。脚本根据自身位置识别工位，不根据终端所在目录猜测。

## 三个命令分别做什么

| 命令 | 行为 |
| --- | --- |
| `status` | 显示当前工位各仓的分支与未提交改动。不联网，显示的远端跟踪信息可能不是最新的。 |
| `pull` | 并行抓取，各仓检查通过后只做快进更新；子仓使用父仓记录的准确提交。 |
| `push` | 核对各推送端，先推子仓、再推父仓；已经一致的端点跳过。不会自动提交文件。 |

例如：agy 的父仓拉取 `origin/agy`，qwen 拉取 `origin/qwen`，master 拉取 `origin/master`。**agy 不会因为 pull 就合入 qwen 的代码。**跨工位合并或全体对齐需另行安排。

## 同步哪些仓

仓列表在同目录 `config.sh` 中维护，目前是：

`sunmoonun`、`knowfeed-app`、`knowbench-app`、`knowbase-app`、`tpl-app`、`knowlab-app`、`knowmart-app`、`sunmoon-link`。

程序再按各父仓的 Git 记录递归发现子模块，数量不写死。新增顶层仓时更新 `REPOS`；新机器须先准备这些仓并初始化子模块，工具不代替克隆和工位创建。

推拉使用各仓配置的 Git remote，默认 `origin`。拉取使用它的 fetch 地址；推送逐个核对它的全部 push 地址。已配置 GitHub、Gitee 双端的仓会向两端推送。

## 两端怎样配合

1. 写代码的一端自行检查并提交；修改子仓时，先提交子仓，再提交父仓的子模块指针。
2. 执行 `./sync.sh push`，确认成功。
3. 另一端执行自己工位里的 `./sync.sh pull`，再继续工作。

推送成功只表示 Git 托管端已更新，**不表示另一台机器的工作目录已更新**。同一工位在两端轮流接手，避免同时修改并推送同名分支。

## 停下时怎么处理

| 提示 | 处理方式 |
| --- | --- |
| 有未提交改动 | 先核对文件并自行提交或妥善处理；工具不会自动提交、暂存或丢弃。 |
| 本地有未推提交 | 核对后先推送；若两端各有独立提交，需要先人工合并，再同步。 |
| 分支不符 | 核对是否调用了正确工位的脚本，以及仓是否在该工位的同名分支。不要为过检查强行重置。 |
| 子仓与父仓指针不一致 | 确认要使用的子仓提交，并把正确指针提交到父仓。 |
| 仓缺失、子模块未初始化或结构改变 | 先完成对应仓和子模块准备，再重跑。 |
| 网络失败、超时或某个推送端拒绝 | 核对网络、权限和已完成的步骤，再重跑；已成功的更新不会自动回滚。 |

工具不执行 rebase、reset 或强推，也不替你处理冲突。跨仓同步不是整体事务，中途失败可能已有部分仓完成，应以输出和 Git 状态为准。

## 配置与维护

- `sync.sh`：入口；`config.sh`：仓列表和默认 remote；`workstation_sync.py`：实现。
- 需要 Bash、Python 3、Git，以及这台机器正常的 Git 认证。脚本和配置随 sunmoonun 拉取更新，无需另装家目录副本。
- 默认最多 4 路并行联网；需要串行排查时用 `SYNC_JOBS=1 ./sync.sh pull`。
- 单次 Git 命令默认超时 120 秒，可用 `SYNC_TIMEOUT` 调整；它不是整轮同步时限。
- 特殊分支布局可以显式设置 `BRANCH`，该值会用于本次所有仓；正常同名工位无需设置。
- 创建、删除工位由 `~/toolboxes/Vlinux/utils/set-up-tools/model-switch/` 中的 `mb` 管理，本工具负责已有工位的日常同步。

在 sunmoonun 仓根运行回归测试：

```bash
python3 -m unittest discover -s scripts -p test_switch_test_sync.py -v
```
