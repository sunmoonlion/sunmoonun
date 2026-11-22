# 增量审查 R01–R08 修复合并发版

由 Cursor 发布并交回现场证据。目标环境为 sunmoon-kind。与第 14 项重叠的 KnowBench 组件可在同一批构建，第 13、14 项各自的业务验收仍在原卡交回。远程工位约 3.7 GiB 内存，构建、数据库测试和浏览器测试宜串行执行。

## 发布候选

| 组件 | Luna 修订 | 部署动作 |
| --- | --- | --- |
| 平台与沙箱 | 供给器源码及 sandbox 构建上下文钉在 `7798c101b`，镜像清单与契约门禁 `59648dd9c` | 取含本卡的平台版本。先构建、核对并更新 sandbox 与 sandbox-provisioner，使运行端可用新的预留回收接口 |
| KnowLab | 父仓 `c2ed6b9`，后端 `d728475`，Web `b125fc5` | 更新父仓公开契约、API、作者 Web |
| KnowBench | 父仓 `af29b72`，后端 `b16d9cd`，Web `0ba5de9` | 更新 API、runner 与工作台 Web。若第 14 项尚未部署，先落实其 KnowBase 接口与 0059 迁移 |

选择实际发布修订后，核对 `sources.yaml` 的 KnowLab 父仓及两端消费者版本，执行 `python3 ci/verify-contracts.py --images-only` 和 `python3 ci/verify-contracts.py --pinned`。本批修复无新增迁移、定价或模型开关。

## 复跑物料与现场验收

1. 在大内存本地工位将 `AGENT_TEST_DATABASE_URL` 与 `DELIVERY_TEST_DATABASE_URL` 指向隔离 PostgreSQL 测试库（库名以 `_tests` 结尾）。平台仓运行 `make -C infrastructure verify-method-transactions`。它会建测试数据，包括 KnowLab 已冻结 P3 样例、长期职责的成稿及 KnowMart 资格目录。完整数据库测试另有 `verify-db-transactions` 入口。
2. 沙箱使用隔离命名空间和本次镜像。按 provisioner 的 `tests/test_instruction_units.py::test_instruction_unit_lifecycle` 构造带原始 proof UID、未绑定网关的预留 PVC。停止准备新单元后触发终态回收。记录回收前后 Pod/PVC UID、runner 的清理状态与重复回收结果。期望无新 Pod，错误 proof 不能删除，原 PVC 消失后清理完成。用 KnowBench 的 `tests/test_instruction_runner_db.py` 复跑 runner 状态转换。独立 API 的端口、临时证书和环境变量见[供给器联调说明](../../../../../gitops/components/sandbox-platform/provisioner/README.md)。
3. 用获准的作者测试身份打开已冻结的 P3 协作专家并发起作者回炉。物料结构见 KnowLab 的 `test_runtime_method_demand_db.py::test_author_handoff_reopens_collaboration_in_its_editable_cell`。确认新工作稿可打开，协作角色和步骤可编辑，原冻结摘要可核对。回炉页同一版本用于不同步骤时应逐行显示。复核页应只显示一次状态提示。
4. 工作台使用 `test_temporary_plan_db.py` 和 `test_ordinary_strict_review_db.py -k two_sources` 的样例复跑探查、成稿与长期职责。探查授权后模拟资料读取失败，再换坐标应被拒绝；同坐标并发请求应共用回执。并发放行同一成稿应只写一次；写入途中撤回后，迟到回执不能让该成稿获得下期使用权。
5. 召回物料见 `test_planning_window_recall_db.py::test_authorized_top_eight_before_and_after_catalog_growth`。先排 96 个获权工具，再排 1 个获权专家，搜索专家首屏应命中；另验证第二窗高匹配专家排名领先、撤权后不可选。隔离库可用上述测试直接生成目录。共享市场没有对应物料时，在回执中分列本地结果与现场实测范围。
6. 在本卡的 `replies/cursor.md` 写回部署号、各组件实际修订与镜像摘要、实际用例和结果。记录未覆盖的现场条件及原因。此卡验收使用隔离物料，无需重启已暂停的第 15 项财务案例。
