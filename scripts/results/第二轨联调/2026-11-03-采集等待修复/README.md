# 确认有效期误报采集中与 PDF 正文缺失（2026-11-03）

## 只读核验

以三个应用自身数据库连接运行 `SET TRANSACTION READ ONLY` 查询；未修改线上任务、
采单、授权或成果。现场代码按 qwen #58 sources 核对。

- 新任务 `0d35c11b-b5cc-4efa-af5d-dba1b6b777fd`，原题是“请对贵州茅台近三年的财务表现进行分析”，未明确要求预测。
- 终态 `SUCCEEDED`，current_step=8；确认记录和 demand_id 均为空，解析清单 `10cc3714-33f1-431c-991d-d54388c38de9` revision=2。
- request r1 记录 3 resolved、16 waiting；缺口 12 必需、4 可选，dropped=[]。其中 12 份是 2023～2026 一季/半年/三季报，另 4 份为 2022 年基期（含年报）。不是严格的“16 份季报”。
- 旧确认 `d6488a64-6f5b-440e-97f6-f83d165dc3eb` 对应需求 `3ee2184d-63c5-4b64-be75-bf7206fb293b`，有 28 个需求项（original 4、table 24），关联 24 个作业，均已失败，reason/last_error 为 invalid_request。有真实尝试，不能说“从没取过”。
- 旧需求创建于 2026-11-02 00:29:27 UTC（北京时间 08:29）；作业最迟于 00:40:26 UTC 失败。旧采单交付的空 label/引用契约问题已见 knowfeed-app CHECKPOINT 与前次修复证据，单看 invalid_request 不能归因为巨潮接口错误。
- 本次步骤交回有 scope/inventory/reconcile/series/indicators/official/forecast/writeup；series 明写无法换算，forecast 明写无法给出预测。事件表无 knowbot/compute 成功记录。
- 冻结验收只有 json_object、required_keys、no_positioning_advice；“通过步骤”没有证明计算、事实引用或页码回查通过。没有改写这份冻结合同或历史成功状态。

临时只读原始输出：`/tmp/luna-task-0d35-readonly.jsonl`、`/tmp/luna-supply-0d35-readonly.jsonl`、
`/tmp/luna-task-0d35-artifacts.jsonl`。未将完整用户正文/供应商响应入库。

## 修复

1. knowbase 去掉“7 天内 confirmation → waiting”的推断与无其它消费者的仓储端口。
   确认是受理、续签依据，不是作业状态；不删除、不缩短确认。缺原件或读法仍 to_confirm。
   消费方按自己的 demand_id 等待；新确认由 knowfeed 现有唯一作业键合流。
2. knowbench 对旧 waiting 不再默认记 incomplete 后续跑，明确要求重新核对采单。
   实际补采结束的 missing 交人路径及用户显式放弃条目不变。定数据说明区分文字、页码与
   事实读法，不能把 PDF 文字当作 compute 的 fact ref，也不能机械追加本题不需要的预测数据。
3. knowfeed PDF 在明确请求 text 时写带页界的正文；不把空白扫描件报告为正文成功。
   公开旧版本已有部分读法不再阻止补齐本次缺项；先取得绑定该版的加工授权，成功后才 ready。
   这是正文加工，不是 OCR，也不是将文字自动变成可计算事实；table 仍走既有财报抽取器。

未承诺完全绕过外网重下载：现有定期报告供给仍会核渠道目录/版本，再交付和补加工。
没有新迁移、协议字段、前端镜像或配置变更。当前无法据本地回归声称真实季报都已取齐。

## 验证与发布边界

- knowbase：21 项真实隔离 DB 回归通过；旧确认不能锁新任务或另一种 reading，数据到达后仍可凭原确认续签。
- knowfeed：62 项读法/供给/调度/网页回归通过；含旧版补 text、已有 pages 不覆写、扫描件不报成功、补表仍失败则 partial。
- knowbench：#58 独立基线 53 项规划/HTTP/隔离 DB 回归通过；旧 waiting 确认返回422，未签新授权、无新 demand、任务仍 WAITING/DATA；解析订正后本人确认正常派单。
- 三个开发子仓 ruff/pyright 通过；#58 移植的测试明确断言导入的是独立工位代码。
- 正式故障候选仅基于 #58，精确 SHA 见原统一发版交接第11节；不含第二轨商城准入、表轴格式或前次精度增量。发布交 qwen 既有 Jenkins。
- 已终结的新旧任务不复活。发布后用本人新任务/正常确认重验实际 demand、逐项读法、facts refs、compute_id 与页码；弱验收专家须通过作者新版完善，不能以空跑“完成”验收财务闭环。
