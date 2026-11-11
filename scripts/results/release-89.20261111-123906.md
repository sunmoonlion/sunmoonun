# release #89：Web and administrator 24-hour login fixes

- 时间：2026-11-11T12:39:06+08:00；分支 login-release-20261111；目标 tpl, knowfeed, knowbase, knowlab, knowmart, knowbench；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/89/）
- 提交：deploy 5452131b0a74953e7fb3b60c7f3695836d552d8f；指针 65c04425dbe9e79b0ae2845436611461f1dc2698；tag release-20261111-1；批准：批准人 admin  2026-11-11T12:24:29+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml: digest: sha256:89a85ac75c092acba475a660a1ee389f494729649ed2c5ef101465df670e4c73 source_revision: f2f6df3163a01c71be13efdd20b87187b63693ec 
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:10384ba19f29152a17bc0c22ae8931ef53329b33ce402671cf2dd6a529518d4e source_revision: 5d78176c5d0e899d9b5fa649c927641c2e8acdfd 
gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml: digest: sha256:4c729217e3d6307c96565bf9ba2cd2ef169d9731627ac4dd7bdd937c18c8dbb8 source_revision: 3188c01da4bffe81511c09062b804bc043c919e7 
gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml: digest: sha256:2fb98ed57a9aeca7549fa9d1f44fab2460989a0f16da0bea2bbba8115b2a34d6 source_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:f6fe17d689a4dc320fd80d74d52dde1c5b93b326c9b5c2820483f3f9b1d20dc9 source_revision: 1d1fdda4e9d1134d6040abd5c26d0f0d64a36b3f 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:1d18c18eee8e4721c2291ab0e52bbe5217e2742850771a70e8789ea1a611a660 source_revision: 4b8248e06366802b9b5e97014110332a66e6a9a7 
gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml: digest: sha256:488a3181a5f5960e9dd96a776e31101d9a7fe3c42c2aad5d9ae4b9c7fd50351a source_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:afe1c8ddc9e2d5c69b19961f1749e4d6f5eab0a51c4c8c9465f1aa6bbc627294 source_revision: 0fa4b9e9b60ca632345f09f5fcdd017b9010ae6c 
gitops/components/app-platform/knowfeed-app/knowfeed-web-frontend/image.lock.yaml: digest: sha256:2a51defb4cf68bddadd5d1743ec260c05a8e213e0fe35ea9a4d98da79e94a5c1 source_revision: 5ef58d640154cf6c9b7de3a0d2cadc75f41bc32e 
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:7ad7e4bd1aed37cbc06f947322c8f28c775c479ae8420db806944e9fa1836961 source_revision: 89fe3ac1f6178018186584db7542f11102896381 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:cd4fa1569f0a076114f044431b2588bfcf3cf8085bfb488d908b06a2a2d6c8a9 source_revision: 07d81cdcac06d9644264740b5db350caf2a2d5b7 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:0f4db6cf0858844c539d48bb1e4d1c5b3630cf770964ec381b8d4854703fc79c source_revision: fea8a24438fa5fa81d4a5b29c025b198a1441a14 
gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml: digest: sha256:78ce490938b33cca0656b18d1d458255c92c0d15ab5ca6c340c41215de26b110 source_revision: 5f109118ffbaca623a732ed33eaea61a2905241a 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:4b93e94952457001143e4fb74d1648f8df0e04a0b1c08ad62295389b48d596bf source_revision: d6b53ba2148f90cd3adbfacb0843b9d6de8ea471 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:eb6a236c7f9c9797803b91cd48c80414082ccbcda442c0d95b490b7ea6ab28d6 source_revision: 6a893cecddeea70fd14cb93e6c027679bdbd9ea1 
gitops/components/app-platform/tpl-app/tpl-admin-frontend/image.lock.yaml: digest: sha256:0312ab07e7c90851d81f6c1bdebccfa676b4665cabd18a48336c0d5b8e22cde3 source_revision: 722c6b80e849d6352f28abbdd7362e1151191c14 
gitops/components/app-platform/tpl-app/tpl-backend/image.lock.yaml: digest: sha256:887f4611cecf9589941064b09d6afd45584f9069b2d3e295f04623326b72915c source_revision: 75482b2602b1300a3244e915b1465ea8d417e60b 
gitops/components/app-platform/tpl-app/tpl-web-frontend/image.lock.yaml: digest: sha256:64b5426d9b68d288b089e5b3941725daba43be1b5c794bf178f68540081312ab source_revision: 6f46aef4bcbca07b126682c24ec1b2cedb42d52c 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-admin-frontend/image.lock.yaml        |  4 +--
 .../knowbase-admin-frontend/workload.yaml          |  4 +--
 .../knowbase-backend/identity/workload.yaml        | 31 +++++++++++-----------
 .../knowbase-app/knowbase-backend/image.lock.yaml  |  6 ++---
 .../knowbase-backend/migration/workload.yaml       |  6 ++---
 .../knowbase-backend/rabbitmq/workload.yaml        |  4 +--
 .../knowbase-backend/redis/workload.yaml           |  4 +--
 .../knowbase-backend/runtime/workload.yaml         | 14 +++++-----
 .../knowbase-web-frontend/image.lock.yaml          |  6 ++---
 .../knowbase-web-frontend/workload.yaml            |  4 +--
 .../knowbench-admin-frontend/image.lock.yaml       |  4 +--
 .../knowbench-admin-frontend/workload.yaml         |  4 +--
 .../knowbench-backend/identity/provision.sops.yaml | 18 ++++++-------
 .../knowbench-backend/identity/workload.yaml       | 31 +++++++++++-----------
 .../knowbench-backend/image.lock.yaml              |  6 ++---
 .../workload.yaml                                  |  4 +--
 .../knowbase-user-data-read-identity/workload.yaml |  4 +--
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 +--
 .../workload.yaml                                  |  4 +--
 .../knowmart-catalog-identity/workload.yaml        |  4 +--
 .../knowmart-demand-identity/workload.yaml         |  4 +--
 .../knowmart-summon-identity/workload.yaml         |  4 +--
 .../knowbench-backend/migration/workload.yaml      |  6 ++---
 .../knowbench-backend/rabbitmq/workload.yaml       |  4 +--
 .../knowbench-backend/redis/workload.yaml          |  4 +--
 .../runtime/agent-releases.sops.yaml               | 22 +++++++--------
 .../knowbench-backend/runtime/workload.yaml        | 20 +++++++-------
 .../service-identity/workload.yaml                 |  4 +--
 .../knowbench-web-frontend/image.lock.yaml         |  6 ++---
 .../knowbench-web-frontend/workload.yaml           |  4 +--
 .../knowfeed-admin-frontend/image.lock.yaml        |  4 +--
 .../knowfeed-admin-frontend/workload.yaml          |  4 +--
 .../knowfeed-backend/identity/workload.yaml        | 31 +++++++++++-----------
 .../knowfeed-app/knowfeed-backend/image.lock.yaml  |  6 ++---
 .../workload.yaml                                  |  4 +--
 .../knowfeed-backend/migration/workload.yaml       |  6 ++---
 .../knowfeed-backend/rabbitmq/workload.yaml        |  4 +--
 .../knowfeed-backend/redis/workload.yaml           |  4 +--
 .../knowfeed-backend/runtime/workload.yaml         | 14 +++++-----
 .../service-identity/workload.yaml                 |  4 +--
 .../knowfeed-web-frontend/image.lock.yaml          |  6 ++---
 .../knowfeed-web-frontend/workload.yaml            |  4 +--
 .../knowlab-admin-frontend/image.lock.yaml         |  4 +--
 .../knowlab-admin-frontend/workload.yaml           |  4 +--
 .../knowlab-backend/identity/workload.yaml         | 31 +++++++++++-----------
 .../knowlab-app/knowlab-backend/image.lock.yaml    |  6 ++---
 .../workload.yaml                                  |  4 +--
 .../workload.yaml                                  |  4 +--
 .../workload.yaml                                  |  4 +--
 .../knowbase-user-data-read-identity/workload.yaml |  4 +--
 .../knowbench-incubate-identity/workload.yaml      |  4 +--
 .../knowbench-testrun-identity/workload.yaml       |  4 +--
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 +--
 .../knowmart-deliver-identity/workload.yaml        |  4 +--
 .../knowlab-backend/migration/workload.yaml        |  6 ++---
 .../knowlab-backend/rabbitmq/workload.yaml         |  4 +--
 .../knowlab-backend/redis/workload.yaml            |  4 +--
 .../knowlab-backend/runtime/workload.yaml          | 14 +++++-----
 .../knowlab-web-frontend/image.lock.yaml           |  6 ++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml |  4 +--
 .../knowmart-admin-frontend/image.lock.yaml        |  4 +--
 .../knowmart-admin-frontend/workload.yaml          |  4 +--
 .../knowmart-backend/identity/workload.yaml        | 31 +++++++++++-----------
 .../knowmart-app/knowmart-backend/image.lock.yaml  |  6 ++---
 .../workload.yaml                                  |  4 +--
 .../knowmart-backend/migration/workload.yaml       |  6 ++---
 .../knowmart-backend/rabbitmq/workload.yaml        |  4 +--
 .../knowmart-backend/redis/workload.yaml           |  4 +--
 .../knowmart-backend/runtime/workload.yaml         | 14 +++++-----
 .../knowmart-web-frontend/image.lock.yaml          |  6 ++---
 .../knowmart-web-frontend/workload.yaml            |  4 +--
 .../tpl-app/tpl-admin-frontend/image.lock.yaml     |  4 +--
 .../tpl-app/tpl-admin-frontend/workload.yaml       |  4 +--
 .../tpl-app/tpl-backend/identity/workload.yaml     | 31 +++++++++++-----------
 .../tpl-app/tpl-backend/image.lock.yaml            |  6 ++---
 .../tpl-app/tpl-backend/migration/workload.yaml    |  6 ++---
 .../tpl-app/tpl-backend/rabbitmq/workload.yaml     |  4 +--
 .../tpl-app/tpl-backend/redis/workload.yaml        |  4 +--
 .../tpl-app/tpl-backend/runtime/workload.yaml      | 14 +++++-----
 .../tpl-app/tpl-web-frontend/image.lock.yaml       |  6 ++---
 .../tpl-app/tpl-web-frontend/workload.yaml         |  4 +--
 81 files changed, 314 insertions(+), 306 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-70c030b4e584cc1e"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-89a85ac75c092acb"}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -1,6 +1,6 @@
@@ -131,9 +131,9 @@ data:
-                    # Owner 2026-11-11: browser sessions and web tokens last at most 24 h;
-                    # admin consoles keep one hour. The backend also enforces token expiry.
-                    'expireInHours': 24 if surface == 'web' else 1, 'refreshExpireInHours': 0,
+                    # Owner 2026-11-11: both web and admin sessions last at most 24 h.
+                    # The backend also enforces token expiry.
+                    'expireInHours': 24, 'refreshExpireInHours': 0,
@@ -187,6 +187,15 @@ data:
+                # Owner 2026-11-11: migrate only the exact previous lifetime (web 12 h,
+                # admin 1 h). Credentials, grants and organization must already match.
+                drift = {k for k, v in desired.items() if existing.get(k) != v}
+                previous_lifetime = 12 if surface == 'web' else 1
+                if drift == {'expireInHours'} and existing.get('expireInHours') == previous_lifetime:
+                    changed = api('POST', '/api/update-application', dict(existing, expireInHours=24),
+                                  params={'id': 'admin/' + config['name'], 'columns': 'expireInHours'})
+                    require(changed == 'Affected', 'Browser session lifetime was not applied')
+                    existing = api('GET', '/api/get-application', params={'id': 'admin/' + config['name']})
@@ -199,14 +208,6 @@ data:
-                # Owner 2026-11-11: only the web lifetime may move from the exact
-                # previous 12-hour policy. Credentials, grants and organization must match.
-                drift = {k for k, v in desired.items() if existing.get(k) != v}
-                if surface == 'web' and drift == {'expireInHours'} and existing.get('expireInHours') == 12:
-                    changed = api('POST', '/api/update-application', dict(existing, expireInHours=24),
-                                  params={'id': 'admin/' + config['name'], 'columns': 'expireInHours'})
-                    require(changed == 'Affected', 'Web session lifetime was not applied')
-                    existing = api('GET', '/api/get-application', params={'id': 'admin/' + config['name']})
@@ -297,7 +298,7 @@ spec:
@@ -311,7 +312,7 @@ spec:
@@ -332,7 +333,7 @@ spec:
-        - {name: script, configMap: {name: 'knowbase-identity-provision-v7'}}
+        - {name: script, configMap: {name: 'knowbase-identity-provision-v8'}}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'bf59f85d0bf619766f8a663d7965e2c57306acf2'}
+            - {name: DEPLOYMENT_ID, value: '5d78176c5d0e899d9b5fa649c927641c2e8acdfd'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-351d15ae5c1ab968"
+  DEPLOYMENT_ID: "knowbase-backend-10384ba19f29152a"
@@ -139,7 +139,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
@@ -208,7 +208,7 @@ spec:
@@ -218,7 +218,7 @@ spec:
@@ -271,7 +271,7 @@ spec:
@@ -281,7 +281,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-4a27071b0f573d02"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-4c729217e3d6307c"}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-068f17cac79a8e37"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-2fb98ed57a9aeca7"}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/identity/provision.sops.yaml
@@ -4,20 +4,20 @@ metadata:
-    clients.json: ENC[AES256_GCM,data:0OusxefIuGtGsnmr6BP9la8vsYj4fbBH85JqQ3Vo2VG2XLXgFr8aRPpciPF2LgCwIHjE2RCpTdr3stcyuFJHMsGGtbQqx+qLwwtnvOc/zLK7F6bBeqO848NrTmnsBTJXMcr2Ws+euorsYMKjHObMppQYC9s6ig==,iv:igJOcUrFWMEKAm7vTd+LxBeN31y+aLWf2V4Xkc1tt3g=,tag:GNdHb1CVjXlWTmsyqpDzrg==,type:str]
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:12bc455cdc2239534ccd1e31debf2e34ca5621310de5d0340d3d77d2d8fcc889
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 5452131b0a74953e7fb3b60c7f3695836d552d8f
pointer-commit 65c04425dbe9e79b0ae2845436611461f1dc2698
tag release-20261111-1
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

### 11-check-tpl.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-89 推送成功后可删。
