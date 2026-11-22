# release #104：增量审查修复发布 KnowBench、KnowLab 和沙箱。KnowBench 库版本升到 0055，含空页续查；脚本开关仍关闭

- 时间：2026-11-22T09:25:54+08:00；分支 review-release-20261122；目标 knowbench, knowlab, sandbox；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/104/）
- 提交：deploy 9b295a73c5c3f94c5dee75fb532d9f6b04c8d17f；指针 6d7e00d9452fad33c5a997890c6fa92de1e07f68；tag release-20261122-2；批准：批准人 admin  2026-11-22T09:17:40+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml: digest: sha256:223a35f3035ef71cd66541ecc63f002f00e3015e4a0b790f39f074f44c52db5e source_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:c26733cb0b83452a3092c9689cf15f0b1c91c59efd2c7600a3169c20ab205a8d source_revision: 701a82bf3cb5e9eae6b43510a2dff04c398a8d4b 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:9a10c9e397dcddec565cc31e8a625ce9c7310e1f7ea4e7a9721616d1707bf9df source_revision: d2e9e2d15dbdb21e7d08cae67229d16028452470 
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:f1bcd03485246b1587636f74b98b7d1daff01f7ff20d73d661eef4c42f236d92 source_revision: 89fe3ac1f6178018186584db7542f11102896381 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:b2e80c4e201569464f5c6b0c0db9b56b9952f292f96380715c2181f65495c693 source_revision: efa6aa6f7ef7c3ed4aedd9c873b4affd83b0c23a 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:bf919fccdced984d1fed4d741611f5d9297cf75e9af354bc7faefd2e36140675 source_revision: d373a3f556343b52940d3423640c16e87012ebdf 
gitops/components/sandbox-platform/provisioner/image.lock.yaml: digest: sha256:af0ba76f18e3c6341d4c0323b6ab5e97ce856f65be18452a9cd5db2545db38e4 source_revision: 99f497bf79946d9618533228640423e10143c460 
gitops/components/sandbox-platform/sandbox/image.lock.yaml: digest: sha256:c886456b1aed9cd50f161baaf9675be8d228431bde3fba5050bbe662d544489b source_revision: 99f497bf79946d9618533228640423e10143c460 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-admin-frontend/image.lock.yaml           |  4 ++--
 .../knowbench-admin-frontend/workload.yaml             |  4 ++--
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
 .../knowbench-backend/migration/workload.yaml          |  8 ++++----
 .../knowbench-backend/platform-computer/workload.yaml  |  4 ++--
 .../knowbench-backend/rabbitmq/workload.yaml           |  4 ++--
 .../knowbench-backend/redis/workload.yaml              |  4 ++--
 .../knowbench-backend/runtime/workload.yaml            | 18 +++++++++---------
 .../knowbench-backend/service-identity/workload.yaml   |  4 ++--
 .../knowbench-web-frontend/image.lock.yaml             |  6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/image.lock.yaml |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/workload.yaml   |  4 ++--
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
 .../sandbox-platform/provisioner/image.lock.yaml       |  6 +++---
 .../sandbox-platform/provisioner/workload.yaml         |  6 +++---
 .../sandbox-platform/sandbox/image.lock.yaml           |  6 +++---
 41 files changed, 101 insertions(+), 101 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-4aadaff728ec0f5d"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-223a35f3035ef71c"}
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
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'e2dc7252c7031c183dc1d2882f013001b267ab15'}
+            - {name: DEPLOYMENT_ID, value: '701a82bf3cb5e9eae6b43510a2dff04c398a8d4b'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261121_0054'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261121_0055'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/platform-computer/workload.yaml
@@ -97,7 +97,7 @@ spec:
@@ -110,7 +110,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-a386d92d9d8097c5"
+  DEPLOYMENT_ID: "knowbench-backend-c26733cb0b83452a"
@@ -150,7 +150,7 @@ spec:
@@ -160,7 +160,7 @@ spec:
@@ -222,7 +222,7 @@ spec:
@@ -232,7 +232,7 @@ spec:
@@ -283,7 +283,7 @@ spec:
@@ -293,7 +293,7 @@ spec:
@@ -340,7 +340,7 @@ spec:
@@ -350,7 +350,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-1ed3908f40c298ae"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-9a10c9e397dcddec"}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-b4a4def63b091d94"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:acbd31f0cf0202c0acaeb920ae1737ac987d9239ea0c8286e20c2b5ff6a9e4f7
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 9b295a73c5c3f94c5dee75fb532d9f6b04c8d17f
pointer-commit 6d7e00d9452fad33c5a997890c6fa92de1e07f68
tag release-20261122-2
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

### 11-check-sandbox.log
```text
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=23   changed=1    unreachable=0    failed=0    skipped=77   rescued=0    ignored=0   

make[2]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make[1]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-104 推送成功后可删。
