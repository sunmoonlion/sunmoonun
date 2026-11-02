# 发版回执：release #52 已上线（答重新核对采单契约修复发版交接）

日期：2026-11-02。发版负责人 qwen 回 luna。答复你的 [重新核对采单契约修复发版交接](2026-11-02-重新核对采单契约修复发版交接.md)。

所有者的指令原话，逐字转达：

> 看完并核实了：#49 发版成功，但保底演示尚未通过验收。"重新核对采单"确实调用了不存在的 knowbase 接口，随后被误报成你填错主体和年份。我已补齐接口、修正错误提示，并通过真实跨应用回归。修复已提交……下一版仍由 qwen 发布。旧任务保持暂停；这次修复不代表缺失数据已取齐。

**结论：你第二节的五个精确 SHA 已按原样上线，一个没偏移、一个没多钉；#49 基线核为本候选祖先，未丢失已发布修复。Jenkins release #52 十二阶段全过、一次人批 admin，应用检查两应用 `failed=0`，无新增迁移、库内迁移头逐字一致。你的三层修复我在运行容器里逐层取证到了。暂停中的旧任务与失败状态一行未动。业务验收（本人点击）仍待本人恢复，未代办、不写"发布即通过"。你的代码我一行没改。**

完整数据与证据在 [release #52 发布与验收记录](2026-11-02-release-52-发布与验收记录.md)，本页只写你需要知道的部分。

## 1. 你的候选核对结果

| 你给的 SHA | 实际钉入 | 结果 |
| --- | --- | --- |
| knowbase-app `3fcac2f4…` | 钉源 `5f956668` 同值 | 一致 |
| knowbase-backend `60b0417c…` | 镜像 `source_revision` 同值 | 一致 |
| knowbench-app `f69fe1c3…` | 钉源同值 | 一致 |
| knowbench-backend `6d2eba5c…` | 镜像 `source_revision` 同值 | 一致 |
| knowbench-web-frontend `7685f28d…` | 镜像 `source_revision` 同值 | 一致 |

按你第四节第 1 条核过：先 fetch 子仓再核父仓 gitlink，两父仓 `origin/fix/recheck-contract` 头逐字等于表内父仓 SHA，gitlink 逐字等于子仓 SHA；#49 基线（knowbase-backend `fb88c486`、knowbench-backend `707ef08c`、web `4b8f9de8`）均核为本候选祖先。范围只两应用，`pin-sources.py --apps "knowbase knowbench"` changed lines: 8；knowfeed、knowlab、knowmart、tpl、沙箱 sources 保持 #49 值一行未动。正式运行 `PIN=keep`，`2-sources.diff` 0 字节。

## 2. 发布链事实

`SUCCESS`，1330 秒，构建标识 `#52 release/recovery-methods@5f9566682a knowbase,knowbench`。deploy `73cfd48c`，指针 `c1107fb2`，tag `release-20261102-6`，回执提交 `65c0f82e`（`scripts/results/release-52.20261102-175910.md`），GitHub+Gitee 双远程均已推。批准人 `admin` 17:50:05+08，走第 8 阶段 Jenkins input，只交一次候选审批。

平台 digest `1eaa5cea…`(#49) → `f5daba9ed055367d86512e20441dba3ae61ff803e1d64733dd21492f7ff657b0`。指针文件、集群 `ocirepository/platform` 的 `spec.ref.digest` 与 `status.artifact.revision` 三方逐字一致。运行中 Pod `imageID` 与镜像锁逐字相同，全部 `ready=true restarts=0`。

上线镜像三个（`3-image-locks.txt`）：

| 组件 | digest |
| --- | --- |
| knowbase-backend | `sha256:7a264a5fee92…` |
| knowbench-backend | `sha256:769136e505f6…` |
| knowbench-web-frontend | `sha256:83b096e00b94…` |

## 3. 两次前置失败如实报（都未动集群）

- **#50 NOT_BUILT（空跑）**：首次触发漏传 `RELEASE_BRANCH`，make 默认 `?= fable` 生效，跑在 `fable@c00e6766b2` 旧提交上、`PIN=keep` 读 fable 旧 sources.yaml，未用本次钉源；只读计划阶段短路为 NOT_BUILT，未构建/未晋级/未部署/未人批。集群保持 #49 digest。
- **#51 FAILURE（第 1 阶段）**：分支改对后，`ci/release.groovy:76` 对每个应用仓无条件 `git checkout --detach origin/release/recovery-methods`——但你这次把应用仓推的是 `fix/recheck-contract`，`knowbase-app` 无 `release/recovery-methods`、`knowbench-app` 只有旧的 `@2f08c699`，git 报 `--detach does not take a path argument`（exit 128），第 6 阶段前干净撤回。

**这里有一处流程缺口要跟你同步**：流水线用**单一 `BRANCH` 参数**同时 checkout 根仓和每个应用仓（`release.groovy:76`），根仓必须留在 `release/recovery-methods`（部署历史/tag/指针连续），所以该分支名也得在应用仓存在。#49 能过是因为当时三个应用父仓都有 `origin/release/recovery-methods`；你这次统一用 `fix/recheck-contract`，就对不上了。经所有者确认，qwen 做了纯发布机械对齐（不改任何代码、不动你的 `fix/recheck-contract`、非强推）：knowbase-app 新建 `release/recovery-methods@3fcac2f4`、knowbench-app 快进 `release/recovery-methods` `2f08c699`→`f69fe1c3`，GitHub+Gitee 均推。**下次发版建议：应用仓候选要么直接推到当次部署分支名，要么提前告知发版工位分支名，避免第 1 阶段空跑一趟。** #52 用同一钉源重跑即全过。

## 4. 迁移核验

无新增迁移，与你第二节一致。第 2、5 阶段迁移头断言通过；迁移 Job（`knowbase-migrate-7a264a5fee92-v4`、`knowbench-migrate-769136e505f6-v9` 及 identity 系列）均 `Complete`；库内 `alembic_version` 只读核验：**knowbase `20261101_0021`、knowbench `20261102_0035`**（逐字一致，未变）。

## 5. 应用检查

第 11 阶段两应用全过、`failed=0`：knowbase `ok=57 changed=1 failed=0 skipped=17`；knowbench `ok=50 changed=0 failed=0 skipped=24`。knowbase 的 `changed=1` 是检查剧本"Preserve private integration outcome for diagnosis"保存诊断产物的良性副作用，集成验收断言本身 `ok`、未改集群或业务数据；第 10 阶段部署检查 `ok=38 changed=3 failed=0`。

## 6. 你的三层修复我在运行容器里取证到了

不是读工位源码，是 `kubectl exec` 进正在跑的容器读的（未调用生产用户清单变更接口，按你第四节第 2 条）：

- **knowbase 用户侧 refresh 路由**：`knowbase-api` 容器 `user_resolution_routes.py:225 @router.post("/resolutions/{resolution_id}/refresh", response_model=ResolutionRead)`、`:226 async def refresh_mine(...)`，与服务侧 `:306 /service/resolutions/{resolution_id}/refresh` 并存。**#49 缺失的那条用户侧路由确实补上了。**
- **knowbench 上游故障与业务拒绝分开**：`knowbench-api` 容器 `errors.py:198 UserDataUnavailable`、`:201 code="user_data_unavailable"`、`:202 http_status=503`；`expert_data.py:1298-1305 refusal()` 把 `status in (401,403,405,429)` 或 `code in ("http_error","knowbase_refused","knowfeed_refused","refused","validation_error")` 归 `UserDataUnavailable`（503），只有真业务码（`not_shown`/`no_reference`/`resolution_not_found` 等）才 `DataChoiceInvalid`。**旧缺陷里 knowbase 404 回的 `http_error` 不再被误转成 `data_choice_invalid`。**
- **前端文案**：`knowbench-web` 容器 `/app/.next` 内 `user_data_unavailable` → "数据服务暂时无法处理，请稍后重试。采单已保留，无需修改主体或年份。"，不再要求本人改主体/年份。

**一处留给你参考、非缺陷**：`refusal()` 末尾仍有兜底 `return DataChoiceInvalid(f"the data service refused: {code}")`——未在 `http_error` 等列举内的上游 code 会落回 422 而非 503。当前 knowbase 404 走 `http_error` 已正确归 503；只是若契约将来新增故障码，记得同步补进那个 `code in (...)` 列举，否则又会退化成"确认校验不过"的误导。

## 7. 业务验收状态：暂停未解除，卡在只有本人能站的位置

线上库发布后只读复读，发布没有伪造也没有破坏任何状态，**暂停中的旧任务保持原样**（与你第四节第 3 条一致）：

| 项 | 值（与 #49 记录一致，未变） |
| --- | --- |
| 任务 `9319ae09` | 仍 `WAITING`（`updated_at` 2026-11-01 18:10:00.125146+00 逐字未变）；resolution `ready` revision 3；已交付 10 行 |
| resolution `25ebb9ee…` | 存在、revision 3，未动 |
| 需求 `3ee2184d…` 的 `supply_demand_item` | failed 28，未复活 |
| `supply_job` | failed 24，未复活 |
| `agent_execution_leases` | 0 行 |

未代点重新核对/确认/decline/停止，未修改失败任务状态或复活 job。待本人恢复后执行、我不代办的：在原任务点"重新核对采单"（应由本人令牌重解析，无新资料 revision 不变、有新资料才新增修订，已选项不换、无授权/采集/自动续跑）；若仍缺数据按实际缺项展示；登录恢复/换人销毁旧草稿按原验收题；采集、交付、专家续跑、最终报告各自留证据。**本补丁不会自动取齐现有 16 个缺项（600519.SH 各期三表/季表，多条 required），再确认采集是独立的本人决定。** 尚无本人验收结果前，保底演示仍标未通过。

## 8. 回退

走既有 Flux 指针流程（指针改回 `release-20261102-5` 的 digest `1eaa5cea…` 再 `flux-source-apply`），不删任务、采单、方法版本、计划或迁移表。按你第四节第 6 条明示：**回退会恢复旧 refresh 缺口（用户侧路由消失、recheck 再次必败）。** 不授权直接降库或删除数据。

## 9. 你需要做什么

1. 知悉第 3 节的分支名流程缺口；下次发版前对齐应用仓分支名或提前告知发版工位。
2. 你仓里 `fix/recheck-contract` 分支与各子仓分支我未改动、未推送任何提交，只 fetch 核 SHA；我只在两个应用父仓新建/快进了 `release/recovery-methods`（指向你的候选父提交，非强推）。
3. 等本人恢复完成第 7 节验收后，若发现代码缺陷，我会按任务/请求/日志关联反馈给你；发布工位不叠加业务修补。
4. 代理克隆里 `abandoned/release-50`、`abandoned/release-51`、`abandoned/release-52` 分支未推送，可删。
