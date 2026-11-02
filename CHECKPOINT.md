# 当前：安装包私有托管候选，停在发布前（2026-10-09，luna）

依据 `sunmoonai/docs/process/switch-test/luna-feedback.md` 最后一节，基线 `67e9fa97`。
本轮由 Luna 实施、Fable 审读，所有者安排 Cursor 发布；助手不自行 push、建桶或晋级线上源。

- 组件目录：`gitops/components/app-platform/investment-app/investment-backend/agent-releases/`。
- Make 校验/上传入口，组件原生 prepare + SOPS + Flux 依赖；独立 reader/writer；只有 API 得到读身份。
- `enabled: false`、`download_available: false` 保持；未生成真实 SOPS、桶或账号。
  开放下载前须上传读回回执与当前摘要匹配。维护方法、发布顺序与回退见该目录 README。
- 本地 10 项上传/策略/模板测试通过；三种托管状态的 Ansible 表达式检查通过（15 项任务，changed=0）；
  Make 只读入口对真实 166 MiB ZIP（90 文件）校验通过、changed=0；语法检查通过。
- 后端 `a01db6f`、网页 `2095c04`、父仓 `231f305` 已本地提交；未发布。
- 下一步：所有者同步给 Fable 审读后，安排 Cursor 按固定源码构建/部署桶与身份、上传、开启下载，
  实测条件写/权限/Range 及浏览器下载→安装→令牌→在线。不能把本地检查写成线上验收。
- 完整输出、失败与重跑、原有真人待验在 runtime 本轮 `agent-release-hosting.20261009.md`。

以下为此前基线携带的历史，不代表本轮另行授权。

# 当前工作：按组件统一操作与账号维护（2026-10-05）

所有者已批准上一轮完整方案并要求按任务表实施。基线53abb007e8960c53faea750ea6477f5c2e92a576，分支platform-kind-v1，仅修改新体系infrastructure/gitops/docs和本检查点；不push，不改旧sunmoonai/冻结Luna或四业务仓。日常Make→Ansible→Flux/SOPS，配置同组件放置。此次授权不自动延长上一单元08:25–10:25 UTC窗口，也不授权WSL关闭/删群；实际停服按具体范围另批2小时，容量10GiB及数据盘230GiB增长检查有效。

## 顺序任务表

| 编号 | 任务 | 依赖 | 验收条件 | 状态 |
|---|---|---|---|---|
| T1 | 逐对象盘点配置、阶段、依赖、账号及密码表映射 | 无 | 对象归属唯一；映射不输出秘密；确认人工账号范围 | 已完成 |
| T2 | 统一platform-*对象选择、只读计划/配置/状态及动作准入 | T1 | 整套/平台/应用/组件选择正确，未知对象拒绝；不增加重复CLI | 13项原生正反例通过；继续与T3联验 |
| T3 | 拆分共用Flux部署阶段与原生选中对象stage/deploy/check | T2 | 组件独立根、真实依赖；未选声明/Pod/Job/PV保持；整体源晋级范围透明 | 188个候选服务对象与原14阶段逐对象一致；拆26阶段；整套/PG/Tpl-Web实际stage范围通过；固定拓扑源已晋级，188对象归属交接通过 |
| T4 | 账号元数据、预设/导入/本机查看、恢复和密码规则 | T1 | 指定值首次生效、随机默认、主备保持；已有身份差异不自动覆盖 | 10类维护账号目录；三类真实登录通过；12/18导入及重复导入通过；PG/Redis/Rabbit首次预设已接入、未新建实演 |
| T5 | 按组件实现真实密码轮换与失败恢复 | T4 | 目标身份/权限核对，新密码登录、配置/备份一致；不重跑旧初始化Job | Harbor/Casdoor事务及原生恢复候选已实现；7项模拟故障/策略检查及6项真实SOPS/临时Git候选检查通过；实际轮换未执行，Kibana保持 |
| T6 | 原生发布、授权范围内实演单组件/整套与已选人工账号 | T3/T5 | 原门禁、真实协议、重复部署；原节点/卷/未选对象保持 | 拓扑部分完成：整套部署、PG/Tpl-Web单组件deploy/check、整套重复deploy、整套check（首次瞬时失败后重跑通过）；Harbor/Casdoor实际轮换未执行，窗口已关闭 |
| T7 | 删除失效公共入口、收敛维护说明及清理本轮临时文件 | T6 | 日常只有一套对象操作；文档准确；本地提交、工作区干净 | 仅完成/tmp证据归档（86文件逐一SHA256核对）；聚合源码清理、入口收敛未做，并入后续重构 |

## 盘点结论与当前候选

当前services layout已经有组件路径映射，但platform-services仍聚合core及三个平台；需要真实拆阶段，不能只把Make名字转接。ELK runtime也聚合Kibana/Logstash，分别处理依赖。应用已有backend/Web/Admin阶段，复用common机制且不修改既有Job字节。

基线已有密码文件会沿用；本轮接入私有初次预设、表导入及账号目录。Kibana当前值保持，未来预设允许8–128字符且不含首尾空白；PG/Redis/Rabbit首次预设候选不覆盖已有值。所有者明确要求保留密码修改表作为开发阶段实际密码查阅表，并授权写入实际值；本表是明确例外，不作为运行部署真源、不输出到对话/日志、不push，生产前统一轮换。新Kibana15d已与私有输入同步，旧ELK密码明确不适用。账号轮换成功后同步当前值。第12项Harbor admin、第18项Casdoor built-in/admin映射已获确认；第15项旧ELK共享管理员不是新Kibana只读账号，不能自动复用。所有者已选择：采用第12/18项，Kibana保持独立现有密码。除所有者授权的开发查阅表外，值只在私有候选/内存读取，不进入日志或Git；现有账号轮换仍先准备具体回退并确认实际停服范围。

本轮只读/候选证据暂在/tmp/component-render-inventory-audit.json、component-stage-scope-audit.json、account-native-audit.json、account-transaction-audit.json及对应root0600日志；交付前归档并逐字节核对后仅清本轮文件。13个选择正反例、188对象相同、149运行UID保持、整套及两个组件实际stage范围通过。账号目录扩为10类，除三类已检查的身份外，数据库管理员只是路径/查看与部分首次预设接入，真实轮换未实现，不能声称全账号已验证。

Casdoor真实检查先失败，原因是把Go IsGlobalAdmin()方法当JSON属性；官方v4.12.0由owner=built-in判断。按真实owner/admin/isAdmin及未禁用/未删除核对后通过，未降权。所有者提醒数据库管理员也属于人工维护范围，因此新增PG/Redis/Rabbit/Elastic/Neo4j/Mongo/对象存储账号元数据，未擅改其口令。

最终候选13项选择及六原生play语法、账号四play语法、188对象与原提交对比、公开PG/Tpl-Web stage范围再次通过。Harbor当前admin/database私有副本已补齐且逐字节一致；账号隧道缓存已隔离到自动清理目录，之前只清本轮33个API发现缓存文件。

维护卡（已删，Git 历史 `53767f6a:docs/platform/component-account-maintenance.md`）；私有恢复快照/mnt/sunmoon-data/backups/host/component-account-20261005T124637Z，原51阶段/两个聚合阶段/149受保护对象，源摘要保持。候选已本地提交e59bdc006a2eaca8c7b3af367ad7e801a6136547，原生flux-release退出0，固定OCI摘要sha256:e26d2a19932686a64a7226cbf64666c457d797450fdf92f462b184a1ca7a2aef，requires_sops=true；未晋级/应用，运行源仍为原摘要。42份准备证据736435字节已逐字节归档到恢复快照下preparation-evidence/，本轮/tmp源暂留作实际维护后复核，T7仅清本轮文件。

2026-10-05T13:03:50Z容量只读检查：C剩119291076608字节，230GiB未来数据盘增长66802679808字节，维护预算3221225472字节，扣减后49267171328字节，10GiB底线通过。窗口开始前重测。下一步申请范围明确的26阶段所有权交接与Harbor/Casdoor轮换，实际T6未开始。Casdoor账号源必须与拓扑发布分为两个OCI候选；本轮仍未发布/晋级/修改API账号/停服。旧单元实际运行状态和剩余大目标如下，不将本次代码整理当成新运行验收。

---

# 新体系交接状态（2026-10-05）

本文件只保留当前续接需要的事实；历次开发过程从Git及私有证据取得，不作为日常维护入口。工作树 `/home/zymun/worktrees/platform-kind-v1/k8s`、分支 `platform-kind-v1`，五仓并列；当前只修改k8s新体系，不push，不改业务仓、旧sunmoonai或冻结Luna参考。

## 已完成单元与批准边界

所有者批准第二个两小时窗口：2026-10-05 08:25:05–10:25:05 UTC（16:25–18:25 CST）。范围是ES永久修复发布、整套统一停启、Harbor全目录摘要与真实节点拉取；不关闭WSL、不删除重建集群。停服前在执行进程内复核时间，预留15分钟恢复。当前开发阶段容量底线10GiB，仍扣除数据盘长满230GiB的增长及操作预算；进入真实服务阶段再确定运维约束。

## 已完成的运行状态

- 原生 Make→独立Ansible模块→Flux/SOPS；已有环境整套platform-deploy、统一platform-check已通过。修复说明文档误入发布门禁后，最后一次完整platform-deploy退出0，46个recap全部failed/unreachable=0；最终健康及Harbor/资产比对均通过。完整原始日志归档到本节私有证据，不保留/tmp作为依赖。
- 独立root运行副本 `/opt/sunmoon/host/sunmoon-kind`、统一target、cluster/boot单元及Harbor/entry依赖已安装。Windows `sunmoon-data-mount` 为所有者登录触发、Highest/Interactive、无分钟周期，实际执行0；固定输入在管理员持有的ProgramData目录，不依赖worktree。
- 六个新旧节点 restart=no；旧Linux附盘单元disabled、新boot enabled。boot当前inactive，因为通过手动start恢复；不能当作真实开机证明。新target/cluster/Harbor/entry active。
- 新三节点sunmoon-kind运行、Ready；原始kind控制面停、两个worker运行。57个Running Pod全部Ready、33个Completed Job保留；51个Flux阶段当前代次Ready，13组PV/PVC Bound/Retain。
- 第二窗口两轮完整stop/start和重复start通过；重复start前后90个Pod UID和重启计数一致。平台/四应用真实公共协议、Harbor认证推拉、三节点Always认证拉取和DNS通过。所有节点、Docker卷、业务卷与数据保留。

## 固定身份与路径

- kubeconfig `~/.kube/sunmoon-kind.config`，context `kind-sunmoon-kind`；kubectl `infrastructure/.tools/bin/kubectl`。Kubernetes1.36.5、KIND0.33.0、Calico3.32.2；版本事实源为物料/image锁。
- kube-system UID `67d27d4a-f9ad-4f01-a37f-225144cacaef`；节点精确ID/挂载事实源 `/data/kind-clusters/sunmoon-kind/bootstrap/identity.json`，不要手写复制ID执行删除。
- Harbor2.15.2，宿主后端11443，公共仓库 `harbor.sunmoonai.com:30443`；独立数据 `/data/harbor/platform-kind-v1`。新集群入口29443、API27443。
- 数据盘230GiB，UUID `a28de356-4ba1-4a21-93f5-744b9b9d8be0`，`/mnt/sunmoon-data` bind到 `/data/kind-clusters` 和 `/data/harbor`；禁止覆盖 `/data/kind-local-storage`。同C物理盘，不防硬件故障。
- 新物料根 `~/k8s-packages`，唯一配置site.yaml；旧物料根仅供原始部署。真实秘密在各模块私有配置/独立备份和SOPS，不能输出或提交。
- 已晋级源 revision `a49760273f05320f16231647d253e25541a94e1f`，digest `sha256:9f7bce56f15708fa015a8c967b32f7f802724e50bab4aebb60ee02676140b33f`。文档/宿主修复提交不自动改变晋级源。

## 本单元修复与证据

1. ES emptyDir保留0440TLS副本导致普通cp重启失败。原模板改 `cp --remove-destination`，保留Secret/数据/权限；a4976027发布、3ef5f402晋级，实际镜像重复复制、滚动及两轮冷启动通过。一次临时权限恢复只为先恢复现网，不成为日常依赖。
2. Docker重写节点hosts丢失Harbor网关，解析127.0.0.1后误访问节点Traefik证书。19191323在原ready/start恢复拥有节点的精确网关记录；未关TLS、未改代理/外部DNS。拉取探针另修正shell参数转义并保存失败Job/events。
3. 原生Windows安装器规范化短账号SID；Bash JSON比较加引号；容量脚本在本地C路径与root副本核对，不绕过RemoteSigned；API readyz、Pod/Flux加入有界收敛等待。
4. 3b4a6912只排除组件README参与晋级对象diff；全GitOps工作区仍须提交，所有其他文件仍严格匹配。只读核对接受README差异、拒绝实际ES声明差异；原失败总入口日志保留。
5. 第二窗口基线40仓库/104镜像条目；data完整冷态清单2676文件。registry/secret共1086文件、13,210,981,875字节路径/大小/SHA256完全保持。24处可变内容仅23个PostgreSQL文件及1个Redis文件；不声称数据库物理字节不变。完整目录逻辑digest/标签/大小、PV/PVC及Job身份、六节点ID/挂载/运行态、Docker卷集合比对通过。

私有证据 `/data/kind-clusters/sunmoon-kind/bootstrap/evidence/lifecycle-maintenance-20261005T0825Z`；前窗口0419Z独立保留。原安装回退 `/mnt/sunmoon-data/backups/host/lifecycle-a2gzkked`。原窗口等管理员操作后已到期，停服前未重新核对；发现后结束新增停服并恢复。失败原始记录不得覆盖为成功。

## 日常入口与后续顺序

日常维护以docs/README.md和模块手册为准：platform-deploy/start/stop/status/check均由 `make -C infrastructure` 调用，保留模块配置开关及单组件入口。修改声明仍render/stage→审阅提交→flux-release→显式晋级→原生bootstrap，不自动部署未批准配置。

1. 本单元完整部署/两轮启停/镜像与卷验收已完成。临时日志和一次性助手逐字节归档后清理；实际运行文件、任务输入、原任务XML及必要回退备份保留。
2. Windows/WSL DNS和系统CA信任、真实浏览器访问；准备具体恢复操作卡后另批真实Windows/WSL关闭/重启。当前任务执行时盘已挂好，不证明缺盘冷启动。
3. 单独维护批准后执行KIND删除重建持久化验收：保护原始kind与Harbor，核对全目录/全部镜像摘要并由新节点认证拉取。不能用当前启停通过代替。
4. 长期空间管理：统一查看/预览/执行，持续容量/告警、Harbor保留GC、构建缓存、日志/索引和备份轮换；删除政策先确认，保护在用/回退镜像及必要备份。只已有批准日志轮转自动运行。
5. 数据库/对象原文/私有输入完整备份恢复、机器外落点待所有者选定；安全门禁/官方修复跟踪、按需身份轮换、业务完整功能和云端建群实机验证仍未完成。
6. 最终清理与维护文档收敛；保护原始kind、新体系及所有者指定Luna参考。本轮未使用东京；不能泛删别人/tmp或原始代码/数据。

本次维护已批准：2026-10-05 13:13:01–15:13:01 UTC；截止epoch 1791213181，14:58:01 UTC后不开始新增动作，预留15分钟恢复。源/旧阶段UID/spec/Ready与149个受保护对象重新核对完全一致。

### 本窗口最终结果（2026-10-05 14:45 UTC 关闭）

执行者在操作卡第5步结束时断网退出，剩余由接手者在同一窗口内收尾；所有动作在14:58 UTC"不开始新动作"线之前启动。

已完成（操作卡1–5）：拓扑源e59bdc00/digest e26d2a19经原生platform-deploy OBJECT=all应用，47段recap全部failed/unreachable=0。旧根在第一次新源应用前撤销了旧阶段暂停；发现后核对原UID/Orphan并重新暂停，显式收敛logstash后188个对象全部归属26个新阶段。仅删除elk-runtime/platform-services两个控制对象，DeleteOptions带UID/resourceVersion前置条件和Orphan传播；无工作负载/卷删除。公开PostgreSQL deploy（10段）/check（2段）、Tpl-Web deploy（7段）/check（2段）、整套重复deploy（47段）全部failed=0。整套platform-check OBJECT=all首次在14:00 UTC失败：第7段对tpl-database阶段的Ready断言在整套重复部署刚结束时取到瞬时非Ready，verify.yaml:51断言无等待直接判失败；期间审计63阶段Ready、无异常Pod。14:40:35–14:43:53 UTC重跑退出0，10段recap failed/unreachable=0（两段changed=1为协议探针回执）。关闭前审计audit-144449.json：149受保护对象UID/spec无差异、无新增对象、63阶段Ready、无暂停、源摘要不变。

未执行（操作卡6–8）：Harbor admin与Casdoor built-in/admin实际轮换均未开始，三个人工账号密码与窗口开始时相同，Kibana不变，密码表当前值未改。Harbor改密前105个镜像条目和1090个registry/secret文件摘要仍私有保存可供下次使用。

证据：/mnt/sunmoon-data/backups/host/component-account-20261005T124637Z（root 0600），含topology-all、scope-*、topology-repeat-all、首次失败的topology-public-check.log（保留不覆盖）、通过的topology-public-check-rerun2.log、audit-*.json；topology-public-check-rerun.log是被中止的首次重跑残片，仅到只读阶段，无副作用。本轮86个/tmp助手脚本与审计JSON已复制到同目录maintenance-tmp-evidence/并逐文件SHA256核对（MANIFEST.json），/tmp原件暂留待所有者确认后清理。

后续：Harbor轮换仍需在线窗口执行；Casdoor轮换与其余账号预设并入新集群sunmoonai-kind冷建；verify.yaml的阶段Ready断言改为有界等待；T7聚合源码清理并入组件合并重构。

---

# 重构检查点（接手后，2026-10-05起）

目标不变：dev/prod parity，本机KIND与将来云端共用同一套组件声明与发布链；只参数化环境。顺序：A 阶段真源下沉到组件并合并services/applications → B make ci → C 环境参数化（去sunmoon-kind/:30443/nodeSelector硬编码，platform与providers/wsl-kind分层）→ D 冷建sunmoonai-kind并预置管理员口令 → E 切换入口、退役sunmoon-kind → F/G 轮换工具与文档收敛。每阶段结束才做一次flux-release+显式晋级；阶段内只做离线等价验证，不碰集群。

## A1 已完成：阶段图唯一来源为组件stage.yaml

31个对象各得`gitops/components/<对象>/stage.yaml`（62阶段，含26平台+36应用）；`infrastructure/components/stages.py`扫描成图并承接原选择算法；`components/topology.yaml`渲染/暂存/校验单一`gitops/clusters/kind/stages.yaml`，替代services.yaml+4个applications-*.yaml和common/backend/stages.yaml.j2；`services/layout.yaml`只剩命名空间与卷清单；`host/deployment.yaml`不再硬编码应用名与四个文件路径（应用名在applications/config.yaml）。

离线验证：渲染的62个Kustomization文档与HEAD五文件逐文档相等；47个OBJECT（含分组、模块、两个非法值）在select动作下选择JSON（三个列表字段按集合比较）、.mk与退出状态与HEAD完全一致，另抽5对象×deploy/stage/check一致；`required_stages`仍满足拓扑序；`services-render OBJECT=all`实际运行（575任务）75个公开声明与已提交相等，`application-render APP=knowbase`14个相等；6个剧本syntax-check通过；`make -n`对比只多出topology步骤。

## 所有者补充的范围（2026-10-05 23:20）

旧体系有而新体系缺的组件，在通用渲染器完成后按组件契约补齐：`ops-platform/pgadmin`（密码表14）、`ops-platform/redisinsight`、`ops-platform/flower`（依赖rabbitmq）、`ops-platform/mongo-express`（旧KIND默认关，沿用）；`relay-platform/relay`与`sandbox-platform/provisioner`（自研镜像，走应用构建链）。待所有者决定：`cicd-platform/jenkins`（旧KIND未启用、仅远程集群；新体系CI为make ci+宿主Harbor）。不加：`question-data-demo`（演示）、`utils/db-provisioner`（已由common/backend/database替代）。

有Web界面但新体系未暴露的组件，各加`ui`子阶段，沿用`elk/kibana/ui`模式（独立hostname、平台CA证书、IngressRoute、NetworkPolicy、入口SNI路由、组件自身账号）：RabbitMQ管理台（15672）、Neo4j Browser（7473）、AIStor控制台（9001）已按该契约写入gitops并`services-stage`；拓扑`gitops/clusters/kind/stages.yaml`现含`rabbitmq-ui`/`neo4j-ui`/`object-storage-ui`。Kibana原本已有。RAGFlow本fork的9380是自定义HTTPS API（`/sunmoon/ready`），不是库存Web UI，本轮不加。Traefik仪表盘默认关。不做：Elasticsearch API路由、数据库TCP直通到公共入口。

所有者更正：新集群管理员从一开始全部映射密码表。已打开 1/4/8/10/11/12/15a/15d/18/19 的 `table_import`；第8/11/19项用户名改为新体系现网名以便导入校验。导入只写首次预设，不覆盖 sunmoon-kind 已有身份。冷建 `sunmoonai-kind` 时首次初始化读取这些预设。应用账号2/3/5–7/9不映射；Jenkins 待组件接入。pgAdmin 第14项已随 ops-platform 接入。

验证脚本已接到`services/verify.yaml`（选中对应`*-ui`或 ops 控制台阶段时走集群入口端口做TLS/登录页/有界API核对）。尚未flux-release、未晋级、未`platform-deploy`、未应用宿主entry；浏览器不可用。Traefik CRD命名空间已加入`messaging-platform-dev`与`ops-platform-dev`（已改生成的`traefik/workload.yaml`）；完整`OBJECT=ingress-platform/traefik make services-render`依赖`services-chart`产生的`.build/components/chart-source.yaml`，本轮未跑chart以免动Harbor。

待办门：工作树gitops已与晋级对象e59bdc00不同，`platform-deploy`会被validate-release拒绝直到下一次flux-release+晋级；`platform-check`不受影响。

## A2 已完成切片：应用渲染并入通用组件渲染器

已抽出 `gitops/components/app-platform/common/backend/prepare.yaml` 与 `common/frontend/prepare.yaml`；四应用 backend/web/admin 的 `stage.yaml` 指向它们。加密路径改为 `.build/components/<object>/...`。`application-render/stage/validate-release` 转接 `services-render/stage`（`OBJECT=app-platform/<app>-app`）；`platform-stage OBJECT=all` 只跑一次 `services-stage`。`applications/deploy.yaml` 负责 plan/validate。

离线/等价验证：阶段图 65/34，12 条应用 prepare 入图；`render.yaml`/`deploy.yaml` syntax-check 通过；`make application-render APP=tpl` 196 任务 failed=0，26 个候选与已提交公开结构及 SOPS 语义全等；`APP=knowfeed` 250 任务 failed=0，34 个候选（含 storage/service-identity）全等。未跑 knowbase（provider 会访问 RAGFlow API）、未 stage、未 flux-release。

## ops-platform：运维控制台已完成切片

已按 Kibana UI 契约写入 `ops-platform/{pgadmin,redisinsight,flower,mongo-express}`：独立 hostname、平台 CA、IngressRoute、NetworkPolicy、入口 SNI；命名空间 `ops-platform-dev`。pgAdmin 映射密码表第14项（`table_import` 已写入首次预设，未改现网其他账号）；Flower 独立 basic-auth（无表行）；RedisInsight 无控制台登录；mongo-express 默认关（镜像锁未收录，未渲染）。Traefik CRD 命名空间已含 `ops-platform-dev`。foundations 增加 ops 命名空间/puller，并把 ops 列为 PG/Redis/Rabbit 客户端。

离线验证：阶段图 69/38（含禁用的 mongo-express）；`render.yaml`/`topology.yaml`/`verify.yaml`/`accounts.yaml` syntax-check 通过；`OBJECT=ops-platform make platform-account-import` 仅第14项 `preset_changed=true, live_account_changed=false`；`make services-stage OBJECT=ops-platform` 178 任务 failed=0（flower/pgadmin/redisinsight 候选入树，mongo-express 未渲染）；随后 `OBJECT=foundations` 61 任务 failed=0（runtime/network/kustomization 含 ops，新增 `ops-platform-dev-puller.sops.yaml`；既有三个 puller 密文载荷与 HEAD 相同，已恢复以免无意义轮换）。拓扑 68 个启用阶段，含 `pgadmin`/`redisinsight`/`flower`。未 flux-release、未晋级、未 platform-deploy、未应用宿主 entry。

## 应用 check 拆分、relay 与 sandbox（本切片）

`application-check` / `application-check-public` 改为 `applications/verify.yaml`；`deploy.yaml` 只保留 plan/validate。`deploy.yaml`/`verify.yaml`/`render.yaml`/`topology.yaml`/`services/verify.yaml` syntax-check 通过。

`relay-platform/relay` 已写入并 stage：独立 hostname `relay.sunmoonai.com`、平台 CA、IngressRoute、无 NodePort；镜像钉 KIND v1-r3 的 `app-images/relay` 摘要。`sandbox-platform/provisioner` 契约已写但默认关：现镜像把沙箱 NP 写死 `edge`，动态 Pod 不满足 restricted PSS，启用前须经应用构建链重建。foundations 增加 `relay-platform-dev`/`sandbox-platform-dev` 命名空间与 puller。

离线验证：阶段图 71/40（含禁用的 mongo-express 与 sandbox-provisioner）；`OBJECT=relay-platform make services-stage` 82 任务 failed=0；随后 `OBJECT=foundations` 67 任务 failed=0。拓扑 69 个启用阶段，含 `relay`，不含 `sandbox-provisioner`。既有 data/messaging/app 三个 puller 密文载荷与 HEAD 相同，已恢复。未 flux-release、未晋级、未 platform-deploy、未应用宿主 entry、未跑应用构建链。

所有者补充（2026-10-06，远程记）：「先上 Argo」= 冷建时直接用 Argo，Flux 侧不再加功能；A 段只做与控制器无关的部分（聚合源清理、入口收敛），重构后的 flux-release/晋级只在现网需要发新声明（第 10 步的应用）时做一次。

所有者决定（2026-10-06，远程记）：新体系由远程接着做完，本地由 Cursor 按 `sunmoonai/docs/process/switch-test/inbox/` 的待办跑。主线改两处：**B 段的 CI 是宿主上的 Jenkins**（容器，调本目录的 `make` 目标，不进集群），不再是 `make ci`；**D 段冷建 `sunmoonai-kind` 之前把 Flux 换成 Argo CD，并趁机规范化**（组件改 Helm chart / Kustomize overlay 让 Argo 原生渲染，依赖改 sync wave / app-of-apps，晋级钉 Git 提交号，密文走 ksops；Ansible 只留宿主与建群）。Flux 在现网用到退役为止。parity 不变：一套声明，环境只差参数。详见 `sunmoonai/docs/design/decisions.md`。

所有者决定（2026-10-06）：mongo-express / sandbox 保持默认关；不重建 Harbor 自研镜像。Jenkins 再议：现网 Harbor 已是宿主模块，不是集群内 `cicd-platform`；本机 KIND 旧体系也未跑 Jenkins。冷建路径下 A 收口不必 flux-release/晋级/deploy；这三步只在 D 冷建 `sunmoonai-kind` 前做一次，且只发布到 Harbor、晋级环境源指针，不往现网 `sunmoon-kind` 部署。当前主线：A 离线收口（审阅/本地提交）→ B `make ci` → C 环境参数化 → D 发布晋级并冷建。

---

# 远程接手后的事实（2026-10-06 起）

- 分支：新体系已并入 `fable`，此后在 `fable` 上改、在 `fable` 工位跑；待办在 `sunmoonai/docs/process/switch-test/inbox/`，结果在 `sunmoonai/scripts/results/`。
- 待办 18（2026-10-06 12:55 +0800，fable 工位）：工具装上（`.venv` 37M、`.tools` 481M），`platform-plan OBJECT=all` 退出 0；`preflight`、`platform-status` 退出 2——`/data/kind-clusters`、`/data/harbor` 两个 bind 不在，`sunmoon-kind` 三节点、Harbor、入口容器和旧 kind 两个 worker 都在约 4 小时前同时退出（255），API 27443、Harbor 30443 都没在听。**这是第一次真实 WSL 开机，单次开机恢复单元没有把平台恢复起来**（验收边界「未完成项」第 1 条的实际表现）。待办 19 先查它停在哪，再用 `platform-start` 恢复。
- 本地助手的接手说明（结果文件第六节）：A 段还没做的——聚合源清理、入口收敛、重构后的 flux-release/晋级/部署、`make ci`、环境参数化；`flux-source.yaml` 仍指 `e59bdc00`/`e26d2a19`，与 `fb55eced` 之后的工作区不是同一提交，集群起来后也不能直接 `platform-deploy` 这次重构；`platform-kind-v1` 工位里唯一没提交的是密码表；`services-stage` 这个名字还在但和 `platform-stage` 同一渲染器；foundations 的 prepare 会重加密已有拉取密钥，要按等载荷恢复；晋级的 revision 必须是 OCI 包对应的 Git SHA。
- 待办 19、20（2026-10-06）：第一次真实开机的失败查清了。登录时的附盘任务先 `wsl.exe -d Ubuntu`（启动 Ubuntu）再 `wsl --mount`，systemd 按 fstab 挂盘时盘还没附上；事后挂的盘只在 PID 1 的挂载命名空间里，用户会话（包括 `wsl.exe -d` 新起的）永远看不见。另外系统盘上留有 10 月 3 日的 `/data/kind-clusters/sunmoon-kind` 残留（52K 空目录），守卫因此拒绝绑定；已改名 `/data/kind-clusters.rootfs-stale-20261003`，没删。用 `sudo nsenter --target 1 --mount --` 进 PID 1 命名空间跑 `platform-start` 退出 0（4 分 15 秒），现网恢复：3 节点、63 阶段 Ready、57 Running Pod、13 PV。`platform-check OBJECT=all` 退出 2：工位阶段图比现网（源 `e59bdc00`）多 ops 控制台、三个 UI、relay 共 7 个阶段，等第 10 步发新声明时一起上。修法（待办 21）：附盘脚本先附盘再启动 Ubuntu；Makefile 在命名空间不一致时自动 `nsenter`；真实重启验收是待办 22。
- 待办 21、22（2026-10-06 13:48–14:05）：附盘顺序修好、运行副本和 Windows 任务重新发布、真实 `wsl --shutdown` 后平台自己恢复（`verification.md`「真实开机恢复」）。开机恢复这一条闭合；Windows 整机重启、删群冷建仍未验。
- `infrastructure/` 的收敛（所有者 2026-10-06 问）：现在不动。B 段和 Jenkins 一起做入口收敛、`applications/` → `build/`、检查并进 `components/`；D 段换 Argo 时渲染层整体换掉；`artifacts/` 不重构。见 0010 第九节。
- 待办 23、23b、24、25（2026-10-06 下午，fable 工位）：12 个应用镜像按 fable 源码构建并发布，锁进 `gitops/`（`7800e159`）；会合点、供给器镜像发布并暂存（`005bd0e0`）；knowfeed、investment 候选暂存（`ee6e0216`），四个部署计划核到 fable 的迁移 head。没过的：沙箱镜像 1200 秒超时且没留日志；会合点暂存因阶段图漂移拒绝；knowbase 暂存卡在供给器前缀断言。远程处理（`e3ce871f`、`0559d44d`）：组件镜像脏树检查只看自己的源码目录、构建日志边跑边落盘、超时按镜像配（沙箱 3600）、Debian 源随下载模式、组件镜像可各钉各的提交、knowbase 只读前缀放宽到 `info/`（供给 Job 代次 v2，容忍「策略已挂」）。收尾在待办 26。
- 待办 26（2026-10-06 16:22–16:46，三次续跑）：沙箱镜像按 fable 源码建成（76 秒，`platform/sandbox@…e758ccb2…`，钉 `e3ce871f`），供给器候选的 `SANDBOX_IMAGE` 跟着换；会合点再暂存无差异；knowbase 暂存通过（`domain.sops.yaml` 只有验签公钥、密文；供给策略前缀 `info/`、Job 代次 v2）；四个部署计划与 `platform-plan OBJECT=all` 退出 0。途中两处修正：Debian 源改 http（slim 基础镜像没有 ca-certificates，`86d8f6de`）；只引用签名密钥对的应用不要求 `private_dir/domain.yaml`（`7f756882`）。0010 第 0–4 步闭合；第 5 步（待办 27）等维护窗口。
- 待办 27（2026-10-06 晚，进行中）：核对、`pg_dumpall`（840K，6 库）、`flux-release`（候选 `b5b9658e` / `sha256:ba81d7d9…`）、晋级提交都过了。整套部署三次停下：1）fable 工位没有 compose（已改：部署前自动装，`145fe107`）；2）入口配置要加 5 个域名，部署链拒绝改活着的监听（按设计先 `entry-stop`）；3）**`entry-stop` 连带停了 Harbor 和集群**：统一目标 `Requires=` 三个服务，停一个传播成停目标，目标再按 `PartOf=` 停其余。Harbor、入口已用 `registry-start` 恢复；集群要 `platform-start` 拉回。目标模板已改 `Wants=`，重装在待办 28（27 之后）。
- 待办 27 续四（2026-10-06 17:40–17:57）：集群 `platform-start` 拉回（184 秒）；整套部署进到发布/调和段，根 Kustomization 等 10 分钟未 Ready：71 个阶段里 30 个未就绪。两个原因：1）pgadmin、redisinsight、flower 三个控制台镜像不在 Harbor（ImagePullBackOff），发布段没有发它们（原因待查，账 47）；2）四个应用的 redis Job 和 knowfeed/investment 的 service-identity Job 因后端镜像换了而撞「Job 模板不可改」（rabbitmq、identity 两种 Job 同样用后端镜像，阶段还没到）。处理：四种身份 Job 的名字像迁移 Job 一样带后端镜像摘要（`common/backend/{redis,rabbitmq,identity,service-identity}`、`applications/verify.yaml`），账 46。现网状态：旧包的应用仍在跑（`lastAppliedRevision` 仍 `e26d2a19`），新包部分对象已建、在等依赖；未退回。下一步：四应用重新暂存 → 发布三个镜像 → 再发布、晋级、部署。
- 待办 27 续五（2026-10-06 18:16）：四应用重新暂存（Job 名带摘要）。三个控制台镜像的本地归档从没下载过（ops 切片后加的，没走过 `services-materials`），`services-publish` 在「拒绝不安全的已有归档」退出 2。账 47 查清：整套部署里发布平台镜像那一段（`services-bootstrap`）排在 `flux-bootstrap` 的 `flux-source-apply` 之后，源一应用全部阶段就开始拉镜像，发布段根本没跑到。已改：`platform-deploy` 在 `flux-bootstrap` 之前先 `services-verify-materials services-publish`；缺的归档仍要显式 `services-materials` 下载（物料规则不变）。
- 待办 27 续六（2026-10-06 18:28–18:52）：三个控制台镜像下载、发布；第二次发布晋级（`68aeb0fd` / `sha256:60450a67…`）；整套部署后 71 个阶段里只剩 flower、pgadmin 两个 HealthCheckFailed，根阶段因此未 Ready（`lastAppliedRevision` 仍旧包，但子阶段都已应用）。四应用带摘要的身份 Job、迁移 Job 都 Complete；runner、relay、provisioner 1/1；tpl、investment 的 application-check(-public) 退出 0；knowfeed、knowbase 的检查失败是验证脚本找不到本工位的 `mc`（整套部署没跑到装它那步）。处理：flower 加 `command: [celery, flower]` 和 `CELERY_BROKER_URL`；pgadmin 给 `/var/log/pgadmin` 临时卷；`application-check(-public)` 先装 mc。
- 待办 27 续七、续八（2026-10-06 19:00–19:19）：flower、pgadmin 重新暂存，第三次发布晋级（`2a0f9993`，指针 `084a3085` / `sha256:5ffeae56…`），`flux-source-apply` 后 **71 个阶段全 Ready，根阶段 `lastAppliedRevision` 已是新包**。fable 的应用第一次在新体系上跑起来。检查：tpl、knowfeed、investment 的 application-check(-public) 退出 0；`platform-check` 与 knowbase 的检查各差一处工具问题（`platform-check` 的对象存储检查在装 `mc` 之前跑；knowbase 检查写诊断文件的 `.build/models` 目录不存在），已改，重跑检查即可，不用再发布。Git tag `release-20261006-1` 打在 `2a0f9993`。
- 第 7 步开始（2026-10-06 19:30）：所有者用 Casdoor 管理员登录成功（现网密码仍是初始密码，没轮换到密码表第 18 项；`platform-account-check` 报 `verified_login: true, password_changed: false`）。登记模型 key 报 `internal_error`：后端用 `cryptography.Fernet` 加密凭据，要 32 字节 urlsafe base64 的密钥，而机制生成的随机值是 40 位字母数字。已改：`domain_secrets` 的随机值支持 `format: fernet`；investment 的 `WORKBENCH_CREDENTIAL_KEY` 改为 fernet，要换钥（删主备私有文件和密文候选后重新暂存，账 48）。
- 待办 27 续九（2026-10-06 19:27）：只重跑检查。`platform-check` 卡在 RabbitMQ 管理台检查读凭据文件时少了一层 `service_credentials`（ops 切片写的、从没跑过）；knowbase 的领域检查在 investment-api 里跑 HTTP 检索校验器报 ModuleNotFoundError：fable 的 investment 后端已没有 HTTP 检索端口（改走沙箱 MCP），校验器删去这一段。两处都只改检查，不用发布。
- 待办 27 续十（2026-10-06 20:03）：investment 的凭据密钥换成 Fernet 格式并第四次发布晋级（`194ab597`，指针 `6bbac954` / `sha256:11bebe39…`，tag `release-20261006-2`）；investment、knowbase 的检查全过。`platform-check` 只剩 Neo4j 控制台：Jetty 回 400 Invalid SNI，原因是 Traefik 对后端的 SNI 是集群内名字而透传的 Host 是公网名字；已改 IngressRoute `passHostHeader: false`，下次发布时带上。
- 所有者决定（2026-10-06）：**边缘放东京服务器**（远程助手所在的云 VM，Ubuntu 24.04，2 核 3G，80/443/7000 空闲，有 Docker）。边缘（Traefik、会合点、frps）和集群里的 frpc 做成新体系的部署单元，排在第 7 步人手点通之后；域名与证书、机房上行仍待定。`docs/拓扑.md` 第一节是正式拓扑，第二节是现网过渡形态。
- 待办 27 续十一（2026-10-06 20:27）：供给器新镜像（带拉取凭据）第五次发布晋级（`aa8e2634`，指针 `72113bee` / `sha256:a6575451…`，tag `release-20261006-3`）。Neo4j 控制台改成不透传 Host 后仍 400 Invalid SNI。按 Jetty 12 的源码：它核的是 **Host 头与服务端自己证书的名字**（`x509.matches(serverName)`），Neo4j 内部证书的 SAN 只有集群内名字；透传时 Host 是公网名字、不透传时 Traefik 把 Host 换成 Pod IP，都对不上。改法：`component-tls.yaml` 支持 `tls_extra_hostnames`，Neo4j 控制台开着时把公网名字签进内部证书；路由恢复透传。现网要重签一次 Neo4j 证书（删主备 `public.crt`，私钥不动，Neo4j 会滚动一次）。
- 第 7 步进行中（2026-10-06 21:10）：key 登记成功、沙箱运行中、本地代理（Linux 版，在 WSL 里）连上会合点（`relay connected`）。查出一个没做的环节：**代理连上后后端不知道有这台机器**（账 49），「项目」页因此显示没有工作区；先用 CLI 手工登记继续点。另：WSL 里要把 `relay.sunmoonai.com` 加进 `/etc/hosts`、把平台 CA 拷到用户目录给 `NODE_EXTRA_CA_CERTS`；`pnpm approve-builds` 要批准 esbuild。
- 所有者决定（2026-10-06 21:20）：第 7 步剩下的（项目、工作、专家、数据目录、申请入库）**等账 49 做好再点**，不手工登记机器。到此已点通：登录、登记 key、拉起沙箱、本地代理连上会合点。未跑的轮次：续十二（Neo4j 内部证书加公网名字，`321f58f7`）、待办 28（统一目标改 Wants）。远程下一件：账 49。
- 账 49 做完（2026-10-06 夜，远程）：本地代理 0.2.0 的 hello 带机器名、白名单目录、上限（runtime `bdcdddd`）；会合点记住并在管理通道加 `agents` 查询（`a43473f1`）；investment 后端 runner 每 10 秒对一次账，登记机器、置在线离线（`d3ff9046`，全量 828 通过）。新体系这边：会合点镜像钉到 `a43473f1`、investment 源码钉到 `d3ff9046`、runner 放行到会合点管理口。现网验证是待办 29（重建两个镜像、发布晋级应用、所有者换新代理看页面）。
- 待办 27 续十二（2026-10-06 21:21）：Neo4j 内部证书加公网名字后控制台 200，Neo4j 项通过；第六次晋级（`9d0f126d`，指针 `cc7b2287` / `sha256:9edd08a3…`，tag `release-20261006-4`）。`platform-check` 下一项停在对象存储控制台「错误口令必须被拒绝」（校验器只认 401/403，实际状态码未知，已让失败信息带上状态码）。后面还有 pgAdmin、RedisInsight、Flower、会合点、供给器几项从没在现网跑过，和待办 29 一起探一遍状态码再统一修。
- 待办 29、28 通过（2026-10-06 22:16）：会合点与 investment 后端新镜像上线（晋级 `7bdb1be0`，指针 `357a2ff4` / `sha256:9c808c72…`，tag `release-20261006-5`），runner 日志 `machine sync starting`；统一目标改 `Wants` 后单独停入口不再连带。所有者换 agent 0.2.0 接入后，机器自动登记，能新建项目、能请专家。
- 第 7 步问数（600009 营业收入）回 dataset unavailable：知识后端的默认样例库不在镜像里，目录整个不可用（账 50，已改 `ee3b0b0c`，全量 952 通过）；另外新集群上还没有任何登记的数据集，600009 要先在 knowfeed 里走一遍采集 → 建数据集 → 登记。`platform-check` 剩对象存储控制台登录 500（账 51）。
- 待办 30 通过（2026-10-07 09:40）：knowbase 后端新镜像上线（晋级 `a1971b7f`，指针 `c68e360b` / `sha256:872ee94d…`，tag `release-20261007-1`）。账 51 查清：对象存储控制台登录时按 `MINIO_SERVER_URL` 回连自己 Pod 的 9000，命名空间默认拒绝且该 Pod 不带客户端标签，连接被丢，页面 500。改法：控制台组件加一条只放行 Pod 回连自己的网络策略（待办 31）。
- **MVP 闭环第一次在新集群上跑通（2026-10-07 上午）**：所有者在 knowfeed 申请 600009 入库并在管理端通过 → knowfeed 采集、建数据集、登记到知识服务 → knowbase 数据目录出现「上海机场 财务报表」→ investment 里请专家（财务复核），专家经 MCP 查到 2025 年营业收入 13,346,192,164.12 元并与年报原文核对；结论栏按设计留给用户填。期间修的：知识目录没默认库也能用（账 50）。另：请专家页在清单请求失败时不显示错误（页面空着），要补提示。
- 2026-10-20（远程 Fable）：产品线暂停，平台线 B 段开工（`tree-build/暂停时的状态.md`）。第 1 步宿主 Jenkins 控制器模块 `infrastructure/jenkins/` 写好、离线校验过（剧本语法、Compose config、`haproxy -c`、systemd 单元、两份锁），卡 fable-b1 给 luna（本地机）；CHECKPOINT 第 131 行「Jenkins 待组件接入」由此接入（密码表第 13 项，`platform-account-import OBJECT=jenkins`）。
- 2026-10-20 晚（luna 在本地机 fable 工位）：B 段第 1 步做成。卡 fable-b1 两次跑：第一次控制器部署全过、停在卡写错的 curl 身份；第二次接续，控制器三项核对、入口加 jenkins 路由、经入口 200、Harbor 不受影响、`platform-status` 退出 0。宿主上有了 Jenkins 2.580.1（回环 18443/18080/50000，`sunmoon-jenkins.service` enabled）。所有者浏览器走查待做。同步改成「一项工作一个工位分支，两边直接推拉 origin/<WS>」。


# 工具协议修复发布检查点

本分支 `fix/tool-roundtrip-release` 从 Jenkins #43 回执提交 c00e6766 开始，保留现网所有无关声明与配置。原始 qwen 基线候选只用于诊断，未部署。

- 运行时根因：Moonshot 发出 function_call 后附带空助理消息，下一轮回传自身历史时报缺失 tool_call_id；原样重放两次 400，删除空消息 200。调用 ID 已正确匹配。完整证据与诊断线程在 knowbench-backend/CHECKPOINT.md。
- 沙箱源代码提交 5798e312：在用户沙箱内做最小 HTTP/SSE 兼容，仅移除无内容助理消息。已通过 14 项测试、真实失败请求重放、真实 Codex 工具往返，以及确切 0.155.1 启动配置检查。
- 后端以线上 7a1c4be 为底，拒绝把进度文字当成成功，并按线程/轮次归属错误；39 项相关测试通过。确切父子仓提交由 sources.yaml 钉住。
- 用户明确要求使用现有 Jenkins。扩展原 release 的 APPS 目标列表，接受 `knowbench sandbox`；保留阶段 8 人批、不可变候选与 Flux 晋级机制。不创建第二条发布流水线。
- 来源与回退：线上 OCI sha256:1557b13795d88fb041e52475ff98516581229ed23018a6d629f66c479a1d2fa0，来源 1104dcd03f14c2f930d6dfe8d5d121558484bfaf。当前目标用户沙箱镜像 sha256:8fac3fdfb14f9c956d00cc65cb5b45aaa683500d162b3ffba7a3110d63cea720；后端镜像 sha256:c33b10ce51bec19eab92360ee16708d9389b8928e9e5df7fed3c19dd66fad59b。
- 发布仅更新供给器的沙箱镜像摘要；已有用户沙箱需在工作台重新供给。不能把供给器 Ready 当成已有用户沙箱已更新。没有修改专家 bindings、任务状态或绕过用户的数据需求确认。
- 搜索声明已确认保留；诊断中模型没有真正完成 webSearch，不能报告搜索端到端验证成功。

待办：推送独立修复分支，触发 Jenkins `release`，APPS="knowbench sandbox"、PIN=keep，审核候选差异后等原有人批；批准后验证目标用户沙箱镜像、find_subject → request_data → 待确认流程。人批不能由修复代理代点。

## 2026-11-02 本地工位对齐与双轨计划接手

- 所有者明确选择：最新已发布版本 + 本次已验证工具回传修复；后续在 `/home/zymun/worktrees/luna` 的各仓 `luna` 分支开发。
- 五工位范围：cursor、fable、kimi、luna、qwen，各含 sunmoonun、sunmoon-link、六应用父仓及 18 子仓。master 与 Jenkins 独立检出不作工位修改。
- sunmoonun 基于 release #43 回执 `c00e6766b24c0d249938152d35511116f6f169ff`，修复来源 `7ead007f6271f3516c1e28ec5e8b2bf54f978d09`；knowbench 父仓 `525735629ed6ba70f3a87038ed2b53ecce1ae453`、后端 `1e7834fae769230d508bca6e399167c3b8a91f6f`；其余应用依 sources.yaml，Link 依 agent-releases/config.yaml 的 0.5.5 源码钉。
- 四份双轨交付相关文档从 qwen `bac3696a5d80699c4549d9b3b22740c5ad19c209` 带入，开发工位改为 luna。文档中 WP 完成状态是历史记录，不能据此声称未纳入本基线的 qwen 代码已经发布或验收。后续先比对保留的 qwen 业务提交与 WP 清单，复用合格实现并补验，避免重写。
- 对齐前各检出 HEAD 留在 `backup/pre-align-20261102/<工位>` 本地分支（每仓独立）；分叉的原工位分支重命名保存，再从固定基线创建同名分支，不 reset、不清理文件、不自动 push。qwen 两份未跟踪文档经审阅均有用：保留空间盘点、归档与清理证据，补充历史适用范围及权限处理纠正后纳入共同提交；原始字节另存本地对齐备份，工作区不留未跟踪副本。
- Jenkins #44 使用原发布分支 fix/tool-roundtrip-release，工位对齐没有改变其候选。2026-11-02 01:24 后该作业 SUCCESS：人批、部署、knowbench 与 sandbox-provisioner 核验通过，release-20261102-1，发布回执提交 `f90b34a756c9707c0f4bc44ff9340ed10a670780` 已合入共同工位基线。修复已通过 39 项后端测试、14 项传输测试及真实失败请求重放；已有用户沙箱重新供应和真实补采闭环仍待完成，不得写成全链已修复。
- 本轮对齐的固定目标与每个工作区旧提交见 scripts/results/workstations-alignment.20261102.json；该记录为本地 Git 工作区证据，不是发布回执。

### 对齐核验与下次继续

- 五工位 130/130 检出已核对目标 SHA、同名分支、空 git status；30/30 应用父仓子模块指针一致；130/130 原 HEAD 有备份分支；master 各仓未改。最终核验原始结果：`/home/zymun/worktrees/luna/workstation-alignment-20261102/verified.json`。本轮未向远端推送工位分支。
- 最终补入 release #44 的生成声明、已晋级指针与回执，保持所有工位根仓一致；本次准备克隆留作排查证据，后续实现用 `/home/zymun/worktrees/luna/{sunmoonun,knowbench-app,knowbase-app,knowfeed-app,...}` 正式工位。
- 原故障下一步：从正常工作台入口重新供应已有用户沙箱，确认实际镜像为 `sha256:ec14e4a591d7401ad222b579d745fa4c5c6e9292c28055c696b9671661f7823c`，再验证 find_subject → request_data → 用户本人确认 → knowfeed → 恢复分析。不要替用户确认采单；本轮无可用的用户网页登录会话。工作台后端已发布镜像为 `sha256:c16adcea4c2c3d8c7cb27f0de9270f8e27c7cc5772245d53523ddbb8337d14e8`。
- 双轨计划下一步：先复核 `backup/pre-align-20261102/qwen` 中三后端的未发布实现与计划状态。knowbench 额外业务提交 `74a443c`、`c166baa`、`c656a65`；knowfeed `278f372`、`092d8a7`、`35fc025`；knowbase `5a22a91`、`c804dd4`。按正式设计决定是否纳入，不能按提交标题直接认可 WP/DCF/Wind 完成。备份分支位于相应 qwen 子仓，luna 子仓需要时可从本地取对象。
- 所有者已在界面设置 Full Access，但本次普通执行仍报 no new privileges；所有者准备退出后重进 luna 会话。新会话先核实实际权限，不把旧提权选项机械沿用。

- 2026-11-02（luna，#44 发布后验收）：真实财务任务已越过原工具回传失败点，成功提出采单并等待用户确认；发现长采单挤走步骤栏、等待说明误用下一步骤文字、工具契约未向模型提供合法词汇与日期形状。已修复并钉 knowbench 父仓 8fc56c8（后端 143912c、前端 7c58ef9），拟经现有 Jenkins 发布。后端 1196 passed/92 skipped，前端 347 passed/2 skipped；后端 pyright 16 条基线既有错误未增加。真实任务尚未确认，采集分析未验收。证据见 scripts/results/knowbench-data-confirmation.20261102.md。


## 2026-11-02 #45 后：排队提示与通用计算候选

- 实测项目 2571913d 中 9319ae09 已完成 data-plan 并 WAITING(DATA)；a0d5cca5、8b79ad62 仍 RECEIVED 排队。前端忽略 task/queued，因没有模型 turn 显示“还没有开始”。web 6e4e0c4 修复提示、项目入口及本条取消（原鉴权/CSRF 接口），353 passed/2 skipped，完整 check 和两尺寸构建预览通过。
- backend bfcfc8c 清除既有类型错误；eb61d25 支持有界 Decimal 分数幂，1204 passed/92 skipped，ruff、pyright 均通过。parent 20427cc，候选沿 fix/data-confirmation 经 Jenkins，源钉已更新；不能把候选当上线。
- 当前采单误解模糊的未来两季度为 2026Q4/2027Q1，用户未确认。所有者指定固定目标 2025Q1/Q2；应通过本人正常入口调整输入和重复任务，不能后台改用户任务或代确认。2024 年报已披露后做这道题，不等于严格 2024 年末的无前视回测。
- 第二轨明确包括任务内按作者方法论动态选步骤/工具；已更新主计划、decisions 与 WP-10/11；代码尚未实现动态规划，不能声明通过。Wind W0 仅本人研发最多 5 次，已做 3 次，缺服务端许可及关键元数据/全文覆盖，判 undecidable；W1 未放行。详见 Wind-W0评估.md。
- 本轮实际 Full Access、approval policy never；不重复要求终端提权。但 Jenkins 人工批准是发布链业务门，不能由代理代批。其他工位暂保留已发布 #45，候选上线后才按确认基线对齐。


## 2026-11-02 夜间交接：#46 成功，第二轨候选未发布

- 所有者最后明确：保底演示仍用巨潮，明天回来验收；今晚继续独立工程，需要本人确认或在场的留明天。#46 已由 Jenkins 记录 admin 在 02:33:50+08 批准，本助手没有调用批准接口；12 阶段成功，release-20261102-3，回执 b0539cbc。线上镜像、排队前端资源、纯计算样例核验见 scripts/results/release-46-live-check.20261102.json。网页刷新即可，无需沙箱更新。
- 发布基线已对齐五工位 130 个 HEAD；此后仅 luna 保留第二轨开发（提交后工作区干净）。对齐证据 workstation-alignment-20261102/verified-release46.json。不要再把 luna 新开发强推到其他工位或部署源；sources.yaml 继续钉发布基线。
- 真实验收现场保留：任务 9319ae09（会话 d206f1df-54f9-4d85-a999-b73100a870c5）完成定数据且 WAITING(DATA)，confirmation_id/demand_id 为空，八步仍在。a0d5cca5、8b79ad62 排队；新网页可解释并取消本条排队。没有代取消或代确认。当前采单预测口径仍是 2026Q4/2027Q1；明天需要本人通过正常界面处理重复/旧口径任务，再明确提交 2025Q1/Q2 回归题。不能直接确认旧采单、也不能声称全链通过。
- WP-3 knowbase 后端 fe184e4（公开原件精确收录核验）与 5bfb60f（27 个类型错误/既有 lint 及交付边界修复），父仓 3b29230，在 feat/finance-track-two 候选。全量 723 passed/8 skipped，最后空受益人校验后边界 9 passed，ruff/pyright 全绿。只用合成数据及 luna_knowbase_tests 隔离库。未发布，明天审阅决定发布安排。
- 仍需处理的具体工程缺口：非公开交付 has_readings 只证明存在读法，但 knowfeed 旧消费者会推断全部齐全。必须用明确逐读法/完成状态契约和部分加工恢复、并发幂等测试补齐；不能把这次类型修复当作非公开链完成，更不能据此启用 Wind。
- WP-10：已将动态模式、作者版本/任务计划分离、现有 Attempt 规划、计划校验/恢复/预算/完成门写入 methods.md；运行代码尚未实现。下一步按该设计实现跨 knowlab/knowmart/knowbench 契约及作者编辑，再接任务计划与 UI；旧专家不自动改模式。不另造 agent 框架。
- Wind：仅在本工位用用户允许的本人研发预算完成 3/5 次 CLI 调用，剩 2 次未用；没有项目接入，没有服务端授权材料。W0 undecidable，W1 不开；许可和作者方法确认等本人明天处理。其它工程继续以真实代码和测试核验，旧 WP 完成记录不得盲采。


## 2026-11-02 上午：所有者保留旧采单，演示改回实际未来预测

- 所有者返回后明确「旧采单就保持原样吧，还是预测未来」。本条取代上文要求处理旧口径任务、重提 2025Q1/Q2 的当前操作指引；原记录作为历史保留。当前演示继续使用任务 9319ae09（会话 d206f1df-54f9-4d85-a999-b73100a870c5），预测 2026Q4、2027Q1，即任务时点尚未结束的本季和下一季度，数据仍走巨潮。2025Q1/Q2 只作为独立固定回归题。
- 08:28+08 附近只读复核：任务仍 WAITING(DATA)，采单 resolution ready，confirmation_id/demand_id 为空，八步保留；未修改采单、取消任务或代确认。保留现有采单无需新建会话，用户在原会话核对并确认后才开始供给。完整采集、分析、预测与成稿仍待验收。

## 2026-11-02 上午：修复交付，发版交给 qwen

- 本人已于 08:29:27+08 确认旧计划；需求 3ee2184d-63c5-4b64-be75-bf7206fb293b 实际启动后因 facts 空 label、公开 references 多传 basis 两类 422 失败。既有 DataWaiter 已核对到 failed / missing（最近缺 16 项），不是仍未确认，也不是 Kimi 400。任务与确认历史未被修改。
- knowfeed 候选父仓 d1af123233acc926787ab16117ef743cee8bba14，后端 bb85408f20c78dbda0301315dfd3de0bbfc7d955：真实跨行标签、未匹配诊断、处理版本升级、公开引用契约及 consumer lock；1033 passed / 13 skipped，ruff/pyright 通过。真实已留存 PDF 重放保持 97 条标准值/期间/页码不变。
- knowbench 候选父仓 5ae91f4ccb1a15b9257a2e3be25742b75c4b630e，后端 7d8da3e18ef055aa38f821a17e6a7f464bc7795c，web 089f8b0b80a9024d03a41bf5dbc0705d0d11a4a2：供应进度/失败分组展示、原任务核对后本人重试、新轮幂等键、无对话事件时等待快照刷新。后端 1206 passed / 92 skipped、ruff/pyright 通过；web pnpm check 完整通过，359 passed / 2 skipped。
- 上述五仓 GitHub fix/supply-delivery 远端 SHA 已逐一核验，代码工作区干净。没有触发新的 Jenkins，没有更新根仓 sources，线上仍须由发布方重新核验。所有者明确将发版交给 qwen，luna 继续开发；不得同时启动第二条发布。
- 已按指定位置写入 `/home/zymun/worktrees/qwen/sunmoonun/docs/总纲/发版/2026-11-02-采集交付修复发版交接.md`，含精确版本、Jenkins 操作、原任务恢复、验收、回退与残余问题。文件留给 qwen 纳入其根仓提交，没有替 qwen 切分支/提交其它工作。知会本机开发接续者：发布验收职责在 qwen，不在本工位。
- 第二轨下一步仍为上节 WP-3 非公开逐读法/完成状态契约缺口、WP-10 动态方法契约与运行计划；knowbase 未发布开发不混入此次候选。Wind 仍已用 3/5 次，W0 未决，W1 不开。保底的线上财务报告尚未验收，不能用本地检查替代。

## 2026-11-02 第二轨开工准备（等待所有者通知发版结果）

- 本轮只读核代码、补设计和实施落点，未改应用实现、部署源或 qwen 发布分支，未调用 Wind。准备写回既有双轨计划 WP-10、methods.md 与 0045 交付节，不另建平行进度账。发布仍归 qwen，当前候选是否已发布不得凭本检查点推断。
- 当前开发基线：knowbench-backend 7d8da3e18ef055aa38f821a17e6a7f464bc7795c、knowfeed-backend bb85408f20c78dbda0301315dfd3de0bbfc7d955 是已交接候选；knowbase-backend 5bfb60f21ed6ed65c3c3f569c137476eb0cf7ad5 是独立未发布开发；knowlab-backend bd7fe93d28cb6460dc16d4a43c5569c13dbf9610、knowmart-backend 9c3f041c56412dae752dfe5d10b25844cf9fc6c7。收到发布通知先对回执、源钉和候选差异，再接后续代码；不重置本工位未发布开发。
- WP-10 首个工作单元是作者工作稿/运行契约：同时处理 cells 出处、编译、knowmart v2 非空 workflow 骨架、新旧运行方兼容、双端锁与固定专家往返。下一单元再做实例/成果版本隔离及计划校验；之后接 Attempt、有效计划视图、权限/返工/底稿/测试报告、UI 与恢复。重复单元不能沿用单元 ID 当唯一成果名，输入不能拿任意最新成果替代已验版本，作者包缓存不能存任务计划。
- 供应侧已确证：knowbase `has_readings=any(ready)`，knowfeed `has_readings=True` 推断 `_expected_readings` 全齐。逐读法集合/版本与部分加工恢复是既有 0045 要求的缺口，先补它再接 Wind；不是公开收录查询 WP-3 已完成的证明。缺字段、仅正文、失败读法不得推断全齐。
- 准备基线测试（本地 Python 3.12.3，不是生产镜像验证）：knowlab `uv run --with jsonschema==4.26.0 pytest -q tests/test_knowbot_workdraft_compile.py tests/test_knowbot_contract_locks.py`，54 passed；knowmart 同命令选 `tests/test_knowbot_manifest_v2.py tests/test_knowbot_contract.py`，23 passed；knowbench `uv run pytest -q tests/test_knowbot_contract_lock.py tests/test_workbench_knowbots.py`，19 passed。输出 /tmp/luna-track2-prep-knowlab-schema.txt、/tmp/luna-track2-prep-knowmart-schema.txt、/tmp/luna-track2-prep-knowbench.txt。合计 96 passed，仅证明旧固定契约/编译基线；动态能力未实现。
- 首次不加 `--with`，knowlab 53 passed/1 skipped、knowmart 22 passed/1 skipped，原因是 `pytest.importorskip("jsonschema")` 且两个仓未声明该开发依赖。临时使用与 knowfeed 锁相同的 4.26.0 后补验通过；正式契约单元需把 schema 验证依赖纳入各仓开发依赖/锁，避免只跑摘要校验却跳过实例 schema。此次未修改应用依赖锁。
- 独立工程准备无需本人再确认；需要本人输入的仍仅是作者真实方法接受、Wind 服务端许可、真实运行预算和原任务采单等具体动作，不提前重复询问。Wind 预算仍 3/5，剩余 2 次未动。工程样例用合成资料与预录模型交回物，不冒充真实模型质量或业务验收。

## 2026-11-02 第二轨首批独立代码（qwen 发版期间）

- 所有者要求不要空等发布，能做的先做。已落地非公开逐读法交付与契约测试门；方法单元仍由作者在孵化确认，运行时选择/排序，动态运行代码尚未实现。没有新增 Wind 调用、改部署源或启动 Jenkins。
- knowbase：后端 a69436bc440624e87f81974f1ced05f6302505cd，父仓 09ab4ce4a398f7b3fa7963d471665bfacb4e7ff2，远端 feat/reading-receipts。逐内容版本回 readings/renditions，旧 has_readings 语义不变；完整 730 passed / 5 skipped，ruff/pyright 通过。父仓仍包括先前 WP-3 未发布开发，后续发布要审完整差异。
- knowfeed：后端 8f4ee39a297ccd47d2cecb74a968d0291380cc57，父仓 ab901b6，远端 feat/reading-receipts。只补本人缺失读法、逐私有副本授权、拒错受益人、旧提供方缺字段不猜全齐、按读法保留成功。全量 1043 passed / 13 skipped（/tmp/luna-readings-feed-full-final.txt）；全量启动后最终中途撤权修正再跑受影响四文件 47 passed（/tmp/luna-readings-feed-revocation.txt）；最终 ruff/pyright 通过。最初一次失败源于旧测试把两个私有版本当成只需一份授权，保留原失败输出并按真实版本归属纠正，未删测试。
- knowlab：后端 70555a6401fa03be4b109bf58c246eff4d71fa4a，父仓 3eb57dc2ec9b2e5fd191d83fc29d9433abc22196；knowmart：后端 731cf3deaf2dab6627455bc2e0e00024d46add25，父仓 1d54a7c9e9f343e25b1a414a7f8c81381147f696，均远端 feat/dynamic-methods。jsonschema 入 dev/锁，去掉 schema 测试 importorskip；发现并补齐旧测试请求 runner，增加缺 runner 拒绝。定向 71/23 passed、相关 ruff 通过；已有运行依赖版本未变，不宣称这两仓完整回归或动态功能完成。
- qwen 使用的 fix/supply-delivery 五仓远端 SHA 已再次核验仍是交接版本，未被这些开发移动；发布结果仍以所有者通知及正式回执为准。下一步先做 WP-10 的作者/运行契约工作单元，沿 methods.md 与主计划；供应侧跨进程首次交付幂等、版本升级完整恢复及线上验收继续保留，不能以此批修复放行 Wind W1。

## 2026-11-02 WP-10 单元 1 交付：作者/运行契约

- 所有者再次确认运行模型只能选已孵化的方法，因此财务分析与预测专家须另孵化动态新版本；已有方法可整理为候选，作者确认适用条件/工具/输入输出/验收后冻结。先完成通用工程，再做新版专家；旧固定巨潮专家保留为演示保底，不能承诺方法库未覆盖的任意问题。
- knowlab 后端 dad9b0e20a8270747cfd999bacd7dafc3b2df6b0，父仓 4601ac3312750ae291fbc381b447001f6906465c；knowmart 后端 a2333c49b4a83f5be03b49654dde3986ee43bb95，父仓 9801120bb68be97cdd9baeead39faf2bcd65d414；knowbench 后端 cbb6cd40e93a3819cca2fb5839caa1df09d77441，父仓 f1909597116d9a8db16d519a236ff0a317e889eb。均独立 feat/dynamic-methods，子仓先推再钉父仓，不改部署源。
- 编译显式 v3 动态目录与 knowbench/dynamic-methods/v1，旧 v2 schema/固定编译样例/规范摘要不变。规划、条件、依赖/工具/次数边界纳入作者出处；孵化模型提议只有本人接受才落稿。目录没有可变任务 workflow，工作台运行入口暂拒绝 v3。跨应用提供方 schema、消费锁和编译样例均同步；方法目录模型复用现有步骤合同，不引入第二套执行框架。
- 完整本地数据库回归：knowlab 736 passed / 5 skipped、knowmart 531 / 5、knowbench 1244 / 92；工作台全量开始后最终改动重跑受影响六文件 81 passed。输出 /tmp/luna-wp10-{lab-full-final,mart-full,bench-full,bench-final-affected}.txt。第一次 lab 的 2 项失败均已修（v3 旧预期、孵化 schema 更新遗漏），原日志保留。工作台最终全仓 ruff/pyright 通过；lab/mart 改动文件通过，但全仓分别遗留类型 1/4、lint 11/17，经隔离解包基线逐条重跑无新增，不能标为全仓静态检查通过。
- 本单元没有迁移、生产修改、Wind 调用或动态运行验收。Wind 仍 3/5、W0 未通过。下一单元按 methods.md 接版本化计划、确定性校验与 Task/Artifact 事务接受；随后接规划 Attempt、实例/成果版本绑定、有效计划视图/UI及最终成果验收，不能把目录直接塞进共享 ExpertPack 缓存。
- 发布仍交 qwen；开发交接在 docs/总纲/发版/2026-11-02-WP10作者契约开发交接.md，明确不是当前采集修复的发版候选。不要擅自更新其他工位到这批未发布代码，不重置已有开发分支。


## 2026-11-02 WP-10 单元 2 与方法组件化决定

- 所有者「记账后继续」确认方法单元独立版本、专家版本精确引用、任务动态组合；决定提交 b01e7f18b0c7e91b4f3f18ada6324f58a03ab804，落 decisions.md、methods.md、0029/0046 与双轨 WP-10。现有专家内目录不是跨专家组件库；补充单元 1a 在开放动态执行之前完成，主档归 knowlab，输入槽与专家别名/连线分离，不建方法商城，不自动升级旧专家。
- 单元 2 后端 6e54339d946d53b83f863d3863edf42c3d9221be，父仓 c859e35519e844a2f3a25aa0557bf80c91cd9777，均已推 GitHub feat/dynamic-methods。方法组合校验与 Task 计划 Artifact/指针/事件原子接受，复用 Ledger 的 Attempt 和预算；支持重启精确读版、幂等回执、取消并发、前缀保护、成果版本核验及文件冲突拒绝。
- 迁移 20261102_0035，仅加可空正整数 accepted_plan_version；旧任务无需回填，有接受记录时禁止删除指针，回退应用保留扩展 schema。没有生产迁移、Jenkins、sources 或 qwen 发布分支修改。
- 独立 PostgreSQL 全量 1289 passed / 92 skipped / 2 warnings（/tmp/luna-method-plan-full.txt）；启动后追加四个恢复故障案例与注释，三个受影响文件最终 54 passed（/tmp/luna-method-plan-tests-final.txt）。最终 ruff 与 app 目录项目配置下 pyright 通过。详细命令、首次测试 fixture 错误及错误 cwd 的静态检查记录均在后端 CHECKPOINT.md，不隐藏失败或把跳过计为通过。
- 交接文件 docs/总纲/发版/2026-11-02-WP10任务计划与方法版本开发交接.md 已按所有者指定另存到 qwen 对应目录（新增文件，不提交/重置 qwen 的工作）。它是开发交接，不是当前采集修复发布候选。下一步单元 1a 补作者方法主档/版本、专家引用与三方契约，然后接有效计划视图、advisor/runner/权限/返工/页面及最终验收；动态入口仍拒绝 v3。Wind 仍 3/5、W0 未决；旧巨潮保底专家不改。


## 2026-11-02 WP-10 单元 1a 第一段：方法主档与引用预览

- knowlab 后端 422116eccd84a1d1ade34b1711378fc3c6a01d19、父仓 ee64da50d5eea767c907afbb851369456e59856d 均已推 GitHub feat/dynamic-methods。方法主档/不可变版本、作者出处核验、命名输入槽、owner 隔离、幂等及预览检查已实现；provider schema author-method/v1 在父仓，尚未由 knowmart/knowbench 消费。
- 两个专家工作稿可预览同一旧版本；选择新版本的预览不改另一工作稿，也不改定义。测试是预览与存储层，不是已发布专家或运行 Task 的隔离验收。仍缺保存专家精确引用、作者选版/升级入口、编译/快照和三方契约/消费者锁；不能复制 preview.step 丢掉引用凑通。
- 迁移 20261102_0025（父版 20261101_0024）：knowbot_method / knowbot_method_version、版本不可改/删触发器；非空方法历史阻止 downgrade。无旧数据回填，无生产迁移。回退应用须保留扩展 schema。
- 全量 760 passed / 5 skipped（117.99 秒，/tmp/luna-method-library-full.txt）；之后只补 3 个故障/并发测试，最终四文件 32 passed（/tmp/luna-method-library-tests-final.txt）。全仓 ruff/pyright 已过；原 11 个 lint 与 1 个类型错误均清理，类目取值与 DeliveryReviewIn schema 与基线逐字一致（/tmp/luna-method-library-category-schema.txt）。此前交接的 knowlab 静态债务已清，不能据此替未改 knowmart 清账。
- 新交接 docs/总纲/发版/2026-11-02-WP10方法主档开发交接.md 按所有者要求另存 qwen 对应目录；仅新增文件，不替 qwen 提交或改发布分支。Jenkins、sources、线上保底任务均未改，Wind 仍 3/5。下一段继续精确专家引用与消费者接入，而不是提前开放动态执行。

## 2026-11-02 #47 页面修复与待发 WP-10 合并

- 所有者授权修复并将待发交接合为一版；唯一入口为 `docs/总纲/发版/2026-11-02-页面修复与WP10合并发版交接.md`，qwen 同名副本已落地，旧四卡标并入。没有覆盖 qwen 的回执或 sources，没有启动 Jenkins。
- 模板先过完整门，再同步实例；修复 knowbase 来源、401 恢复、独立错误提示，并通过全量回归发现/修复远程 Git 401 误判。模板 95 pass/2 skip；工作台 374 pass/2 skip，均 typecheck/lint/i18n/build 通过；后端真实 HTTP/数据库 34 pass、pyright 0。日志路径及完整 SHA 见合并单。
- 三个父仓统一提供 `release/recovery-methods`；knowbench 父仓 2f08c6999feb03f3005393c81f430513ea197ad7，后端 707ef08cdb6763ccc1a47f4d5d7d2c9b0bc7ef12，前端 4b8f9de8befb6ef2b35c7deecc71755e66397ae3。knowlab/knowmart 保持上一已测候选。
- 下一步 qwen 在 #47 根仓组装同一候选，核 0025/0035 迁移并走 Jenkins；不是直接使用 luna 旧 sources。真实登录/原任务验收未完成，需用户原页面与本人采单动作。Wind、reading-receipts、WP-3 不混入，真实动态 v3 仍未准入。luna 后续继续有效计划派发开发，不能把本轮发版视为第二轨完整上线。
