# release #63：测试确认后数据授权编号修复

- 时间：2026-11-03T09:25:59+08:00；分支 release/recovery-methods；目标 knowlab；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/63/）
- 提交：deploy 8469a22a64902adbf23a3199f35c559fa9e5f6ba；指针 1eb504c5faab0f85712224c2816b487a1454c88b；tag release-20261103-5；批准：批准人 admin  2026-11-03T09:20:39+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:33e4e4648c37c1fc22f68c65269124e112bedee0b263542c52eafa8753d87fa6 source_revision: d9f13baa1228f7f678012b3e6021715a4dce9fe6 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowlab-app/knowlab-backend/identity/workload.yaml            | 4 ++--
 .../app-platform/knowlab-app/knowlab-backend/image.lock.yaml      | 6 +++---
 .../knowbase-user-data-directory-identity/workload.yaml           | 4 ++--
 .../knowbase-user-data-grant-test-identity/workload.yaml          | 4 ++--
 .../knowbase-user-data-output-identity/workload.yaml              | 4 ++--
 .../knowbase-user-data-read-identity/workload.yaml                | 4 ++--
 .../knowlab-backend/knowbench-incubate-identity/workload.yaml     | 4 ++--
 .../knowlab-backend/knowbench-testrun-identity/workload.yaml      | 4 ++--
 .../knowlab-backend/knowfeed-supply-demand-identity/workload.yaml | 4 ++--
 .../knowlab-backend/knowmart-deliver-identity/workload.yaml       | 4 ++--
 .../knowlab-app/knowlab-backend/migration/workload.yaml           | 6 +++---
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml            | 4 ++--
 .../app-platform/knowlab-app/knowlab-backend/redis/workload.yaml  | 4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml             | 8 ++++----
 14 files changed, 32 insertions(+), 32 deletions(-)
```
```diff
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
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbench-testrun-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowfeed-supply-demand-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowmart-deliver-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'c5d9f4e23612252de0303ee4b1a26c4f3c840d76'}
+            - {name: DEPLOYMENT_ID, value: 'd9f13baa1228f7f678012b3e6021715a4dce9fe6'}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowlab-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowlab-backend-fa9c6f449d6fd855"
+  DEPLOYMENT_ID: "knowlab-backend-33e4e4648c37c1fc"
@@ -113,7 +113,7 @@ spec:
@@ -181,7 +181,7 @@ spec:
@@ -244,7 +244,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:be25ae125bd4d0f0ec44f099a70f0405a603d046a4bc9ba9c62f5e687555711b
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 8469a22a64902adbf23a3199f35c559fa9e5f6ba
pointer-commit 1eb504c5faab0f85712224c2816b487a1454c88b
tag release-20261103-5
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
```

## 检查（11-check-*.log 尾部）

### 11-check-knowlab.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-63 推送成功后可删。
