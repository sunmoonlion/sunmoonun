# release #82：按所有者要求向全部登录账号开放Wind，保持各自确认与私有入库

- 时间：2026-11-04T11:29:12+08:00；分支 release/wind-runtime-activation；目标 knowfeed；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/82/）
- 提交：deploy 96e0c1778a73478c97d05b2f64d15ad1985d3514；指针 f86f1dda15ee4d411881e6e9eff9925e951f051c；tag release-20261104-10；批准：批准人 admin  2026-11-04T11:23:45+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml: digest: sha256:cf613373679c13a221db8f93cb469af93cbfcf3c5999f09f636fe070ff7abd7e source_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:abbadcc4a6f2ae3758dc63d7d75ec965470237f198c55228490cc6b896ea7ad3 source_revision: 15606aaf039fb39dfa81b4489760a94c9eae4f8e 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowfeed-app/knowfeed-admin-frontend/image.lock.yaml          | 6 +++---
 .../knowfeed-app/knowfeed-admin-frontend/workload.yaml            | 4 ++--
 .../knowfeed-app/knowfeed-backend/identity/workload.yaml          | 4 ++--
 .../app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml    | 6 +++---
 .../knowbase-user-data-supply-identity/workload.yaml              | 4 ++--
 .../knowfeed-app/knowfeed-backend/migration/workload.yaml         | 6 +++---
 .../knowfeed-app/knowfeed-backend/rabbitmq/workload.yaml          | 4 ++--
 .../knowfeed-app/knowfeed-backend/redis/workload.yaml             | 4 ++--
 .../knowfeed-app/knowfeed-backend/runtime/workload.yaml           | 8 ++++----
 .../knowfeed-app/knowfeed-backend/service-identity/workload.yaml  | 4 ++--
 10 files changed, 25 insertions(+), 25 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowfeed-admin-frontend-1b75696e964dfefd"}
+            - {name: DEPLOYMENT_ID, value: "knowfeed-admin-frontend-cf613373679c13a2"}
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/knowbase-user-data-supply-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '2bc17f152d2fc2261a731d0cbbe4bac7165c97ec'}
+            - {name: DEPLOYMENT_ID, value: '15606aaf039fb39dfa81b4489760a94c9eae4f8e'}
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowfeed-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowfeed-backend-4cf0841eb3d9814b"
+  DEPLOYMENT_ID: "knowfeed-backend-abbadcc4a6f2ae37"
@@ -93,7 +93,7 @@ spec:
@@ -160,7 +160,7 @@ spec:
@@ -223,7 +223,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:2eb2e420624e457908b2f1db8990f8fa5a69bfb3d688dbb93da64be6fa3389e8
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 96e0c1778a73478c97d05b2f64d15ad1985d3514
pointer-commit f86f1dda15ee4d411881e6e9eff9925e951f051c
tag release-20261104-10
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
```

## 检查（11-check-*.log 尾部）

### 11-check-knowfeed.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=54   changed=0    unreachable=0    failed=0    skipped=20   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-82 推送成功后可删。
