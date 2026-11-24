# release #116：五项联合发布：模板选型编排、任务运行时0061与M02脚本报价

- 时间：2026-11-24T10:12:30+08:00；分支 m02-joint-release-20261124；目标 knowlab, knowbench；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/116/）
- 提交：deploy cb5d2890b76ea5e6baade88c6aa74d517abe57a8；指针 53a863335d675fecbeeb87e5378d01be3f3ba0de；tag release-20261124-1；批准：批准人 admin  2026-11-24T10:05:24+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 7dcc7e5ce..da63bd021 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -30,20 +30,20 @@ applications:
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: d455503701e422801b2427f23d3ecc74fbc265bb
-    backend_parent_revision: ced42af9db496922e90fc50837c6ef9af1a27586
-    backend_revision: ced42af9db496922e90fc50837c6ef9af1a27586
-    web_parent_revision: 5991d27261b22ba9837c29d2479816aaa9f6cfd6
-    web_revision: 5991d27261b22ba9837c29d2479816aaa9f6cfd6
+    parent_revision: e46959d92fb8793436fe2d7963de0f36ab5f0780
+    backend_parent_revision: 0eb40f0312e199d0c86c7b1d9d724ad655e913a7
+    backend_revision: 0eb40f0312e199d0c86c7b1d9d724ad655e913a7
+    web_parent_revision: b54f2baf7062624c75b8c9af2ec14c7d36519d52
+    web_revision: b54f2baf7062624c75b8c9af2ec14c7d36519d52
     admin_parent_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
     admin_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 3697473bf659fd0d35146ad89526aeed9c2c2dd6
-    backend_parent_revision: d7284751c499ec7b23fe1c71e0ce4c84b0f05371
-    backend_revision: d7284751c499ec7b23fe1c71e0ce4c84b0f05371
-    web_parent_revision: 583e6dfcb33a62e60f398f2cd1425aeb94d9f617
-    web_revision: 583e6dfcb33a62e60f398f2cd1425aeb94d9f617
+    parent_revision: 08bebfcee46e3be61981fe50005f818294373678
+    backend_parent_revision: 468cee92956c7654cffea3b9fdc1ab6197d6fe1d
+    backend_revision: 468cee92956c7654cffea3b9fdc1ab6197d6fe1d
+    web_parent_revision: 9f65b6bbeccc8ed6c9c21ccf5df71942a0173019
+    web_revision: 9f65b6bbeccc8ed6c9c21ccf5df71942a0173019
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
     admin_revision: 89fe3ac1f6178018186584db7542f11102896381
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:ee09225cd1ee720a698fb4685bcd7f49fce4630cfaff18bad819e34584746232 source_revision: 0eb40f0312e199d0c86c7b1d9d724ad655e913a7 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:d00a974e3e5ff677b385f65a9eb241c93d1c3045dd97a4e9377101b6a4ec82ad source_revision: b54f2baf7062624c75b8c9af2ec14c7d36519d52 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:5620ca05788e88b9681cf83b0675338df8de8ed8774b67aa8b5c4f394b286d71 source_revision: 468cee92956c7654cffea3b9fdc1ab6197d6fe1d 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:1b798e84ed4606b9d235d380634b264c7a2d44d42db8ff452604410f8f459433 source_revision: 9f65b6bbeccc8ed6c9c21ccf5df71942a0173019 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-backend/identity/workload.yaml        |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml |  6 +++---
 .../workload.yaml                                   |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml  |  4 ++--
 .../workload.yaml                                   |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml   |  4 ++--
 .../workload.yaml                                   |  4 ++--
 .../knowmart-catalog-identity/workload.yaml         |  4 ++--
 .../knowmart-demand-identity/workload.yaml          |  4 ++--
 .../knowmart-summon-identity/workload.yaml          |  4 ++--
 .../knowbench-backend/migration/workload.yaml       | 12 ++++++------
 .../knowbench-backend/rabbitmq/workload.yaml        |  4 ++--
 .../knowbench-backend/redis/workload.yaml           |  4 ++--
 .../knowbench-backend/runtime/workload.yaml         | 21 +++++++++++----------
 .../service-identity/workload.yaml                  |  4 ++--
 .../knowbench-web-frontend/image.lock.yaml          |  6 +++---
 .../knowbench-web-frontend/workload.yaml            |  4 ++--
 .../knowlab-backend/identity/workload.yaml          |  4 ++--
 .../knowlab-app/knowlab-backend/image.lock.yaml     |  6 +++---
 .../workload.yaml                                   |  4 ++--
 .../workload.yaml                                   |  4 ++--
 .../workload.yaml                                   |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml  |  4 ++--
 .../knowbench-incubate-identity/workload.yaml       |  4 ++--
 .../knowbench-testrun-identity/workload.yaml        |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml   |  4 ++--
 .../knowmart-deliver-identity/workload.yaml         |  4 ++--
 .../knowlab-backend/migration/workload.yaml         |  6 +++---
 .../knowlab-backend/rabbitmq/workload.yaml          |  4 ++--
 .../knowlab-app/knowlab-backend/redis/workload.yaml |  4 ++--
 .../knowlab-backend/runtime/workload.yaml           |  8 ++++----
 .../knowlab-web-frontend/image.lock.yaml            |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml  |  4 ++--
 33 files changed, 86 insertions(+), 85 deletions(-)
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
@@ -1,6 +1,6 @@
@@ -58,7 +58,7 @@ data:
@@ -72,22 +72,22 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'ced42af9db496922e90fc50837c6ef9af1a27586'}
+            - {name: DEPLOYMENT_ID, value: '0eb40f0312e199d0c86c7b1d9d724ad655e913a7'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261122_0060'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261123_0061'}
-        - {name: verify, configMap: {name: 'knowbench-schema-check-v14'}}
+        - {name: verify, configMap: {name: 'knowbench-schema-check-v15'}}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-074534fcc72fb003"
+  DEPLOYMENT_ID: "knowbench-backend-ee09225cd1ee720a"
@@ -119,7 +119,8 @@ data:
-  WORKBENCH_SKILL_SCRIPTS_ENABLED: "false"
+  WORKBENCH_SKILL_SCRIPTS_ENABLED: "true"
@@ -154,7 +155,7 @@ spec:
@@ -164,7 +165,7 @@ spec:
@@ -226,7 +227,7 @@ spec:
@@ -236,7 +237,7 @@ spec:
@@ -287,7 +288,7 @@ spec:
@@ -297,7 +298,7 @@ spec:
@@ -344,7 +345,7 @@ spec:
@@ -354,7 +355,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-44ac257bdec5127a"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-d00a974e3e5ff677"}
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
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:c5e08e3857216c76ab3075efd37e2c4a53e19edd8bfa2936b794b23fd253d482
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: cb5d2890b76ea5e6baade88c6aa74d517abe57a8
pointer-commit 53a863335d675fecbeeb87e5378d01be3f3ba0de
tag release-20261124-1
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

### 11-check-knowlab.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-116 推送成功后可删。
