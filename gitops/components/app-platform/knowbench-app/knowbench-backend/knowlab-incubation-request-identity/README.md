# knowbench → knowlab 服务身份（incubation-request）

用户点「孵化一个专家」后，工作台以他的名义到 knowlab 建「问题」申请（decisions 10-29「AI 请专家」，请专家方案设计第 4.9 节）。配置是[后端config](../config.yaml)的 `service_clients` 里 target=knowlab、relation=incubation-request 那一项，机制在[通用出站服务身份](../../../common/backend/service-client/README.md)。本目录的 `workload.yaml`、`provision.sops.yaml`、`kustomization.yaml` 由 stage 生成，不手改；生成前目录只有本说明（`stages.py` 要求阶段目录存在）。

在 Casdoor 里建独立组织 `sunmoon-workload-knowbench-knowlab-incubation-request` 与只有 client_credentials 的服务应用，scope `knowlab:incubation-request`；私有输入 `service-client-knowlab-incubation-request.yaml` 主备逐字节一致，丢了先恢复，不重新生成。knowlab 按自己的 `service_receivers` 从这里推出受众、主体与 scope 来校验令牌。只挂 knowbench 的 api 进程。

随交Fable-gitops 第 2a 节加（10-29）。
