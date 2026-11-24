# Cursor 回执

- 对应请求：../request.md
- 构建：[release #116](https://jenkins.dev.sunmoonai.com:30443/job/release/116/)，结果 SUCCESS。批准人 admin，2026-11-24T10:05:24+08:00。回执时间 2026-11-24T10:12:30+08:00。
- 分支 `m02-joint-release-20261124`，从 #115 的 `789e9ed27` 起。准备提交 `139d668f9`。部署 `cb5d2890b`。晋级指针 `53a863335`。标签 `release-20261124-1`。流水线回执提交 `9316239d5`，正文 `scripts/results/release-116.20261124-101230.md`。部署 OCI `sha256:c5e08e3857216c76ab3075efd37e2c4a53e19edd8bfa2936b794b23fd253d482`。
- 发布状态：KnowLab、KnowBench 已在 sunmoon-kind 就绪。业务验收由 Luna 负责。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web | `08bebfc` / `468cee9` / `9f65b6b` | 后端 `sha256:5620ca05788e88b9681cf83b0675338df8de8ed8774b67aa8b5c4f394b286d71`，Web `sha256:1b798e84ed4606b9d235d380634b264c7a2d44d42db8ff452604410f8f459433` |
| KnowBench 父仓 / 后端 / Web | `e46959d` / `0eb40f0` / `b54f2ba` | 后端 `sha256:ee09225cd1ee720a698fb4685bcd7f49fce4630cfaff18bad819e34584746232`，Web `sha256:d00a974e3e5ff677b385f65a9eb241c93d1c3045dd97a4e9377101b6a4ec82ad` |
| 两端管理端 | KnowLab `89fe3ac`，KnowBench `33559e9` | 沿用上一版，未重建 |

API、runner、worker、scheduler 使用同一后端镜像。发布后九个部署均为 1/1 就绪。

## 库版本与配置

- KnowBench 迁移作业 `knowbench-migrate-ee09225cd1ee-v15` 完成。日志为 `20261122_0060 -> 20261123_0061`，校验回读 `schema=20261123_0061`。
- KnowLab 迁移作业 `knowlab-migrate-5620ca05788e-v5` 完成，库版本仍是 `20261120_0029`。
- 构建前核对过即将构建的配置：Kimi 指令路由与复核路由仍在，请专家全量入口仍关，试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`。交付写回仍关。
- 发布后 `knowbench-runtime`：`WORKBENCH_SKILL_SCRIPTS_ENABLED=true`。报价环境 `sunmoon-kind`、修订 1、每容器秒 0.01 元，供给器地址与 `WORKBENCH_PROVISIONER_URL` 同为 `http://sandbox-provisioner.sandbox-platform-dev.svc.cluster.local:8080`。上述路由和名单与构建前一致。

## 维护窗口

没有单独把旧写入进程缩到 0 再迁移。admin 批准后，Flux 按既有顺序先跑迁移作业，再换新版进程。迁移开始时上一版 API、runner、worker、scheduler 仍在运行。迁移成功后，这些进程和两端 Web 已换成上表镜像。
