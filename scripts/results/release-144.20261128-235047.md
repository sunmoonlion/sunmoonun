# release #144：巨潮公告轮询跨限速窗口续查

- 时间：2026-11-28T23:50:47+08:00；分支 luna-release-587；目标 knowfeed；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/144/）
- 提交：deploy 5da325cdf597cc54cd373312073967e08b0f606d；指针 1cb415a6dc8e27f30d5bf03c014fc3421c433a99；tag release-20261128-7；批准：批准人 admin  2026-11-28T23:45:45+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:48f36e900dff008785dfedd8297601906d7ec58b3911eac55d6268d0ddd3ef72 source_revision: 9c6e9a7d73e910b5888295b7a310ee5054d9021d 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowfeed-app/knowfeed-backend/identity/workload.yaml          | 4 ++--
 .../app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml    | 6 +++---
 .../knowbase-user-data-supply-identity/workload.yaml              | 4 ++--
 .../knowfeed-app/knowfeed-backend/migration/workload.yaml         | 6 +++---
 .../knowfeed-app/knowfeed-backend/rabbitmq/workload.yaml          | 4 ++--
 .../knowfeed-app/knowfeed-backend/redis/workload.yaml             | 4 ++--
 .../knowfeed-app/knowfeed-backend/runtime/workload.yaml           | 8 ++++----
 .../knowfeed-app/knowfeed-backend/service-identity/workload.yaml  | 4 ++--
 8 files changed, 20 insertions(+), 20 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/identity/workload.yaml
@@ -300,7 +300,7 @@ spec:
@@ -314,7 +314,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/knowbase-user-data-supply-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '152df3b3aae86605036035f0429c22c54a87e96c'}
+            - {name: DEPLOYMENT_ID, value: '9c6e9a7d73e910b5888295b7a310ee5054d9021d'}
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowfeed-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowfeed-backend-788f8376c1e6682b"
+  DEPLOYMENT_ID: "knowfeed-backend-48f36e900dff0087"
@@ -94,7 +94,7 @@ spec:
@@ -161,7 +161,7 @@ spec:
@@ -224,7 +224,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:e423158eb551743a6724f806672c8df6de25bf61306271fdd01ddbd128d98ef4
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 5da325cdf597cc54cd373312073967e08b0f606d
pointer-commit 1cb415a6dc8e27f30d5bf03c014fc3421c433a99
tag release-20261128-7
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-144 推送成功后可删。
