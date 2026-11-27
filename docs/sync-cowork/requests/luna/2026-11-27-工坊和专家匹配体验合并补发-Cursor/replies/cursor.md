# Cursor 回执

- 对应请求：../request.md
- 本轮：进行中（Jenkins 已排队，待人批）
- 回执时间：2026-11-27T20:42+08:00（中间态）

## 候选

从 #128 回执尖端 `7316e3a54` / 现场 OCI `sha256:36fc3381…` 拉出分支 `studio-match-hotfix-20261127`。跨仓契约 `--pinned` 通过。KnowLab 库版本仍为 `20261126_0030`，无新迁移。

| 组件 | #128 基线 | 本轮候选 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web | `c4d4748` / `7e67b587` / `36c13dae` | `7c42f27` / `b089eb1` / `d5b9477` |
| KnowBench 父仓 / Web | `7db6547` / `88514dd7` | `4b37b64` / `ecc32a1` |
| KnowBench 后端 | `2ec1c338` | 沿用 |

## Jenkins

- 参数：`BRANCH=studio-match-hotfix-20261127`，`APPS=knowlab knowbench`，`PIN=heads`，`APPROVAL_TIMEOUT_MINUTES=180`。
- NOTE：工坊创建删除与专家匹配澄清侧栏体验合并补发。
- **第 8 阶段需 admin 点「批准发布」**。批准并部署后补写镜像摘要、Flux 修订与就绪状态。

业务验收由 Luna 按本卡现场条目接手。
