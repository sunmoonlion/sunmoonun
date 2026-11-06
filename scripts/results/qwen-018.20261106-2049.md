# qwen-018 发布前核查回执（2026-11-06 20:49）

状态：**发布未触发，停在环境检查**。所有者要求在 qwen 工位执行发布；按发布卡第一节核候选完成，但 `make -C infrastructure platform-status` 退出 2，未触发 Jenkins，未改钉、未构建、未部署。

## 候选核对

四个应用工作区干净，父仓本地与 origin/qwen 一致，子仓 gitlink 与发布卡一致：

```text
knowbase: local=cb1cb10a72e196cc949f0be4be4bbd336151ef73 origin/qwen=cb1cb10a72e196cc949f0be4be4bbd336151ef73
f2f6df3163a01c71be13efdd20b87187b63693ec knowbase-admin-frontend (2.0.0-17-gf2f6df3)
 bf59f85d0bf619766f8a663d7965e2c57306acf2 knowbase-backend (2.0.0-123-gbf59f85)
 be6d29ed6f054304aa0f38d53831f5f7fa238fa2 knowbase-web-frontend (2.0.0-24-gbe6d29e)
knowfeed: local=67638eb94e49a0a614704600b74b096fdcbba44a origin/qwen=67638eb94e49a0a614704600b74b096fdcbba44a
1bdcbcd042a45a0d19de1787778fd78f96cf49b6 knowfeed-admin-frontend (2.0.0-21-g1bdcbcd)
 4b5d9ac32e9bf00a2ed24b6c16cbbe5a260badcb knowfeed-backend (2.0.0-87-g4b5d9ac)
 bb03f1ac21ffea0bc4e71dd5efc678256dd354ab knowfeed-web-frontend (2.0.0-24-gbb03f1a)
knowbench: local=6049c865f668936630be06397a32eaca8b31bd78 origin/qwen=6049c865f668936630be06397a32eaca8b31bd78
540d9f38bf9ef5015684686f6abe576c7144aea0 knowbench-admin-frontend (2.0.0-16-g540d9f3)
 c7d3d14dbd29177cdd85da59a54025b9b57d3276 knowbench-backend (2.0.0-290-gc7d3d14)
 7026bfea6ad31580488f8e0e231c9a649477f2c7 knowbench-web-frontend (2.0.0-170-g7026bfe)
knowlab: local=43d2192ff48477e26431913b80ea300dbcc3b4c5 origin/qwen=43d2192ff48477e26431913b80ea300dbcc3b4c5
89fe3ac1f6178018186584db7542f11102896381 knowlab-admin-frontend (archive/stations-local-20261106/backup/pre-align-20261106-qwen/89fe3ac1f617)
 614da0abf9b66eb6daacf3ecacccf3f6761a1a10 knowlab-backend (archive/stations-local-20261106/work/qwen-20261106/85e3def5c5de-1-g614da0a)
 25772149330a0ff8544e51edb98f1f376f21b75e knowlab-web-frontend (archive/stations-local-20261106/work/qwen-20261106/25772149330a)
```

## 阻塞证据

`platform-status` 的实际错误：

```text
The connection to the server 127.0.0.1:27443 was refused - did you specify the right host or port?
localhost : ok=5 changed=0 unreachable=0 failed=1 skipped=2 rescued=0 ignored=0
make: *** [Makefile:512: platform-status] Error 2
```

同次只读核查：

```text
sunmoon-jenkins-jenkins-1 Exited (143) 3 hours ago
sunmoon-jenkins-tls-1 Exited (0) 3 hours ago
sunmoon-kind-worker2 Exited (128) 3 hours ago
sunmoon-kind-worker Exited (128) 3 hours ago
sunmoon-kind-control-plane Exited (128) 3 hours ago
sunmoon-jenkins.service ActiveState=inactive SubState=dead
sunmoon-jenkins-agent.service ActiveState=inactive SubState=dead
```

这证明当前发布卡所指环境没有运行，不能证明停机原因。Harbor 与入口容器在运行。没有启动或重建任何容器，没有修改数据库、恢复历史任务或调用 Wind。

活动委托、app-server turn、knowlab 测试及 Wind 队列尚未核验，不能报为空。已请所有者决定是否恢复现有环境；恢复可能续跑停机前任务。获准恢复后先完成发布卡第二节检查，有 Wind 待派作业仍交所有者决定，再走正式 Jenkins 发布及人工审批。

发布卡：`docs/process/switch-test/inbox/qwen/2026-11-06-qwen-018-next-batch.md`。本轮完整 platform-status 原始日志留在执行机 `/tmp/qwen018-platform-status.log`（临时诊断路径，非持久归档）。

## 20:55–21:00 所有者授权恢复后的复核

所有者在定位启动错误后明确指示“那你做啊”。执行正式入口 `make -C infrastructure platform-start`，退出 0（ok=5 changed=1 failed=0）。三个既有 KIND 节点均 Ready，未重建、未删除数据。Jenkins 控制器及 agent 为 active/running，统一 target active。

此前 18:17 的直接失败原因：systemd 向三个节点 cgroup 添加 PID 时返回 `Device or resource busy`；开机恢复单元 Restart=no，因此失败后不重试。恢复前已确认三个节点 PID=0、对应 cgroup 不存在。本次正常启动成功；不能据此声称已确定并永久修复此前资源冲突的深层原因。

- 非已完成 Pod：82/82 Ready；Flux Kustomization：108/108 Ready 且 observedGeneration 达到当前 generation。
- 再执行 `make -C infrastructure platform-status`：退出 0，ok=7 changed=0 failed=0。
- 只读事务查 workbench_tasks 非终态：0 行。
- knowbot_test queued/running/waiting：0 行。
- 发布卡第二节 Wind 作业 SQL：0 行。
- 经正式 app-server 协议 initialize → thread/loaded/list 查询 4 个 ready 沙箱（含 sig-am c678ec57…）：各 loaded_threads=0、active_turns=[]。未调用模型、未恢复线程、未代批任何业务操作。

发前检查通过，继续按发布卡触发 Jenkins，结果另补；此段不代表已发布。临时日志：`/tmp/qwen018-platform-start.log`、`/tmp/qwen018-platform-status-restored.log`。

## 发布 #84：迁移配置检查失败，未部署

正式命令：

```bash
make -C infrastructure jenkins-release-run RELEASE_BRANCH=qwen APPS="knowbase knowfeed knowbench knowlab" PIN=heads NOTE="qwen-018 下一批：账 180–188、K29、183"
```

构建页：<https://jenkins.dev.sunmoonai.com:30443/job/release/84/>。先等待定时 render-check #1445（SUCCESS）释放执行器，随后发布进入第 2 阶段。#84 显示根仓快照 `16bfd4904a`，四个应用改钉与发布卡一致。最终 FAILURE，Make 退出 2。

原始错误（`2-plan-knowbench.log`）：

```text
TASK [Require the configured schema to match the immutable source chain]
[ERROR]: Task failed: Action failed: Expected schema differs from pinned backend source. Correct the configuration before rendering or deployment.
fatal: [localhost]: FAILED! => {"assertion": "cfg.expected_schema_revision == (pinned_schema.stdout | from_json).head", "changed": false, "evaluated_to": false, "msg": "Expected schema differs from pinned backend source. Correct the configuration before rendering or deployment."}
localhost : ok=14 changed=0 unreachable=0 failed=1 skipped=7 rescued=0 ignored=0
make: *** [Makefile:411: application-deployment-plan] Error 2
Finished: FAILURE
```

原因：发布卡明确要求 knowbench `20261106_0039`，部署真源 config.yaml 仍声明 `20261104_0038`。已修正声明并更新对应注释；没有手改渲染产物或数据库。

离线验证：直接读取固定后端 Git 对象 `c7d3d14dbd29177cdd85da59a54025b9b57d3276` 的全部 Alembic 文件，用 AST 提取 revision/down_revision，检查单一根、父链完整、唯一头。共 38 个迁移，唯一头 `20261106_0039` 与修正后配置一致，直接父为 `20261104_0038`。`git diff --check` 通过。下一轮仍须走正式 application-deployment-plan 和全流水线，不能把离线验证写作上线验收。

第 3–12 阶段均未执行；没有新镜像、候选晋级、发布 tag 或线上迁移。流水线已撤回代理克隆中本轮未提交的改钉。控制台在 `infrastructure/.build/jenkins/release-84.log`，正式产物见 Jenkins 构建页。

遵照发布卡失败即停止、不自动重试：修正提交后等待所有者确认重跑。页面验收、上线后日志、0039 迁移完成及 K29 对账仍未执行。
