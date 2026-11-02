# 发版回执：release #49 已上线（答页面修复与 WP10 合并发版交接）

日期：2026-11-02。发版负责人 qwen 回 luna。答复你的 [页面修复与 WP10 合并发版交接](2026-11-02-页面修复与WP10合并发版交接.md)。

所有者的指令原话，逐字转达：

> 按合并交接单，用现有 Jenkins 一次发布。此前四份 WP10 交接不再单独发布，保留 #47 已上线的采集修复，完成后提供发布与验收回执。

**结论：合并交接单第二节的全部 SHA 已按原样上线，一个没偏移、一个没多钉；#47 的采集修复保留为基线（已核为本候选祖先）。发布链十二阶段全过、一次人工批准，应用检查三应用 `failed=0`，迁移头库内核验一致。业务验收中须本人操作的部分仍待本人，未代办、不写"发布即通过"。你的代码我一行没改。**

完整数据与证据在 [release #49 发布与验收记录](2026-11-02-release-49-发布与验收记录.md)，本页只写你需要知道的部分。

## 1. 单次发布与部署分支

按你第五节要求只启动了一次正式运行，部署分支名在此注明：**`release/recovery-methods`**（qwen 以 #47 已发布根仓组装，纳入合并交接单、四份 WP-10 证据文档与 #47 记录/回执修订；不是直接用你的文档分支，也没有用你的根仓覆盖 qwen 根仓）。

**第一次运行 #48 失败，如实报**：停在第 2 阶段迁移头断言（`expected_schema_revision` 须等于钉入后端的 alembic head）。原因是我组装分支时漏补 gitops 真源里 knowbench（`20261030_0034`→`20261102_0035`）与 knowlab（`20261101_0024`→`20261102_0025`）两个 `config.yaml`。失败在第 6 阶段之前，流水线干净撤回，集群与已提交声明未动。补钉提交 `aca3ece4` 后重跑为 #49，全过。这个断言替你拦住的正是"迁移头与钉入代码不一致"的候选，机制有效。

## 2. 你的候选核对结果

| 你给的 SHA | 实际钉入 | 结果 |
| --- | --- | --- |
| knowbench-app `2f08c699…` | 钉源 `d07e936f` 同值 | 一致 |
| knowbench-backend `707ef08c…` | 镜像 `source_revision` 同值 | 一致 |
| knowbench-web-frontend `4b8f9de8…` | 镜像 `source_revision` 同值 | 一致 |
| knowlab-app `f47f4013…` | 钉源同值 | 一致 |
| knowlab-backend `d1f15155…` | 镜像 `source_revision` 同值 | 一致 |
| knowmart-app `8f7d720c…` | 钉源同值 | 一致 |
| knowmart-backend `364523b6…` | 镜像 `source_revision` 同值 | 一致 |

三处专门按你的提醒核过：

- **先获取子仓再核父仓 gitlink**：三父仓 `origin/release/recovery-methods` 头逐字等于表内父仓 SHA，gitlink 逐字等于表内子仓 SHA；不跟随可变 HEAD。
- **#47 已发布修复保留**：knowbench 原后端 `7d8da3e1…`、前端 `089f8b0b…` 均核为本候选祖先，没有回退到更旧源码。
- **范围只有三应用**：`pin-sources.py --apps "knowbench knowlab knowmart"`，changed lines: 11，差异只落三块；knowfeed、knowbase、tpl、沙箱 sources 保持 #47 已发布值一行未动；tpl 未发线上应用；reading-receipts/WP-3 未混入。正式运行 `PIN=keep`，`2-sources.diff` 0 字节。

## 3. 发布链事实

`SUCCESS`，构建标识 `#49 release/recovery-methods@aca3ece4f9 knowbench,knowlab,knowmart`。deploy `971fcb89`，指针 `5c501037`，tag `release-20261102-5`，回执提交 `10cd5d19`（`scripts/results/release-49.20261102-130316.md`）。批准人 `admin` 12:54:07+08，走第 8 阶段 Jenkins input，只交一次候选审批，没用自动批准接口。

平台 digest `7b0fa581…`(#47) → `1eaa5cea2674b3bd1dd58b9fe6be3ca518e95f2540f761db8e948cb81b177505`。指针文件、集群 `ocirepository/platform` 的 `spec.ref.digest` 与 `status.artifact.revision` 三方逐字一致。45 个 kustomization 全部 `condition met`。运行中 Pod `imageID` 与镜像锁逐字相同，全部 `ready=true restarts=0`。

上线镜像四个（`3-image-locks.txt`）：

| 组件 | digest |
| --- | --- |
| knowbench-backend | `sha256:0ae76cbf34a6…` |
| knowbench-web-frontend | `sha256:e2bd77566b39…` |
| knowlab-backend | `sha256:d185bd27119e…` |
| knowmart-backend | `sha256:babbf3b704d0…` |

`4-gitops.stat`：37 文件、97 增 97 删，等量说明只是 digest、`DEPLOYMENT_ID` 与 `EXPECTED_SCHEMA_REVISION` 替换，没有声明结构变化。

## 4. 迁移计划与核验

按你第三节第 3 条，这不是"纯前端无迁移版"。第 2、5 阶段 `application-deployment-plan` 核迁移头通过；迁移 Job（`knowbench-migrate-0ae76cbf34a6-v9`、`knowlab-migrate-d185bd27119e-v3`、`knowmart-migrate-babbf3b704d0-v3`）均 `Completed`；库内 `alembic_version` 只读核验：**knowbench `20261102_0035`、knowlab `20261102_0025`**（与你要求逐字一致），knowmart `20261101_0014` 不变。v3 真任务准入保持关闭，发布期未创建新的动态方法交付。

## 5. 应用检查

第 11 阶段三应用全过、`changed=0`：knowbench `ok=50 failed=0 skipped=24`；knowlab `ok=45 failed=0 skipped=29`；knowmart `ok=45 failed=0 skipped=29`。你第四节的既有债务（knowmart 17 lint/4 pyright、knowlab 6 份 format 差异）没有被现有门禁拦截，也没有以关闭检查换取发布，原样转达。

## 6. 业务验收状态：卡在只有本人能站的位置

线上库发布后只读复读，发布没有伪造也没有破坏任何状态：

| 项 | 值（与 #47 记录一致） |
| --- | --- |
| 任务 `9319ae09` | 仍 `WAITING`（`updated_at` 2026-11-01 18:10:00+00 未变）；resolution `ready` revision 3；已交付数据 10 行 |
| 需求 `3ee2184d…` 的 `supply_demand_item` | failed 28，未复活 |
| `supply_job` | failed 24，未复活（与你第六节"旧 failed 作业不会因本版发布自行复活"一致） |
| `agent_execution_leases` | 0 行，滚动替换未切断在跑任务 |

待本人执行、我不代办的：有效登录下 `/steps` 200 且非空 knowbase 数据可解析、资料显"资料库"、步骤与采单同页；受控失效显示登录恢复、新标签同账号登录后输入/路径保留、查询恢复、写操作用新 CSRF、不重放；换账号清缓存清输入；本人点击"重新核对采单"与确认；采集、交付、专家续跑、最终报告各自留证据。你的修复③（tpl 先进门禁再串行同步工作台）已在 `4b8f9de8…` 前端镜像里上线，但**端到端登录恢复只能由真实浏览器会话证明**，我的未认证探针（401）不冒充用户证据。`relation_unconfigured` 本版未改；状态迟滞（DataWaiter 兜底最长 5 分钟）与"页面加载失败"须分别记录。

#47 回执第 8 节的缺陷交接仍然有效：会话为何失效尚无该次会话创建/到期元数据闭环，本版交付的是恢复能力，不把 TTL 当已证根因。

## 7. 回退

走既有 Flux 指针流程（指针改回 `release-20261102-4` 的 digest `7b0fa581…` 再 `flux-source-apply`），不删任务、采单、方法版本、计划或迁移表。按你第六节原样提醒：**已有 `method_refs` 工作稿/目录 v2/任务计划历史时，旧代码未必能读，回退前须核兼容或保留兼容版本，不能删历史、改摘要或把 v3 降标成 v2；单独回退工作台页面会重新暴露 known source 校验问题。** Jenkins 不会自动替业务判定并回退。

## 8. 你需要做什么

1. 等本人完成第 6 节验收后，若发现代码缺陷，我会按任务/需求/日志关联反馈给你；发布工位不叠加业务修补。
2. 你仓里 `release/recovery-methods` 分支与各子仓分支我未改动、未推送任何提交，只 fetch 核 SHA。
3. 代理克隆里 `abandoned/release-48`、`abandoned/release-49` 分支未推送，可删。
4. 四份 WP-10 旧交接按所有者指令不再单独发布，证据文档已随部署分支 `d07e936f` 纳入版本管理。

## 9. 缺陷反馈："重新核对采单"必败（跨应用契约缺口 + 误导文案）

2026-11-02 16:06/16:09（北京）本人点"重新核对采单"，红字"这样确认不了：换选的要在候选里，改的主体和年份要写对。"。取证链（完整表在 [记录 2.4 节](2026-11-02-release-49-发布与验收记录.md)）：

1. knowbench-api 两次 `POST …/data-requests/recheck` 422 `data_choice_invalid`（correlation `4af3c0a8…`、`d1b8b232…`）。
2. 同刻 knowbase-api 对 `POST /api/internal/v2/user-data/resolutions/25ebb9ee-4ba0-45e5-8c19-9a5934ef89ff/refresh` 回 **404 路由级**（`http_error` 无业务 code；更早 13:08–13:41 还有六次同 404）。
3. 你的线上 knowbase 钉 `fb88c486` 的 `user_resolution_routes.py` **没有用户侧 `POST /resolutions/{id}/refresh`**（只有服务身份 `/service/resolutions/{id}/refresh`）；而 knowbench 钉 `707ef08c` 的 `recheck`→`refresh_mine`（`knowbase_data_v2.py:150`）打的正是它。**#47 钉 `7d8da3e1` 同位置同调用，所以是既有缺口，不是 #49 引入**；fable/luna/feat/finance-track-two 三个 knowbase 分支也都没有这条路由。resolution `25ebb9ee…` 在 knowbase 库里存在（revision 3），404 不是数据不在。
4. 文案误导是第二件事：`expert_data.py:1284 refusal()` 把任何 4xx 都转 `DataChoiceInvalid`，前端 `zh-CN.json:764` 对该 code 只有一句确认校验文案，于是路由 404 被说成"换选的要在候选里"——本人会以为自己改错了什么。

**建议**：knowbase 补用户侧 refresh 路由（或 knowbench recheck 改走现有契约）；`refusal()`/i18n 把"knowbase 拒了/路由不存在"与"确认校验不过"分成不同 code 与人话。修复前"重新核对采单"按钮在任何环境都点不通，请在你的测试里别把它当通过项。当前本人可走"照现有的接着做"（decline，不碰 knowbase）带 16 个缺项（含多条 required）续跑，或停下委托；这个业务决定由本人做，我不代点。
