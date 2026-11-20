# Cursor 发布回执

2026-11-20。Jenkins `release` #96 成功。用户脚本开关保持关闭。真实供应商 OAuth 与 agy 的 C1/C6 独立回执都不在本轮。

## 发布结果

- 分支 `c1-c6-release-20261120`，回执提交 `50c1a6e6bd4309c96c0bd95ba6f87424ce5eb7d3`。
- 部署真源 `8c6893f496f839727088a4e341cc6ec35a0a9173`。指针 `e16fba8413deb1fdfbcd7b6265bb916ea3f8e890`。回执记录标签 `release-20261120-1`。
- OCI `sha256:51e5cbfd61f433e0785eaede7e94b18e858e1cd56f1b6e6fcc3d4db10fdcd76c`，仓库 `oci://harbor.sunmoonai.com:30443/platform/deployments-kind`，路径 `./clusters/kind`。
- 任务：<https://jenkins.dev.sunmoonai.com:30443/job/release/96/>。admin 于 2026-11-20T12:54:18+08:00 批准。回执时间 2026-11-20T13:06:20+08:00。
- 同分支早先的 #95 在沙箱镜像构建阶段失败，没有部署。清华 Debian 与 PyPI 返回 403，构建机没有走代理。随后只在这条发布分支把本次构建的 Debian 与 PyPI 改到阿里云，并保留对历史清华地址的识别。#96 用这个提交构建成功。

上线前可恢复版本是标签 `release-20261114-1`（`9a53427f900e7921a75192a8fab17d8f2692625c`）。当时的部署修订是 `cd1b6ceed06d63c6180fda3247fbd4155eb760b4`，OCI 是 `sha256:ea7cc14c2cd52ba6577e8add762fb23573dcb640f6e3a608c49a29f16469c61a`。数据库 schema 不随 Git 指针回退。

## 镜像与迁移

运行中的工作负载与镜像锁一致。迁移 Job 的 `succeeded` 均为 1。

| 组件 | 镜像摘要 | 源码 | 迁移 |
| --- | --- | --- | --- |
| KnowBench 后端 | `sha256:d52419126a2574f168c25ae4e668b41f2fd708bc6822d19348372f6fe4987539` | `4aa68b7d0fe58b9d78c7ebc14742790da3840c02` | v11 / `20261120_0049` |
| KnowBench Web | `sha256:bd761ca251b612a267d3a0e08adc54c5dfb14f7d86f4aef839c604a11caa27f7` | `11a3fd728ad63d35d47cd2b1a9bd60d2850ce5ea` | — |
| KnowLab 后端 | `sha256:5323de113029902efe50980f4a03131e4e2781682ce2102e57c1fa8421344ff4` | `e7e3c5451492c116cf094c480a974c2068b71018` | v4 / `20261115_0027` |
| KnowLab Web | `sha256:47af9a8bc6b5dadf431e30493f55488770b2309ce0ff5031e4e3c74678cc65eb` | `7eb57a755c676e6208dd1b33abf1e30af81e6145` | — |
| KnowBase 后端 | `sha256:acd2487ccb02794d58e902a845ba05112ceedccf832065c5b772c06bc117b28d` | `906f88aeaf8bd6f08495cb16ff3a34151909d9b5` | v5 / `20261119_0022` |
| KnowBase Web | `sha256:04a7db3481cf18ba0900ff6f10b2544404656b214d50e6998e20611b7eb3a478` | `884d235418f63676a88002978bf99bd99112cdb1` | — |
| KnowBase Admin | `sha256:00e481c455d0a2c667af8e8ee6135341d8024a5024480368675525851088eb4a` | `f2f6df3163a01c71be13efdd20b87187b63693ec` | — |
| KnowMart 后端 | `sha256:4c7ee214ddce35da392f691de2a93c5ef2efda8e2b64028283895b2808df5195` | `090da88031ef0fa0b6db1300acc778ed41d7c050` | v4 / `20261120_0015` |
| KnowMart Web | `sha256:24f05af2490abb7869211e96908deff6782cced6a57f2b59ceb545d9dd49074a` | `305f0876c9a1174e625f840c8d907da935c4b006` | — |
| KnowMart Admin | `sha256:9f0c0a4b52549aca9bde02d966592f302a9c01da51cf42eb7e46b7c7c8627b8d` | `5f109118ffbaca623a732ed33eaea61a2905241a` | — |
| 沙箱 | `sha256:aaf941ee938d30b6a938f7e46ed2d1521142dc654e75fe8ff61fb483bb05f46b` | `42ef8470eaf8df065184dbae0537c963ad15b8a8` | — |
| 供给器 | `sha256:3eeb6761c7ffc69dc5943b6cf3346e6f5e559e2f87402926bc5e9e12b348d9fb` | 同上 | — |

供给器 Deployment `sandbox-provisioner` 在 `sandbox-platform-dev`，镜像与上表一致。

## 相对开发候选的差异

镜像锁里的应用源码就是需求列出的后端、Web 与 Admin 提交。沙箱和供给器没有直接使用 Luna 的 `9edd61e02` 或 Dockerfile 提交 `5b11c856` 作为构建修订，因为组件构建只导出已固定修订里的文件。发布分支把已复核的沙箱与供给器树导入 `42ef8470eaf8df065184dbae0537c963ad15b8a8`，再把组件修订钉在这个提交上。该提交相对 `9edd61e02` 的沙箱目录和供给器模板没有差异；Dockerfile 的 `ARG CODEX_VERSION=0.170.0` 与 `5b11c856` 相同。

没有并入 Luna 的文档和旧的 GitOps。生产上的 MCP 地址、`WORKBENCH_OUTPUT_WRITE_ENABLED=false`、空的固定计划所有者保持原样。本地浏览器脚本 `0c5b26f7` 不是部署镜像的一部分。tpl 与 KnowFeed 不在本次应用列表里，指针未改。

## 开关与未做的验收

已部署的 KnowBench 运行清单写明 `WORKBENCH_SKILL_SCRIPTS_ENABLED: "false"`。用户脚本入口没有打开。

agy 的 `replies/agy.md` 仍未写。目标集群上的 Python、Bash、Node 完整包、凭据隔离、网络拒绝、资料输入、产物下载、停止和清理都没有做。因此没有按页面复验脚本操作卡，也没有启用开关。真实供应商账号、授权范围和回调仍缺，OAuth 未发布。本环境没有另行核对运营单价、容器计量和根预算。Opus 全局审查留到下一版。

已经存在的用户沙箱没有被这次发布重启，仍使用更早的沙箱镜像。新创建的沙箱才会用到上面的新摘要。

## Codex 0.170.0 与 Link 0.5.9

新建沙箱：在 `sandbox-platform-dev` 用摘要 `sha256:aaf941ee938d30b6a938f7e46ed2d1521142dc654e75fe8ff61fb483bb05f46b` 起了一个一次性 Pod。其中 `codex --version` 为 `codex-cli 0.170.0`。对该 Pod 内的 app-server 做初始化握手，返回成功，`userAgent` 带 `0.170.0`。探针 Pod 随后删除。

Link 0.5.9 的发行配置与运行中的下载描述一致。设置页读取的就是这份描述：版本 `0.5.9`，Codex `0.170.0`，Windows 包 224357476 字节，SHA-256 `807ac5eb4a738b5b785ef014f1bc3293e27483c0afc82a82b5467acdaa1fa135`。本轮没有另外打开已登录的浏览器页面。

正式对象：

- Windows：`windows-x64/0.5.9/sunmoon-link-0.5.9-318f79e-windows-x64.zip`，SHA-256 `807ac5eb4a738b5b785ef014f1bc3293e27483c0afc82a82b5467acdaa1fa135`，清单 `de3df6c95d4b1cbe50b72a235d6f904ac913803bbc8f99d39c03694b1411e63f`，224357476 字节。
- Linux：`linux-x64/0.5.9/sunmoon-link-0.5.9-318f79e-edge-public-linux-x64.tar.gz`，SHA-256 `6c0cd50f84095739a5f7fb8459da3618d242dc7c55cb1c6131bda371b677e35c`，清单 `5f8e4c0ad6ba9bb5b206cf4005425b789c9ee61ac7f256a063f793d71047a9b9`，164961662 字节。
- 组包提交 `318f79e54cfe2be27fc9ceb722d172a8e757d975`。

本地两份已验包的 SHA-256 与大小和上述配置一致。0.5.9 使用新的对象键，没有覆盖 0.5.8 的键。

Windows 正式包里的 `cli.js --version` 输出 `0.5.9`。用包内原生 `codex.exe` 另起一次 exec-server，初始化返回 `executorVersion=0.170.0`、`platformOs=windows`。探针进程已停，没有替换这台电脑上原有的 Link。

平台电脑 `knowbench-platform-computer-knowbot-tester` 已换到新沙箱镜像，并按配置取用 Linux 0.5.9 对象。启动日志为 `version=0.5.9`、`codex=0.170.0`，包目录是 `/data/releases/0.5.9-6c0cd50f8409`，exec-server 就绪后已连上会合点。再对这个包内的 Codex 二进制单独做一次初始化，返回 `executorVersion=0.170.0`、`platformOs=linux`。本地 Linux 包的同一种初始化也返回 `executorVersion=0.170.0`。
