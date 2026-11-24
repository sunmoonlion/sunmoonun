# release #117：发布 KnowLab 选型目录能力修复，只更新后端

- 时间：2026-11-24T10:47:25+08:00；分支 m02-catalog-fix-20261124；目标 knowlab；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/117/）
- 提交：deploy 9e6515a823bbbe444f1b1493d78510fb016e5d25；指针 3c47619850d2f89916b16626f88a7363dc4e7ba0；tag release-20261124-2；批准：批准人 admin  2026-11-24T10:43:09+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index da63bd021..f698f6cb6 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -39,9 +39,9 @@ applications:
     admin_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 08bebfcee46e3be61981fe50005f818294373678
-    backend_parent_revision: 468cee92956c7654cffea3b9fdc1ab6197d6fe1d
-    backend_revision: 468cee92956c7654cffea3b9fdc1ab6197d6fe1d
+    parent_revision: a46c632b98fd12b42649b9ec234a6d8410f0a3cc
+    backend_parent_revision: 4bb3f279c768e0f6b9182dfc6caf06929b24050d
+    backend_revision: 4bb3f279c768e0f6b9182dfc6caf06929b24050d
     web_parent_revision: 9f65b6bbeccc8ed6c9c21ccf5df71942a0173019
     web_revision: 9f65b6bbeccc8ed6c9c21ccf5df71942a0173019
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:a0a41bca6c688b7201a95f649a0061b052287c8f656af8b1babb739bbe5728df source_revision: 4bb3f279c768e0f6b9182dfc6caf06929b24050d 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowlab-app/knowlab-backend/identity/workload.yaml            | 4 ++--
 .../app-platform/knowlab-app/knowlab-backend/image.lock.yaml      | 6 +++---
 .../knowbase-user-data-directory-identity/workload.yaml           | 4 ++--
 .../knowbase-user-data-grant-test-identity/workload.yaml          | 4 ++--
 .../knowbase-user-data-output-identity/workload.yaml              | 4 ++--
 .../knowbase-user-data-read-identity/workload.yaml                | 4 ++--
 .../knowlab-backend/knowbench-incubate-identity/workload.yaml     | 4 ++--
 .../knowlab-backend/knowbench-testrun-identity/workload.yaml      | 4 ++--
 .../knowlab-backend/knowfeed-supply-demand-identity/workload.yaml | 4 ++--
 .../knowlab-backend/knowmart-deliver-identity/workload.yaml       | 4 ++--
 .../knowlab-app/knowlab-backend/migration/workload.yaml           | 6 +++---
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml            | 4 ++--
 .../app-platform/knowlab-app/knowlab-backend/redis/workload.yaml  | 4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml             | 8 ++++----
 14 files changed, 32 insertions(+), 32 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/identity/workload.yaml
@@ -298,7 +298,7 @@ spec:
@@ -312,7 +312,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbase-user-data-directory-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbase-user-data-grant-test-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbase-user-data-output-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbase-user-data-read-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbench-incubate-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbench-testrun-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowfeed-supply-demand-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowmart-deliver-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '468cee92956c7654cffea3b9fdc1ab6197d6fe1d'}
+            - {name: DEPLOYMENT_ID, value: '4bb3f279c768e0f6b9182dfc6caf06929b24050d'}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowlab-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowlab-backend-5620ca05788e88b9"
+  DEPLOYMENT_ID: "knowlab-backend-a0a41bca6c688b72"
@@ -113,7 +113,7 @@ spec:
@@ -181,7 +181,7 @@ spec:
@@ -244,7 +244,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:f1f890c58720c5a363edd4c4f23a264c116933e25097092436d36bbaf94bef8f
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 9e6515a823bbbe444f1b1493d78510fb016e5d25
pointer-commit 3c47619850d2f89916b16626f88a7363dc4e7ba0
tag release-20261124-2
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
kustomization.kustomize.toolkit.fluxcd.io/knowlab-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-directory-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-grant-test-identity condition met
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
kustomization.kustomize.toolkit.fluxcd.io/knowlab-web condition met
```

## 检查（11-check-*.log 尾部）

### 11-check-knowlab.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-117 推送成功后可删。
