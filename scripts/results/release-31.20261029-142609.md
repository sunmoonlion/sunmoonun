# release #31：AI请专家三条服务关系与knowlab跨应用链接 交Fable-gitops 2a 2b 单发

- 时间：2026-10-29T14:26:09+08:00；分支 fable；应用 knowbench, knowmart, knowlab；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/31/）
- 提交：deploy 33ae7500c39604273348465dc716263c697e320b；指针 79b7421de400c53a2c1e15f706a85e18fa0da7b1；tag release-20261029-2；批准：批准人 admin  2026-10-29T14:18:48+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
(no image lock changed: same pins rebuilt to the same digests)
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-backend/runtime/kustomization.yaml   |  3 +++
 .../knowbench-backend/runtime/workload.yaml        | 26 ++++++++++++++++++----
 .../knowlab-backend/runtime/workload.yaml          | 15 ++++++++++---
 .../knowmart-backend/runtime/workload.yaml         | 20 ++++++++++++++---
 4 files changed, 54 insertions(+), 10 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/kustomization.yaml
@@ -11,3 +11,6 @@ resources:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -31,6 +31,21 @@ data:
+  KNOWMART_CATALOG_SERVICE_APPLICATION: "sunmoonai-knowbench-knowmart-catalog"
+  KNOWMART_CATALOG_SERVICE_CLIENT_ID: "sunmoon-knowbench-knowmart-catalog"
+  KNOWMART_CATALOG_SERVICE_SCOPE: "knowmart:catalog"
+  KNOWMART_CATALOG_SERVICE_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  KNOWMART_CATALOG_SERVICE_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  KNOWMART_DEMAND_SERVICE_APPLICATION: "sunmoonai-knowbench-knowmart-demand"
+  KNOWMART_DEMAND_SERVICE_CLIENT_ID: "sunmoon-knowbench-knowmart-demand"
+  KNOWMART_DEMAND_SERVICE_SCOPE: "knowmart:demand"
+  KNOWMART_DEMAND_SERVICE_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  KNOWMART_DEMAND_SERVICE_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  KNOWLAB_INCUBATION_REQUEST_SERVICE_APPLICATION: "sunmoonai-knowbench-knowlab-incubation-request"
+  KNOWLAB_INCUBATION_REQUEST_SERVICE_CLIENT_ID: "sunmoon-knowbench-knowlab-incubation-request"
+  KNOWLAB_INCUBATION_REQUEST_SERVICE_SCOPE: "knowlab:incubation-request"
+  KNOWLAB_INCUBATION_REQUEST_SERVICE_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  KNOWLAB_INCUBATION_REQUEST_SERVICE_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
@@ -119,7 +134,7 @@ spec:
@@ -153,6 +168,9 @@ spec:
+            - {secretRef: {name: knowbench-knowmart-catalog-service}}
+            - {secretRef: {name: knowbench-knowmart-demand-service}}
+            - {secretRef: {name: knowbench-knowlab-incubation-request-service}}
@@ -189,7 +207,7 @@ spec:
@@ -251,7 +269,7 @@ spec:
@@ -308,7 +326,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/runtime/workload.yaml
@@ -70,6 +70,13 @@ data:
+  SERVICE_AUTH_INCUBATION_REQUEST_CALLERS: "knowbench"
+  SERVICE_AUTH_INCUBATION_REQUEST_KNOWBENCH_CASDOOR_APPLICATION: "sunmoonai-knowbench-knowlab-incubation-request"
+  SERVICE_AUTH_INCUBATION_REQUEST_KNOWBENCH_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_INCUBATION_REQUEST_KNOWBENCH_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_INCUBATION_REQUEST_KNOWBENCH_AUDIENCE: "sunmoon-knowbench-knowlab-incubation-request"
+  SERVICE_AUTH_INCUBATION_REQUEST_KNOWBENCH_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowbench-knowlab-incubation-request"
+  SERVICE_AUTH_INCUBATION_REQUEST_KNOWBENCH_REQUIRED_SCOPE: "knowlab:incubation-request"
@@ -79,6 +86,8 @@ data:
+  CROSS_APP_TARGETS_JSON: "{\"knowbench\": {\"web_base_url\": \"https://knowbench.dev.sunmoonai.com:30443\"}}"
+  CROSS_APP_SOURCES_JSON: "{\"knowbench\": {\"return_url\": \"https://knowbench.dev.sunmoonai.com:30443/zh-CN/workbench?ref={ref}\"}, \"knowbase\": {}, \"knowfeed\": {}}"
@@ -114,7 +123,7 @@ spec:
@@ -187,7 +196,7 @@ spec:
@@ -254,7 +263,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/runtime/workload.yaml
@@ -21,6 +21,13 @@ data:
+  SERVICE_AUTH_CATALOG_CALLERS: "knowbench"
+  SERVICE_AUTH_CATALOG_KNOWBENCH_CASDOOR_APPLICATION: "sunmoonai-knowbench-knowmart-catalog"
+  SERVICE_AUTH_CATALOG_KNOWBENCH_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_CATALOG_KNOWBENCH_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_CATALOG_KNOWBENCH_AUDIENCE: "sunmoon-knowbench-knowmart-catalog"
+  SERVICE_AUTH_CATALOG_KNOWBENCH_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowbench-knowmart-catalog"
+  SERVICE_AUTH_CATALOG_KNOWBENCH_REQUIRED_SCOPE: "knowmart:catalog"
@@ -28,6 +35,13 @@ data:
+  SERVICE_AUTH_DEMAND_CALLERS: "knowbench"
+  SERVICE_AUTH_DEMAND_KNOWBENCH_CASDOOR_APPLICATION: "sunmoonai-knowbench-knowmart-demand"
+  SERVICE_AUTH_DEMAND_KNOWBENCH_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_DEMAND_KNOWBENCH_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_DEMAND_KNOWBENCH_AUDIENCE: "sunmoon-knowbench-knowmart-demand"
+  SERVICE_AUTH_DEMAND_KNOWBENCH_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowbench-knowmart-demand"
+  SERVICE_AUTH_DEMAND_KNOWBENCH_REQUIRED_SCOPE: "knowmart:demand"
@@ -72,7 +86,7 @@ spec:
@@ -134,7 +148,7 @@ spec:
@@ -192,7 +206,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:f90acd9ab2492202bbafb9d33538971e7ac9e6bf32a617fb3a399a810dc040f5
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 33ae7500c39604273348465dc716263c697e320b
pointer-commit 79b7421de400c53a2c1e15f706a85e18fa0da7b1
tag release-20261029-2
```

## 部署（10-apply.log 尾部、10-wait.txt）

```text

TASK [Require current generation Ready with the exact promoted digest] *********
ok: [localhost] => (item=ocirepository)
ok: [localhost] => (item=kustomization)

TASK [Require digest selection and reconciliation revision to agree] ***********
ok: [localhost]

TASK [Verify the actual declared platform release marker] **********************
ok: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=38   changed=3    unreachable=0    failed=0    skipped=28   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
kustomization.kustomize.toolkit.fluxcd.io/knowbench-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-agent-releases condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowbase-user-data-output-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowbase-user-data-read-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowfeed-supply-demand-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowlab-incubation-request-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowlab-read-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowmart-catalog-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowmart-demand-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowmart-summon-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-platform-computer condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-service-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-web condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-knowbase-user-data-purchase-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-web condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-directory-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-grant-test-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-import-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-output-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-read-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbench-incubate-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbench-testrun-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowfeed-supply-demand-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowmart-deliver-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-web condition met
```

## 检查（11-check-*.log 尾部）

### 11-check-knowbench.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=50   changed=0    unreachable=0    failed=0    skipped=24   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

### 11-check-knowlab.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=50   changed=0    unreachable=0    failed=0    skipped=24   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

### 11-check-knowmart.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-31 推送成功后可删。
