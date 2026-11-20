# KnowBench 连接器与脚本操作卡发版需求

**正式发版需求，交 Cursor 执行。** 所有者于 2026-11-20 调整顺序，本轮按已处理的分项回执发布，包含 Codex 0.170.0。agy（Opus）全局审查保留，结论由 Luna 处理后排入下一版。

Luna 已处理 [C5 分项回执和五条修订](../../../archive/luna/2026-11-20-C5专家分步执行与脚本计费复核/request.md)。Cursor 可开始本轮已复核范围的发布。C1/C6 的独立回执仍由 agy 写在本目录 `replies/agy.md`。在回执及目标集群验收完成前，保持用户脚本开关关闭，发布说明按实际完成的范围填写。真实供应商待专用账号、授权范围和回调。Cursor 完成后在 `replies/cursor.md` 记录实际部署、开关、包版本及线上核验。

## 候选版本

| 仓或组件 | Luna 开发提交 |
| --- | --- |
| KnowBench 应用 | `0b56e0a7b2f4f9ff7a2b7e45452a358acb891927` |
| KnowBench 后端（含 runner） | `4aa68b7d0fe58b9d78c7ebc14742790da3840c02` |
| KnowBench Web | `11a3fd728ad63d35d47cd2b1a9bd60d2850ce5ea` |
| KnowLab 应用 | `8bbce621c053a861d8e7bcfad1b6ebdeb4c67163` |
| KnowBase、KnowMart 配套应用 | `9552fba44565e0a71b5a8f0d9d921b217537bbba`、`bbc14059920140252c9ebf4977ee763d5c3c71ed` |
| sunmoonun 隔离供给器、权限配置 | `9edd61e02b25bc573fd62e2b886a47a11310d85a` |
| 本地浏览器联调脚本 | `0c5b26f7c72399d217f337275200a789ed872a96` |

本轮 KnowBench 含 C5 分项意见修订及 C1/C6 本地验收。请 Cursor 比较当前部署与上述候选，在隔离发布分支整理本次需要的运行时代码、子仓指针、迁移与组件镜像，记录最终发布提交和相对开发候选的差异。

## Codex 0.170.0 同批发布

| 对象 | 固定来源 | Cursor 交回的线上证据 |
| --- | --- | --- |
| 平台沙箱 | `sunmoonun` 镜像 Dockerfile 自 `5b11c85639cba4c7dedfd09f97bc39db8e14ee59` 锁定 0.170.0，采用上表平台候选构建 | 镜像摘要、目标集群新建沙箱内的 `codex --version` 及 app-server 初始化握手 |
| SunMoon Link 0.5.9 Windows x64 | Link 仓 `13f2c81842b9342557246d370626d75546df1088`，组包提交 `318f79e54cfe2be27fc9ceb722d172a8e757d975` | 已发布下载对象及读回 SHA-256、页面标示的版本、从正式包启动的 Link 0.5.9 与包内 Codex 0.170.0 握手 |
| SunMoon Link 0.5.9 Linux x64（平台电脑） | 同一组包提交 | 正式 Linux 对象的读回 SHA-256、平台电脑升级后的 Link 心跳版本和包内 Codex 0.170.0 握手 |

本轮复测沙箱镜像内 `codex --version` 为 `codex-cli 0.170.0`，Windows 和 Linux 均使用随包原生程序重新完成 exec-server 初始化，返回 `executorVersion=0.170.0`。Luna 复算两个 `edge-public` 本地候选，Windows ZIP 的 SHA-256 为 `807ac5eb4a738b5b785ef014f1bc3293e27483c0afc82a82b5467acdaa1fa135`，Linux tar.gz 为 `6c0cd50f84095739a5f7fb8459da3618d242dc7c55cb1c6131bda371b677e35c`。Cursor 核对目标站点，按对应发行配置构建或取已验包、上传新版本对象并读回，随后更新发行配置中的版本、对象键、源码提交、摘要和大小。目标站点或重建产物不同，按实际产物重新核验并记录。保留 0.5.8 的不可变对象和回退入口。生产用户电脑按既有安装流程获取 Windows 更新。[开发验证与清单摘要](../../../../../scripts/results/codex-0170-mcp-20261119.json) · [发行配置](../../../../../gitops/components/app-platform/knowbench-app/knowbench-backend/agent-releases/config.yaml)

## 可复核的本地证据

- 在 KnowBench 后端独立 PostgreSQL 测试库设置 `AGENT_TEST_DATABASE_URL`，执行 `.venv/bin/pytest -q tests/test_connector_cross_scene_db.py`。同一账号的同一个连接 ID 在聊天、工作和三步专家的读写叶子中出现。合成 HTTPS MCP 服务校验同一凭据，记录每次读取和发送。聊天与工作中的批准、拒绝、读授权复用、撤销或到期按调用账核对。发送端收件后断开，重建服务后仍按原调用返回未知，服务端发送计数只增加一次。此用例的专家脚本由测试执行器驱动；C5 原请求另有专家调用真实容器的证据。
- 构建对应 KnowBench Web，使用 KnowBench 后端的虚拟环境运行[脚本操作卡联调](../../../../../scripts/local-integration/script_card.py)。入口需本机独立 PostgreSQL 的 `*_tests` 库和隔离测试供给器，通过 `AGENT_TEST_DATABASE_URL`、`SCRIPT_TEST_PROVISIONER_URL`、`SCRIPT_TEST_PROVISIONER_TOKEN` 提供。本地 Chromium 点击批准后下载 `answer.txt`，文件字节为 `42`。第二个脚本运行中刷新页面，再从原卡停止，核对两条原始调用及两份 Job 均已回收。浏览器登录和 Codex 工具事件使用测试夹具，能力路由、数据库、执行供给器与 KIND 容器实际参与。
- 真实供应商待提供专用测试账号、授权范围和已登记的回调地址。按所有者决定先交本地结果；外部凭据的授权、刷新、撤销和供应商侧结果另记。

**本次交付候选。** 已按节点名逐项核对 KnowBench 后端 2,942 项，2,933 通过、9 跳过。另在真实 KIND 跑通 3 项容器用例和 1 项浏览器操作卡。供给器 28 项通过，KnowBench Web 503 通过、2 跳过，常规 Chromium 9 通过。Ruff、Pyright、ESLint、类型检查、国际化与生产构建通过。

C5 分项意见修订前的本地基线回归收集 2,940 项，首轮 2,930 通过、9 跳过、1 项在清理测试 schema 时出现数据库死锁。相同代码重跑受影响的完整分片为 494 通过、3 跳过，与其余分片合计核对为 2,931 通过、9 跳过。首轮死锁已交 Opus 核查。三个跳过的真实容器用例另行通过；另六项为三个可选消息队列探针和三个退役样例空参数组。KnowBench Web 单元与组件 503 通过、2 跳过，Playwright 常规 9 通过，另以 PostgreSQL、真实供给器与 KIND 跑通专用操作卡用例。构建、类型、国际化、变更测试文件的 ESLint 均通过。断网容器内以 Codex 0.170.0 和合成 Responses/MCP 核对两轮事件的线程、轮次及调用 ID。旧研究表单用例调整为配对 Run API 的事件流、授权引用与人工确认检查。

## Cursor 发布与交回

1. 按[接入工作单 §17.6](../../../../总纲/mcp和skill接入实施方案.md#176-本次先发布发布后补齐的工作单所有者-2026-11-13-确认)核对独立复核和遗留项。在最终发布候选复验 API、runner、Web 和供给器的版本组合，核对旧标签页刷新、在途任务排空或中止、调用账容量及备份恢复演练。若发布范围缩小，在回执列出实际包含的能力和继续关闭的入口。
2. 由 Cursor 执行既有人工晋级流程，记录 Jenkins 构建号、镜像摘要、数据库迁移版本、部署真源提交及上线前的可恢复版本。用户脚本开关 `WORKBENCH_SKILL_SCRIPTS_ENABLED` 从关闭状态开始。先在目标集群受控验收 Python、Bash、Node 完整包、凭据隔离、网络拒绝、资料输入、产物下载、停止和清理，再按既定开关条件启用并用实际页面复验。收费环境额外核对运营单价版本、容器计量和根预算结算。
3. 用固定 Codex 版本核对真实事件与 Attempt 的关联。用获准的账号验证同一连接在聊天、工作、专家中的读写、拒绝、过期、撤权及恢复。未知写入按原调用核实供应商记录。记录已验场景、未验条件及上线后开关值。
4. 如验收失败，关闭受影响入口，停止新增派发，保存原调用与未结预留。核对外部已生效的写入，按已演练的代码及数据恢复方案回退，记录回退版本和复验结果。
