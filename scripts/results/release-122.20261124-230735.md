# release #122：KnowBench后端三次补发收紧匹配交付承诺与规划输入来源，沿用当前Web与库版本

- 时间：2026-11-24T23:07:35+08:00；分支 method-entry-release-20261124；目标 knowbench；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/122/）
- 提交：deploy 4411a9b17c4b58016a4e6069328f53c2468510e7；指针 7ee45ca5088140379bc751c9bf25eadacff73232；tag release-20261124-8；批准：批准人 admin  2026-11-24T23:02:12+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 8ae2593b1..0759febc9 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -30,9 +30,9 @@ applications:
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: 370d07bd7b31e973f50fbdcefa5d706e815816bb
-    backend_parent_revision: d26859c66772b3fcff42fea96a9b996c4b2591cd
-    backend_revision: d26859c66772b3fcff42fea96a9b996c4b2591cd
+    parent_revision: c14eca8ae07b8c6ebc92afb1a2cc2dca23a5b82e
+    backend_parent_revision: 644ca9be97de7825e7b0c01f1d869b6155b50e76
+    backend_revision: 644ca9be97de7825e7b0c01f1d869b6155b50e76
     web_parent_revision: 56a5f7ded75465583dac0262d4b7febae9ee59c7
     web_revision: 56a5f7ded75465583dac0262d4b7febae9ee59c7
     admin_parent_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:f4c409e506d43947ed7f1cdbd84816c51d31ff6801d9d0d752cc02eeb9d1d614 source_revision: 644ca9be97de7825e7b0c01f1d869b6155b50e76 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-app/knowbench-backend/identity/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml            |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml           |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml             |  4 ++--
 .../knowbench-function-publish-identity/workload.yaml          |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml              |  4 ++--
 .../knowlab-incubation-request-identity/workload.yaml          |  4 ++--
 .../knowbench-backend/knowmart-catalog-identity/workload.yaml  |  4 ++--
 .../knowbench-backend/knowmart-demand-identity/workload.yaml   |  4 ++--
 .../knowbench-backend/knowmart-summon-identity/workload.yaml   |  4 ++--
 .../knowbench-app/knowbench-backend/migration/workload.yaml    |  6 +++---
 .../knowbench-app/knowbench-backend/rabbitmq/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/redis/workload.yaml        |  4 ++--
 .../knowbench-app/knowbench-backend/runtime/workload.yaml      | 10 +++++-----
 .../knowbench-backend/service-identity/workload.yaml           |  4 ++--
 15 files changed, 35 insertions(+), 35 deletions(-)
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
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowbench-function-publish-identity/workload.yaml
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
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'd26859c66772b3fcff42fea96a9b996c4b2591cd'}
+            - {name: DEPLOYMENT_ID, value: '644ca9be97de7825e7b0c01f1d869b6155b50e76'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-578b1de581361011"
+  DEPLOYMENT_ID: "knowbench-backend-f4c409e506d43947"
@@ -165,7 +165,7 @@ spec:
@@ -237,7 +237,7 @@ spec:
@@ -298,7 +298,7 @@ spec:
@@ -355,7 +355,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:df59766469b632d3a9eb53531b6c536d1f6af37f81db61006f92d314a7ce28b9
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 4411a9b17c4b58016a4e6069328f53c2468510e7
pointer-commit 7ee45ca5088140379bc751c9bf25eadacff73232
tag release-20261124-8
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
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowbench-function-publish-identity condition met
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-122 推送成功后可删。
