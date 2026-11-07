# 2026-11-07 全部工位对齐 qwen

所有者授权：确认 qwen 最新后，将本地全部工位和远程三个工位对齐。本轮已确认 qwen 包含其他工位与 GitHub 同名分支的全部提交；未发现独有提交、分叉或未提交改动。

## 范围与结果

- 本地 `/home/zymun/worktrees/`：cursor、fable、kimi、luna、qwen、agy，6 × 26 = 156 个仓检出。
- 远程 `zym@43.153.135.74:1022` 的 `/home/zym/worktrees/`：fable、qwen、agy，3 × 26 = 78 个仓检出。
- 每工位包含 8 个主仓与 18 个子仓。全部 HEAD 已对齐本轮 qwen 快照，保留工位同名分支，upstream 为 origin 同名分支，父仓 gitlink 与子仓 HEAD 一致；两端工作区干净。
- GitHub、Gitee 上 26 个仓的 cursor/fable/kimi/luna/qwen/agy 六条分支均通过普通 atomic push 对齐：子仓先推、父仓后推，未强推、未 reset、未删除历史或文件。
- master 及归档引用不动。不触发流水线、部署或业务任务；没有调用模型或 Wind。代码同步不代表上线或业务验收，qwen-020 暂停发布的状态不变。

## 统一应用基线

| 主仓 | 提交 |
| --- | --- |
| knowfeed-app | `56ed9df09bf21dea70231eb271868182d63af661` |
| knowbench-app | `915e31c489c7e4915690eaf38a602f9390b70859` |
| knowbase-app | `582efeaa4171cab9a2b478872bf14dea84c9f8a5` |
| tpl-app | `2ed1c71904909e8ee128d7b1dc12cbaff0b479a8` |
| knowlab-app | `30e2ae8cad708be8e0fac67ab5b5f3a2d3e73834` |
| knowmart-app | `7cd605ddcd44a1b0234c43d650f5d651ed6281ef` |
| sunmoon-link | `5c41d1fba9af0526af9a26a802a140dba6dd77a6` |

文档仓起点为 `60db835ec99687182748d35e8a1fe29a9faa17c0`，本回执随后同样合入六条工位分支并同步远程三工位。应用提交保持上表值。

## 验证记录

- 本地逐仓验证：156/156 HEAD 等于 qwen 快照，upstream 的提交相同，分支名正确，git status --porcelain 为空。
- 远程逐仓验证：78/78 HEAD 等于同一快照，分支与上游正确，工作区干净；父仓检查包括所有子模块状态。
- Git 托管双端：26 个仓的逐仓推送均退出 0（已一致的返回 Everything up-to-date）。
- 前一轮保留的 link 问题记录及其留存副本未改动。远程工位配置继续含 agy、仓登记为 sunmoonun。
- 本次不改应用实现、不重跑应用测试；核查覆盖 Git 对齐与工作区状态。

以后统一称“远程”和“本地”；远程指上述开发机，不再指云端容器。

exit=0
