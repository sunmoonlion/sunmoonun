# 回执：0042 批次发布（knowbase → knowmart → knowbench → knowlab，link 0.5.2）

- 日期：2026-10-25 14:30–17:05（北京时间）；执行：Fable，经反向隧道在本地机跑 Jenkins `release`，所有者在第 8 阶段批
- 发版卡：`docs/ops/发版卡-0042批次.md`；平台准备回执：`fable-0042-platform-1.20261025-1300.md`、`fable-0042-platform-2-4.20261025-1400.md`
- 构建日志：本地 `~/sunmoon-probe-runs/release-0042/`（不入 Git）

## 一、结果

| 构建 | 应用 | 结果 | 标签 | 后端钉 = 锁 | 库版本 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| #16、#17、#18 | knowbase | 倒在流水线问题 | | | | 445bbe0d/a8a7b4d0 第 2 阶段计划对后端、web、admin 不再核「锁 == 钉」；895462c8 运行时模板 `object-storage-client` 注解重了一次（kustomize 报重复键）；668b25db 存储验收探针按 `env_prefix` 取变量；#18 已部署、已批，倒在验收 |
| #19 | knowbase | 成功 | release-20261025-2 | 8ca7fc8 | 20261023_0008 | 身份 v6：audience 应用 `sunmoon-kind-knowbase-user-data` 建成；桶 `knowbase-originals` 七项存储检查过 |
| #20 | knowmart | 倒在第 2 阶段 | | | | web 钉断言，同上一条的修法 |
| #21 | knowmart | 成功 | release-20261025-3 | 928ad74 | 20261024_0008 | |
| #22 | knowbench | 成功 | release-20261025-4 | 281f4bc | 20261023_0025 | 测试电脑 Pod 跑 link 0.5.2，`relay connected`，`TMPDIR=/workspace/runs/.tmp` |
| #23 | knowlab | 部署成功、验收倒 | | 519e21d | 20261024_0012 | 迁移 0010→0011→0012 跑完、没有 `cannot backfill`；倒在 `Administrator could not read the admin console list`：`check-browser.py` 的 `ADMIN_LISTS['knowlab']` 还是 `/api/admin/v1/knowbot-drafts`，0037 把这个列表去掉了。cf267149 改成 `/knowbot-counts`，本地用真账号复跑验收通过。账 173 |
| #24 | knowlab | 倒在第 2 阶段 | | | | `PIN=keep`：#23 没走到第 12 阶段，它写的钉没进 origin/fable，keep 拿到旧钉 e328702（库版本 0010）对不上期望 0012。教训：验收倒了的发布，重发要用 `PIN=heads`（账 160 推送原子化的又一例） |
| #25 | knowlab | 成功 | release-20261025-6 | 519e21d | 20261024_0012 | 与 #23 同一组头；验收 `admin_list_read: true`；钉与回执 42d9cb7e、33a55ed5、98f07a32 已推 |

link 0.5.2：Windows 包、Linux 包都已上传并读回核过（平台回执二），knowbench 发行配置指向 0.5.2；所有者本地电脑已装 0.5.2 并进提权模式（见第三节）。

## 二、发完的核对（远程集群 sunmoon-kind）

| 项 | 结果 |
| --- | --- |
| knowlab 库 | alembic 头 `20261024_0012`；12 张 `knowbot_*` 表；迁移前备份 `~/sunmoon-probe-runs/release-0042/backup/knowlab-20261025-1622.dump`（本地，100 KB） |
| knowlab 搬旧资料 | 17:02 `python -m app.bootstrap.import_datasets`：`datasets imported batch=8 total=8`，0 错；knowbase `user_data_item` 共 9 条（8 条搬入 + 1 条已有）。跑时没有在跑的测试（passed 3、failed 4） |
| Casdoor（admin 会话只读） | 六个网页端应用 `expireInHours` 12、管理端 1；knowmart、knowbench、knowlab 网页端 `grantTypes` 含 `token-exchange`；knowbase、knowfeed、tpl 只有 `authorization_code`；audience 应用 `sunmoon-kind-knowbase-user-data` 在 |
| 身份 Job | 四家 v6 Job 全 Complete：knowbase `token_exchange_migrated: [web]`、`audience_created`；knowmart `token_exchange_migrated: [web]`；knowbench、knowlab `token_exchange: [web]` |
| knowlab 进程 | api、admin、web、worker、scheduler 各 1/1；scheduler 每 5 秒派 `durable-delivery` |
| render-check | 每次期望版本号提交到发布之间的红窗口属预期；#340、#342、#343、#351、#353 成功、差异 0 |

## 三、所有者本地电脑的 link 0.5.2

- 16:32 重启后 `elevated sandbox read grants granted:0 present:11 failed:[]`、`read denials denied:0 present:2 failed:[]`、`mode: elevated`、`relay connected`。「提高安全」弹窗报失败是误报（账 174，交 Opus）。
- icacls（只看权限）：`C:\Users\zymun\.sunmoon-link\config.json`、`C:\Users\zymun\.codex\auth.json` 对 `CodexSandboxUsers` 显式 `(DENY)(R)`；`codex-home\.sandbox-secrets` 为 Codex 自己加的 `(DENY)(M)`；`mcp.json`、`codex-home\auth.json` 不存在。所有者可在工作台里让分身 `type` 这两个文件验证应得「拒绝访问」。

## 四、流水线改动（都已推 fable）

| 提交 | 改什么 |
| --- | --- |
| 445bbe0d、a8a7b4d0 | 第 2 阶段发布前计划（`plan_before_build=true`）对后端、web、admin 跳过「镜像锁 == 钉」 |
| 895462c8 | 运行时模板 `sunmoonai.com/object-storage-client` 注解只出一次 |
| 668b25db | 存储验收探针 `common/backend/storage/verify-runtime.py`、`object-storage/verify.py --env-prefix` |
| b1407722 | `applications/deploy.yaml`、`verify.yaml` 里过时的提供方/存储断言副本 |
| 341a0147 | render-check 给发布让位：`jenkins/agent.yaml` 排队前写 `/mnt/sunmoon-data/jenkins/repos/.release-active`，结束删；render-check 见到 4 小时内的标记就 NOT_BUILT |
| cf267149 | `check-browser.py` knowlab 管理员列表路径 `/knowbot-counts` |
| ae14b701 | 账 173、174 |

## 五、教训

1. 应用改了管理端接口，平台仓的验收脚本不知道：列表路径该由应用声明（账 173）。
2. 验收倒了的发布，钉没推上去；重发用 `PIN=heads`，不用 `PIN=keep`（账 160）。
3. `make jenkins-release-run` 要在本地机用 `nohup` 起，日志放本地；经 ssh 把日志重定向到远程不存在的目录会让命令根本没跑。
4. 用 `http.client` 查 Casdoor 要收齐全部 `Set-Cookie`，只拿第一个会得到打了码的应用（`expireInHours: -1`）。

## 六、还没做的（发版卡第四节）

- 所有者走查 knowlab、knowmart（knowbench 已在走）；0037 真跑另开回执。
- 账 157–162、170 的关账核对。
- 从 Jenkins 页面点 Build with Parameters 发起的发布不会写 `.release-active`（标记由 make 目标写）：把写标记挪进 `04-release.groovy.j2` 开头（下一提交）。
- knowfeed 单独一发；之后打 `kind-flux-final` 标签，再 C4、C5。
