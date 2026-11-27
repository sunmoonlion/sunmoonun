# Cursor 回执

- 对应请求：../request.md
- 构建：[release #128](https://jenkins.dev.sunmoonai.com:30443/job/release/128/)，结果 SUCCESS。批准人 admin，2026-11-27T17:45:32+08:00。回执时间 2026-11-27T17:55:00+08:00。
- 分支 `expert-method-ux-release-20261127`，从 #124 回执 `0ec9ab8f8` 起，合入契约门禁、迁移头与锁源尾斜杠修复。部署 `57f9efb960716886832e5d4786b4927c311f5cda`。晋级指针 `a271de3fdd97fe949d110fe7b9ba1ef294d07041`。标签 `release-20261127-1`。流水线回执正文 `infrastructure/.build/release/128/release-128.20261127-175500.md`。部署 OCI `sha256:36fc3381842b3df6400f7e2d69330678eedef32dde4f5bb2093e5ddbc447e606`。GitHub 与 Gitee 都已收到分支和标签。

## 前半段失败（已消化）

| 构建 | 停点 | 处理 |
| --- | --- | --- |
| #125 | 迁移头 | 配置升到 `20261126_0030` / `20261126_0063` / `20261127_0022`（`57897599b`） |
| #126 | KnowLab 后端 `select-python-source` | 承认阿里云 registry 尾斜杠（`89fa7a2f3`） |
| #127 | KnowMart Web 国内拉 `pnpm@10.24.0` 失败；官方回退缺代理环境 | 网络恢复后以 #128 重跑，国内源通过 |

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web | `c4d4748` / `7e67b587`（`5c1ad30`+`8ddff902`） / `36c13dae` | 后端 `sha256:71f068741cfcc80277817a7d16db43d33191c9d852c18f4e8ee4ac52671cef83`，Web `sha256:99b84f4aa3e01f9c013b5f44f4081d604c05bfb64fadb001146cab01c10d887e` |
| KnowLab 管理端 | `89fe3ac` | 沿用现场，未重建 |
| KnowBench 父仓 / 后端 / Web | `7db6547` / `2ec1c338` / `88514dd7` | 后端 `sha256:24f874af5f99375ee50620c655eea282b9dc440be52025007f259d0c2d18cb36`，Web `sha256:62bdb0138d3404d30511d9a92f9c932c0251571496b6e19048159480f827a162` |
| KnowBench 管理端 | `33559e9` | `sha256:74c0a17b57aa11feda8adec69f3d18865515388987c237f3886edcd44dcc2725` |
| KnowMart 父仓 / 后端 / Web | `bdb7e9d` / `7ae8eb8c` / `7bafcc75` | 后端 `sha256:def252913eb0d4a6ec875c58b4aa2918705be96cdf946cf3d428a61647075a75`，Web `sha256:67c151998ad5fb49c4678594ca51fb70aff0e5248b2d84b22ef8899001b2051f` |
| KnowMart 管理端 | `6badf80b` | `sha256:bc7a12b7aa179fd0bee3e73c4874c376368deac55512eb8cdf236391949d7aae` |

## 迁移与就绪

- 迁移作业完成：`knowlab-migrate-71f068741cfc-v5` → `20261126_0030`；`knowbench-migrate-24f874af5f99-v16` → `20261126_0063`；`knowmart-migrate-def252913eb0-v5` → `20261127_0022`。
- Flux `platform` Ready，修订 `sha256:36fc3381…`。三端 API / Web / worker / scheduler 与 KnowBench runner 均为 1/1，镜像摘要与上表一致。KnowLab 管理端仍为上一版副本。
- `application-check` 对 knowlab / knowbench / knowmart 均通过。

## 可访问时间

约 2026-11-27T17:55+08:00 起可体验。入口：

- [KnowLab 五要素工坊](https://knowlab.dev.sunmoonai.com:30443/zh-CN/studio)
- [KnowBench 方法与技能](https://knowbench.dev.sunmoonai.com:30443/zh-CN/workbench/methods)
- [KnowMart 我的小店](https://knowmart.dev.sunmoonai.com:30443/zh-CN/shop)
- [KnowMart 运营条目审核](https://knowmart-admin.dev.sunmoonai.com:30443/zh-CN/market/listings)

业务验收由 Luna 接手。若要回退，先停消费，再把指针退回 `release-20261126-1` 并按现有规程应用。
