# knowfeed → knowbase 服务身份（user-data-supply）

凭加工依据向 knowbase 领授权、写回读法，受理前核确认（SDD 0043 第 2.7、3.3 节；SDD 0045）。入库那份身份只有 `knowbase:ingest` 一个 scope，所以另开这一条，代码按 `KNOWBASE_USER_DATA_SUPPLY_SERVICE_*` 与 `KNOWBASE_INTERNAL_URL` 读。配置是[后端config](../config.yaml)的 `service_clients` 里 target=knowbase、relation=user-data-supply 那一项，机制在[通用出站服务身份](../../../common/backend/service-client/README.md)。本目录的 `workload.yaml`、`provision.sops.yaml`、`kustomization.yaml` 由 stage 生成，不手改；生成前目录只有本说明（`stages.py` 要求阶段目录存在）。

在 Casdoor 里建独立组织 `sunmoon-workload-knowfeed-knowbase-user-data-supply` 与只有 client_credentials 的服务应用，scope `knowbase:user-data-supply`；私有输入 `service-client-knowbase-user-data-supply.yaml` 主备逐字节一致，丢了先恢复，不重新生成。knowbase 按自己的 `service_receivers` 从这里推出受众、主体与 scope 来校验令牌。

随数据第四版（交Fable-gitops 10-29）加入，先于 qwen 那批代码发布：旧代码不读这组变量，不受影响。
