# release #67：发布第19节knowlab人工特批与二轨工程候选

- 时间：2026-11-03T21:07:29+08:00；分支 release/recovery-methods；目标 knowbench, knowlab, knowmart；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/67/）
- 提交：deploy d2f6a99fdfcb106d0be38bb1a6ab9e4eb02e2945；指针 a8160a6f25285860501b3530310259f7c923342b；tag release-20261103-9；批准：批准人 admin  2026-11-03T20:59:41+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:e5481cf62fe34a6466837a91336f9986b36538e64ffdb3bc556933b82c9f5d68 source_revision: da892497525676dc35894e7c009f05a6851f568c 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:4c850db17a916b31b84c2cbdf841ee4c275d5fb6cf49539d9e57099e687c7fbd source_revision: 725610e826873a042a0754d8653aef8874fbefd7 
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:d78adb9cbdf2d0700ab4b23e132c708d1967596c4ba7c6e28db600600a096af3 source_revision: 89fe3ac1f6178018186584db7542f11102896381 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:4f491dd36a20fe30cdab677f7c92a0d4dd74a432e31e6c9c649b9e16ffffa3b7 source_revision: b86eedfc547bb28bda3c2cd8639189c17a61f6ce 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:899502727ab4570504d96586c7207cafc97b7f4cb95ebd1d2e59027d9e8c4c29 source_revision: 61fdc470d1bd6cf7033ca084925e59f8338828ff 
gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml: digest: sha256:9305a419e2e8e37543456231095bd39536242f35571485549f930e064878246c source_revision: 5f109118ffbaca623a732ed33eaea61a2905241a 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:e7bc236467e30830ca6f82cc72c949d9c8d0d89e2ecceb1f8f8f6e0572f2c9e0 source_revision: 09cf0256d7ea0eb8064914f70d6d31b13dac5c13 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:ae84e4610ff94bf895047e6e180794c77a4dd5dd0bdd6d8ed05fdf3645ed4d87 source_revision: 2bf8dfd67b3996c67de9a96134011e13ceee8246 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-app/knowbench-backend/identity/workload.yaml |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml        |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml       |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml         |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml          |  4 ++--
 .../knowlab-incubation-request-identity/workload.yaml      |  4 ++--
 .../knowmart-catalog-identity/workload.yaml                |  4 ++--
 .../knowmart-demand-identity/workload.yaml                 |  4 ++--
 .../knowmart-summon-identity/workload.yaml                 |  4 ++--
 .../knowbench-backend/migration/workload.yaml              |  6 +++---
 .../knowbench-app/knowbench-backend/rabbitmq/workload.yaml |  4 ++--
 .../knowbench-app/knowbench-backend/redis/workload.yaml    |  4 ++--
 .../knowbench-app/knowbench-backend/runtime/workload.yaml  | 10 +++++-----
 .../knowbench-backend/service-identity/workload.yaml       |  4 ++--
 .../knowbench-app/knowbench-web-frontend/image.lock.yaml   |  6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml     |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/image.lock.yaml     |  6 +++---
 .../knowlab-app/knowlab-admin-frontend/workload.yaml       |  4 ++--
 .../knowlab-app/knowlab-backend/identity/workload.yaml     |  4 ++--
 .../knowlab-app/knowlab-backend/image.lock.yaml            |  6 +++---
 .../knowbase-user-data-directory-identity/workload.yaml    |  4 ++--
 .../knowbase-user-data-grant-test-identity/workload.yaml   |  4 ++--
 .../knowbase-user-data-output-identity/workload.yaml       |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml         |  4 ++--
 .../knowbench-incubate-identity/workload.yaml              |  4 ++--
 .../knowbench-testrun-identity/workload.yaml               |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml          |  4 ++--
 .../knowmart-deliver-identity/workload.yaml                |  4 ++--
 .../knowlab-app/knowlab-backend/migration/workload.yaml    |  8 ++++----
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml     |  4 ++--
 .../knowlab-app/knowlab-backend/redis/workload.yaml        |  4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml      | 14 +++++++-------
 .../knowlab-app/knowlab-web-frontend/image.lock.yaml       |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml         |  4 ++--
 .../knowmart-app/knowmart-admin-frontend/image.lock.yaml   |  4 ++--
 .../knowmart-app/knowmart-admin-frontend/workload.yaml     |  4 ++--
 .../knowmart-app/knowmart-backend/identity/workload.yaml   |  4 ++--
 .../knowmart-app/knowmart-backend/image.lock.yaml          |  6 +++---
 .../knowbase-user-data-purchase-identity/workload.yaml     |  4 ++--
 .../knowmart-app/knowmart-backend/migration/workload.yaml  |  6 +++---
 .../knowmart-app/knowmart-backend/rabbitmq/workload.yaml   |  4 ++--
 .../knowmart-app/knowmart-backend/redis/workload.yaml      |  4 ++--
 .../knowmart-app/knowmart-backend/runtime/workload.yaml    |  8 ++++----
 .../knowmart-app/knowmart-web-frontend/image.lock.yaml     |  4 ++--
 .../knowmart-app/knowmart-web-frontend/workload.yaml       |  4 ++--
 45 files changed, 110 insertions(+), 110 deletions(-)
```
```diff
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
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '8527273db217d7d2b79ab9aa7b2e246011c2733c'}
+            - {name: DEPLOYMENT_ID, value: 'da892497525676dc35894e7c009f05a6851f568c'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-4ef85196251efa1e"
+  DEPLOYMENT_ID: "knowbench-backend-e5481cf62fe34a64"
@@ -136,7 +136,7 @@ spec:
@@ -208,7 +208,7 @@ spec:
@@ -269,7 +269,7 @@ spec:
@@ -326,7 +326,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-5294863336348591"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-4c850db17a916b31"}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-cc2c423463bcb934"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-d78adb9cbdf2d070"}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
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
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:9fbf666b231c8bba15f473521bdcee1eb08a9322e90868cd4140e6834d92eb18
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: d2f6a99fdfcb106d0be38bb1a6ab9e4eb02e2945
pointer-commit a8160a6f25285860501b3530310259f7c923342b
tag release-20261103-9
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

### 11-check-knowmart.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-67 推送成功后可删。
