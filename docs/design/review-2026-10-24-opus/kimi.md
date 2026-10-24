# Kimi 评审：Opus 2026-10-23 至 10-24 的工作

读了：0037 的迁移 0012、knowbot_service / knowbot_experts / knowbot_board / 两端路由与视图、knowmart 的交付 / 停用 / 空号 / 市场服务与迁移 0007、0008、tpl 的令牌交换、knowbase 的用户令牌核验、knowbench 的钉住数据（pinned_data）与授权交还、link 的 129（runs/ 建删）与 168（windowsSandboxRead）实现。前端只抽查了视图层，没逐页看；测试没重跑，只看了覆盖面声明与关键用例名。

按轻重排。

## 一、要在发版前处理或拍板的

1. **knowmart 内部停用接口不校验来源是 knowlab**（knowmart-backend `app/application/services/knowbot_service.py` `stop(by_knowlab=True)`、内部路由 `POST .../versions/{version}/stop`）。`by_knowlab=True` 时完全跳过 `source_ref.startswith(KNOWLAB_REF)` 检查，而鉴权用的是与交付同一条 `knowmart:deliver` 服务关系。后果：持有这条关系（knowlab，或任何拿到同一凭据的）可以停用 knowmart 里**任意** knowbot 的任意版本，包括 knowmart 原生上架的。建议：`by_knowlab` 时仍要求 `bot.source_ref.startswith(KNOWLAB_REF)`，不是 knowlab 来源的回 403/404。

2. **0012 回填的两个隐含着网数据假设，建议发版前各跑一条核对 SQL**（knowlab-backend `app/alembic/versions/20261024_0012_knowbot_lifecycle.py`）：
   - `CAST(d.version AS integer)`：旧代码只写 `str(已交付数+1)`，我核过旧 `add_draft`，成立；但只要现网有一行 `version !~ '^\d+$'`（比如手工写进过 "1.0"），整个迁移直接失败。发版前跑：`SELECT id, version FROM knowbot_draft WHERE version !~ '^\d+$';`
   - 回填专家靠「通过 / 已交付的准专家版本号互不撞」。旧 `add_draft` 确实有「有待测 / 测试中 / 通过的不许建新稿」拦截（旧 `knowbot_service.py` 约 230 行），我核过，成立；但旧库若有过直接改数据，照旧会撞 `uq_knowbot_expert_version` 或部分唯一索引 `uq_knowbot_test_one_active`。发版前跑：`SELECT request_id, version, count(*) FROM knowbot_draft WHERE status IN ('passed','delivered') GROUP BY 1,2 HAVING count(*)>1;` 与 `SELECT request_id, count(*) FROM knowbot_draft WHERE status='testing' GROUP BY 1 HAVING count(*)>1;`（加 `run_id IS NOT NULL` 的 pending_test 会回填成 platform_error，不占活跃索引，无碍）。

3. **测试数据 sha256 不符时静默退回旧路**（knowlab-backend `knowbot_service.py` `_data_grant`）。绑定里任何一项对不上（没搬进 knowbase、owner 不符、**sha256 不符**）都整体不签授权、退回经 knowlab 旧路读——旧路不核 sha256。也就是说「数据被改过」这种本该报错的场景，会变成在改过的数据上照跑照判。过渡期「没搬完就退回」合理，但 sha256 不符与其它原因不同：建议这种情形至少记 warning、在测试报告里写明 fallback 原因；更稳的是 sha256 不符直接拒测。待议。

4. **审核通过 + 交付失败时审核接口回 200，靠回包里的 `delivery_error` 提示**（knowlab-backend `knowbot_experts.py` `review`）。服务端口径我认可（审核结论要留住、交付幂等可重试），但要确认管理端在回包带 `delivery_error` 且 `listed_at` 为空时给出的是显眼的「审核通过、上架失败、可重试」，而不是「完成」。前端我没逐页核，建议发版前在管理端点一次这个状态。另：`deliver()` 的 stage 校验在事务外，并发双击会双发 knowmart（交付单号幂等兜住，可接受，记一句即可）。

5. **身份证号摘要未加盐**（knowmart-backend `app/domain/market.py` `hash_id`：裸 `sha256(号码大写)`）。只存遮罩 + 摘要的方向对，但身份证号熵很低（地址码 + 生日 + 三位顺序 + 校验位），库泄后可离线穷举还原。建议改 HMAC 或服务端 pepper（放配置），查重语义不变。现在还没上线、没真实数据，改的成本就是现在最低。

## 二、值得改、不挡发版的

6. **knowlab `accept()` 不加 request 锁**（`knowbot_service.py` `accept`）：两个运营同时给同一版写受理单，第二个撞主键拿 500 而不是 409。加 `lock_request` 或把 IntegrityError 翻成 409。

7. **空号结局「尽力送达」可能长期缺**（knowlab `knowbot_experts.py` `_tell_unlisted`）：在 decide / review / deliver 事务提交后触发，进程崩在这中间，这一次的结局要等下一次事件才补发；若这个创意此后再无事件，knowmart 详情页就一直缺「没有上架」。建议加一个低频次对账（比如每小时把 declined / rejected 的整份重发一次；现在反正整份替换、幂等），或在 knowlab 侧记 `unlisted_sent_at` 扫未送达的。

8. **委托 / 会话授权的孤儿兜底**：knowbench 靠 runner 周期扫 `grants_to_release` 交还；runner 崩溃或委托记录异常时授权留到 TTL（委托 7 天、会话 24 小时）自己失效。口径可接受，但建议确认周期扫的查询覆盖「委托已结束但 `grant_released_at` 为空」的全部情形（包括委托被删的）；knowlab 测试授权 `_revoke` 失败只 log 一行，建议发版后盯一阵这个告警量。

9. **性能**：栏目与 counts 全量取、内存分组，`answered_by_user` 逐个查——Opus 已自标。补一句：`my_counts` 是每次打开页面都走的，建议最先把 counts 下推成 SQL 聚合，分组可以后一步。

10. **knowmart 证件照片存库内 LargeBinary（≤5MB）**：admin-only 读取 + NO_STORE + 一年后清理都有，可以；量大了挪对象存储，不挡这期。

## 三、我核过、认为成立的（回 Opus 的「请重点看」）

- **0037-1 回填依赖的旧规矩**：旧 `add_draft` 确实有「进行中不许建新稿」拦截（见上 2），版本号生成规则单调，通过 / 已交付不撞号在代码层成立；剩下的只是现网数据核对（见 2）。`downgrade` 只恢复上架了的、交付失败的审核结论会丢——作为紧急回退可以接受，建议在 SDD 里把「回退丢什么」写一句。
- **0037-2「通过还没交付」回填成「已交回」**：同意。旧 web 端一通过就展示且能点「要这一版」，回填成待交回反而改变用户已见状态；`user_accepted` 只在 `delivery.accepted_at` 存在时置 true，也对。发版后抽查一例确认。
- **0037-4 停用顺序（先 knowmart 后 knowlab）**：重试安全（knowmart 再停幂等 204，knowlab 侧 `stage_of` 仍 listed 可重入）。空号「整份替换」天然对账，方向对；缺的是触发频率（见 7）。
- **0037-5 同意文字改了、版本没升**：同意不升（意思不变、避免全员重签）。建议在 0042 或 0037 里把「文字改了、版本没升、为什么」记一句，免得日后审问。
- **0037-8 权限**：路由层核过——受理、孵化、请用户审核、核出处、判定卡住、交回、运营审核、重试交付、停用都挂 `require_knowlab_release`，发起测试 / 刷新挂管理端基本权限，与说法一致。给用户看的视图确实不带 run_id / 规则名 / 谁做的（`knowbot_views.py` 里 admin 才带）。
- **0042-1 令牌交换与核验**：tpl 的 `exchange_token` 走 RFC 8693、400/401 翻成 `reauth_required`、其它 5xx 翻成平台故障，对；knowbase 的 `UserTokenVerifier` 验签名 / iss / aud / exp / iat、按 `azp` 认应用、只认登记的三家、`tokenType` 非 access-token 拒，对。配置项（audience、apps_json）发版时要配齐已在第六节。
- **0042-3 钉住与核对**：取到字节核 sha256、对不上报「数据被改过」、验收记「平台没能核」而不是判失败——口径对，避免用户数据问题误判专家。
- **129**：只认 Linux、只对 `<根>/runs/<名字>` 一层、名字白名单不含分隔符、不跟链接、删不存在算成功，好。inspect 与 rm 之间有 TOCTOU，由「rm 不跟链接」兜住，测试机上可接受。
- **168（windowsSandboxRead.ts）**：范围（PATH 与用户程序目录中在用户目录之下的）、排除清单（与 Codex 的 USERPROFILE_ROOT_EXCLUSIONS 一致，另排 link 私有目录）、先查后授、只授 (OI)(CI)(RX)，都对。两点提醒：(a) `sandboxGroupCanRead` 解析 icacls 输出依赖组名字符串与 (OI)(CI)(RX) 符号，中英文系统都成立，但「已有授权但缺 CI」这类中间态建议在所有者 Windows 上真机回归一次；(b) 授读的 PATH 目录若同时是某工具的配置目录，沙箱命令也能读到那些配置——可接受，记一句。

## 四、没核的

- 两个前端各页面（只抽查了 knowlab 的视图裁剪）；回包「多字段不算错」的前端改动没看实现。
- knowbench 聊天 / 工作选用云端知识库的会话授权改选换签（57ab32e）没细看。
- 0018 的定时活（资质到期、照片清理）只核了存在性，没逐条过。
- 测试都没重跑；以 Opus 报的（knowlab 597、knowmart 492、knowbench 网页 336 等）为准。
