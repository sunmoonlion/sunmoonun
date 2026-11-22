# release #106：请专家入口与回炉及Kimi指令复核同一版发布，全量入口保持关闭

- 时间：2026-11-22T17:31:08+08:00；分支 expert-entry-release-20261122；目标 knowbench, knowlab；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/106/）
- 提交：deploy 284913fbcf15159c21318e90ef3f37f6d4ddbea7；指针 fb08ce5f953780f94c61c83ef714c1673dd4d8e8；tag release-20261122-4；批准：批准人 admin  2026-11-22T17:23:03+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 5d26ce1a2..ff3be2f71 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -30,20 +30,20 @@ applications:
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: 9af9371f938fcb83733050b59683cbc26d43dea5
-    backend_parent_revision: df93384f3f70a268d84c5c0db83deb8ff16ccc88
-    backend_revision: df93384f3f70a268d84c5c0db83deb8ff16ccc88
-    web_parent_revision: 87598bd70ac2865cb9deba20571cf56759c13366
-    web_revision: 87598bd70ac2865cb9deba20571cf56759c13366
+    parent_revision: 2a20aea1ee2ff018d2e21ad44641c6afbcca5165
+    backend_parent_revision: 60ea2f46a49e73528c14c3483f137e63c4395ad7
+    backend_revision: 60ea2f46a49e73528c14c3483f137e63c4395ad7
+    web_parent_revision: 65089bcbba7be4014fd599f65886c8373b5e43b8
+    web_revision: 65089bcbba7be4014fd599f65886c8373b5e43b8
     admin_parent_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
     admin_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: a7dae5b83b63cebbe575ca708b1f2a9f28bdd0c0
-    backend_parent_revision: f14182fa724b64f2a5170f517c8786655d29ad27
-    backend_revision: f14182fa724b64f2a5170f517c8786655d29ad27
-    web_parent_revision: 9edf1a0051b8bd7c1356b14aad296033113fe14d
-    web_revision: 9edf1a0051b8bd7c1356b14aad296033113fe14d
+    parent_revision: 677af26c3c7b04e980d513df53a4af10316eae36
+    backend_parent_revision: 1d2e24290a9e84a369a043d97741c57215eb61be
+    backend_revision: 1d2e24290a9e84a369a043d97741c57215eb61be
+    web_parent_revision: 76c6bfd804ce4a5c5bf04a1435fc50c0e4601cf2
+    web_revision: 76c6bfd804ce4a5c5bf04a1435fc50c0e4601cf2
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
     admin_revision: 89fe3ac1f6178018186584db7542f11102896381
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:bbeafed4ca61bf2cc222df5e311b623583cdb00a678c89f979c5be06dfec0a1a source_revision: 60ea2f46a49e73528c14c3483f137e63c4395ad7 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:73213c3a3edf09d42f8c8ec28b1600232be3c6cdf78e364eb8d8fd94b4fc2261 source_revision: 65089bcbba7be4014fd599f65886c8373b5e43b8 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:4f735a46cc6219a563b095d37a44e1a0a00af3fa2802ce6a9395eabe99a2db12 source_revision: 1d2e24290a9e84a369a043d97741c57215eb61be 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:05b8d403de3a06ba3d91cd5987975775d5fd6f38c6dae5594948cbf966eda0b6 source_revision: 76c6bfd804ce4a5c5bf04a1435fc50c0e4601cf2 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-backend/identity/workload.yaml       |  4 ++--
 .../knowbench-backend/image.lock.yaml              |  6 +++---
 .../workload.yaml                                  |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml |  4 ++--
 .../workload.yaml                                  |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 ++--
 .../workload.yaml                                  |  4 ++--
 .../knowmart-catalog-identity/workload.yaml        |  4 ++--
 .../knowmart-demand-identity/workload.yaml         |  4 ++--
 .../knowmart-summon-identity/workload.yaml         |  4 ++--
 .../knowbench-backend/migration/workload.yaml      |  6 +++---
 .../knowbench-backend/rabbitmq/workload.yaml       |  4 ++--
 .../knowbench-backend/redis/workload.yaml          |  4 ++--
 .../knowbench-backend/runtime/workload.yaml        | 24 +++++++++++++---------
 .../service-identity/workload.yaml                 |  4 ++--
 .../knowbench-web-frontend/image.lock.yaml         |  6 +++---
 .../knowbench-web-frontend/workload.yaml           |  4 ++--
 .../knowlab-backend/identity/workload.yaml         |  4 ++--
 .../knowlab-app/knowlab-backend/image.lock.yaml    |  6 +++---
 .../workload.yaml                                  |  4 ++--
 .../workload.yaml                                  |  4 ++--
 .../workload.yaml                                  |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml |  4 ++--
 .../knowbench-incubate-identity/workload.yaml      |  4 ++--
 .../knowbench-testrun-identity/workload.yaml       |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 ++--
 .../knowmart-deliver-identity/workload.yaml        |  4 ++--
 .../knowlab-backend/migration/workload.yaml        |  6 +++---
 .../knowlab-backend/rabbitmq/workload.yaml         |  4 ++--
 .../knowlab-backend/redis/workload.yaml            |  4 ++--
 .../knowlab-backend/runtime/workload.yaml          |  8 ++++----
 .../knowlab-web-frontend/image.lock.yaml           |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml |  4 ++--
 33 files changed, 86 insertions(+), 82 deletions(-)
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
-            - {name: DEPLOYMENT_ID, value: 'df93384f3f70a268d84c5c0db83deb8ff16ccc88'}
+            - {name: DEPLOYMENT_ID, value: '60ea2f46a49e73528c14c3483f137e63c4395ad7'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-3ed02f9d3d64e347"
+  DEPLOYMENT_ID: "knowbench-backend-bbeafed4ca61bf2c"
@@ -115,8 +115,12 @@ data:
+  EXPERT_UNIFIED_ENTRY_ENABLED: "false"
+  EXPERT_PLANNING_OWNERS: "[\"721f2c10-db3f-4ca4-b6bf-093bb4420ea7\"]"
+  WORKBENCH_INSTRUCTION_ROUTES: "[{\"provider\":\"kimi\",\"model\":\"kimi-k3\",\"base_url\":\"https://api.moonshot.cn/v1\",\"price_key\":\"kimi-k3\",\"context_tokens\":1048576,\"output_tokens\":8192}]"
+  WORKBENCH_REVIEW_ROUTES: "[{\"provider\":\"kimi\",\"model\":\"kimi-k3\",\"family\":\"kimi\",\"price_key\":\"kimi-k3\"}]"
-  WORKBENCH_FIXED_AS_PLAN_OWNERS: "[]"
+  WORKBENCH_FIXED_AS_PLAN_OWNERS: "[\"721f2c10-db3f-4ca4-b6bf-093bb4420ea7\"]"
@@ -150,7 +154,7 @@ spec:
@@ -160,7 +164,7 @@ spec:
@@ -222,7 +226,7 @@ spec:
@@ -232,7 +236,7 @@ spec:
@@ -283,7 +287,7 @@ spec:
@@ -293,7 +297,7 @@ spec:
@@ -340,7 +344,7 @@ spec:
@@ -350,7 +354,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-2850fd13ae5fb102"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-73213c3a3edf09d4"}
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
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:86115dcb5b5dac4843a054ae52da8df799259025b72c1ec542eb712e9d7ce61b
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 284913fbcf15159c21318e90ef3f37f6d4ddbea7
pointer-commit fb08ce5f953780f94c61c83ef714c1673dd4d8e8
tag release-20261122-4
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-106 推送成功后可删。
