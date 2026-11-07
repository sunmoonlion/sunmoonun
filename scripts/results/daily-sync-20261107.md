# 日常单机 Git 同步简化回执（2026-11-07）

所有者要求：两端分别提交推送、自己拉取，减少一次同步的等待。

## 已实施

- 以根仓 14615532 为基线，主实现提交 59d1a7f3，旧脚本完成标志兼容提交 02074f95。
- 唯一日常实现 workstation_sync.py；五仓脚本和 human 两个入口共用。默认4仓并行联网，每仓只fetch一次；先全量核查再串行快进。
- 子模块按父仓gitlink固定，不再额外pull两个后端；保留同名分支，不能倒退或丢弃独有提交。
- 推送只处理已提交内容：每个push URL独立核对，差异才推；先子后父。网络错误不当作分支缺失；不自动add/commit/rebase/reset或强推。
- 两端已安装 ~/five-repos-sync/sync-five-repos.sh 与独立 maintenance-sync.sh；config.sh、代理和密钥未改。日常不SSH操作对方；旧to-remote/from-remote改为当前机器push/pull别名。
- 原维护测试原件改名 tests/test_maintenance.py.txt 留存，日常测试入口加载仓内同一套测试。历史参考副本未改、不作为运行真源。

## 验证

| 项目 | 结果 |
| --- | --- |
| 临时真实 Git 仓库回归，本地安装入口 | 19 passed，9.009秒 |
| 同一回归，远程安装入口 | 19 passed，13.353秒 |
| ruff、Bash语法、git diff --check | 通过 |
| 本地真实26仓pull | 退出0，15.5秒，HEAD/指针未漂移 |
| 远程真实26仓pull | 退出0，15.5秒，HEAD/指针未漂移 |
| 本地真实26仓push（双托管端） | 退出0，15.5秒；实际推送0个端点，已一致的全部跳过 |
| status | 在本机读取，未联网；原human入口也已纳入回归 |

回归覆盖并发上限、每仓只fetch一次、父子发布顺序、子仓拒绝时不推父仓、双镜像端补推、未提交文件保护、抓取失败、分叉、游离分支保护、gitlink固定及新分支发布。真实执行未运行旧版作同环境基准，不声称固定加速倍数；网络不同会影响耗时。跨仓推送不能整体回滚，发生故障明确停止并保留已成功操作。

原始临时日志：本地 /tmp/luna-daily-real-pull.log、/tmp/luna-daily-real-push.log、/tmp/luna-daily-installed-tests.log；远程 /tmp/luna-daily-remote-pull.log、/tmp/luna-daily-remote-tests.log。安装和代码同步不涉及发布、业务数据库或付费调用；维护入口未执行，本轮不认定旧维护逻辑重新验收通过。

exit=0
