# 审查：opus-qwen 第 3–5 步这一批修复（11-08）

> 发卡：qwen（由 Opus 执行，远程 qwen 工位），2026-11-08。执行：agy。**只审不改被评文件**，规矩同上一张卡 `2026-11-08-review-qwen-23-frozen-binding.md`：在 `~/worktrees/qwen` 只读被评内容，测试库与跑法也一样。

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

- 回执写到 `~/worktrees/qwen/sunmoonun/docs/sync-cowork/inbox-review/qwen/replies/2026-11-08-review-qwen-batch-3/agy.md`，注明实际评审提交、结论、文件定位、建议及未验证项。
- 在 qwen 工位仅提交自己的回执，Git 操作与开发助手串行；向所有者报“已提交、未推送”。
- qwen 在本请求记录采纳情况及修复提交，完成后原位标记“已完成”，保留请求和回执。
