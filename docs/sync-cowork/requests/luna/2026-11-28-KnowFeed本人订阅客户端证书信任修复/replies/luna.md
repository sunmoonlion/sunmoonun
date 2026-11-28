# Luna 直接发布及复验

按所有者最新安排，Luna 直接启动 Jenkins 并负责业务验收。从 #141 回执 44779f1fb 快进，KnowFeed 后端 0c87da9、父仓 ae061c4、部署源 a65511c26 已同步到 GitHub 和 Gitee 的 luna-release-587。Jenkins [release #142](https://jenkins.dev.sunmoonai.com:30443/job/release/142/) 已启动，参数 APPS=knowfeed、PIN=keep。

候选源码的订阅 Web 测试 23 项通过。独立本地 HTTPS 校验确认显式信任服务 CA 时连接成功，缺少可信 CA 或服务名不匹配时连接被拒。共享环境业务结论待发布后填入。
