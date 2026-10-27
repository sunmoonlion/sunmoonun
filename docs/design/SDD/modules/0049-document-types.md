# 资料类型词表第二版：大类加细类（0049）

> 状态：**已定（2026-10-27）**，实施中。所有者 10-27：「我觉得现在桶里在postgresl的描述的类型好像分的不够细，不符合我的要求」；Opus 查了巨潮、东方财富、天软、上交所《公告格式指南》后出方案，所有者：「按你的方案来，四条都做」「研究报告的分类，wind做得最好，你查查按它的方案」，并截了 Wind 终端研报平台的两张图。决定原话见 [decisions](../../decisions.md)「数据第四版开工中的讨论」第 ⑬ 条。
>
> 取代 [0043](0043-data-v4.md) 第 2.5 节「词表第一版的类型」那一句；描述的其余规矩（确认状态、改动留痕、不产生新内容版本）照旧。

## 一、市面做法（2026-10-27 查）

| 来源 | 分法 |
| --- | --- |
| 巨潮资讯 | 一层 26 类（年报、半年报、一季报、三季报、业绩预告、权益分派、董事会、监事会、股东大会、日常经营、公司治理、中介报告、首发、增发、股权激励、配股、解禁、公司债、可转债、其他融资、股权变动、补充更正、澄清致歉、风险提示、特别处理和退市、退市整理期）；分类代码见本地 AKShare 源码 `stock_feature/stock_disclosure_cninfo.py` |
| 东方财富 | 两层：一级 7 类（重大事项、财务报告、融资公告、风险提示、资产重组、信息变更、持股变动），二级如重大合同、投资相关、股权激励、定期报告、利润分配、业绩预告、业绩快报、增发、新股发行、配股、要约收购、吸收合并、回购；每条另有更细的「公告类型」 |
| 天软 | 两层约 50 项（重大事项下关联交易、担保、诉讼仲裁、出售资产；公司治理下工作规程、内部控制报告、社会责任报告；特别提示下异常波动、停复牌等） |
| 上交所《上市公司自律监管指南第1号——公告格式》（2026-04 修订） | 按事项 56 号，各家细类大体落在这 56 号上，是监管口径 |
| Wind 公告分类 | 只在终端里，未公开 |
| Wind 研报平台（所有者截图） | 「类别」15 个；行业 29 个；盈利预测（首次覆盖、评级变动、预测变动）；筛选条件页数、日期、市场、语言、深度、更新频率、附件类型、研究员；来源分证券公司、期货公司与各家机构 |

共同点：定期报告单列；临时公告至少再分一层；研报按研究领域分类、行业与机构另作筛选维度。

## 二、结构

- **两层**：大类、细类。资料的描述只记**细类**，大类由词表推出；专家声明的 `doc_type` 可以写细类（只要这一种）或大类（这类都行）。编码全局唯一，大类与细类不重名。
- **每个大类留「其他」**（`<大类>_other`，定期报告除外）：归不进细类的放这里，不硬套。
- **版本形态** `edition`：全文 `full`（缺省）、摘要 `summary`、英文版 `english`。另记一栏，不进细类（东财分、巨潮不分）。
- **研究报告的属性** `attributes`：来源机构、研究员、行业（Wind 29 个）、盈利预测（可多选）、市场、语言、深度、更新频率、评级。研报只能本人上传，属性由上传时填或识别后本人确认。
- **期间**：定期报告照旧按报告期（年初到报告期末）；**其余类型的期间是披露时间窗**（含两端），资料按披露日落在窗里算对得上。声明加期间规则 `recent`：最近 `months` 个月内披露的（1–60），截至任务日期。
- **词表改版的规矩**：只加细类、加属性取值不升 `VOCAB_VERSION`，旧描述照常参与解析；改名、删除、改词义才升。契约 `knowbot-data-needs/v2` 尚未上线，本次在 v2 内直接改（第一版那几个编码里 `announcement`、`prospectus`、`policy`、`statistics`、`webpage` 换了归属或拆开），上线以后同样的改动要开 v3。

## 三、大类与细类

「采」一栏：上市证券的公告类由 knowfeed 按描述去巨潮采；政策、统计按机构编号采；研报、网页（要给网址）与其他不采。「巨潮」一栏是采的时候查哪个巨潮分类，再按第四节的标题规则归细类。

### 3.1 上市公司披露（主体是证券代码，可采）

| 大类 | 编码 | 细类 | 编码 | 巨潮分类 |
| --- | --- | --- | --- | --- |
| 定期报告 | `periodic` | 年报 | `annual_report` | 年报 |
| | | 半年报 | `semiannual_report` | 半年报 |
| | | 一季报 | `q1_report` | 一季报 |
| | | 三季报 | `q3_report` | 三季报 |
| 业绩 | `results` | 业绩预告 | `results_forecast` | 业绩预告 |
| | | 业绩快报 | `results_express` | 业绩预告 |
| | | 业绩说明会 | `results_briefing` | 公司治理 |
| | | 其他 | `results_other` | 业绩预告 |
| 发行上市 | `ipo` | 招股书申报稿 | `prospectus_filing` | 首发 |
| | | 招股书 | `prospectus` | 首发 |
| | | 上市公告书 | `listing_announcement` | 首发 |
| | | 其他 | `ipo_other` | 首发 |
| 再融资 | `refinancing` | 向特定对象发行（增发） | `private_placement` | 增发 |
| | | 配股 | `rights_issue` | 配股 |
| | | 可转债 | `convertible_bond` | 可转债 |
| | | 公司债 | `corporate_bond` | 公司债 |
| | | 其他 | `refinancing_other` | 其他融资 |
| 分红 | `dividend` | 利润分配方案 | `dividend_plan` | 权益分派 |
| | | 权益分派实施 | `dividend_implementation` | 权益分派 |
| | | 其他 | `dividend_other` | 权益分派 |
| 会议与治理 | `governance` | 董事会 | `board` | 董事会 |
| | | 监事会 | `supervisory_board` | 监事会 |
| | | 股东大会 | `shareholder_meeting` | 股东大会 |
| | | 治理制度 | `governance_rules` | 公司治理 |
| | | 内部控制报告 | `internal_control` | 公司治理 |
| | | 社会责任/ESG 报告 | `esg_report` | 公司治理 |
| | | 董监高变动 | `personnel_change` | 公司治理 |
| | | 其他 | `governance_other` | 公司治理 |
| 经营与交易 | `operations` | 重大合同与中标 | `major_contract` | 日常经营 |
| | | 对外投资 | `external_investment` | 日常经营 |
| | | 购买出售资产 | `asset_transaction` | 日常经营 |
| | | 关联交易 | `related_transaction` | 日常经营 |
| | | 担保 | `guarantee` | 日常经营 |
| | | 财务资助 | `financial_assistance` | 日常经营 |
| | | 诉讼仲裁 | `litigation` | 日常经营 |
| | | 政府补助 | `government_subsidy` | 日常经营 |
| | | 募集资金使用 | `fund_raising_use` | 日常经营 |
| | | 会计政策变更与差错更正 | `accounting_change` | 日常经营 |
| | | 会计师事务所变更 | `auditor_change` | 日常经营 |
| | | 其他 | `operations_other` | 日常经营 |
| 重组与收购 | `restructuring` | 重大资产重组 | `major_restructuring` | 不限（按标题） |
| | | 要约收购 | `tender_offer` | 股权变动 |
| | | 吸收合并 | `merger` | 不限（按标题） |
| | | 破产重整 | `bankruptcy_reorganization` | 不限（按标题） |
| | | 其他 | `restructuring_other` | 不限（按标题） |
| 股本与股东 | `equity` | 权益变动 | `equity_change` | 股权变动 |
| | | 增持 | `shareholding_increase` | 股权变动 |
| | | 减持 | `shareholding_decrease` | 股权变动 |
| | | 质押冻结 | `pledge_freeze` | 股权变动 |
| | | 回购 | `buyback` | 股权变动 |
| | | 股权激励 | `equity_incentive` | 股权激励 |
| | | 限售股解禁 | `lockup_release` | 解禁 |
| | | 协议转让与司法拍卖 | `share_transfer` | 股权变动 |
| | | 其他 | `equity_other` | 股权变动 |
| 交易提示与风险 | `trading` | 异常波动 | `abnormal_fluctuation` | 风险提示 |
| | | 停复牌 | `suspension_resumption` | 风险提示 |
| | | 风险提示 | `risk_warning` | 风险提示 |
| | | 澄清 | `clarification` | 澄清致歉 |
| | | 更正补充 | `correction` | 补充更正 |
| | | 风险警示与退市 | `delisting_risk` | 特别处理和退市、退市整理期 |
| | | 其他 | `trading_other` | 风险提示 |
| 中介报告 | `intermediary` | 审计报告 | `audit_report` | 中介报告 |
| | | 法律意见书 | `legal_opinion` | 中介报告 |
| | | 保荐与核查意见 | `sponsor_opinion` | 中介报告 |
| | | 评估报告 | `valuation_report` | 中介报告 |
| | | 评级报告 | `rating_report` | 中介报告 |
| | | 其他 | `intermediary_other` | 中介报告 |
| 投资者关系 | `investor_relations` | 投资者关系活动记录 | `ir_activity` | 公司治理 |
| | | 互动问答 | `ir_qa` | 不采（交易所互动平台，以后另接渠道） |
| | | 其他 | `ir_other` | 公司治理 |
| 监管 | `regulatory` | 问询函及回复 | `inquiry` | 不限（按标题） |
| | | 监管措施与纪律处分 | `regulatory_measure` | 不限（按标题） |
| | | 其他 | `regulatory_other` | 不限（按标题） |

### 3.2 研究报告（照 Wind 研报平台，只能上传）

| 大类 | 编码 | 细类（Wind「类别」原名） | 编码 |
| --- | --- | --- | --- |
| 研究报告 | `research` | 晨会纪要 | `research_morning` |
| | | 宏观研究 | `research_macro` |
| | | 策略研究 | `research_strategy` |
| | | 行业研究 | `research_industry` |
| | | 公司研究 | `research_company` |
| | | 金融工程 | `research_quant` |
| | | 市场综述 | `research_market` |
| | | 固定收益 | `research_fixed_income` |
| | | 商品期货 | `research_commodity` |
| | | 衍生品 | `research_derivatives` |
| | | 基金研究 | `research_fund` |
| | | 外汇市场 | `research_fx` |
| | | REITs研究 | `research_reits` |
| | | ESG研究 | `research_esg` |
| | | 其他报告 | `research_other` |

研报的属性（`attributes`，都可空）：

| 属性 | 键 | 取值 |
| --- | --- | --- |
| 来源机构 | `institution` | 自由文本（机构名），不参与匹配以外的推断 |
| 研究员 | `analysts` | 名字列表 |
| 行业 | `industry` | Wind 29 个：石油石化、煤炭、有色金属、电力及公用事业、钢铁、基础化工、建筑、建材、轻工制造、机械、电力设备、国防军工、汽车、商贸零售、消费者服务、家电、纺织服装、医药、食品饮料、农林牧渔、银行、非银行金融、房地产、交通运输、电子元器件、通信、计算机、传媒、综合 |
| 盈利预测 | `forecast` | 首次覆盖 `initiation`、评级变动 `rating_change`、预测变动 `estimate_change`，可多选 |
| 市场 | `market` | A 股 `cn`、港股 `hk`、美股 `us`、其他 `other` |
| 语言 | `language` | 中文 `zh`、英文 `en`、其他 `other` |
| 深度 | `depth` | 深度 `deep`、一般 `regular` |
| 更新频率 | `frequency` | 日 `daily`、周 `weekly`、月 `monthly`、季 `quarterly`、年 `yearly`、不定期 `irregular` |
| 评级 | `rating` | 自由文本（照报告原文，如「买入」） |

公司研究的主体是证券代码；其余研报的主体可空（宏观、策略）或用机构编号。

### 3.3 政策法规、统计数据（主体是机构编号，可采）

| 大类 | 编码 | 细类 | 编码 |
| --- | --- | --- | --- |
| 政策法规 | `policy` | 法律 | `law` |
| | | 行政法规 | `administrative_regulation` |
| | | 部门规章 | `departmental_rule` |
| | | 规范性文件 | `normative_document` |
| | | 地方性法规 | `local_regulation` |
| | | 司法解释 | `judicial_interpretation` |
| | | 交易所与协会规则 | `self_regulatory_rule` |
| | | 政策解读 | `policy_interpretation` |
| | | 其他 | `policy_other` |
| 统计数据 | `statistics` | 统计公报 | `statistical_bulletin` |
| | | 月度数据 | `statistics_monthly` |
| | | 季度数据 | `statistics_quarterly` |
| | | 年度数据 | `statistics_annual` |
| | | 普查 | `census` |
| | | 其他 | `statistics_other` |

### 3.4 网页与其他（不采；网页要给网址）

| 大类 | 编码 | 细类 | 编码 |
| --- | --- | --- | --- |
| 网页与其他 | `other` | 网页 | `webpage` |
| | | 新闻 | `news` |
| | | 其他表格 | `other_table` |
| | | 其他文本 | `other_text` |

港股、美股（10-27 决定 ⑩「以后再说」）到时加大类：港股照港交所标题类别，美股照 SEC 表格类型（10-K、10-Q、8-K 等）。

## 四、knowfeed 按标题归细类

巨潮的「日常经营」「公司治理」「股权变动」「中介报告」等一类装几个细类，knowfeed 采进来按标题归：

1. **先看强信号**（不论巨潮分类）：问询函、关注函及回复 → `inquiry`；警示函、监管措施、纪律处分、通报批评 → `regulatory_measure`；重大资产重组 → `major_restructuring`；吸收合并 → `merger`；破产重整、重整计划 → `bankruptcy_reorganization`；异常波动 → `abnormal_fluctuation`；停牌、复牌 → `suspension_resumption`；更正、补充公告 → `correction`；投资者关系活动记录 → `ir_activity`；业绩说明会 → `results_briefing`。
2. **再按巨潮分类内的规则**：第三节「巨潮分类」一栏写同一类的几个细类，按标题关键词归（如日常经营里「合同」「中标」→ 重大合同与中标，「关联交易」→ 关联交易，「担保」→ 担保……；业绩预告里「快报」→ 业绩快报；权益分派里「预案」「方案」→ 利润分配方案，「实施」→ 权益分派实施；首发里「申报稿」→ 招股书申报稿，「招股说明书」「招股意向书」→ 招股书，「上市公告书」→ 上市公告书）。
3. **认不出归该大类的「其他」**，不硬套；规则带版本，改规则不回头改已交付的描述（描述改动另走留痕）。
4. **版本形态**照标题认：「摘要」→ `summary`，「英文」「English」→ `english`，其余 `full`；已取消的、H 股的不要（照现有规则）。

按描述采时（需求单）：细类查对应的巨潮分类，「不限」的不带分类按标题关键词检索；大类查它所有细类对应的分类。定期报告一份描述对一份报告；其余类型一条描述是一个披露时间窗，窗里归到这个细类的全部交付（每份一份资料）。

## 五、各仓要改的

| 仓 | 改什么 |
| --- | --- |
| knowbase | 词表（大类、细类、版本形态、研报属性、`recent` 期间规则）；描述加 `edition`、`attributes`（迁移）；解析按大类展开、按披露窗与版本形态、研报属性匹配；契约 `knowbot-data-needs/v2` 与 `user-data/v2` 重新生成 |
| knowmart、knowlab、knowbench | 本仓的声明 v2 模型照新契约改、锁更新 |
| knowfeed | 巨潮插件：细类 → 分类与标题规则、版本形态、按披露窗列出多份、每份交付；标题归细类（第四节） |
| knowbase web端 | 描述表单从词表接口取大类、细类（不写死，已是这样） |
