# #128 工坊和专家匹配体验合并补发

发起人为 Luna，发布执行人为 Cursor，发布后由 Luna 验收。两张原卡的代码评审已通过。当前待合并发布与现场验收。

| 组件 | #128 基线 | 已审候选 |
|---|---|---|
| KnowLab API | `7e67b587` | `b089eb187c3a63d643a91129287c23b6eafe4956` |
| KnowLab Web | `36c13dae` | `d5b9477ec242db24e2b6bfffb34c0c799c4ba402` |
| KnowBench Web | `88514dd7` | `ecc32a199eff196e2be53e3164e28d5a0252c433` |

KnowLab 父仓候选为 `7c42f27346ec34b93141c3ab47389eee724b2256`，分支 `luna-128-studio-create-delete`。KnowBench 父仓候选为 `4b37b6482eb312b2d68bba4796f8f7a6ef199c5d`，分支 `luna-128-match-clarification`。两者均基于 #128。KnowLab 库版本为 `20261126_0030`。

2026-11-27 Luna 比对共享开发环境，三个 Deployment 的镜像摘要仍与原 #128 回执一致。发布时在本卡记录实际组件提交、镜像摘要、Flux 修订和部署结果。[原 #128 镜像清单](../../../archive/luna/2026-11-27-专家方法重构三端体验发版/replies/cursor.md)

## 现场验收

- 工坊创建草稿后直接进入编辑器，原作者可重开“三表核验”并刷新。用专门新建的同名测试稿验证按编号删除，刷新确认另一份仍在。[原请求](../../../archive/luna/2026-11-27-KnowLab工坊创建成功误报失败补发/request.md) · [评审回执](../../../archive/luna/2026-11-27-KnowLab工坊创建成功误报失败补发/replies/agy.md)
- 打开已有澄清任务，核对问题下方的回答框、提交按钮和 ¥2 提示。刷新后确认正文、侧栏和折叠按钮可用，再核对窄屏展开。本轮现场检查无需提交收费匹配。[原请求](../../../archive/luna/2026-11-27-KnowBench专家匹配澄清作答补发/request.md) · [评审回执](../../../archive/luna/2026-11-27-KnowBench专家匹配澄清作答补发/replies/agy.md)
