# release #103：增量审查修复先发布 KnowMart 买方资格分页，库版本升到 0018

- 时间：2026-11-22T08:59:19+08:00；分支 review-release-20261122；目标 knowmart；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/103/）
- 提交：deploy b7aaac96665a977ebca2e770b406e3621acea029；指针 fc993563f81015e7abb258ab2b5babee86462d31；tag release-20261122-1；批准：批准人 admin  2026-11-22T08:47:48+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml: digest: sha256:0799a9cab79a252ff5f1f30a294c010ad47e8417f15c04be96d8ca08169128ec source_revision: 5f109118ffbaca623a732ed33eaea61a2905241a 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:52ac2932b03a71f61047d889b2aa78e500499a67da014b0c10c33256d3ba7ae1 source_revision: 7e07c84cda06c0ba4fd0030f16359d61b903a5fd 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:7b98f0222ff7ac252e528684cb0bbd6dc42f6baa31a2f40c5efc5cc23880b463 source_revision: 14515db89f249d76ea67f83b746fed030ccdf7f0 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowmart-app/knowmart-admin-frontend/image.lock.yaml   |  4 ++--
 .../knowmart-app/knowmart-admin-frontend/workload.yaml     |  4 ++--
 .../knowmart-app/knowmart-backend/identity/workload.yaml   |  4 ++--
 .../knowmart-app/knowmart-backend/image.lock.yaml          |  6 +++---
 .../knowbase-user-data-purchase-identity/workload.yaml     |  4 ++--
 .../knowmart-app/knowmart-backend/migration/workload.yaml  |  8 ++++----
 .../knowmart-app/knowmart-backend/rabbitmq/workload.yaml   |  4 ++--
 .../knowmart-app/knowmart-backend/redis/workload.yaml      |  4 ++--
 .../knowmart-app/knowmart-backend/runtime/workload.yaml    | 14 +++++++-------
 .../knowmart-app/knowmart-web-frontend/image.lock.yaml     |  4 ++--
 .../knowmart-app/knowmart-web-frontend/workload.yaml       |  4 ++--
 11 files changed, 30 insertions(+), 30 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowmart-admin-frontend-9f0c0a4b52549aca"}
+            - {name: DEPLOYMENT_ID, value: "knowmart-admin-frontend-0799a9cab79a252f"}
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/identity/workload.yaml
@@ -298,7 +298,7 @@ spec:
@@ -312,7 +312,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/knowbase-user-data-purchase-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'bacc888efd460b35ba5628d67a362a744370530d'}
+            - {name: DEPLOYMENT_ID, value: '7e07c84cda06c0ba4fd0030f16359d61b903a5fd'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261120_0017'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261122_0018'}
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowmart-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowmart-backend-c42bbb4ed36c05ae"
+  DEPLOYMENT_ID: "knowmart-backend-52ac2932b03a71f6"
@@ -86,7 +86,7 @@ spec:
@@ -96,7 +96,7 @@ spec:
@@ -148,7 +148,7 @@ spec:
@@ -158,7 +158,7 @@ spec:
@@ -206,7 +206,7 @@ spec:
@@ -216,7 +216,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowmart-app/knowmart-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowmart-web-frontend-bea512b3ab1bae69"}
+            - {name: DEPLOYMENT_ID, value: "knowmart-web-frontend-7b98f0222ff7ac25"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:1ac80486f8f9ee029a876a779693d22c811678e0e1b202302f94703f8797827b
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: b7aaac96665a977ebca2e770b406e3621acea029
pointer-commit fc993563f81015e7abb258ab2b5babee86462d31
tag release-20261122-1
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
kustomization.kustomize.toolkit.fluxcd.io/knowmart-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-knowbase-user-data-purchase-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-web condition met
```

## 检查（11-check-*.log 尾部）

### 11-check-knowmart.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-103 推送成功后可删。
