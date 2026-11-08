# Luna 回执：Link 0.5.7 常驻实机验收

- 对应请求：[request.md](../request.md)。2026-11-08，本地 qwen 工位。
- 被测源码：sunmoon-link `686a74c463360b33a56accd41ae0904647323a8a`，版本 0.5.7。
- 结论：本机普通、提权两种模式的计时及常驻生命周期检查通过；所有者已亲自确认网页浏览目录、建项目正常。历史 EOF 故障未复现，真实退回路径未触发，保留该限制。
- **只完成第一、二节。未上传或发布 0.5.7；线上下载及平台电脑仍为此前已发布的 0.5.6。发布需所有者另行明确授权。**

## 1. 构建、测试与升级

agent 目录执行 `pnpm test`：35 个测试文件通过、4 个跳过；366 项通过、33 项跳过。`pnpm typecheck` 通过。没有把跳过项计为通过。运行代码未改。

Windows 使用 release-windows.mjs 原生入口，冻结依赖、编码检查及 Windows 候选安装自检均通过。Linux 使用 build-linux.mjs，明确 `edge-public.json`，未复用上次错误的 dev-kind Linux 配置。两个包均来自上述精确源码。

| 项目 | Windows x64 | Linux x64 |
| --- | --- | --- |
| 文件名 | sunmoon-link-0.5.7-686a74c-windows-x64.zip | sunmoon-link-0.5.7-686a74c-edge-public-linux-x64.tar.gz |
| 字节数 | 180991581 | 139188189 |
| 包 SHA256 | 2179e6d82557d0b26f215e277d4480b041cf494496efcaefdeb2405735f6fc51 | ea0695017627faf2de0fc76911518bdfd5be0c23d8ce26ef2b315b8a4557e7a2 |
| 清单 SHA256 | 762fa2bc2021aceee04c3f906c5776d22d44ed1ef0d3ef1526fd7f4106ba0ac0 | 7520e546c4c83ed3692550a0f7210eff226c6de9ff3b6040ddefa5987c395143 |
| 站点 | dev-kind | edge-public |

候选目录：`/home/zymun/sunmoon-probe-runs/link-057-20261108/`，Windows 在其中 windows/ 子目录。

真实安装前 Link 0.5.6 的 bridge connections/active、service connections/active 均为 0。按既有卸载程序移除旧程序、保留配置后安装 0.5.7：卸载 11018ms，安装 1720ms；配置文件只做摘要比较，前后相同。恢复原已启用的登录任务、启动 Link 和托盘，最终 PID 27100、0.5.7、relay connected。没有新配对、新 UAC 或模型调用。

## 2. 计时

同一 WindowsFiles 正式 API，每模式每项 3 轮，毫秒；表内为整批中位数 / 最大值。0.5.7 暖态计时不含首次启动，首次完整调用（含 not-found 契约探测、沙箱启动和 ping）普通 **213.852ms**、提权 **998.135ms**。

| 模式 | 项目 | 0.5.6 中位 / 最大 ms | 0.5.7 中位 / 最大 ms |
| --- | --- | ---: | ---: |
| 普通 | 元数据 50 次 | 28373.329 / 29710.613 | 35.587 / 38.041 |
| 普通 | 读 20 个 4KB | 11212.102 / 11802.360 | 18.819 / 22.767 |
| 普通 | 列 500 条目录 | 727.963 / 934.576 | 198.526 / 211.786 |
| 普通 | 写 10 个 4KB | 5851.380 / 5970.757 | 18.496 / 25.109 |
| 提权 | 元数据 50 次 | 54125.657 / 55860.940 | 32.998 / 47.526 |
| 提权 | 读 20 个 4KB | 20817.792 / 21834.601 | 19.097 / 24.412 |
| 提权 | 列 500 条目录 | 1379.983 / 1476.653 | 143.112 / 201.761 |
| 提权 | 写 10 个 4KB | 10990.568 / 11037.393 | 17.887 / 26.258 |

旧表来自 `scripts/results/link-0.5.6-20261108/windows-*.json`；新表来自本轮 windows-*.json，所有单次样本保留。读文件逐字节核对，目录恰好 500 项，写文件逐个核对 4096 字节内容。本轮两模式并行使用独立 fixture，上轮负载不同；结果证明本机消除了重复启动开销，不承诺模型任务整体按这个倍数提速。

## 3. 卡片第二节逐项核验

| 项 | 实测结论 |
| --- | --- |
| 1 计时 | 两模式均完成 a–d 各 3 轮，首启单列，见上表 |
| 2 确为常驻 | 连续三轮均只有同一 resident PID；普通 Codex PID 26988 / helper 14788，提权 Codex PID 30748 / helper 33044，PID 与创建时间留证 |
| 3 没有退回 | 直接只读生产 WindowsFiles 的 processFallback 状态：首启、计时后、最终均 false；未注入测试 fallback 或改时限 |
| 4 空闲退出 | 最后一次调用后等 40 秒，两模式 Codex/helper/conhost（提权含 runner）均退出；resident 清空；工作目录改名并改回成功 |
| 5 句柄 | fs/open 后等 40 秒仍为同一活进程，fs/readBlock 内容正确；fs/close 后再等 40 秒，原进程树全部退出 |
| 6 崩溃恢复 | 只 taskkill 本轮 helper（普通 30424、提权 33304），紧接调用均报 exited prematurely；再下一次调用成功，新 Codex PID 普通 32784、提权 13700；旧进程树均无残留 |
| 7 真实使用 | 所有者在本次聊天明确回复“浏览和建项目均正常”；未以 CLI 探针冒充网页登录结果，未跑模型对话 |
| 8 退回路径 | 本机没法复现历史 EOF 阻塞，未触发真实 ping 超时退回；模拟覆盖随全量单测通过，不能称实机退回已通过 |

全部探针 finally 执行 WindowsFiles.close、清理独立 exec-server；最终检查没有本轮 helper 进程树残留。原用户 Link 保持在线。

环境：Windows 11 家庭版中文版 build 26300、AMD RYZEN AI MAX+ 395、KIOXIA KBG60ZNS1T02 SSD；Node 24.19.0、Codex 0.155.1；Defender 实时防护原为 false，未改变设置。

## 4. 证据与操作诊断

证据提交：sunmoon-link `3c6488e57f81015bc5ecbe805fd8c89cfa997fa3`；目录 `scripts/results/link-0.5.7-resident-20261108/`，包含原始计时、PID/创建时间、句柄与崩溃结果、环境、安装、包摘要、所有者网页反馈、脚本摘要。临时探针留在 Windows `C:\Users\zymun\sunmoon-probe-runs\link-057-20261108`，不进仓。正式代码、当前 Link 配置和沙箱隔离参数未修改；提权启动复用已有沙箱设置，不读取真实凭据。

首次从 WSL 直接执行安装目录 node.exe 被 Linux 权限拒绝，改经 Windows PowerShell 调用后正常，未改权限；一次环境脚本路径形式不对，改 Windows 命令取得环境。升级已结束但 Linux interop 包装仍等待：核实 Windows supervisor PID 5136 已退出后，仅终止 Linux 包装 PID 2651899；前后 Link PID 27100 均 connected。没有留下后台 running 探针。

## 5. 交回

本轮只提交证据和本回执，按默认规则推送 qwen 的 sunmoon-link 与 sunmoonun；提交号及两端推送结果见实际交回。发起者核对后结案，Luna 不代归档。0.5.7 发布仍待所有者明确授权。
