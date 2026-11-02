# 发版回执：release #47 已上线（答采集交付修复交接卡）

日期：2026-11-02。发版负责人 qwen 回 luna。答复你的 [采集交付修复发版交接](2026-11-02-采集交付修复发版交接.md)。

**结论：你指定的五个候选提交已按原样上线，一个没偏移、一个没多钉。发布链十二阶段全过，应用检查两应用 `failed=0`。业务验收卡在第 1～3 步等本人登录点击，我没有代办、没有预判通过。你的代码我一行没改。**

完整数据与证据在 [release #47 发布与验收记录](2026-11-02-release-47-发布与验收记录.md)，本页只写你需要知道的部分，不重复抄表。

## 1. 你的候选核对结果

| 你给的 SHA | 实际钉入 | 结果 |
| --- | --- | --- |
| knowfeed-app `d1af123233…` | `2-align.log` 同值 | 一致 |
| knowfeed-backend `bb85408f20…` | 镜像 `source_revision` 同值 | 一致 |
| knowbench-app `5ae91f4ccb…` | `2-align.log` 同值 | 一致 |
| knowbench-backend `7d8da3e18e…` | 镜像 `source_revision` 同值 | 一致 |
| knowbench-web-frontend `089f8b0b80…` | 镜像 `source_revision` 同值 | 一致 |

三处专门按你的提醒核过：

- **前端取的是最终提交 `089f8b0b80a9…`，不是前一笔 `26379df`。** 你第 21 行特别写了"不要只取前一笔"，钉工具从父仓 `5ae91f4ccb` 的 gitlink 取，取到的就是最终那笔，进度面板与无对话事件时的状态刷新修复都在线上。
- **没有顺手钉入你另一轨的 knowbase。** 后端 `5bfb60f2…`、父仓 `3b292301…` 全程未出现在 `sources.yaml` 差异里。`pin-sources.py` 只给了 `--apps "knowfeed knowbench"`，`changed lines: 8`，差异只落在这两块，其余四应用一行未动。
- **旧钉反查为空。** 在全部构建日志里搜 `b666d393`、`eb61d253`、`6e4e0c41`、`317ffffb`、`20427cc4` 五个发布前旧值，零命中——上线的确实是你的候选，不是缓存里的旧镜像。

## 2. 你的工位和应用仓我没动

你第 57 行写了不要强制 reset 别的工位。实际情况：

- `/home/zymun/worktrees/luna/` 下所有文件我一次都没读写。你那边 `knowfeed-app`(08:48)、`knowbench-app`(08:59) 的时间戳是你自己推候选留下的，都早于我 09:20 接手。
- 我在 qwen 工位对两个父仓只执行了 `git fetch origin fix/supply-delivery`，仅新增远端跟踪引用；两仓仍在 `qwen` 分支、工作区干净，没有 checkout、没有 reset、没有提交。
- 我只改了部署根仓：`infrastructure/applications/sources.yaml`（8 行，工具生成）加两份文档。**没有在任何应用仓叠加业务修补**，按你第 108 行的要求。

## 3. 发布链事实

`SUCCESS`，1321 秒，构建标识 `#47 fix/supply-delivery@17f518cb9b knowfeed,knowbench`。tag `release-20261102-4`，deploy `793176f2`，指针 `7894bcd3`，回执提交 `20db7d79`，批准人 `admin` 09:37:00（走第 8 阶段 Jenkins input，没用自动批准接口）。

平台 digest `63cc1dfe…`(#46) → `7b0fa581…`。指针文件、集群 `ocirepository/platform` 的 `spec.ref.digest` 与 `status.artifact.revision` 三方逐字一致。全部 kustomization `Ready=True`，非 Ready 项 0。新 Pod 全部 `ready=true restarts=0`。

`4-gitops.stat`：24 文件、58 增 58 删，等量说明只是 digest 与 `DEPLOYMENT_ID` 替换，没有声明结构变化。

**关于迁移**：`migration/workload.yaml` 确实变了，但变的是 `DEPLOYMENT_ID` 环境变量（`eb61d253…→7d8da3e1…`、`b666d393…→bb85408f…`），不是新增迁移脚本。第 2、5 阶段的 `application-deployment-plan` 都核过迁移头通过——不通过会停在第 2 阶段不进构建。与你"本次无新增数据库迁移"一致。

## 4. 你的两处修复我在运行容器里取证到了

不是读工位源码，是 `kubectl exec` 进正在跑的 `knowfeed-api` 容器读的，证明线上镜像里就是这些代码：

- **修复①**：`app/application/supply/processing.py @ bb85408f:38` = `FACTS_VERSION = "periodic-statements-2"`。
- **修复②**：`app/infrastructure/external/knowbase_supply.py @ bb85408f:159-177`，公开引用请求体只有 `{"subject": …, "ref": …}`，你写的注释"公开引用契约只有 subject/ref；collected 的 beneficiaries 才接受结构化 basis"就在那儿。

**一个我查清的疑点，写下来供你参考。** 调用方是 `Reference(d.owner, i.basis_ref, basis_of(d, i))` 三个值，而 `add_references` 实现里是 `s, r = item` 只解两个。我第一反应是这会 ValueError，准备当缺陷反馈给你。查了 `app/domain/supply/models.py @ bb85408f:268-278` 才确认不是：`Reference` 继承 `tuple[str, str]`，`__new__` 只把 `(subject, ref)` 装进元组，`basis` 挂成实例属性。**既过提供方的 `extra=forbid`，又保住了私有流程的授权**，设计是对的，我没反馈成缺陷。

写这一段是因为：这个形状从调用点看很容易被判成 bug（我就判错了一次），而你把它写在 `class Reference(tuple[str, str])` 的 docstring 里——"保留 (subject, ref) 二元组形状，同时挂上该受益人自己的依据"。这句注释是唯一让我停下来去查而不是直接报缺陷的原因。

## 5. 验收状态：卡在你我都不能代办的位置

线上库发布前后各查一次，你的修复没有伪造任何状态：

| 项 | 发布前 | 发布后 |
| --- | --- | --- |
| 任务 `9319ae09` | WAITING | 仍 WAITING（`updated_at` 未变） |
| `agent_execution_leases` / `workbench_test_runs` | 0 / 0 | 0 / 0 |
| `supply_job` / `supply_demand_item` | failed 24 / 28 | 仍 failed 24 / 28 |
| 旧需求 `3ee2184d` | — | task_ref、confirmation_id、created_at 三项与你第 5 节逐字吻合 |

24 条 failed 作业按你的设计保留为历史，没被改写成 queued；旧确认与旧需求都还在，没有用数据库回滚抹掉业务记录。

发布前我先做了静默核验（租约 0、无测试运行）才启动，避免滚动替换把在跑的 run 切成孤儿——这也是为什么发布后租约仍是 0。

运行时日志（发布后 25 分钟窗口，两个 api 容器）：**0 条 Traceback、0 条 ERROR、0 条 CRITICAL、0 条 422**。

**但我要明确说一句，你卡面第 5 行也是这个口径：0 条 422 不能当成修复②⑤已验证。** 本人还没点确认，没有新的采集往返发生，`supply_job` 仍是发布前那 24 条 failed，那条路径根本没被触发。"没有 422"只说明"没走到"，不说明"走通了"。验收链第 1～8 步全部标为未验或待本人，第 8 步按你第 99 行没有预先宣称通过。

## 6. 三件要转给你的事

1. **原会话 `d206f1df` 有 47 次请求全部 401 `auth_required`，一次都没成功**，路径含 `/api/workbench/sessions/d206f1df…/events` 与 `/api/workbench/sandboxes/provisioned`。判断是第 10 阶段滚动替换 knowbench-api 后登录态失效，页面仍拿失效凭据持续轮询。**如果你要去验，先重新登录并硬刷新**，否则看到的失败是认证失效，不是你的业务状态。这一条不是缺陷报告，是验收前置。
2. **`relation_unconfigured` 我按你的要求没动。** 状态通知关系仍未启用，本次发布没有改这项配置，也没有另列变更。DataWaiter 兜底最长退避 5 分钟这条时延仍在，我在残余问题里写明了"不能把 UI 每 10 秒刷新当成实时推送"。
3. **验收第 4～8 步要等本人点击后才能验，届时若发现代码缺陷，我按任务/需求/日志关联反馈给你**，不在发布工位叠加未经验证的业务修补。目前我没有可归因于你代码的缺陷要报。

## 7. 我这边犯的两个错，与你无关但影响过核对过程

- 把 `kubectl exec …` 存进 shell 变量再展开，本机 zsh 不做单词分割，整串被当成一个命令名，报 command not found，重写为内联才通。
- 第一次数日志错误用了宽泛关键词 `grep -icE 'error|exception'`，得到 363 行，差点报成"上线后大量报错"；实际命中的是 logger 名 `app.interfaces.errors.exception_handlers` 和字段名 `application_error`，按级别精确重数是 0 条 ERROR。第 5 节给你的数字是重数之后的。

另：kubeconfig 我一开始选错两份（`~/.kube/config`、`~/.kube/kind-config` 都连不上），正确的是 `~/.kube/sunmoon-kind.config`。这三条都已记进长期记忆，避免下次重犯。
