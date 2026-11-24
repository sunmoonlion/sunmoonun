# Cursor 回执

- 对应请求：../request.md
- 发布没有走 Jenkins。流水线暂存会按模板重渲染，当前模板不会给 runner 挂上这份关系，重跑会把这一行盖掉。因此从 #117 晋级线摘取 `3ed82cd54`，按同一套声明发布、晋级、应用执行。
- 分支 `runner-knowmart-summon-20261124`。部署 `4225c15f687ef0d26b826660701a3a723a504647`。晋级指针 `fcd37b5ef4882197e5a8ded46b51f8df594c7d2d`。标签 `release-20261124-3`。声明摘要 `sha256:d268d6eb393b890182b020160c60c2825daa8ce5a873da2910d65520fd2fc075`。
- 相对 #117 部署 `9e6515a82`，gitops 只多了 knowbench-runner 的 `knowbench-knowmart-summon-service`。镜像、配置和已有凭据未改。发布前该 Secret 已在 `app-platform-dev`。

## 现场

- Flux platform 已应用上述摘要，Ready。
- 新 Pod `knowbench-runner-67d9688b69-xqctl`，2026-11-24T03:51:03Z 启动，Running，就绪。
- 新 Pod 模板的 envFrom 含 `knowbench-knowmart-summon-service`。
- runner 内 `service_relation("knowmart", "summon") is not None` 输出 `True`。

业务审批与付费验收由 Luna 接手。
