# 基础修复与 P1 作者短链下次发版需求

**状态为待 Cursor 接手合并发布。** 原 P1 单暂停期间，Luna 已完成 F01–F21 收回并验通合并候选。请在同一次发布使用下表版本。此前 [#96 发布单](../2026-11-20-C1-C6跨场景验收发版需求/request.md)继续追踪原上线范围的待验事项。[P1 基础修复档案](../../../archive/luna/2026-11-20-第11项开工前基础修复/request.md)

## 同一发布窗口的合并候选

所有者于 2026-11-20 暂停过原 P1 单，要求审查修复完成后同批发布。原 P1 单中的前序候选为 KnowLab `422dcd1`、KnowBench `815a76d`、KnowBase `70f9566`、KnowMart `190f8ce`。Cursor 准备发布时使用下表，核对父仓与子仓指针。平台构建来源继续使用已审定的 `sunmoonun` 清单修订 `8065602d3`，其中两个沙箱镜像的源码均为 `9edd61e02`。旧版 Jenkins #96 的未验项目仍在其原单。

| 应用 | 合并候选 | 对应后端或交付范围 |
| --- | --- | --- |
| KnowBench | `0f031cd78351a1e95d3bfbbb1e2b1e28c736afeb` | `3a3eb862ffb6d752eec84e477c6c6a417dad710f`，含 runner、正式方法生成代码及供给方锁 |
| KnowLab | `c61b98e92c6b2f9254ab3e9ee8dd566eb49e998a` | `185e1ca91d2d114f7d466b89b55d028900e2ca47`，含正式契约提供方，Web 按父仓固定的 P1 版本 |
| KnowBase | `c9ed334702e3dd9e2fd0fd4842b923947d9ed2ea` | `b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b`，资料授权复用及正式读取的编码错误 |
| KnowMart | `190f8ce3282a4ac4dd3cf15448077d7383e8ba58` | 本轮沿用 P1 单的市场候选，验慢交付与并发撤架 |

[全局审查处置与验证](../../../archive/luna/2026-11-20-Luna开发全程逐行代码审查-Opus/request.md) · [P1 作者联调](../../../../../scripts/local-integration/p1_author.py) · [跨服务市场交付](../../../../../scripts/local-integration/formal_market_delivery.py)

## Cursor 发布及回执

1. 核对实际待升级环境与候选的迁移差异。候选 head 为 KnowBase `20261119_0022`、KnowMart `20261120_0017`、KnowBench `20261120_0050`、KnowLab `20261120_0028`。按项目已有发布流程滚动更新，核对退场 runner 的任务与租约、历史冻结版的槽位和依赖回填。
2. 按平台清单构建 sandbox-provisioner 与 sandbox，记录实际镜像摘要。沿用 `WORKBENCH_SKILL_SCRIPTS_ENABLED=false` 及已有授权范围。真实 OAuth 和生产付费测试仍待原先约定的条件。
3. 发布后抽验 P1 补查与采用、保存重开、中途取消、完成和冻结；核对同资料两步同意、递归取消的中间调用状态、排队加审批的等待时间，以及慢交付期间撤架后拒绝新买方获取。正式探针的未知项应留下不通过的证据。
4. 在本目录 `replies/cursor.md` 交回实际发布版本、构建号、应用和镜像摘要、迁移结果、开关、实测与未验范围。由 Luna 收回并归档。
