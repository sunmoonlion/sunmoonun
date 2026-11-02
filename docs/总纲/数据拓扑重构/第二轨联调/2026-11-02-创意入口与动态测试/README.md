# 创意选方法与动态作者测试：联调记录

日期：2026-11-02，Luna。属于第二轨 WP-10 后续增量，不改变 qwen 已获放行的发布候选。

## 本次实际完成

1. knowlab 申请/修改创意可从本人真实方法库选择确切版本。创意记录 ID/版本/摘要，
   旧创意不随方法升版改变。保存拒绝越权、缺版、伪造摘要和重复方法。
2. 工作稿显示创意中待装配的方法，作者选择位置、连接输入，沿原预览/确认接口保存
   精确引用。未设置规划或方法位置时提示先设置；不自动发明数据接入方法或判断规则。
3. knowbench 的动态测试准入由构造期布尔值改为部署侧精确作者名单，正式 bootstrap
   与 HTTP 路由接通。默认空，网页/模型不能自行开启。关闭新受理不影响既有任务恢复。
4. 同一份不可变方法目录，真实 Kimi 对两类问题生成不同计划，并在隔离数据库中经
   现有受理、Conductor、Runner、Advisor、验收与结果回收完成两件任务。

## 源码候选

| 仓库 | 分支 | 完整提交 |
| --- | --- | --- |
| knowlab-app | feat/idea-method-entry | 08ec0f964df982c9c4ba7332b8b6525a05dcf5c7 |
| knowlab-backend | feat/idea-method-entry | a18f72d7faa3430fa496a4912b9508c7820f7fdc |
| knowlab-web-frontend | feat/idea-method-entry | 9bc5f5afa80c1464875c9d3586489d2fde7c60c6 |
| knowbench-app | feat/dynamic-author-intake | 70ebdf603631d2c5f1a935599f1c49bdb125ef33 |
| knowbench-backend | feat/dynamic-author-intake | b86cdcdbd751ea75f6a94ed5396596f70b90d372 |

## 验证事实

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 创意、方法、请求服务和 HTTP，真实 PostgreSQL | 47 passed | knowlab-tests.txt |
| knowlab 前端 | 188 passed / 2 既有 skipped | frontend-tests.txt |
| 动态准入 HTTP 与生命周期 | 17 passed | intake-tests.txt |
| 固定测试、规划、MCP、动态成果回归 | 52 passed | runtime-regression.txt |
| 后端静态检查；前端类型/lint/i18n/build | 通过，956 个翻译键 | 各子仓 CHECKPOINT 的本地日志路径 |
| 实际沙箱规划 | 两题均通过确定性校验，选择 2/3 个方法 | real-planning.jsonl、planning-input.json |
| 实际模型参与完整隔离运行 | 2 passed，166.12 秒 | real-engine-results.txt、real-engine-turns.jsonl |

实际沙箱 Codex 0.155.1，模型 kimi-k3。第一层两个规划 turn；第二层共八个 turn，
包括一份开头不完整的 JSON 规划。运行方严格拒绝后重试，通过后才执行方法；没有
给它补括号、绕过校验或手写成功状态。第二条任务选中的实例名不同也可正常验收，
说明运行不依赖固定实例 ID。报告中的金额为配置价目表估算，不是供应商账单。

第二层仅连接登记为合成测试账号，转接器把实际运行器的每轮提示发往作者沙箱中的
独立临时线程，再把真实回复及用量交回运行器。合成文档全文在题面，模型选择空工具
子集。因此它覆盖模型、运行器、账房、验收与结果收回，**不覆盖生产 relay、knowbase
授权读、Wind 采集或年报 PDF 页码校验**。没有修改线上旧任务或确认任何采单。
临时线程协议依照 [OpenAI app-server 文档](https://learn.chatgpt.com/docs/app-server)，
并以项目实际运行的 0.155.1 行为为准；不是用另一套模型 HTTP 客户端绕过沙箱。

## 发布与恢复

这是后续增量：qwen 当前批次继续原 SHA，不中途移动构建源。下一批同时更新 lab
前后端与 bench 后端，并按本分支配置增加 KNOWBOT_DYNAMIC_TEST_OWNERS。
账号 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7` 来自只读核对任务
`9319ae09-c8b7-4c3b-844e-27306e9e98d8` 的 auth_user.subject，不按显示名猜。
数组仅含该作者；无需改沙箱配置。需要暂停新测试时改回 `[]`，不删除运行记录。

根仓只修改配置真源，不手写渲染物；qwen 经原 Jenkins render/stage/build/apply。
本增量无迁移；保留当前发布批次的迁移头与其他配置。不可整文件覆盖 qwen 新回执
或发布声明。旧后端不理解新创意字段，回退应保留支持该字段的后端并暂停新入口，
不通过改历史 JSON “兼容回退”。商城 v3 准入仍关闭。

## 剩余业务验收

- 真正的财务专家方法版本仍需作者在 knowlab 接受和测试；20 个财务合成夹具未导入
  为正式资产。本次没有冒用作者身份冻结、上架或批准它们。
- 新入口使用已冻结的本人方法。没有正式方法时列表为空，这是实际状态，不用占位
  卡片伪造可选资产。已有工作稿可先经“保存为独立方法”冻结，再回创意选用。
- 已开发的 Wind/年报适配器属于 qwen 当前候选；服务端来源配置、正式采单确认、
  knowbase 证据读取、财务预测与 PDF 对照要在发布后联验。文本响应不冒充 PDF。
- 作者动态测试通过真实数据样例后，再开放商城动态专家准入；保底固定专家保持可用。

## 复核探针

本目录 *.py.txt 是本次实际执行的取证脚本，不是部署程序。planning-probe.py.txt
包含两份合成目录提示；probe-remote.py.txt 是远端 websocket 调用模板；
probe-isolated-engine.py.txt 复用当前 backend 测试夹具和真实 Runner，输出真实回执。
复跑会使用指定沙箱作者的模型额度，必须在同一授权范围内，并先核当前 Pod、账号、
隔离数据库地址和版本；不盲目复制旧 Pod 名。凭据只在 Pod 内从现有文件读取，不进
参数、回执或 Git。数据库测试只用专属测试库/随机 schema，不连生产数据库。
