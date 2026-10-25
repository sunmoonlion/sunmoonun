# 四类知识库：放什么、读哪里、怎么读、怎么用；请专家用自己的数据（0042）

> 状态：**实施中**（进度见第十一节，qwen 只提交未发）。所有者 2026-10-23 定，Opus 同日整理；第五节六项所有者「除了选数据的弹框，「财务分析与预测」重孵化第 2 版都按你拟的」，听完解释后第 6 项「行」。
>
> 所有者原话（10-23，按先后）：
> - 早上：「knowlab knowmart都有自己的知识库，但是它们都在云端，而knowbench的用户的知识库在本地」「每个用户除了出售专家服务，还出售私有知识」「云端知识库当然在knowbench（knowlab也有知识库，与knowbench不同）。knowbench的本地知识就叫本地知识库」「经过自己的后端转调knowbase」「它们虽然可以身份相同，但大多少其实不同，应该独立，不能互相拿」
> - 晚上：「按甲」（专家不绑数据、请专家用自己的数据本期一起做）「你不要图省事，这些反正要做，分期做，后面还要做一遍，其实工作量更大」（云端知识库本期一起做）「你先要理清：那类知识库，读哪里，怎么读这是三类不同的问题，不要混」「对啊，knowmart和knowlab，都只有云端知识库，展示在前端，真源在knowbase；knowbenh有本地和远端知识库，真源分别在本地和knowbase，这不是早上讨论定好的吗」「都做出来，以后不要被法律评估挡住：如果挡住就按是否有资质处理。现在要定的或明确的是：各类知识库使用方式问题」「都按你拟的」（第四节四项）
>
> 相关：[数据拓扑](../../../总纲/数据拓扑.md)（第五节运行授权、第七节代采、第八节本地知识库、第十六节）、[0018](0018-advisor-market.md) 第十节（knowmart 供需市场）、[0037](0037-idea-avatar-expert.md)（knowlab 两端与专家生命周期）。

## 一、有哪几类

| 类 | 是什么 | 不算知识库的 |
| --- | --- | --- |
| A. knowbench 本地知识库 | 用户自己留着的资料，放在用户电脑上 | 项目目录（干活的地方） |
| B. knowbench 云端知识库 | 用户干活用的云端资料：上传的、代采取回的、从 knowmart 买来的 | 产出（专家交回的底稿，是结果不是来源） |
| C. knowlab 知识库 | 孵化、测试专家用的资料 | — |
| D. knowmart 知识库 | 卖家放上架出售的知识（私有资料） | knowmart 的条目（介绍、样张）是条目，不是资料本身 |

四类相互独立，不互相读（10-23）。

## 二、读哪里（真源）

| 类 | 真源 | 前端经谁 |
| --- | --- | --- |
| A | 装有本地 link 的那台电脑上的「本地知识库目录」（本地 link 设置里选，只读） | knowbench 网页 → 本机回环口或会合点服务流 → 本地 link |
| B | knowbase 里这个用户的 knowbench 部分 | knowbench 网页 → knowbench 后端 → knowbase |
| C | knowbase 里这个用户的 knowlab 部分（现存在 knowlab 自己的对象存储里，本期搬过去，第七节） | knowlab 网页 → knowlab 后端 → knowbase |
| D | knowbase 里这个用户的 knowmart 部分 | knowmart 网页 → knowmart 后端 → knowbase |

各前端只连自己的后端；knowbase 不直接对前端（数据拓扑第二节）。

## 三、怎么读

| 谁读 | A | B | C | D |
| --- | --- | --- | --- | --- |
| 用户本人看、管 | 浏览器 → 本机回环口 → 本地 link；在远程登录 link 的电脑上：→ knowbench 后端 → 会合点服务流 → 本地 link | 浏览器 → knowbench 后端 → knowbase，凭用户本人凭据（第六节） | 浏览器 → knowlab 后端 → knowbase，凭本人凭据 | 卖家：浏览器 → knowmart 后端 → knowbase，凭本人凭据；买家买之前只看条目与样张 |
| knowbench 聊天、工作 | Codex 经本地 link 就地读（现在就能） | 读数据工具 → knowbench 后端凭「会话」运行授权 → knowbase，只读用户在对话里选的那几份 | 不读 | 不读 |
| knowbench 请专家 | 就地读，或读数据工具 → knowbench 后端 → 服务流 → 本地 link；都只读请专家时选中、钉住摘要的那几份 | 读数据工具 → knowbench 后端凭「委托」运行授权 → knowbase，只读选中的那几版 | 不读 | 不读 |
| knowlab 测试 | 不读 | 不读 | 工作台凭「测试」运行授权 → knowbase，只读测试绑定的那几版 | 不读 |
| knowlab 辅助孵化 | 不读 | 不读 | 凭「孵化」运行授权，只读格式 | 不读 |
| 后端算数、验收 | 经服务流读钉住的那份，核摘要 | 凭运行授权读钉住的那一版 | 凭测试运行授权读 | 不读 |
| 买卖 | — | 买下的知识复制一份进来 | 买下的知识复制一份进来 | 卖出时复制一份给买家（进买家的 B 或 C） |

## 四、怎么用（所有者 10-23「都按你拟的」）

| | A 本地 | B 云端 | C knowlab | D knowmart |
| --- | --- | --- | --- | --- |
| 东西怎么进来 | 用户往目录里放；从 B 下载下来 | 用户上传；knowbench 发起的代采；买来的（买家选进 B） | 用户上传；knowlab 发起的代采；买来的（买家选进 C） | 卖家上传 |
| 用户本人能做的 | 在电脑上随意增删改；上传到 B | 看、删、下载到 A | 看、删 | 看、删、用它建上架条目 |
| 在哪些场合被用 | 聊天、工作时 Codex 就地读；请专家时选作数据 | 请专家时选作数据；**聊天、工作时选用几份**（凭「会话」运行授权，会话结束就撤） | 孵化时读格式；测试时按准专家的数据需求声明绑定版本 | 上架出售：条目按驻场规则写，**上架前审资质**；买家买之前只看条目和样张；买下后复制一份进买家的 B 或 C |
| 不能做的 | 专家写不进；原文件不进云端存储 | 专家写不进；产出不自动进来 | 不给 knowbench 请专家用 | 专家运行时不读；卖家下架、删除不影响已卖出的 |
| 删除 | 用户自己管 | 被进行中的委托、会话钉住的，结束前不能删 | 被测试或在做的准专家绑定的不能删 | 删了不影响已卖出的 |

- **应用之间挪资料：只能下载再上传**，不做一键复制；后端之间不直接拷（三个应用独立）。
- **knowbench 发起的代采先进 B**（代采在云端跑），用户要的话再下载到 A；knowlab 发起的进 C（数据拓扑第七节）。
- **上架要审资质**：发布主体（个人 / 非个人）按类目审资质，审过才能上架。被法律评估卡住的地方一律按「有没有资质」处理，不再等法律评估（所有者 10-23）。审什么材料照 WorkBuddy 开放平台的做法拟一版，在 0018 里写。
- 产出（底稿）不是知识库；想当资料再用，上传进 B 或放进 A。
- 买来的知识归买家，能下载；转卖按驻场规则（0018 第十节）。

## 五、请专家用自己的数据（所有者 10-23 定）

10-23 定「专家只是逻辑、不绑数据」，本期一起做（所有者「按甲」）。

| # | 项 | 定了什么 |
| --- | --- | --- |
| 1 | 本地知识库和项目目录怎么区分 | 按用途：本地知识库放来源资料，只读、各项目共用；项目目录是干活的地方，专家在里面写底稿、成稿（本地 link 现在就是这么管的） |
| 2 | 请专家时数据从哪选 | A 和 B；项目里的文件不算（项目里是产出） |
| 3 | 数据需求声明写什么 | 专家清单里逐样写：名字、说明、格式（PDF / Excel / CSV / 文本，沿用 knowlab 现有几种）、要几份（如「5 份年报」）、必填还是可选；表格类可写要有哪几张表、哪几列。knowlab 测试按这份声明从 C 绑数据 |
| 4 | 钉住与核对 | 请专家那一刻：A 里选中的文件由本地 link 算 sha256、B 里选中的记 knowbase 的版本与摘要，记进这次委托；专家只能读这几份；读时再核摘要，委托开始后改过的报「数据在这次委托开始后被改过」；数值验收按钉住的内容复核 |
| 5 | 专家怎么读 | 两种都可以：就地读（A，快，大文件可用 python 处理）和读数据工具（A 经服务流、B 凭运行授权）；算数和验收一律由后端按钉住的那份读 |
| 6 | 选数据的界面、现有专家怎么过渡 | 请专家时弹框，按声明逐样从 A 或 B 选，必填缺了不能开始；同一项目再请同一个专家默认选上次那几份。「财务分析与预测」按带声明的格式重新孵化出第 2 版；第 2 版上架后停用第 1 版（第 1 版读的是作者绑定的数据） |

随之要改的（三个应用）：

- **清单格式**（knowlab 写、knowmart 存、knowbench 用）：分「数据需求声明」与「测试绑定」两块；交 knowmart 只带声明，不带绑定（「交付绑定」取消）。跨应用契约只加不改，旧格式的专家照旧能请到第 2 版上架为止。
- **knowbench 后端**：读数据工具（`list_my_data`、`read_my_data`、`read_my_table`）、`compute`、数值验收（`acceptance_numbers.py`）从「经 knowlab 读作者绑的」改成「读这次委托钉住的 A、B」；`knowlab_data_client.py` 退役。`list_library`、`read_library_item` 改读 B（凭会话或委托运行授权）。
- **knowbench 网页**：请专家时的选数据弹框；工作台显示用了哪些数据；「知识库」页改名「云端知识库」，按第四节放三样，底稿不再进来；对话里选用 B 的入口。
- **knowmart**：清单模型去掉绑定、加声明；详情页显示「需要你提供哪些数据」。

## 六、knowbase 要补的：本人凭据、运行授权、留痕

| 项 | 做法 |
| --- | --- |
| 本人凭据 | **Casdoor 令牌交换（RFC 8693）**：应用后端拿用户的登录令牌，向 Casdoor 换一张发给 knowbase 的令牌（`audience` = knowbase）。2026-10-23 读 Casdoor 4.12.0（部署的版本）源码核过：`object/token_oauth.go` 的 `GetTokenExchangeToken`，核令牌未吊销、用户未禁用、目标应用存在且服务这个组织、权限只能收窄；换出的令牌带用户（`sub`）与代办应用（`azp`），满足数据拓扑第 5.3 节第 4 条。要在各应用的 Casdoor 应用上打开这个授权类型。不由 knowbase 自己签发。**10-23 在临时 Casdoor 4.12.0（正式环境同一镜像）上实测通过**（[`opus-0042-token-exchange-lab.20261023-2009.md`](../../../../scripts/results/opus-0042-token-exchange-lab.20261023-2009.md)）：换出的令牌 `aud` = knowbase、`azp` = 代办应用、`sub` = 用户；放大权限、别的应用代换、吊销后再换都被拒。随之要做：应用会话在服务端存用户的访问令牌（现在登录后丢了），knowbase 新加按 `azp` 认应用 |
| 运行授权 | knowbase 签发，四种：测试、委托、孵化（已定）、**会话**（新加：knowbench 聊天、工作里用户选用 B 的几份，会话结束就撤，兜底按会话的时限）；只能在用户选的范围内，越界就拒；申请不到不开跑 |
| 留痕 | 每次读：谁、凭哪条运行授权、读了哪个数据集哪一版；只记编号不记数值，留一年（数据拓扑第 5.3 节第 9 条） |
| 分区 | knowbase 里按「用户 × 应用（knowbench / knowlab / knowmart）」分开存；买来的知识复制一份，归属与删除各算各的 |
| 工作台旧令牌 | 工作台自签的「knowbase MCP 令牌」照数据拓扑第十五节撤掉 |

## 七、knowlab 知识库搬进 knowbase

- 现在 knowlab 的「我的数据」存在 knowlab 自己的对象存储（`infrastructure/storage/object_storage.py`），元数据在 knowlab 库里。
- 搬：对象搬进 knowbase 的 knowlab 分区，knowlab 只留业务记录（哪份数据被哪个准专家、哪次测试绑定）；读写经 knowlab 后端凭本人凭据或测试运行授权去 knowbase。
- 已有的绑定（数据编号 + 版本 + sha256）搬过去后编号对得上，摘要不变，已测过的结果照样能复现。
- 页面叫法「我的数据」改「知识库」，和 knowbench 的一致（knowlab 只有这一个）。

怎么落地（Opus 10-23 拟，实现细节）：

| 项 | 做法 |
| --- | --- |
| 编号 | knowlab 的数据记录照旧（数据编号、版本 "1"、sha256），加一栏 knowbase 的资料编号；清单里的绑定、格子地址、引文都还写 knowlab 的数据编号，所以编号对得上、摘要不变 |
| 新传的 | 网页 → knowlab 后端凭本人令牌传进 knowbase 的 knowlab 分区，knowlab 只记业务记录；不再进 knowlab 自己的对象存储 |
| 删 | 先核绑定（在做的、已交付的草稿绑着的不能删），再凭本人令牌删 knowbase 那份 |
| 已有的 | 一次性搬：knowlab 服务身份把旧对象逐份交给 knowbase（新接口「导入」，只能导进调用方自己的分区，按 knowlab 数据编号幂等），回填资料编号；旧对象留到「财务分析与预测」第 1 版停用（第 1 版运行时照旧经 knowlab 读作者绑的） |
| 测试同意 | 用户在 knowlab 知识库传、删时（本人在场），knowlab 凭本人令牌在 knowbase 更新一条「测试」同意依据，范围是他 knowlab 知识库里的全部资料；页面写明「放在这里的资料只用于测试你的创意」 |
| 测试读数 | 发起测试时 knowlab 凭同意依据向 knowbase 签测试运行授权（读的一方是 knowbench，只读绑定的那几份，时限按测试的超时加等人），随测试请求交给 knowbench（`knowbot-test-run/v1` 只加一个可选的 `data_grant`）；knowbench 把这几份钉进每条用例的委托，按钉住的读；测试结束 knowlab 撤授权 |
| 没搬完的 | 测试绑的数据还没有资料编号时不签授权，照旧经 knowlab 读（第 1 版停用后这条路撤掉） |

## 八、knowmart 知识库与供需市场

本期一起做（所有者 10-23「都做出来」），设计写在 0018（供需市场：卖家发布供给、买家发布需求、驻场规则、专家与知识两种商品、资质审核、交易记录）。本页只管 D 这一类知识库：卖家上传、管理；上架条目引用 D 里的资料；卖出时复制一份进买家的 B 或 C。

## 九、实施分块（同一期，按依赖排）

| 块 | 做什么 | 依赖 |
| --- | --- | --- |
| 1 | knowbase：令牌交换验本人、运行授权（四种）、留痕、按应用分区、上传与下载接口 | — |
| 2 | knowbench：云端知识库页（上传、看、删、下载到本地）、对话里选用 B | 1 |
| 3 | knowlab：知识库搬进 knowbase、测试走运行授权 | 1 |
| 4 | 清单格式（声明 + 测试绑定）、knowlab 孵化与测试按新格式 | 0037 |
| 5 | knowbench：请专家选数据、钉住、读数据工具与验收改读 A / B | 1、4 |
| 6 | knowmart：清单模型改、详情页显示数据需求；D 知识库与供需市场（0018） | 1、4 |
| 7 | 「财务分析与预测」重孵化第 2 版、上架、停用第 1 版 | 4、5、6 |

每块写完单测与跨应用契约锁；照旧只在 qwen 提交，等 Fable 回来按平台流程发（所有者 10-23）。

## 十、不做

- 一键在应用之间复制资料（只能下载再上传）。
- 让 knowbase 直接对前端。
- 「专家随数据」（10-20 公开专家随专家提供一套数据）：10-23 取代。

## 十一、实施进度（qwen 工位，只提交、不推、不发）

| 块 | 已做 | 提交 |
| --- | --- | --- |
| 1 | knowbase 用户资料：按「用户 × 应用」分区存、上传下载删、同意、运行授权（测试、委托、孵化、会话）、凭授权读内容或格式、买卖复制、读数留痕；验令牌的 `aud`、`azp`；契约 `user-data/v1` | knowbase 后端 `0465409`、`54a0bd0`，父仓 `1947261`、`915863a` |
| 1 | 三个应用留下用户访问令牌、向 Casdoor 令牌交换、knowbase 客户端 | tpl `736d94d`（父 `c96dd25`）；knowbench `6b28350`（父 `e2d12cf`）；knowlab `47cf74c`（父 `75042a0`）；knowmart `23a18a3`（父 `899e1f6`） |
| 2 | knowbench「云端知识库」页（上传、看、删、下载） | knowbench 后端 `a359320`、网页 `39d17d9`，父 `5ccdad2` |
| 5 | 读数层（抽文字、分页、按格子、核引文）从 knowlab 搬到 knowbench | knowbench 后端 `a4797cc` |
| 5 | 本地 link 服务流能只读本地知识库目录 | sunmoon-link `3f44f92`（随下一版 link） |
| 5 | 委托钉住的数据表（迁移 `20261023_0024`）；读数据工具、`compute`、数值验收先读钉住的那几份：云端凭委托的运行授权经 knowbase，本地经服务流一块块读，取到就核 sha256，对不上报「数据在这次委托开始后被改过」（验收里记平台没能核）；没钉的旧格式专家照旧经 knowlab | knowbench 后端 `77f3114`，父 `33953f8` |
| 4 | 清单外层加数据需求声明 `data_needs`（每样：key、名字、说明、格式 pdf / excel / csv / text、必填、`min_count`～`max_count`、表格类要有的表与列；合起来不超过 64 份），绑定可写对应哪一样 `need`；写了声明的交到 knowmart 不带绑定；声明为空、`need` 没写时不进规范 JSON，旧清单摘要不变（测试钉了加之前的两个摘要）。格式照市面做法拟（Dify 应用的「用户输入表单」：变量名、标签、必填、文件类型、最多几份） | knowmart 后端 `cf1cdbe`，父 `b6e83d9`（契约 `knowbot-manifest/v1` 只加） |
| 4 | knowlab：建草稿先核声明，测试绑定按声明核（每份写对应哪一样、格式对、份数在范围里），交 knowmart 去掉测试绑定 | knowlab 后端 `28db63b`，父 `7639424` |
| 5 | knowbase：读的一方能交还给自己的运行授权（`POST /grants/{id}/release`），委托结束就撤、不用用户在场 | knowbase 后端 `d17eb26`，父 `cc24146` |
| 5 | 本地 link 服务流加 `fs/digest`：在 link 这头算整份文件的 sha256（Windows 经沙箱助手按块读、在 link 里算） | sunmoon-link `855655b`（随下一版 link） |
| 5 | knowbench 请专家选数据：写了声明的专家没选不建委托；云端凭本人令牌核资料、签一条委托运行授权（7 天兜底），本地只收本地知识库目录里的文件、由 link 算摘要（老 link 一块块读回来算）；钉住的数据随委托同一提交写下；同一把幂等钥匙重发不再签；建委托没成就交还；委托结束由 runner 交还授权；`GET /workbench/packs/{id}/data-needs` 给弹框声明与同一项目上次所选；委托单带 `chosen_data` | knowbench 后端 `41596bd`，父 `17a474c` |
| 5 | knowbench 网页：请专家页「要用的数据」一节与选数据弹框（云端按格式列、本地文件树），必填缺了不能交；委托页顶上写用了哪些数据 | knowbench 网页 `5a1262d`，父 `cce89b1` |

| 2、5 | 聊天、工作里选用云端知识库：每段对话选几份、凭「会话」运行授权（24 小时兜底，改选换一条、交还旧的）；每轮说明写这段对话能读哪几份；`list_library` / `read_library_item` 改读这几份；撤旧的「交回物当资料」（迁移 `20261023_0025`）；网页输入框旁「云端知识库」 | knowbench 后端 `57ab32e`、网页 `5fe3e2d`，父 `f36f83d`、`6b6e490` |
| 3 | knowbase：应用搬自己的旧资料（`POST /imports`，服务关系 `user-data-import`，只进调用方自己的分区、按原编号幂等）；同意依据最多 1000 份（授权仍 64） | knowbase 后端 `f6fcf8f`、`f7eaa39`，父 `588865b`、`232fd21` |
| 3 | knowlab：新传、删走 knowbase（迁移 `20261023_0011`），每人最多 1000 份；传、删、打开知识库页时更新测试同意；发起测试签测试运行授权、随请求带 `data_grant`，结束、退回、开跑失败都撤；一次性命令 `python -m app.bootstrap.import_datasets` 搬旧数据；网页「我的数据」改「知识库」 | knowlab 后端 `b8dd62b`、网页 `3be2704`，父 `9fafac8`（契约 `knowbot-test-run/v1` 只加 `data_grant`） |
| 3 | knowbench：测试请求认 `data_grant`，每条用例的委托钉这几份按钉住的读（钉表主键改成委托＋数据编号、记授权种类，测试授权不由 runner 交还） | knowbench 后端 `cc81702`，父 `09c239a` |

| 6 | knowmart：详情页显示需要你提供的数据；D 知识库（卖家上传、管理）；供需市场（知识条目从 D 选资料，卖出时经 knowbase 复制进买家的 B 或 C） | 见 [0018](0018-advisor-market.md) 第十一节第 10 小节 |

评审后（10-24，处置见 [`review-2026-10-24-opus/opus-response.md`](../../review-2026-10-24-opus/opus-response.md)）：

| 评审条 | 改了什么 | 提交 |
| --- | --- | --- |
| Astra F01 | 缓存不跳过授权：knowbase 加「核一次」`GET /grants/{id}/items/{item}/check`（同读内容的判断，不给内容，留痕 `check`；迁移 0008 的 CHECK 加这个值；契约 user-data/v1 只加 `ItemCheck`）。knowbench 读钉住的数据，没取字节就先核：云端 check，本地 `fs/digest` 重算 | knowbase 后端 `9ecc492`、`5c45cf6`，父 `cef673e`；knowbench 后端 `9e5ed18`，父 `606616c` |
| Astra F02 | 签不出测试运行授权不开跑，不退回旧读路。三种情况：没绑数据，不签；全没搬进 knowbase，照旧经 knowlab；有搬进去的，必须签。开测前就报的码：`data_not_imported`、`data_binding_stale`、`test_consent_missing`。knowbase 拒签或不可达，这一次记平台出错。knowlab 的测试读法只给没签授权的、没搬的那几份；knowbench 带授权的测试不退回 knowlab | knowlab 后端 `b32c593`，knowbench 后端 `8b21a46`，父 `ee03afe`、`606616c` |
| Astra F03 | 删资料前先立不含它的新同意、撤旧同意（迁移 0011 加待撤同意表 `knowbot_consent_withdrawal`），撤不成停下报 `consent_not_withdrawn`、可重试；活动授权挡住删除时同意放回 | knowlab 后端 `dc5e11c`、web端 `5336d29`，父 `ee03afe` |
| Astra F04 | 打开知识库页把 knowbase 里 knowlab 分区有、knowlab 没登记的补登记（数据编号按资料编号定，重来不重复），在 knowmart 买进 knowlab 的就能绑、能测 | knowlab 后端 `74f451e`，父 `ee03afe` |
| Qwen Q-06 | 运行授权兜底：委托 7 天、会话 24 小时（原来 knowbase 截成 24、12 小时，与本节和 knowbench 申请的不一致） | knowbase 后端 `a37915f`，父 `9759248` |
| Qwen Q-08 | 老 link 没有 `fs/digest`、走回退路径时记一行日志 | knowbench 后端 `9d6ab2d`，父 `2a72f77` |
| Astra D01 | Windows 补授读：从用户目录到目标逐级拒符号链接与联接，realpath 核实际目标就是这个路径；icacls 带 `/L`，授前再核 | sunmoon-link `c2cbb83`（随下一版 link） |

已知限制（Astra D01、Qwen Q-13、Kimi 168）：
- 补授读按 PATH 里用户目录之下的目录授，`(OI)(CI)(RX)` 继承到其下所有文件，沙箱命令能读到这些目录里的东西（包括顺带放在那里的配置）。要不要收窄到固定的程序根，影响所有者实测过的 Python 场景，没改。
- 真 NTFS 上的 ACL 前后与沙箱实读（含「已有授权但缺 CI」的中间态），等所有者 Windows 真机回归。

撤回测试同意只挡新授权，已签的到交还、撤销或到期为止（Fable 10-25 定，D03；写进契约 user-data/v1 说明）。

Fable 评审后（10-25，处置见 [`review-2026-10-24-opus/opus-response.md`](../../review-2026-10-24-opus/opus-response.md) 第四节）：

| 评审条 | 改了什么 | 提交 |
| --- | --- | --- |
| P1-1 | 测试运行授权上限 7 天（原来截成 26 小时）；knowlab 签出的比要的短就撤掉、当没签成 | knowbase 后端 `3df65ea`，knowlab 后端 `0b99028` |
| P2-4、5、6 | 搬过来的旧数据还有旧对象、本人还没补上测试同意时照旧经 knowlab 读（取代上面「先打开知识库页才能测」的说法）；测试同意刷新整段加锁；补登记跳过搬旧数据建的 | knowlab 后端 `c053eb7` |
| P2-16 | 买来不许转卖的资料带 `no_resale`（knowbase 迁移 0008 加栏，契约只加可选字段），同一个人再传同样内容的也带上；knowbench 云端知识库、knowlab 知识库标出来 | knowbase 后端 `b031c85`，knowbench `1e640b4`、`1ba80ac`，knowlab `519e21d`、`3a0f2c8` |
| P1-3、P1-4、P2-11、P2-14、P2-15、P2-12 | link 删只读测试目录、远程拉仓库不记住令牌、远程操作只转给连着的电脑、测试不写 /tmp、重新 init 留着设备编号、提权模式下控制文件拒读 | sunmoon-link `c5cef2d`、`1c4cea9`、`d85aeb9`、`4f36a06`，knowbench `05911d1`、`e41edac`、`94c620c`、`1cf2b07`、`44d08cd`、`39b5dc6`、`281f4bc` |

还没做（按第九节的块）：`knowlab_data_client.py` 与 knowlab 的旧读数路、旧对象，等「财务分析与预测」第 1 版停用后撤；块 7 重孵化。knowlab 0037 的数据结构与两端重做已做，见 [0037](0037-idea-avatar-expert.md) 第十八之二节第 4 小节。

发版时要配（等 Fable）：

- knowbase：迁移 `20261023_0008`；配置 `user_token_audience`、`user_token_apps_json`、`user_data_bucket`、`user_data_prefix`、`user_data_reader_apps_json`；服务关系 `user-data-read`、`user-data-grant-test`、`user-data-purchase`；期望库版本随之改。
- Casdoor：knowbench、knowlab、knowmart 三个应用打开令牌交换授权类型；建 knowbase 目标应用（它的客户端编号就是各应用的 `KNOWBASE_USER_AUDIENCE`）。
- knowbench、knowlab、knowmart：`KNOWBASE_USER_AUDIENCE`、`KNOWBASE_INTERNAL_URL`、`KNOWBASE_USER_DATA_<关系>_SERVICE_*`。
- knowbench：期望库版本改成 `20261023_0024`（`gitops/.../knowbench-backend/config.yaml` 与 `migration/workload.yaml` 的 `expected_schema_revision`）。runner 起了交还授权的线，要能连 knowbase（服务关系 `user-data-read`）。
- knowbase：knowlab 的导入服务身份配上 `knowbase:user-data-import`，并在 `USER_DATA_READER_APPS_JSON` 里登记成 knowlab；knowlab 签测试授权的身份要 `user-data-grant-test`。
- knowbench：期望库版本改成 `20261023_0025`（上面那条的 0024 作废）。
- knowlab：期望库版本改成 `20261024_0012`（0037 的迁移在 0011 之后；只写 0011 的那一版作废）；配 `KNOWBASE_INTERNAL_URL`、`KNOWBASE_USER_AUDIENCE`、`KNOWBASE_USER_DATA_GRANT_TEST_SERVICE_*`、`KNOWBASE_USER_DATA_IMPORT_SERVICE_*`；发版后跑一次 `python -m app.bootstrap.import_datasets`。
- 发布顺序：knowbase（交还授权、导入、同意放宽）→ knowmart（清单外层）→ knowbench（认 `data_grant`）→ knowlab（声明与绑定、知识库搬家、发 `data_grant`）；本地 link 新版带 `fs/digest`，老版本照样能用（工作台一块块读回来算）。
- 评审后（10-24）：
  - knowbase 迁移 0008 的内容变了（读数留痕多 `check`），版本号不变。knowbench 读钉住的数据要用 knowbase 的 check，knowbase 要先上（顺序已满足）。
  - knowlab 迁移 0011 多一张待撤同意表，期望库版本仍是 `20261024_0012`。
  - knowlab 开测签不出授权就不开跑。搬过来的旧数据在本人补上测试同意之前照旧经 knowlab 读（Fable P2-4），所以发版后跑完 `import_datasets` 就能测；`import_datasets` 要在没有在跑的测试时跑。
  - Fable 评审后：knowbase 迁移 0008 又加资料的 `no_resale`；knowlab 迁移 0011 又加数据记录的 `no_resale`，0012 退回前核新写入；期望库版本都不变。
  - 测试电脑的 TMPDIR 设到 `<工作区>/runs/.tmp`（Fable P2-14，平台配置）。没设之前测试照旧能写 /tmp，没有隔离。
