# Opus 对评审意见的处置（2026-10-24）

收到 Astra（`astra.md`）、Qwen（`qwen.md`）、Kimi（`kimi.md`）三份；Fable 的还没到，到了另补。

每条在源码里核过再处置。改了的都在 qwen 工位提交（只提交、不推、不发），各仓全量测试过、与 fable 分支试合并干净。所有者 10-24 定：Astra 的 F05、D02、D03 由 Fable 定，这里不实施，只写明待定什么。

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
| F05 0037 迁移的发版与回退 | 待 Fable 定 | 待定：旧程序能不能与新库共存；还是发版窗口停写；downgrade 要保住哪些新状态 | — |
| F06 资格没贯穿审核与使用 | 改了 | 资格收成一条：主体实名审过，类目要证照的另要有效证照。以下几处都现核：运营批准知识条目或公开专家（不过回 409 `publisher_not_qualified`）；知识市场只列卖家现在有资格的；买（409 `listing_unavailable`）；召请与公开专家列表（有证照也要主体审过）。扫表照旧收敛展示 | knowmart `248f9fb`、web `fce9b22`（`413c924`） |
| F07 买知识没有可恢复的幂等 | 改了 | `BuyIn` 带 `request_id`。先落一笔「复制中」，定下成交编号与要复制的几份，逐份复制、逐份记下，都复制完才成交。同键重来接着做；同键不同参数回 409 `request_reused`；换键同参数的，接着做没复制完的那一笔；并发只有一笔（买家 + 键唯一）。没复制完的不进「我的成交」，运营的成交记录标出来；不许转卖按要复制的几份算。迁移 0007 未发布，trade 表直接加栏。网页每次打开生成键，重试沿用，改了买进哪里就换键 | knowmart `f491bac`、web `af3ffc7`、管理端 `84f96ee`（`413c924`） |
| F08 空号结局整份替换、尽力送 | 改了 | knowmart 改按版本逐条写：`PUT .../unlisted/{version}`，body `{outcome}`，终态 upsert，乱序与重发都收敛。knowlab 逐条送，送到一条记一条 `unlisted_sent_at`（迁移 0012 未发布，直接加栏）；beat 每 5 分钟跑 `knowbot-unlisted-resend` 补发 | knowmart `28a983a`、knowlab `50695d3`（`413c924`、`ee03afe`） |
| D01 Windows 补授只核路径字符串 | 改了 | 从用户目录到目标逐级 lstat，有一级是符号链接或联接就不授；realpath 核出的实际目标必须就是这个路径。icacls 的查与授都带 `/L`，授之前再核一遍。另一点：PATH 当授予清单是否收窄到固定的程序根，影响所有者实测过的 Python 场景，没改，写进 0042 的已知限制。真 NTFS 上的 ACL 与沙箱实读没有 Windows 实机，没测 | sunmoon-link `c2cbb83` |
| D02 试行期补审不通过 | 待 Fable 定 | 待定：补审只是补历史记录（页面写明「不改变已有可用性」），还是有效准入门（不通过就按停用流程先停 knowmart） | — |
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

## 四、发版要配因此多出的（已写进 0037、0042、0018）

- knowbase：迁移 0008 的内容变了（读数留痕多 `check`），版本号不变。
- knowlab：迁移 0011（多一张待撤同意表）、0012（专家多 `unlisted_sent_at`，开头核数据前提）内容变了，期望库版本仍是 `20261024_0012`。beat 多一项 `knowbot-unlisted-resend`。
- knowmart：迁移 0007 内容变了（trade 多四栏），期望库版本仍是 `20261024_0008`；新私密配置 `PUBLISHER_ID_HASH_KEY`。空号结局的内部接口换成按版本写，knowmart 要先于 knowlab 发（现有顺序已满足）；先发的 knowlab 送不到也会补发。
