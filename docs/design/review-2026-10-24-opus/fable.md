# Fable 审查意见：Opus 2026-10-23—24（按 Astra、Qwen、Kimi 意见改完后的最新代码）

> 所有者 10-25：不按 request.md 审，按改完后的最新代码审，看还有什么不完善。
>
> **Fable 10-25 复核**：这份先由 Opus 5.5 代我写（当时这条会话跑的是 Opus，等于 Opus 审自己），所有者发现后让我自己复核。我逐条重读了 5 条 P1、三条决定、P2 里会改坏数据的几条，以及「核过没问题」清单里的 knowbase 验令牌、F01 读路、knowlab 本人核对、F06 现核点、165 令牌经手；四块审查助手的结论都对得上源码。复核改动：**0037 的「答过的提问套到别的用例」升为 P1（第 6 条）**；**0018 的「不许转卖」从 P3 升为 P2（第 16 条）**；P3 里「测试产出带 run_id」一条不成立，删去；P2-12 补上 Codex 源码的核对。其余定级与三条决定维持。
>
> 审的版本（本地 qwen 工位 HEAD，与 fable 钉的版本比）：knowbase 后端 `ad1e2ed..a37915f`；knowbench 后端 `44888e2..9d6ab2d`、网页 `4748b94..17252b6`；knowlab 后端 `e328702..fc28f29`、管理端 `2d5c112..4a867b8`、网页 `d758958..5336d29`；knowmart 后端 `c00eebf..bc22bd1`、网页 `50e280e..02b2927`、管理端 `107fda2..84f96ee`；tpl 后端 `497b422..736d94d`；sunmoon-link `7d1e2fc..c2cbb83`；sunmoonun `c2ce7751..8f8ca292`。
>
> 怎么审的：我分四块（0037、0042、0018、link 0.5.2 一批）请四个只读审查助手并行读源码、跑不要真库的单测；平台与发版、Opus 留给我定的三条由我自己看。下面每条 P1、P2 都对着当前代码核过，标「我核过」的是我亲手看了源码的；标「待核」的要实机或现网数据才能定。没有改任何文件、没有提交。说明一处：link 那块的审查助手在 knowbench-backend 里跑过一次 `git fetch -q`，只动了远端跟踪引用，工作区与分支没动。
>
> 先说结论：三位提的问题，Opus 改的都在，方向对；但改完还留着 **5 条 P1**（1 条是平台发版的，会像 C2b 的 #9、#11 那样在发版时撞墙），十来条 P2。建议先修 P1 与第二节的平台配置，再发。

## 一、Opus 留给我定的三条（所有者 10-24：由 Fable 定）

### F05 0037 迁移的发版与回退：停写切换，不做新旧共存

- **不做**新旧程序共存（分阶段约束、兼容投影）。理由：knowlab 在试行期，真实使用只有所有者，在跑的只有「财务分析与预测」一位；做共存要多出一整套过渡代码，换来的只是几分钟窗口。
- **发版这样做**（写进发版卡）：
  1. 发版前核 knowlab 没有在跑的测试（准专家 `testing` 为 0），也没有等用户答的提问；有就等完或先 reset。
  2. 迁移前对 knowlab 库做一次一次性备份（`pg_dump`，放本地 `~/sunmoon-probe-runs/`，root 0600，不进 git）。
  3. knowlab 的迁移 Job 与新镜像在同一次发布里，迁移与新 Pod 起来之间旧 Pod 若有写入会报错，这几分钟窗口接受（窗口里没人用）。
- **downgrade 加前置拒绝**（knowlab `20261024_0012_knowbot_lifecycle.py` 的 `downgrade()` 开头）：库里只要有迁移后的新写入就不准退，报出是哪几类、各多少行。判据都是新代码才会写、回填不会写的：
  - `knowbot_test.run_id LIKE 'knowlab-test-%'`（新代码发起的测试；回填的保留旧 run_id）；
  - `knowbot_request_version.version > 1`；
  - `knowbot_acceptance.decided_by <> 'system:trial'`；
  - `knowbot_expert` 里 `trial = false` 的行。
  
  有新写入时的回退 = 用第 2 步的备份恢复库 + 旧镜像，不是 downgrade。在 0037 的发版要配里写明这一句，并补一条真库测试：升级后写一次新测试，再 downgrade 必须被拒。

### D02 试行期补审「不通过」：当作有效的准入门

- 补审通过：只补审核记录（现状）。
- 补审不通过：**走现成的停用流程**——先停 knowmart 那一版，停成了再记停用与审核结论；停不成就照停用的失败处理，审核结论照样记下，页面写明「已判不通过，停用没成，请重试停用」。
- 理由：所有者定的是「上架前两道门」，试行期第 1 版是没过门就上架的；运营补审判了不通过，它就不该继续在架。现有代码只写 `review_approved=False`，`expert_stage` 先看 `listed_at` 仍算上架，也不停 knowmart（我核过：`domain/knowbots/lifecycle.py:193-208`、`knowbot_experts.py:147-163`）。只调换 stage 的判断顺序不够，要真停。

### D03 撤回同意是否连带撤已发的授权：保持现状，只挡新授权

- 现状（我核过）：knowbase 签测试授权时核同意没撤；读时 `Grant.active` 只看授权自己的撤销与到期。授权记着 `consent_id`。
- 定：**保持现状**。理由：① 用户界面上没有「撤回同意」按钮，撤回只发生在 knowlab 删资料的内部流程里（F03 修复：立新同意、撤旧同意）；② 正在被测试用的资料，knowbase 本来就因活动授权拒删；③ 若改成撤同意连带撤授权，「删一份资料」会直接打断正在跑的测试，并与 F03 的删除顺序打架。
- 要补的只有说明：knowbase 契约 `user-data/v1` 写明「撤回同意只挡此后的签发；已签的授权到交还或到期为止」；将来若加用户可点的「撤回同意」，再按那时的语义另定（届时连带撤授权也只需按 `consent_id` 撤，代码量很小）。

## 二、发版要配（平台）——request.md 第六节没写全的，我来做，但要 Opus 那边配合两处代码

**P1-平台 · Casdoor 打开令牌交换不是改配置，是改身份注册模板**
- 位置：sunmoonun `gitops/components/app-platform/common/backend/identity/provision.py.j2:114`（网页端 `grantTypes` 写死 `['authorization_code']`，并要求 Casdoor 里登记的字段与之完全一致，不一致就停「explicit migration required」）。
- 要做：① 模板按应用开关给网页端加 `urn:ietf:params:oauth:grant-type:token-exchange`（knowbench、knowlab、knowmart 三家，tpl 等不加）；② 注册脚本加第四种显式迁移：只差「多了 token-exchange 这一项授权类型」时更新；③ **三家的 `identity_revision` 升 v5→v6**（C-R11；C2b 的 #11 就是改了脚本没升版本，Flux 一直看旧的失败 Job）；④ 新建 knowbase 的「目标应用」（只作 audience，客户端编号 = `KNOWBASE_USER_AUDIENCE`），要一个新的注册件（照 `service-identity` 的写法，不给登录）。这几样我在 sunmoonun 里写，发版前先在临时 Casdoor 上走一遍「已有应用 → 迁移 → 交换成功」。

**P2-平台 · 网页端令牌 1 小时，会话 12 小时**
- 位置：同上 `provision.py.j2`，网页端 `expireInHours: 1`、`refreshExpireInHours: 0`；tpl 的 `auth_service` 存的就是这张令牌，过期后凡用 knowbase 的操作回 `reauth_required`（三家网页有提示）。
- 后果：用户每过一小时碰一次知识库就要重新登录一次。
- **所有者 10-25 定：网页端令牌改 12 小时**，与会话对齐（只影响令牌寿命，改法同上一条，随 v6 一起迁）；不引入刷新令牌。

**P2-平台 · 新的跨应用链路，网络放行与服务身份一条都还没有**
- 现有配置（fable）：knowbench 只有到 knowmart、knowlab 的 `service_clients`；knowlab 只有到 knowmart、knowbench；knowbase 没有接收方配置。
- 要新加：knowbench（api、worker、runner）→ knowbase `user-data-read`；knowlab（api、worker）→ knowbase `user-data-grant-test`、`user-data-import`、用户资料读写；knowmart（api、worker）→ knowbase `user-data-purchase` 与用户资料；各自的出站放行与 knowbase 的入站放行；knowmart 的 `CROSS_APP_TARGETS_JSON` 加 knowlab。发版卡逐条列、逐条验。

**P2-平台 · 发版当天的顺序要再细一步**（与下面 0042 的第 4 条相关）：knowlab 的 `import_datasets` 必须在「没有在跑的测试」时跑；跑完后测试同意要补齐（见三·0042-4），否则运营发起的测试一律 `test_consent_missing`。

## 三、代码问题（按轻重）

### P1

1. **0042 · 测试运行授权被 knowbase 截成 26 小时，等人一天以上的测试中途读不到数据**（我核过）
   - knowbase `app/app/domain/user_data.py:47` `"test": timedelta(hours=26)`；`grant_expiry` 静默取小（`:251-257`）。knowlab `knowbot_service.py:87-90` 按「超时 + 等人 3 天 + 1 小时」申请（最长约 4 天），注释写「knowbase 最长给 7 天」；不回读 `expires_at`。
   - 改：knowbase 测试上限 ≥ knowlab 可能申请的最大值（7 天，与 schema 一致）；knowlab 比对回包 `expires_at`，短于申请就当签发失败。Q-06 的修复漏了测试这一种。

2. **0018 · 卖家删了在架条目里的资料，买家拿到半份，这笔成交永远卡在「复制中」，也再买不了**（我核过）
   - knowmart `interfaces/endpoints/library_routes.py:111-118` 删除不核是否在待审、在架的条目里；`application/services/market.py:562` 起的 `_copy` 遇到复制失败不收尾；`infrastructure/repositories/market.py:567-583` `copying_trade` 总捞回这笔。
   - 改：删资料前核条目引用，在就拒（或先下架那条）；`_copy` 遇到资料没了把成交记成终态失败、告诉买家，`copying_trade` 不再捞终态。

3. **link 账 129 · 一次测试留下只读目录，以后所有测试都开不了跑**
   - sunmoon-link `agent/src/service.ts:230` `fs.rmSync(target, {recursive, force})`：测试电脑以非 root 运行，`runs/<id>/` 里有 0555 的目录（模块缓存、`chmod -R a-w`）就 EACCES；knowbench `application/workbench/test_folders.py:76-86` 删旧目录被拒就抛 `FolderRefused`，新测试跟着失败；run.sh 的每小时兜底也删不掉。审查助手在本地 node 24 上实测复现。
   - 改：link 删除前逐级 lstat、不跟链接，把目录补 `u+rwx` 再删；knowbench 删不掉旧目录时挪到 `runs/.trash-*` 并记日志，不挡新测试。

4. **link 账 165 · 远程新建项目时「记住」照样显示，令牌会存进装 link 那台电脑的 git 凭据，与同一对话框「只用这一次、不落盘」相反**（我核过）
   - 网页 `features/projects/ui/new-project-dialog.tsx:121`、`:353-361`（勾选框不分本机、远程）；后端 `workbench_routes.py` 远程 clone 原样转发 `remember`；link `localProjects.ts:137` `git credential approve`。文字 `auth.remoteLead`（zh-CN `:883`）。
   - 改：远程模式不显示勾选框；后端远程 clone 去掉 `remember`；link 收到经会合点来的 clone 一律不 remember。

5. **平台 · 令牌交换的身份注册**：见第二节第一条。

6. **0037 · 答过的开步前提问按用例编号存，改创意后会套到别的用例上，用户没确认过的判断被当成确认过**（复核后由 P2 升 P1；我核过）
   - 网页 `components/knowbots/request-form.tsx:48-50` 每次提交按位置重编 `c1..cn`；后端 `knowbot_service.py:107-118` `cases_for_test` 按编号把 `case_answers` 并进用例，用例自己没写的就用旧答案。
   - 场景：v1 的 c1 问 A、c2 问 B，测试中用户给 c1 答了「period=2023」；改 v2 删掉 A，B 变成 c1；测 v2 时 A 的答案悄悄填进 B，这一问不再问用户。编号不变、只改了问题文字时也一样沿用旧答案。
   - 为什么是 P1：这直接碰 C-L1（用户的判断由用户做）——产品承诺是「开步前问人」，这里把没问过的当成问过的，而且用户看不出来。改：改版时保留原 case_id、只给新加的用例发新号；答案的键加上问题文本摘要，或按版本存。

### P2

**0037**
1. **运营审成「公开」，第一次交付必定留自用，而且不报错**（我核过）：knowmart `infrastructure/repositories/knowbots.py:119-140` 第一次收到某专家时建的记录不带类目（默认 `uncategorized`）；`application/services/market.py:318-339` `ask_public_on_delivery` 里 `check_category` 抛错被吞，回 `self`；knowlab 照记 `review_listing='public'`。真库测试 `tests/test_market_db.py:320` 先用 SQL 改了类目所以没发现。改：交付带类目（清单或交付体），没类目回明确的 `listing_status`（如 `category_needed`），knowlab 管理端照实显示。
2. **「自用 / 公开」knowlab 按版本审，knowmart 按整位专家生效**：knowlab `knowbot_experts.py:183` 只在公开时送 `request_public=True`；knowmart `knowbot_service.py:195-210` `_summonable` 只看专家整体 `visibility`。第 1 版公开、第 2 版审成自用，第 2 版照样被别人请。改：knowmart 按版本记可见范围，或 knowlab 自用版显式送 `request_public=false` 由 knowmart 降级；设计写明以哪边为准。
3. （复核后升为 P1，见 P1 第 6 条。）

**0042**
4. **跑完 `import_datasets` 后，用户打开知识库页之前，他的测试一律开不了跑**：knowlab `knowbot_service.py:543-559`（有一份搬进 knowbase 就要求测试同意）；`knowbot_data_read.py:351` 旧路拒读已搬的；`bootstrap/import_datasets.py:6` 的说明「补上之前测试照旧经 knowlab 读」与代码不符。测试是运营发起的，所有者不在场。改：import 流程里顺带补齐测试同意（导入身份能做的话），或「同意补上之前，没进同意的那几份仍走旧路」；至少改对说明与发版卡。
5. **测试同意并发刷新会留下一条 knowlab 不知道的旧同意，里面的资料从此删不掉**（我核过）：knowlab `application/services/knowbot_data.py:352-368`，`current` 在锁外读，先在 knowbase 建新同意再进事务覆盖写；两次并发（上传 + 打开页面、两个标签页）各建一条，被盖掉的那条不进待撤，knowbase 也没有按 ref 列同意的接口，没法对账。F03 修得不完整。改：在 `lock_owner_data` 下「先记将要建的、再建」，建好后锁内重读当前那条，凡被覆盖的一律进待撤；或 knowbase 给「按 ref 换同意」的原子操作 / 按 ref 列同意供对账。
6. **补登记（F04）与搬旧数据竞争，产生重复记录并让 import 永远失败**：knowlab `knowbot_data.py:192-225` `adopt`、`:242-262` `import_old` 不加 owner 锁；迁移 0011 对 `knowbase_item_id` 唯一。import 已在 knowbase 建好、本地还没写时用户打开页面，`adopt` 按 uuid5 登记成新资料；再跑 import 撞唯一索引退出，原数据编号永远 `data_not_imported`。改：`adopt` 跳过 `origin_ref` 以 `knowlab-dataset:` 开头的；`import_old` 加锁并处理已被补登记。

**0018**
7. **换键接手的那一笔，新键没登记，用新键重试会整份再买一遍**（我核过）：knowmart `market.py:507-511`，`trade_by_request(K2)` 查不到（记的是 K1），`copying_trade` 也查不到（已 done），于是新起一笔。改：接手时登记 K2 为这笔的别名，或回原成交编号。
8. **审过的主体、证照没法撤销**：`market.py:1035-1075` `decide_publisher`、`decide_license` 只收 pending；发现证照伪造只能逐条下架，卖家再申请公开照样过。改：加撤销（approved → revoked），走同一套现核立即生效，sweep 收回相关条目。
9. **需求选中后结不了单**：`market.py:710-718` `close_demand` 只收 open；`:829-855` 要求成交的正是选中响应附的那一条。卖家「做好上架再告诉买家」、专家类需求（`record_summon` 不带需求）都走不通，需求永远「已选定」。改：允许关闭 chosen；选中的卖家可补附条目；专家成交可带 `demand_id`。
10. **被平台下架的专家，卖家点「只自用」就把下架冲掉了**：`market.py:292-297` private 分支不看 `taken_down`；管理端专家审核栏不显示 `review_note`。改：private 保留 taken_down，或另记下架。

**0018（复核补）**
16. **「不许转卖」没有真正跟着走**（复核后由 P3 升 P2；我核过）：knowmart `infrastructure/repositories/market.py:626-655` `bought_without_resale` 读的是条目**现在**的 `resale_allowed`，不是成交那一刻的——卖家下架、改勾、再上架，已买家能不能转卖就跟着翻；复制到 knowbase（`infrastructure/external/knowbase_user_data.py:181-203`）不带任何标记，knowbench、knowlab 里那份看不出不许转卖，拦截只靠内容摘要比对，改一个字节就过。所有者 10-23 定的六项里有这一条，request 第三节第 4 条写的「标记跟着走」与实现不符。改：成交上存当时的 `resale_allowed`；契约 `user-data/v1` 的复制加 `no_resale`，knowbase 资料带标记，上架时按标记拦，不只按摘要。

**link 0.5.2**
11. **远程看文件、新建项目不核对是哪台机器**：knowbench `workbench_routes.py:358-364` `_relay_user_of` 只核机器归属，然后找此刻连着的那份 link。有 A、B 两条记录时，选 B 的操作会落到 A 上。改：核这条记录的 `device_id` 等于会合点在线 agent 报的；老 agent 无编号时退回按名字比；不一致回 409。
12. **账 168 · 提权模式下沙箱命令仍读得到控制目录里的令牌（待核，要 Windows 实机）**：Codex `setup.rs` 在全盘可读档给用户目录第一层逐项授读，`.sunmoon-link`（`config.json` 是会合点令牌）与 `.codex`（`auth.json`）都在第一层、不在它的排除名单里；`windowsSandboxRead.ts` 的排除只管 PATH 补授这一路。不是这批引入的，但账 168 与请求里写的「排除控制目录」会让人以为护住了。改：权限档对 `config.json`、`mcp.json`、`%USERPROFILE%\.codex` 加禁读（Codex 有 `deny_read_paths`）或令牌改存 DPAPI；实机用沙箱账户 `type` 验。
    - 复核（Fable，远程机本地 Codex 源码 `~/repo/codex`，主干 2026-08-28）：`codex-rs/windows-sandbox-rs/src/setup.rs:55-68` 的 `USERPROFILE_ROOT_EXCLUSIONS` 确是写死的 12 个名字（`.ssh`、`.tsh`、`.brev`、`.gnupg`、`.aws`、`.azure`、`.kube`、`.docker`、`.config`、`.npm`、`.pki`、`.terraform.d`），**没有 `.sunmoon-link`、`.codex`**；`deny_read_paths` 在 `elevated_impl.rs:24` 起确实存在。部署的 0.155.1 是否同样，待核。
13. **每用户只有 2 条服务流，一次远程拉仓库占一条最多 16 分钟**：relay `relay.py:48` 默认 2（部署没改）；knowbench `CLONE_TIMEOUT_SECONDS=16*60`。拉仓库时展开目录、看文件、`fs/digest` 一起来就 `too many service streams`；网页「取消」后后端仍占着流。改：调高上限（平台配置，我来），或拉仓库改受理号 + 轮询；浏览器断开时后端关流。
14. **账 129 隔离漏了 /tmp**：`projects.py:322-330` 测试轮次没设 `excludeSlashTmp`/`excludeTmpdirEnvVar`；测试电脑 `/tmp` 是整个 Pod 共用的 emptyDir（1Gi）、`TMPDIR=/tmp`，上一次测试写的下一次读得到，写满还会驱逐 Pod。改：测试轮次设两项为 true，`TMPDIR` 指到 `runs/<id>/.tmp`。
15. **账 143 设备编号一换，项目挂在永远离线的老记录上**：link `cli.ts:81,92` `init` 用 `defaultConfig()` 重写会生成新编号；后端 `repository.py:192` 只认领没编号的记录。改：`init` 保留原 `deviceId`；后端遇新编号且有同名、同 `first_host`、已离线的记录时认领或提示合并。

### P3（不挡发版，记账）

- 0037：并发交付后到的一次回 409，knowlab 失败分支可能把 `delivery_error` 写到已上架的专家上（knowmart 锁后再查一次交付单号；knowlab 只在阶段仍是 `to_deliver` 时写错误）——Opus 对 Kimi 4 的「靠交付单号幂等兜住」不完全成立。0012 回填把「用户要了、当年交付失败」的行换了交付单号（旧 `knowlab-draft-…` → 新 `knowlab-expert-…`），若旧交付其实落了地会一直 409（待核现网有无此行；前置检查列出这类行，或交付时「同版本同摘要已存在」当成功）。0012 前置检查漏了 `(report->>'finished_at')::timestamptz` 转换失败（待核运行方是否总给 ISO 时间）。用户不要 / 审核不过之后「待孵化」看不到这个名称（`knowbot_board.py:65-82`）。修订号按整个名称递增，与第十六节例子「2.1」不符（改代码或改文档）。web端 `/avatars?draft=` 一律跳 `/applications`、`/experts` 不认 `?draft=`。两个开步前提问同时作答可能丢一个（`_remember` 没锁名称）。knowmart `contracts/README.md` 没写只认 `knowlab-` 引用；迁移 0008 的说明还写「整份替换」。（原稿这里还有一条「给用户的测试产出带 run_id」，复核不成立：`knowbot_views.py:249-250` 的 `run_id` 只在 `admin` 时给，删去。）
- 0042：会话改选并发留孤儿授权（`session_data.py:100-142`）；共享抽取任务出错时把 A 的 `grant_inactive` 传给 B（`text_extract.py:186-201`，误拒不越权）；老 link 每读一次整份读回（`pinned_data.py:299-309`，50 MB 约 100 个往返，易超 45 秒工具时限）；knowbase `import_item`、`purchase` 撞唯一索引回 500 并留孤儿对象（`user_data_service.py:129-136`）；测试进行中跑 import 会中途读不到（写进发版卡）；补登记不受 1000 份上限约束（`adopt`）；同一用户的模型能读另一段对话选的资料（`workbench_mcp.py` `_library_call` 只核对话归属，待所有者定要不要绑会话）。
- 0018：评价不核成交状态、可无限刷，`expert_market` 对私有专家也回价格与评价；身份证号查重可绕过（只存前 3 后 4、不校验 GB 11643 校验码、`id_number_hash` 无唯一索引）；照片清理漏三种（从未进审、审后补传、没挂到证照上的），上传张数无上限；「到期前 30 天提醒」只写 `reminded_at`、没人被提醒；日期按 UTC 取，北京 0–8 点过期的证照仍算有效、截止日过了的需求还能建（统一按 `Asia/Shanghai`）；`PUBLIC_MARKET_ENABLED` 关着时仍显示「已公开」；专家公开审核看不到清单能力、主体与资质，禁词只扫名称与一句话，knowlab 判了自用的卖家仍可在 knowmart 申请公开（待议，属 0037 契约）；卖家「我卖出的」看得到买家的资料编号；关闭、已选定的需求任何人按编号可读可留言；`KnowbaseUserData()` 每请求新建、服务令牌缓存不住。
- link：`first_host` 只写一次，改电脑名后「像是拷来的」提示消不掉；账 148 `splitArtifact` 只要有一行以 ``` 开头就整段折叠，账 147 删除全是 `- ` 列表的文件时列表符号被当成补丁标记；`runsWritable` 判 `!== "win32"`（macOS 也开），knowbench 开 `KNOWBOT_TEST_ISOLATE` 前不核 agent 报没报 `service-runs-v1`；`--concurrent-requests 8` 下同一进程的 `process/write` 理论上可能乱序（待核 app-server 是否串行发）；`prepareElevatedReads` 启动时同步跑 icacls、大目录会卡启动，用户目录被 junction 挪盘时全部拒授、`start` 直接退出而不退回普通模式（待核，实机）。

## 四、核过、没问题的（免得重复看）

- 令牌交换模板：knowbench、knowlab、knowmart 三份与 tpl 完全一致；用户令牌只用于 knowbase、不进日志；knowbase 按 aud、azp 认分区，授权按单份资料编号限定。
- F01：所有读内容的路径要么真取字节、要么先调 `check`；委托 7 天、会话 24 小时两边一致；`data_grant` 生产方与消费方字段一致；knowbench 迁移 0022–0025 成线、与 fable 不冲突。
- 0037：测试「先锁名称再锁准专家」+ 部分唯一索引；x 已出专家拒测；平台出错的几条都退回待测；两道门顺序与行锁；停用先停 knowmart；受理加锁；web 接口都核本人；两端回包校验已不 `.strict()`（账 144）。
- 0018：web 端归属都核了；证件照只经管理端、`no-store`；422 与未捕获异常不回显请求体、数据库 `hide_parameters=True`；F06 的五处现核都在；F07 的同键幂等与逐份记账对。
- link：新 knowbench/relay 对老 0.5.1、新 0.5.2 对现网 relay/knowbench 都不会坏；165 的令牌经环境变量交给 git、不进 argv，会合点不记帧，日志只记方法名（除上面 P1 第 4 条）。

## 五、建议的顺序

1. 修第三节 P1 的 1–4，与 P2 的 3、5、6、7（数据会错或卡死的）；
2. 我做第二节的平台改动（令牌交换的注册件与迁移、knowbase 目标应用、网络与服务身份、服务流上限、网页端令牌 12 小时），先在临时 Casdoor 上走通。**所有者 10-25 定：等 Opus 修完代码再一起做**；
3. 发版卡按 F05 的停写切换写，含 import 的时机与同意补齐；
4. P2 其余与 P3 记账，发版后按账做；168 的控制目录禁读与 129 的只读目录要在 Windows 与测试电脑实机各验一次。
