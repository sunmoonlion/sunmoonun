# 专家团与长期 Agent：四家产品对照（opus）

> Opus 以 qwen 身份 2026-11-09 写。所有者：「你完全独立地查第一手资料，写出你自己的版本」。同目录 `agent-team-luna.md` 是 luna 的版本，本文写作时没有读它的正文。
> **资料范围**：只用厂商自己的文档、公告和产品页，2026-11-09 读取；第三方文章、博客、百科一概不用。厂商页面没写的，照实写"文档没说"，不拿推测补。第六节是我按我们的架构做的判断，和前五节的事实分开。

## 一、四家各是什么

| 产品 | 厂商自己的一句话 | 上线 |
| --- | --- | --- |
| **dots**（OpenAI） | "an always-on agent that keeps work moving"——一个常驻的个人 Agent | 文档写"逐步开放"，没写日期 |
| **Grok Bot**（xAI） | "your team of always-on agents"——一组常驻 Agent，像队友一样干活 | 2026-08-11（发布页） |
| **WorkBuddy 专家 / 专家团**（腾讯） | 专家是"角色切换"机制，"人设 + 方法论 + 工具链"；专家团由多位专家分工协作、团长统一调度 | 文档没写日期 |
| **Muse**（Meta） | "a personal AI agent. It doesn't just answer questions, it actually does the work." | 2026-09-08（Meta 新闻稿） |

四家里，**真正做"多个 Agent 组队"的是 Grok Bot 和 WorkBuddy**；dots 和 Muse 都是"一个人一个常驻 Agent"，dots 能把活分给后台 Agent，Muse 只有一个管上网的哨兵 Agent。

## 二、逐家要点

### 1. OpenAI dots

- **形态**：每人一个，起名、选外观，得到一个 `@名字-dot` 的称呼；跑在云端它自己的电脑和浏览器上，用户设备关了也继续干。
- **派活**：ChatGPT 桌面端、手机端（含语音通话），Slack（私信或在频道 @它）、Teams；美国 Pro 用户可以发短信（测试中）。可以定时（定什么、何时、何时结束、结果送哪），也可以盯事件，但"把它加进频道不等于开始盯"，要明说盯什么。
- **一个 dot 内部怎么分工**：它能同时担几件事、来回切换；"can split work among background agents that report back to it"——把活拆给后台 Agent，后台的向它汇报；也能把活交给 ChatGPT Work 或 Codex，开云端任务或本地任务。**文档没有描述多个 dot 之间怎么协作**，没有"领队""交接""共享工作区"这类说法。
- **记忆**：它自己记一份关于偏好、决定、进行中工作的笔记，加上相关的 ChatGPT 记忆；换个地方跟它说话不会重置。文档特别说明："Using information doesn't grant permission to share it with another audience"——知道了不等于能讲给别人听。
- **审批**：动作执行前有一道自动审查，对照你的指示、权限、自定义规则和内置安全要求，决定"能做、要你批、还是要你自己动手（比如改密码）"。自定义规则有四档：不问就做、你说了才做、做前先问、交给你做。规则"不授予访问权限、不覆盖安全要求、不免掉必需的确认"。"让它起草回复不等于授权它发送"。
- **停下**：暂停只停当前主任务，不停已经分出去的任务，也不取消定时任务；"停下不撤销已经做完的动作"。
- **完成不等于成功**：多处提醒要复核结果，"Fluent writing or a confident summary is not enough to establish that a task succeeded"。
- **费用**：Pro、Business Premium 的用户和 dot 聊天不计入 ChatGPT 用量；它交给 Work 或 Codex 跑的任务计入那两个产品的用量。

### 2. xAI Grok Bot

- **形态**：一个账号可以有好几个 Bot，每个有自己的名字、头像、对话、记忆、定时例程、附件；同一用户的 Bot **共用一台**常驻云电脑（浏览器、文件系统、终端）。有一个**主 Bot**："main point of contact. It checks in on its own and coordinates your other Bots"。发布页的说法是"chief-of-staff Bot 管着几位专项 Bot（收件箱、报销、招聘、修 bug）"。
- **怎么建**：建好后在第一条消息里说清它的职责、能用的来源、审批界限，让它记住，再给一件真活。个人 Bot 没有设置页，改行为就在对话里跟它说。"一件事需要长期有人管时，才给它单独一个 Bot"。
- **Bot 之间怎么交接**：一个 Bot 可以给另一个 Bot 发异步消息，对方醒来处理、晚些回复，交接在对话里看得见。文档的建议："Assign one owner per stage"——每个阶段只定一个负责的，并行交接会重复干活、刷屏。
- **群聊**：2 到 6 个 Bot 一个群；你正常说话，让群里的 Bot 自己决定谁回，或者用 @ 指名。审批请求、登录或密钥请求、邮件和 Slack 草稿**不进群**，只发给本人。
- **例程**：定时（两次至少隔 5 分钟），或由事件触发（Slack 消息、GitHub 等事件、发到 Bot 自己邮箱的信、Webhook）；一个 Bot 最多 50 个例程，每小时总共最多 300 次运行。
- **审批**：Auto Review 在每个命令、应用操作、电脑动作执行前先查，"大多数动作自己就过了"；要你点头的弹审批卡等你。可以写自定义规则（"先问我"或"自动允许"）。文档原话："Only your own messages count as instructions"——网页上、别人邮件里写的话，不算你的指令；也坦白"这些检查降低风险，不能消除"。
- **身份与凭据**：Bot 没有自己的账号和凭据，"做不了你做不了的事"；登录信息放进 Vault，Bot 用但看不到。
- **共享 Bot**：在团队里像共享文档一样共享一个 Bot（不复制），所有者定谁能用；协作者能和它聊天，管理者还能改它的指令、技能、记忆、应用。每个人和它的对话都是私密的，所有者也看不到。它用的是所有者接的应用和密钥；要用你自己的账号时先问你。在 Slack 线程里，只有提问的人能点审批卡。
- **模板与市场**：Bot 可以"创建副本"发布成模板，拿到的人得到自己的副本，不带原主人的电脑、登录和历史；发布前要自己删掉密钥、内部网址、客户数据。有一个 Bot 市场页，列着各个 Bot 的名字、作者、一句话介绍和"Add"按钮，有"From Grok Bot Team"分类和"Featured"区；**市场页没写定价、评价、审核、怎么上架**。
- **团队与企业**：管理员能看到所有 Bot、改访问范围、按组自动加到成员侧边栏；有能力开关（云端委派、Agent 邮箱、在成员本机执行等）、数据保留期（30 到 365 天）、动作记录（企业版）。这些后台在 Cursor 的控制台里，团队成员用 Cursor 账号登录。
- **费用**：每个 Bot 的回复都算用量，"包括群里的回复和 Bot 之间的消息"，所以"Bot 越少，回复越少"；共享 Bot 回谁就算谁的用量。

### 3. 腾讯 WorkBuddy

- **专家**："人设 + 方法论 + 工具链"。专家本身不主动拿系统权限，只处理用户主动给的对话和上传的文件；配了技能（Skill）或 MCP 才会在用户授权下间接访问文件或外部服务。
- **专家团**：多位专家分工、团长统一调度；团长"自动拆解任务、分配给成员、执行并返回完整结果"，"并行执行、整合交付"。
- **专家团在开发侧怎么写**（开放平台）：一个主理人（团长）定义文件加若干成员定义文件，可选共享技能。关键规矩：
  - 建团"必须且只能由主理人执行"；
  - 成员产出必须由成员本人输出，主理人只编排和汇编；
  - **成员之间不直连**，跨成员的信息都经主理人转交；
  - 每个阶段结束，把完整产出原文交给下一阶段的成员；
  - 主理人正文里写团队成员表、标准工作流程（SOP）和协作规则。官方示例是一个五阶段的交易团队：数据采集（并行）→ 多空辩论 → 交易决策 → 风险评估（并行）→ 最终报告。
  - 工具："开发者不可自行添加 tools，所有工具权限由系统统一分配"；只有主理人能用派活和发消息的工具。
- **项目**：团队协作的容器，里面放指令（任务继承）、连接器（公共授权共享一个账号，个人授权只存本地、协作任务里用不了）、专家与技能、资产（默认 5 GB）、任务；任务可以"分享"（多人进同一会话）或"流转"（带全部上下文复制到新会话交给别人）；项目计划有看板、列表、表格、甘特、日历视图。任务的对话花的是任务所有者的积分。
- **费用**：专家团积分消耗"通常为单专家的 3–5 倍"。
- 详见 [workbuddy-opus](workbuddy-opus.md)。

### 4. Meta Muse

- **形态**：一个人一个，像给人发消息一样用（Muse 应用或 WhatsApp）；关了应用照样在后台干，有变化或要审批时回来找你。
- **执行环境**：跑在 **Muse Secure VM**——每人一台云上专用电脑，带自己的浏览器，装着 Muse 和接入服务的数据与凭据，"别人的 Agent 碰不到"。同一台机器上另有一个**哨兵 Agent（Sentinel）**，在系统层和 Muse 隔开："Nothing Muse does reaches the internet unless the Sentinel approves it"。计划推出只有用户持钥的加密版 VM。
- **接入**：用户选接哪些应用、给多少权限；邮件可以选"只读"或"也能代发"。付款经 Stripe 的 Link 生成一次性卡号。Connect 2026（9-23）后又加了：自己的邮箱地址；Mac 版，经许可能操作 Mac 上的应用，本机应用的权限分「关、只读、读并交互」三档，删除的文件进废纸篓、能恢复；接入沃尔玛、百思买、Notion、GitHub、Box 等。小企业版接 Shopify、QuickBooks、Stripe、Slack、Canva 等十几家。
- **审批**："checks with the person before sensitive actions like sending an email or making a purchase"；"Nothing publishes, sends, or spends without your approval, and you can undo actions"；给完整的审计记录：做过什么、打算做什么。
- **隐私**：对话和 VM 里的数据不给 Meta 的广告系统；可以选择不拿来训练；Muse 看不到密码和支付方式。
- **多 Agent**：官方材料只提到哨兵；**没有面向用户的多 Agent 或专家团**。
- **费用**：大部分功能免费，另有订阅。

## 三、对照表

| | dots | Grok Bot | WorkBuddy 专家团 | Muse |
| --- | --- | --- | --- | --- |
| 几个 Agent | 一个，能分活给后台 Agent | 多个，有主 Bot | 一个团长 + 若干成员 | 一个（加一个哨兵） |
| 谁协调 | dot 自己 | 主 Bot / chief-of-staff；群里 Bot 自己定谁回 | 团长（主理人）按 SOP | — |
| 成员怎么交接 | 后台 Agent 向 dot 汇报 | Bot 之间直接发异步消息；每阶段一个负责的 | **不直连**，全经团长转交，阶段间交完整原文 | — |
| 组队写在哪 | — | 用户在对话里说 | 开发者写主理人与成员定义文件 | — |
| 执行环境 | 云端自己的电脑与浏览器；也能用你连上的本机 | 每人一台云电脑，几个 Bot 共用 | 文档没写（客户端与项目） | 每人一台隔离 VM |
| 记忆 | dot 自己的笔记 + ChatGPT 记忆 | 每个 Bot 各自；少量事实跨 Bot 共享 | 项目指令、资产 + 个人记忆 | 记住要紧的，可让它忘 |
| 审批 | 自动审查 + 四档自定义规则 | Auto Review + 自定义规则；审批卡不进群 | 连接外部服务时弹授权卡；文档没写执行中审批 | 敏感动作先问；可撤销；审计记录 |
| 身份 | 用你连上的账号与权限 | 用你的；共享 Bot 用所有者的、要用你的先问 | 公共授权或个人授权 | 你授权的应用；凭据它看不到 |
| 团队共享 | 工作区管理员管 | 共享 Bot（不复制）、模板（复制） | 项目；分享专家给人是副本 | 文档没写 |
| 市场 | 文档没写 | Bot 市场页（无价格、评价、审核说明） | 专家中心（行业分类、推荐）；开放平台审核上架 | 文档没写 |
| 怎么计费 | 聊天不计（部分套餐）；委派的任务另计 | 每条回复都计，含 Bot 之间 | 积分；专家团 3–5 倍 | 大部分免费 + 订阅 |

## 四、四家共同的做法

1. **常驻、后台跑，要人时才回来**：四家都是这样。用户看到的是"它在干、要你决定什么"，不是一问一答。
2. **执行前审批，审批不等于验收**：动作前过一道（自动审查、Auto Review、哨兵、授权卡），敏感动作要人点头；同时都提醒"完成不等于做对"，结果要复核。
3. **别人的话不是你的指令**：Grok Bot 写得最明白；dots"知道了不等于能转述"；Muse 用哨兵管上网。
4. **凭据不进模型**：Vault、凭据库、一次性卡号，Agent 用得到、看不到。
5. **停下不等于撤销**：dots、Grok Bot 都明说已经做了的不会回滚。
6. **多 Agent 一定有一个协调者**：Grok 的主 Bot、WorkBuddy 的团长；dots 是 dot 自己管后台 Agent。
7. **多 Agent 更贵，厂商都明说**：WorkBuddy 3–5 倍；Grok"Bot 越少，回复越少"。

## 五、两种组队方式的差别

| | Grok Bot：长期队友 | WorkBuddy：一次任务的班子 |
| --- | --- | --- |
| 团是什么 | 用户自己养的几个长期 Bot，各管一摊，有记忆、有例程 | 开发者打包的一个产品：团长 + 成员 + SOP，用户召唤一次跑一次 |
| 谁定分工 | 用户在对话里定，主 Bot 协调 | 开发者写死在主理人的 SOP 里，团长按 SOP 拆 |
| 交接 | 成员之间直接发消息 | 成员不直连，全经团长；阶段间交完整原文 |
| 适合 | 长期、反复的个人或团队事务 | 有固定流程的复杂任务（研究、报告、交易分析） |

## 六、对我们的启示（我的判断，不是厂商的说法）

对照我们的架构：专家归作者，投资逻辑与数据来自用户，跑在用户自己的沙箱里、用用户的 key，平台只做工程化与测试。

1. **我们的专家团更像 WorkBuddy，不像 Grok**：我们的专家是作者孵化、上架的产品，专家团也应当是作者定的"团长 + 成员 + 协作规则"，用户请一次跑一次；Grok 那种"用户自己养长期 Bot"是另一种产品。所有者 10-28 说的"演变成 workbuddy 的专家团"也是这个方向。
2. **团长的协作规则就是作者的方法**：WorkBuddy 把 SOP 写在主理人正文里，由开发者定。对我们来说，"怎么拆、谁先谁后、谁的成果交给谁"是作者的判断，应该和单个专家的"规划原文"一样，由作者写、随版本冻结，平台不替作者编排。
3. **成员不直连、全经团长转交，适合我们**：所有交接都有一个经手人，产出原文整份交下一阶段，好留痕、好验收，也绕开了"成员之间传的产出算什么"这类问题（[请专家与执行](../专家使用方案/opus/请专家与执行.md) 第 9.3 节第 6 条）——成员交给团长的，就是团长这一轮的输入，照现有的计划绑定、按确切版本取。
4. **每阶段一个负责的、审批不进群**：Grok 的两条经验可以直接用：并行阶段每段只有一个成员负责；审批、数据确认、费用只发给请专家的本人。
5. **成员各自的数据，还是"谁的数据谁挑"**：团里每位成员要用户的数据，都走同一个定数据；作者自带的数据各随各的成员版本。不能因为组了团就合并授权。
6. **费用要事先说清**：多成员、多轮，WorkBuddy 自己说 3–5 倍。我们是用户出模型费，请专家团前要给一个"大概几倍"的提示，跑的时候照现在的花费实时显示、随时能停。
7. **市场上卖的是团的版本，团里钉成员的版本**：Grok 的模板是"复制一份"，WorkBuddy 的分享也是副本；我们的专家团上架时，应当钉住每位成员的确切版本，和单个专家钉方法版本一个道理，成员出新版不自动改团。
8. **"完成不等于成功"要落到验收上**：四家都只是提醒用户复核；我们有确定性验收和成果指纹，团长整合交付也要过验收，不能只凭团长说"做完了"。

## 七、资料来源（2026-11-09 读取）

**OpenAI**
- [Meet dots](https://learn.chatgpt.com/docs/dots)
- [dots：Tasks and memory](https://learn.chatgpt.com/codex/dots/tasks-and-memory)
- [dots：Controls](https://learn.chatgpt.com/codex/dots/controls)
- [Working with agents](https://learn.chatgpt.com/codex/working-with-agents)

**xAI**
- [Introducing Grok Bot](https://x.ai/news/introducing-grok-bot)
- [Grok Bot overview](https://docs.x.ai/grok-bot/overview)
- [Create and manage Bots](https://docs.x.ai/grok-bot/bots)
- [Message and collaborate](https://docs.x.ai/grok-bot/chat-and-collaboration)
- [How Grok Bot works](https://docs.x.ai/grok-bot/how-grok-bot-works)
- [Skills and routines](https://docs.x.ai/grok-bot/skills-routines-and-automations)
- [Use the computer and apps](https://docs.x.ai/grok-bot/computer-and-apps)
- [Approvals, security, and privacy](https://docs.x.ai/grok-bot/approvals-security-and-privacy)
- [Shared Bots](https://docs.x.ai/grok-bot/shared-bots)
- [Teams and enterprises](https://docs.x.ai/grok-bot/teams-and-enterprises)
- [Bot marketplace](https://x.ai/bot/marketplace)

**腾讯**：见 [workbuddy-opus](workbuddy-opus.md) 第八节。

**Meta**
- [Introducing Muse（Meta 新闻稿，2026-09-08）](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)
- [The Biggest News From Connect 2026（2026-09-24）](https://about.fb.com/news/2026/09/the-biggest-news-from-connect-2026/)
- [Muse for Small Business](https://muse.ai/business)
- [Meta Connect 2026: Everything We Announced（meta.com）](https://www.meta.com/blog/meta-connect-2026-everything-we-announced/)
- [How Muse works with files and apps in your Mac（Meta 帮助中心）](https://www.meta.com/help/artificial-intelligence/1126304576638594/)

OpenAI 帮助中心（help.openai.com）拒绝抓取，没有绕过，dots 的资料都取自 learn.chatgpt.com。
