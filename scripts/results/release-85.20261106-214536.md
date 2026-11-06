# release #85：qwen-018 修正0039迁移声明后重跑

- 时间：2026-11-06T21:45:37+08:00；分支 qwen；目标 knowbase, knowfeed, knowbench, knowlab；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/85/）
- 提交：deploy 6778c4c82118b655df83d72a8690258d49cdcc17；指针 e4e3cfda4128ad010746b75f160386d878c94797；tag release-20261106-1；批准：批准人 admin  2026-11-06T21:35:14+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index c7a59dd6..2822d5c5 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -14,36 +14,36 @@ applications:
     admin_parent_revision: 722c6b80e849d6352f28abbdd7362e1151191c14
     admin_revision: 722c6b80e849d6352f28abbdd7362e1151191c14
   knowfeed:
-    parent_revision: c81bee9f94da2eebf1cd8cf9bde63ff9cd3906dd
-    backend_parent_revision: 15606aaf039fb39dfa81b4489760a94c9eae4f8e
-    backend_revision: 15606aaf039fb39dfa81b4489760a94c9eae4f8e
+    parent_revision: 67638eb94e49a0a614704600b74b096fdcbba44a
+    backend_parent_revision: 4b5d9ac32e9bf00a2ed24b6c16cbbe5a260badcb
+    backend_revision: 4b5d9ac32e9bf00a2ed24b6c16cbbe5a260badcb
     web_parent_revision: bb03f1ac21ffea0bc4e71dd5efc678256dd354ab
     web_revision: bb03f1ac21ffea0bc4e71dd5efc678256dd354ab
     admin_parent_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
     admin_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
   knowbase:
-    parent_revision: a48d278e0994bdeff51f6597d09603f452c77ced
-    backend_parent_revision: e6822640e15aa6bebf49c9a7d57b54da45666de5
-    backend_revision: e6822640e15aa6bebf49c9a7d57b54da45666de5
+    parent_revision: cb1cb10a72e196cc949f0be4be4bbd336151ef73
+    backend_parent_revision: bf59f85d0bf619766f8a663d7965e2c57306acf2
+    backend_revision: bf59f85d0bf619766f8a663d7965e2c57306acf2
     web_parent_revision: be6d29ed6f054304aa0f38d53831f5f7fa238fa2
     web_revision: be6d29ed6f054304aa0f38d53831f5f7fa238fa2
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: f973f237a78bf2362860e82a9652c8c8d341c205
-    backend_parent_revision: 6c4a6844b52916d7a1f5e47e971daa0c3ab8f3b1
-    backend_revision: 6c4a6844b52916d7a1f5e47e971daa0c3ab8f3b1
-    web_parent_revision: 8cd235b6f7f8b18a0a619be94c15a2e7cc9ead6e
-    web_revision: 8cd235b6f7f8b18a0a619be94c15a2e7cc9ead6e
+    parent_revision: 6049c865f668936630be06397a32eaca8b31bd78
+    backend_parent_revision: c7d3d14dbd29177cdd85da59a54025b9b57d3276
+    backend_revision: c7d3d14dbd29177cdd85da59a54025b9b57d3276
+    web_parent_revision: 7026bfea6ad31580488f8e0e231c9a649477f2c7
+    web_revision: 7026bfea6ad31580488f8e0e231c9a649477f2c7
     admin_parent_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
     admin_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: af1b021bea760a2a17956d7ec428e874745d8e5a
-    backend_parent_revision: b86eedfc547bb28bda3c2cd8639189c17a61f6ce
-    backend_revision: b86eedfc547bb28bda3c2cd8639189c17a61f6ce
-    web_parent_revision: 61fdc470d1bd6cf7033ca084925e59f8338828ff
-    web_revision: 61fdc470d1bd6cf7033ca084925e59f8338828ff
+    parent_revision: 43d2192ff48477e26431913b80ea300dbcc3b4c5
+    backend_parent_revision: 614da0abf9b66eb6daacf3ecacccf3f6761a1a10
+    backend_revision: 614da0abf9b66eb6daacf3ecacccf3f6761a1a10
+    web_parent_revision: 25772149330a0ff8544e51edb98f1f376f21b75e
+    web_revision: 25772149330a0ff8544e51edb98f1f376f21b75e
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
     admin_revision: 89fe3ac1f6178018186584db7542f11102896381
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:351d15ae5c1ab968c07444ac18f898a58ef13958b030063f07060de29d8c278d source_revision: bf59f85d0bf619766f8a663d7965e2c57306acf2 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:da0a1a48a333b0db34d4124ddb8fed2f7a409f666f6a91e8e420fe303063ebb3 source_revision: c7d3d14dbd29177cdd85da59a54025b9b57d3276 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:449ebb581542a94ac48f1692feadf1dc54d84fe061a380c0d6d6f374eb7028bb source_revision: 7026bfea6ad31580488f8e0e231c9a649477f2c7 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:53e9f3924a0c6ce6d17da8691d21b4c0257fe5c33b6f3ca0209a3b658280a5f1 source_revision: 4b5d9ac32e9bf00a2ed24b6c16cbbe5a260badcb 
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:4783493e4915d27e0ce2d3c21f344ee5067fab33abd0179bff7eab04888e2f1a source_revision: 89fe3ac1f6178018186584db7542f11102896381 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:29c65565fd70296ba8c921c71600cd6a8ddd7c7e2fc6fb1d49706cce5d58b59a source_revision: 614da0abf9b66eb6daacf3ecacccf3f6761a1a10 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:328046b690182f34d32214f2455a55703b9321802ba23b699f1b36bc92c94c83 source_revision: 25772149330a0ff8544e51edb98f1f376f21b75e 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-backend/identity/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/image.lock.yaml      |  6 +++---
 .../knowbase-backend/migration/workload.yaml           |  6 +++---
 .../knowbase-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/redis/workload.yaml  |  4 ++--
 .../knowbase-backend/runtime/workload.yaml             |  8 ++++----
 .../knowbench-backend/identity/workload.yaml           |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml    |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml   |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml     |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml      |  4 ++--
 .../knowlab-incubation-request-identity/workload.yaml  |  4 ++--
 .../knowmart-catalog-identity/workload.yaml            |  4 ++--
 .../knowmart-demand-identity/workload.yaml             |  4 ++--
 .../knowmart-summon-identity/workload.yaml             |  4 ++--
 .../knowbench-backend/migration/workload.yaml          |  8 ++++----
 .../knowbench-backend/rabbitmq/workload.yaml           |  4 ++--
 .../knowbench-backend/redis/workload.yaml              |  4 ++--
 .../knowbench-backend/runtime/workload.yaml            | 18 +++++++++---------
 .../knowbench-backend/service-identity/workload.yaml   |  4 ++--
 .../knowbench-web-frontend/image.lock.yaml             |  6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml |  4 ++--
 .../knowfeed-backend/identity/workload.yaml            |  4 ++--
 .../knowfeed-app/knowfeed-backend/image.lock.yaml      |  6 +++---
 .../knowbase-user-data-supply-identity/workload.yaml   |  4 ++--
 .../knowfeed-backend/migration/workload.yaml           |  6 +++---
 .../knowfeed-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowfeed-app/knowfeed-backend/redis/workload.yaml  |  4 ++--
 .../knowfeed-backend/runtime/workload.yaml             |  8 ++++----
 .../knowfeed-backend/service-identity/workload.yaml    |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/image.lock.yaml |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/workload.yaml   |  4 ++--
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
 .../knowlab-app/knowlab-backend/runtime/workload.yaml  | 16 ++++++++--------
 .../knowlab-app/knowlab-web-frontend/image.lock.yaml   |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml     |  4 ++--
 48 files changed, 124 insertions(+), 124 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'e6822640e15aa6bebf49c9a7d57b54da45666de5'}
+            - {name: DEPLOYMENT_ID, value: 'bf59f85d0bf619766f8a663d7965e2c57306acf2'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-4c755636ef9debd8"
+  DEPLOYMENT_ID: "knowbase-backend-351d15ae5c1ab968"
@@ -149,7 +149,7 @@ spec:
@@ -218,7 +218,7 @@ spec:
@@ -281,7 +281,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
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
@@ -58,7 +58,7 @@ data:
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '6c4a6844b52916d7a1f5e47e971daa0c3ab8f3b1'}
+            - {name: DEPLOYMENT_ID, value: 'c7d3d14dbd29177cdd85da59a54025b9b57d3276'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261104_0038'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261106_0039'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-d9219f35634742d0"
+  DEPLOYMENT_ID: "knowbench-backend-da0a1a48a333b0db"
@@ -126,7 +126,7 @@ spec:
@@ -136,7 +136,7 @@ spec:
@@ -198,7 +198,7 @@ spec:
@@ -208,7 +208,7 @@ spec:
@@ -259,7 +259,7 @@ spec:
@@ -269,7 +269,7 @@ spec:
@@ -316,7 +316,7 @@ spec:
@@ -326,7 +326,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:c26e5e5bf6ebc1650f6bb6a0c7707f2ff67d2e0a3c26979e7d4b756d86ffb139
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 6778c4c82118b655df83d72a8690258d49cdcc17
pointer-commit e4e3cfda4128ad010746b75f160386d878c94797
tag release-20261106-1
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
kustomization.kustomize.toolkit.fluxcd.io/knowbase-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-provider condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-web condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-knowbase-user-data-supply-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-service-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-web condition met
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

### 11-check-knowfeed.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=54   changed=0    unreachable=0    failed=0    skipped=20   rescued=0    ignored=0   

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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-85 推送成功后可删。
