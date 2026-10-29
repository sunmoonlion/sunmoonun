# 数据第四版 gitops 第 2a、2b 节单发回执（release #31，2026-10-29）

执行人 Fable，在本地工位经反向隧道操作；所有者定「单发」（只发新增配置，不带 qwen 代码）。

## 发了什么

| 提交 | 内容 |
| --- | --- |
| eac18b59 | knowbench `service_clients` 加 knowmart:catalog、knowmart:demand、knowlab:incubation-request（只挂 api）；knowmart、knowlab `service_receivers` 加 caller=knowbench；knowlab `cross_app_enabled: true`；domain/prepare.yaml 里 knowlab 去 knowbench；三个身份目录 README；stage.yaml 阶段与 runtime 依赖 |
| 63dd00ef | `topology-stage OBJECT=all`：阶段图加三个身份阶段（release 任务不生成阶段图） |
| 33ae7500 / 79b7421d / af410a7e | 流水线：deploy、晋级、回执 `release-31.20261029-142609.md` |

发前在本地用 render-check 同一条命令（`components-render`）渲了三个应用候选逐行核过；发后 Jenkins render-check #838（af410a7e）SUCCESS。

## 发后核对（app-platform-dev）

- Flux 阶段 `knowbench-knowmart-catalog-identity`、`knowbench-knowmart-demand-identity`、`knowbench-knowlab-incubation-request-identity`、三个 runtime 都 Ready，同一修订。
- 三个 identity Job Complete 1/1；Secret 六个（`-service`、`-provision` 各三）。
- 十个后端 Pod（knowbench 4、knowmart 3、knowlab 3）全部 Ready、重启 0，都是 14:21 滚动后的新 Pod。
- knowbench api：三组 `*_SERVICE_{APPLICATION,CLIENT_ID,CLIENT_SECRET,SCOPE,DISCOVERY_URL,BACKCHANNEL_ENDPOINT}` 齐全，SCOPE 分别 `knowmart:catalog`、`knowmart:demand`、`knowlab:incubation-request`；`KNOWMART_INTERNAL_URL`、`KNOWLAB_INTERNAL_URL` 原样。
- knowmart api：`SERVICE_AUTH_CATALOG_CALLERS`、`SERVICE_AUTH_DEMAND_CALLERS` = knowbench；knowlab api：`SERVICE_AUTH_INCUBATION_REQUEST_CALLERS` = knowbench，`CROSS_APP_TARGETS_JSON` 含 knowbench。
- 现网代码不读这些变量、没有新链接（knowbench 子模块 ce8e3b0、knowlab 网页端 3a0f2c8 里都没有），所以用户看不到任何变化；qwen 那批代码上线后才起作用。

## 没做、留着的

- 删除类仍在本地分支 `fable-v4-deletions`（头 2f5bbd7c，基于 eac18b59；迁移头 knowlab 20261029_0021、knowbench 20261029_0032、knowmart 0011、knowbase 0018、knowfeed 0019），等第四轮评审修完、qwen 五仓合进 fable 后再发；那次还要手工 stage provisioner 与 traefik、`topology-stage OBJECT=all`，并先删 Flux Kustomization（Orphan）再删对象。
- 这次没有要手工清的对象。
