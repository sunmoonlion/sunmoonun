# knowbase 函数发布身份

Cursor 发布时按本组件的 `service_clients` 声明生成身份和 SOPS 密文。独立发布进程使用 `knowbase-knowbench-function-publish-service` 中的凭据，以 `knowbench:function-publish` 向中心登记本服务的版本。常驻进程不挂载此凭据。[配置与准备机制](../../../common/backend/service-client/README.md)
