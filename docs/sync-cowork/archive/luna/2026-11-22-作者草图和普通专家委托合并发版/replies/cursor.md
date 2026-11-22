# Cursor 回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 实际检查版本：sunmoon-kind 发布 #105。部署 `5cb6b5ec2ac8fda58fefbfd3d924516282d0cdb8`，指针 `520fdd77dc567e31b67a37855bfca2f8c0698638`，tag `release-20261122-3`，Jenkins 回执 `scripts/results/release-105.20261122-152349.md`（提交 `8b307c16f`）。
- 结论：部分完成。镜像、库版本、内部入口和协议检查已在 sunmoon-kind 落地。第 1–17 项的目标环境行为没有可跑的冻结方法、已收产物、复核路由或合成供应商，未判通过。下一步由 Luna 决定。

## 发现

- F01：发布本身成功。admin 于 2026-11-22T15:15:26+08:00 批准，任务 https://jenkins.dev.sunmoonai.com:30443/job/release/105/ ，结果 SUCCESS。部署 OCI `sha256:d2d4311d782926053acc331c2cd331d862c09e1b2994ad51777550c09a93e271`。Flux platform 对该摘要 Ready。
- F02：既有用户沙箱不会随供给器自动换镜像。供给器已指向新沙箱镜像，现场七个用户沙箱里只有 sig-am 这一份换成新镜像。其余六份仍是 #104 的 `sha256:c886456b1aed9cd50f161baaf9675be8d228431bde3fba5050bbe662d544489b`。
- F03：`knowbench-runtime` 没有 `WORKBENCH_REVIEW_ROUTES`、`WORKBENCH_REVIEW_MODEL_GRANTS`、`WORKBENCH_INSTRUCTION_ROUTES`。三项派发开关保持关闭。脚本路径因此不能当通过。
- F04：sig-am 在 KnowLab 没有可冻结的方法或专家，方法技能管理中心没有正式登记，也没有直接登记的脚本或指令。连接与工具页没有可用能力。第 1–17 项依赖的隔离作者、已收产物、已冻结指令图和合成供应商都不在这个账号上。
- F05：验收时点过 sig-am 的「更新沙箱」。没有重新颁发 knowbot-tester 的令牌，没有保存复核偏好，没有对现有研究对话发模型请求。

## 发布

环境：sunmoon-kind。应用命名空间 `app-platform-dev`，沙箱命名空间 `sandbox-platform-dev`。分支 `author-delegation-release-20261122`。NOTE：作者草图与普通专家委托同一版发布，三项派发开关保持关闭。APPS：knowbench、knowlab、sandbox。PIN=heads。KnowMart 未进入本批。

| 对象 | 父仓 / 子仓 | 镜像 |
| --- | --- | --- |
| KnowBench 后端 API / runner | `9af9371f938fcb83733050b59683cbc26d43dea5` / `df93384f3f70a268d84c5c0db83deb8ff16ccc88` | `sha256:3ed02f9d3d64e347894a343cf2dca18c80c41aeb63f96bc98b60ee005e87c025` |
| KnowBench Web | `87598bd70ac2865cb9deba20571cf56759c13366` | `sha256:2850fd13ae5fb102dac23a981cb7bbe090c63fb3a415f9b6de0eaaa5c0f5af0a` |
| KnowBench 管理 Web | `33559e926c3ebb7570716d5bb318b5a014e0d645`，与 #104 相同，未重建 | 沿用上一版 |
| KnowLab 后端 | `a7dae5b83b63cebbe575ca708b1f2a9f28bdd0c0` / `f14182fa724b64f2a5170f517c8786655d29ad27` | `sha256:764f154693d8254798eb32f7ae1e03d5535a907f286cca6e2fa5fb56f806aeed` |
| KnowLab 作者 Web | `9edf1a0051b8bd7c1356b14aad296033113fe14d` | `sha256:fc6b0d50a7cddbc09ba8a78a0184ccf10bfcaac72459295bb5b64a52e956fa91` |
| KnowLab 管理 Web | `89fe3ac1f6178018186584db7542f11102896381`，与 #104 相同，未重建 | 沿用上一版 |
| 供给器 / 沙箱 | `edd9b00f569a5bae30e4261de67555cd234e81fd` | `sha256:932097966a661641838c7eec5c2ec27a8f6cd66f409bc812290d0f6ee28ebf5a`、`sha256:8fc0460292c0ad31a697f390dbbb4a45d9bc86a29f41d2b0a34965b163066475` |

部署修订 `5cb6b5ec` 的内部入口配置含 `/api/internal/v1/instruction-control`，对应候选 `a019168945de8d2491de2633523e2b793a8b2f0d`。

协议检查：knowbench ok=50 failed=0，knowlab ok=45 failed=0，sandbox ok=23 failed=0。证据在 Jenkins 构建的 `11-check-*.log`。

库版本：`knowbench-migrate-3ed02f9d3d64-v13` 完成，流水线预期 `20261122_0058`。`knowlab-migrate-764f154693d8-v5` 完成。发布后从 KnowLab API 读到的 alembic 头仍是 `20261120_0029`。`knowbench-identity-3ed02f9d3d64-v9`、`knowlab-identity-764f154693d8-v8` 完成。

现网 `knowbench-runtime`：`WORKBENCH_SKILL_SCRIPTS_ENABLED=false`，`WORKBENCH_FIXED_AS_PLAN_OWNERS=[]`，`WORKBENCH_OUTPUT_WRITE_ENABLED=false`。复核路由、模型授权、指令路由三个键不存在。

## 现场

账号 sig-am。浏览器打开 KnowLab `孵化` 与 KnowBench 设置。没有打印令牌或 key。

- KnowLab 页面：自己来 0，平台孵化 0，专家 0，待办 0。全库 `knowbot_method` 0、`knowbot_method_version` 0；全库草稿 12、专家 4，未按该账号拆开。
- 方法技能管理中心：正式方法「没有符合条件的登记」；脚本和指令「还没有直接登记的脚本或指令」。
- 连接与工具：「还没有可用能力」。
- 模型页有「默认复核助手」。计划主笔显示 kimi / kimi-k3，复核连接显示「自动选择唯一可用连接」。没有点保存，所以没有保存重开的证据。账号上有两条有效的 kimi 凭据。
- 电脑页：zymun 的本地 link 连着，Codex 0.170.0。更新前沙箱就绪、配对成功。点「更新沙箱」后，`sandbox-u-0c520909ee72` 为就绪 1，镜像 `sha256:8fc0460292c0…`。令牌到期日仍是 2026-12-21。另一台已登记电脑显示没连着。

请求里的本地 55、80、518 项没有在本轮重跑，不作为本集群通过。

## 第 1–17 项

| 项 | 本次能核对的 | 未跑 |
| --- | --- | --- |
| 1 | 新 KnowLab Web 已上线。sig-am 没有方法可保存、重开或冻结。 | 缺隔离阻止执行、交付资格、KnowMart 审核和精确版本获取。 |
| 2 | KnowMart 沿用 #103，本批未改。 | 买方与未获取目录、委托预览、逐步审批、根交付和重启后的调用身份。 |
| 3 | 部署前后镜像见上表。没有新的委托或调用。 | 脱敏委托号、调用号，以及回退后的试跑证据。 |
| 4 | 模型页能看到默认复核助手，未保存。 | 没有已收产物，未进入「去 KnowBench 选复核助手并核对交接范围」。保存重开、撤销失效、缺报价、旧产物只存候选，都没有样本。 |
| 5 | 无。 | 单轮派发、根预算、Attempt、线程、产物，以及同一确认打开原委托。 |
| 6 | 无。 | 严格双轮的两轮请求、封存发现、根账，以及第二轮失败时首轮仍可查。 |
| 7 | 项目列表没有进入「查看复核意见」。 | 裁定保存、另一账号不可读、单轮不得显示成双轮。迁移 0058 的表随 v13 作业落地，没有新写入的裁定可核对。 |
| 8 | 已部署修订含内部指令入口。 | 测试委托上的 `claim` 和 `receipt` 没有实调用。 |
| 9 | 两端 Web 与契约检查同批通过。 | 导入定义后角色来自导入版本，以及发送前校验失败释放预留。 |
| 10 | 脚本开关仍关。 | 两个冻结指令的合格两笔费用，以及不合格时复核无外发、无费用。 |
| 11 | 工作台有「请专家」入口，本轮没有从新会话发起。 | 冻结版本、逐步批准、最终产物和重开后的委托编号。 |
| 12–14 | 无。 | 审批超时、二选一子专家、两对象清单及到期只收已完成对象。 |
| 15 | 连接页没有外部 A2A。 | 提交、查询、取消，以及丢失响应后只补一次。 |
| 16 | 无。 | 子委托交接、父调用结案、取消后的迟到回执。 |
| 17 | 无复核路由配置，无两步或三步测试图。 | 真实请求字段、供应商模型、独立线程与容器、两次返工后等人裁定、断线恢复和 worker 目录。 |

## 交回

回执只在本文件。发布分支、指针和 tag `release-20261122-3` 已由 Jenkins 推送。请求状态未改，目录未归档。第 1–17 项留待 Luna 决定是补测试物料后再验，还是按当前条件结发布、另开验收。
