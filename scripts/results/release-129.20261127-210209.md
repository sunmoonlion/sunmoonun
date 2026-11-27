# release #129：工坊创建删除与专家匹配澄清侧栏体验合并补发

- 时间：2026-11-27T21:02:09+08:00；分支 studio-match-hotfix-20261127；目标 knowlab, knowbench；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/129/）
- 提交：deploy ea4f89b537aaba604594f1b3779ff6c53991175d；指针 ed7ef33e1eb3585d317021c2c8c9b21b6ed07952；tag release-20261127-2；批准：批准人 admin  2026-11-27T20:55:50+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:b3a18979fa6ef1be6f6ceb64bb3accca5dd279386424069078f69631d0b4b4e0 source_revision: ecc32a199eff196e2be53e3164e28d5a0252c433 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:e36be3c8666904aac2b6805624ffecd4431babf89ccf42dbcbcfe97519556325 source_revision: b089eb187c3a63d643a91129287c23b6eafe4956 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:a3d88158fca704cca191c8ad584d6020b349b5eab4a302c46534432811bd9249 source_revision: d5b9477ec242db24e2b6bfffb34c0c799c4ba402 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-app/knowbench-web-frontend/image.lock.yaml          | 6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml            | 4 ++--
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
 .../app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml | 6 +++---
 .../app-platform/knowlab-app/knowlab-web-frontend/workload.yaml   | 4 ++--
 18 files changed, 42 insertions(+), 42 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-62bdb0138d3404d3"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-b3a18979fa6ef1be"}
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
-            - {name: DEPLOYMENT_ID, value: '7e67b5872bdfb048939601be93188014d4445f27'}
+            - {name: DEPLOYMENT_ID, value: 'b089eb187c3a63d643a91129287c23b6eafe4956'}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowlab-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowlab-backend-71f068741cfcc802"
+  DEPLOYMENT_ID: "knowlab-backend-e36be3c8666904aa"
@@ -113,7 +113,7 @@ spec:
@@ -181,7 +181,7 @@ spec:
@@ -244,7 +244,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-99b84f4aa3e01f9c"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-a3d88158fca704cc"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:a36b4fd8edc1e21029367c163f24ad1a93cd263d8d4352a7e0b6558552d2ca67
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: ea4f89b537aaba604594f1b3779ff6c53991175d
pointer-commit ed7ef33e1eb3585d317021c2c8c9b21b6ed07952
tag release-20261127-2
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-129 推送成功后可删。
