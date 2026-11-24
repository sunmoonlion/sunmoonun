# release #119：方法目录、请专家入口与正式指令回执增量发布，沿用试验名单和报价

- 时间：2026-11-24T19:42:40+08:00；分支 method-entry-release-20261124；目标 knowmart, knowbench, knowlab；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/119/）
- 提交：deploy 08e2365eaaa9e3b033f5b7e838a11e225dbbe096；指针 81ae3c93302eb96489c5c8964d61a46cac2d74f3；tag release-20261124-5；批准：批准人 admin  2026-11-24T19:33:39+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:b5f96ca98c22be848b3caaa25b290758590772bdc654864717f86b22f4e02aab source_revision: e544b380689a4e4fc0e378c51aa1193acb8fa4ef 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:1be8c33b29c31274fbfb7f96fab50a0fabc7c40307c6a743715adc8f794063cc source_revision: 56a5f7ded75465583dac0262d4b7febae9ee59c7 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:466d29d6d59e8f5ea210620615f2ce911a5dda0b28eafb671e036886e0b56485 source_revision: f85f3d2ac53935c3f736b601d5421b1980815950 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:445cc7c5e575f1a015a8b5820830105e08d237ced723167d5d05fe9826040424 source_revision: db5870a093ee8b2f622a85e96cf42bcc87cb21a8 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:f4a8ab8ec5207ce6400bc6d8fb6694934290ce5ceb6149924375432b70c23489 source_revision: 410fc4633e107d7c8b6570dadb78b6632d0da9f6 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:bb7934c5aad51038ad4e912397881d1431fc7fc39045e178324013ba8e4b213b source_revision: db4cbd0b4b552c46d2371f6de4e8108d05e55bba 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
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
 .../knowmart-backend/identity/workload.yaml            |  4 ++--
 .../knowmart-app/knowmart-backend/image.lock.yaml      |  6 +++---
 .../knowbase-user-data-purchase-identity/workload.yaml |  4 ++--
 .../knowmart-backend/migration/workload.yaml           | 12 ++++++------
 .../knowmart-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowmart-app/knowmart-backend/redis/workload.yaml  |  4 ++--
 .../knowmart-backend/runtime/workload.yaml             | 16 ++++++++--------
 .../knowmart-app/knowmart-web-frontend/image.lock.yaml |  6 +++---
 .../knowmart-app/knowmart-web-frontend/workload.yaml   |  4 ++--
 42 files changed, 114 insertions(+), 114 deletions(-)
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
-            - {name: DEPLOYMENT_ID, value: 'a51757145093ead36d268c476e65d294900c108a'}
+            - {name: DEPLOYMENT_ID, value: 'e544b380689a4e4fc0e378c51aa1193acb8fa4ef'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261123_0061'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261124_0062'}
-        - {name: verify, configMap: {name: 'knowbench-schema-check-v15'}}
+        - {name: verify, configMap: {name: 'knowbench-schema-check-v16'}}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-a988f8bb69516acc"
+  DEPLOYMENT_ID: "knowbench-backend-b5f96ca98c22be84"
@@ -155,7 +155,7 @@ spec:
@@ -165,7 +165,7 @@ spec:
@@ -227,7 +227,7 @@ spec:
@@ -237,7 +237,7 @@ spec:
@@ -288,7 +288,7 @@ spec:
@@ -298,7 +298,7 @@ spec:
@@ -345,7 +345,7 @@ spec:
@@ -355,7 +355,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-c3d02b31256ed6b2"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-1be8c33b29c31274"}
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
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:470c70d0b53ad1ede8283b7afc7cbe7ac93bdca7a2828c4973c65fcd227c6a83
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 08e2365eaaa9e3b033f5b7e838a11e225dbbe096
pointer-commit 81ae3c93302eb96489c5c8964d61a46cac2d74f3
tag release-20261124-5
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-119 推送成功后可删。
