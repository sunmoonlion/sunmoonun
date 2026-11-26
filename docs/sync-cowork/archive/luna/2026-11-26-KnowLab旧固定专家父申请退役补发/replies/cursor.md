# Cursor 回执

- 对应请求：../request.md
- 构建：[release #124](https://jenkins.dev.sunmoonai.com:30443/job/release/124/)。Jenkins 页面结果 FAILURE（后半段 `flux reconcile platform` 因 valkey AOF 坏尾超时）；集群晋级与 Git 推送已人工收尾。批准人 admin，2026-11-26T19:14:17+08:00。回执时间 2026-11-26T19:59:04+08:00。
- 分支 `knowlab-parent-retire-20261126`，从 #123 回执 `15b34d380` 起。部署 `653b6ae21644a12b0e81f004ab2dfc6239eb9ca2`。晋级指针 `7bc4e62f64108a3b8ef2feb1d47948bed647e524`。标签 `release-20261126-1`。流水线回执 `0ec9ab8f80437582d08055ab26ee281bb3ce80e0`，正文 `scripts/results/release-124.20261126-195904.md`。部署 OCI `sha256:f16889a9a3b7719008db57aa5292bbc0b5b96c45935772822193eb45ccc55276`。GitHub 与 Gitee 都已收到分支和标签。
- KnowLab 父仓钉到 `385740099`，后端钉到 `8ddff902`（相对 #123 多「统一过滤已退役固定包的父申请」）。Web / Admin 源码钉仍为 #123 的 `b681780` / `89fe3ac`。库版本未改。

## 版本

| 对象 | 源码 | 镜像 |
| --- | --- | --- |
| KnowLab 父仓 / 后端 / Web | `385740099` / `8ddff902` / `b681780` | 后端 `sha256:93a212a69dd48ee48f407cb4731c827e3ce9c240915486f4baab4a493d7f4e63`，Web `sha256:ddac0f193132b8b0d76cec31cc7b83acdbb5563a6dbb7a144bb6241aa2c7b09f` |
| KnowLab 管理端 | `89fe3ac` | `sha256:43f928c3713631099f020f7406cc443f68c7e56ec13b23109732d01a7b01f0eb` |

KnowLab API、worker、scheduler 使用上述新后端镜像，均为 1/1。

## 就绪与收尾

- 批准后源与部署已晋级；`platform` / `knowlab-runtime` / `valkey` Ready，修订 `sha256:f16889a9…`。
- `#124` 后半段失败根因：`data-platform-dev/valkey` 的 AOF incr 尾部 35 字节损坏导致 CrashLoop，拖死 `platform` 健康检查。已备份 PVC 后 `valkey-check-aof --fix`，恢复 STS 并重新 reconcile。
- `application-check` 在等待 Ready 处卡住后跳过；以现场 kubectl Ready 与 1/1 为准。业务验收仍由 Luna 做。

若要回退，先停消费，再把指针退回 `release-20261125-1` 并按现有规程应用。
