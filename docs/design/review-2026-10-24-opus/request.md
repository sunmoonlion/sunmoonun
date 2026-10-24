# 请 Fable、Astra、Qwen、Kimi 评审：Opus 2026-10-23 至 10-24 的工作

> 所有者 2026-10-24：「现在你帮你这两天来的工作进行详细说明并写成文档，我让astra和fable对你的工作进行审核」，随后补「再加一个qwen」「再加：kimi」。
>
> 这份是给评审看的总结与索引，不是任务卡。请读源码与设计；回执只在要查细节时看。
>
> **意见交到哪**（所有者 10-24：「建立一个文件夹让各助手把它们的审查都提交在该文件夹，不提交到各工位了」）：都写进这份请求所在的文件夹，一人一个文件——`fable.md`、`astra.md`、`qwen.md`、`kimi.md`。
>
> - 本地路径：`/home/zymun/worktrees/qwen/sunmoonun/docs/design/review-2026-10-24-opus/`；在远程机上走挂载：`~/wsl-worktrees/qwen/sunmoonun/docs/design/review-2026-10-24-opus/`。
> - 只往这个文件夹里加自己那一个文件；**不要 git 提交**，也不要改 qwen 工位的别的文件。你们写完，由 Opus 统一提交。
> - 不再写进各自的工位。
> - 格式：按轻重排，每条写清在哪（仓、文件、函数或行）、为什么、建议怎么改；拿不准的标「待议」。采不采纳由 Opus 定，拿不准的问所有者。
>
> **状态**：全部在本地 qwen 工位（`/home/zymun/worktrees/qwen/...`）**只提交、没推、没发版**（所有者 10-23：「先提交，不推，不发版，等fable回来让它处理」）。每段做完都和 fable 试合并过（`git merge-tree`，都没有冲突），子仓的新提交都接在父仓 fable 分支钉的那一版后面（快进）。平台文件（gitops、`infrastructure/`、Jenkins、发版卡）一个都没动，要配的都写在第六节。
>
> **最要紧的是第一部分（0037）与第二部分（0042）**：改了数据结构、跨应用契约与授权，上线后难回头。第三部分（0018 供需市场）量大但自成一块。第四部分是 10-23 上午的本地 link 0.5.2 一批与账。

## 零、读哪些提交

各子仓的 diff 范围都是「父仓 fable 分支钉的那一版..qwen 头」。在本地工位里看：`cd /home/zymun/worktrees/qwen/<父仓>/<子仓> && git diff <起>..<止>`。

| 仓 | 范围 | 提交数 | 量 | 主要内容 |
| --- | --- | --- | --- | --- |
| knowbase-backend | `ad1e2ed..f7eaa39` | 5 | +3431 −3 | 用户资料（0042 块 1、3、5） |
| knowbench-backend | `44888e2..cc81702` | 10 | +6867 −900 | 账 129、141、143、165；0042 块 1、2、5、3 |
| knowbench-web-frontend | `4748b94..17252b6` | 10 | +3048 −7898 | 账 83 作废、143、165、168；0042；账 147、148（大量删减是旧「资料库」页与它的预览样例） |
| knowlab-backend | `e328702..23af09f` | 7 | +7360 −2053 | 账 141；角色；0042 块 3、4；0037 重做 |
| knowlab-admin-frontend | `2d5c112..4a867b8` | 3 | +3834 −3248 | 账 141；角色；0037 四栏 |
| knowlab-web-frontend | `d758958..8e95e56` | 2 | +2890 −2589 | 0042「知识库」；0037 三栏 |
| knowmart-backend | `c00eebf..7745167` | 8 | +6334 −39 | 0042 块 1、4、6；0018 供需市场；0037 契约 |
| knowmart-web-frontend | `50e280e..b8ae4e0` | 4 | +4120 −36 | 0042、0018 八栏、0037 空号与停用 |
| knowmart-admin-frontend | `107fda2..627e3e1` | 1 | +923 −3 | 0018 五栏 |
| tpl-backend | `497b422..736d94d` | 1 | +286 −10 | 令牌交换（模板，三个应用照抄） |
| sunmoon-link | `7d1e2fc..855655b` | 9 | — | 0.5.2（账 128、129、143、165、168）、0042 本地知识库 |
| 父仓 | knowbase-app `a5051fa..232fd21`、knowbench-app `c38dca6..6a60c84`、knowlab-app `43cd00f..3dd4da3`、knowmart-app `a7f6847..e37c884`、tpl-app `2100a56..c96dd25` | | | 指针、契约（`contracts/`） |
| sunmoonun（k8s） | `c2ce7751..e27dd0bc` | 42 | | 设计、决定、回执、会合点一处代码（`3644498b`） |

设计与决定的入口：
- [SDD 0037](../SDD/modules/0037-idea-avatar-expert.md)：第十八之二节「落地做法」与第 4 小节「实施进度」。
- [SDD 0042](../SDD/modules/0042-knowledge-bases.md)：第十一节「实施进度」与「发版时要配」。
- [SDD 0018](../SDD/modules/0018-advisor-market.md)：第十一节（供需市场）与第 10 小节「实施」。
- [decisions.md](../decisions.md)：10-23 各条（三个应用相互独立、四类知识库、供需市场六项、角色、终端不做等）。
- [待办账](../pending-after-migration.md)：129、141、142、143、144、147、148、165、168。
- 回执：`process/switch-test/done/2026-10-23-opus-052-1` 至 `-5`。

测试的运行方式：各后端 `uv run --frozen pytest -q -p no:randomly`，真库测试要 `DELIVERY_TEST_DATABASE_URL`（或 `AGENT_TEST_DATABASE_URL`）指向一个一次性的 `*_tests` 库；前端 `pnpm typecheck && pnpm lint && pnpm check:i18n && pnpm vitest run && pnpm build`。

---

## 一、0037：knowlab 的数据结构与两端重做（10-24）

所有者 10-20、10-23 定的方案（0037 页首原话）：过程和结果分开（左边栏是过程，右边栏只放这个过程的输出）；没有退回；创意、准专家、专家用版本号，测试用编号，都只增；一个名称一生；上架前两道门，先用户同意、后运营审核；「分身」改叫「准专家」；补充方法（0035）取消。

### 1. 数据（knowlab 后端 `21a883f`，迁移 `20261024_0012`）

| 表 | 是什么 | 关键约束 |
| --- | --- | --- |
| `knowbot_request`（改） | 创意的名称；加 `latest_version`、`case_answers` | `idea`、`cases`、`consent_version` 是最新版本的镜像，给旧读路径用 |
| `knowbot_request_version`（新） | 创意的一个版本 | 主键（创意，版本号）；只插不改 |
| `knowbot_acceptance`（新） | 受理单：三样（C-L5、C-L2、C-L1）各自的结论与说明、受理与否、理由 | 一个版本一张；不受理必须有理由（CHECK） |
| `knowbot_draft`（改） | 准专家；加 `request_version`（外键到版本表）、`user_review` | 状态只剩 pending_test / testing / passed / failed |
| `knowbot_test`（新） | 一次测试：编号、准专家、状态、预算、超时、run_id、运行授权、开始结束、报告、错误 | （创意，编号）唯一；run_id 唯一；**同一个创意同时只有一个在跑**（部分唯一索引 `status IN (queued, running, waiting)`） |
| `knowbot_expert`（新） | 一版专家：出自哪次测试、交回、用户同意门、运营审核门、上架、交付错误、停用、试行期标记 | （创意，版本号）唯一；一个准专家最多一版；通过要有自用 / 公开，不通过要有理由，停用要有人和理由（CHECK） |

**只扩不缩**（`rules/constraints.md`「做数据迁移时」）：准专家上的 `run_id`、`run_attempts`、`run_started_at`、`run_timeout_seconds`、`report`、`delivery`、`last_error`、`run_grant_id` 留着、不再写；状态约束里的 `delivered` 也留着。等新流程跑稳，再出一次收缩迁移删掉。

**回填**（0037 第十节）：每个创意回填 v1 与一张「试行期自动受理」（受理人 `system:trial`）；准专家 `request_version` = 1；每个测过的准专家回填一次测试（编号按开跑时间排；测试中的按报告分排队 / 进行中 / 等用户答，通过与已交付的是通过，没通过的是没通过，退回待测的是平台出错、原因取 `last_error`）；通过与已交付的回填专家（版本号用准专家的；已交付的标试行期，上架信息与 knowmart 编号、摘要照搬）。之后准专家的「已交付」改「通过」。

`downgrade` 会把上架了的准专家改回「已交付」，并把回执并回 `delivery`（旧读路径按它找）。

### 2. 流程（`application/services/knowbot_service.py`、`knowbot_experts.py`）

- 申请出 v1；改创意出新版本，只插不改；名称、运行方一生不变。
- 受理：给某一版写受理单，一张写了不改；三样都过才能受理，不受理要写理由。
- 孵化（照旧是手工贴清单）：只能选受理了的版本，不选就用最新受理的那一版；规则出处不许再引补充方法；版本号 x = 已有专家的最大版本号 + 1，修订号 y 在这个创意里递增。
- 请用户审核准专家（可选）：等用户答的不能测；用户说「不行」（必须写意见）的不再测，要再孵化。
- 测试：发起就是一个新编号，run_id 改成 `knowlab-test-<测试编号>`（每次都不同，不会撞上运行方按 run_id 的幂等）。运行方报错、超时、开跑失败、运营判定卡住，都记「平台出错」结束这一次，准专家回到待测，再测是新编号。x 已出过专家的准专家不许再测。通过就建专家，版本号就是 x。
- 测试中用户答过的「开步前提问」不再改创意的用例，另记在 `case_answers`，开跑时并进用例（用例里自己写了的不覆盖）。
- 专家：交回（通知用户）→ 用户要 / 不要 → 运营审核（通过定自用或公开，不通过写理由）→ 交 knowmart（交付单号 `knowlab-expert-<编号>`，幂等）。交付失败记在 `delivery_error`，审核结论照样留着，可以重试。试行期上架、没审过的可以补一次审核记录，不再交付。停用：上架了的才能停，先停 knowmart 那一版，停成了才记。
- 运行方读数据（knowbot-data/v1）：专家用途按「上架了、没停用」的那版核摘要；测试用途按「在跑的那次测试」核。
- 两端的栏、大类、「等我们 / 要你做的」数，与详情页的记录都在后端算（`knowbot_board.py`），前端只画。

### 3. 接口（`interfaces/endpoints/knowbot_routes.py`、`knowbot_views.py`）

- web端：`POST /knowbot-requests`（申请）、`POST /knowbot-requests/{id}/versions`（改创意）、`GET /knowbot-requests/{id}`（详情页）、`GET /knowbot-counts`、`GET /knowbot-board/{applications|inbox|experts}`、`POST /knowbot-drafts/{id}/review`、`GET /knowbot-tests/{id}/outputs`、`POST /knowbot-experts/{id}/decision`、`POST /knowbot-experts/{id}/stop`；知识库、问题照旧。
- 管理端：`GET /knowbot-counts`、`GET /knowbot-board/{acceptance|incubation|tests|delivery}`、`GET /knowbot-requests/{id}`、受理单、建准专家（带 `request_version`）、请用户审核、核出处、清单原文、发起测试、`/knowbot-tests/{id}/refresh|reset|outputs`、`/knowbot-experts/{id}/return|review|deliver|stop`；问题照旧。
- **撤掉的**：web 的创意列表、`/knowbots`、`/knowbot-drafts/{id}`、`/accept`、写补充；管理端的创意列表、草稿列表、不照做补充。只有 knowlab 自己两个前端用，已一起改。
- 给用户的视图不带规则名（三样只给受理与否和理由）、run_id、清单原文、谁做的。

### 4. 两个前端

- **管理端**（`4a867b8`）：左边栏「受理 · 孵化 · 测试 · 交付」，每栏是「左边大类与列表 / 中间过程页（输入完整显示）/ 右边栏只放输出」。交付栏有「全部专家」。新增名称详情页 `/names/{id}`。旧地址跳转：`/ideas?request=` 到详情页，`/avatars?draft=` 到孵化里那一位，`/experts` 到全部专家，`/knowbots` 到受理。顺带账 142（成稿写「第几步「步名」写的」）。
- **web端**（`8e95e56`）：左边栏「申请 · 审核 · 专家」。审核是待办箱：转给我的问题、请我审核的准专家、交回等我定的专家。首页顶上一条「你的创意『…』测试通过了，去确认」。修改创意从上一版带过来改（预先给的答案照带）。名称详情页的记录用用户的说法。旧地址跳转。
- 两端的回包校验改成「多了字段不算错」（账 144：线上前端严格校验，后端多一个字段整页读不出）。

### 5. 跨应用

- knowmart 后端 `1771683`：交付可带 `request_public`。卖家的发布主体与类目资质都过的，这一版进 knowmart 的上架审核；不过的留自用、不报错；回包多 `listing_status`。新加内部接口「knowlab 停用某一版」（服务关系同交付）。
- knowmart 后端 `7745167`、web端 `b8ae4e0`、knowlab 后端 `23af09f`：
  - **空号**（0037 第三节「详情页写明空号那一版的结局」）：knowlab 在用户不要、审核不过、交付成功这三个时点，把没上架那几版的结局整份交过去（`PUT /internal/v1/knowmart/owners/{owner}/sources/{ref}/unlisted`，knowmart 迁移 `20261024_0008`）。knowmart 详情的版本记录写「没有上架：你没要这一版 / 运营审核没通过」，结局只给主人看。交不到只记一行日志，下一次再交整份。
  - **停用**：knowlab 交来的专家（引用以 `knowlab-` 开头）在 knowmart 直接停用回 409 `stop_in_knowlab`，页面带去 knowlab 停，免得两边对不上。

### 6. knowbench 账 147、148（`17252b6`）

- 147：Codex 报新建、删除的文件时给的是整份内容、不是补丁，Markdown 的「- 」列表行被当成删掉的行，新建的成稿显示「+0 −38」。改成按整份内容数行，前面补上 + 或 −；已经一行一个 + 的照原样用（兼容预览样例）。
- 148：专家拿着方向盘时，每步交回的原文（整段 JSON，或先说一句再贴 JSON）折成一行，写前面那句说明，点开才看。原来纯 JSON 的直接不摆，先说一句再贴的整段摊开。

### 7. 请重点看（0037）

1. **回填与只扩不缩**：回填 SQL 依赖一个旧规矩——旧的 `add_draft` 在有待测 / 测试中 / 通过的稿时不许建新稿，所以每个创意最多一个在测、通过的稿不会撞版本号。这一点在现网数据上成立吗？`downgrade` 的语义（只恢复上架了的）够不够？收缩迁移什么时候出合适？
2. **「通过还没交付」的旧稿回填成「已交回」**：理由是旧 web端一通过就给用户看并能点「要这一版」。如果你们认为应当回填成「待交回」，让运营再走一遍交回，请指出。
3. **我自己拿的主意**（设计没写死的地方）：
   - 请用户审核是可选的：请了就等答完才能测；说不行就死这一稿。
   - 「待孵化」的定义：最新受理了的版本还没有能往下走的准专家（待测且用户没说不行、版本号没被占，或在测，或已通过）。
   - 各栏「等我们」怎么数：受理数待受理的；孵化数待孵化的；测试数待发起、且版本号没被占的；交付数待交回、待运营审核、审过待交付的。
   - 审核通过但交付失败时，审核接口不报错，回包带 `delivery_error`，由管理端重试。
   - knowbot_test_output 仍按（准专家，run_id）挂，没加到测试表的外键；测试与产出靠 run_id 对上。
4. **跨应用的一致性**：停用先停 knowmart、再记 knowlab（knowmart 停成、knowlab 没记成时，重试是安全的）。空号结局是「尽力送达、下次整份重送」，中间会有一段时间不准；knowmart 只知道「不要 / 审核不过」，还没定的空号只写「没有上架」。这样可以吗，还是要加重试队列？
5. **改了用户看到的同意文字**：web端申请表里那句测试数据同意说明，「分身」改「准专家」，「交付」改「上架」（意思不变），后端同意版本号没升（仍是 2），所以已经同意过的用户不会被要求重新同意。若认为改说明文字就该升版本，请指出。
6. **试行期的第 1 版**（`084acc72…`，「财务分析与预测」）：回填后是「已上架、试行期、两道门之前交付」；knowmart 里不能再直接停，要到 knowlab 停（knowlab 发版前，knowmart 那边就停不了它）。
7. **性能**：栏目接口每次把全部创意的版本、受理单、准专家、测试、专家都取出来在内存里分（试行期量很小）；`answered_by_user` 是逐个查。量大了要下推到 SQL。
8. **权限**：受理、孵化、请用户审核、核出处、判定卡住、交回、运营审核、重试交付、停用都要 `knowlab:release`；发起测试、刷新只要管理端基本权限。10-23 所有者定 operator 也有 `knowlab:release`。

### 8. 测过什么、没测什么（0037）

- knowlab 后端全量 597 过、9 跳过（真 PostgreSQL）。新测试：`test_knowbot_creation_service.py`（流程 13 条，重写）、`test_knowbot_experts.py`（两道门、交付重试、停用、试行期、空号送达）、`test_knowbot_board.py`（四栏、三栏、记录）、`test_knowbot_creation_routes.py`（接口重写）、`test_knowbot_repository_db.py`（真库约束、并发发起只留一个、数据在用的新判断、**0012 回填在一份 0011 时的旧数据上逐项核，再退回、再升级**）。
- 管理端 59 过、web端 107 过；两端类型检查、lint、文案、构建都过。knowmart 后端 492 过；knowmart web端 105 过、构建过。knowbench 网页 336 过。
- **没做的**：浏览器里看真页面；部署；0037 第十六节的「真跑」（拿「财务分析与预测」走一遍新流程，和块 7 重孵化第 2 版一起做）；上线后给试行期第 1 版补一次运营审核记录；收缩迁移。

---

## 二、0042：四类知识库、请专家用自己的数据（10-23 晚）

所有者 10-23（决定记录 10-23 晚「四类知识库……」一条）：三个应用相互独立、各有知识库；专家只是逻辑、不绑数据；请专家的人用自己的数据；knowlab 知识库搬进 knowbase；法律评估不挡路，按资质。做法见 0042，进度表在第十一节，下面按块说。

### 1. 块 1：knowbase 用户资料与本人凭据

- knowbase 后端 `0465409`、`54a0bd0`（父 `1947261`、`915863a`），契约 `user-data/v1`。按「用户 × 应用」分区存；上传、下载、删；同意依据；运行授权（测试、委托、孵化、会话四种）；凭授权读内容或格式；买卖时复制；读数留痕。验令牌的 `aud`、`azp`。服务权限照跨应用约定写成「目标:关系」。
- 令牌交换：tpl 后端 `736d94d`（三个应用照抄：knowbench `6b28350`、knowlab `47cf74c`、knowmart `23a18a3`）。登录时留下用户访问令牌，要调 knowbase 时向 Casdoor 换一个给 knowbase 的令牌（RFC 8693）。在临时 Casdoor 4.12.0（与正式同镜像）上实测通过，记录与脚本在 sunmoonun `8599c623`（`scripts/results`）。
- 后加的三项：读的一方交还自己的运行授权 `POST /grants/{id}/release`（`d17eb26`）；应用搬自己的旧资料 `POST /imports`（服务关系 `user-data-import`，只进调用方自己的分区，按原编号幂等，`f6fcf8f`）；同意依据最多 1000 份、授权仍 64 份（`f7eaa39`）。

### 2. 块 2：knowbench 云端知识库

knowbench 后端 `a359320`、网页 `39d17d9`。网页的「知识库」页换成 knowbase 的 knowbench 分区（上传、看、删、下载，写明每份从哪来）。旧的「资料库」页与它的预览样例删了（网页那一大片删减就是这个）。

### 3. 块 4：清单格式（数据需求声明）

knowmart 后端 `cf1cdbe`（父 `b6e83d9`，契约 `knowbot-manifest/v1` 只加）。清单外层加 `data_needs`：每样有 key、名字、说明、格式、必填、份数范围、表格类要有的表与列，合起来不超过 64 份。绑定可写对应哪一样 `need`。写了声明的交到 knowmart 不带绑定。声明为空、`need` 没写时不进规范 JSON，旧清单摘要不变（测试钉了加之前的两个摘要）。knowlab 后端 `28db63b`：建稿先核声明，测试绑定按声明核。

### 4. 块 5：请专家用自己的数据

- 读数层（抽文字、分页、按格子、核引文）从 knowlab 搬到 knowbench：`a4797cc`。
- 委托钉住的数据（迁移 `20261023_0024`，后改主键为（委托，数据编号），加授权种类、交还时间）：读数据工具、`compute`、数值验收先读钉住的那几份。云端凭委托的运行授权经 knowbase 读；本地经服务流一块块读。取到就核 sha256，对不上报「数据在这次委托开始后被改过」：`77f3114`。
- 请专家选数据：没选必填的不建委托；云端凭本人令牌核资料、签一条委托运行授权（7 天兜底），本地只收本地知识库目录里的文件、由本地 link 算摘要（老版本 link 一块块读回来算）；同一把幂等钥匙重发不再签；建委托没成就交还；委托结束由 runner 交还。后端 `41596bd`、网页 `5a1262d`（选数据弹框）。
- 本地 link：服务流能只读本地知识库目录（`3f44f92`），新加 `fs/digest`（`855655b`）。
- 聊天、工作里选用云端知识库：每段对话选几份，凭「会话」运行授权（24 小时兜底，改选就换一条、交还旧的）；`list_library`、`read_library_item` 改读这几份；撤掉旧的「交回物当资料」（迁移 `20261023_0025`）。后端 `57ab32e`、网页 `5fe3e2d`。

### 5. 块 3：knowlab 知识库搬进 knowbase

knowlab 后端 `b8dd62b`、网页 `3be2704`（父 `9fafac8`，契约 `knowbot-test-run/v1` 只加 `data_grant`）；knowbench 后端 `cc81702`。新传的只在 knowbase；删也走 knowbase；每人最多 1000 份。传、删、打开知识库页时更新测试同意。发起测试签测试运行授权、随请求带 `data_grant`，结束、退回、开跑失败都撤。knowbench 测试按授权钉住的读。一次性命令 `python -m app.bootstrap.import_datasets` 搬旧数据。签不出授权时测试照跑，退回旧路（经 knowlab 读）。

### 6. 块 6：knowmart

详情页显示「需要的数据」（`458f1f1`、`1ca4ddf`）；knowmart 知识库 D（`e857e6d`、`d19ab30`）。供需市场见第三部分。

### 7. 请重点看（0042）

1. **令牌交换与 knowbase 验令牌**：`aud`、`azp` 的核法；交换来的令牌只用于 knowbase；令牌不进日志。Casdoor 三个应用要打开令牌交换授权类型（平台配置）。
2. **运行授权的时限与交还**：委托 7 天、会话 24 小时、测试按超时加最长等待再加一小时（最多 7 天）兜底；交还在委托结束、会话改选、测试结束时。runner 交还失败只记一行（到期自己失效）。够不够？
3. **钉住与核对**：本地文件由本地 link 算摘要；数据在委托开始后被改过时，验收记「平台没能核」而不是判失败。这个口径对吗？
4. **一份数据两处并存的过渡期**：knowlab 旧对象留到「财务分析与预测」第 1 版停用（第 1 版运行时照旧经 knowlab 读）；`knowlab_data_client.py` 与旧读数路等那时再撤。
5. **同意依据放宽到 1000 份**：契约 `user-data/v1` 只改了这一处上限（授权仍 64 份）。

---

## 三、0018 第十一节：knowmart 供需市场（10-23 晚）

所有者 10-23：「都做出来，以后不要被法律评估挡住：如果挡住就按是否有资质处理」，供需市场设计六项「都按你拟的」（决定记录 `95acef83`）。

| 块 | 提交 |
| --- | --- |
| 后端：迁移 `20261023_0007`。发布主体按用户一条，实名只存遮住的号码与摘要，证件照片存私有表、审过留一年；资质加照片；knowbot 加每次请的价格与上架审核；新表：知识条目、需求、响应、交易记录、评价、留言、驻场规则版本、举报。web端、管理端接口；公开改为「要证照的类目看证照，不要证照的看发布主体实名审过」；平台开了公开（`PUBLIC_MARKET_ENABLED`）时别人也能请，「请这位」记一笔成交；买知识经 knowbase 复制进买家选的 knowbench 或 knowlab 知识库，买来不许转卖的不能再卖；每小时定时活（资质到期提醒、过期改回自用或下架、照片到期清掉） | knowmart 后端 `e568c79`、`762189d`（父 `f5a052c`） |
| web端八栏：专家、知识、需求大厅、我发布的、我买到的、知识库、发布主体、驻场规则 | `9aa357a`（父 `409d0b4`） |
| 管理端五栏：条目审核（标出禁止类的词）、资质审核（看证件照片）、举报处理、驻场规则（改了出新版本）、成交记录 | `627e3e1`（父 `b47dbb0`） |

请重点看：
1. **实名与证件**：身份证号只存遮住的与摘要；照片的存放、谁能看、留一年后清。合规上够不够？
2. **公开的判定**：类目要不要证照（类目表 `domain/knowbots/catalog.py` 的 `license` 一栏，判定在 `application/services/market.py` 的 `needs_license`、`_qualified`）；资质过期后自动改回自用或下架。
3. **本期只标价、不收钱**：成交只是记一笔；「请这位」记成交的条件（请的是别人公开的专家）。
4. **买知识的复制**：经 knowbase 的 `user-data-purchase` 复制；不许转卖的标记跟着走。
5. 市场的管理端接口与 knowmart 原有管理端角色的关系。

---

## 四、10-23 上午：本地 link 0.5.2 一批与几笔账

| 账 | 做了什么 | 提交 | 回执 |
| --- | --- | --- | --- |
| 129 | 测试电脑的测试目录：服务流在测试电脑上（`SUNMOON_AGENT_TEST_RUNS=1`，只认 Linux）可在白名单根下 `runs/<名字>` 建、删一层目录；knowbench 读目录按本地 link 实际回的 `name/type`（原来字段名不对，实际一个旧目录都删不掉） | link `1b61b7d`；knowbench 后端 `f608e0e` | 052-1 |
| 143 | 设备编号（第一次运行生成、一直沿用）；hello 与 `/presence` 带编号、主机名、系统、连接状态；托盘五项；叫法改「本地 link」「重新颁发令牌」「确认码」。会合点转发编号；knowbench 按编号认机器（迁移 `20261023_0022`），新接口 `GET /api/workbench/local-link`；网页打开工作台时核对本机与账号配的是不是同一台，侧栏不挂状态，设置改三项 | link `97c76bc`；k8s `3644498b`；knowbench 后端 `c9a8de8`、网页 `fb7a064` | 052-1、052-2、052-3 |
| 141 | 测试已受理、没开跑时记下在等什么（测试电脑不在线 / 还没给出干净目录，迁移 `20261023_0023`）；契约 `knowbot-test-run/v1` 结果加可选的 `blocked`；knowlab 管理端照实说 | knowbench 后端 `c9a8de8`；knowlab 后端 `b810ae3`、管理端 `252a359` | 052-2 |
| 128 | Windows 包一条命令出包；版本号 0.5.2；入口改叫 SunMoon link；安装脚本模板同步 | link `57d1061`、`7b27e9d`；k8s `3fdbef6d` | 052-1 |
| 165 | 远程登录 link 的电脑也能看文件、看工作底稿、新建项目（经会合点服务流转发；令牌只转给本地 link，不进日志、不存） | link `3a537bd`；knowbench 后端 `41930be`、网页 `9dacdfd` | 052-4 |
| 168 | Windows 上 Codex 命令默认走提权沙箱：给沙箱账户补授读程序目录（普通模式拦写不拦删）；托盘「提高安全」；网页提示普通模式 | link `5bc283a`；knowbench 网页 `aef3233` | 052-5 |
| 83 | 右边栏「终端」不做（所有者 10-23），去掉占位栏；SDD 0040 远程终端写了设计稿后作废 | knowbench 网页 `ac69cfd`、`2d4e513` | — |
| — | exec-server 开并发处理（`--concurrent-requests 8`） | link `7ecd50b` | — |
| — | knowlab 管理端角色：operator 现在也能做全部管理端的事（admin 多出的权限以后定） | knowlab 后端 `6134b40`、管理端 `c404784` | 决定记录 `094e4002` |

设计稿（只有文档）：SDD 0041 远程目录（第一期改为「本地 link 经 SSH 把执行端放到远程机器上」，挂载作废，记了第一轮实测），SDD 0040 远程终端（作废）。

请重点看：
1. **168 的补授读**（`windowsSandboxRead.ts`）：给 `CodexSandboxUsers` 授读的范围（本地 link 自带的 `node`、`app` 与用户目录下 PATH 里的目录），以及排除项（`.ssh`、控制目录、codex-home）。Astra 熟悉 Windows 沙箱，请特别看这一条。
2. **129 测试电脑能删目录**：只认 Linux、只在 `runs/` 下一层、不跟链接。
3. **165 远程拉仓库要令牌**：令牌经会合点转给本地 link 的那一路。
4. **0.5.2 还没发**：版本号与安装脚本模板改了，等 Fable 出包。

---

## 五、几处我顺手改的、可能被忽略的

- knowlab 后端 `knowbot_data_read.py`：只在 knowbase 的资料（没有旧对象）经 knowlab 旧路读时，原来会把 `None` 传给对象存储，现在回「没有」（类型检查发现的旧问题）。
- knowlab 后端一条真库测试按提交时间比先后，同一事务里写的两条时间一样，偶尔失败；改成不按先后比（`23af09f`）。
- 几个仓的格式化工具会顺手改无关文件，我都只格式化了自己改的文件；各仓原有的格式、行长问题没动。

---

## 六、发版时要配（等 Fable；都已写进对应 SDD）

发布顺序：knowbase → knowmart → knowbench → knowlab。本地 link 0.5.2 单独出包。

- **knowbase**：迁移到 `20261023_0008` 并改期望库版本；配置 `user_token_audience`、`user_token_apps_json`、`user_data_bucket`、`user_data_prefix`、`user_data_reader_apps_json`；服务关系 `user-data-read`、`user-data-grant-test`、`user-data-purchase`、`user-data-import`（knowlab 的导入身份要登记成 knowlab）。
- **Casdoor**：knowbench、knowlab、knowmart 三个应用打开令牌交换授权类型；建 knowbase 目标应用（它的客户端编号就是各应用的 `KNOWBASE_USER_AUDIENCE`）。
- **三个应用**：`KNOWBASE_USER_AUDIENCE`、`KNOWBASE_INTERNAL_URL`、`KNOWBASE_USER_DATA_<关系>_SERVICE_*`。
- **knowbench**：期望库版本 `20261023_0025`；runner 能连 knowbase（交还授权）。
- **knowlab**：期望库版本 `20261024_0012`；发版后跑一次 `python -m app.bootstrap.import_datasets`；两个前端与后端一起发。
- **knowmart**：期望库版本 `20261024_0008`；`PUBLIC_MARKET_ENABLED`（打开才有公开的专家）；Celery beat 跑 `market-sweep`；`KNOWBASE_USER_DATA_PURCHASE_SERVICE_*`；`CROSS_APP_TARGETS_JSON` 加 knowlab 的 `web_base_url`（专家详情「到 knowlab 停用」的去处；不配就只写一句去哪停）。交付的 `request_public`、停用、空号结局都用现有的 `knowmart:deliver` 服务关系。
- **账 141、143、165、168**：knowbench 迁移 `20261023_0022`、`0023`（已含在 0025 之前）；会合点随 k8s `3644498b`。

## 七、还没做的

- 块 7：「财务分析与预测」按新格式重孵化第 2 版，上架后停用第 1 版；之后撤 `knowlab_data_client.py`、knowlab 的旧读数路与旧对象。要部署后在线上做。
- 0037 的真跑、补运营审核记录、收缩迁移（第一部分第 8 小节）。
- 0029 的孵化记录与辅助、自动孵化（0037 第十五节，本期不做）。
- 所有页面都没在浏览器里实机看过，要等发版后所有者走一遍。
