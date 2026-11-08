# 项目入口指针

本仓是 SunMoonAI 平台的部署与项目文档仓，与 `tpl-app`、`knowfeed-app`、`knowbase-app`、`knowbench-app`、`knowlab-app`、`knowmart-app` **并列放置**（`sunmoon-link` 是客户端仓，不要求并列）。

**先读这一份**——项目现在是什么样（产品定位、仓、拓扑、部署、红线、去哪查）：

`docs/project-guide/overall-architecture.md`

**动结构前必读**——七层加三横切：每样东西归哪一层、层间只有哪几种关系、新东西往哪放（所有者 2026-10-20 定）；代码事实在代码地图：

`docs/总纲/架构总纲.md`
`docs/design/平台代码地图.md`

**专家执行架构最新决定（2026-11-03）**：保留固定财务专家，供用户和AI按声明能力选择；撤销演示后自动退役产品的安排。固定计划与动态计划长期共用执行体系，等价迁移验收通过后才清理旧执行代码。开发前读 [方法架构决定](docs/design/SDD/architecture/methods.md#2026-11-03-最新决定保留固定财务专家统一执行体系) 与 K31；不另建第二套运行逻辑。

我们在建什么、做到哪了、每一站谁做：

`docs/process/pipeline.md`

**动代码前必读**——代码必须符合的规则（按主题分组，含合规 `C-L*`）：

`docs/design/rules/constraints.md`

要建什么（需求的真源）：

`docs/design/PRD/requirement.md`

任何开发任务都要遵守的通用开发规范，以及自己那一类（PRD、SDD、IMP、UAT）的规则：

`docs/process/turn/README.md`

涉及人的批准、裁量或终审时（人介入、权力表、审批档位）：

`docs/process/turn/approvals.md`

部署、运维、某个组件怎么维护：

`README.md`（仓根）与 `docs/README.md`（维护导航）

不在此复述其中规则。

## 必须知道的几条（规矩原文在指向的位置）

| 规矩 | 原文 |
| --- | --- |
| **专家线的合规边界**：投资逻辑与数据只来自用户，我们只做工程化与测试，专家只归用户自己（所有者 2026-10-16 定） | `constraints.md`「合规」、`tree-build/SDD/modules/0026-knowlab.md` |
| 配置、实现与说明同职责目录放；版本与共享环境单一来源；秘密只在私有目录与 SOPS；实施入口只用原生 Make / Ansible / Flux，不加重复 CLI 或转接层 | `constraints.md`「发布」`C-R13`、`C-R14` |
| 部署声明保留平台 → 应用 → 组件三层；应用统一 `app_namespace`；应用共用机制只在 `app-platform/common`，改了要证明既有应用渲染对象不变、不碰已完成的不可变 Job | `constraints.md`「发布」`C-R11`、`C-R15`、`gitops/components/README.md`、`gitops/components/app-platform/common/README.md` |
| 应用构建国内源优先，失败按规则切一次官方源 + 代理；只在 `infrastructure/applications/config.yaml` 选 `domestic` 或 `official-proxy`；证书、签名、哈希校验不得关闭 | `infrastructure/applications/README.md` |
| 开发阶段维护窗口 2 小时、容量底线 10 GiB（真源 `infrastructure/host/config.yaml`），不关容量检查、不因此授权删数据 | `docs/README.md`、`infrastructure/host/README.md` |
| 正式文档以维护者日常操作为中心，入口只导航，不写未验证的功能，不放明文秘密 | `docs/README.md`「正式文档怎么写」 |

## 开发密码查阅表（所有者确认，2026-10-05）

仓根 `密码修改表.md` 由所有者保留，开发阶段允许保存实际登录密码供本人查阅。它不是部署真源，不得改成纯索引或删除密码；组件私有输入与 SOPS 机制照旧。实际账号轮换且登录验证通过后才同步本表；旧体系条目和待轮换目标须明确标注，不能冒充当前凭据。**不得在对话、日志或 diff 输出中显示密码，不得读出来代填**，不自动 push；生产上线前轮换开发凭据。其它文件继续遵守不保存明文秘密的规则。

## 日常交回与推送（所有者 2026-11-08 最新决定）

助手默认完成修改、验证、提交后，立即用当前工位的 `docs/sync-cowork/sync/sync.sh push <本次涉及仓>` 推送，再汇报提交号、验证和各推送端结果。本地与远程助手都遵守，无需逐次请示。所有者临时要求“不推送”、指定推送目标或时机时，以临时指令的范围与期限为准；期限不明不自行认定已结束。此决定取代 2026-11-07 的“助手只提交、所有者推送”规则，旧任务卡沿用旧默认的文字以本条为准。默认推送不包括他人未授权的工作、强推、部署、付费调用或凭据文件；子仓先推，父仓后推。详细分工见 `docs/sync-cowork/README.md`。

## 统一协作请求（所有者 2026-11-08 决定）

接到开发、评审、验证、发布等协作任务时，先读 [协作请求使用说明](docs/sync-cowork/协作请求使用说明.md)，再读指定的 `requests/<发起身份>/<任务>/request.md`。请求与回执共用任务目录；按当前协作身份而非模型名归档，Opus以qwen身份工作时归qwen。只接明确指派，不自动执行同步提示里的旧卡。Git操作串行，默认验证、提交后推送；所有者临时指令优先。

协作请求结案后，由发起者核对成果、记录结论并将整个任务目录移入 `docs/sync-cowork/archive/<发起身份>/<任务>/`，修正当前引用；执行者不代替发起者删卡。同步仅显示请求目录入口，不逐条打印旧任务。
