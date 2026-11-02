# 第6步补充采用修复

## 现状与纠正

所有者指出旧补充仍显示“没用上”。核对确认：此前工作稿30及准专家2.3只加入Markdown交付，
第6步仍是“对照官方披露/主要会计数据/0.1%”，并未采用旧补充。
此前遗漏了这条作者要求，不能解释成“只是显示问题”。

通过正式服务完成：

1. 取消旧规则测试3 `41f664e4-b880-495b-b410-7ae3dd9871a0`，运行方 cancelled、knowlab platform_error。
   已产生模型/工具调用，取消前运行进度 spent 为2.223640；此数不是最终结算金额。
   保留历史测试、用户已确认的采集任务和已入库材料，未删记录或复活作业。
2. `KnowbotWorkdraftService.save`：工作稿30→31，仅修改第6步的标题、说明、原规则、输出结构和检查。
   其余七步逐字段不变，成稿仍写 `财务分析报告.md`。完整作者原话与变更见 `author-change.json`。
3. `KnowbotWorkdraftService.publish`：冻结准专家 **2.4**，id `feec8eae-82b9-4ad0-ba59-4c8a507ccf28`，
   `pending_test`；未测试、未上架。完整冻结内容和保留的旧测试见 `published-draft.json`。

## 状态显示修复

旧页面投影只认退役 `amendment:` 引用；工作稿新清单只允许正常作者 `record:` 引用。
因此把原文写入工作稿并出稿后，旧投影仍显示 open。

开发修复：只有作者edit/accept记录被已出稿清单引用、归属于同一工作稿与作者、
原文逐字进入对应步骤的做法或规则，才推导为 used，显示最新采用的修订号。
不修改旧补充、不恢复旧写入口；仅存工作稿/部分改写/跨作者/跨工作稿/缺记录均不算。
本修复不推断改写、复制或导入包的“等价采用”，这些情况仍须单独的明确出处。

真实数据只读验证见 `usage-readonly.json`：新投影used(4)，现网旧投影仍open。
此文件记录的是候选逻辑验证，**状态显示修复尚未部署**。

## 验证与边界

- knowlab补充/工作稿服务/编译/创建回归：92 passed；Ruff、全仓Pyright通过。
- 现网knowbench已支持所用验收字段；对实际编译的第6步执行10项合成材料测试，全符合预期。
  `verify_rules.py`使用mock资料读取、真实judge/judge_numbers，不写业务数据、不调用模型或Wind。
  `rules-regression.json`保留结果；复现时从knowbench Python环境执行脚本并传入author-change.json文本。
- 支持项缺引文、原文找不到、错页、漏结论、重复结论、非法判值、空原因均拒绝；
  未提到或找不到章节且判不支持、说明原因允许交回。章节选择和语义支持关系仍需实际运行/人工核对。
- 旧测试仍指向未声明的official_by_year、horizon，以及预设缺人数/缺公司；未删测试冒充通过。
  所有者已选择先整理新版测试供其核对，见[新版测试待核对](新版测试待核对.md)。

## 代码与发布

knowlab-backend `8d77867eefa28a1b8ee6bf78e2ebcffa70588b73`，父仓
`b8bf11b113f81a213ca194191903e83b422c2a4d`，分支 `feat/idea-method-entry`。
这是累计开发分支；状态修复提交可独立摘取到#59后端491538c，不直接替换整个开发HEAD。
只需knowlab后端镜像，无迁移、前端/API字段、沙箱或模型配置变更。发布仍交Qwen。
旧测试与版本不重写；回退本修复只恢复旧显示投影，不撤销作者工作稿或已冻结准专家。


## 2026-11-03 release #60 后续核验

所有者通知发布完成。Qwen回执提交c945b9e6，Jenkins release #60，部署a4448ead。
已核9个运行角色Ready及镜像，与发布交接的5镜像一致（见release60-runtime-images.json）。
实际knowlab API/worker与knowbench API/runner的Expectation均含row。
本版不含首页提交问题后自动找专家入口；该缺口不能随此次发布宣称解决。

通过已审阅的register_confirmed_tests.py及正式revise/publish服务登记作者确认的3题
（期望数35/1/1），保留旧用例；工作稿33不变。生成准专家2.5
6d0abd39-9ff7-433a-922a-b313c01fed14，登记回执见release60-registration.json。
经电脑在线、白名单根、模型配置与无活动测试守卫，正式start_self_test启动第4次测试
bdc4eb40-75a5-470f-bcac-3f03ad116df1，20.00上限/3600秒，见release60-test-start.json。
没有代点新采单，没有交付或上架专家第2版。

当前已观察c1通过定范围和数据摸底、进入勾稽，真实query_facts返回季度营收/归母净利润、
报告材料ID/版本/页码。模型一次错误科目码6001被code_invalid拒绝，随后按字典纠正。
这不是全部3题通过；数值复算、管理层讨论语义、季度预测和实际文件仍须后续验收。

### 供给证据与计数纠正

本轮复用作者此前确认的测试集，正式服务为新运行签授权；不是重新采集全部材料。
只读复核旧需求8af82651-3f47-4732-8b93-4cf594b09e42：15项ready，渠道全为cninfo，
关联作业15项done，last_error均空，均有material_id入库回执。时间为北京时间11月3日
01:56—01:59。2026Q1/H1/Q3材料ID与本轮query_facts返回出处一致。
结构化证据见release60-supply-trace.json。
此前交接及CHECKPOINT所写“16项ready”计数不准确，以此次真实15项复核为准；不把
测试集材料总量、需求项数量及reading数量混在一起。也不将供给done等同于本次全新下载。
