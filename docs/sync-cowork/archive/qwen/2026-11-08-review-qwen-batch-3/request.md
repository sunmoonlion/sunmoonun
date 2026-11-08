# 审查：opus-qwen 第 3–5 步这一批修复（11-08）

- 类型：评审
- 状态：已完成
- 发起身份：qwen（使用 Opus）
- 执行身份：agy
- 主工位：远程 ~/worktrees/qwen
- 仓与分支：下表各仓，都在 qwen 分支
- 待评版本（完整提交号）：
  - knowbase-app/knowbase-backend：`1a7889421dac7a3d854541b0b3d012eceebd215a`、`7875a8b5e5b15a83163d6fe42e95aab0737f2482`、`d1b10f9a6749821ee40a8275e070d381cb786aed`、`c7dc805bdbefe2298b3080be65f55769ca6d14cd`
  - knowbench-app/knowbench-backend：`44f2f28ec6b3b76f832050d164449494f9b5e8ba`、`4e4ba5ed4808ec221adab3f0bcb83d9267346bb3`
  - knowbench-app/knowbench-web-frontend：`5fd34c6dbfce71e467f30fa046083f29df2ee76f`
  - knowfeed-app/knowfeed-backend：`3390ee54c9df983bd571300476112b304ccf3af7`
  - knowmart-app/knowmart-backend：`a326fbcc58bfef2b6bc1e75d49707864d1023083`
  - tpl-app/tpl-backend：`2f583804214d9c2c9b77421ff25c843cd5066af4`
- 回执：replies/agy.md

> 统一请求迁移（2026-11-08）：类型：评审；发起身份：qwen；执行身份：agy；状态：沿用原请求状态；本次只迁移目录。后续交接回执放本任务 `replies/agy.md`。保留以下历史正文和证据；旧文中的默认推送及移入done要求由[当前协作规则](../../../协作请求使用说明.md)取代，本次迁移不恢复、重启或重新授权任何任务。

> 发卡：qwen（由 Opus 执行，远程 qwen 工位），2026-11-08。执行：agy。**只审不改被评文件**，规矩同上一张卡 `../2026-11-08-review-qwen-23-frozen-binding/request.md`：在 `~/worktrees/qwen` 只读被评内容，测试库与跑法也一样。

## 目标

逐个提交审：修法对不对、有没有漏的、测试够不够。
另有几条，Opus 核实后定为「不成立 / 不改 / 撤回」，请你判断这些结论对不对。依据见 `sunmoonun/docs/总纲/opus-qwen.md` 第九节。

## 要审的提交（都在 `qwen` 分支）

| 仓 | 提交 | 对应条 |
| --- | --- | --- |
| knowbase-app/knowbase-backend | `1a78894` | 5：0051 的类型贯通 |
| 同上 | `7875a8b` | 1、2、21：产出许可上限照 10-30 约定；回显按存下的出处 |
| 同上 | `d1b10f9` | 3、9：采集件跳过删了副本的受益人；先核描述和依据再存 |
| 同上 | `c7dc805` | 8、22：PDF 识别名额；升档摘要由服务给出 |
| knowbench-app/knowbench-backend | `44f2f28` | 25：两条过时的测试 |
| knowbench-app/knowbench-web-frontend | `5fd34c6` | 25：同一份快照 |
| knowbench-app/knowbench-backend | `4e4ba5e` | 13、22：字面量指数；命令唤醒抽成模块 |
| knowfeed-app/knowfeed-backend | `3390ee5` | 22：注释归位、变量改名 |
| knowmart-app/knowmart-backend | `a326fbc` | 15：被拒的那一批记告警 |
| tpl-app/tpl-backend | `2f58380` | 26：迁移清单 |

**重点请看 `7875a8b`**：按受益人和 ref 去查授权，不管执行方是谁。这个口径会不会把别的执行方、同名 ref 下的授权错算进来？会话时间窗那部分，用的是「签发时间在窗内」或「窗内有读数」，请判断是不是太宽或太严。

**改判的几条**（第 6、7、10、11、12、14、16、17、20 条），每条请回：同意，或者不同意并给出依据（文件:行）。

> 2026-11-08 协作目录迁移：发起者 qwen（由 Opus 执行），评审人 agy；回执改在 qwen 工位，不改变原审查范围。状态：待评审（若已有回执，由发起者核对后更新）。

## 交回

- 回执写到 `~/worktrees/qwen/sunmoonun/docs/sync-cowork/archive/qwen/2026-11-08-review-qwen-batch-3/replies/agy.md`，注明实际评审提交、结论、文件定位、建议及未验证项。
- 在 qwen 工位仅提交自己的回执，Git 操作与开发助手串行；向所有者报“已提交、未推送”。
- qwen 在本请求记录采纳情况及修复提交，完成后原位标记“已完成”，保留请求和回执。

## 处理记录

| 日期 | 事项 | 处理 |
| --- | --- | --- |
| 2026-11-08 | 补头部字段（状态、完整提交号），按《协作请求使用说明》第 4 节 | 发起者补；正文与评审范围不变 |
| 2026-11-08 | agy 回执（[replies/agy.md](replies/agy.md)）：10 个提交都通过，9 条改判全部同意 | 收到，无需改 |
| 2026-11-08 | 重点 `7875a8b`：按受益人加 ref 查不限执行方、会话时间窗用「签发在窗内或窗内有读数」 | 同意 agy 的分析：各过程的 ref 是编号或带前缀的单号，又限定了受益人，不会串；时间窗既不漏也不宽 |
| 2026-11-08 | `d1b10f9` 备注：整批都被跳过时，knowfeed 会重试 5 次再收口 | 同意留作以后的优化（已记在 opus-qwen 第九节） |
| 2026-11-08 | 结案 | 线上验收随下次各应用发版 |

> 2026-11-08 归档：发起者 qwen 已在上述处理记录结案；Luna 按所有者本次清理要求整包归档，保留原回执及待上线验收说明。后续按当前协作规则，不再留在 requests。
