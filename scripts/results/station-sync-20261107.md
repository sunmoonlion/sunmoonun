# 2026-11-07 恢复旧开发机与三工位同步

所有者授权：“修正并把本地的 fable 和 qwen 同步到远程，然后在远程新增 agy 工位并同步本地”。此次只同步工作区与分支配置，没有发版、启动业务委托、调用模型或 Wind。

## 协作端与处理

- 本地：WSL `/home/zymun/worktrees/<工位>`。
- 远程：`zym@43.153.135.74:1022`，主机 `VM-0-13-ubuntu`，`/home/zym/worktrees/<工位>`。恢复与此机上的 Opus 协作，停止以云端容器作为当前协作端。
- 已检查本地 fable、qwen、agy：每个 8 主仓与 18 子仓，共 78 个检出；原均干净。本地 fable、agy 的 sunmoonun 落后同名 origin 分支 24 笔，已先快进。其余应用版本与各自 origin 同名分支一致。
- 远端原 fable、qwen 提交均为本地目标祖先，无独有提交；通过 Git origin fetch 后逐个确认目标 SHA，再只做 ff-only 更新。全部主仓/子仓接回工位同名分支，跟踪 `origin/<工位>`，修正了 qwen 子仓误跟踪 origin/fable 的问题。
- 远端 agy 原不存在；从各主仓的 origin/agy 建立 agy 分支与 worktree，按父仓 gitlink 初始化全部子仓，再接回 agy 分支。以本地 agy 的既有版本为准，未用 qwen 的较新应用版本覆盖它。
- 远端 model-switch 的 `layout.conf` 增加 agy；`repos.conf` 中 `$HOME/master/k8s` 改为 `$HOME/master/sunmoonun`。仅修改这两项运行配置，未同步代理、密钥、模型凭据或其他机器专属配置；这些工具目录配置未推送到工具仓。

## 原文件保留

远端 qwen/sunmoon-link 原有未跟踪文件 `新机器安装linkbug.md`。已证明其 SHA-256 与本地新版已入库同名文件完全一致：

`bad876356fd2cb0dcc7ce95c3287e31d29e3dbafb4eea94fb00c42bac2a965ef`

先将原件留存在 `/home/zym/sync-preserved/2026-11-07-qwen-sync/新机器安装linkbug.md`，再快进工作区，使同名文件成为正常受版本控制文件；更新后再次核对散列一致。没有丢弃原件、重置历史或强制推送。

## 应用版本对照

下表为同步完成、提交本回执前的主仓版本；sunmoonun 随本回执提交继续在三工位同步，应用代码不变。

| 仓 | fable 两端 | qwen 两端 | agy 两端 |
| --- | --- | --- | --- |
| sunmoonun | `cce1d1208a` | `cce1d1208a` | `cce1d1208a` |
| knowfeed-app | `1d1150e2f1` | `56ed9df09b` | `1d1150e2f1` |
| knowbench-app | `59d22e02a9` | `915e31c489` | `59d22e02a9` |
| knowbase-app | `f24ea062b1` | `582efeaa41` | `f24ea062b1` |
| tpl-app | `2ed1c71904` | `2ed1c71904` | `2ed1c71904` |
| knowlab-app | `2ea79c5b7c` | `30e2ae8cad` | `2ea79c5b7c` |
| knowmart-app | `7cd605ddcd` | `7cd605ddcd` | `7cd605ddcd` |
| sunmoon-link | `c75d0fd2bf` | `5c41d1fba9` | `c75d0fd2bf` |

## 验证

远端逐仓采集 HEAD、当前分支、upstream、工作区状态，与本地目标逐项比较：78/78 提交相同、78/78 分支与工位同名、78/78 跟踪 origin 同名分支、78/78 工作区干净。父仓状态同时检查子模块 gitlink，未发现偏离。原未跟踪文件已作为新版受控文件保留。

本回执与协作入口说明在 sunmoonun 提交，同步 fable、qwen、agy 三条分支；其他工位与旧开发机 master 的工作区未调整。此次未重跑应用测试，不把“代码已同步”写成业务验收通过；qwen-020 仍暂停发布，按后续交接执行。

exit=0
