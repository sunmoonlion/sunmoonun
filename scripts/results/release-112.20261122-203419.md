# release #112：补上指令回调入口并发布回炉与审查修复，全量入口和写回保持关闭

- 时间：2026-11-22T20:34:19+08:00；分支 callback-release-20261122；目标 knowbase, knowlab, knowbench, sandbox, traefik；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/112/）
- 提交：deploy 8f6a4e3e999e37a5e1385960e3541d2efabf9457；指针 6a30f1682c7e54cc6f2536dcfdc2c183851837a7；tag release-20261122-6；批准：批准人 admin  2026-11-22T20:24:29+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index ff3be2f71..fa33ab771 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -22,28 +22,28 @@ applications:
     admin_parent_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
     admin_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
   knowbase:
-    parent_revision: 6f041372c0dd922bf81f08a8caa70db435b61f7a
-    backend_parent_revision: 5563cc79fd3da76f3bf15707afb049707e11b714
-    backend_revision: 5563cc79fd3da76f3bf15707afb049707e11b714
+    parent_revision: 00b59ec8b5391fbf3fa54bfd9ebf4d7fc2a5e54a
+    backend_parent_revision: a30b375fc4850dacf163820290bf1454497ff8d2
+    backend_revision: a30b375fc4850dacf163820290bf1454497ff8d2
     web_parent_revision: 884d235418f63676a88002978bf99bd99112cdb1
     web_revision: 884d235418f63676a88002978bf99bd99112cdb1
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: 2a20aea1ee2ff018d2e21ad44641c6afbcca5165
-    backend_parent_revision: 60ea2f46a49e73528c14c3483f137e63c4395ad7
-    backend_revision: 60ea2f46a49e73528c14c3483f137e63c4395ad7
-    web_parent_revision: 65089bcbba7be4014fd599f65886c8373b5e43b8
-    web_revision: 65089bcbba7be4014fd599f65886c8373b5e43b8
+    parent_revision: af29b7238f38dd095e95de3129018b6d07df056f
+    backend_parent_revision: b16d9cd88ad9f7d33affdadf7f05cd8a735ba7e2
+    backend_revision: b16d9cd88ad9f7d33affdadf7f05cd8a735ba7e2
+    web_parent_revision: 0ba5de9512b3859148541e68f6a08430f471ab23
+    web_revision: 0ba5de9512b3859148541e68f6a08430f471ab23
     admin_parent_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
     admin_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 677af26c3c7b04e980d513df53a4af10316eae36
-    backend_parent_revision: 1d2e24290a9e84a369a043d97741c57215eb61be
-    backend_revision: 1d2e24290a9e84a369a043d97741c57215eb61be
-    web_parent_revision: 76c6bfd804ce4a5c5bf04a1435fc50c0e4601cf2
-    web_revision: 76c6bfd804ce4a5c5bf04a1435fc50c0e4601cf2
+    parent_revision: c2ed6b9a32b0c5d4549b06a3fcce73de7ce0bf03
+    backend_parent_revision: d7284751c499ec7b23fe1c71e0ce4c84b0f05371
+    backend_revision: d7284751c499ec7b23fe1c71e0ce4c84b0f05371
+    web_parent_revision: b125fc55e37d424c284eccef166c8ba45a47d1b6
+    web_revision: b125fc55e37d424c284eccef166c8ba45a47d1b6
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
     admin_revision: 89fe3ac1f6178018186584db7542f11102896381
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml: digest: sha256:e7affd1c995b55186280552373cdb666b803d86c1416c6d1ad079a41d55aab23 source_revision: f2f6df3163a01c71be13efdd20b87187b63693ec 
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:a178753154b3dec903a6e7358ccbaad4230214feab4d399b810b4735d77bd4bc source_revision: a30b375fc4850dacf163820290bf1454497ff8d2 
gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml: digest: sha256:8a6ecfe684ab5e71d31ef769ef01113dd38b9dfb6d9ac5de0aff718df0c71ec0 source_revision: 884d235418f63676a88002978bf99bd99112cdb1 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:bb987ae23916be1b0b47b98b330f0c2793b5fa02a1b961d929f4743e3a8348d9 source_revision: b16d9cd88ad9f7d33affdadf7f05cd8a735ba7e2 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:6222bca81db6db72e427555a37501b736fd9a024c83bf08f013cc69b0ca40f63 source_revision: 0ba5de9512b3859148541e68f6a08430f471ab23 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:d7b5ad72fb46c637d48000b977f832a1d4aa1e95a931581e46eaa1e4d455892d source_revision: d7284751c499ec7b23fe1c71e0ce4c84b0f05371 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:822d6ffc04ff104adbe973e30178404534e41a4290c2d3d23a4d5acf01801ff4 source_revision: b125fc55e37d424c284eccef166c8ba45a47d1b6 
gitops/components/sandbox-platform/provisioner/image.lock.yaml: digest: sha256:8ac9b946c447ce38165c395297ce832ecfe8fd87d7e9355e7a031d573fdf09e3 source_revision: 7798c101b9c82d5e7f5016fd3706688a4c9d8ca6 
gitops/components/sandbox-platform/sandbox/image.lock.yaml: digest: sha256:6f90cb180dcade90b2eff303a6617fb7398bf1f132f96bc463951d55f40d2289 source_revision: 7798c101b9c82d5e7f5016fd3706688a4c9d8ca6 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-admin-frontend/image.lock.yaml            |  4 ++--
 .../knowbase-app/knowbase-admin-frontend/workload.yaml |  4 ++--
 .../knowbase-backend/identity/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/image.lock.yaml      |  6 +++---
 .../knowbench-function-publish-identity/workload.yaml  |  4 ++--
 .../knowbase-backend/migration/workload.yaml           |  6 +++---
 .../knowbase-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/redis/workload.yaml  |  4 ++--
 .../knowbase-backend/runtime/workload.yaml             | 14 +++++++-------
 .../knowbase-app/knowbase-web-frontend/image.lock.yaml |  4 ++--
 .../knowbase-app/knowbase-web-frontend/workload.yaml   |  4 ++--
 .../knowbench-backend/identity/workload.yaml           |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml    |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml   |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml     |  4 ++--
 .../knowbench-function-publish-identity/workload.yaml  |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml      |  4 ++--
 .../knowlab-incubation-request-identity/workload.yaml  |  4 ++--
 .../knowmart-catalog-identity/workload.yaml            |  4 ++--
 .../knowmart-demand-identity/workload.yaml             |  4 ++--
 .../knowmart-summon-identity/workload.yaml             |  4 ++--
 .../knowbench-backend/migration/workload.yaml          | 12 ++++++------
 .../knowbench-backend/platform-computer/workload.yaml  |  4 ++--
 .../knowbench-backend/rabbitmq/workload.yaml           |  4 ++--
 .../knowbench-backend/redis/workload.yaml              |  4 ++--
 .../knowbench-backend/runtime/workload.yaml            | 18 +++++++++---------
 .../knowbench-backend/service-identity/workload.yaml   |  4 ++--
 .../knowbench-web-frontend/image.lock.yaml             |  6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml |  4 ++--
 .../knowlab-app/knowlab-backend/identity/workload.yaml |  4 ++--
 .../knowlab-app/knowlab-backend/image.lock.yaml        |  6 +++---
 .../workload.yaml                                      |  4 ++--
 .../workload.yaml                                      |  4 ++--
 .../knowbase-user-data-output-identity/workload.yaml   |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml     |  4 ++--
 .../knowbench-incubate-identity/workload.yaml          |  4 ++--
 .../knowbench-testrun-identity/workload.yaml           |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml      |  4 ++--
 .../knowmart-deliver-identity/workload.yaml            |  4 ++--
 .../knowlab-backend/migration/workload.yaml            |  6 +++---
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml |  4 ++--
 .../knowlab-app/knowlab-backend/redis/workload.yaml    |  4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml  |  8 ++++----
 .../knowlab-app/knowlab-web-frontend/image.lock.yaml   |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml     |  4 ++--
 .../traefik/service-access/workload.yaml               |  4 ++++
 .../sandbox-platform/provisioner/image.lock.yaml       |  6 +++---
 .../sandbox-platform/provisioner/workload.yaml         |  6 +++---
 .../sandbox-platform/sandbox/image.lock.yaml           |  6 +++---
 49 files changed, 128 insertions(+), 124 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-00e481c455d0a2c6"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-e7affd1c995b5518"}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -298,7 +298,7 @@ spec:
@@ -312,7 +312,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/knowbench-function-publish-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '5563cc79fd3da76f3bf15707afb049707e11b714'}
+            - {name: DEPLOYMENT_ID, value: 'a30b375fc4850dacf163820290bf1454497ff8d2'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-3f1e6f47c227f8e0"
+  DEPLOYMENT_ID: "knowbase-backend-a178753154b3dec9"
@@ -145,7 +145,7 @@ spec:
@@ -155,7 +155,7 @@ spec:
@@ -214,7 +214,7 @@ spec:
@@ -224,7 +224,7 @@ spec:
@@ -277,7 +277,7 @@ spec:
@@ -287,7 +287,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-04a7db3481cf18ba"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-8a6ecfe684ab5e71"}
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
-            - {name: DEPLOYMENT_ID, value: '60ea2f46a49e73528c14c3483f137e63c4395ad7'}
+            - {name: DEPLOYMENT_ID, value: 'b16d9cd88ad9f7d33affdadf7f05cd8a735ba7e2'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261122_0058'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261122_0059'}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:ba29bc4a5565f1f01340f27ca74fb11a898719f088548c6359ef420760ebfdcf
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 8f6a4e3e999e37a5e1385960e3541d2efabf9457
pointer-commit 6a30f1682c7e54cc6f2536dcfdc2c183851837a7
tag release-20261122-6
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
kustomization.kustomize.toolkit.fluxcd.io/knowbase-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-knowbench-function-publish-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-provider condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-web condition met
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

### 11-check-knowbase.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=57   changed=1    unreachable=0    failed=0    skipped=17   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

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

### 11-check-sandbox.log
```text
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=23   changed=1    unreachable=0    failed=0    skipped=77   rescued=0    ignored=0   

make[2]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make[1]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

### 11-check-traefik.log
```text
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=21   changed=1    unreachable=0    failed=0    skipped=79   rescued=0    ignored=0   

make[2]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make[1]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-112 推送成功后可删。
