# Qwen 发布卡 qwen-020：按指标要数（SDD 0051）＋固定专家新路名单（SDD 0050），三个应用成组发

> 状态：**可执行**（Opus 2026-11-07 写；取代暂停的 [qwen-019](2026-11-06-qwen-019-fixed-expert-as-plan.md)）。所有者说「发」再跑。
> 为什么成组：knowbench 第 0 步现在会按指标要数（主体、期间、科目编码、口径），只有新的 knowbase 认得这种需求、只有新的 knowfeed 会去取；三个只要少发一个，第 0 步就会失败。所有者 11-07 定：三个一起发，Wind 的指标对照做好前，要数的先全走巨潮（下年报抽表，慢，但都是公告原件、能核页码）。

```text
被测仓：sunmoonun，qwen 工作树 ~/worktrees/qwen/sunmoonun，分支 qwen
一次发布：knowbase knowfeed knowbench，PIN=heads（钉到三个父仓在 qwen 的头，子仓取父仓的 gitlink）
迁移：三个都没有新迁移（knowbench 仍 20261106_0039；knowbase、knowfeed 迁移头不变），部署声明的期望版本不用改
部署配置：knowbench-backend config.yaml 的 domain_env 有 WORKBENCH_FIXED_AS_PLAN_OWNERS（只有所有者本人的 subject），qwen-019 时已加
不发：knowlab（只跟了契约锁、加了一个还没用到的模型，行为不变）、tpl、knowmart、link
停下的规则：任何一步 exit 不是 0 就停，输出原样进回执，不重试、不退回
做完：回执提交并推到 qwen（提交即推；推不上去就停下说，不 rebase）
```

## 这一批上什么

| 应用 | 子仓（线上 #85 → 这次） | 内容 |
| --- | --- | --- |
| knowbase | 后端 `bf59f85d` → `3b23eb52` | 解析「要哪些数」：先在标准化层找本人能用的，同一个数在几份报告里时按当期原始披露 / 最新调整后挑，缺的交 knowfeed；契约 data-request/v1、user-data/v2 都是加法 |
| knowfeed | 后端 `4b5d9ac3` → `d0552d13` | 收要数的需求项：照用户确认的原样留住键，自己推「落在哪份定期报告里」去找渠道；Wind 只认配置里有对照的科目（现在没有对照，所以不认），落到巨潮 |
| knowbench | 后端 `c7d3d14d` → `d6257003`；网页 `7026bfea` → `c8f70622` | 第 0 步按指标要数、提示不再叫模型点名供应商；数据清单能显示要数的条目；固定专家新路（名单只放所有者本人）；K29 只认标记列；目录模型「接什么」照 knowmart |

远程（云端容器）跑过的：三个后端全量（真库），knowbench 网页 typecheck、lint、i18n、单测、`next build`；knowfeed 端到端「要数 → 巨潮年报 → 交 knowbase 抽表写事实 → 就绪」（假渠道）。**真模型、真沙箱、真巨潮、页面都没在远程跑过。**

## 一、核对（只读）

```bash
cd ~/worktrees/qwen/sunmoonun && git log --oneline -1 && git status --short | head -3
for a in knowbase knowfeed knowbench; do d=~/worktrees/qwen/$a-app; git -C $d fetch -q origin qwen; printf "%-10s 本地 %s 远端 %s\n" $a $(git -C $d rev-parse --short=8 HEAD) $(git -C $d rev-parse --short=8 origin/qwen); git -C $d submodule status; done
grep -n "WORKBENCH_FIXED_AS_PLAN_OWNERS\|expected_schema_revision" gitops/components/app-platform/knowbench-app/knowbench-backend/config.yaml
make -C infrastructure platform-status; echo "status exit=$?"
```

要看到：三个父仓本地与远端同号，且是 knowbase `582efeaa`、knowfeed `56ed9df0`、knowbench `915e31c4`；子仓号与上表一致；config 里有名单那一行、knowbench 迁移版本 `20261106_0039`；`status exit=0`。不一致就先 `WS=qwen bash ~/switch-test/human-local.sh` 再核。

## 二、发前查三样（只读，有任何一样不是空就停，贴给所有者）

1. 工作台没有在跑的委托、sig-am 的 app-server 没有在跑的 turn（同 qwen-018 发前那次查法）。
2. 名单里的 subject 确实是所有者本人，且只有一个账号：`select count(*) from auth_user where subject = '721f2c10-db3f-4ca4-b6bf-093bb4420ea7';` 要 `1`；不是 1 就停，不要自己换。
3. knowfeed 没有停在队里的 Wind 作业（同 qwen-018 第二节第 3 条的查法）。

## 三、发布

```bash
cd ~/worktrees/qwen/sunmoonun && make -C infrastructure jenkins-release-run RELEASE_BRANCH=qwen APPS="knowbase knowfeed knowbench" PIN=heads NOTE="qwen-020 按指标要数（0051）＋固定专家新路名单（0050）"
```

照 Jenkins 的人批页看：改钉只有这三个应用（父仓与子仓号同第一节），镜像锁变的只有 knowbase-backend、knowfeed-backend、knowbench-backend、knowbench-web-frontend，三个应用的迁移头都不变。再批。批完等到 `11 检查` 全过；Jenkins 推的回执在 `scripts/results/release-<号>.*.md`。

## 四、上线后核

| # | 谁 | 做什么 | 要看到 |
| --- | --- | --- | --- |
| 1 | Qwen | knowbase、knowfeed、knowbench 的 api 与 worker（knowbench 加 runner）最近 10 分钟日志查 `Traceback\|ERROR` | 没有命中 |
| 2 | Qwen | knowbench runner 的 Pod 里只查 `WORKBENCH_FIXED_AS_PLAN_OWNERS` 这一个变量 | 值是名单那一个 subject |
| 3 | 所有者 | 用**本人账号**请「财务分析与预测」，问双轨 8.2 的回归题：「分析贵州茅台 2023—2025 年营业收入、归母净利润和经营现金流，给出 2024、2025 年同比、各年归母净利率及来源。」看第 0 步列出的数据：可能出现「要哪些数」的条目（如「营业收入… 2025」）；照常确认 | 清单能正常显示、能确认；要的数 knowbase 里有就直接定，没有的去取（走巨潮，会慢）；数到了委托接着做完。数值与来源由所有者判断（会花模型费用，所有者自己点） |
| 4 | Qwen | 第 3 行那件委托：`select state, accepted_plan_version from workbench_tasks where id = '<委托编号>';`；`select step_id, status, refs->>'kind' from workbench_attempts where task_id = '<委托编号>' order by created_at;` | `accepted_plan_version = 1`（固定专家走了新路）；各步 `kind` 是 `method_step`；状态 `SUCCEEDED`（停在等人就照实写停在哪、为什么） |
| 5 | Qwen | knowfeed 库：`select status, channel_id, key->>'kind', reason from supply_demand_item where created_at > '<本次发布完成时刻>' order by created_at;` | 若有 `kind = facts` 的项：渠道是巨潮、状态最后是 `ready`；有 `unsatisfiable` 的照实贴 |
| 6 | Qwen | 名单外没走新路：同 qwen-019 第四节第 5 行那条 SQL | `0` |

**出问题就回退**：
- 只是固定专家新路的问题：把 config 里那一行改成 `WORKBENCH_FIXED_AS_PLAN_OWNERS: '[]'`，照第三节只发 knowbench。
- 要数那条路出问题（第 0 步失败、清单打不开）：三个应用一起退回 #85 的钉（knowbase `cb1cb10a`、knowfeed `67638eb9`、knowbench `6049c865` 那一版），不改库、不删数据；照实贴给所有者，Opus 修。

不做的：不代所有者请专家、不代确认数据、不新开付费测试、不放开名单、不在管理端给 Wind 配指标对照。

## 回执

`scripts/results/qwen-020.<时间>.md`：第一、二节输出原文；第三节 Jenkins 号、tag、人批页的改钉与镜像锁摘要、`11 检查` 结果；第四节各行（第 3 行所有者写一句结果，第 4、5 行贴查询输出）。提交并推到 qwen，跟所有者说「推好了」。
