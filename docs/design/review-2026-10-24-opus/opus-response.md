# Opus 对评审意见的处置（2026-10-24）

收到 Astra（`astra.md`）、Qwen（`qwen.md`）、Kimi（`kimi.md`）、Fable（`fable.md`，10-25，按改完后的最新代码审）四份。

每条在源码里核过再处置。改了的都在 qwen 工位提交（只提交、不推、不发），各仓全量测试过、与 fable 分支试合并干净。所有者 10-24 定：Astra 的 F05、D02、D03 由 Fable 定；Fable 10-25 定了，照它定的实施（第四节）。

处置分四种：
- **改了**：写明提交；
- **核过成立，不用改**：写明依据；
- **待 Fable 定**：不实施；
- **本期不做**：写明理由。

提交号写子仓号，括号里是父仓号。

## 一、Astra

| 条 | 处置 | 怎么改的 / 依据 | 提交 |
| --- | --- | --- | --- |
| F01 缓存绕过授权与摘要 | 改了 | knowbase 加「核一次」：`GET /grants/{id}/items/{item}/check`，判断与读内容相同但不给内容，留痕 `operation=check`（迁移 0008 未发布，CHECK 直接加值；契约 user-data/v1 只加 `ItemCheck`）。knowbench 每次读，没取字节就先核一次：云端调 check，本地请 link 用 `fs/digest` 重算（老 link 整份读回来算）。抽取结果照旧缓存。补测：暖缓存后撤授权、暖缓存后改本地文件、同摘要不同授权、并发读 | knowbase `9ecc492`、`5c45cf6`（`cef673e`）；knowbench `9e5ed18`（`606616c`） |
| F02 签不出测试授权照样开跑 | 改了 | knowlab 开测前分三种情况：没绑数据不签；绑的都没搬进 knowbase，照旧经 knowlab 读（0042 第七节「没搬完的」）；有搬进去的必须签。以下情况开测前就报，不建测试：`data_not_imported`（搬了一半）、`data_binding_stale`（数据删了或变了）、`test_consent_missing`、knowbase 没配。knowbase 拒签或不可达时，这一次记平台出错，准专家回待测。knowbot-data/v1 的测试读法只给没签授权的测试、没搬进 knowbase 的那几份。knowbench：授权里的编号不合格受理时就拒；带了授权却没钉上的，不退回 knowlab 读 | knowlab `b32c593`；knowbench `8b21a46`（`ee03afe`、`606616c`） |
| F03 资料被自己的测试同意挡住 | 改了 | 删除的顺序改成：核引用 → 立不含这一份的新同意、旧的记进待撤（迁移 0011 新表 `knowbot_consent_withdrawal`）→ 撤待撤的 → 删 knowbase 资料、记删除。撤不成回 `consent_not_withdrawn`，可重试，旧编号不丢；活动授权挡住删除时，同意放回这一份；打开知识库页时接着撤待撤的。假 knowbase 照实拦删除 | knowlab `dc5e11c`、web `5336d29`（`ee03afe`） |
| F04 买进 knowlab 的看不到 | 改了 | 打开知识库页先列 knowbase 的 knowlab 分区，没登记的补登记：数据编号 = uuid5(固定命名空间, 资料编号)，重来不重复；删了的不再登记回来。补上的随即进测试同意，能绑、能签。knowmart 买好提示「已复制进你的 knowlab 知识库」，用户打开那页就收拢 | knowlab `74f451e`（`ee03afe`） |
| F05 0037 迁移的发版与回退 | Fable 10-25 定、已实施 | 停写切换，不做新旧共存；downgrade 有新写入就拒，回退用发版前备份（见第四节） | knowlab `614c1b9` |
| F06 资格没贯穿审核与使用 | 改了 | 资格收成一条：主体实名审过，类目要证照的另要有效证照。以下几处都现核：运营批准知识条目或公开专家（不过回 409 `publisher_not_qualified`）；知识市场只列卖家现在有资格的；买（409 `listing_unavailable`）；召请与公开专家列表（有证照也要主体审过）。扫表照旧收敛展示 | knowmart `248f9fb`、web `fce9b22`（`413c924`） |
| F07 买知识没有可恢复的幂等 | 改了 | `BuyIn` 带 `request_id`。先落一笔「复制中」，定下成交编号与要复制的几份，逐份复制、逐份记下，都复制完才成交。同键重来接着做；同键不同参数回 409 `request_reused`；换键同参数的，接着做没复制完的那一笔；并发只有一笔（买家 + 键唯一）。没复制完的不进「我的成交」，运营的成交记录标出来；不许转卖按要复制的几份算。迁移 0007 未发布，trade 表直接加栏。网页每次打开生成键，重试沿用，改了买进哪里就换键 | knowmart `f491bac`、web `af3ffc7`、管理端 `84f96ee`（`413c924`） |
| F08 空号结局整份替换、尽力送 | 改了 | knowmart 改按版本逐条写：`PUT .../unlisted/{version}`，body `{outcome}`，终态 upsert，乱序与重发都收敛。knowlab 逐条送，送到一条记一条 `unlisted_sent_at`（迁移 0012 未发布，直接加栏）；beat 每 5 分钟跑 `knowbot-unlisted-resend` 补发 | knowmart `28a983a`、knowlab `50695d3`（`413c924`、`ee03afe`） |
| D01 Windows 补授只核路径字符串 | 改了 | 从用户目录到目标逐级 lstat，有一级是符号链接或联接就不授；realpath 核出的实际目标必须就是这个路径。icacls 的查与授都带 `/L`，授之前再核一遍。另一点：PATH 当授予清单是否收窄到固定的程序根，影响所有者实测过的 Python 场景，没改，写进 0042 的已知限制。真 NTFS 上的 ACL 与沙箱实读没有 Windows 实机，没测 | sunmoon-link `c2cbb83` |
| D02 试行期补审不通过 | Fable 10-25 定、已实施 | 有效准入门：不通过走停用流程（见第四节） | knowlab `9551115`、管理端 `25ca1d6` |
| D03 撤回同意是否终止已发授权 | 待 Fable 定 | 待定：撤同意只挡新授权（现状），还是同时撤掉由它签出的授权。F01 已让撤授权本身对缓存生效 | — |

## 二、Qwen

| 条 | 处置 | 怎么改的 / 依据 | 提交 |
| --- | --- | --- | --- |
| Q-01 回填编号排序不稳 | 改了 | 排序键加建立时间与编号兜底；迁移开头同时核现网数据前提（见 Kimi 第 2 条） | knowlab `fc28f29`（`d10deb6`） |
| Q-02 aud/azp 核验 | 核过成立 | `oidc.verify_access_token` 先核签名，再核 aud 必须含 knowbase 受众（不含回 `audience_mismatch`，`test_oidc_security.py:206` 有受众不对的用例），再核 iss/exp。`UserTokenVerifier` 再按 azp 认应用，只认登记的三家（`test_user_tokens_that_are_refused`）。真 Casdoor 上「别的受众被 knowbase 拒」随上线验收再跑一次 | — |
| Q-03 证件照片清理 | 核过成立 | `purge_documents` 到期把 content 置空、记 `purged_at`，行留作审计；量大了再挪对象存储 | — |
| Q-04 停用窗口期 | 核过成立 | knowlab 记录失败时，那一版仍是「上架中」，再点停用即可（knowmart 再停幂等 204），这就是手动对账，不另加按钮 | — |
| Q-05 栏目全量加载 | 本期不做 | 试行量小；创意多了先把 counts 下推成 SQL 聚合（Kimi 第 9 条同），再改分组。记进待办账 169 | 文档 |
| Q-06 授权时限与设计不符 | 改了 | 属实：knowbench 申请委托 7 天、会话 24 小时，knowbase 截成 24、12 小时（会话到期 knowbench 还按 24 小时记）。上限改成委托 7 天、会话 24 小时。孵化 6 小时不变，现在没有调用方，接上时再定 | knowbase `a37915f`（`9759248`） |
| Q-07 需求生命周期 | 核过成立 | `demand` 表有 `deadline` 与 `status`（open / chosen / closed / taken_down），响应也有状态 | — |
| Q-08 老 link 回退 | 改了 | 回退路径本来就能用（选数据与读钉住的数据两处都有测试）；走回退时记一行日志，便于看还有多少人没升级 | knowbench `9d6ab2d`（`2a72f77`） |
| Q-09 同意文字改了版本没升 | 核过成立 | 意思没变，不升，免得全员重签；0037 记一句 | 文档 |
| Q-10 market-sweep 幂等 | 核过成立 | 提醒记 `reminded_at`，提醒过的不再提醒；照片清理是置空，可重复 | — |
| Q-11 items 结构 | 核过成立 | `KnowledgeListingIn.items` 至少 1 份、每份按 `KnowledgeItemRef` 校验，后端挡 | — |
| Q-12 data_needs 上限 | 核过成立 | 清单模型后端校验：最多 20 样，`max_count` 合计不超过 64，键不重复 | — |
| Q-13 Windows 补授范围 | 改了一部分 | 见 Astra D01；「PATH 里目录内的文件沙箱都能读」写进 0042 已知限制 | sunmoon-link `c2cbb83` |
| O-01 至 O-04 | 记下 | 收缩迁移在 0037 真跑过后出；发版卡每步写验证点，在 0037、0042 的发版要配里 | — |

## 三、Kimi

| 条 | 处置 | 怎么改的 / 依据 | 提交 |
| --- | --- | --- | --- |
| 1 内部停用不核来源 | 改了 | knowlab 来停的只认 `knowlab-` 开头的引用，别的回 404；空号结局也只收 knowlab 的引用。现网自第一次交付（`318559a`）起引用都是 `knowlab-{request_id}` | knowmart `435a5d4`（`ac0aa3e`） |
| 2 0012 回填的数据前提 | 改了 | 迁移开头先查三条（通过、已交付的版本号是整数；同一创意不重号；至多一个测试中的），不成立就停下、列出前 20 行，不半途撞约束；真库测试造了坏数据确认会停 | knowlab `fc28f29`（`d10deb6`） |
| 3 sha256 不符静默退旧路 | 改了 | 同 Astra F02：数据删了或变了回 `data_binding_stale`，不开测 | knowlab `b32c593` |
| 4 审核过、交付失败 | 核过成立 | 管理端「待交付」那一档红字显示交付错误，带「交付」按钮重试。并发双击会双发，靠交付单号幂等兜住 | — |
| 5 身份证号摘要没加盐 | 改了 | 改 HMAC-SHA256，钥匙 `PUBLISHER_ID_HASH_KEY` 放 SOPS；没配时个人入驻回 503 `publisher_unconfigured`。还没有真实数据，不用重算 | knowmart `bc22bd1`、web `02b2927`（`ac0aa3e`） |
| 6 受理不加锁 | 改了 | 受理先锁名称，后到的回 409 `already_decided`；真库并发测试 | knowlab `a7c308c`（`d10deb6`） |
| 7 空号结局尽力送 | 改了 | 同 Astra F08 | — |
| 8 授权孤儿兜底 | 核过成立 | 交还的扫表覆盖四种终态（与 `TASK_TERMINAL` 一致）。委托删了，钉表随之级联删除，那条授权就等兜底时限自己失效（委托授权兜底 7 天）。knowlab 撤测试授权失败的告警，发版后盯 | — |
| 9 性能 | 本期不做 | 同 Qwen Q-05 | — |
| 10 照片存库 | 核过成立 | 同 Qwen Q-03 | — |
| 三·0037-1 回退丢什么 | 记下 | 写进 0037 第十八之二节第 4 小节 | 文档 |
| 三·0037-5 同意版本 | 记下 | 同 Qwen Q-09 | 文档 |
| 三·168 真机回归 | 记下 | 「已有授权但缺 CI」等中间态，等所有者 Windows 真机回归一次；写进 0042 已知限制 | — |

## 四、Fable（10-25，按改完后的最新代码审）

Fable 自己定的三条照定的做了；P1、P2 逐条在源码里核过再改。平台那几条（令牌交换的身份注册、网页端令牌 12 小时、跨应用网络与服务身份、服务流上限、发版卡）归 Fable，所有者 10-25 定等代码修完一起做。

| 条 | 处置 | 怎么改的 / 依据 | 提交 |
| --- | --- | --- | --- |
| F05 发版与回退 | 照定的做 | 0012 的 downgrade 开头核新写入：新代码发起的测试、第 2 版以后的创意、人写的受理单、非试行期的专家；有就拒、报各多少，回退改用备份。真库测试：升级后写一次新测试，再退被拒。停写切换的三步写进 0037 发版要配 | knowlab `614c1b9` |
| D02 补审不通过 | 照定的做 | 不通过走停用：先停 knowmart，停成了才记，理由「补审没通过：…」；停不成审核结论照样留着，管理端写明「已判不通过，停用没成，请重试」 | knowlab `9551115`、管理端 `25ca1d6` |
| D03 撤同意 | 照定的做 | 契约 user-data/v1 写明：撤同意只挡此后的签发，已签的到交还、撤销或到期为止 | knowbase-app `8e91d13` |
| P1-1 测试授权截成 26 小时 | 改了 | knowbase 测试上限改 7 天；knowlab 按回包的签发与到期时刻比，签出的比要的短就撤掉、当没签成（`grant_too_short`） | knowbase `3df65ea`、knowlab `0b99028` |
| P1-2 卖家删在架资料、成交卡住 | 改了 | 删知识库资料前核待审、在架条目，在就 409 `item_listed`；复制时卖家那份没了，这笔记终态 `failed`（迁移 0007 加 `failure`），已复制的归买家、不再接手，换键可再买 | knowmart `aa182c4`、web `d1adb0a` |
| P1-3 只读目录卡住所有测试 | 改了 | link 删不掉时逐级 lstat、不跟链接，把自己的目录补 `u+rwx` 再删（node 24 实测只读目录能删、链接指向的目录权限不动）；knowbench 删旧目录被拒只记一行，照样建这次的。测试电脑 run.sh 的兜底删除归 Fable | link `c5cef2d`、knowbench `05911d1` |
| P1-4 远程新建项目记住令牌 | 改了 | 网页远程时不显示「记住」也不发；knowbench 收到不转；link 服务流来的 clone 一律去掉 remember | link `1c4cea9`、knowbench `e41edac`、web `94c620c` |
| P1-5 令牌交换的身份注册 | 归 Fable | 平台 | — |
| P1-6 答过的提问套到别的用例 | 改了 | 答案连同那条用例当时问的哪一句（摘要）一起记，编号与摘要都对上才并，不然照样问用户；记答案前锁名称（也修了 P3「两问同时答丢一个」）；网页改创意保留原用例编号、新的才发新号 | knowlab `8af7d59`、web `fa7f0e1` |
| P2-1 审成公开、第一次交付必定自用 | 改了 | 查出 knowmart 根本没有地方给专家设类目：卖家「我发布的」申请公开时选类目；交付时没类目回 `category_needed`、资质没过回 `not_qualified`，knowlab 管理端照实显示 | knowmart `7df9aa9`、web `e6e8506`、knowlab 管理端 `28c79f0` |
| P2-2 自用 / 公开按版本还是整位 | 改了 | 以 knowlab 逐版审核为准：knowmart 版本记 `public_allowed`（迁移 0008 加，之前的回填为真），别人只看到、只请得到审成公开的那几版 | knowmart `04afca2` |
| P2-4 搬家后测试开不了跑 | 改了 | 搬过来的旧数据还有旧对象、本人还没补上测试同意时，照旧经 knowlab 读；同意是最新的就必须签授权。搬旧数据命令的说明改对 | knowlab `c053eb7` |
| P2-5 同意并发刷新漏旧同意 | 改了 | 读当前、立新、换下旧的整段在这个人的锁里；立了没记上当场撤掉；真库并发测试只立一条 | knowlab `c053eb7` |
| P2-6 补登记与搬家竞争 | 改了 | 补登记跳过 `origin_ref` 以 `knowlab-dataset:` 开头的；搬旧数据写本地时加锁 | knowlab `c053eb7` |
| P2-7 换键接手不记新键 | 改了 | 接手时把新键记进 `trade_request_alias`（迁移 0007 加表），按键查时一并看 | knowmart `162865c` |
| P2-8 审过的主体、证照不能撤销 | 改了 | 运营可撤销（`…/revocation`）：撤主体即不算实名、公开专家改自用、在审在架知识下架；撤证照收回那个类目的；现核随即不过。管理端资质审核加「已审过的」一节 | knowmart `1303b2a`、管理端 `d14c3dc`、web `18981c7` |
| P2-9 需求选中后结不了单 | 改了 | 选定的也能关；选中的卖家可补附条目再成交；请专家时选中那家附的正是这位就记在需求上、关掉 | knowmart `d69dde2`、web `db315f2` |
| P2-10 「只自用」冲掉下架 | 改了 | private 保留 `taken_down` | knowmart `7df9aa9` |
| P2-11 远程操作不核哪台机器 | 改了 | 经会合点转的要求选的这台此刻正连着（对账每 10 秒按设备编号记），不是回 409 `machine_not_connected`。比会合点在线代理的编号更准，但每次远程读都要多问一次会合点，没这样做；切换后约 10 秒的窗口照旧 | knowbench `1cf2b07`、web `44d08cd` |
| P2-12 控制目录的令牌沙箱读得到 | 改了，待实机 | 补授读时对 `config.json`、`mcp.json`、两处 `auth.json` 加 CodexSandboxUsers 显式拒绝读。核过 Codex 源码的排除名单确实没有这两个目录；没有 Windows 实机，要所有者用沙箱账户 `type` 验 | link `4f36a06` |
| P2-13 服务流上限 | 归 Fable | 平台配置 | — |
| P2-14 测试漏了 /tmp | 改了，平台要配 | 测试的一轮沙箱 `excludeSlashTmp=true`、`excludeTmpdirEnvVar=false`（核过 Codex 字段名）；开测前随别的目录清掉并重建 `runs/.tmp`。测试电脑把 TMPDIR 设到 `<工作区>/runs/.tmp` 才生效，没设之前行为不变 | knowbench `39b5dc6` |
| P2-15 设备编号一换挂在离线记录上 | 改了 | link 重新 init 留着原编号；knowbench 新编号报到时认领同名、同主机、已离线的老记录 | link `d85aeb9`、knowbench `281f4bc` |
| P2-16 不许转卖没跟着走 | 改了 | 成交记下那一刻的 `resale_allowed`，按它算；knowbase 复制时给买家那份带 `no_resale`（契约只加可选字段），同一个人再传同样内容的也带上；knowmart 上架按标记拦、摘要兜着；knowbench 云端知识库、knowlab 知识库标出「不许转卖」。改过字节的认不出，只能靠驻场规则 | knowbase `b031c85`、knowmart `928ad74`、knowbench `1e640b4`、`1ba80ac`、knowlab `519e21d`、`3a0f2c8` |
| P3 | 记账 | 已顺手修的：两问同时答丢一个（随 P1-6）、knowmart 契约说明没写只认 `knowlab-` 引用、0008 说明还写「整份替换」。其余记进待办账 170 | — |

父仓：knowbase-app `e268747`、knowbench-app `e9dc9eb`、knowlab-app `6e95425`、knowmart-app `09218c1`。

## 五、发版要配因此多出的（已写进 0037、0042、0018）

- knowbase：迁移 0008 的内容变了（读数留痕多 `check`），版本号不变。
- knowlab：迁移 0011（多一张待撤同意表）、0012（专家多 `unlisted_sent_at`，开头核数据前提）内容变了，期望库版本仍是 `20261024_0012`。beat 多一项 `knowbot-unlisted-resend`。
- knowmart：迁移 0007 内容变了（trade 多四栏），期望库版本仍是 `20261024_0008`；新私密配置 `PUBLISHER_ID_HASH_KEY`。空号结局的内部接口换成按版本写，knowmart 要先于 knowlab 发（现有顺序已满足）；先发的 knowlab 送不到也会补发。
- Fable 评审后再加：
  - knowlab 迁移 0011（数据记录加 `no_resale`）、0012（退回前核新写入）内容又变；
  - knowmart 迁移 0007（成交加 `failure`、`resale_allowed`，加 `trade_request_alias` 表，主体与证照的审核状态加 `revoked`）、0008（版本加 `public_allowed`）内容又变；
  - knowbase 迁移 0008（资料加 `no_resale`）内容又变；
  - 各期望库版本号都不变。测试电脑的 TMPDIR 设到 `<工作区>/runs/.tmp`（P2-14）。
