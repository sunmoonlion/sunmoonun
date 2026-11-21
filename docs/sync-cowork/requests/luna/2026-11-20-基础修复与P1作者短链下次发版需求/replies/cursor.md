# Cursor 发布回执

2026-11-20。Jenkins `release` #97 成功。用户脚本开关保持关闭。真实供应商 OAuth 与生产付费测试不在本轮。

## 发布结果

- 分支 `p1-f21-release-20261120`，从 `origin/c1-c6-release-20261120`（#96 回执 `50c1a6e6b`）拉出。库版本提交 `b08268a2fcbb5cb16e538d548e77eacdc2ad4163`。
- 部署提交 `522f76c1571f432c668a1c42e811635f73386d27`。指针 `ab1e0994fe803f1d8133b99f7ccc9f9d9ff5ff75`。回执提交 `40ad55c93`。标签 `release-20261120-2`。
- OCI `sha256:086da47df80d5dfcbdffdefd351fc73ccbfe2e9c4861c43874ffed16fcc0e670`，仓库 `oci://harbor.sunmoonai.com:30443/platform/deployments-kind`，路径 `./clusters/kind`。
- 任务：<https://jenkins.dev.sunmoonai.com:30443/job/release/97/>。admin 于 2026-11-20T21:22:40+08:00 批准。Jenkins 回执时间 2026-11-20T21:33:17+08:00。官方回执在 `scripts/results/release-97.20261120-213316.md`。
- 上线前可恢复的 Git 指针是标签 `release-20261120-1`。数据库 schema 不随 Git 指针回退。

四个应用父仓与子仓指针和需求表一致。`PIN=heads` 只改了 KnowBase、KnowMart、KnowBench、KnowLab；tpl 与 KnowFeed 未动。

## 镜像与迁移

协议检查均为 `failed=0`。四个新迁移 Job 均为 `Complete 1/1`。线上 API、runner、worker 已换到下表镜像。

| 组件 | 镜像摘要 | 源码 | 迁移 |
| --- | --- | --- | --- |
| KnowBase 后端 | `sha256:ea82f12d44b25e4bc1d9a3c459c42768ab31e85808b2bb15511848a253794eb0` | `b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b` | 仍为 `20261119_0022`，Job 只复核未再升级 |
| KnowBench 后端 | `sha256:aec3f2bddad53bb6af599e0449114e9f4963b6c178051e71e697cf48b9f44fc9` | `3a3eb862ffb6d752eec84e477c6c6a417dad710f` | `20261120_0049` → `20261120_0050` |
| KnowBench Web | `sha256:32af4acb375d0c37619378a7ecb2f29275a29d0ad9aa854711cc13e32ec2ab52` | `ed6ed7aefddd313ea2b304c0cc35413297024a50` | — |
| KnowLab 后端 | `sha256:45282caca6d9832400ed73187ce569a4da66ce598d977ea5cdf8c1fa01879c0b` | `185e1ca91d2d114f7d466b89b55d028900e2ca47` | `20261115_0027` → `20261120_0028` |
| KnowLab Web | `sha256:83827a55898ef1cbdb73464020834b64054e857542f1fddf3f553d0883d343a3` | `f4ace6f9e9b5194a75ca6c613b6a1dd7bbcc18af` | — |
| KnowMart 后端 | `sha256:d3575d6e11ca203c67e205ce4759e3308cdb90ca42b015ea9d240334718378f9` | `71751d52b5d145c32d3d829103f0486ccfe1cdb8` | `20261120_0015` → `20261120_0016` → `20261120_0017` |
| KnowMart Web | `sha256:bea512b3ab1bae69b9f7f9c9c6a2698027e1cf46bd749945d24698dd1020ec09` | `14515db89f249d76ea67f83b746fed030ccdf7f0` | — |
| 沙箱 | `sha256:aaf941ee938d30b6a938f7e46ed2d1521142dc654e75fe8ff61fb483bb05f46b` | `42ef8470eaf8df065184dbae0537c963ad15b8a8` | — |
| 供给器 | `sha256:3eeb6761c7ffc69dc5943b6cf3346e6f5e559e2f87402926bc5e9e12b348d9fb` | 同上 | — |

沙箱与供给器按平台清单重建，摘要与 #96 相同。`9edd61e02` 与 `42ef8470` 的沙箱目录没有差异，发布分支不能把构建修订指到不在该分支历史上的 `9edd61e02`，所以继续钉 `42ef8470`。

`20261120_0028` 的迁移日志显示已从正式版本的 `provenance` 回填 `method_version_slots` 和 `method_dependencies`。没有另做行数核对。

## 开关与滚动更新

线上 ConfigMap `knowbench-runtime` 中 `WORKBENCH_SKILL_SCRIPTS_ENABLED=false`，`WORKBENCH_OUTPUT_WRITE_ENABLED=false`，`DEPLOYMENT_ID=knowbench-backend-aec3f2bddad53bb6`。

KnowBench 的 api、runner、worker、scheduler 都是新 Pod，约在批准后启动，各 1/1。没有留下旧 runner Pod。没有为了复查租约再停一次 runner。

已经存在的用户沙箱没有被这次发布替换，仍使用更早的沙箱镜像。新创建的沙箱才会用到上面的沙箱摘要。供给器 Pod 仍是 8 小时前的那个，镜像摘要与本次重建结果相同。

## 未在集群重做的抽验

以下项目没有在目标集群上重跑。Luna 的本地验收仍以原单和归档记录为准，不能写成这次的线上通过。

- 作者 P1 的补查、采用、保存重开、中途取消、完成和冻结。
- 同资料两步同意、递归取消的中间调用状态、排队加审批的等待时间。
- 慢交付期间撤架后拒绝新买方获取。
- 正式探针里应留下不通过证据的未知项。
- 真实供应商 OAuth 和生产付费测试。

## 第二轮目标集群抽验（2026-11-20）

沿用 Jenkins #97，没有重新发布，也没有改开关。`WORKBENCH_SKILL_SCRIPTS_ENABLED` 仍为 `false`。真实供应商 OAuth 与生产付费仍留在待办第 10 项。第一轮的版本、镜像和迁移记录保持原样。

本轮没有获准测试身份的会话或令牌，也没有可指向目标集群的合成资料。`scripts/local-integration/p1_author.py` 和 `formal_market_delivery.py` 打的是一次性测试库和本机服务，不能当作这次集群抽验。因此第 3 条的行为项都没有运行编号、产物引用、调用状态或时间。

| 抽验项 | 结果 | 还缺什么 |
| --- | --- | --- |
| P1 补查、采用、保存重开、中途取消、完成和冻结 | 未做 | 获准测试身份，以及能在目标集群走完这些步骤的合成资料。交回时要带运行编号和产物引用 |
| 同资料两次同意 | 未做 | 同上，并要同一份资料上的两次同意记录 |
| 递归取消的中间调用状态 | 未做 | 同上，并要各层调用状态和时间 |
| 排队加审批的等待时间 | 未做 | 同上，并要排队和审批两端的时间 |
| 慢交付期间撤架后的获取 | 未做 | 同上，并要撤架后新买方获取被拒绝的结果 |
| 正式探针未知项 | 未做 | 同上，并要该未知项的拒绝记录 |

历史版本回填也没有做成“符合预期”的结论。`knowlab-migrate-45282caca6d9-v4` 的日志只有这一行升级：

`Running upgrade 20261115_0027 -> 20261120_0028, Index the external slots and direct dependencies of immutable formal versions.`

随后的 schema 复核是 `20261120_0028`。日志没有槽位行数、依赖行数，也没有和 `provenance` 投影的对照。要补上这一项，需要一次只读计数：正式方法版本按迁移里同一投影算出的槽位和依赖，对照 `method_version_slots`、`method_dependencies`。这次没有查库。

退场任务和租约只查了还在的记录，没有再停 runner。当前 Pod 是 `knowbench-runner-759f885f4d-cvrhw`，`2026-11-20T13:24:57Z` 启动，1/1。启动日志有 `workbench runner starting id=sunmoon-kind-r1`，没有租约释放或未结算任务的条数。`release_leases` 写在进程退出路径上，旧 Pod 已经不在，它的日志也没有留下来。`workbench_sandbox_leases` 里 `sunmoon-kind-r1` 的有效和已到期行，以及当时未结算任务，这次都没有查。要补这一项，需要上述只读行，或者旧 Pod 的退出日志。

## 用集群入口补查已有记录（2026-11-21）

用目标集群里 KnowLab 和 KnowBench 自己的数据库连接做了只读计数。没有重发，没有改开关，也没有另造用户会话。

历史回填对得上，因为这个库里没有正式版本。库版本是 `20261120_0028`，触发器 `index_formal_method` 在。`knowbot_method_version`、`method_version_slots`、`method_dependencies` 都是 0 行，运行角色 `knowlab_runtime` 没有绕过行级权限，这三张表也没有打开行级权限。投影、缺行、多行和字段不一致都是 0。这里没有一份历史冻结正式版本可以再对照槽位内容。

退场租约有记录。`sunmoon-kind-r1` 的 4 条租约都已到期，到期时间和更新时间都是 `2026-11-20 13:24:55.912396+00:00`，比新 Pod 的 `2026-11-20T13:24:57Z` 早两秒。没有其他 runner 的租约。这 4 个沙箱上没有 `VALIDATING`、`QUEUED`、`RUNNING`、`RECEIVED` 或 `WAITING` 任务。全部 55 个任务都已结束：成功 18、失败 19、取消 18。其中 28 个来自 KnowMart，27 个是内置包，都没有正式方法执行契约。

第 3 条的补查、采用、重开、取消、冻结、两次同意、递归取消、排队审批、撤架获取和未知探针，仍然没有运行编号。集群里的数据库连接查得到上面的表，不能代替获准用户在 KnowLab 和 KnowMart 上走这些步骤。当前 KnowLab 没有任何方法版本。
