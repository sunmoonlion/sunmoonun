# Qwen 发布卡 qwen-019：固定专家按计划执行，先只对所有者本人开（SDD 0050）

> 状态：**作废，由 [qwen-020](2026-11-07-qwen-020-facts-and-fixed-plan.md) 取代**（所有者 11-07 定三个应用成组发）。作废前：暂停（Opus 2026-11-07）：knowbench 的 `qwen` 头上又多了 SDD 0051 的「按指标要数」（第 0 步改成按指标要、提示不再叫模型走 Wind）。只发 knowbench 会坏：线上 knowbase、knowfeed 还不认要数的需求，第 0 步会失败；而且 Wind 的指标对照还没做，要数的会全走巨潮。等所有者定 0051 怎么发后重写这张卡。原状态：可执行（Opus 2026-11-06 写；计划第 11 项）。
> 为什么：固定专家（财务分析与预测等）和动态专家收成同一条执行路（11-03 决定、K31）。远程已做十二个场景的等价验收，开着、关着逐项相等；还没在真环境、真模型上跑过。只有一个开发站点、没有单独测试环境，所有者 11-06 定**先只放本人账号**，本人跑通保底题再放开。

```text
被测仓：sunmoonun，qwen 工作树 ~/worktrees/qwen/sunmoonun，分支 qwen
一次发布：knowbench，PIN=heads（钉到 knowbench-app 在 qwen 的头，子仓取父仓的 gitlink）
迁移：没有新迁移，knowbench 迁移头仍是 20261106_0039（部署声明 expected_schema_revision 已是它）
部署配置：knowbench-backend config.yaml 的 domain_env 加了 WORKBENCH_FIXED_AS_PLAN_OWNERS（只有所有者本人的 subject）
不发：其它五个应用；knowbench 网页与管理端不变
停下的规则：任何一步 exit 不是 0 就停，输出原样进回执，不重试、不退回
做完：回执提交并推到 qwen（提交即推；推不上去就停下说，不 rebase）
```

## 这一次上什么

| 子仓 | 线上（#85） → 这次 | 内容 |
| --- | --- | --- |
| knowbench-backend | `c7d3d14d` → `e9cf02f9` | K29 浏览只认标记列（#85 后对账 0 才动）；目录模型「接什么」照 knowmart 改成可不写（逐字段比对查出）；固定专家计划回执（生成、写入、读回）；执行核心收成一路；名单开关；十二个场景等价验收 |
| knowbench-web-frontend | `7026bfea` 不变 | — |
| 部署配置 | sunmoonun `gitops/…/knowbench-backend/config.yaml` | `WORKBENCH_FIXED_AS_PLAN_OWNERS: '["721f2c10-…ea7"]'` |

名单里的账号**新受理**的固定专家委托会多一份平台写的计划回执（`__method_plan__`，不进时间线、不开尝试），之后按回执取输入、开步、验收、收尾；用户看到的步骤、成果名、成稿不变，交回里的「已核实」清单变成已接受的各步结果（所有者 11-06 接受）。不在名单里的账号、动态专家、已经在跑的委托都不受影响。

远程（云端容器）跑过的：knowbench 后端全量（真库）、等价验收十二个场景（连跑八次稳定）、名单外账号照旧路一条。**真模型、真沙箱、页面都没在远程跑过。**

## 一、核对（只读）

```bash
cd ~/worktrees/qwen/sunmoonun && git log --oneline -1 && git status --short | head -3
d=~/worktrees/qwen/knowbench-app; git -C $d fetch -q origin qwen; printf "knowbench 本地 %s 远端 %s\n" $(git -C $d rev-parse --short=8 HEAD) $(git -C $d rev-parse --short=8 origin/qwen); git -C $d submodule status
grep -n "WORKBENCH_FIXED_AS_PLAN_OWNERS\|expected_schema_revision" gitops/components/app-platform/knowbench-app/knowbench-backend/config.yaml
make -C infrastructure platform-status; echo "status exit=$?"
```

要看到：knowbench 父仓本地与远端同号、是 `4ad760d5`；knowbench-backend 子仓 `e9cf02f9`、web 仍是 `7026bfea`；config 里有名单那一行、迁移版本 `20261106_0039`；`status exit=0`。不一致就先 `~/worktrees/qwen/sunmoonun/docs/process/switch-test/five-repos-sync/sync-five-repos.sh pull` 再核。

## 二、发前查两样（只读，有任何一样不是空就停，贴给所有者）

1. 工作台没有在跑的委托、sig-am 的 app-server 没有在跑的 turn（同 qwen-018 发前那次查法）。
2. 名单里的 subject 确实是所有者本人的账号，且只有一行：

   ```sql
   select count(*) from auth_user where subject = '721f2c10-db3f-4ca4-b6bf-093bb4420ea7';
   ```

   要 `1`。不是 1 就停，**不要自己换别的 subject**。

## 三、发布

```bash
cd ~/worktrees/qwen/sunmoonun && make -C infrastructure jenkins-release-run RELEASE_BRANCH=qwen APPS="knowbench" PIN=heads NOTE="qwen-019 固定专家按计划执行，名单只有所有者本人"
```

照 Jenkins 的人批页看：改钉只有 knowbench（父仓与 backend 子仓），镜像锁变的只有 knowbench-backend，迁移计划核到 `20261106_0039`（不变），渲染出的 knowbench-backend 环境里有 `WORKBENCH_FIXED_AS_PLAN_OWNERS`。再批。批完等到 `11 检查` 全过；Jenkins 推的回执在 `scripts/results/release-<号>.*.md`。

## 四、上线后核

| # | 谁 | 做什么 | 要看到 |
| --- | --- | --- | --- |
| 1 | Qwen | knowbench api、worker、runner 最近 10 分钟日志查 `Traceback\|ERROR` | 没有命中 |
| 2 | Qwen | knowbench runner 的 Pod 环境里查 `WORKBENCH_FIXED_AS_PLAN_OWNERS`（只看有没有这个变量和它的值，不打印别的环境变量） | 值是名单那一个 subject |
| 3 | 所有者 | 在 knowbench 网页用**本人账号**请「财务分析与预测」，问双轨计划 8.2 的回归题：「分析贵州茅台 2023—2025 年营业收入、归母净利润和经营现金流，给出 2024、2025 年同比、各年归母净利率及来源。」照常确认数据、等它做完 | 步骤和以前一样一步步走完，成稿照常写出；数值与来源由所有者判断（会花模型费用，所有者自己点） |
| 4 | Qwen | 第 3 行那件委托跑完后，按委托编号只读查：`select state, current_step, accepted_plan_version, pack_source from workbench_tasks where id = '<委托编号>';` 与 `select step_id, status, refs->>'kind' as kind from workbench_attempts where task_id = '<委托编号>' order by created_at;` | `accepted_plan_version = 1`；各步尝试的 `kind` 是 `method_step`；状态 `SUCCEEDED`（若停在等人，照实写停在哪一步、为什么） |
| 5 | Qwen | 名单外没有走新路：`select count(*) from workbench_tasks t join auth_user u on u.id = t.owner_actor_id where t.accepted_plan_version is not null and t.created_at > '<本次发布完成时刻>' and coalesce(t.pack_snapshot ? 'runtime_contract', false) = false and u.subject <> '721f2c10-db3f-4ca4-b6bf-093bb4420ea7';` | `0` |

**出问题就回退**：把 config 里那一行改成 `WORKBENCH_FIXED_AS_PLAN_OWNERS: '[]'`，照第三节再发一次 knowbench。已经写了回执的委托照回执做完（代码两条路都认），新委托回到老路；不删回执、不改库。

不做的：不代所有者请专家、不代确认数据、不新开付费测试、不放开名单。

## 回执

`scripts/results/qwen-019.<时间>.md`：第一、二节输出原文；第三节 Jenkins 号、tag、人批页的改钉与镜像锁摘要、`11 检查` 结果；第四节各行（第 3 行所有者写一句结果，第 4 行贴查询输出）。提交并推到 qwen，跟所有者说「推好了」。
