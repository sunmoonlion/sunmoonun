# 模型怎么取数据：数据 MCP 与工具层（0048）

> 状态：**设计稿（2026-10-27）**，未实施。所有者 10-27 指出「我们现在好像只讨论了api接口，但是，模型如何调用接口好像没做，具体说，就是mcp好像没设计」，要求「先查市面做法再定」；本轮目标是「财务分析与预测」对用户问的任意一家 A 股上市公司都能跑通（所有者：「我告诉你的意思是这是我们的目标」），本页是这条链上「模型能读」那一环。
>
> 工具放哪、令牌谁签是 Opus 查了市面做法后的建议，所有者没有另定（「好，按这个顺序做」）；写完后读现有代码做了一处修正，见第二节末。
>
> 和 [0043](0043-data-v4.md)（授权、解析）、[0047](0047-public-disclosures-facts-search.md)（事实、检索）的关系：那两页定 knowbase 的接口，本页定模型经什么工具用到它们。

## 一、市面做法（2026-10-27 查）

- **MCP 官方规范**：MCP 服务是资源服务器，令牌要绑定发给它自己（audience），「MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server」，明令禁止令牌原样转给下游；每个请求都验，不靠会话认人；权限最小、逐步升级，服务端自己核业务规则，不只看令牌里写的权限（[安全最佳实践](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)、[授权](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)）。
- **网关还是分服务**：服务多、团队多用网关统一管，少就直连；关键不在拓扑在令牌，转给下游要换范围更小的凭据（[Arcade](https://arcade.dev/blog/mcp-gateway-pattern)、[Composio](https://composio.dev/content/enterprise-mcp-deployment-patterns)、[Aident](https://aident.ai/blog/what-is-an-mcp-gateway)）。
- **代用户调用**：每次代理运行用短期、绑用户、限范围的令牌，每次调用重新核；调下游用令牌交换（[Logto](https://blog.logto.io/mcp-server-token-strategy)、[Auth0](https://auth0.com/ai/docs/mcp/intro/overview)）。

## 二、架构

```
沙箱里的 Codex ─┐
用户 link 上的 ─┼─▶ knowbench（中继，只转发、不验不换令牌）──▶ knowbase 数据 MCP
               │                                              （验令牌、按授权核、留痕）
               └─▶ knowbench 工作台 MCP（项目、计算、要数据）
```

- **knowbase 开数据 MCP**：读钉住的输入、查事实（含跨全市场）、找证据片段、全文搜、按描述查、科目与指标字典。授权、留痕、开关都在 knowbase，和数据规则在一处。
- **knowbench 工作台 MCP 只留跟任务有关的**：读项目对话与底稿、`compute`、`request_data`（缺数据时提出要什么，第五节）。
- **都经 knowbench 中继**：用户的沙箱只连得到 knowbench（工作台给沙箱配置时特意不发 knowbase 的令牌：「用户的沙箱到不了平台的数（数据拓扑，待办账 111）」），用户 link 也只连 knowbench；knowbench 把数据 MCP 的请求原样转给 knowbase，只许转这一个地址（防 SSRF），不验、不换令牌。
- **修正**（写完读代码后）：原建议「令牌由 knowbase 自己签」改为**沿用 knowbench 签**——knowbase 现有 MCP 本来就认 knowbench 签的 ES256 令牌（audience 是 knowbase）。令牌只说明「这个沙箱代用户 U、以 knowbench 名义在用」，**能读什么由 knowbase 每次按用户签的运行授权或会话范围核**，knowbench 自己拿不到用户没授权过的数据。

## 三、令牌

| 项 | 内容 |
| --- | --- |
| 签发 | knowbench 工作台（现有 ES256 签发器），和记录工具的令牌一起在给沙箱配置时发；link 经设备令牌向 knowbench 领 |
| audience | `knowbase-data`（只给数据 MCP 用，别的服务不认） |
| 内容 | `sub` 用户、`azp` 执行的应用（knowbench）、沙箱或设备编号、允许的工具、过期时间 |
| 能干什么 | 只证明身份与沙箱；每次调用另带 `run`（委托或测试编号）或 `session`（会话编号），knowbase 按它找有效的授权再核 |
| 失效 | 沙箱删掉、设备解绑、过期；授权撤了的立即读不到（不看令牌） |

## 四、工具（knowbase 数据 MCP）

每个工具都带 `run` 或 `session` 之一；返回的每个数、每段文字都带**出处**：资料编号、名字、内容版本、读法版本、页码（有的）、摘要前 8 位，模型照这个引用。

| 工具 | 做什么 | 凭什么能读 |
| --- | --- | --- |
| `list_inputs` | 这次运行钉了哪几份：需求 key、描述（主体、类型、报告期）、版本、钉住的读法、内容归谁 | `run` 下有效的运行授权（含运行中追加的新修订） |
| `read_input` | 读一份：正文或按页文字（可按页范围）、表格读法、只看格式 | 同上，只读钉住的那一版与那个读法 |
| `query_facts` | 查事实：按主体、科目编码、报告期、口径、原样或标准化、长表或宽表；`scope=run` 只查钉住的，`scope=market` 查全市场公开原件的事实（筛选、排序、排名、统计） | `run`：授权项；`market`：资格、权限、平台总开关（0047 第 4.4 节） |
| `query_metric` | 按指标算（毛利率等），回公式与参与计算的每个数的出处 | 同 `query_facts` |
| `describe_items` | 科目表与指标定义（编码、中文名、属于哪张表、适用哪类公司） | 只要令牌有效 |
| `search_evidence` | 先圈后找：先圈出这次运行钉住的那几份（会话里是读过的那几份），**可按描述的维度再圈小**（类型或大类、主体、期间、版本形态、事项、行业、语言、研报的几维，[0049](0049-document-types.md)）；再在圈里找证据片段，回片段与页码。块 9 之前「找」是在按页文字里按关键词扫（回 `method: keyword`）；块 9（RAGFlow 一版本一文档，文档带维度元数据，0047 第 2.4 节）后换 RAGFlow + Infinity 的关键词加向量，圈的范围与维度条件一并作 RAGFlow 的文档与元数据条件传下去 | `run` 的授权项；会话里是这段会话已读过的 |
| `search_documents` | 全文搜公开原件与他名下的资料（Elasticsearch），按公司、类型、年份筛 | 资格、权限、平台总开关；他名下的按展示依据（0047 第 5.2 节，随 P4） |
| `lookup` | 按精确描述查某一份在不在、在哪个范围 | 只要令牌有效；同一用户限流 |
| `list_library` | 会话里能读的：他放开给 knowbench 的，加公开原件层 | `session` |

旧工具：knowbase 的 `list_datasets` / `describe_schema` / `metric_definitions` / `run_sql` / `query_metric`（SQLite 数据集）与工作台的 `list_my_data` / `read_my_data` / `read_my_table` / `list_library` / `read_library_item`，跟「财务分析与预测」第 2 版上架一起退；兼容窗口内 v1 专家照旧用。

## 五、逐步升级：首读小授权与缺数据

规范说的「需要时再升级、服务端自己核」，对上 0043 已定的两件事：

1. **会话首读一份**：会话开始时应用凭本人令牌在 knowbase 登记这段会话（会话编号、执行的应用、范围 = 他放开给 knowbench 的，24 小时）。模型在会话里第一次读某一份时，knowbase 核这一份在范围里，当场签一条小授权（0043 第 2.7 节「会话」），钉住组合；累计刚过 50 份时工具结果里带一句提示，界面提示一次，不挡。
2. **缺数据**：模型发现要一份没钉的（比如还要上一年的年报），调工作台的 `request_data`，写明要什么（按声明的形状：主体、类型、期间、读法）。knowbench 请 knowbase 给这张解析清单出新修订（0043 第 3.2 节），把待确认的列进用户的待办，任务停在「等数据」，工具回「已列进确认清单，等用户确认」。**模型不能替用户确认**（0043 第 3.3 节第 6 条）。用户确认后照 0043 第 3.3、3.4 节补齐，应用新签一条独立授权（运行中追加），模型下一轮 `list_inputs` 就看得到。

## 六、跟已做代码要对齐的

- **测试与平台过程的执行方**：块 1c 里 knowlab 签的测试、平台授权把执行的应用记成 knowlab，但测试是运行方（knowbench）跑的、模型经 knowbench 读。要改成：执行的应用 = 运行方 knowbench，签发方 = knowlab；平台过程的「运营看」另记读的一方是运营。
- **会话登记**：块 1c 的会话小授权现在要本人令牌逐条签，改为「本人登记会话一次，模型首读时 knowbase 凭会话范围签」（第五节第 1 条）。
- **运行中追加的服务路**：块 2 的「清单出新修订」现在要本人令牌；`request_data` 由 knowbench 以服务身份提（只出修订、不签授权，确认仍要本人）。
- **数据 MCP 的读数留痕**：读的一方记沙箱或设备编号与令牌里的执行应用，操作记哪种工具。

## 七、实施

| 块 | 做什么 | 依赖 |
| --- | --- | --- |
| M1 | knowbase：数据 MCP（`list_inputs`、`read_input`、`query_facts`、`query_metric`、`describe_items`、`search_evidence`、`lookup`、`list_library`），令牌验证，按授权逐次核，留痕；会话登记与首读小授权；第六节的对齐 | 0047 P1、P2 |
| M2 | knowbench：中继（只转数据 MCP）、给沙箱与 link 发 `knowbase-data` 令牌、工作台 MCP 加 `request_data`、等数据的协调 | M1，0043 块 6 |
| M3 | `search_documents` | 0047 P4 |

**怎么验**：
- 委托跑「财务分析与预测」第 2 版：`list_inputs` 列出钉的几份年报；`query_facts` 查得到三大表，每行有出处到页；`search_evidence` 只回钉住版本里的片段。
- 同一令牌换一个不属于他的 `run`：读不到；授权撤掉后立即读不到。
- 会话里读一份没读过的、放开给 knowbench 的：自动签小授权；读一份没放开的：拒绝并提示去 knowbase 放开。
- 模型调 `request_data` 要上一年年报：任务进「等数据」、用户待办里出现确认清单；没确认之前 `list_inputs` 看不到它。
- 平台总开关关掉：`query_facts(scope=market)`、`search_documents` 拒绝。

## 八、实施进度

- M1（knowbase）：做完，knowbase-backend `5309b14`（对齐：执行方、会话登记、运行中加需求的服务路）与 `7957b5c`（数据 MCP，`/mcp/data`）。读法格式定为：`text` 是 UTF-8 纯文本，`pages` 是 `[{page, text}]` 的 JSON。
- M2（knowbench 中继、发令牌、`request_data`）、M3（`search_documents`）：未开始。
- **要记着做**（所有者 10-27：「这个要记得做啊，保证到时可以按维度过滤检索」）：`search_evidence` 先圈后找：「圈」已接按维度过滤（knowbase 词表第 2 版，在授权范围里按描述的维度筛，回 `materials_searched`）；**「找」还没换成 RAGFlow（等块 9），换的时候把同样的维度条件作 RAGFlow 元数据条件传下去**，保证按维度过滤检索。
