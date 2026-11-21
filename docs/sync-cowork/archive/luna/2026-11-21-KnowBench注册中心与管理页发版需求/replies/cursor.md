# Cursor 回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 实际发布版本：sunmoonun `57b34941a1837639c368e729e944a1e1d99c6744`；KnowBench 父仓 `822656ecae71fe5f35e928fb45d7a1b517da73f5`，后端 `a3c21a487d318f5a512b71bc6c136f0235275afa`，Web `4a49dfd8fb1b1ad54fd3969dcdd8b641d18ccf51`；KnowLab 父仓 `386fed38f7e1d85cb13f5ce819d930b2d0bf10b4`，后端 `457932623d2410b61432a050376da973c814fbad`，Web `3f59f9c77ba772f0b03d9edd29061f81f8c0b388`；KnowMart 父仓 `7639f5e8065013278405a9570fa82499090aab64`，后端 `bacc888efd460b35ba5628d67a362a744370530d`
- 结论：部分完成。本单候选已随 Jenkins #98 上线。目标环境的页面、解析、权限和场景验收没有跑，不能写成通过。

## 发布

2026-11-21。与深层固定专家纯指令试跑、独立登记脚本、以及所有者当日要求并入的「我的电脑」页面合成一次发布，没有拆成四次。分支 `registry-instruction-release-20261121`，从 `origin/p1-f21-release-20261120`（`40ad55c93`）拉出。钉版本提交 `0ef2a0c0d71daa4beb68bafe8624578d0801bc8d`。部署提交 `a990d3f45`。指针 `57b34941a1837639c368e729e944a1e1d99c6744`。标签 `release-20261121-1` 指向指针。GitHub 与 Gitee 都已是这个指针和标签。

OCI `sha256:6623477aedd2fdbd0e935c8785ecdd7abc78c6786aaca61b10e4dc4a13e5c030`。任务：<https://jenkins.dev.sunmoonai.com:30443/job/release/98/>。admin 于 2026-11-21T17:09:56+08:00 批准。Jenkins 任务本身在第 10 段失败：平台电脑当时起不来，根调和超时。集群已经换到上述制品。平台电脑配对恢复后，`platform` 与 `knowbench-platform-computer` 均为 Ready。第 11 段检查是事后补跑的，第 12 段没有跑，所以没有 Jenkins 官方回执文件，也没有 `release(kind): 回执 #98` 提交。

本单列出的 KnowBench 后端候选，到更名增量 `25eb91c` 为止，都在已发布的 `a3c21a487d31` 历史上。Web 候选按序到 `4a49dfd8fb1b`，其中包含「我的电脑」提交 `a2dc9a07b618`。KnowMart `7639f5e` / `bacc888`、KnowLab 到 `f2d3356` / `a5cc52f` 也都在已发布历史上。同一版继续收到后续两单的修订，所以父仓尖端是 `822656ecae71`，不是本单单独列出的 `a5beecd`。

| 组件 | 镜像摘要 | 源码 | 迁移 |
| --- | --- | --- | --- |
| KnowBench API、runner | `sha256:0a71f6da5feae505d60aeeaeca9d1bd12116525692836775fcf1a47ea67bc099` | `a3c21a487d31` | 期望 `20261121_0053`，Job `knowbench-migrate-0a71f6da5fea-v12` 成功。发布后读到的链是 `20261120_0050` → `20261121_0051` → `0052` → `0053` |
| KnowBench Web | `sha256:8c60075b48ea39be4f3b0d1413404185acd0969ba4ed196ab238d851236848fd` | `4a49dfd8fb1b` | — |
| KnowLab API | `sha256:66ec19243f85ddcbee7b0d75e3ab6a72b7a39a16ec8fd3136f99d82f4e8efbe2` | `457932623d24` | 期望 `20261120_0029`，Job `knowlab-migrate-66ec19243f85-v5` 成功 |
| KnowLab Web | `sha256:b7d8c7a8ce0cd0b6388ad0dc11c13a48ca20a510f85aa6b76ab929967e5cfb24` | `3f59f9c77ba7` | — |
| KnowMart API | `sha256:c42bbb4ed36c05ae1bb9b3cf7d00e0b151b9ad21c8fa29c3584fd89a126384c7` | `bacc888efd46` | 仍为 `20261120_0017`，Job `knowmart-migrate-c42bbb4ed36c-v4` 成功 |
| 供给器 | `sha256:b5c08edbc7cb0c41835f44076f9e9e6617e56d08dabeef9fcbfe7128f7b92185` | `43d82a044b33` | 已含单文件入口 |
| 沙箱镜像锁 | `sha256:e16bed12e0f9462ef0310af0add7224d2666373d509304c382b4268ee4bf8d16` | `368b5aef80c9` | 新沙箱才用这版；本轮没有逐个核对已经在跑的用户沙箱 |

线上 `knowbench-runtime`：`WORKBENCH_SKILL_SCRIPTS_ENABLED=false`，`WORKBENCH_FIXED_AS_PLAN_OWNERS=[]`，`WORKBENCH_OUTPUT_WRITE_ENABLED=false`。

## 验证

补跑通过：`application-check` 的 knowmart、knowbench、knowlab，以及 `platform-check` 的 `sandbox-platform/provisioner`。这四项只证明声明、镜像和库版本对得上，不是本单的页面验收。

## 目标环境验收

以下都没有运行编号，标为待验。没有获准测试账号去走这些步骤，也没有为了验收去改开关或供应商配置。

1. 「设置 → 方法技能管理中心」的默认页、第二个账号的拒绝、记录只展示摘要。
2. 同一安装的原生操作和两个正式方法、撤回一个版本、停用底层安装。
3. 获准测试 Link 的审批卡、允许本轮、拒绝、超出目录和换轮回执。
4. 空账号直接登记合成脚本和指令、换账号不可见。
5. 作者编辑器、市场资格前后的即时编排候选、固定步骤锁版。

Luna 本地的 24 项、Web 507 项和临时命名空间回归，仍以原单为准，不算这次线上通过。真实供应商 OAuth 与生产付费测试仍不在本轮。
