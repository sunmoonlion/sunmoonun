# model-switch（mb）

多仓批量 git 操作器：一条命令对多个注册仓做切换/挂工位。
工位目录和本机分支由 `mb` 管；Git 仓库远端、本机与服务器之间的同步由
`~/five-repos-sync` 管。两边共用本目录的 `layout.conf`。

## 设计前提：模型与分支是正交的

「谁写的」（模型）和「写到哪」（分支/工位）是两个独立的轴。
本工具**不做任何身份假设**：分支名、工位名任意，没有声明文件，
没有身份检查。模型归属由使用者在提交粒度上自行负责
（单模型时段：归属=时间段；多模型对比实验：建议令工位名=模型名，
这只是场景约定，不是工具的强制）。

---

## 同一工位实际有五层

本机是工位，远程也是工位。每一侧都是「目录 + 本地分支」，中间再夹一层 Git 仓库，一共五层。
以 `kimi` 为例：

| 侧 | 层 | 是什么 |
| --- | --- | --- |
| 本机工位 | 1 | `~/worktrees/kimi/<仓>`（worktree 目录） |
| 本机工位 | 2 | `refs/heads/kimi`（本机本地分支） |
| Git 仓库 | 3 | `origin/kimi`（远端分支） |
| 远程工位 | 4 | 远程 `~/worktrees/kimi/<仓>`（worktree 目录） |
| 远程工位 | 5 | 远程 `refs/heads/kimi`（远程本地分支） |

本机跑 `mb worktree remove` **默认只拆第 1 层**；远程跑同一条命令 **默认只拆第 4 层**。
第 2、3、5 层的分支都还在。

这五层里，第 4、5 层是因为**远程也是工位**才有的；第 3 层是 Git 仓库，只要工位分支曾经 push 上去，只在本机干活也会碰到。

只在本机、且仓库里**没有**这些工位分支时：第 1 节三步（收工位 → 改 `master` → 重新挂出）就够，不必走简便命令。
仓库里**已经有**同名分支时：收本机之后有时还要删第 3 层，否则按新 `master` 重建再 `push` 会被快进挡住。远程工位（第 4、5 层）仍可跳过。

**默认建议：收工位时删掉本机分支，改完 `master` 先对齐两端主目录，再从这份 `master` 挂出。**
不删分支就 `realign`，远程拿到的是旧工位，对齐 `master` 没有意义。只在明确要继续上一轮工位时才留分支。

工位名 = 目录名 = Git 分支名。`master` 除外：主目录停在 `$HOME/master/<仓>`。
本机与远程各自展开自己的 `$HOME`。

---

## 1. 分步：结束一轮，改 master，再挂出

只在本机时就是三步：**收工位 → 改 `master` → 重新挂出。** 对应下面的 ①②、然后改 `master`、然后本机 `add`。

仓库里如果已经有这些工位分支，收的时候**有时还要做 ③**（删 `origin` 上的同名分支）。没 push 过、下一轮也不打算 push，③ 可以不做。

④⑤ 和两端同步，是远程也是工位才多出来的。第一次看、或某层卡住时把五层都走一遍，便于对上原理。
命令以五仓、五工位为例；只收一个工位就把 `--all --all` 换成名字。

### ① 第 1 层：收本机 worktree

```bash
mb worktree remove --all --all
```

目录没了。**第 2 层本机分支还在。** 有未提交改动时 `remove` 会拒绝。

只想把某条分支拿回主目录检出：做到这一步为止，**不要**动第 2–5 层。

### ② 第 2 层：删本机本地分支

不删的话，后面 `add` 会把旧 `kimi` 挂回来，不会从新的 `master` 长。

```bash
for repo in k8s info-app investment-app knowledge-app tpl-app; do
  for b in cursor kimi luna opus qwen; do
    git -C ~/master/$repo branch -D "$b" 2>/dev/null || true
  done
done
```

未并入 `master` 的提交被 `-D` 后，分支指针没了，提交暂时还在 reflog。

只在本机、仓库里也没有这些工位分支时，收到这里即可去改 `master`，改完用文末的本机 `add` 重新挂出，④⑤ 跳过。
仓库里已经有同名分支、下一轮还要 push，接着做 ③，④⑤ 仍然跳过。

### ③ 第 3 层：删 Git 仓库里的同名分支

只在本机时**有时也要做这一步**。工位分支曾经 push 到 `origin` 后，仓库里就有一份独立于本机目录的指针。本机 ①② 收干净、按新 `master` 再挂，只动了第 1、2 层；第 3 层还停在旧历史上。之后普通 `push` / `to-remote` 只允许快进，会被挡住。

要删的情况：准备把新挂出的工位再推上仓库，或想让仓库里不再留上一轮的工位分支。
可以不删的情况：这些分支从未 push 过；或下一轮只在本机用、不推仓库。不删又要推上去，改用第 2 节的 `realign-to-remote` 改写，不要走快进。

```bash
for repo in k8s info-app investment-app knowledge-app tpl-app; do
  for b in cursor kimi luna opus qwen; do
    git -C ~/master/$repo push origin --delete "$b"
  done
done
```

仓库里还没有这条分支时，这条命令会报错，可以忽略。

### ④ 第 4 层：收远程 worktree

远程也是工位。在远程（`43.153.135.74`，家目录 `/home/zym`）拆目录：

```bash
mb worktree remove --all --all
```

目录没了。**第 5 层远程本地分支还在。**

### ⑤ 第 5 层：删远程本地分支

远程目录如果还停在旧历史上，本机即使已经把新分支推上仓库，远程 `pull --ff-only`
也不是快进。分支若还在，远程 `add` 同样会挂回旧历史。所以在远程再做一遍与 ② 相同的
`git branch -D`。

### 然后：只在 master 上干活

主目录 `~/master/<仓>`。提交、合并、推送 `master`。
并行时期不要在主目录写代码；工位都收掉之后，这条禁忌解除。

只在本机时，这里提交完即可跳到本机 `mb worktree add --all --all` 重新挂出。有远程时，先让两端 `master` 对齐，例如本机：

```bash
~/five-repos-sync/sync-five-repos.sh to-remote master
```

### 然后：两端重新挂出，再同步工位

本机（第 2 层已删，会从**当前** `master` 新建第 1、2 层）：

```bash
mb worktree add --all --all
```

远程同样 `mb worktree add --all --all`（远程 `master` 必须已经是新的；第 5 层已删，
会从远程当前 `master` 新建第 4、5 层）。

第 3 层已被删掉，所以这次是新建远端分支，快进即可：

```bash
~/five-repos-sync/sync-five-repos.sh to-remote -all
```

也可以一次只推一个工位：`to-remote luna`。哪一端先推都可以，先推的那端成为仓库上的权威。

---

## 2. 日常简便做法

第 1 节后半（④⑤、拆远程工位、再 `to-remote`）是两端都在时的手工拆法，步数多。
简便命令也是为「本机 + 仓库 + 远程工位」准备的：本机仍按「收了再挂出」，第 3–5 层不再手拆，用 `realign` 一次盖到仓库和远程工位。

只在本机、仓库里也没有工位分支时，不要走这一节，用第 1 节那三步。
只在本机、但仓库里还有旧工位分支：要么做第 1 节 ③ 手删后再 `to-remote`，要么仍用下面的 `realign-to-remote` 改写第 3 层（没有远程工位可拨时，见「远程工位也收掉了」）。

就跑这些命令。这就是上面那条默认建议：删本机分支，对齐 `master`，再从它挂出并盖到远程。中间只在 `~/master` 提交，不要夹别的收挂。

收工位：

```bash
mb worktree remove --delete-branch --all --all
```

`master` 干完并提交后：

```bash
~/five-repos-sync/sync-five-repos.sh to-remote master
mb worktree add --all --all
~/five-repos-sync/sync-five-repos.sh realign-to-remote cursor
~/five-repos-sync/sync-five-repos.sh realign-to-remote kimi
~/five-repos-sync/sync-five-repos.sh realign-to-remote luna
~/five-repos-sync/sync-five-repos.sh realign-to-remote opus
~/five-repos-sync/sync-five-repos.sh realign-to-remote qwen
```

为何这几条就和上面的五层一致：

| 层 | 分步里怎么做 | 上面哪条在做 |
| --- | --- | --- |
| 1 本机目录 | `mb worktree remove` | `remove --delete-branch` 一并拆掉 |
| 2 本机分支 | `git branch -D` | 同上，不单独删 |
| 3 仓库分支 | `git push origin --delete` | **不删。** `realign-to-remote` 改写 `origin` 上的同名分支 |
| 4 远程目录 | 远程再 `mb worktree remove` | **不拆。** `realign-to-remote` 对远程工位 `reset --hard` |
| 5 远程分支 | 远程再 `git branch -D` | **不删。** 与第 4 层一起被拨到新指针 |

再挂出用裸 `add` 即可：第 2 层已经删掉，会从**当前本机 `master`** 新建分支。所以 `to-remote master` 必须在它前面，否则工位从旧 `master` 长，`realign` 又不管 `master`，远程工位也会停在旧历史上。

`--from-master` 不在默认路径里。裸 `add` 若发现同名分支还在，会把旧分支挂回来，不会拨到 `master`。只有下面这些情况才加它：目录没拆、要就地把工位拨回 `master`；或目录拆了但第 2 层还在（`--delete-branch` 因超前没删掉），要强制拨到 `master` 再挂。

上面那套是默认路径。下面四种情况要把其中一条换成别的命令。

### 工位上还有没并进 master 的提交

先分清两件事：工作区里有没有**未提交的改动**，和分支上有没有**已提交但没并进 master** 的历史。

直接 `mb worktree remove`（不加 `--delete-branch`）**只看未提交改动**。工作区干净就会拆第 1 层目录，哪怕工位分支比 `master` 超前也允许收。第 2 层分支原样留下，之后可以在主目录 `checkout` 那条分支。git 的 `worktree remove` 也不检查是否已合并。

`--delete-branch` 才去动第 2 层，而且默认用 `git branch -d`：只有已经并入本机 `master` 的工位分支才会删。上一轮实验还没吸收、分支比 `master` 超前时：第 1 层目录照样拆掉，第 2 层分支留下，并提示加 `--force`。

这样是怕把没合并的提交随分支指针一起丢掉。确认那一轮不要了，再强制删分支：

```bash
mb worktree remove --delete-branch --force --all --all
```

`--force` 对应 `git branch -D`。分支指针没了，提交暂时还在 reflog。

默认不要走「留着旧分支再 `realign`」。确认上一轮不要了：`--delete-branch`（超前加 `--force`），对齐 `master`，再裸 `add`。只想把某条分支拿到主目录检出：裸 `remove`，不要 `--delete-branch`。只有明确要在远程继续上一轮工位时，才不加 `--from-master` 直接挂回旧分支再 `realign`——那时同步 `master` 没有意义。

第 2 层没删干净又要从新 `master` 开一轮：不要裸 `add`（会挂回旧分支），改用：

```bash
mb worktree add --from-master --all --all
```

### master 是在远程改的

默认第 2 步 `to-remote master` 是：本机推 `master` 到仓库，远程主目录再拉。
`master` 如果是在远程 `~/master` 上改的，方向反了，远程的新提交到不了本机，后面裸 `add` 会从本机那份旧 `master` 长工位。

把那一条换成：

```bash
~/five-repos-sync/sync-five-repos.sh from-remote master
```

其余命令不变。哪一端改的 `master`，就以那一端为源去同步两端主目录。

### 仓库里还没有这五条工位分支

`realign-to-remote` 是改写仓库里已有的同名分支（`--force-with-lease`），再把远程工位拨过去。
`origin` 上若从来没有 `cursor` / `kimi` / `luna` / `opus` / `qwen`，没有旧历史要对齐，普通快进推送就是新建远端分支。

五条 `realign-to-remote` 整段换成：

```bash
~/five-repos-sync/sync-five-repos.sh to-remote -all
```

一旦仓库里已经有过这些分支，下一轮仍用 `realign-to-remote`。本机按新 `master` 重建的同名分支和仓库里的旧历史对不上，快进会被挡住。

### 远程工位也收掉了

简便做法假定远程第 4 层目录还在，所以 `realign` 可以对它 `reset --hard`，第 5 层分支跟着走。
若远程也跑过 `mb worktree remove`，第 4 层没了，`realign` 的远程 `reset` 会因目录不存在而失败（或无处可拨）。

先在本机把第 3 层写进仓库（`realign-to-remote`，仓库里还没有则 `to-remote`），再登录远程挂出工位：

```bash
mb worktree add --all --all
```

远程第 5 层若还在，裸 `add` 会挂回旧分支，这时才改用 `mb worktree add --from-master --all --all`，先拨到远程当前 `master` 再挂。所以远程 `master` 必须已经和仓库里的 `master` 对齐，否则会从远程旧 `master` 长出来。这又回到上面「先同步 master」。

---

## 命令一览

```bash
mb                              # 状态一览（只读）：各仓当前分支 + 全部 worktree
mb k8s                          # 只看某一仓（仓名裸调 = 查状态）

mb checkout <分支> [仓名|--all]        # 把主目录切到指定分支

mb worktree add [--from-master] <名字> [仓名|--all]
mb worktree add --from-master --all --all
mb worktree remove [--delete-branch [--force]] <名字> [仓名|--all]
mb worktree remove --delete-branch --all --all

mb repo list
mb repo add <路径>
mb repo remove <仓名|路径>
```

作用域有两层，两个 `--all` 各管一层，不要省略：

- **第一个参数（工位）**：名字 = 那一个工位；`--all` = `LAYOUT_WORKSPACES` 全部具名工位。
- **第二个参数（仓）**：仓名 = 那一仓；`--all` = `repos.conf` 全部注册仓。单个工位时省略第二参数也等于全部仓。

```bash
mb worktree add luna            # 一个工位 × 全部仓
mb worktree add luna k8s        # 一个工位 × 一个仓
mb worktree add luna --all      # 一个工位 × 全部仓（与第一行相同）
mb worktree add --all --all     # 全部具名工位 × 全部仓
mb worktree add --all k8s       # 全部具名工位 × 只挂 k8s
```

漏写 `add` 时，`mb worktree --all --all` 也按 add 处理。只写一个 `--all` 会提示把第二个补上。
工位名不能以 `-` 开头（否则 git 会把 `--all` 当成 `-a`）。

保护行为（全部自动）：

- 有未提交改动的仓：跳过/拒绝，并说明；
- checkout 的目标分支被某个 worktree 占用：报出占用位置（一条分支同一时刻
  只能有一个检出，git 强制）；
- 目标分支不存在：从 `master` 新建；
- 不加 `--from-master` 时，已存在的工位目录会跳过；
- `--delete-branch` 遇到未并入 `master` 的分支会留下，除非再加 `--force`；
- worktree add 全部失败时不留空目录。

建议 alias：

```bash
alias mb='$HOME/toolboxes/Vlinux/utils/set-up-tools/model-switch/model-branch.sh'
```

## 布局：主目录与工位

目录规则写在本目录 `layout.conf`，与 `~/five-repos-sync` 共用：

```bash
LAYOUT_MASTER="master"       # 主目录：$HOME/master/<仓>
LAYOUT_WORKTREES="worktrees" # 工位：  $HOME/worktrees/<名字>/<仓>
LAYOUT_WORKSPACES=(cursor kimi luna opus qwen)  # mb worktree add --all --all
```

改这一份即可；不要在 sync 的 `config.sh` 里再写一套根路径。
环境变量 `WORKTREE_ROOT` 仍可临时覆盖工位根。

一条分支同一时刻只能有一个检出（git 强制），所以多仓协作分两个舞台：

| 舞台 | 目录 | 用途 |
| --- | --- | --- |
| 主目录 | `$HOME/$LAYOUT_MASTER/<仓>`（默认 `~/master/...`，停 master） | 单模型日常开发、评审、合并、push；`mb checkout` 管理 |
| 工位 | `$HOME/$LAYOUT_WORKTREES/<名字>/<仓>` | 并行开发（多模型对比、长任务隔离）；`mb worktree` 管理 |

互斥关系：被工位占用的分支，主目录切不过去（checkout 会报出占用位置）；
想拿回主目录，先 `mb worktree remove <名字>`（不要加 `--delete-branch`）。

并行时期唯一禁忌：**没有任何编辑器开着主目录写代码**——那时主目录是
公共参考位，谁写一笔归属就糊涂。单模型时期无此禁忌。

编辑器/助手各开各的工位目录；**哪个工位窗只启动与该工位同名的助手**——
luna/opus 窗口里不要碰 Codex 扩展（它在任何窗口都是 kimi 的脑）。

## 注册仓列表

清单在本目录 `repos.conf`（每行一个路径，`#` 注释）。路径可用 `$HOME`
或 `~`，本机与远端共用同一份，不必按用户名改。
用 `mb repo add / remove / list` 维护，不必手改文件。

## 边界

model-switch 只管**多仓批量操作与工位布局**。它不推送、不删除 `origin` 上的分支，
也不 SSH 到远程机器。那些走 `~/five-repos-sync`。它也不含任何模型/供应商配置：

- `../codex-official-setup.md` — 新增一个 Codex 官方身份（CODEX_HOME）的步骤
- `多模型登录踩坑与纪律.md`（本目录内） — 各身份登录方式、踩坑病根、纪律与排障速查
