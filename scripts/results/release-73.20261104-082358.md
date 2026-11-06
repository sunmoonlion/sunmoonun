# release #73：发布勾稽权益抽取与重复检索修复

- 时间：2026-11-04T08:23:59+08:00；分支 release/recovery-methods；目标 knowfeed, knowbench；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/73/）
- 提交：deploy b187709ccab3eef6f29f63a2f509881fee9ec53d；指针 d5e03b7b1730244fcffd1f7c36ad9f8d88486b77；tag release-20261104-5；批准：批准人 admin  2026-11-04T08:17:07+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:4cfa3ab619f75b189bccc7b1e9c5cd54e189ff58d1a2969ff40db6a9020ee540 source_revision: 8a662f18f80f3bb731293c57f78d8086a4facc57 
gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml: digest: sha256:dc414340d3e24bdd3137a85e497b85f571288affbe42df744bd145220b437efa source_revision: a290cde1ffdf1abc3acc2885f23503057a8034f7 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:2e9368ed81b7579a0c8745763e0b23ca527d0dcea02ba0ce8e22bcad4491fc53 source_revision: c4df6c87fd607669bdd0acd183939b88f4c3f511 
gitops/components/app-platform/knowfeed-app/knowfeed-web-frontend/image.lock.yaml: digest: sha256:2d3dfcb560e0af6eff22bcac3057bc9b4d450aa72e6bb69f376bdedf9cb9694f source_revision: bb03f1ac21ffea0bc4e71dd5efc678256dd354ab 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-app/knowbench-backend/identity/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml            |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml           |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml             |  4 ++--
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
 .../knowfeed-app/knowfeed-admin-frontend/image.lock.yaml       |  4 ++--
 .../knowfeed-app/knowfeed-admin-frontend/workload.yaml         |  4 ++--
 .../knowfeed-app/knowfeed-backend/identity/workload.yaml       |  4 ++--
 .../app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml |  6 +++---
 .../knowbase-user-data-supply-identity/workload.yaml           |  4 ++--
 .../knowfeed-app/knowfeed-backend/migration/workload.yaml      |  6 +++---
 .../knowfeed-app/knowfeed-backend/rabbitmq/workload.yaml       |  4 ++--
 .../knowfeed-app/knowfeed-backend/redis/workload.yaml          |  4 ++--
 .../knowfeed-app/knowfeed-backend/runtime/workload.yaml        |  8 ++++----
 .../knowfeed-backend/service-identity/workload.yaml            |  4 ++--
 .../knowfeed-app/knowfeed-web-frontend/image.lock.yaml         |  4 ++--
 .../knowfeed-app/knowfeed-web-frontend/workload.yaml           |  4 ++--
 26 files changed, 61 insertions(+), 61 deletions(-)
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
-            - {name: DEPLOYMENT_ID, value: 'f2404150af37935c9a368405ac939ef7c0ff4bb1'}
+            - {name: DEPLOYMENT_ID, value: '8a662f18f80f3bb731293c57f78d8086a4facc57'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-580854b909d97649"
+  DEPLOYMENT_ID: "knowbench-backend-4cfa3ab619f75b18"
@@ -136,7 +136,7 @@ spec:
@@ -208,7 +208,7 @@ spec:
@@ -269,7 +269,7 @@ spec:
@@ -326,7 +326,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowfeed-admin-frontend-6a64e0c20ed73c17"}
+            - {name: DEPLOYMENT_ID, value: "knowfeed-admin-frontend-dc414340d3e24bdd"}
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
-            - {name: DEPLOYMENT_ID, value: 'df981b29762a2156f8879d832c1eb7cbe23d856c'}
+            - {name: DEPLOYMENT_ID, value: 'c4df6c87fd607669bdd0acd183939b88f4c3f511'}
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowfeed-app/knowfeed-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowfeed-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowfeed-backend-a2bda94b46c5ab38"
+  DEPLOYMENT_ID: "knowfeed-backend-2e9368ed81b7579a"
@@ -93,7 +93,7 @@ spec:
@@ -159,7 +159,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:eeb5e58c7d33d6f37b23abc36a1772af2279a702b1cacf771048f3fc80410b7d
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: b187709ccab3eef6f29f63a2f509881fee9ec53d
pointer-commit d5e03b7b1730244fcffd1f7c36ad9f8d88486b77
tag release-20261104-5
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-73 推送成功后可删。
