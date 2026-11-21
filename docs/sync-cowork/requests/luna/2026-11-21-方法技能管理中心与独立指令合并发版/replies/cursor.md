# Cursor 回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 实际检查版本：sunmoon-kind 发布 #100。部署 `31518fe902d0d42857763e7f7d8b9351318a2c5d`，指针 `6cd934db9598616250af946a785ba0f19ef989b6`，tag `release-20261121-2`。候选与镜像见下表。
- 结论：部分完成。镜像、库版本和两家各 10 项 v1 登记已在 sunmoon-kind 落地，重复登记摘要一致。管理页、合成任务、Skill、递归指令、Link 和会话重准备没有现场账号与物料，未跑。

## 发现

- F01：发布 #99 在阶段图核对处停止。按应用渲染会改写整个 `gitops/clusters/kind/stages.yaml`，当时提交里还没有两个 `knowbench-function-publish-identity` 阶段。集群仍停在 #98。把渲染结果提交为 `4219c5dfe` 后，#100 完成。证据：`/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure/.build/release/100/release-100.20261121-220828.md`。
- F02：Jenkins 一次同步了 KnowBase、KnowBench API 与 runner、KnowLab 和沙箱供给器，没有拆成“先只上 KnowBench API、登记完成后再上其余”。登记在这一组起来之后补跑，两次摘要一致，未触发回滚。发布前没有单独冻结新派发，也没有清点在途调用。
- F03：脚本与写入开关在现网 `knowbench-runtime` 仍为关闭：`WORKBENCH_SKILL_SCRIPTS_ENABLED=false`，`WORKBENCH_FIXED_AS_PLAN_OWNERS=[]`，`WORKBENCH_OUTPUT_WRITE_ENABLED=false`。
- F04：KnowMart 未重建。现网后端仍是 `sha256:c42bbb4ed36c05ae1bb9b3cf7d00e0b151b9ad21c8fa29c3584fd89a126384c7`。

## 发布

环境：sunmoon-kind。应用命名空间 `app-platform-dev`，沙箱命名空间 `sandbox-platform-dev`。批准人 admin，2026-11-21T21:57:51+08:00。任务 https://jenkins.dev.sunmoonai.com:30443/job/release/100/ 。部署 OCI `sha256:83c04c4325342e5aee542b253bf9f4a785bd27caf1b2b0c85dfe2045c5da7e15`，仓库 `oci://harbor.sunmoonai.com:30443/platform/deployments-kind`。

| 对象 | 父仓 / 子仓 | 镜像 |
| --- | --- | --- |
| KnowBase 后端 | `6f041372c0dd922bf81f08a8caa70db435b61f7a` / `5563cc79fd3da76f3bf15707afb049707e11b714` | `sha256:3f1e6f47c227f8e000023ed463c21c1045546fba62df06a19b23f1f51e2e0779` |
| KnowBase Web / 管理 Web | `884d235418f63676a88002978bf99bd99112cdb1` / `f2f6df3163a01c71be13efdd20b87187b63693ec` | 未更换：`sha256:04a7db3481cf18ba0900ff6f10b2544404656b214d50e6998e20611b7eb3a478`、`sha256:00e481c455d0a2c667af8e8ee6135341d8024a5024480368675525851088eb4a` |
| KnowBench 后端 API / runner | `a5a251432107b7ca3e48813d26699dee57f9e5d1` / `e2dc7252c7031c183dc1d2882f013001b267ab15` | `sha256:a386d92d9d8097c5234c7aaecf12e54a881f52a7bb9d52ee797f78293fba4107` |
| KnowBench Web / 管理 Web | `b15ac0a232ed4ff7ccb43eee8ae60e7e2e8f0f11` / `33559e926c3ebb7570716d5bb318b5a014e0d645` | `sha256:1ed3908f40c298ae66347bad936f844addf2b60b0146ce3e815b93b057048c49`、`sha256:4aadaff728ec0f5d0f59636c5e5e8739e4e384d0561fa07d1102a3a429654681` |
| KnowLab 后端 / 作者 Web | `306948df928494526295c1f0f50185b78ff81540` / `e469e4e2ab6d18832db36ea99abfdc6578a07431`、`b63d3a882682f86b81fd252765a9df7784263a41` | `sha256:2ad8e529aa58847702e5e561a88a28e598917752073af41a236fff26b39c3e77`、`sha256:74e993c438848deebde4be7e02d2a31d6ecbea1580f398913910bb6bead1e7e4` |
| KnowLab 管理 Web | `89fe3ac1f6178018186584db7542f11102896381` | 未更换：`sha256:b4a4def63b091d949e8ff1ed19eebc4bad2be4a35e9ef61cb932e07ee1d322b6` |
| 供给器 / 沙箱 | `e5e104a2e7928c74dbf5fd360760bb9f5f38b647` | `sha256:9833097128c08b6a291b9a439867da364fbbb1a279dddf3aaab4c794f34f165f`、`sha256:61508ffc4b8fcb31beb7cf7a75b0a4104da0e21f387659266b1a73e0d6ef54b7` |

协议检查：knowbase ok=57 failed=0，knowbench ok=50 failed=0，knowlab ok=45 failed=0，sandbox ok=23 failed=0。

库版本：`knowbench-migrate-a386d92d9d80-v12` 由 `20261121_0053` 升到 `20261121_0054`。KnowBase `knowbase-migrate-3f1e6f47c227-v5` 仍是 `20261119_0022`。KnowLab `knowlab-migrate-2ad8e529aa58-v5` 仍是 `20261120_0029`。

身份作业 `knowbase-knowbench-function-publish-identity-3f1e6f47c227-v1`、`knowbench-knowbench-function-publish-identity-a386d92d9d80-v1` 已完成。发布身份为 `sunmoon-knowbase-knowbench-function-publish` 与 `sunmoon-knowbench-knowbench-function-publish`，scope `knowbench:function-publish`。凭据只挂在一次性登记进程上，登记后作业和临时网络策略已删除。

## 登记

两家各用对应镜像跑了两次 `python -m app.bootstrap.publish_functions`。源站 `https://knowbench-tls.app-platform-dev.svc.cluster.local`，路径前缀 `/api/internal/v1/method-skill-center/functions`。第二次与第一次逐项相同。

KnowBase v1，10 项：

| 名称 | 摘要 |
| --- | --- |
| read_method_input | `sha256:a8e3dc3aa52af29740119d49be37a11da39b29e74c51f435376661dacd061630` |
| list_inputs | `sha256:b5727f84e1251513babc3765d0dbbb74a076c32eeb22727fcc3e7a5542f76261` |
| read_input | `sha256:f68230df3635c707714ffb7e9902d2b3d1a3172800618229d8f34a62156c76ac` |
| query_facts | `sha256:5c76a15a66732bf1d31985c225a2039ec83dfae555355f61798b3231c0db5b60` |
| query_metric | `sha256:e01fe84d0ba21204e74ecd4cbdd3fe4533cc109172ce673888e8302dad0a9499` |
| read_facts | `sha256:ef74b2a54f7ba99164536a2aa28f7c49581dd2dd223c8e36e5c52569ba3a5a58` |
| describe_items | `sha256:f045e02e80858fdc4d8c664a72aea90b74bcce3930d947ca128aa2cc888f08d9` |
| search_evidence | `sha256:c07fd54fcbc89b0ba0f4865d7a6156e7d80b8e433767054b7e2e0f9ccd125781` |
| lookup | `sha256:9b2f01a417c693dfd64a905d41de973d2682caa56f4fb3f2964bebc018d734e6` |
| list_library | `sha256:851e871daca4b0636a0937b883b240eac70b2b2b3fcf070dcd905fea81d80024` |

KnowBench v1，10 项：七项业务、两项 Skill 读取、一项会话操作结果。

| 名称 | 摘要 |
| --- | --- |
| discover_source_tools | `sha256:c7ad888267dd69052024724a0fadbeb65c3c90da0ff72f7ea074ad4280526ab2` |
| find_subject | `sha256:d708eb8c13cbc74a764fca4382844dfa6640bd5de5be1d8445116f01f477732d` |
| request_data | `sha256:12a779a62820a27524e629810e17fab0ed7924d7467f662e03605328f4107d41` |
| find_expert | `sha256:18195f7edf8310b9a4a4da8d1fa05fe0a793527ed277a64084fb08690778dac9` |
| compute | `sha256:75ace9987f498c252fbb4883c811a8c70ee05fe7a6db7eaea20148fa88c1c277` |
| list_project_conversations | `sha256:a9ad8e10baef904c7ff94c974f4bd7c8c9e0ea3b77b7c3a5d244f2add669e59c` |
| read_project_conversation | `sha256:c177f38e60b537f45b9d0b2be697ca142a64334b8ab0a723942fea994f7edd47` |
| skill_files | `sha256:23694e12f76f7f6e168219b2cb7b16ff80ee078ffa7115bde708265ac7e6c6bd` |
| skill_read | `sha256:e014e0114b570b0bb058ebf96d905a4ef375e3238ee39c1b6089b561c38e2b4c` |
| action_result | `sha256:2c7707889fd377291b02fff14d523851c1ff3ccb98f600e768e73caa118ac403` |

## 沙箱

七个既有用户沙箱换成上面的沙箱镜像，Codex 仍是 `codex-cli 0.170.0`。七个 `*-codex-home` 卷保持 Bound，部署没有删除。

重建前配置段：`5cdfe57e345f`、`9c4bf023b0f8` 有 `sunmoon_knowbase` 和 `sunmoon_workbench`；`f1cee6277692` 有 `sunmoon_knowledge` 和 `sunmoon_workbench`；其余四个只有 `sunmoon_workbench`。重建后七个都只剩 `sunmoon_workbench`。

## 验证

已核对现网镜像、三家迁移作业输出、身份作业完成、两次登记摘要，以及沙箱卷、镜像和 MCP 段名。

未运行，因为没有授予的测试账号、配对设备、合成资料和模型预算，脚本开关也保持关闭：

- 管理页、同名不同提供方、普通用户安装与正式方法、登记和市场资格。
- 供应商与同名主体、待确认资料需求、授权读与撤权、带引用计算、重放底稿、本账号专家目录。没有 task、调用 ID 或提供端回执。
- 已安装 Skill 的列文件、分页读、本会话操作结果，以及换账号、撤安装、跨会话拒绝。
- 撤登记后的已准备轮次。共享集群上的登记予以保留。
- 递归专家 `read_task_output`、作者选源、获取者自有账号、撤权阻断、独立指令的草稿试跑和私有冻结。
- Link 本机白名单、批准、工作目录和会话交付。
- 切换前已打开会话的重新准备，以及在途未知结果的对账。

#98 现场项仍在 `docs/总纲/luna-待办.md#release-98`，本批没有改那张待办。

## 交回

本文件为第 1 轮回执。请求状态仍由 Luna 结案，本回执不归档。
