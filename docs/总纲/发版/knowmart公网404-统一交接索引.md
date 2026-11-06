# knowmart 公网 404：并入统一交接第16节

所有者在外部演示机由 knowbench 跳商城，经 Casdoor 登录后在正确地址 `/zh-CN/knowbots` 收到404。Luna 已核实公网边缘和集群 frpc 均漏了 knowmart；应用路由/回调已有，无需重新配对电脑。

- 真源：`/home/zymun/worktrees/luna/sunmoonun/docs/总纲/发版/2026-11-03-新版财务测试合并发版交接.md` 第16节。
- 修复提交：sunmoonun `b5733135f9a8d664e734074bca9e0bc3b452d819`，分支 `feat/idea-method-entry`。只取这个增量；第15节应用候选保持原SHA，不发布累计开发HEAD。
- 范围：edge_domains、frpc_domains/断言、原生stage生成的frpc代理及Deployment滚动摘要，文档与3项模板回归。Secret、镜像和其它组件未改。edge-plan和定向stage通过，Luna未部署。
- 本修复不需要新建knowmart镜像。frpc声明须入Jenkins所晋级的Flux候选；东京边缘另在正式checkout执行既有edge-plan/edge-deploy，不能仅发布应用后宣称已修复。
- edge-deploy有配置变化时会重启共用边缘服务；先核所有用户活动任务和维护窗口，不自行停用户任务。保持Casdoor路径限制和其它内网域名边界。
- 验收包括公网证书、frpc两副本及新滚动摘要、knowmart页面/登录回跳、已有入口回归。最后演示机登录待用户实测；本机hosts直连成功不能替代公网验收。

Qwen 工位统一交接正文已有未提交修改，本文件不覆盖它。合并时保留 Qwen 回执，把真源第16节并入同一发布记录；详细命令、副作用、停止条件和回退见真源。


2026-11-03 补充：统一交接第17节已记所有者“两轨并存、固定版本保留”决定，文档提交 `8056c851`（Luna feat/idea-method-entry）。本批仍按第15+16节推进，不将第二轨累计HEAD混入。当前只读无运行中测试，仅固定专家第1版任务 `45932c61-fb7f-49b8-92b6-4bee53c5c0c3` 在WAITING(DATA)、无active_attempt；保留它，触发前再核新任务与真实app-server turn。不要把该检查写成“全线程已空闲”，不要代确认数据或启动付费重测。


所有者最新长期决定已记录于 Luna 提交 `8bdabc0f`：两轨并存仅到2026-11-04实际演示结束；随后删除旧固定执行及临时兼容，固定计划统一进动态体系。统一交接17.1、方法架构与K31为准。今晚保留固定演示备用；不要把长期删除决定误执行为本批立即下架/删除，也不要将双轨写成永久保留。此增量仅文档，不新增镜像或部署任务。
