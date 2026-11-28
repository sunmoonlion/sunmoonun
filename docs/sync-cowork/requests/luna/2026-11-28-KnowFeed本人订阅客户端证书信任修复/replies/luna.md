# Luna 直接发布及复验

按所有者最新安排，Luna 直接启动 Jenkins 并负责业务验收。从 #141 回执 44779f1fb 快进，KnowFeed 后端 0c87da9、父仓 ae061c4、部署源 a65511c26 已同步到 GitHub 和 Gitee 的 luna-release-587。Jenkins [release #142](https://jenkins.dev.sunmoonai.com:30443/job/release/142/) 已启动，参数 APPS=knowfeed、PIN=keep。

候选源码的订阅 Web 测试 23 项通过。独立本地 HTTPS 校验确认显式信任服务 CA 时连接成功，缺少可信 CA 或服务名不匹配时连接被拒。共享环境业务结论待发布后填入。

## #142 现场结果

Jenkins 最终 SUCCESS，标签 release-20261128-5，后端镜像摘要前缀 43d924f7efb3。滚动切换期间首次业务请求返回 504，使用原幂等键再次提交后成功。原五粮液公告订阅两次 POST 均为 201，ID 均为 a11a228c-e6af-4b30-9713-4989e159aa2c，本人列表中只出现一次；暂停、恢复均为 200。KnowBase 本人授权列表出现同 ID 的修订 1，范围为 000858.SZ 的 interim_announcement。KnowFeed 取消为 200 / cancelled，再查 KnowBase 列表已无该授权。

真实资料投递仍未通过。独立验收订阅 c48605cf-c477-469e-af02-d17eee0224a0 的调度轮次已启动，实际渠道为巨潮 cninfo。只读核实渠道状态 paused，原因为 auto_paused: 5 failures，watch 作业 queued、执行次数 0，未生成交付物，无法确认文档归属。两条验收订阅均已取消。后续需在渠道恢复后用真实公告验证投递及文档归属；本次发布没有修改渠道状态。
