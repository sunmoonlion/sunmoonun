# Cursor 回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 实际检查版本：sunmoon-kind。应用镜像来自发布 #106，部署 `284913fbcf15159c21318e90ef3f37f6d4ddbea7`，指针 `fb08ce5f953780f94c61c83ef714c1673dd4d8e8`，tag `release-20261122-4`。指令控制面地址来自随后的 #108，部署 `ca2d9423e05d3784b3c03d64c75ebc8552eb7c0d`，指针 `304e733bdc0be56954e5113ec1072c4439aafc94`，tag `release-20261122-5`。
- 结论：部分完成。KnowBench、KnowLab 和新的 sig-am 试验配置已在目标集群。控制面地址在 #108 之后才写进运行中的供给器。L105 现场跑了一次，失败，花费 0 元。第 13 项验收、#105 余项和三道盲测没有可交付的产物。下一步由 Luna 决定。

## 发现

- F01：#106 发布成功。admin 于 2026-11-22T17:23:03+08:00 批准，https://jenkins.dev.sunmoonai.com:30443/job/release/106/ ，结果 SUCCESS。回执 `scripts/results/release-106.20261122-173108.md`（提交 `168c5af2ed9364bbd40910f03958d9790eaee286`）。这次只暂存了 KnowBench 和 KnowLab，供给器清单没有重渲染，`INSTRUCTION_CONTROL_ORIGIN` 仍是空字符串，`instruction-control-ca` 不存在。
- F02：#107 用来补这处地址，make 退出码 0，但 Jenkins 结论是 NOT_BUILT。第 5 阶段看到暂存后没有清单差异，按「同一组钉已在线上」收工，没有进人批，也没有新的 Flux 制品。分支上的修正提交 `643dee688` 当时没有进集群。
- F03：#108 只重渲染供给器，发布成功。admin 于 2026-11-22T17:51:43+08:00 批准，https://jenkins.dev.sunmoonai.com:30443/job/release/108/ 。部署 OCI `sha256:6783cc31adc0a8fba5a8fad2d4032ef8cd60e7afce55660f3da52df0887787bd`，Flux platform 对该摘要 Ready。回执 `scripts/results/release-108.20261122-175445.md`。运行中的供给器环境为 `https://knowbench-tls.app-platform-dev.svc.cluster.local`。ConfigMap `instruction-control-ca` 的证书主体是 `CN=SunMoon Registry Local CA`。沙箱镜像没有重建，网关实际使用 `sha256:8fc0460292c0ad31a697f390dbbb4a45d9bc86a29f41d2b0a34965b163066475`。
- F04：脚本开关和交付写回保持关闭。没有已核定的脚本报价。打开交付写回会推进其他账号已有的一条待写产出，没有另建隔离部署。只有 Kimi 一个模型家族，没有装 `WORKBENCH_REVIEW_MODEL_GRANTS`，也没有获准的合成 A2A 提供方。
- F05：L105 只点了一次「开始实际验证」。线程和 turn 已建立，约 19 秒后以 `instruction_trial_failed` 结束，输出为空，用量回执没有形成。没有第二笔，没有冻结，没有动 knowbot-tester 的令牌。

## 发布

环境：sunmoon-kind。应用命名空间 `app-platform-dev`，沙箱命名空间 `sandbox-platform-dev`。分支 `expert-entry-release-20261122`。入口仍是 `knowlab.dev.sunmoonai.com:30443` 和 `knowbench.dev.sunmoonai.com:30443`。

#106 的 NOTE：请专家入口与回炉及 Kimi 指令复核同一版发布，全量入口保持关闭。APPS：knowbench、knowlab。PIN=heads。

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowBench 后端 API / runner | `60ea2f46a49e73528c14c3483f137e63c4395ad7` | `sha256:bbeafed4ca61bf2cc222df5e311b623583cdb00a678c89f979c5be06dfec0a1a` |
| KnowBench Web | `65089bcbba7be4014fd599f65886c8373b5e43b8` | `sha256:73213c3a3edf09d42f8c8ec28b1600232be3c6cdf78e364eb8d8fd94b4fc2261` |
| KnowBench 管理 Web | `33559e926c3ebb7570716d5bb318b5a014e0d645`，未重建 | 沿用上一版 |
| KnowLab 后端 | `1d2e24290a9e84a369a043d97741c57215eb61be` | `sha256:4f735a46cc6219a563b095d37a44e1a0a00af3fa2802ce6a9395eabe99a2db12` |
| KnowLab Web | `76c6bfd804ce4a5c5bf04a1435fc50c0e4601cf2` | `sha256:05b8d403de3a06ba3d91cd5987975775d5fd6f38c6dae5594948cbf966eda0b6` |
| KnowLab 管理 Web | `89fe3ac1f6178018186584db7542f11102896381`，未重建 | 沿用上一版 |
| 供给器持有的沙箱 | 未进入 #106 / #108 的镜像重建 | `sha256:8fc0460292c0ad31a697f390dbbb4a45d9bc86a29f41d2b0a34965b163066475` |

父仓与请求表一致：KnowBench `2a20aea1ee2ff018d2e21ad44641c6afbcca5165`，KnowLab `677af26c3c7b04e980d513df53a4af10316eae36`。库头没有新迁移：KnowBench 仍是 v13 / `20261122_0058`，KnowLab 仍是 v5 / `20261120_0029`。

#106 之后读到的 `knowbench-runtime`：

- `EXPERT_UNIFIED_ENTRY_ENABLED=false`
- `EXPERT_PLANNING_OWNERS` 与 `WORKBENCH_FIXED_AS_PLAN_OWNERS` 都只含 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`（sig-am）
- `WORKBENCH_INSTRUCTION_ROUTES`：kimi / kimi-k3，`https://api.moonshot.cn/v1`，上下文上界 1048576，输出上限 8192
- `WORKBENCH_REVIEW_ROUTES`：kimi / kimi-k3，家族 kimi
- `WORKBENCH_DATA_SUPPLY_ENABLED=true`
- `WORKBENCH_SKILL_SCRIPTS_ENABLED=false`，`WORKBENCH_OUTPUT_WRITE_ENABLED=false`
- 价目沿用代码内 kimi-k3 CNY 表（2026-10-04）：输入 20、缓存输入 2、缓存写入 20、输出 100，单位是每百万 token

#108 的 NOTE：重渲染供给器以发布指令控制面地址。APPS：sandbox。PIN=heads。应用镜像和上面的开关没有换。

## 现场

账号 sig-am，浏览器在 KnowLab 正式方法页。当前用户显示 sig-am。申请 `5c4fa327-e511-40a5-9ead-e8597cdc7ef2`，名称「Luna105 标记回执」。实现来源显示 `b0a48ce7-546e-42e4-981a-3676fbbf29c5 · 1 · Luna #105 私有标记`，允许的调用来源勾了宿主程序。

表单：宿主发起，执行成功，输入 `{"marker":"L105"}`，断言 `[{"kind":"equals","pointer":"/receipt","value":"L105"}]`，重复次数和至少通过次数都是 1。电脑选在线的 `zymun`。已授权目录只有 `C:\Users\zymun\Desktop`。预算从页面原有的 1 元改成 30 元。执行时限 300 秒，最长等待 3600 秒，沿用页面原值。2026-11-22 18:07 点了一次「开始实际验证」。

| 项 | 值 |
| --- | --- |
| KnowLab 验证记录 | `f2204cb7-2a73-40db-854f-fc32a6d9a5ed` |
| 方法单元 | `3de9e0c7-4aee-4d53-92d6-7eb65ba4aba3` |
| KnowBench 任务 | `40021330-5239-4441-94f1-9a65d3e2dcb3`，状态 FAILED |
| 尝试 | `9ca84f63-a0d6-4094-b422-d16347d7da86`，角色 execute，状态 FAILED |
| 线程 / turn | `01a202b9-6d12-71d0-bc29-3e0f698bd551` / `01a202b9-6d52-7791-8c35-d7fdd32d59ba` |
| 页面结果 | 验证失败，`instruction_trial_failed`，case_1 执行失败 |
| 库内结果 | `formal_result.outcome=failed`，`detail=instruction_trial_failed`，`outputs={}` |
| 报价 | kimi-k3，上限 21.790720 CNY，价目日 2026-10-04 |
| 费用 | 预算限额 30 CNY，已用 0，预留 0。页面显示已花费 0.000000 元 |

KnowLab 在 2026-11-22T10:07:03Z 接受了执行请求，状态 200。KnowBench 内部正式方法执行接口同一秒返回 202。供给器在 10:07:06Z 对 prepare 返回 200，10:07:16Z 记下 turn 绑定，10:07:35Z 收到 stop 和删除。

原因：这一轮已经开出线程和 turn，但没有交回合格的最终文本，runner 收成 `instruction_trial_failed`。worker 只把模型请求发给网关的 47801，且不重试。同一时段该端口的就绪探针先超时，再变成连接被拒绝，没有供应商用量回执。worker 事件里的 DeadlineExceeded 是停机时把 `activeDeadlineSeconds` 改成 1，不是 900 秒到期。绑定密钥 not found 与拆 Pod 同一秒，是收尾现象。

网关 Pod `instr-7b847c244be347f090610f9e302f6c0f` 使用沙箱镜像 `sha256:8fc0460292c0…`。没有刷新出第二笔运行。没有点「确认冻结这个版本」。

请求里的本地测试数量没有在本轮重跑，不作为本集群通过。三道业务盲测没有建委托，业务产物留待 zymun；本回执不代替那份业务意见。

## 第 13 项与 #105 余项

| 范围 | 本次能核对的 | 未跑 |
| --- | --- | --- |
| 手册第一关 L105 | 私有申请、来源 v1、表单和一次真实试跑都在。运行失败，`/receipt` 不是 L105，费用为 0，没有可核的供应商用量。 | 成功运行、刷新仍是同一笔、冻结自用。失败前的条件不成立，没有改表再跑。 |
| 本卡第 13 项 1–3 | sig-am 在试验名单里，全量入口仍关。Kimi 指令和同家族复核路由已装上。 | 新入口的匹配、零候选、结束未匹配、计划复用、送 KnowLab 的三种去向。L105 没有留下可冻结版本。 |
| 本卡第 13 项 4 | 付费试跑只发生了上面这一笔，实耗 0。 | 三道盲测的委托、目录快照、计划和交付。 |
| #105 第 1–7、9–17 项 | 应用镜像和内部入口已在。复核路由只有 Kimi。脚本、写回、A2A 按 F04 保持未装。 | 冻结、交付、单轮和双轮复核、图、外部任务。没有第二笔模型调用。 |
| #105 第 8 项 | #108 之后供给器地址和 CA 已在，prepare 返回 200。 | 网关没有把这次调用收成可关联的供应商回执。claim 与 receipt 不能判通过。 |

## 交回

回执只在本文件。#106 与 #108 的指针和 tag 已由 Jenkins 推送。请求状态未改，目录未归档。L105 没有通过，第 13 项和三道盲测留待 Luna 决定是先修网关回执再复跑，还是按当前发布结果另行安排。
