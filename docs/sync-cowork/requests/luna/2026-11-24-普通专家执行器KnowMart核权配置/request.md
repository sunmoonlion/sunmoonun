# 普通专家执行器接入既有 KnowMart 核权关系

Cursor 负责发布，Luna 负责用保留的普通委托验收。请从 #117 晋级指针 `3c4761985` 或包含它的最新晋级线上摘取 sunmoonun `3ed82cd54`。此提交仅给 knowbench-runner 的 envFrom 增加现有 knowbench-knowmart-summon-service 引用。使用当前晋级线的镜像、配置和已有服务凭据即可。

## 现场依据

sig-am 工作台已经选中自用 M02 v2。六步执行预览通过，预算上限 12 元，预览上限 5.46 元。确认后，执行器在首步向 KnowMart 复核正式工具使用资格时反复报告 `summoning from knowmart is not configured`。#117 的 API 和 worker 均具有这个服务关系，runner 缺少引用。runner 到身份服务的 TLS 握手已成功。本地已渲染 runtime 清单并确认仅这一处引用改变。

## 发布回执与业务续验

1. 发布前确认运行命名空间中已有该 Secret，对照晋级差异仅涉及 knowbench-runner 的 Pod 模板。按现行发布规程应用和等候 runner 滚动就绪。
2. 用新 Pod 回读 envFrom 名称，并在 runner 中调用 `service_relation("knowmart", "summon") is not None` 只输出布尔值。记录发布编号、提交、新 runner 就绪状态和检查结果到本卡 `replies/cursor.md`。由 Luna 接手审批与付费验收。
3. Luna 续看原业务执行 `e8f93cc5-0845-4fc1-8d74-01ce661a0dcc`。核对六步的版本、报价、资料，逐次审批，检查交付的五项差额、十四行出处和实际费用。如果等待期间任务已终止，先核清终态、既有调用与费用，再决定是否需要新执行。

[本次业务验收回执](../2026-11-24-M02孵化选型目录能力修复/replies/luna.md)
