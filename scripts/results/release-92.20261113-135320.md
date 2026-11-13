# release #92：capability-entries-empty-home-verified

- 时间：2026-11-13T13:53:21+08:00；分支 capabilities-release-20261113；目标 knowbench；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/92/）
- 提交：deploy 3b50aa703678501fab13821b8d914208f6eda7c6；指针 563c33e9ab6f746262aea093da81e268809d23f6；tag release-20261113-1；批准：批准人 admin  2026-11-13T13:47:28+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:b4bf22d5ac66e624655009876e1b7728078e9e7e570a1a2999cfda333e8448b1 source_revision: a128987fed884906df5134fc9f45e9513cec0d04 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:bde4ecf4e7cd4d047b0dc20cf3f8e86844ea86b0aafe9a2720c9885e357706ff source_revision: af17aff5e9bcc252ef50d213cb6b5b05ca3e4031 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-backend/identity/workload.yaml         |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml  |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml   |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml    |  4 ++--
 .../workload.yaml                                    |  4 ++--
 .../knowmart-catalog-identity/workload.yaml          |  4 ++--
 .../knowmart-demand-identity/workload.yaml           |  4 ++--
 .../knowmart-summon-identity/workload.yaml           |  4 ++--
 .../knowbench-backend/migration/workload.yaml        | 12 ++++++------
 .../knowbench-backend/rabbitmq/workload.yaml         |  4 ++--
 .../knowbench-backend/redis/workload.yaml            |  4 ++--
 .../knowbench-backend/runtime/workload.yaml          | 20 +++++++++++---------
 .../knowbench-backend/service-identity/workload.yaml |  4 ++--
 .../knowbench-web-frontend/image.lock.yaml           |  6 +++---
 .../knowbench-web-frontend/workload.yaml             |  4 ++--
 16 files changed, 47 insertions(+), 45 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/identity/workload.yaml
@@ -451,7 +451,7 @@ spec:
@@ -465,7 +465,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowbase-user-data-output-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowbase-user-data-read-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowfeed-supply-demand-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowlab-incubation-request-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowmart-catalog-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowmart-demand-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowmart-summon-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/migration/workload.yaml
@@ -1,6 +1,6 @@
@@ -58,7 +58,7 @@ data:
@@ -72,22 +72,22 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '1d1fdda4e9d1134d6040abd5c26d0f0d64a36b3f'}
+            - {name: DEPLOYMENT_ID, value: 'a128987fed884906df5134fc9f45e9513cec0d04'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261106_0039'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261113_0040'}
-        - {name: verify, configMap: {name: 'knowbench-schema-check-v9'}}
+        - {name: verify, configMap: {name: 'knowbench-schema-check-v10'}}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-f6fe17d689a4dc32"
+  DEPLOYMENT_ID: "knowbench-backend-b4bf22d5ac66e624"
@@ -78,6 +78,8 @@ data:
+  WORKBENCH_CAPABILITY_MCP_URLS: "[]"
+  WORKBENCH_CAPABILITY_MCP_URL: "https://knowbench.dev.sunmoonai.com:30443/api/mcp/capabilities"
@@ -128,7 +130,7 @@ spec:
@@ -138,7 +140,7 @@ spec:
@@ -200,7 +202,7 @@ spec:
@@ -210,7 +212,7 @@ spec:
@@ -261,7 +263,7 @@ spec:
@@ -271,7 +273,7 @@ spec:
@@ -318,7 +320,7 @@ spec:
@@ -328,7 +330,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-1d18c18eee8e4721"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-bde4ecf4e7cd4d04"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:2f27e3f93dc10d22228a1973c25ffaf60873abd7fa3f05e366e4ebb86eee667c
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 3b50aa703678501fab13821b8d914208f6eda7c6
pointer-commit 563c33e9ab6f746262aea093da81e268809d23f6
tag release-20261113-1
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-92 推送成功后可删。
