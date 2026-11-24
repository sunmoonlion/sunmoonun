# Cursor 回执

- 对应请求：../request.md
- 构建：[release #118](https://jenkins.dev.sunmoonai.com:30443/job/release/118/)，结果 SUCCESS。批准人 admin，2026-11-24T15:14:08+08:00。回执时间 2026-11-24T15:21:26+08:00。
- 分支 `htn-planning-release-20261124`，从现场晋级线 `8117df3f6` 起。该提交包含 #117 和 runner 核权角色 `roles: [api, worker, runner]`。部署 `fb7d636691298a9602c98125b6a9c8a184cd9cae`。晋级指针 `56d78caf2a9dffb14d10020a09c14bbef479304c`。标签 `release-20261124-4`。流水线回执 `ee570b4270b70ba8d7255e715f9e768632030178`，正文 `scripts/results/release-118.20261124-152126.md`。部署 OCI `sha256:1a4c138de866e93c3ad7d4d1f61eca5a01b1fc7ba70506675bd93bf7af83f90c`。
- 发布前核对过钉到的契约：KnowBench 消费锁与 KnowLab 提供方清单一致，正式方法定义摘要 `sha256:b6fa16646e356e851857ab9c5f995e0442b8f717f960323c8dd568a1a7d5e5e6`。切换前把仍在旧镜像 `ee09225cd1ee` 上的 `knowbench-runner` 缩到 0。当时日志尾部停在 2026-11-24T05:50:11Z 的 `turn.interrupt`，没有更新的领取记录；旧 Pod `knowbench-runner-67d9688b69-xqctl` 退出后，Flux 才把 runner 换成新镜像。没有单独查询数据库里的在途命令。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web | `0f7a155` / `99d5e4c` / `7fc44ac` | 后端 `sha256:62f90a42da65794868abbed54e6dbe8ed2d8b54439c488c2694ad9556aaec06a`，Web `sha256:09fdcbf28931d9c50fa4f4bef800fdf92bed21ab6a1d7bd3825365f800b37d18` |
| KnowBench 父仓 / 后端 / Web | `2e8a226` / `a517571` / `b1516d0` | 后端 `sha256:a988f8bb69516acc980c9e4ee1a920634cc5d06cc31542cdc51eb6d387789074`，Web `sha256:c3d02b31256ed6b225e79c8c4826d8cacd831475b939fdb51a536cd3d6a46939` |
| 两端管理端 | KnowLab `89fe3ac`，KnowBench `33559e9` | 沿用上一版，未重建 |

KnowLab API、worker、scheduler 与 KnowBench API、worker、scheduler、runner 均使用各自的新后端镜像，部署均为 1/1。运行中的 runner 读到规划协议 `htn/v1`，并且 `knowbench-knowmart-summon-service` 已挂上，核权关系可用。

## 现场

- KnowLab 迁移作业 `knowlab-migrate-62f90a42da65-v5` 完成，库版本仍是 `20261120_0029`。KnowBench 迁移作业 `knowbench-migrate-a988f8bb6951-v15` 完成，库版本仍是 `20261123_0061`。
- `https://knowlab.dev.sunmoonai.com:30443/zh-CN/login` 与 `https://knowbench.dev.sunmoonai.com:30443/zh-CN/login` 均返回 HTTP 200。应用检查里网页端组织仍是 `sunmoonai`。没有做交互登录。
- Kimi 指令路由与复核路由仍在，请专家全量入口仍关，试验名单仍是 `721f2c10-db3f-4ca4-b6bf-093bb4420ea7`。`WORKBENCH_SKILL_SCRIPTS_ENABLED=true`。报价环境 `sunmoon-kind`、修订 1、每容器秒 0.01 元。

业务验收由 Luna 接手。若要回退，先把 runner 缩到 0，排空或取消本版新建的规划任务，再按现有发布规程退回 `release-20261124-3`。
