# Luna 现场体验验收

2026-11-27 在共享开发环境复核发布 #128。Flux 的 platform 以及 knowlab-runtime、knowbench-runtime、knowmart-runtime 均已应用 `sha256:36fc3381842b3df6400f7e2d69330678eedef32dde4f5bb2093e5ddbc447e606`，状态 Ready。三端迁移 Job 全部 Complete，API、Web、管理端、worker、scheduler 与 KnowBench runner 均为 1/1。[构建、镜像与迁移记录](cursor.md)

| 登录后的入口 | Windows Edge 现场结果 |
| --- | --- |
| KnowLab 方法工坊 | zymun 打开 `/zh-CN/studio`，看到了 S1–S4 四种样板、方法名称、方法形态和在孵草稿区。 |
| KnowBench 方法与技能 | sig-am 打开 `/zh-CN/workbench/methods`，逐个切换三个页签。可用专家与工具列出 M02 v2 及其子方法，本地技能页显示连接器与脚本，两次切换后可返回原清单。 |
| KnowMart 我的小店 | sig-am 和 zymun 分别打开 `/zh-CN/shop`。sig-am 能看到自己的正式方法、版本、上架状态和监管类目。zymun 的同一栏显示暂无正式方法条目。 |
| KnowMart 运营条目审核 | 以 admin 登录并打开 `/zh-CN/market/listings`。管理员身份接口和审核队列接口均返回 200，正式方法、知识条目、申请公开的专家三个分区均显示“没有等处理的。”现场没有待审样本，未验证单条记录的批准或驳回。 |

**#124 退役入口。** 在原作者 zymun 的已登录会话中，旧固定包父申请详情返回 404，申请看板与专家看板均返回 200，且不含旧申请编号。sig-am 打开自己的新综合财务申请，返回 200，响应和申请看板都含正确的新编号。另在本版 KnowLab API 的只读事务里复核运营列表，旧编号已排除，新编号仍可读。

本单按 #128 的版本验收。后续编译器补充与旧入口清理单独提审。本次只查看、切换页面和读取记录。

2026-11-27，四个登录入口及 #124 退役行为验收通过，#128 体验发版单结案。
