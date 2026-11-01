# release #39：发版前补齐计划与数据第四版全量交付及Link双平台0.5.5发布

- 时间：2026-11-01T19:02:52+08:00；分支 fable；应用 knowfeed, knowbase, knowbench, knowlab, knowmart；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/39/）
- 提交：deploy c4f64f03349df7148225430cf2506ba3746decd7；指针 5d17e1ba4018f70cb09d5bce157a1a889ed707e6；tag release-20261101-5；批准：批准人 admin  2026-11-01T18:51:28+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index df2c96f4..324d001f 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -14,44 +14,44 @@ applications:
     admin_parent_revision: 722c6b80e849d6352f28abbdd7362e1151191c14
     admin_revision: 722c6b80e849d6352f28abbdd7362e1151191c14
   knowfeed:
-    parent_revision: fc065ea073eb496d2b40260a4323056a5a2e9a48
-    backend_parent_revision: c4cd1d683abd8b275777f82fd19b2c7d096e84ff
-    backend_revision: c4cd1d683abd8b275777f82fd19b2c7d096e84ff
-    web_parent_revision: bca159f76befc47b1b38e7028c0f63c68b334759
-    web_revision: bca159f76befc47b1b38e7028c0f63c68b334759
-    admin_parent_revision: b344c106c4f44522770b8cca3e9a8121e0b3ce32
-    admin_revision: b344c106c4f44522770b8cca3e9a8121e0b3ce32
+    parent_revision: 317ffffba0afb982c8b4027b7aaf17ee878c505e
+    backend_parent_revision: b666d393ef2d23555f78f16ae39465415ceef916
+    backend_revision: b666d393ef2d23555f78f16ae39465415ceef916
+    web_parent_revision: bb03f1ac21ffea0bc4e71dd5efc678256dd354ab
+    web_revision: bb03f1ac21ffea0bc4e71dd5efc678256dd354ab
+    admin_parent_revision: d7af6017f16f2ea2ac2d8ba71876a4be64c7f11d
+    admin_revision: d7af6017f16f2ea2ac2d8ba71876a4be64c7f11d
   knowbase:
-    parent_revision: b16d7aa8c7ace36a3d84e873718c69a8e2d5f9ae
-    backend_parent_revision: eedb6d06a361dd229c505ca9b721d0a6b28da807
-    backend_revision: eedb6d06a361dd229c505ca9b721d0a6b28da807
-    web_parent_revision: 8c338db2b7222702f71cef892fd283016c148210
-    web_revision: 8c338db2b7222702f71cef892fd283016c148210
-    admin_parent_revision: f097495080ef6ef7296beb0fcc9430b4079d8011
-    admin_revision: f097495080ef6ef7296beb0fcc9430b4079d8011
+    parent_revision: 14e341a17a8add888d024df7fb75c00d72e63d0f
+    backend_parent_revision: fb88c4868a4245f934e59123506b9fe9c7087463
+    backend_revision: fb88c4868a4245f934e59123506b9fe9c7087463
+    web_parent_revision: be6d29ed6f054304aa0f38d53831f5f7fa238fa2
+    web_revision: be6d29ed6f054304aa0f38d53831f5f7fa238fa2
+    admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
+    admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: 1022e50100568252112acb472673c65bfe03cf7d
-    backend_parent_revision: ce8e3b013bd6fcd2bc7a6b8b77bb5e47036ddd8d
-    backend_revision: ce8e3b013bd6fcd2bc7a6b8b77bb5e47036ddd8d
-    web_parent_revision: 17cd09be9b83fec7483123a7f4969e2f44db6062
-    web_revision: 17cd09be9b83fec7483123a7f4969e2f44db6062
-    admin_parent_revision: 26964553ed9d581ac855c38edeaee8e65add792f
-    admin_revision: 26964553ed9d581ac855c38edeaee8e65add792f
+    parent_revision: f601d3668f5420ba78bfd072c7e898e60afee47a
+    backend_parent_revision: 849bcc862dc2e9fc9905917e736d73c3b9a7a08d
+    backend_revision: 849bcc862dc2e9fc9905917e736d73c3b9a7a08d
+    web_parent_revision: e538f00560464d922912770667bc65e008ddb052
+    web_revision: e538f00560464d922912770667bc65e008ddb052
+    admin_parent_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
+    admin_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: ce93fbc63e2ddea6b1c435f227ec3f8af6dfbe6a
-    backend_parent_revision: 8684d258b452e5b755de1a67b08884a5bdf29aa2
-    backend_revision: 8684d258b452e5b755de1a67b08884a5bdf29aa2
-    web_parent_revision: 3a0f2c847c220770d28177288023debc75172f19
-    web_revision: 3a0f2c847c220770d28177288023debc75172f19
-    admin_parent_revision: 28c79f0c38d4a01753dd92f403587470585f9ac3
-    admin_revision: 28c79f0c38d4a01753dd92f403587470585f9ac3
+    parent_revision: 0488b7e5992b52e6a684df7a89bc90e66deb0962
+    backend_parent_revision: bd7fe93d28cb6460dc16d4a43c5569c13dbf9610
+    backend_revision: bd7fe93d28cb6460dc16d4a43c5569c13dbf9610
+    web_parent_revision: 4334a198dc89d95b4c71ecc3165d9f965734a7e2
+    web_revision: 4334a198dc89d95b4c71ecc3165d9f965734a7e2
+    admin_parent_revision: fc8b4edc9144365248a7a96c58eaac5947fed111
+    admin_revision: fc8b4edc9144365248a7a96c58eaac5947fed111
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowmart:
-    parent_revision: 5e19a4cd28817d7db4069dc1a3b8ff4954c32939
-    backend_parent_revision: 884f0931efcd696dc1923c7cf9f1f341edf746be
-    backend_revision: 884f0931efcd696dc1923c7cf9f1f341edf746be
-    web_parent_revision: db315f20e6354ce9fdaee34b563a6d0a3ef2ef9e
-    web_revision: db315f20e6354ce9fdaee34b563a6d0a3ef2ef9e
-    admin_parent_revision: d14c3dc41293c660634a92aed2f1b14d46d5ef80
-    admin_revision: d14c3dc41293c660634a92aed2f1b14d46d5ef80
+    parent_revision: 255ae5024c83e7d7ad70acba698d173b3a1e0ccb
+    backend_parent_revision: 9c3f041c56412dae752dfe5d10b25844cf9fc6c7
+    backend_revision: 9c3f041c56412dae752dfe5d10b25844cf9fc6c7
+    web_parent_revision: 10b80aa56f31bb0f83270a2ae3dd46f1dccfcf12
+    web_revision: 10b80aa56f31bb0f83270a2ae3dd46f1dccfcf12
+    admin_parent_revision: 5f109118ffbaca623a732ed33eaea61a2905241a
+    admin_revision: 5f109118ffbaca623a732ed33eaea61a2905241a
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml: digest: sha256:a259d4515d2b4ba69086b5e2b38a7d4084ca20ab43ef50bdec534228ccd28437 source_revision: f2f6df3163a01c71be13efdd20b87187b63693ec 
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:4ff05034d1f80dcbf0a0bffd316f2f860e55eab58f62bb58f0cbc7fc6e8d22dc source_revision: fb88c4868a4245f934e59123506b9fe9c7087463 
gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml: digest: sha256:fcf501f37efdcf199d71100771bdfc87a1a60679ccb8014eb53a0f4b24e1b062 source_revision: be6d29ed6f054304aa0f38d53831f5f7fa238fa2 
gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml: digest: sha256:3141960938b789f71994f008c85310796e8f334f80cbaf8cc9f2b0d89fa97461 source_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:123d94d8a93b215d7cfe4371ff01436ed686a5b27d716a67d7de1e5ff1274f6b source_revision: 849bcc862dc2e9fc9905917e736d73c3b9a7a08d 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:7855e687c46814b724cae4404ab1737b37a9fedab3c8a6eabf6064219f7e2b8b source_revision: e538f00560464d922912770667bc65e008ddb052 
gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml: digest: sha256:87d0716d1658678b23f0a79591c107f156acad8ecf36b50e1910d5110b775f21 source_revision: d7af6017f16f2ea2ac2d8ba71876a4be64c7f11d 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:77932942a5419b4a0f517da65405caeba6f4aafe5738b577f90643cfaf44890f source_revision: b666d393ef2d23555f78f16ae39465415ceef916 
gitops/components/app-platform/knowfeed-app/knowfeed-web-frontend/image.lock.yaml: digest: sha256:e383c9e6ca5497aeef86490944aa9b8dc5b8c59e680865d3f8724a3c843ded20 source_revision: bb03f1ac21ffea0bc4e71dd5efc678256dd354ab 
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:bf60be5f6b6496d24f35fab2dbed5a5b95c58773963943b8989367be3c5955c1 source_revision: fc8b4edc9144365248a7a96c58eaac5947fed111 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:e78fdcd5d5b66203f68126f96190671abe35c9ee6a3e10e0a26169ff6fa1fa80 source_revision: bd7fe93d28cb6460dc16d4a43c5569c13dbf9610 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:d3af13e4489fbba340afe935e971cbaffc1dfa0b7e14303f9a84d07c56f30333 source_revision: 4334a198dc89d95b4c71ecc3165d9f965734a7e2 
gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml: digest: sha256:8c6dac7f8093c5ddc46da47546b2abbec89203c8939f5b1c863e22358238073c source_revision: 5f109118ffbaca623a732ed33eaea61a2905241a 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:118e5869d897694fa7bd90c372875e314af48fe7c14b1a968406abebef5b86c6 source_revision: 9c3f041c56412dae752dfe5d10b25844cf9fc6c7 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:af42ee99dd444fe2208863af8eab6517226827f90f202f10daebb9f164aab38c source_revision: 10b80aa56f31bb0f83270a2ae3dd46f1dccfcf12 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-admin-frontend/image.lock.yaml        |  6 +--
 .../knowbase-admin-frontend/workload.yaml          |  4 +-
 .../knowbase-backend/identity/workload.yaml        |  4 +-
 .../knowbase-app/knowbase-backend/image.lock.yaml  |  6 +--
 .../knowbase-backend/migration/workload.yaml       | 12 ++---
 .../knowbase-backend/provider/workload.yaml        | 10 ++---
 .../knowbase-backend/rabbitmq/workload.yaml        |  4 +-
 .../knowbase-backend/redis/workload.yaml           |  4 +-
 .../knowbase-backend/runtime/workload.yaml         | 30 ++++---------
 .../knowbase-web-frontend/image.lock.yaml          |  6 +--
 .../knowbase-web-frontend/workload.yaml            |  4 +-
 .../knowbench-admin-frontend/image.lock.yaml       |  6 +--
 .../knowbench-admin-frontend/workload.yaml         |  4 +-
 .../knowbench-backend/identity/workload.yaml       |  4 +-
 .../knowbench-backend/image.lock.yaml              |  6 +--
 .../workload.yaml                                  |  4 +-
 .../knowbase-user-data-read-identity/workload.yaml |  4 +-
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 +-
 .../workload.yaml                                  |  4 +-
 .../knowmart-catalog-identity/workload.yaml        |  4 +-
 .../knowmart-demand-identity/workload.yaml         |  4 +-
 .../knowmart-summon-identity/workload.yaml         |  4 +-
 .../knowbench-backend/migration/workload.yaml      | 12 ++---
 .../platform-computer/workload.yaml                | 12 ++---
 .../knowbench-backend/rabbitmq/workload.yaml       |  4 +-
 .../knowbench-backend/redis/workload.yaml          |  4 +-
 .../runtime/agent-releases.sops.yaml               | 22 ++++-----
 .../knowbench-backend/runtime/workload.yaml        | 29 ++++--------
 .../service-identity/workload.yaml                 |  4 +-
 .../knowbench-web-frontend/image.lock.yaml         |  6 +--
 .../knowbench-web-frontend/workload.yaml           |  4 +-
 .../knowfeed-admin-frontend/image.lock.yaml        |  6 +--
 .../knowfeed-admin-frontend/workload.yaml          |  4 +-
 .../knowfeed-backend/identity/workload.yaml        |  4 +-
 .../knowfeed-app/knowfeed-backend/image.lock.yaml  |  6 +--
 .../workload.yaml                                  |  4 +-
 .../knowfeed-backend/migration/workload.yaml       | 12 ++---
 .../knowfeed-backend/rabbitmq/workload.yaml        |  4 +-
 .../knowfeed-backend/redis/workload.yaml           |  4 +-
 .../knowfeed-backend/runtime/workload.yaml         | 15 +++----
 .../service-identity/workload.yaml                 |  4 +-
 .../knowfeed-web-frontend/image.lock.yaml          |  6 +--
 .../knowfeed-web-frontend/workload.yaml            |  4 +-
 .../knowlab-admin-frontend/image.lock.yaml         |  6 +--
 .../knowlab-admin-frontend/workload.yaml           |  4 +-
 .../knowlab-backend/identity/workload.yaml         |  4 +-
 .../knowlab-app/knowlab-backend/image.lock.yaml    |  6 +--
 .../workload.yaml                                  |  4 +-
 .../workload.yaml                                  |  4 +-
 .../workload.yaml                                  |  4 +-
 .../knowbase-user-data-read-identity/workload.yaml |  4 +-
 .../knowbench-incubate-identity/workload.yaml      |  4 +-
 .../knowbench-testrun-identity/workload.yaml       |  4 +-
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 +-
 .../knowmart-deliver-identity/workload.yaml        |  4 +-
 .../knowlab-backend/migration/workload.yaml        | 12 ++---
 .../knowlab-backend/rabbitmq/workload.yaml         |  4 +-
 .../knowlab-backend/redis/workload.yaml            |  4 +-
 .../knowlab-backend/runtime/workload.yaml          | 52 +++++-----------------
 .../knowlab-web-frontend/image.lock.yaml           |  6 +--
 .../knowlab-app/knowlab-web-frontend/workload.yaml |  4 +-
 .../knowmart-admin-frontend/image.lock.yaml        |  6 +--
 .../knowmart-admin-frontend/workload.yaml          |  4 +-
 .../knowmart-backend/identity/workload.yaml        |  4 +-
 .../knowmart-app/knowmart-backend/image.lock.yaml  |  6 +--
 .../workload.yaml                                  |  4 +-
 .../knowmart-backend/migration/workload.yaml       | 12 ++---
 .../knowmart-backend/rabbitmq/workload.yaml        |  4 +-
 .../knowmart-backend/redis/workload.yaml           |  4 +-
 .../knowmart-backend/runtime/workload.yaml         | 14 +++---
 .../knowmart-web-frontend/image.lock.yaml          |  6 +--
 .../knowmart-web-frontend/workload.yaml            |  4 +-
 72 files changed, 226 insertions(+), 284 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-a8dcfbd497d4fe47"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-a259d4515d2b4ba6"}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -1,6 +1,6 @@
@@ -58,7 +58,7 @@ data:
@@ -72,22 +72,22 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'eedb6d06a361dd229c505ca9b721d0a6b28da807'}
+            - {name: DEPLOYMENT_ID, value: 'fb88c4868a4245f934e59123506b9fe9c7087463'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261025_0009'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261101_0021'}
-        - {name: verify, configMap: {name: 'knowbase-schema-check-v2'}}
+        - {name: verify, configMap: {name: 'knowbase-schema-check-v4'}}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/provider/workload.yaml
@@ -1,13 +1,13 @@
-    {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion"], "Resource": ["arn:aws:s3:::knowfeed-originals/knowfeed/*"]}]}
+    {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion"], "Resource": ["arn:aws:s3:::knowfeed-originals/knowfeed/original/*"]}]}
@@ -52,7 +52,7 @@ spec:
-              printf '{"reader":"knowbase_source_reader","source":"knowfeed-originals/knowfeed/","read_only_policy":true,"management_denied":true}\n'
+              printf '{"reader":"knowbase_source_reader","source":"knowfeed-originals/knowfeed/original/","read_only_policy":true,"management_denied":true}\n'
@@ -62,5 +62,5 @@ spec:
-        - {name: policy, configMap: {name: knowbase-source-policy-v2}}
+        - {name: policy, configMap: {name: knowbase-source-policy-v3}}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-f94d58f949a47ce7"
+  DEPLOYMENT_ID: "knowbase-backend-4ff05034d1f80dcb"
@@ -30,7 +30,7 @@ data:
-  ARTIFACT_S3_ALLOWED_PREFIXES: "knowfeed/"
+  ARTIFACT_S3_ALLOWED_PREFIXES: "knowfeed/original/"
@@ -58,13 +58,6 @@ data:
-  SERVICE_AUTH_USER_DATA_IMPORT_CALLERS: "knowlab"
-  SERVICE_AUTH_USER_DATA_IMPORT_KNOWLAB_CASDOOR_APPLICATION: "sunmoonai-knowlab-knowbase-user-data-import"
-  SERVICE_AUTH_USER_DATA_IMPORT_KNOWLAB_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
-  SERVICE_AUTH_USER_DATA_IMPORT_KNOWLAB_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
-  SERVICE_AUTH_USER_DATA_IMPORT_KNOWLAB_AUDIENCE: "sunmoon-knowlab-knowbase-user-data-import"
-  SERVICE_AUTH_USER_DATA_IMPORT_KNOWLAB_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowlab-knowbase-user-data-import"
-  SERVICE_AUTH_USER_DATA_IMPORT_KNOWLAB_REQUIRED_SCOPE: "knowbase:user-data-import"
@@ -109,17 +102,10 @@ data:
-  KNOWBASE_DATASET_TITLE: "\u96f6\u552e\u7ecf\u8425\u5e93\uff08\u6700\u5c0f\u5b9e\u4f8b\uff09"
-  KNOWBASE_DATASET_REGISTRY_ENABLED: "true"
-  KNOWBASE_DATASET_ALLOWED_BUCKETS: "knowfeed-originals"
-  KNOWBASE_DATASET_CACHE_DIR: "/tmp/knowbase-datasets"
-  KNOWBASE_SEMANTIC_ENGINE_ENABLED: "true"
-  KNOWBASE_SEMANTIC_CACHE_DIR: "/tmp/knowledge-semantic"
-  USER_DATA_READER_APPS_JSON: "{\"admin/sunmoonai-knowbench-knowbase-user-data-read\": \"knowbench\", \"admin/sunmoonai-knowlab-knowbase-user-data-grant-test\": \"knowlab\", \"admin/sunmoonai-knowlab-knowbase-user-data-import\": \"knowlab\", \"admin/sunmoonai-knowmart-knowbase-user-data-purchase\": \"knowmart\"}"
@@ -153,7 +139,7 @@ spec:
@@ -163,7 +149,7 @@ spec:
@@ -222,7 +208,7 @@ spec:
@@ -232,7 +218,7 @@ spec:
@@ -285,7 +271,7 @@ spec:
@@ -295,7 +281,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-543ccea19e2023d0"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-fcf501f37efdcf19"}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-07ba70d1c2800ffc"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:cf2aa9357d5305fe56165742ac1816a5cf9556a4df0ccd4651c62927d73921bc
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: c4f64f03349df7148225430cf2506ba3746decd7
pointer-commit 5d17e1ba4018f70cb09d5bce157a1a889ed707e6
tag release-20261101-5
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

### 11-check-knowmart.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-39 推送成功后可删。
