# release #130：专家交付编译器与双入口审阅补发

- 时间：2026-11-27T21:24:52+08:00；分支 compiler-dual-entry-hotfix-20261127；目标 knowlab, knowbench；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/130/）
- 提交：deploy c3d41f0510851de21d94827152613eed6c645ad8；指针 fc85c18d30d32ba33e39d5d140cf39e27e661ef8；tag release-20261127-3；批准：批准人 admin  2026-11-27T21:18:03+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:82f783e0cac9dd27a986935a9e78cb29da2d2c6386fab8c66ec70a4399a37988 source_revision: 64339ceef3a8d2714c794484e0e38b3980056411 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:6b44408730032981e9b1635aad9edef7b9e19846d5f5e4da8840040dc098089f source_revision: 171e1b5942554c00b8b9138cef4dac0d810f776d 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:c123f2f3c39b1e02908fb2e7bafd88e3715e99a6dc9c00389f162f90c69d39e2 source_revision: 0a2edf3070c08394cf11946b5c2bb2ba27f6b146 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:ab2e7c3329bff54503f23166f5d7e2c280eb5e3902e5a34f35e7c5f8b1f7ec83 source_revision: e9266eb554b3ac99f5bf3625c69b736d523c6eb6 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-app/knowbench-backend/identity/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml            |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml           |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml             |  4 ++--
 .../knowbench-function-publish-identity/workload.yaml          |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml              |  4 ++--
 .../knowlab-incubation-request-identity/workload.yaml          |  4 ++--
 .../knowbench-backend/knowmart-catalog-identity/workload.yaml  |  4 ++--
 .../knowbench-backend/knowmart-demand-identity/workload.yaml   |  4 ++--
 .../knowbench-backend/knowmart-summon-identity/workload.yaml   |  4 ++--
 .../knowbench-app/knowbench-backend/migration/workload.yaml    |  6 +++---
 .../knowbench-app/knowbench-backend/rabbitmq/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/redis/workload.yaml        |  4 ++--
 .../knowbench-app/knowbench-backend/runtime/workload.yaml      | 10 +++++-----
 .../knowbench-backend/service-identity/workload.yaml           |  4 ++--
 .../knowbench-app/knowbench-web-frontend/image.lock.yaml       |  6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml         |  4 ++--
 .../knowlab-app/knowlab-backend/identity/workload.yaml         |  4 ++--
 .../app-platform/knowlab-app/knowlab-backend/image.lock.yaml   |  6 +++---
 .../knowbase-user-data-directory-identity/workload.yaml        |  4 ++--
 .../knowbase-user-data-grant-test-identity/workload.yaml       |  4 ++--
 .../knowbase-user-data-output-identity/workload.yaml           |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml             |  4 ++--
 .../knowlab-backend/knowbench-incubate-identity/workload.yaml  |  4 ++--
 .../knowlab-backend/knowbench-testrun-identity/workload.yaml   |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml              |  4 ++--
 .../knowlab-backend/knowmart-deliver-identity/workload.yaml    |  4 ++--
 .../knowlab-app/knowlab-backend/migration/workload.yaml        |  6 +++---
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml         |  4 ++--
 .../knowlab-app/knowlab-backend/redis/workload.yaml            |  4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml          |  8 ++++----
 .../knowlab-app/knowlab-web-frontend/image.lock.yaml           |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml             |  4 ++--
 33 files changed, 77 insertions(+), 77 deletions(-)
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
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '2ec1c338c2f1b3941c44f55470fa50a4f887c040'}
+            - {name: DEPLOYMENT_ID, value: '64339ceef3a8d2714c794484e0e38b3980056411'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-24f874af5f99375e"
+  DEPLOYMENT_ID: "knowbench-backend-82f783e0cac9dd27"
@@ -165,7 +165,7 @@ spec:
@@ -237,7 +237,7 @@ spec:
@@ -298,7 +298,7 @@ spec:
@@ -355,7 +355,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-b3a18979fa6ef1be"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-6b44408730032981"}
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
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:8ed98e11aa5a2566f204faa92b8135b8fec2d475013306c7f7cf00d2a820e4f9
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: c3d41f0510851de21d94827152613eed6c645ad8
pointer-commit fc85c18d30d32ba33e39d5d140cf39e27e661ef8
tag release-20261127-3
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-130 推送成功后可删。
