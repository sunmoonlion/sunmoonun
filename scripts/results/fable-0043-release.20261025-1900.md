# 回执：走查缺陷修复批（账 173–178）与发布 #28

- 日期：2026-10-25 17:40–19:00（北京时间）；执行：Fable，所有者 17:40 授权「直接修改完善代码再发版，成功后同步对齐到各工位」
- 发布：Jenkins `release` #28，六应用一次，PIN=heads，所有者第 8 段批；标签 `release-20261025-7`；回执 `scripts/results/release-28.*`（流水线写）
- 发前备份：六个库 pg_dump（custom）在本地 `~/sunmoon-probe-runs/release-0043/backup/`（不入 Git）

## 一、修了什么

| 账 | 改法 | 提交 |
| --- | --- | --- |
| 174 link「提高安全」弹窗误报 | `setupElevated` 探测失败隔两秒再探、最多三次；探测异常记 `why` | sunmoon-link b398c1d |
| 176 link 提权模式 helper 起不来 | `helperProgramDirectories` 把安装根目录加进补授读 | 同上 |
| 177 link 工作区本身建项目 EPERM | helper 查白名单根本身时进它自己核身份，不进上级 | 同上 |
| link 0.5.3 包 | Windows zip `cf0e0b85…`（180990435 B，清单 `a6f2f2b8…`）、Linux tarball `d93bfc54…`（139190700 B，清单 `60d2471f…`）；上传、读回核对；knowbench 发行配置指到 0.5.3 | sunmoonun 8daaa9d9 |
| 175 换域名切出第二份本地用户 | 六个后端 `auth_user` 唯一约束改为 subject，upsert 按 subject 更新 issuer；新迁移把同一 subject 的多份合并到最新一份：旧份名下所有 `owner_actor_id`/`actor_id` 改过来，按人唯一的记录以新份为准，改不动的行（knowbench 钉住分身版本有「不许改」触发器）删了按新份重插 | knowbench 2ffdc12、knowlab 8684d25、knowmart 884f093、knowbase eedb6d0、knowfeed c4cd1d6、tpl c7cc3f4 |
| 178「接入电脑」页对在线电脑说未配对 | 根源：现网会合点是 4028d32（不转设备编号），knowbench 只认有设备编号的电脑。会合点镜像重建到 3644498b（镜像 `50adcbc5…`）；knowbench `assigned_environment` 没编号的也取最近联系的那台 | sunmoonun f16844ec；knowbench 037f224 |
| 173 验收脚本写死管理端路径 | `check-browser.py` 改读 `<app>_deployment.admin_list_path`（knowbench、knowlab 各声明一条） | sunmoonun 0a1d7d20 |
| 流水线 | release 开头写「发布中」标记前先删 make 放的 root 文件；make 放的那份归代理用户（#27 倒在这里） | d5aea168 |

## 二、预演与测试

- 175 用现网 knowbench 库的拷贝（plain dump 装进本地 postgres:16）跑迁移：26 份 → 23 份、重复 0、悬空引用 0、sig-am 旧份 3 个项目并入新份；第一次预演抓到钉住分身版本表的触发器，改法见上。
- 后端测试（auth adapters、schema readiness、auth service；knowbench 另加 machines、routes）：knowbench 43、knowlab 24、knowmart 24、knowbase 24、knowfeed 24、tpl 24，全过（本地一次性 postgres:16 容器，已删）。
- link：Linux 359 通过；Windows 在所有者电脑上用探针复现 176/177，`icacls` 手工补授后新建子目录项目成功。

## 三、发后核对（远程集群）

| 项 | 结果 |
| --- | --- |
| 六库 alembic 头 | knowbench 20261025_0026、knowlab 0013、knowmart 0009、knowbase 0009、knowfeed 0015、tpl 0004；`auth_user` 重复 0；唯一约束 `uq_auth_user_subject` |
| knowbench 账号 | sig-am 合成一份（4 个项目）；zymun 旧份保留（还没在新地址登录，下次登录原地换 issuer） |
| 会合点 | Pod `relay@50adcbc5` Running；所有者电脑的环境已带设备编号、在线 |
| 验收 | knowbench、knowlab `admin_list_read: true`（按声明的路径） |
| #26、#27 | 没起来：NOTE 超 120 字；标记文件改写不了（已修） |

## 四、还没做的

- 所有者电脑升到 link 0.5.3（「接入电脑」页重装，配对保留），再验「目录留空」与「提高安全」。
- 各工位对齐到 fable（本回执之后做）。
- knowfeed 单独一发（Opus）；之后打 `kind-flux-final`，再 C4、C5。
