# Qwen 发布卡 qwen-018：下一批——四个应用成组发（账 180–188、K29、183）

> 状态：**可执行**（Opus 2026-11-06 写；计划第 7 项）。所有者说「发」再跑；发之前第二节有一处可能要所有者定。
> 为什么成组：开发头比线上 #83 多出的几处互相依赖，单发一个会坏——线上 knowlab 挑数据要的格式接口在 knowbase（账 180）；knowbench 网页发 `expert-match/v4`，线上后端不认；K29 要 knowbench 后端（迁移 0039）与 knowlab 前后端一起（账 181）。

```text
被测仓：sunmoonun，qwen 工作树 ~/worktrees/qwen/sunmoonun，分支 qwen
一次发布：knowbase knowfeed knowbench knowlab，PIN=heads（钉到四个父仓在 qwen 的头，子仓取父仓的 gitlink）
新迁移：只有 knowbench 20261106_0039（接 0038）；knowbase 0021、knowfeed 0022、knowlab 0026 线上已在
不发：tpl、knowmart（knowmart 与线上一致；tpl 网页多 1 笔登录恢复，另批）；本地 link 0.5.6 另卡（账 187 已改代码）
停下的规则：任何一步 exit 不是 0 就停，输出原样进回执，不重试、不退回
做完：回执提交并推到 qwen（2026-11-06 起提交即推；推不上去就停下说，不 rebase）
```

## 这一批上什么

| 应用 | 子仓（线上 → 这次） | 内容 |
| --- | --- | --- |
| knowbase | 后端 `e6822640` → `bf59f85d`（+6） | 版本表格式接口 `ada6ac9`（账 180）；确认不等于在取；GB18030 的 CSV、省略 `r` 的 xlsx 照常读表轴（账 186）；清除不删冻结给专家的数据（账 185）；PDF 首页识别超时生效（账 188） |
| knowfeed | 后端 `15606aaf` → `4b5d9ac3`（+1） | 派发认 `daily_cap=0` 为不限，Wind 确认后的查询派得出去（账 184）；父仓的 knowbase 契约锁跟上 |
| knowbench | 后端 `6c4a6844` → `c7d3d14d`；网页 `8cd235b6` → `7026bfea` | 声明选择 v4、K29 测试留在 knowlab（迁移 0039）、原子方法来源校验；一步 30 分钟无进展只提醒（账 183） |
| knowlab | 后端 `b86eedfc` → `614da0ab`；网页 `61fdc470` → `25772149` | 原子方法与执行策略分开、idea 模板来源、K29 本人测试管理；一份表轴读不出不挡整次挑数据（账 186） |
| 部署配置 | sunmoonun `gitops/…/knowlab-backend/config.yaml` | 登录回跳补上网页现有各栏、去掉没有页面的 `/data`；删掉 `runtime/` 下两份没被 kustomization 引用、代码也不再读的密文（`knowbase-user-data-import-service.sops.yaml`、`storage.sops.yaml`），渲染对象不变（账 182） |

远程（云端容器）跑过的：knowfeed 全量（真库）、knowbase 全量（真库）、knowlab 全量、knowbench 全量（真库，1922 过；另 2 条 run data contract 快照与专家入口进度不带这批改动也失败，不是这批引入）与网页 typecheck、lint、i18n、单测、`next build`；要另一个应用的解释器、对象存储 CA、先构建产物的几条在远程跑不了，各仓提交说明里写了。**页面、集群、真模型、Wind 都没在远程跑过。**

## 一、核对（只读）

```bash
cd ~/worktrees/qwen/sunmoonun && git log --oneline -1 && git status --short | head -3
for a in knowbase knowfeed knowbench knowlab; do d=~/worktrees/qwen/$a-app; git -C $d fetch -q origin qwen; printf "%-10s 本地 %s 远端 %s\n" $a $(git -C $d rev-parse --short=8 HEAD) $(git -C $d rev-parse --short=8 origin/qwen); git -C $d submodule status; done
make -C infrastructure platform-status; echo "status exit=$?"
```

要看到：四个父仓本地与远端同号，且是 knowbase `cb1cb10a`、knowfeed `67638eb9`、knowbench `6049c865`、knowlab `43d2192f`；子仓号与上表一致；`status exit=0`。不一致就先 `WS=qwen bash ~/switch-test/human-local.sh` 再核。

## 二、发前查三样（只读，有任何一样不是空就停，贴给所有者）

1. 工作台没有在跑的委托、sig-am 的 app-server 没有在跑的 turn（同 #83 发前那次查法）。
2. knowlab 没有在测的分身：`select id, status, run_id from knowbot_test where status in ('queued','running','waiting');`
3. **knowfeed 有没有停在队里的 Wind 作业**（账 184 修好后，这些会在部署后自动开跑、调 Wind）：

   ```sql
   select j.id, j.channel_id, j.status, j.created_at, count(i.id) as waiting_items
   from supply_job j
   join supply_channel c on c.id = j.channel_id and c.plugin = 'wind-mcp'
   left join supply_demand_item i on i.job_id = j.id and i.status = 'fetching'
   where j.status in ('queued','waiting','running')
   group by j.id order by j.created_at;
   ```

   有行就停：这些是用户确认过、一直没派出去的查询；**跑不跑由所有者定**（照跑、还是先在管理端取消）。

## 三、发布

```bash
cd ~/worktrees/qwen/sunmoonun && make -C infrastructure jenkins-release-run RELEASE_BRANCH=qwen APPS="knowbase knowfeed knowbench knowlab" PIN=heads NOTE="qwen-018 下一批：账 180–188、K29、183"
```

照 Jenkins 的人批页看改钉（4 个应用的父仓与子仓号与第一节一致）、镜像锁（变的只有这四个应用的子仓）、迁移（knowbench 计划核到 `20261106_0039`，其余三个迁移头不变）再批。批完等到 `11 检查` 全过；Jenkins 推的回执在 `scripts/results/release-<号>.*.md`。

## 四、上线后核

| # | 谁 | 做什么 | 要看到 |
| --- | --- | --- | --- |
| 1 | Qwen | knowbase、knowfeed、knowbench、knowlab 四个 api 与 worker 最近 10 分钟日志查 `Traceback\|ERROR` | 没有命中 |
| 2 | Qwen | knowbench 迁移 Job 按名直查 | `Complete`，库里 `alembic_version` 是 `20261106_0039` |
| 3 | 所有者 | knowlab 网页用作者账号，在一份工作稿「数据」栏挑一份表格 | 挑得上，不报「No such material」（账 180）；挑一份 GBK 编码的 CSV 也挑得上（账 186） |
| 4 | 所有者 | knowlab 网页打开一次正在跑的作者测试，看本轮问题、点「停止」 | 看得到问题；停下后显示已停止；knowbench 普通工作台不再列这次测试（K29） |
| 5 | 所有者 | knowlab 网页登录过期后从「申请」「测试」等栏重新登录 | 回到原来那一栏（账 182） |
| 6 | 所有者（可选，会花 Wind 额度） | 工作台请专家时确认一条 Wind 查询 | 作业派出去、拿到回执（账 184） |

不做的：不代确认采单、不恢复历史失败轮次、不新开付费测试。

## 回执

`scripts/results/qwen-018.<时间>.md`：第一、二节输出原文；第三节 Jenkins 号、tag、人批页的改钉与镜像锁摘要、`11 检查` 结果；第四节各行（所有者的写一句结果）。提交并推到 qwen，跟所有者说「推好了」。
