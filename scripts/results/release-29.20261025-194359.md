# release #29：账 179：接入电脑页能移除没连着的电脑

- 时间：2026-10-25T19:43:59+08:00；分支 fable；应用 knowbench；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/29/）
- 提交：deploy d7b5c39b6693f82eafa1c0ae08915fad1826a459；指针 237ce6897cd73a4222268e4b2395a237884db923；tag release-20261025-8；批准：批准人 admin  2026-10-25T19:38:49+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 14facdee..df2c96f4 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -30,11 +30,11 @@ applications:
     admin_parent_revision: f097495080ef6ef7296beb0fcc9430b4079d8011
     admin_revision: f097495080ef6ef7296beb0fcc9430b4079d8011
   knowbench:
-    parent_revision: 436860216f3e3e3f33e9d372dbb51b541e1f873b
-    backend_parent_revision: 2ffdc12299cedcb4d39390fd40c2fd4a98a49ddd
-    backend_revision: 2ffdc12299cedcb4d39390fd40c2fd4a98a49ddd
-    web_parent_revision: 44d08cdc2f5562e9557f68bf85b4bb2719b2d3eb
-    web_revision: 44d08cdc2f5562e9557f68bf85b4bb2719b2d3eb
+    parent_revision: 1022e50100568252112acb472673c65bfe03cf7d
+    backend_parent_revision: ce8e3b013bd6fcd2bc7a6b8b77bb5e47036ddd8d
+    backend_revision: ce8e3b013bd6fcd2bc7a6b8b77bb5e47036ddd8d
+    web_parent_revision: 17cd09be9b83fec7483123a7f4969e2f44db6062
+    web_revision: 17cd09be9b83fec7483123a7f4969e2f44db6062
     admin_parent_revision: 26964553ed9d581ac855c38edeaee8e65add792f
     admin_revision: 26964553ed9d581ac855c38edeaee8e65add792f
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:73535ae04fe769815762b381e42143154841eee545e53ba1223f4a102e26d307 source_revision: ce8e3b013bd6fcd2bc7a6b8b77bb5e47036ddd8d 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:acd3e23980ebbd68d236e523e8f4743bed3dd1aa05ad6c4b9f4eba0f00e6f7f1 source_revision: 17cd09be9b83fec7483123a7f4969e2f44db6062 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-app/knowbench-backend/identity/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml            |  6 +++---
 .../knowbase-user-data-read-identity/workload.yaml             |  4 ++--
 .../knowbench-backend/knowlab-read-identity/workload.yaml      |  4 ++--
 .../knowbench-backend/knowmart-summon-identity/workload.yaml   |  4 ++--
 .../knowbench-app/knowbench-backend/migration/workload.yaml    |  6 +++---
 .../knowbench-app/knowbench-backend/rabbitmq/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/redis/workload.yaml        |  4 ++--
 .../knowbench-app/knowbench-backend/runtime/workload.yaml      | 10 +++++-----
 .../knowbench-backend/service-identity/workload.yaml           |  4 ++--
 .../knowbench-app/knowbench-web-frontend/image.lock.yaml       |  6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml         |  4 ++--
 12 files changed, 30 insertions(+), 30 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowbase-user-data-read-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowlab-read-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/knowmart-summon-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '2ffdc12299cedcb4d39390fd40c2fd4a98a49ddd'}
+            - {name: DEPLOYMENT_ID, value: 'ce8e3b013bd6fcd2bc7a6b8b77bb5e47036ddd8d'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-309d4b37e49c5115"
+  DEPLOYMENT_ID: "knowbench-backend-73535ae04fe76981"
@@ -110,7 +110,7 @@ spec:
@@ -178,7 +178,7 @@ spec:
@@ -238,7 +238,7 @@ spec:
@@ -295,7 +295,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-9c37e642b6b9a99c"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-acd3e23980ebbd68"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:a600f30161a6cc11393ad6f0e1cf53904fb85b9c341eb34146bef96aafb2d6ee
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: d7b5c39b6693f82eafa1c0ae08915fad1826a459
pointer-commit 237ce6897cd73a4222268e4b2395a237884db923
tag release-20261025-8
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
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowbase-user-data-read-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowlab-read-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowmart-summon-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-service-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-test-computer condition met
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-29 推送成功后可删。
