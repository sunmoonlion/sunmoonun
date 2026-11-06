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
