# 工位同步与协作

所有助手使用同一种协作请求：**一个任务一个目录，请求和各人的回执放在一起**。开发、评审、验证、发布等区别写进请求正文。

**接手前必读：[协作请求使用说明](协作请求使用说明.md)。**其中明确身份与工位、允许动作、请求与回执格式、状态、跨机器交接和Git操作纪律。

## 目录

| 目录 | 用途 |
| --- | --- |
| `requests/<发起身份>/<任务>/request.md` | 请求、指派、状态和采纳／处理记录 |
| `requests/<发起身份>/<任务>/replies/<执行身份>.md` | 该任务每位执行者的独立回执 |
| [sync/](sync/README.md) | 当前工位的推送、拉取和状态检查 |
| [align/](align/README.md) | 以指定本机工位为基准快进对齐其他工位 |
| `archive/<发起身份>/<任务>/` | 发起者结案后整包归档，请求与回执一起保留 |
| `hold/`、`done/` | 仅历史导航，不接收新任务 |

按**当前协作身份**归档，不按模型名：Opus以qwen身份工作，请求归到`requests/qwen/`。执行者在请求中指定；看到索引不等于获准自行领任务。

## 两端分工与同步

- 远程：`zym@43.153.135.74:1022`，家目录`/home/zym`。
- 本地：所有者的WSL，家目录`/home/zymun`。
- 具体任务在哪个工位、由谁执行，以请求为准；评审可以直接在主工位读代码、写自己的回执。
- 默认助手修改、验证、提交后立即推送本次涉及的仓，并汇报结果；所有者临时指定不推送、目标或时机时优先遵守。此规则取代旧卡中的“只提交不推送”默认。

```bash
cd ~/worktrees/qwen  # 例子；应进入请求指定的主工位
./sunmoonun/docs/sync-cowork/sync/sync.sh status
./sunmoonun/docs/sync-cowork/sync/sync.sh pull sunmoonun

# 助手验证、提交后执行；有临时不推送指令时不执行
./sunmoonun/docs/sync-cowork/sync/sync.sh push sunmoonun
```

省略仓名处理全部注册仓；指定父仓包含子仓，指定子仓不改父仓指针。只拉sunmoonun不会拉齐被评应用。推送后另一端还要拉取；同一分支两端轮流写，同机共享工位的Git操作串行。

master在`~/master`运行同样入口。脚本根据自身路径识别工位，不需要WS参数。同名分支推拉不会合并其他工位；独立开发成果先集成验证，再用align对齐，不能强推或硬重置掩盖分叉。

所有者说“pull 某工位”，助手直接调用指定工位的 `sync.sh pull`；未指定仓就拉全部注册仓，指定仓就按范围拉取。默认在当前机器执行，明确指定机器时从其指定。具体映射和异常处理见[同步说明](sync/README.md#所有者说pull-某工位时)。

## 工位管理

创建、删除工位使用`mb`，正式工具在`~/toolboxes/Vlinux/utils/set-up-tools/model-switch/`，配置为`layout.conf`和`repos.conf`。本目录不保存工具副本；日常同步仓列表在`sync/config.sh`。

原`inbox-cowork`、`inbox-review`已统一为requests。旧脚本及旧任务原文在Git历史保留，不再使用`human-local.sh`、`human-remote.sh`或`sync-workertree`入口。

同步完成只显示请求目录入口，不逐条打印任务。发起者负责核对交付、记录结案并整包移入 archive；仍暂停或待验收的任务不能随意删除。
