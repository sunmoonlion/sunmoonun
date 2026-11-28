# release #141：KnowFeed令牌交换v10：放行24h会话补grant

- 时间：2026-11-28T22:55:35+08:00；分支 luna-release-587；目标 knowfeed, knowbase；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/141/）
- 提交：deploy 42171f4cfaeeeaa8d8e79ef11c1a7c40042b62a9；指针 dfa223e1f9ad41d6c4e2a22d1fb68f799be0b88d；tag release-20261128-4；批准：批准人 admin  2026-11-28T22:49:00+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml: digest: sha256:7fe4d5227189c304db7370811fba4e77c2e968fdccbeb6ec072d99b5b03b9c80 source_revision: da9d62cd224dbdb6f40ca56e8c0feb82ebeefcd9 
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:f32032fcf5875193210bdae23e51cbb2a57b4f6c3762311ad9e38debcba455d6 source_revision: 288dc831be714374b0d91ba1ce399c2c8e5bc2f1 
gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml: digest: sha256:650b3abb5061c3e839cddb2d2ab1ceada861d0859b4395555191b2e8bf6fa885 source_revision: e10d22628deb3b1eb7653236452cb85224195a9f 
gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml: digest: sha256:24a20109394045063e9ad3e7abb2e06ae94f829ab460a6e2f12529e01ad2e924 source_revision: 51cb6030c6e07485912aacf92958fe0cb3e452e1 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:63689a74f1e23479c0b40f4d59c448d2715aeb33699c2d3cf486ad4582d7feec source_revision: cf0d52d64ebf35b8816bfad8f37c707a5d9b7c25 
gitops/components/app-platform/knowfeed-app/knowfeed-web-frontend/image.lock.yaml: digest: sha256:b19650de5a08868d55257e6f927b0592b7c5f8a78a6295ef87b82677bf71074d source_revision: 188010e2376312078c1987ffc4abb8b75ee9d7f5 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-admin-frontend/image.lock.yaml          |  4 ++--
 .../knowbase-admin-frontend/workload.yaml            |  4 ++--
 .../knowbase-backend/identity/workload.yaml          | 14 ++++++++------
 .../knowbase-app/knowbase-backend/image.lock.yaml    |  4 ++--
 .../workload.yaml                                    |  4 ++--
 .../knowbase-backend/migration/workload.yaml         |  4 ++--
 .../knowbase-backend/rabbitmq/workload.yaml          |  4 ++--
 .../knowbase-backend/redis/workload.yaml             |  4 ++--
 .../knowbase-backend/runtime/workload.yaml           | 16 ++++++++--------
 .../knowbase-web-frontend/image.lock.yaml            |  4 ++--
 .../knowbase-app/knowbase-web-frontend/workload.yaml |  4 ++--
 .../knowfeed-admin-frontend/image.lock.yaml          |  4 ++--
 .../knowfeed-admin-frontend/workload.yaml            |  4 ++--
 .../knowfeed-backend/identity/workload.yaml          | 20 +++++++++++---------
 .../knowfeed-app/knowfeed-backend/image.lock.yaml    |  4 ++--
 .../knowbase-user-data-supply-identity/workload.yaml |  4 ++--
 .../knowfeed-backend/migration/workload.yaml         |  4 ++--
 .../knowfeed-backend/rabbitmq/workload.yaml          |  4 ++--
 .../knowfeed-backend/redis/workload.yaml             |  4 ++--
 .../knowfeed-backend/runtime/workload.yaml           | 15 ++++++++-------
 .../knowfeed-backend/service-identity/workload.yaml  |  4 ++--
 .../knowfeed-web-frontend/image.lock.yaml            |  4 ++--
 .../knowfeed-app/knowfeed-web-frontend/workload.yaml |  4 ++--
 23 files changed, 73 insertions(+), 68 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-4b1db137a4ba3af2"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-7fe4d5227189c304"}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -196,13 +196,15 @@ data:
-                # SDD 0042 / owner 2026-10-25: the fourth allowed migration, only from the pre-0042
-                # shape (authorization code only, one-hour tokens): add the token exchange grant and
-                # the longer web token. Everything else must already match.
+                # SDD 0042 / owner 2026-10-25: the fourth allowed migration, only from authorization
+                # code alone. Pre-0042 apps were one-hour; later lifetime migrations left some apps at
+                # 12 h or 24 h without token-exchange (KnowFeed). Allow those lifetimes too so adding
+                # the exchange grant (and aligning expireInHours to 24 when still short) is one step.
+                # Everything else must already match.
-                        and existing.get('expireInHours') == 1):
+                        and existing.get('expireInHours') in (1, 12, 24)):
@@ -298,7 +300,7 @@ spec:
@@ -312,7 +314,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/knowbench-function-publish-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,7 +72,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-3f8d581373d454dd"
+  DEPLOYMENT_ID: "knowbase-backend-f32032fcf5875193"
@@ -109,7 +109,7 @@ data:
-  USER_TOKEN_APPS_JSON: "{\"sunmoon-kind-knowbench-web\": \"knowbench\", \"sunmoon-kind-knowlab-web\": \"knowlab\", \"sunmoon-kind-knowmart-web\": \"knowmart\"}"
+  USER_TOKEN_APPS_JSON: "{\"sunmoon-kind-knowbench-web\": \"knowbench\", \"sunmoon-kind-knowlab-web\": \"knowlab\", \"sunmoon-kind-knowmart-web\": \"knowmart\", \"sunmoon-kind-knowfeed-web\": \"knowfeed\"}"
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
-            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-ee7787f25f1acf98"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-650b3abb5061c3e8"}
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowfeed-admin-frontend-1feb3531e35394f9"}
+            - {name: DEPLOYMENT_ID, value: "knowfeed-admin-frontend-24a2010939404506"}
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/identity/workload.yaml
@@ -1,6 +1,6 @@
@@ -196,13 +196,15 @@ data:
-                # SDD 0042 / owner 2026-10-25: the fourth allowed migration, only from the pre-0042
-                # shape (authorization code only, one-hour tokens): add the token exchange grant and
-                # the longer web token. Everything else must already match.
+                # SDD 0042 / owner 2026-10-25: the fourth allowed migration, only from authorization
+                # code alone. Pre-0042 apps were one-hour; later lifetime migrations left some apps at
+                # 12 h or 24 h without token-exchange (KnowFeed). Allow those lifetimes too so adding
+                # the exchange grant (and aligning expireInHours to 24 when still short) is one step.
+                # Everything else must already match.
-                        and existing.get('expireInHours') == 1):
+                        and existing.get('expireInHours') in (1, 12, 24)):
@@ -298,7 +300,7 @@ spec:
@@ -312,7 +314,7 @@ spec:
@@ -323,7 +325,7 @@ spec:
-            - {name: TOKEN_EXCHANGE_SURFACES, value: "[]"}
+            - {name: TOKEN_EXCHANGE_SURFACES, value: "[\"web\"]"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:55dacd58f241046b52d2d53e88f26621af417b4c6b76e641faa2a59bfea00a3d
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 42171f4cfaeeeaa8d8e79ef11c1a7c40042b62a9
pointer-commit dfa223e1f9ad41d6c4e2a22d1fb68f799be0b88d
tag release-20261128-4
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
kustomization.kustomize.toolkit.fluxcd.io/knowbase-knowbench-function-publish-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-provider condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-web condition met
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

### 11-check-knowfeed.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=54   changed=0    unreachable=0    failed=0    skipped=20   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-141 推送成功后可删。
