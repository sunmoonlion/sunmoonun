# knowlab → knowbench 服务身份（incubate）

孵化栏「AI 起草」的一轮交 knowbench 跑（专家孵化方案第 8.2、十八节，契约 knowbot-incubation/v1），入口共用 `KNOWBENCH_INTERNAL_URL`，照 testrun 那一套。配置是[后端config](../config.yaml)的 `service_clients` 里 target=knowbench、relation=incubate 那一项，机制在[通用出站服务身份](../../../common/backend/service-client/README.md)。本目录的 `workload.yaml`、`provision.sops.yaml`、`kustomization.yaml` 由 stage 生成，不手改；生成前目录只有本说明（`stages.py` 要求阶段目录存在）。

在 Casdoor 里建独立组织 `sunmoon-workload-knowlab-knowbench-incubate` 与只有 client_credentials 的服务应用，scope `knowbench:incubate`；私有输入 `service-client-knowbench-incubate.yaml` 主备逐字节一致，丢了先恢复，不重新生成。knowbench 按自己的 `service_receivers` 从这里推出受众、主体与 scope 来校验令牌。

随数据第四版（交Fable-gitops 10-29）加入，先于 qwen 那批代码发布：旧代码不读这组变量，不受影响。
