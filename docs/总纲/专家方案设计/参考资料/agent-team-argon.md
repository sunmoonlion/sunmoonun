# 四款主流智能体与多智能体协作产品一手架构调研（argon 独立版）

> **调研声明**：本报告由 `argon` 独立完成，100% 基于对 **OpenAI**、**xAI / Cursor**、**腾讯云 WorkBuddy**、**Meta Superintelligence Labs (MSL)** 四家厂商官方一手技术文档、管理员指南、API 规范与官方发布博客的直接抓取与核查撰写，完全不参考、不引用任何其他助手的整理文稿。
> **事实与判断分离原则**：凡属于官方文档明确记载的事实均附带一手官方 URL；官方文档未公开的底层实现细节均明确标注“官方未披露”；所有面向本项目的启发与对比均归入独立的“argon 架构判断”章节。

---

## 一、 一手官方信息源清单

### 1. OpenAI dots（ChatGPT Personal & Workspace Agents）
- [Manage dots permissions and capabilities | ChatGPT Learn](https://learn.chatgpt.com/docs/enterprise/dots-admin-guide)（及 `.md` 原文）
- [Safety and security in dots | ChatGPT Learn](https://learn.chatgpt.com/docs/enterprise/dots-security)（及 `.md` 原文）
- [Managing dots in ChatGPT workspaces | OpenAI Help Center](https://help.openai.com/en/articles/20001554-managing-dots-in-chatgpt-workspaces)
- [Getting started with your dot | OpenAI Help Center](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)

### 2. xAI Grok Bot（SpaceXSI / Cursor Grok Bot 体系）
- [Grok Bot Official Product Page](https://x.ai/bot)
- [Skills and routines | SpaceXSI Docs](https://docs.x.ai/grok-bot/skills-routines-and-automations)
- [Work with Grok Bot | Cursor Docs](https://cursor.com/docs/grok-bot/work)（及 `.md` 原文）
- [Grok Bot for Teams and Enterprise | Cursor Docs](https://cursor.com/docs/grok-bot/teams)（及 `.md` 原文）
- [Grok Bot Security | Cursor Docs](https://cursor.com/docs/grok-bot/security)（及 `.md` 原文）
- [Subagents | Cursor Docs](https://cursor.com/docs/subagents)（及 `.md` 原文）

### 3. 腾讯 WorkBuddy（腾讯云产品代号 `1831` / `1316`）
- [WorkBuddy 产品简介（1831/134384）](https://cloud.tencent.com/document/product/1831/134384)
- [WorkBuddy 专家与专家团（1831/134393）](https://cloud.tencent.com/document/product/1831/134393)
- [WorkBuddy 企业控制台 - 专家管理（1831/134421）](https://cloud.tencent.com/document/product/1831/134421)
- [WorkBuddy 项目协作、任务流转与计划看板（1831/138797）](https://cloud.tencent.com/document/product/1831/138797)
- [CodeBuddy / WorkBuddy Agent Teams 协作机制（1831/137017）](https://cloud.tencent.com/document/product/1831/137017)
- [WorkBuddy Managed Agents - Agent Manifest v2.0 字段说明（1831/139534）](https://cloud.tencent.com/document/product/1831/139534)
- [WorkBuddy 技能（1831/134432）](https://cloud.tencent.com/document/product/1831/134432)、[连接器（1831/134525）](https://cloud.tencent.com/document/product/1831/134525)、[默认权限与安全沙箱（1831/134401）](https://cloud.tencent.com/document/product/1831/134401)
- [WorkBuddy 版本说明（1831/134332）](https://cloud.tencent.com/document/product/1831/134332)、[计费说明（1831/134334）](https://cloud.tencent.com/document/product/1831/134334)、[积分说明（1831/134339）](https://cloud.tencent.com/document/product/1831/134339)

### 4. Meta Muse（Meta Superintelligence Labs）
- [Introducing Muse Spark: Scaling Towards Personal Superintelligence | Meta AI Blog (2026-04-08)](https://ai.meta.com/blog/introducing-muse-spark-msl/)
- [Introducing Muse Spark 1.1 & Meta Model API | Meta AI Blog (2026-07-09)](https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/)
- [Meta Newsroom: Introducing Muse Spark](https://about.fb.com/ja/news/2026/04/introducing-muse-spark-meta-superintelligence-labs-first-model-built-to-prioritize-people/)

---

## 二、 四款产品的一手事实深度拆解

### 2.1 OpenAI dots：面向个人持久代理与跨线程任务委派的云端工作空间体系

#### （1）核心定位与运行形态（官方事实）
根据 [dots-admin-guide](https://learn.chatgpt.com/docs/enterprise/dots-admin-guide) 与 [dots-security](https://learn.chatgpt.com/docs/enterprise/dots-security)：
- **定义**：`dot` 是 ChatGPT 中的个人持久化智能体（personal agent that can keep working between conversations），能够在会话关闭后持续跟进工作、调用已授权的外部应用连接（Connected Apps），并将重型子任务委派给 **ChatGPT Work** 或 **Codex** 线程执行。
- **底层基础设施**：`dot` 构建在与 **ChatGPT Work Cloud** 相同的托管云端计算机基础设施（cloud computer）之上，支持跨会话保存云端计算机快照（preserve cloud computer snapshots across sessions），使任务无需每次从零初始化。
- **模型底座**：[dots-security](https://learn.chatgpt.com/docs/enterprise/dots-security) 明确披露 `dots` 背后的模型属于 **GPT-6 家族**（文档原话：*OpenAI trains models in the GPT-6 family to refuse harmful requests and resist malicious instructions hidden in emails, files, or web pages*）。

#### （2）多智能体/跨组件委派与主动研究机制（官方事实）
- **主从委派（Delegation to Work / Codex）**：`dot` 本身扮演个人常驻总控代理角色，当遇到专项文档分析或软件工程任务时，可向 **ChatGPT Work** 或 **Codex Cloud** 发起异步委派；被委派的 Codex 任务遵循 Codex Cloud 自身的安全策略与所选运行环境权限，且按标准费率独立计费。
- **主动研究（Proactive Research）**：[dots-security](https://learn.chatgpt.com/docs/enterprise/dots-security) 披露了 `dot` 区别于传统被动问答的关键特性——**Proactive Research**。无需等待用户发起新指令，`dot` 可主动轮询已授权的关联应用以发现与当前工作相关的更新，并保存私有笔记（private notes）。
  - **主动研究的安全降权**：官方文档明确规定，在 Proactive Research 阶段，`dot` 的研究工具**被硬性禁止**直接向他人发送消息、禁止修改关联应用中的内容、禁止操控浏览器或计算机；只有用户显式调度的任务才按完整动作权限规则执行。

#### （3）渠道集成与身份隔离（官方事实）
根据 [dots-admin-guide#3-configure-communication-channels](https://learn.chatgpt.com/docs/enterprise/dots-admin-guide)：
- 支持接入 **Slack** 与 **Microsoft Teams**。以 Slack 为例，官方提供两种正交的接入模式：
  1. **通过 Plugin 复用成员自身 Slack 账号**：成员在 ChatGPT 内与 `dot` 对话，`dot` 借用成员的 Slack 连接读取/操作，不拥有独立的 Slack 机器人身份。
  2. **赋予 `dot` 独立的 Slack 身份（Slack identity）**：所有人在频道中可见 `dot` 的发言，其所有者可在 Slack 中直接私聊或 `@` 提及自己的 `dot`。
- **严格的个人所有权边界**：个人 `dot` 严格绑定其所有者（Owner）授权的账户凭证，工作空间的其他成员在公共频道提及他人 `dot` 不会获得对该 `dot` 的控制权。

#### （4）企业权限管控、Auto-review 与计费模式（官方事实）
- **RBAC 四大核心权限开关**（Admin Console > Permissions）：
  1. `Use dots`：是否允许成员创建和使用个人 `dot`。
  2. `Add dots to Slack and Microsoft Teams`：是否允许将 `dot` 接入外部 IM。
  3. `Allow local computer access`：独立显式开关（Opt-in），控制是否允许 `dot` 突破云端计算机、直接操作员工本机（FedRAMP、EKM 等受限工作空间不支持本机访问）。
  4. `Use custom rules for dots`：是否允许成员为自己的 `dot` 编写自定义规则。
- **云端计算机三级能力开关**（与 Work Cloud 及团队自动化共享）：`Use a browser`（使用云浏览器）、`Allow network access`（代码与 Shell 联网）、`Allow computer use`（桌面交互）。即使全部关闭，`dot` 仍可起草内容并调用被允许的 Connected Apps。
- **Auto-review（自动安全审查拦截器）**：在 `dot` 执行对外发送邮件、共享简报等具有外部影响（consequential actions）的操作前，独立的 **Auto-review** 机制会对照所有者指令、Custom Rules 及安全要求审查接收方与内容，可直接阻断或强制转人工确认；**`dot` 自身无法关闭必需的 Auto-review 检查**。
- **预览与计费时间表**：面向 ChatGPT Enterprise、Edu、Healthcare 工作空间开放预览，预览期免费；**2026 年 11 月 18 日**起默认开启并开始计费，企业可选择按工作类型固定费率（flat rate）或按消耗量（consumption）付费，委派给 ChatGPT Work 或 Codex 的子任务按各自标准费率另行计费。

---

### 2.2 xAI Grok Bot：基于单用户共享 Firecracker MicroVM 的多角色常驻机器人矩阵

#### （1）核心定位与运行时架构（官方事实）
根据 [cursor.com/docs/grok-bot/work](https://cursor.com/docs/grok-bot/work) 与 [cursor.com/docs/grok-bot/teams](https://cursor.com/docs/grok-bot/teams)：
- **产品形态**：Grok Bot 是运行在云端的计算机操控智能体（computer-use agent），桌面端（macOS/Windows）与移动端（iOS）均为负责聊天、审阅与审批的**薄客户端（thin clients）**。
- **虚拟化隔离底座（极为关键的架构事实）**：
  - **跨用户硬件级隔离**：每个用户在云端分配一台专属的持久化 **Firecracker microVM**（具备独立内核、内存与虚拟设备），不同用户之间硬件级完全隔离。
  - **同用户多 Bot 共享单机（Shared Computer per User）**：[teams.md#how-users-are-isolated](https://cursor.com/docs/grok-bot/teams) 明确指出，**同一用户名下创建的所有个人 Bot 共享同一台 Firecracker microVM**（*all of that user's Bots share one computer, and Bots isolate personalities and workspaces, not compute*）。因此，一个 Bot 在云端电脑上产生的文件或登录态对同一用户的其他 Bot 天然可见，从而实现了零拷贝的文件交接，但也要求对需要强凭据隔离的负载使用独立账号。
  - **共享机器人例外（Shared Bots）**：当某个 Bot 被设为团队共享（Shared Bot）并在 Slack 频道、线程或群聊中被调用时，该 Shared Bot 运行在**它自己独立的一台云端计算机**上；而在成员个人私聊或 Slack DM 中调用 Shared Bot 时，默认仍在调用者本人的云端计算机上运行并消耗调用者额度。

#### （2）多 Bot 协同（Group Chats & Asynchronous Handoffs）与 Subagents（官方事实）
Grok Bot 体系同时支持两层多智能体协作：
1. **常驻角色层（Named Bots & Group Chats & Handoffs）**：
   - 用户按职责边界创建具名常驻 Bot（如 `Talent Scout`、`Expense Manager`、`Bug Reproduction`），每个 Bot 维护独立的对话历史、持久规则（Lasting rules）与工作记忆。
   - **群聊协同（Group Chats）**：用户可将多个具名 Bot 拉入同一个群聊，通过 `@Researcher`、`@Writer`、`@Reviewer` 在同一条指令中编排多角色流水线。
   - **Bot 间异步交接（Hand work between Bots）**：[work.md#hand-work-between-bots](https://cursor.com/docs/grok-bot/work) 记载，一个 Bot 可以向另一个 Bot 发送异步消息，唤醒目标 Bot 处理并在稍后回复，整个交接链路在对话流中对人类可见。官方文档特别给出了工程最佳实践：**每个阶段只指定唯一负责人（single owner at each stage），避免并行交接导致重复劳动与噪音**；且 Bot 到群聊的交接消息仅限纯文本，如需传递图片需点对点直接发给目标 Bot。
2. **会话内子代理层（Subagents）**：
   - 根据 [cursor.com/docs/subagents](https://cursor.com/docs/subagents)，主代理在单轮执行中可通过 `Task` 工具派生拥有**独立上下文窗口（clean context window）**的 Subagent，分为 **Foreground（前台阻塞等待结果）** 与 **Background（后台异步并行）** 两种模式。
   - 内置两类专门解决“中间过程噪音撑爆主上下文”的专用子代理：**`Explore`**（使用更快的模型并行执行 10+ 次代码库检索，只向主代理返回摘要）与 **`Browser`**（通过 MCP 操控浏览器，过滤庞大的 DOM 快照与截图噪音）。
3. **跨层委派（Cloud Agents）**：Grok Bot 可将重度编程任务委派给独立的 **Cloud Agents** 容器执行，企业管理员可控制是否允许派生（spawning）。

#### （3）能力沉淀：Skills 与 Routines（官方事实）
根据 [docs.x.ai/grok-bot/skills-routines-and-automations](https://docs.x.ai/grok-bot/skills-routines-and-automations)：
- **Skill（技能）**：可复用的标准化作业指令集，明确包含 6 要素：**何时使用（When to use）、所需输入与权限（Required inputs and access）、执行步骤序列（Sequence of work）、结果校验方式（How to validate）、返回产物格式（What to return）、何处必须审批（What requires approval）**。支持保存为个人私有技能库（跨本人所有 Bot 共享），也支持在团队内一键 `Publish` 及后续 `Sync` 同步更新。
- **Routine（例程/自动化）**：将验证可靠的单次任务或 Skill 绑定到触发器上自动运行。支持两类触发器：
  1. **定时触发（Schedule）**：按日/周/固定时间周期运行。
  2. **事件驱动触发（Event Triggers）**：监听 Slack 消息、GitHub / Linear / Sentry / PagerDuty 事件、邮件或外部 Webhook 调用自动唤醒指定 Bot。

#### （4）安全网关、凭据保险箱与企业级治理（官方事实）
根据 [cursor.com/docs/grok-bot/security](https://cursor.com/docs/grok-bot/security)：
- **凭据盲填（Vault & Secure Form）**：Bot 默认无任何系统权限，填充密码或信用卡时通过用户的 **Vault**、密码管理器或 **Secure Form** 注入，**Bot 模型上下文无法看到明文密码值**；遇到 SSO 或 Passkey 时交还人类成员完成。
- **OAuth 令牌服务端托管**：接入 GitHub、X、Google Workspace、Microsoft 365 等 MCP 连接器时，OAuth 令牌保留在服务端 Connector Backend，Bot 仅调用工具而不接触原始 Token。
- **独立模型审批门禁（Auto Review & Approval Cards）**：敏感动作由独立的审查模型 **Auto Review** 评估并生成交互式审批卡片（Approval Cards），用户未点击批准前绝不对外生效；Enterprise 版支持管理员强制开启 `Enforce Auto-review` 并下发团队级审查规则。
- **网络出口白名单与 MCP 联动拦截（Enterprise 专属）**：支持 `Allow All`、`Defaults + Team Allowlist`、`Team Allowlist Only` 三档网络策略，并提供 **`Apply to MCP servers`** 开关——开启后，即便是运行在云端服务端的远程 MCP 连接器，其请求的目标域名（如 `api.github.com`、`sheets.googleapis.com`）也必须命中企业网络白名单，否则直接拒绝调用。
- **推理钩子（Inference Hooks）**：Enterprise 支持配置推理钩子以对接企业 DLP（数据防泄漏）策略。

---

### 2.3 腾讯 WorkBuddy：面向企业全场景办公的“连接器-技能-专家/专家团-项目”四层工作台

> 注：关于 WorkBuddy 的完整架构细节详见配套专题报告 [workbuddy-argon.md](file:///home/zym/worktrees/qwen/sunmoonun/docs/总纲/专家方案设计/参考资料/workbuddy-argon.md)，此处提炼其与其余三家的横向对比核心事实。

#### （1）核心定位与端云双模架构（官方事实）
根据腾讯云官方文档 [1831/134384](https://cloud.tencent.com/document/product/1831/134384) 与 [1831/138797](https://cloud.tencent.com/document/product/1831/138797)：
- WorkBuddy 是腾讯出品的全场景 AI 办公工作台（与研发侧的 **CodeBuddy IDE / CodeBuddy Code** 及云端托管的 **WorkBuddy Managed Agents (WMA)** 同属腾讯云 `1831` 产品矩阵）。
- **三种工作模式**：**默认模式**（直接执行）、**问一问（Ask）**（只读问答不改文件）、**想一想（Plan）**（先生成执行计划，人工确认后再执行）。
- **本地任务 vs 云端任务双轨运行**：
  - **本地任务（本机模式）**：AI 推理在云端，脚本与文件读写在本机 지정工作空间（Workspace）执行，可访问本地文件、已装软件与企业内网。
  - **云端任务（云上模式）**：在腾讯云隔离沙箱中执行，无需本机开机，支持云端资料库、Markdown 人机双写与划词评论（v5.10.0）。

#### （2）Skill、专家（Agent 型）与专家团（Team 型）的三层显式划分（官方事实）
根据 [1831/134393](https://cloud.tencent.com/document/product/1831/134393)，WorkBuddy 在产品界面与架构定义上将三者做了极为清晰的切割：
- **Skill（技能）**：工具能力层（含 `SKILL.md`、`config.yaml`、`scripts/`，兼容 OpenClaw 社区技能导入），决定 AI“能做什么具体动作”。
- **专家（Agent 型）**：“角色切换”机制，通过“人设 + 方法论 + 工具链”解决垂直领域的明确单点问题。**专家本身不主动获取系统权限**，仅在挂载了 Skill / MCP 且获用户授权时访问外部资源。
- **专家团（Team 型）**：“协作执行”机制（v5.11.0 / 企业版 v5.30.0 正式合入客户端“项目”模块），由团长（Team Lead）根据需求自动拆解任务、分配给多位不同专长的成员专家并行执行，最终由团长整合交付完整结果。
- **会话隔离硬约束**：[1831/134393](https://cloud.tencent.com/document/product/1831/134393) 明确规定，在已使用专家团的会话中若搜索召唤其他专家，系统强制提示“当前会话已使用专家团，切换其他专家需要开启新对话”，**新专家绝不回绑到当前专家团会话**，以此防止多角色上下文污染。

#### （3）底层多实例团队运行时（Agent Teams）与声明式契约（Agent Manifest v2.0）（官方事实）
- **Agent Teams 运行时**（[1831/137017](https://cloud.tencent.com/document/product/1831/137017)）：
  - 四大核心组件：**团队领导（Team Lead）**、**成员（Teammates，各自拥有完全独立的上下文窗口，不继承领导对话历史）**、**共享任务列表（Task List，含待处理/进行中/已完成三态及 DAG 依赖阻塞自动解锁，支持领导指派与成员自主认领）**、**消息系统（Mailbox，支持点对点 `message`、全员 `broadcast`、优雅关闭 `shutdown_request/response` 及计划审批 `plan_approval_response`）**。
  - **委派模式（Delegate Mode）**：按 `Shift+Tab` 开启后，强制剥夺 Team Lead 直接读写文件或运行命令的工具，将其锁死在协调工具集（`Agent`、`TaskStop`、`SendMessage`、`AskUserQuestion`、`StructuredOutput`），防止领导“越俎代庖”自己干活；而成员实例默认拥有完整 `default` 工具权限。
  - **人工直连任意成员**：用户无需经过团长中转，可通过 `@成员名`、状态栏或方向键焦点导航（`↓` 进入、`←/→` 切换、`Ctrl+O` 返回主视图）直接查看任一成员的独立对话历史与 Token 消耗并向其发消息（已完成成员收到新消息自动重启）。
- **Agent Manifest v2.0 协议**（[1831/139534](https://cloud.tencent.com/document/product/1831/139534)）：
  - 采用严格的 JSON Schema（上限 256 KiB），顶层包含 `version: "2.0"`、`system_prompt`、`skills`、`experts`、`mcp_servers`、`subagents`、`metadata`。
  - **引用式资源声明（`SkillRef` / `ExpertRef`）**：仅声明 `type`（`builtin` / `custom` / `authorized`）+ `id` + `version`（缺省为 `latest`）+ `auth_enterprise_id`，物理下载地址由平台运行时解析补齐。
  - **凭据零明文强制校验**：`mcp_servers` 严禁携带 `headers` 或 `env` 字段（提交即整体拒绝），所有鉴权凭据由平台运行时统一托管注入。

---

### 2.4 Meta Muse：将“多智能体并行编排”直接内化进基座模型训练的推理架构

#### （1）核心定位与模型矩阵（官方事实）
根据 Meta AI 官方博客 [Introducing Muse Spark (2026-04-08)](https://ai.meta.com/blog/introducing-muse-spark-msl/) 与 [Introducing Muse Spark 1.1 (2026-07-09)](https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/)：
- **研发主体**：**Meta Superintelligence Labs (MSL)**，依托 Hyperion 数据中心对 Meta AI 技术栈进行从零重构（ground-up overhaul），目标是构建“个人超级智能（Personal Superintelligence）”。
- **模型演进与上下文容量**：首发模型为 **Muse Spark**（2026 年 4 月），随后升级为 **Muse Spark 1.1**（2026 年 7 月，同步推出 **Muse Image** 并开放 **Meta Model API** 公共预览）。支持原生多模态输入、视觉思维链（Visual Chain of Thought）、**100 万 Token（1M tokens）** 上下文窗口以及主动上下文压缩（context compaction）。

#### （2）推理层与任务层双轨多智能体编排（官方事实）
Meta Muse 的最大架构特殊性在于，它不是单纯在应用外壳层做多 Agent 拼接，而是**在基座模型强化学习与后训练阶段直接训练模型的 Multi-Agent Orchestration 能力**：
1. **Contemplating Mode（熟考模式 —— 推理时多智能体并行）**：
   - 在 [Introducing Muse Spark](https://ai.meta.com/blog/introducing-muse-spark-msl/) 中，官方披露除日常对话模式与标准 `Thinking` 模式外，专门推出了 **`Contemplating mode`**，通过**同时编排多个并行推理的智能体（orchestrates multiple agents that reason in parallel）**来对抗 Gemini Deep Think 与 GPT Pro，在 Humanity's Last Exam (HLE) 取得 58% 的成绩，在 FrontierScience Research 取得 38% 的成绩。
2. **主从角色共训（Main Agent vs. Subagent Co-training）**：
   - 在 [Introducing Muse Spark 1.1](https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/) 中，官方明确披露模型同时针对两种角色进行了联合训练：
     - **作为主代理（As the main agent）**：负责收集上下文、制定整体计划（make a plan），并将执行任务并行委派给多个子代理（delegate execution across parallel subagents），以优化端到端延迟（end-to-end latency）。
     - **作为子代理（As a subagent）**：严格遵守被分配的职责边界（adheres to its job），理解当前可用工具，并**明确知道何时应当向主代理汇报升级（knows when to escalate back to the main agent）**。
3. **零样本工具泛化与自适应脚本/GUI 切换（Computer Use）**：
   - 原生支持零样本泛化（zero-shot generalization）到全新的原生工具、**MCP Servers** 与自定义 **Skills**。
   - 在 Computer Use 场景下，模型被训练出自主判断“何时写脚本批量自动化更快、何时直接点击 GUI 界面更简单”的混合执行能力，并能在每一步生成批量动作（batches of actions）。

---

## 三、 四款产品核心架构维度横向对比表

| 架构维度 | OpenAI dots | xAI Grok Bot | 腾讯 WorkBuddy (`1831`) | Meta Muse (`Muse Spark 1.1`) |
| :--- | :--- | :--- | :--- | :--- |
| **核心产品形态** | ChatGPT 工作空间内的个人持久化代理（Personal Agent） | 云端常驻具名 AI 队友（Named Durable Teammates）+ 薄客户端 | 企业级全场景桌面/云端 AI 办公工作台 + 托管智能体平台（WMA） | 原生支持多智能体编排的多模态推理基座模型 + Meta Model API |
| **计算与沙箱隔离粒度** | 每 `dot` 独立托管云端计算机（支持跨会话快照）+ 可选本机访问 | **每用户单台持久化 Firecracker microVM**（同用户多 Bot 共享单机；团队群聊 Shared Bot 独立单机） | **双轨制**：本地模式（以本地任务文件夹 Workspace 为边界）+ 云上模式（腾讯云隔离沙箱） | 模型 API 层由调用方Harness承载；Meta AI 消费端运行于云端沙箱（底层虚拟化细节**官方未披露**） |
| **多智能体/专家团拓扑** | 个人 `dot` 总控 $\rightarrow$ 异步委派给 **ChatGPT Work** 或 **Codex** 线程 | ① 群聊 `@Bot` 流水线与 Bot 间点对点异步 Handoff<br>② 会话内 `Task` 派生 Foreground/Background Subagents | ① 业务层：**专家（单点角色）** vs **专家团（团长拆解+成员并行）**<br>② 引擎层：**Agent Teams**（Lead + Teammates + 共享 Task List + Mailbox） | ① 推理层：**Contemplating Mode** 多分支并行推理<br>② 任务层：模型原生训练的 **Main Agent 规划扇出 + Subagent 履约与异常上抛** |
| **上下文隔离与共享机制** | `dot` 维护长期工作上下文；委派线程各自独立 | 同用户多 Bot 隔离对话与人设但共享云电脑文件系统；Subagent 采用独立干净上下文窗口 | 专家团会话与单专家强制隔离；Agent Teams 成员拥有完全独立上下文（不继承 Lead 历史），通过 Mailbox 与共享文件通信 | 1M Token 主上下文主动压缩（Compaction）+ 子代理独立聚焦执行并向主代理返回压缩结果 |
| **能力与方法封装契约** | Connected Apps（插件连接器）+ Custom Rules | **Skill**（6 要素标准化作业指令，支持团队发布与同步）+ **Routine**（定时与 Webhook/事件触发器） | **四层解耦**：MCP/连接器 $\rightarrow$ Skill（`SKILL.md`+脚本）$\rightarrow$ 专家/专家团 $\rightarrow$ Agent Manifest v2.0（`type+id+version` 强类型引用） | 模型层零样本泛化支持 Native Tools、**MCP Servers** 与 **Custom Skills** |
| **人机协同与审批门禁** | **Auto-review** 独立拦截对外敏感操作（`dot` 无法自关）+ Activity View 实时接管 | **Auto Review** 独立审查模型 + **Approval Cards（审批卡片）** + 密码盲填（Vault/Secure Form） | 三档工作模式（默认 / Ask / Plan）+ 默认权限高风险弹窗确认 + Agent Teams **计划审批（Plan Approval）** + 人类可 `@成员` 直连任意子实例 | 子代理遇到模糊边界主动 Escalate 回主代理；Computer Use 关键节点请求用户确认 |
| **企业级治理与安全边界** | RBAC 四大开关 + 云电脑三子开关 + Compliance API 审计 | Enterprise 专属网络白名单 + **`Apply to MCP servers` 域名级强校验** + Inference Hooks (DLP) | 企业控制台统一管控（内置专家默认禁用先审后用、可见范围、安全扫描、按需连接引导卡片、公共授权 vs 个人授权连接器） | Meta Model API 区分数据不用于训练的商业档与贡献者档（企业级私有网关治理细节**官方未披露**） |
| **商业化与计费模型** | 按工作类型固定费率（Flat Rate）或按消耗量计费；委派给 Work/Codex 独立计费（2026-11-18 起） | 包含于付费套餐席位周配额（Teams/Enterprise/X 订阅），按席位用量池与超额计费 | **统一积分（Credits）配额池**（旗舰版 198 元/人/月、专享版 316 元/人/月，均赠 2000 Credits/人/月团队共享 + 6 个月有效期加量包；企业自定义模型不扣 Credits） | API 按 Token 计费（区分输入/缓存输入/输出及隐私档位） |

---

## 四、 argon 的独立架构判断：对本项目的六条核心启示

结合四家厂商的一手官方架构设计与我们自身的 `knowlab`（孵化）、`knowbench`（工作台使用）、`knowmart`（市场交易）、`knowbase`（知识与数据底座）四模块拓扑，我给出以下六条独立架构判断：

### 判断 1：“工具能力（Skill/Method）— 领域专家（Expert）— 协作专家团（Expert Team）”必须做成三层正交契约，严禁混为一谈
- **一手事实印证**：腾讯 WorkBuddy 在 [1831/134393](https://cloud.tencent.com/document/product/1831/134393) 中明确将 **Skill（让 AI 能做某件事的工具能力）**、**专家（人设+方法论+工具链的垂直领域顾问）**、**专家团（团长拆解+多成员并行协作的团队）** 彻底分离；xAI Grok Bot 同样将 **Skill（含输入/步骤/校验/审批边界的可复用方法）** 与 **Bot（持久角色与记忆）** 解耦。
- **对本项目的映射**：
  - 在我们的**单兵专家方案**中，主理人拍板的“勾稽验证（四张表恒等式）”、“对照管理层讨论（MD&A 交叉核验）”本质上就是**标准化的领域方法（Method / Skill）**，而“确定分析口径 $\rightarrow$ 解析取数 $\rightarrow$ 动态挂接方法集 $\rightarrow$ 汇总交付报告”则是**通用执行模板（Template）**。
  - 只有将**原子方法（Method）**与**专家外壳（Expert）**解耦，同一个专家才能在面对不同题目、不同数据完备度时，在同一个执行模板上动态组装不同的方法子集，彻底消除“固定专家一套代码、动态专家另一套代码”的双轨割裂。

### 判断 2：资产声明必须采用“不可变版本引用（`id + version`）”与“公开能力声明 vs 私有实现分离”的 Manifest 架构
- **一手事实印证**：WorkBuddy 的 [Agent Manifest v2.0（1831/139534）](https://cloud.tencent.com/document/product/1831/139534) 给出了极佳的工业级范本——Manifest 仅通过 `{ type, id, version }` 引用 `skills` 和 `experts`，严禁内联明文凭据，且在 `WorkBuddy Managed Agents` 中严格区分“版本相关配置”与“版本无关配置”，支持多版本并存与基于源版本派生新版本。
- **对本项目的映射**：
  - **`knowmart`（市场层）**：无论是单兵专家还是专家团，都是具有稳定 `expert_id` / `team_id` 的商品实体，通过语义化版本号（SemVer）演进；专家团的某个版本必须**显式锁定（Pin）**其所引用的成员专家版本（或声明兼容版本区间），防止成员专家独自升级导致专家团流水线崩溃。
  - **知识产权保护（防克隆）**：对外暴露给 `knowmart` 与 `knowbench` 路由器的只能是**公开能力契约（Capability Declaration：擅长领域、输入数据契约、可交付产物 Schema、支持的可选方法标签、验收指标）**；而作者在 `knowlab` 中打磨的核心 Prompt、私有方法编排脚本与权重参数必须作为加密/服务端受控的运行时载荷，绝不下发给调用方明文查看。

### 判断 3：专家团绝不是“把几个专家的 Prompt 拼在一个大窗口里”，而是“团长（Delegate Mode）+ 共享任务看板（Task DAG）+ 独立上下文成员 + 标准化产物交接”
- **一手事实印证**：
  - WorkBuddy 的 [Agent Teams（1831/137017）](https://cloud.tencent.com/document/product/1831/137017) 揭示了一个极其真实的工程教训：“*默认情况下，领导可能会自己动手实现任务，而不是等成员完成*”，为此专门设计了 **Delegate Mode（委派模式）**，剥夺团长的底层执行工具，强制团长只做拆解、派单、审批与汇总。
  - Grok Bot 的 [work.md](https://cursor.com/docs/grok-bot/work) 与 Cursor 的 [subagents.md](https://cursor.com/docs/subagents) 证明：子代理的核心价值在于**上下文隔离（Context Isolation）**——把充满噪音的中间检索、大规模报表试算、网页 DOM 解析隔离在成员自己的独立上下文里，只把符合验收标准的**结构化产物（Reviewable Artifacts）**交接给下游或团长。
- **对本项目的映射**：
  - 在 `knowbench` 中运行专家团时，**团长（Lead）**运行在受限的编排态，负责生成并维护可视化的**任务看板（Task Kanban / DAG）**；每个**成员专家（Member）**在独立上下文中执行自己的通用模板+专属方法，产出持久化的工作区产物文件（Artifact），下游成员通过产物引用（Artifact Ref）而非全量聊天记录接续工作。

### 判断 4：长周期与复杂专业任务必须内置“计划先行（Plan Approval）”与“独立验收门禁（Auto-review / Deterministic Gate）”
- **一手事实印证**：
  - OpenAI dots（**Auto-review** 强制拦截高影响动作，代理不可自关）、xAI Grok Bot（**Auto Review** 独立模型生成 **Approval Cards**）、WorkBuddy（**Plan 模式** + Agent Teams 中成员向团长提交 **Plan Approval Request**）。
  - Meta Muse Spark 1.1 则在模型层训练了子代理在遇到异常或边界模糊时主动向主代理 **Escalate（上抛升级）** 的能力。
- **对本项目的映射**：
  - 这直接印证了我们即将设计的**统一交互机制（Unified Interaction Protocol）**与**确定性验收门禁（Deterministic Acceptance Gate）**：
    1. **执行前**：动态专家或专家团团长先基于用户意图与数据探查结果生成《执行计划与方法选型单》，在需要时提交给用户或团长确认。
    2. **执行中**：当成员专家发现财报科目缺失、勾稽不平或口径歧义时，通过统一的交互事件（`Escalation / Clarification / Approval`）向上抛给团长、任务看板或人类用户（甚至在孵化态抛给作者）。
    3. **交付前**：必须经过独立于生成模型的**确定性校验器**（如 Python/SQL 恒等式验算、必填章节 Schema 校验、溯源引用核查），验算不通过禁止标记任务完成。

### 判断 5：多角色会话与数据连接必须具备“按需懒加载引导”与“公共授权 vs 个人授权隔离”
- **一手事实印证**：
  - WorkBuddy 的 [专家与连接器机制（1831/134393, 1831/138797）](https://cloud.tencent.com/document/product/1831/134393) 提供了两个极其实用的交互设计：
    1. **按需连接引导（Just-in-time Connection Prompt）**：不会在会话开始时一次性弹窗逼用户授权所有依赖的数据源，而是当执行到某一步真正需要某个未就绪的数据源/连接器时，才在输入框上方弹出引导卡片，授权完成后**自动断点续跑当前步骤，无需重开对话**。
    2. **项目级公共授权 vs 个人授权分离**：多人协作任务强制使用项目级公共数据源授权，个人私有凭证仅留存本地、绝不外泄到协作流。
- **对本项目的映射**：
  - 在 `knowlab`（作者按题选数据调试）与 `knowbench`（用户项目内跑专家/专家团）中，专家声明的是**抽象数据契约（Data Contract，如“需提供近三年合并资产负债表、利润表、现金流量表及附注”）**，运行前或运行到对应步骤时动态绑定项目工作区内的 `knowbase` 知识集或用户上传文件；若缺失某项可选数据（如未提供管理层讨论 MD&A），动态专家可自动降级裁剪掉“对照管理层讨论”方法并在报告中显式声明范围边界，或弹出补数卡片支持补齐后断点续跑。
