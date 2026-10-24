# Astra 审查意见：Opus 2026-10-23—24

审查日期：2026-10-24。依据本目录 `request.md`；独立审读，没有读取其他评审人的意见。

## 结论与边界

**建议先修下面的问题，再将 0037、0042 与供需市场作为一批发布。** 当前主要风险在跨服务拼接处：每个服务单看都有检查，但组合后存在授权失败仍开跑、缓存跳过授权、资料无法删除、购买后接收应用不可见等问题。0037 的迁移也不能按“只扩不缩，所以旧程序还能运行、换回旧镜像即可回退”来安排。

这是一份**源码与设计审查**，不是上线验收报告。本次没有执行测试、迁移、构建、Windows ACL 命令或线上调用，没有改实现、部署配置及运行状态。下文“触发步骤”是根据真实调用链给出的复现方法，**不是声称已实机复现**。作者报告的测试通过数不在本报告中再次背书。

重点审读了 0037 的迁移、测试与专家状态流转，0042 的令牌、同意、授权、读取、删除与购买链路，以及市场资格检查、link 的 Windows 补授读与服务流实现。前端只抽查了 knowbench 的数据选择和本地/远程 link 分流；**没有逐页审完所有前端、没有做完整性能和合规审计**。

### 审查版本

以下路径均以 `/home/zymun/worktrees/qwen/` 为根。文中的行号对应这些版本。

| 简称 | 仓与版本 |
| --- | --- |
| knowbase | `knowbase-app/knowbase-backend`，`f7eaa399d6dc58d553364f5d9fa00810ab484848` |
| knowbench | `knowbench-app/knowbench-backend`，`cc8170252b227e319feeced72437c21e30fd18d5` |
| knowlab | `knowlab-app/knowlab-backend`，`23af09fd08e374fad24e2c249d52809c9f929820` |
| knowmart | `knowmart-app/knowmart-backend`，`774516703e177a9ea8102e79c0644103d590d13c` |
| link | `sunmoon-link`，`855655b5f662f0d9d5a78ab7f7af9fcb0afb5668` |
| knowbench web | `knowbench-app/knowbench-web-frontend`，`17252b6` |
| 设计与请求 | `sunmoonun`，读取时 HEAD 为 `b6448604`；相对请求中的 `e27dd0bc`，后续变更是评审请求及目录组织 |

严重度：P1 表示建议在相关功能发布前处理；P2 表示应修复的可靠性问题。后面的“待议”不计作已证实的运行故障。

## 一、源码已确认的问题

### F01 · P1：抽取缓存命中后，绕过本次运行授权与文件变化检查

**位置**

- knowbench：`app/app/application/workbench/pinned_data.py:117`（`read`）、`:249`（`_tables`）、`:259`（`_bytes`）。
- knowbench：`app/app/infrastructure/documents/text_extract.py:185`、`table_extract.py:198`。
- knowbench：`app/app/bootstrap/workbench.py:73`；`application/workbench/knowbot_data.py:90`；`session_data.py:195`。
- knowbase：`app/app/application/services/user_data_service.py:256`（实际的运行授权检查）。

**证据与影响**

抽取器的 key 是 `sha256:content_type`。命中就直接返回结果，不调用 `load`；文字抽取中的 `_pending` 也按这个 key 共用任务。抽取器经 `@lru_cache(maxsize=1)` 在进程内共用。

但 `load` 对应的 `_bytes` 正是执行 `cloud.content(grant_id, item_id)` 或本地文件读取、再核 SHA256 的地方。外层 `_scope` 核委托归属和数据绑定；它没有重新核 knowbase 授权。会话 `_live` 仅核本地保存的到期时间，也没有核远端撤销状态。

因此，先成功读一次后：

1. 云端运行授权被撤销，仍活跃的委托/会话再次读同一资料，可直接拿到缓存内容，不经过 knowbase 的 `grant_inactive` 拒绝与读审计。
2. 本地文件被修改，继续读或核引文可能使用旧抽取结果，不触发设计要求的“数据在这次委托开始后被改过”。
3. 同摘要的另一个请求可以复用已有抽取任务，其自己的 `load` 不一定执行。

这**不等于任意用户只凭摘要就能下载数据**，外层仍有绑定检查；问题是已绑定数据的持续授权和新鲜度边界被缓存跨过了。SDD 0042 第五节要求读时核摘要，第六节要求每次读留授权记录。

**建议**

把“是否仍允许这次读、是否还是钉住的数据”放到缓存之前，每次执行。抽取结果可以继续按内容缓存；授权检查不能跟着缓存。云端可设计轻量的授权/内容身份核验与读取审计，但不能仅调用当前不检查 active 的 `grant_view` 就算完成。按当前设计，本地每次使用前须重新核文件摘要；若要改成不可变快照语义，应先修订设计及用户提示。

**补验建议**

暖缓存后撤销授权；暖缓存后修改本地文件；同摘要、不同授权，其中一个失效；同时进行的两次读取。文字、表格、引文验收均覆盖。

现有 `app/tests/test_pinned_data.py:176` 明确断言第二次不再取云端内容；`:187` 的变更检查只覆盖首次读取。不能只增加冷缓存失败用例。

### F02 · P1：knowbase 拒绝测试授权，knowlab 仍启动测试并退回旧读路

**位置**

- knowlab：`app/app/application/services/knowbot_service.py:478`、`:497`，尤其 `:537–548`。
- knowlab：`app/app/application/services/knowbot_data_read.py:252`、`:286`。
- knowbench：`app/app/application/workbench/knowbot_data.py:98–130`。
- 设计：`sunmoonun/docs/design/SDD/modules/0042-knowledge-bases.md:86`，明确“申请不到不开跑”。

**证据与影响**

`_data_grant` 捕获 `test_grant` 的任意 `AppException` 后返回 `None`；无同意记录、资料尚未导入等情况也返回 `None`。`start_test` 不区分“确实不需要资料”和“授权失败”，继续调用 `runtimes.start`。

旧读路只核 active test、运行方、归属与清单绑定，没有再核这次 knowbase 同意/授权：

- 已迁入 knowbase、但仍保留旧对象的数据，授权被拒后仍可能从旧对象读取。这让同意撤回/范围拒绝变成可以绕开的条件。
- 只有 knowbase 副本的新上传资料，旧路 `_content` 因无 `object_key/version_id` 返回不存在。测试已经启动，却必然在用到资料时失败。

请求文档公开说明了这个降级，测试 `test_a_refused_grant_does_not_stop_the_test`（`app/tests/test_knowbot_knowledge_base.py:258`）还将其固定为期望行为；这是实现与安全设计冲突，不是漏加一条异常处理。

**建议**

显式区分“无数据”“受控历史版本兼容”“0042 授权必需”三种情况。历史已交付 v1 的兼容路径可以按设计保留，但不能因新测试的授权拒绝或服务错误自动选择旧路。需要授权而签不出时不得调用运行方，并将已创建的 queued test/draft.testing 正确结束或回滚，保留可诊断的错误类型。

**补验建议**

对撤回同意、越范围、403/404、knowbase 不可达分别断言不启动、不读取旧对象；无资料测试仍可启动；历史 v1 的明确兼容路径单独验。

### F03 · P1：knowlab 的正常上传资料被自己的测试同意永久挡住删除

**位置**

- knowlab：`app/app/application/services/knowbot_data.py:131–157`、`:219–249`、`:267–287`。
- knowbase：`app/app/infrastructure/repositories/user_data.py:136–168`。

**调用链**

1. 上传后 `_refresh_consent` 为当前知识库全部资料创建有效测试同意。
2. 删除未被准专家或测试占用的资料，knowlab 先调 `knowledge.delete`。
3. knowbase 的 `delete_item` 只要发现任何未撤回 consent 引用该项，就返回 `409 in_use`。
4. knowlab 原计划在删除成功后才 `_refresh_consent`，所以根本走不到撤旧同意这一步。

用户没有任何正在使用它的任务，也会删不掉。这不是“在用数据不许删”的预期限制。

**建议**

将删除、收窄同意与本地资料记录维护设计成可恢复操作：核对在用状态，先准备不含目标项的新同意并撤掉仍含目标项的旧同意，再删除；活动运行授权仍由 knowbase 拦住。处理中断或撤销失败必须可重试，不能丢掉旧 consent_id。另一可行方式是由 knowbase 提供原子收窄同意并删除的能力，但不能简单取消活动授权保护。

现有 `_refresh_consent` 撤旧失败仅记日志，随后只保存新 ID，也可能留下长期阻止删除的旧同意；需一起解决对账与重试。

**补验建议**

真实调用两个服务完成“上传一份 → 未绑定 → 删除”，再覆盖活动授权阻止删除、撤旧失败、操作中断后的重试。现有假实现 `app/tests/test_knowbot_knowledge_base.py:64` 的 delete 仅追加列表，不模拟 knowbase 的 consent 冲突，因此当前单元测试不能发现它。

### F04 · P1：买入 knowlab 的知识没有接入 knowlab 的资料目录，无法选来孵化

**位置**

- knowmart：`app/app/application/services/market.py:454–505`（`buy`）。
- knowbase：`app/app/application/services/user_data_service.py:302–346`（`purchase`）。
- knowlab：`app/app/application/services/knowbot_data.py:84–86`、`:159–175`；`knowbot_service.py:322–329`。
- knowlab：`app/app/interfaces/endpoints/knowbot_routes.py:337–350`、`:483–499`；`app/app/application/ports/knowbots.py:473–515`。

**证据与影响**

市场允许 `target_app=knowlab`；购买只把副本写入 knowbase 的买家×knowlab 分区，并在 knowmart 记交易。没有同步创建 knowlab 的 dataset 记录。

与此同时，knowlab 的知识库列表、管理端孵化资料清单、测试同意范围和 `add_draft` 绑定校验都来自本地 `repo.list_datasets`。`KnowledgeBase` 适配接口没有从 knowbase 列表反向接入副本的能力；`import_old` 是相反方向的旧数据导入。

结果是购买返回成功，knowbase 中也有副本，但买家在 knowlab 看不到、运营拿不到合法 dataset_id，不能按设计使用买入资料。

**建议**

明确 knowbase 为资料真源，给 knowlab 建立带幂等 item_id 映射的接入/对账机制，或让资料列表与绑定直接使用统一资料身份。购买后的页面刷新必须能收敛；不要在页面上仅补一条假记录。测试同意仍需遵守用户确认的范围，不能仅凭交易服务身份替用户新增授权。

**补验建议**

真实购买到 C → knowlab 列表可见 → 取得稳定 dataset_id → 刷新/重试不重复 → 选入清单并签测试授权。与购买到 B 分别验证。

### F05 · P1：0037 不是旧程序兼容的扩展迁移，现有 downgrade 也不能保住新运行状态

**位置**

- knowlab：`app/alembic/versions/20261024_0012_knowbot_lifecycle.py:217–224`、`:299`、`:302–329`。
- 旧版 `e328702`：`app/app/infrastructure/repositories/knowbots.py:229`（`create_draft`）、`:351`（`find_delivered_draft`）。
- 新版：`app/app/application/services/knowbot_service.py:463–477`、`:669–708`。
- 旧版 `e328702`：`knowbot_service.py:430`（`refresh`）、`:603`（`reset_stuck`）。

**两个明确的不兼容点**

1. 迁移回填后立即把 `request_version` 设为 NOT NULL，无数据库默认值；旧程序的 `create_draft` 不填该列。迁移完成后旧写入端仍在运行或直接回退旧镜像，就会写失败。单加默认值也不够，旧程序新建创意不会创建对应的版本外键记录。
2. 迁移把旧 `delivered` 改成 `passed`。旧版 `find_delivered_draft` 明确按 `status == delivered` 读取，因此共存期/仅回退镜像时原已交付专家的数据旧读路也会失效。

**downgrade 的额外风险**

新代码不再写 draft 的旧 run/report 字段。新建准专家开始一次测试后，run_id 等只存在 `knowbot_test`；downgrade 仅恢复已上架专家的 delivery，随后删除 test/expert 等表。旧版会得到 `status=testing` 但 `run_id/run_started_at` 为空的草稿：refresh 不问运行方，reset_stuck 也拒绝。新测试记录、审核及停用记录同样不是这一 downgrade 的保留对象。

这不是要求把所有新功能都无损塞回旧 schema，而是必须明确：**这条 downgrade 不能作为已有新业务写入后的通用业务回退。** 现有 `test_0012_backfills_versions_acceptances_tests_and_experts` 只验证旧 fixture 升→降→升，没有覆盖升级后新增业务写入的回退。

**建议**

二选一并写入发布设计：

- 真正的兼容扩展：分阶段约束、兼容读写/投影，旧版本退出后再变更状态语义和收缩。
- 经批准的停写迁移：停止旧写入端及轮询任务，排空或明确接管在途测试，备份后迁移并整体切换。区分“尚无新写入可退”与“已有新写入须恢复整套一致备份/执行专门逆向迁移”，不得宣传换镜像即可回退。

建议在无法保全新状态时给 downgrade 加明确的前置拒绝，避免自动化误执行造成静默丢失。回填前还应盘点重复活动测试、同一创意同版本多条 passed/delivered、非整数版本、缺 run_id 的历史成功记录；这些是待核数据条件，本次没有查询现网，不能断言现网已有此类脏数据。

### F06 · P1：市场资格检查没有贯穿审核和使用，已失去资格的主体仍可能公开成交

**位置**

- knowmart：`app/app/application/services/market.py:122–159`（改主体即变 pending/非实名）、`:225–242`（`_qualified`）。
- 同文件 `:395–405`、`:454–479`、`:972–1002`、`:1099–1138`。
- knowmart：`app/app/infrastructure/repositories/knowbots.py:265–305`；`application/services/knowbot_service.py:191–213`。

**证据与触发条件**

知识条目在提交审核时调用 `_qualified`，但运营批准与购买时不再核当前主体/许可证。主体此后修改资料会被置回 pending 且 `real_name_verified=False`，但原条目仍可 listed 并购买。许可证在提交后、批准前到期，也可被批准；购买只认 listed，需要等定时扫表才下架。

专家的运行检查也不一致：`licensed_publisher` 只有在“没有有效证照”时才核免证照类别及主体状态；只要还有有效证照，就不会要求主体 `review_status=approved` 和实名有效。新增的“改主体需要重新审”流程因此不能持续限制这一类专家。

**建议**

将“主体有效 + 类目所需证照有效”收为统一策略，至少在公开批准、实际召请/复制前核验；定时任务负责收敛展示状态与提醒，不独自承担使用授权。主体重审/撤销后的在途运行与新交易行为写清，避免有证类目反而绕过主体审核。

**补验建议**

提交后改主体再批准、上架后改主体再购买/召请、证照到期但 sweep 未运行、补新证后恢复。按许可类与免许可类分别覆盖。本条是代码授权一致性审查，不是法律合规结论。

### F07 · P2：买知识的复制与成交记录缺少可恢复的幂等操作

**位置**

- knowmart：`app/app/application/services/market.py:470–505`；`app/app/domain/market.py:205–212`。
- knowbase：`app/app/application/services/user_data_service.py:315–331`。

**证据与影响**

每次 HTTP 请求先生成新的 `trade_id`，顺序复制各项，再一次性写交易。复制幂等键是这个新 ID 加序号，`BuyIn` 没有请求幂等键。

两份资料第一份成功、第二份失败时，第一份已经进入买家知识库，而市场没有交易记录。重试会换 ID，第一份再复制一次。全部复制成功而写交易失败、或者响应丢失后重试，同样没有稳定恢复位置。这还可能令“不许转卖”检查失去交易依据：`_items` 的禁止集合来自 `bought_without_resale`，不完整成交的副本不在完整交易账里。

**建议**

先以客户端操作幂等键落 pending 交易及项目快照，记录逐项复制进度，固定 `transaction_ref`，同一操作重试恢复原交易。对账能定位无完成回执的复制，不要自动删除买家可能已开始使用的资料。参数不一致的同幂等键须拒绝；重复提交与用户主动再买一份应区分。

**补验建议**

第二项失败、交易落库失败、响应丢失、并发重试四类注入；均应收敛到一笔操作及确定的一组副本。

### F08 · P2：未上架版本结局仅尽力通知，丢包或乱序后不会可靠收敛

**位置**

- knowlab：`app/app/application/services/knowbot_experts.py:205–223`（`_tell_unlisted`）。
- knowmart：`app/app/infrastructure/repositories/knowbots.py` 的 `replace_unlisted`（先删除该名称全部记录，再写传入集合）。

**证据与影响**

本地决定成功后，调用整份替换接口；失败仅日志，没有持久重试或待同步状态。如果这是该名称最后一次决定，市场的空号原因可能永久缺失。两个不同版本先后决定、两个快照乱序到达时，旧快照还可能覆盖新快照；只补重试会放大乱序问题。

**建议**

按名称维护同步修订号，数据库事务内写 outbox/待同步记录，接收端拒绝旧修订覆盖；或改成按版本幂等更新并保留终态。提供失败重试与对账入口。符合约束 C-C9 的跨应用幂等、失败去向、对账要求。

这主要影响展示完整性，和 F01/F02 的读权限风险分开，不建议为此阻塞所有不相关功能。

## 二、需要明确决定或补实机证据的事项

### D01 · P1 候选／待议：Windows 补授 ACL 只核字符串路径，未核目录联接的实际目标

**位置**：link `agent/src/windowsSandboxRead.ts:25–37`、`:60–66`；`windowsBootstrap.ts:33–37`。

确定的源码事实：筛选用 `path.win32.resolve`、字符串前缀与首层目录黑名单；存在性用会跟随链接的 `fs.statSync`；授 ACL 前没有 realpath/reparse 检查。随后原路径交给 `icacls ... /grant CodexSandboxUsers:(OI)(CI)(RX)`。

因此，`C:\Users\u\bin` 是指向 `.ssh`、控制目录、codex-home 或 profile 外目录的 junction 时，路径筛选仍可能把它当作普通 PATH 目录；祖先目录是 junction 也一样。现有 `agent/test/windowsSandboxRead.test.ts` 用 `Set` 模拟 `isDirectory`，没有真 junction 的覆盖。

**尚未证明的部分**：本次没有在 Windows 上运行 icacls，不能把“目标 ACL 已被越界修改、敏感文件已可读”写成实测结论。它是授予持久 OS 权限前的一处已确认检查缺口，影响应在真实 NTFS 上单独核实。

建议先拒绝目标及祖先 reparse point，或使用可靠的实际目标身份核验，再对实际目标做相同排除；考虑检查与授予间被换路径的竞争，不要只额外做一次字符串 normalize。用专用无秘密 fixture 检查 junction、symlink、大小写及路径别名，验证授予前后 ACL 和实际沙箱读权限，并精确恢复 ACL。

另一个范围问题：`(OI)(CI)(RX)` 会向后代继承。当前只对 PATH 根做排除，不能由此推断其内部所有后代都可授权；建议明确支持的程序根，而非把用户 PATH 当作天然可信的授予清单。

### D02 · 待议：试行期专家补审“不通过”仍保留已上架状态

**位置**：knowlab `knowbot_experts.py:135–168`；`domain/knowbots/lifecycle.py:193–207`。

补审写 `review_approved=False`，但 `expert_stage` 优先看 `listed_at`，仍为 listed，也没有调用 knowmart.stop。`_tell_unlisted` 不会把它列入 rejected。

需要决定补审是历史说明还是有效准入门：若只补历史记录，应在接口/UI明确“不改变既有可用性”，避免用户误以为拒审已停用；若不通过必须停用，就按原停用流程先停 knowmart、再记本地，不要只调换 stage 判断顺序。SDD 目前不足以让我将这一项直接判成确定 bug。

### D03 · 待议：撤回测试同意是否同时终止已发出的运行授权

knowbase 的 `grant_test` 核 consent 未撤回，但读时 `Grant.active` 只核运行授权自身 revoked_at/expires_at，不再次核 consent。当前语义是撤回同意阻止新授权，已有授权直到单独撤销/到期仍可用。

请明确这一语义，并让 UI 使用准确说法。若要求撤回即停止读，需撤销由该 consent 签出的有效授权；不能只靠前端停按钮。F01 则无论采用哪种语义都要修，因为它连运行授权本身的撤销也会跳过。

## 三、对评审请求中设计问题的建议

1. **TTL 可以作为兜底，不能代替主动撤权。** 委托 7 天、会话 24 小时、测试按运行加等待计算本身不是这次发现的阻断点。交还失败应有可观测待重试状态；数据缓存必须服从当前授权。
2. **内容变化记“平台没能核”合理。** 不应把平台读不到钉住内容判成用户的业务验收失败；前提是暖缓存路径也能发现变化，且保留本次选定摘要与错误原因。
3. **迁移期间保留旧对象可以，但旧访问资格要窄。** 仅对应已批准历史版本，不能“knowbase 任何失败 → 旧路接管”。两份对象应有独立使用范围与退出条件。
4. **状态拆表方向合理，但不能让展示先于持久事实。** 独立 Test、Expert 和幂等 delivery_id 有利于追踪多次测试；试行补审语义、出站通知收敛、迁移回退仍须补齐。
5. **身份验令牌方向符合设计。** 此次读到的 verifier 先走签名/issuer/audience 验证，再以受配置限制的 azp 映射应用，没有发现通过普通请求字段直接改 owner×app 分区的路径；但没有复跑 Casdoor 交换、轮钥、错误受众和跨应用真机验收，不能把集成判为通过。
6. **实名与证件不作“合规已足够”的结论。** 源码存遮罩/摘要、私有照片、保留期限，只覆盖工程控制的一部分。应另外核接口授权、日志、备份中的副本生命周期及定时任务失败的告警；合规要求需单独确认，不在本次静态审查中代作法律判断。
7. **link 测试目录删除与远程 clone 有防线，但不是本次已通过的攻击验收。** 服务流对 runs 的路径形状、祖先链接、平台/开关有检查，clone 复用了 LocalProjects。尚未实测并发换祖先目录、断线清理、Windows 帮手及代理凭据链。不要把本报告作为这些项目的验收凭证。

## 四、建议的修复及复审顺序

1. 先修 F01/F02：让缓存、历史兼容都服从运行授权；补冷/暖缓存及拒绝路径。
2. 修 F03/F04：打通真实两个服务的删除与购买接入闭环，不只验 mock。
3. 明确 F05 的发布/回退方案，验证旧程序共存或明确停写；包含升级后的新业务状态，不能只用旧 fixture 升降。
4. 修 F06/F07：资格检查贯穿使用，复制成交可重试可对账。
5. F08 加持久同步与顺序保护；D01 做专用 Windows 权限验证，D02/D03 先定语义。
6. 最后再做跨应用真实用户链路：上传/购买 → 选择 → 签授权 → 测试/委托 → 撤权 → 删除；及专家通过/拒绝/停用的双端一致性。

本报告只提出处置建议；本次没有实施上述修复或补验。按评审约定只新增本文件，不做 Git 提交，由 Opus 统一收取。
