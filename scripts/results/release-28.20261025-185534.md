# release #28：账 175 六应用本地用户按 subject 认并合并旧份；knowbench 178、link 0.5.3；会合点转发设备编号；账 173

- 时间：2026-10-25T18:55:35+08:00；分支 fable；应用 tpl, knowfeed, knowbase, knowbench, knowlab, knowmart；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/28/）
- 提交：deploy 3219770a3715c5c1ca0626efa1f4fb0a33c8405b；指针 3c4a3031992860154e0d1197138fd0c43013f4f1；tag release-20261025-7；批准：批准人 admin  2026-10-25T18:42:36+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 57ed4d72..14facdee 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -6,51 +6,51 @@
 ---
 applications:
   tpl:
-    parent_revision: 65b8b11d3c21717a0c768490e329e5e19e43e020
-    backend_parent_revision: ab7139389cbc40a04459a3403ffc5ee4c8e26d89
-    backend_revision: ab7139389cbc40a04459a3403ffc5ee4c8e26d89
-    web_parent_revision: 479c7e6ce6e69a5e4daf41bb55aed5f3b95a87c7
-    web_revision: 479c7e6ce6e69a5e4daf41bb55aed5f3b95a87c7
-    admin_parent_revision: b89e474191109d807cdd50d56ecea971c0269a4a
-    admin_revision: b89e474191109d807cdd50d56ecea971c0269a4a
+    parent_revision: 4df23f1e89d529cd3d76f531edfd83add0e53afb
+    backend_parent_revision: c7cc3f4806fc9f945e9d4fb2c858bbe9049e1a76
+    backend_revision: c7cc3f4806fc9f945e9d4fb2c858bbe9049e1a76
+    web_parent_revision: 76b50b6c49dfa92df6cee09ed3fe6fb0d1065160
+    web_revision: 76b50b6c49dfa92df6cee09ed3fe6fb0d1065160
+    admin_parent_revision: 722c6b80e849d6352f28abbdd7362e1151191c14
+    admin_revision: 722c6b80e849d6352f28abbdd7362e1151191c14
   knowfeed:
-    parent_revision: 808b7e1de97272f4376674f58907e94896e29d0e
-    backend_parent_revision: 6239d224d9b2fc5bd4be03923800b5cd40490e8d
-    backend_revision: 6239d224d9b2fc5bd4be03923800b5cd40490e8d
+    parent_revision: fc065ea073eb496d2b40260a4323056a5a2e9a48
+    backend_parent_revision: c4cd1d683abd8b275777f82fd19b2c7d096e84ff
+    backend_revision: c4cd1d683abd8b275777f82fd19b2c7d096e84ff
     web_parent_revision: bca159f76befc47b1b38e7028c0f63c68b334759
     web_revision: bca159f76befc47b1b38e7028c0f63c68b334759
     admin_parent_revision: b344c106c4f44522770b8cca3e9a8121e0b3ce32
     admin_revision: b344c106c4f44522770b8cca3e9a8121e0b3ce32
   knowbase:
-    parent_revision: b6bf588eb1163a9a62502238780c7a20802c16aa
-    backend_parent_revision: 8ca7fc88f1567da2976ecd53143addc443c48588
-    backend_revision: 8ca7fc88f1567da2976ecd53143addc443c48588
+    parent_revision: b16d7aa8c7ace36a3d84e873718c69a8e2d5f9ae
+    backend_parent_revision: eedb6d06a361dd229c505ca9b721d0a6b28da807
+    backend_revision: eedb6d06a361dd229c505ca9b721d0a6b28da807
     web_parent_revision: 8c338db2b7222702f71cef892fd283016c148210
     web_revision: 8c338db2b7222702f71cef892fd283016c148210
     admin_parent_revision: f097495080ef6ef7296beb0fcc9430b4079d8011
     admin_revision: f097495080ef6ef7296beb0fcc9430b4079d8011
   knowbench:
-    parent_revision: e9dc9ebe7c44831a5642aebf398cbf5d59247007
-    backend_parent_revision: 281f4bc29e55a93a7c48a2b61b882b07f1b8747c
-    backend_revision: 281f4bc29e55a93a7c48a2b61b882b07f1b8747c
+    parent_revision: 436860216f3e3e3f33e9d372dbb51b541e1f873b
+    backend_parent_revision: 2ffdc12299cedcb4d39390fd40c2fd4a98a49ddd
+    backend_revision: 2ffdc12299cedcb4d39390fd40c2fd4a98a49ddd
     web_parent_revision: 44d08cdc2f5562e9557f68bf85b4bb2719b2d3eb
     web_revision: 44d08cdc2f5562e9557f68bf85b4bb2719b2d3eb
     admin_parent_revision: 26964553ed9d581ac855c38edeaee8e65add792f
     admin_revision: 26964553ed9d581ac855c38edeaee8e65add792f
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 6e95425348b673f7a02efb59b1bdf3f719092ef2
-    backend_parent_revision: 519e21d695ce95cc97446f0107d6693e1471ded0
-    backend_revision: 519e21d695ce95cc97446f0107d6693e1471ded0
+    parent_revision: ce93fbc63e2ddea6b1c435f227ec3f8af6dfbe6a
+    backend_parent_revision: 8684d258b452e5b755de1a67b08884a5bdf29aa2
+    backend_revision: 8684d258b452e5b755de1a67b08884a5bdf29aa2
     web_parent_revision: 3a0f2c847c220770d28177288023debc75172f19
     web_revision: 3a0f2c847c220770d28177288023debc75172f19
     admin_parent_revision: 28c79f0c38d4a01753dd92f403587470585f9ac3
     admin_revision: 28c79f0c38d4a01753dd92f403587470585f9ac3
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowmart:
-    parent_revision: 09218c16a29cb9150b7758e1aca06798e928efde
-    backend_parent_revision: 928ad749fe0d5ac9a186b41de7baef13ca1d295f
-    backend_revision: 928ad749fe0d5ac9a186b41de7baef13ca1d295f
+    parent_revision: 5e19a4cd28817d7db4069dc1a3b8ff4954c32939
+    backend_parent_revision: 884f0931efcd696dc1923c7cf9f1f341edf746be
+    backend_revision: 884f0931efcd696dc1923c7cf9f1f341edf746be
     web_parent_revision: db315f20e6354ce9fdaee34b563a6d0a3ef2ef9e
     web_revision: db315f20e6354ce9fdaee34b563a6d0a3ef2ef9e
     admin_parent_revision: d14c3dc41293c660634a92aed2f1b14d46d5ef80
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:f94d58f949a47ce72def77921a17b32d374ff5abef0a00bbe8fe1593f269b018 source_revision: eedb6d06a361dd229c505ca9b721d0a6b28da807 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:309d4b37e49c5115a12d54d90d893cd3b47e46a5451301761548e9ea17793972 source_revision: 2ffdc12299cedcb4d39390fd40c2fd4a98a49ddd 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:dd38938ea04f41678c2e39618b6721e5f2e8c9420f617a7f1fcad0c1778d5b54 source_revision: c4cd1d683abd8b275777f82fd19b2c7d096e84ff 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:aba8d849bbffe8aa5fbfc90e955966ed2941a29bf07c5385ccb48461770fad90 source_revision: 8684d258b452e5b755de1a67b08884a5bdf29aa2 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:3f5dc774eb5c9051f8e3f1740941a86e2a22e070702001df8eb23029effd57c9 source_revision: 884f0931efcd696dc1923c7cf9f1f341edf746be 
gitops/components/app-platform/tpl-app/tpl-admin-frontend/image.lock.yaml: digest: sha256:6b427f8e0510465ec76f6b6decddde94e5d3c9e58d08e557bed1f43fa3aec4e6 source_revision: 722c6b80e849d6352f28abbdd7362e1151191c14 
gitops/components/app-platform/tpl-app/tpl-backend/image.lock.yaml: digest: sha256:1f1c52b5e8d5585d1331550bf73c0b61d83b0240f30318119ca5f10568a6fc3b source_revision: c7cc3f4806fc9f945e9d4fb2c858bbe9049e1a76 
gitops/components/app-platform/tpl-app/tpl-web-frontend/image.lock.yaml: digest: sha256:be8c8f9af7da10848af7faccf3ddcce3790d2d4c13402a4538fe3b963534a9fa source_revision: 76b50b6c49dfa92df6cee09ed3fe6fb0d1065160 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-backend/identity/workload.yaml        |  4 ++--
 .../knowbase-app/knowbase-backend/image.lock.yaml  |  6 +++---
 .../knowbase-backend/migration/workload.yaml       |  8 ++++----
 .../knowbase-backend/rabbitmq/workload.yaml        |  4 ++--
 .../knowbase-backend/redis/workload.yaml           |  4 ++--
 .../knowbase-backend/runtime/workload.yaml         | 14 +++++++-------
 .../knowbench-backend/identity/workload.yaml       |  4 ++--
 .../knowbench-backend/image.lock.yaml              |  6 +++---
 .../knowbase-user-data-read-identity/workload.yaml |  4 ++--
 .../knowlab-read-identity/workload.yaml            |  4 ++--
 .../knowmart-summon-identity/workload.yaml         |  4 ++--
 .../knowbench-backend/migration/workload.yaml      |  8 ++++----
 .../knowbench-backend/rabbitmq/workload.yaml       |  4 ++--
 .../knowbench-backend/redis/workload.yaml          |  4 ++--
 .../runtime/agent-releases.sops.yaml               | 22 +++++++++++-----------
 .../knowbench-backend/runtime/workload.yaml        | 18 +++++++++---------
 .../service-identity/workload.yaml                 |  4 ++--
 .../knowbench-backend/test-computer/workload.yaml  | 12 ++++++------
 .../knowfeed-backend/identity/workload.yaml        |  4 ++--
 .../knowfeed-app/knowfeed-backend/image.lock.yaml  |  6 +++---
 .../knowfeed-backend/migration/workload.yaml       |  8 ++++----
 .../knowfeed-backend/rabbitmq/workload.yaml        |  4 ++--
 .../knowfeed-backend/redis/workload.yaml           |  4 ++--
 .../knowfeed-backend/runtime/tls.sops.yaml         | 18 +++++++++---------
 .../knowfeed-backend/runtime/workload.yaml         | 14 +++++++-------
 .../service-identity/workload.yaml                 |  4 ++--
 .../knowlab-backend/identity/workload.yaml         |  4 ++--
 .../knowlab-app/knowlab-backend/image.lock.yaml    |  6 +++---
 .../workload.yaml                                  |  4 ++--
 .../workload.yaml                                  |  4 ++--
 .../knowbench-testrun-identity/workload.yaml       |  4 ++--
 .../knowmart-deliver-identity/workload.yaml        |  4 ++--
 .../knowlab-backend/migration/workload.yaml        |  8 ++++----
 .../knowlab-backend/rabbitmq/workload.yaml         |  4 ++--
 .../knowlab-backend/redis/workload.yaml            |  4 ++--
 .../knowlab-backend/runtime/workload.yaml          | 14 +++++++-------
 .../knowmart-backend/identity/workload.yaml        |  4 ++--
 .../knowmart-app/knowmart-backend/image.lock.yaml  |  6 +++---
 .../workload.yaml                                  |  4 ++--
 .../knowmart-backend/migration/workload.yaml       |  8 ++++----
 .../knowmart-backend/rabbitmq/workload.yaml        |  4 ++--
 .../knowmart-backend/redis/workload.yaml           |  4 ++--
 .../knowmart-backend/runtime/workload.yaml         | 14 +++++++-------
 .../tpl-app/tpl-admin-frontend/image.lock.yaml     |  6 +++---
 .../tpl-app/tpl-admin-frontend/workload.yaml       |  4 ++--
 .../tpl-app/tpl-backend/identity/workload.yaml     |  4 ++--
 .../tpl-app/tpl-backend/image.lock.yaml            |  6 +++---
 .../tpl-app/tpl-backend/migration/workload.yaml    |  8 ++++----
 .../tpl-app/tpl-backend/rabbitmq/workload.yaml     |  4 ++--
 .../tpl-app/tpl-backend/redis/workload.yaml        |  4 ++--
 .../tpl-app/tpl-backend/runtime/tls.sops.yaml      | 18 +++++++++---------
 .../tpl-app/tpl-backend/runtime/workload.yaml      | 14 +++++++-------
 .../tpl-app/tpl-web-frontend/image.lock.yaml       |  6 +++---
 .../tpl-app/tpl-web-frontend/workload.yaml         |  4 ++--
 54 files changed, 187 insertions(+), 187 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '8ca7fc88f1567da2976ecd53143addc443c48588'}
+            - {name: DEPLOYMENT_ID, value: 'eedb6d06a361dd229c505ca9b721d0a6b28da807'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261023_0008'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261025_0009'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-0d6765b3fbec8f01"
+  DEPLOYMENT_ID: "knowbase-backend-f94d58f949a47ce7"
@@ -120,7 +120,7 @@ spec:
@@ -130,7 +130,7 @@ spec:
@@ -189,7 +189,7 @@ spec:
@@ -199,7 +199,7 @@ spec:
@@ -252,7 +252,7 @@ spec:
@@ -262,7 +262,7 @@ spec:
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
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '281f4bc29e55a93a7c48a2b61b882b07f1b8747c'}
+            - {name: DEPLOYMENT_ID, value: '2ffdc12299cedcb4d39390fd40c2fd4a98a49ddd'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261023_0025'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261025_0026'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/agent-releases.sops.yaml
@@ -4,22 +4,22 @@ metadata:
-    WORKBENCH_AGENT_DOWNLOAD: ENC[AES256_GCM,data:X5iWoN3ZSxnW9eliRWyTKUteVw2AjQBXIiucdxuHMsJtU5PQFNKkg1mEK0SZhYoO+pX3DTVRmvZ3+uqzwHbd5yR208WlLDQQolvUccymnyoQmIgLgeD/eWQRZJRVx1aJuTzgUnaX9r2e6aiIMfBnkd7AnQfuc+7/BR9dul6LQFcBUgTaInMsm3hrImWmKZN/CzZ8Hn8jmhHHp1wyoU0VRRq7gXEEQQJep0EOtEp1+J0S9G+Fm5xtEkdIji8PtidIaqvGS8OQTB3KsaEAMteA9nFSpgtjnyFV7tc35oWhy2C/9YwJd+w+sAOJAdQcwtcjdwbb3kS2N1ifY4CAk8Mp3aocJhlHdmjPOS3VOmXoJkIEwFdSLUDqC6OR8AhSXatnrzNfS7Bv3yQGXAetJ1lTRQOCIkhleCASVWzMZ7CXR6VYnZVzLDqmVpYrP8ENoLIo1qzFJeFd6EHstr35ldk4LM/Rul4N4ZQeH+fzgQtNnqt4pX6SYoWFWyiy1QKnqwdxzBJyHbHK9k4fEEKY/iX/TfQu+qWrWMu00zPsgJVc19/Qymw2KlLdrkn6,iv:l7u3y4IQeV1Xdsy/btAMTcErzX2tpySijU0Jlgq8s+M=,tag:a1tLUHA2c4XWHbHrTWP7zw==,type:str]
-    WORKBENCH_AGENT_INSTALL_SCRIPT_TEMPLATE: ENC[AES256_GCM,data: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,iv:qWJx55EgqH80vO3MVp/sCRIzPywkW7EdXarLAo/XcAE=,tag:niJO4gHy4s5I19kZdGwloQ==,type:str]
-    WORKBENCH_AGENT_RELEASE_STORAGE: ENC[AES256_GCM,data:6dLzUcoVbaX9ur44rOsYgFJW4dCMmMa3/veOZUA5ijL06D//UVssDiAmBmfhdR3j2CMdP8Efnv3LAdNzL6Al3BW1MNyLTm5G5BzuBGhRI+z4e0eHC1OnM3wYfsSVj+CQFHOuO7nNLK3v2zzamlrpgeRc9ds8CORiETP2phgrD3lDmvGqB3Ekvp3y6SusQXZ0FfMjLjrB210XkZr/EdJayGie0QGHVj/6DUZbe7BSFy+29h2Z6y9i1BYuZGJhNa8qhqHREFLQFG3xPGGxuCLfjAiOzdl3cvo6Yhf/GDWKlu+6osRA0J0mp3sLR7c0WDrsdHh28YlF5bKlmCs=,iv:ST8FpRJtl/v6MjF3uH44TmOGxLaRmbJu/YCmpVo1NM0=,tag:L9ivKdMmg/VGlMg2tCYGBg==,type:str]
-    ca.crt: ENC[AES256_GCM,data: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,iv:0qleGCGpFReG7aw+Zszi748ZMMfPmc+B58pRER61YdQ=,tag:xQzsIIa7B08KnguGOLgEag==,type:str]
+    WORKBENCH_AGENT_DOWNLOAD: ENC[AES256_GCM,data:SLBM1JUykPULdjIqfTiLzlUJXeJSMUeRjWpLPoHEoTszRUfokCDDL8NpEWBSRFEtImWWJAs0dsv3pm19TyiLkhMrIJalBTbihS6P7bGYPT47R/CCUtfvvJ72lKAf3CycvMzEUAxfWwiPGjlKxjMg4umqlyHDSAfXK1KCaz60evmg2BLcOKskpVtV2RpOAzboa3gaPUgXGrtDE/RxtGAjXnQS1dJN6cwoj9xL7kn6/NsYN5xd/A33frbco1Kk50v9NUkQen56xhhyViJNrdDcnAH7eLPMqmj4YYuwTCdtv1rsZfaZ7dA3zqNQhk2nzE7DSMp+Jj1LnK8oBLsi5WjFopBhtga/7buHf3IGb3LuwhwDUxzxPJgGcJEcQVRR/fjH4NdsOg3FFS/HYTtUQT2tW6Om4tty5XSbHv3ERCfAKg+oADHklhALvwMNpaiwhWo7IYSJ61I5r9Cqu0U7qDcOk83EhaOGG9NOY9+l4uVQbH99dadTtQ5OFMXK4N10P+x5pmuM19+/4Af6rcZqeEeWD0sin5ZOtd8wXRD11eWjZ87hLeTHBeYUhKJR,iv:o9STA25IMxDG39uDUPZIcJg9dgtDNeqrycdKRa7nh2A=,tag:5lH6m5TE4grGZtvJSlTsTw==,type:str]
+    WORKBENCH_AGENT_INSTALL_SCRIPT_TEMPLATE: ENC[AES256_GCM,data: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,iv:KJdqwr7wlPLl+7DBYYyyxnKv88p3jb5e832rmId3n5U=,tag:RJCflp8oM0GPr+1ObXkw0w==,type:str]
+    WORKBENCH_AGENT_RELEASE_STORAGE: ENC[AES256_GCM,data:itiwcmFkwLb72YxLMDIX8pzPSKq1dDn/CyeKAG5NboEtZ1FMj+4HF+vCyddZWvD359OGpFtxFcbtusKj9hy5a6Y1EIYjVGnsnZtc9fuPdBJNYrmAz5B89AAR83DkEk1Ke21Alg7TZVDJh5+6ys6lCdCdgvR4s6SuFLmX1eM2jXnhfmD/l4UkOCgYFQZQ+FytBtLKWhqAxlkchpq8ZTPYH/SGOqz9u/CK64eNkW8OjhTzk9KCW/BBoyzyhQDtX4cCuUlx2JbOxia39NIukeh0LX5RSJNqIoXF4KlQLxSqMSk/jkNqGo47UAJJevhInblpVn0zmmt/7zdTwG4=,iv:r4yGhklOJ36eLu5moyk2gPrZ8n7yUTRMCdJeYldHQQo=,tag:+z4WsqzsGf9DYdjz4H9mvQ==,type:str]
+    ca.crt: ENC[AES256_GCM,data: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,iv:LhpPYcG0Ur8tF/StlNp4ysS9CsZ3gp4ZQ7t8/gDaW40=,tag:hWF42L/Opjv6MscXKGB1Tg==,type:str]
-            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBSMFF4YVFYZUtuUS9xM1ZM
-            QnZQUW1ndzhjb2lNbzJJejJwS0xBR1hrWDJFCnVyS1lKU0x4a2hiMTBGdnJWTjBX
-            UWkrRVZFOTJkSm11MUtzbWJwKzRmY0kKLS0tIEw3REFrVFZoTk1OTGFVWEJUN3Zn
-            d3Nsem44QzlreXNZTHk3R1FjTFJoZkEKW0jbq9G8ocqg6guI/9e/OXS+mBMgWAa/
-            CDPPmbXx3UgMZwtbUAEjJ6quFJiXIrodeCtfhVvBF8KyadW7t1DPgw==
+            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBnQWZOeWw4OXBTaEVjYnJQ
+            WnVtQ0E0V1NjMUFxRWhwT3pWczZRRHA0bGhNClVwWHAxT3FsczdQdXZ1TTZvcVNI
+            T3pwUllyKy9Ea0p1a2Y3bmtsMlZGWmMKLS0tIFNSckNaUTJzMW11UmYrTXo3QnlV
+            Y1h2b2k1T3UyZWIzMU9JYlV1K0VRbncKfV54YGcClHybPSj2o8CCKf4u8A05ctjp
+            NEs+oFjv1orwrOBfVRhPnh7AgHRBZlCdmbv6xBDuhyg/tLco0zSVBA==
-    lastmodified: "2026-10-25T05:42:12Z"
-    mac: ENC[AES256_GCM,data:2bPrFAcQifCIeiDaCxjxvmCsN8RAQETPF/mALFjgkK9wqjljiS2G0ORkqvKP5QfYYyqFKneuFYWlfJAbAjQuOC5NAuUzaT8jSNDOGpfXZBn9LqMVRNt2CLqiFPcEPsjkb9bt+0O5QKupCZ4vbPTfIzrPQXDpCvjVq/GpUGRDD3c=,iv:Ov0tWOE+Y2OECIV4zFPNzGO/TZd5c3gRK8+FxenYoTE=,tag:/yOIyOv7gKv/vBVVH0Y6Ig==,type:str]
+    lastmodified: "2026-10-25T09:52:25Z"
+    mac: ENC[AES256_GCM,data:IvOB7jyzXohigaBZFI3lnU4pZwTMNISPHQt7xxBlTvEpssTt/lcuzpjDIirPKCFf75H7gwGO7C+9+NDgXsPHl6m8GsR5RpRBAyL+jLhHNp6LXmsnVRAXPaLhv/EGnSWPCNgRe9Q+Lhbol3Osdtw11ixyTyuZDCPJqFzo0rZG91g=,iv:ERLcyPci4VS5tE0mL5Wt+uNBTGeuYk/gFn5DBXCSWgg=,tag:5RYi3VLXOdhcBMDNg3vkXw==,type:str]
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:bc3e45ba84e818c30466e5526e75fb14c11c2ed7101763acb02e77143486b57a
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 3219770a3715c5c1ca0626efa1f4fb0a33c8405b
pointer-commit 3c4a3031992860154e0d1197138fd0c43013f4f1
tag release-20261025-7
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
kustomization.kustomize.toolkit.fluxcd.io/tpl-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/tpl-database condition met
kustomization.kustomize.toolkit.fluxcd.io/tpl-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/tpl-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/tpl-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/tpl-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/tpl-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/tpl-web condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowfeed-identity condition met
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
kustomization.kustomize.toolkit.fluxcd.io/knowlab-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-grant-test-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-import-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbench-testrun-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowmart-deliver-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-storage condition met
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

### 11-check-tpl.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-28 推送成功后可删。
