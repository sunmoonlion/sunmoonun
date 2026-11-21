# release #100：统一登记十项函数与独立指令孵化合并发布，脚本开关保持关闭

- 时间：2026-11-21T22:08:29+08:00；分支 function-registry-release-20261121；目标 knowbase, knowbench, knowlab, sandbox；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/100/）
- 提交：deploy 31518fe902d0d42857763e7f7d8b9351318a2c5d；指针 6cd934db9598616250af946a785ba0f19ef989b6；tag release-20261121-2；批准：批准人 admin  2026-11-21T21:57:51+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index a85ab0b3e..097aa5c70 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -22,28 +22,28 @@ applications:
     admin_parent_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
     admin_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
   knowbase:
-    parent_revision: c9ed334702e3dd9e2fd0fd4842b923947d9ed2ea
-    backend_parent_revision: b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b
-    backend_revision: b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b
+    parent_revision: 6f041372c0dd922bf81f08a8caa70db435b61f7a
+    backend_parent_revision: 5563cc79fd3da76f3bf15707afb049707e11b714
+    backend_revision: 5563cc79fd3da76f3bf15707afb049707e11b714
     web_parent_revision: 884d235418f63676a88002978bf99bd99112cdb1
     web_revision: 884d235418f63676a88002978bf99bd99112cdb1
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: 822656ecae71fe5f35e928fb45d7a1b517da73f5
-    backend_parent_revision: a3c21a487d318f5a512b71bc6c136f0235275afa
-    backend_revision: a3c21a487d318f5a512b71bc6c136f0235275afa
-    web_parent_revision: 4a49dfd8fb1b1ad54fd3969dcdd8b641d18ccf51
-    web_revision: 4a49dfd8fb1b1ad54fd3969dcdd8b641d18ccf51
-    admin_parent_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
-    admin_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
+    parent_revision: a5a251432107b7ca3e48813d26699dee57f9e5d1
+    backend_parent_revision: e2dc7252c7031c183dc1d2882f013001b267ab15
+    backend_revision: e2dc7252c7031c183dc1d2882f013001b267ab15
+    web_parent_revision: b15ac0a232ed4ff7ccb43eee8ae60e7e2e8f0f11
+    web_revision: b15ac0a232ed4ff7ccb43eee8ae60e7e2e8f0f11
+    admin_parent_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
+    admin_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 386fed38f7e1d85cb13f5ce819d930b2d0bf10b4
-    backend_parent_revision: 457932623d2410b61432a050376da973c814fbad
-    backend_revision: 457932623d2410b61432a050376da973c814fbad
-    web_parent_revision: 3f59f9c77ba772f0b03d9edd29061f81f8c0b388
-    web_revision: 3f59f9c77ba772f0b03d9edd29061f81f8c0b388
+    parent_revision: 306948df928494526295c1f0f50185b78ff81540
+    backend_parent_revision: e469e4e2ab6d18832db36ea99abfdc6578a07431
+    backend_revision: e469e4e2ab6d18832db36ea99abfdc6578a07431
+    web_parent_revision: b63d3a882682f86b81fd252765a9df7784263a41
+    web_revision: b63d3a882682f86b81fd252765a9df7784263a41
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
     admin_revision: 89fe3ac1f6178018186584db7542f11102896381
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:3f1e6f47c227f8e000023ed463c21c1045546fba62df06a19b23f1f51e2e0779 source_revision: 5563cc79fd3da76f3bf15707afb049707e11b714 
gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml: digest: sha256:4aadaff728ec0f5d0f59636c5e5e8739e4e384d0561fa07d1102a3a429654681 source_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:a386d92d9d8097c5234c7aaecf12e54a881f52a7bb9d52ee797f78293fba4107 source_revision: e2dc7252c7031c183dc1d2882f013001b267ab15 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:1ed3908f40c298ae66347bad936f844addf2b60b0146ce3e815b93b057048c49 source_revision: b15ac0a232ed4ff7ccb43eee8ae60e7e2e8f0f11 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:2ad8e529aa58847702e5e561a88a28e598917752073af41a236fff26b39c3e77 source_revision: e469e4e2ab6d18832db36ea99abfdc6578a07431 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:74e993c438848deebde4be7e02d2a31d6ecbea1580f398913910bb6bead1e7e4 source_revision: b63d3a882682f86b81fd252765a9df7784263a41 
gitops/components/sandbox-platform/provisioner/image.lock.yaml: digest: sha256:9833097128c08b6a291b9a439867da364fbbb1a279dddf3aaab4c794f34f165f source_revision: e5e104a2e7928c74dbf5fd360760bb9f5f38b647 
gitops/components/sandbox-platform/sandbox/image.lock.yaml: digest: sha256:61508ffc4b8fcb31beb7cf7a75b0a4104da0e21f387659266b1a73e0d6ef54b7 source_revision: e5e104a2e7928c74dbf5fd360760bb9f5f38b647 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-backend/identity/workload.yaml        |  4 +--
 .../knowbase-app/knowbase-backend/image.lock.yaml  |  6 ++--
 .../knowbase-backend/migration/workload.yaml       |  6 ++--
 .../knowbase-backend/rabbitmq/workload.yaml        |  4 +--
 .../knowbase-backend/redis/workload.yaml           |  4 +--
 .../knowbase-backend/runtime/kustomization.yaml    |  1 +
 .../knowbase-backend/runtime/workload.yaml         | 22 ++++++++-----
 .../knowbench-admin-frontend/image.lock.yaml       |  6 ++--
 .../knowbench-admin-frontend/workload.yaml         |  4 +--
 .../knowbench-backend/identity/workload.yaml       |  4 +--
 .../knowbench-backend/image.lock.yaml              |  6 ++--
 .../workload.yaml                                  |  4 +--
 .../knowbase-user-data-read-identity/workload.yaml |  4 +--
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 +--
 .../workload.yaml                                  |  4 +--
 .../knowmart-catalog-identity/workload.yaml        |  4 +--
 .../knowmart-demand-identity/workload.yaml         |  4 +--
 .../knowmart-summon-identity/workload.yaml         |  4 +--
 .../knowbench-backend/migration/workload.yaml      |  8 ++---
 .../platform-computer/workload.yaml                |  4 +--
 .../knowbench-backend/rabbitmq/workload.yaml       |  4 +--
 .../knowbench-backend/redis/workload.yaml          |  4 +--
 .../knowbench-backend/runtime/kustomization.yaml   |  1 +
 .../knowbench-backend/runtime/workload.yaml        | 37 ++++++++++++++++------
 .../service-identity/workload.yaml                 |  4 +--
 .../knowbench-web-frontend/image.lock.yaml         |  6 ++--
 .../knowbench-web-frontend/workload.yaml           |  4 +--
 .../knowlab-backend/identity/workload.yaml         |  4 +--
 .../knowlab-app/knowlab-backend/image.lock.yaml    |  6 ++--
 .../workload.yaml                                  |  4 +--
 .../workload.yaml                                  |  4 +--
 .../workload.yaml                                  |  4 +--
 .../knowbase-user-data-read-identity/workload.yaml |  4 +--
 .../knowbench-incubate-identity/workload.yaml      |  4 +--
 .../knowbench-testrun-identity/workload.yaml       |  4 +--
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 +--
 .../knowmart-deliver-identity/workload.yaml        |  4 +--
 .../knowlab-backend/migration/workload.yaml        |  6 ++--
 .../knowlab-backend/rabbitmq/workload.yaml         |  4 +--
 .../knowlab-backend/redis/workload.yaml            |  4 +--
 .../knowlab-backend/runtime/workload.yaml          | 14 ++++----
 .../knowlab-web-frontend/image.lock.yaml           |  6 ++--
 .../knowlab-app/knowlab-web-frontend/workload.yaml |  4 +--
 .../sandbox-platform/provisioner/image.lock.yaml   |  6 ++--
 .../sandbox-platform/provisioner/workload.yaml     |  6 ++--
 .../sandbox-platform/sandbox/image.lock.yaml       |  6 ++--
 46 files changed, 146 insertions(+), 119 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -298,7 +298,7 @@ spec:
@@ -312,7 +312,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b'}
+            - {name: DEPLOYMENT_ID, value: '5563cc79fd3da76f3bf15707afb049707e11b714'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/kustomization.yaml
@@ -6,3 +6,4 @@ resources:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-ea82f12d44b25e4b"
+  DEPLOYMENT_ID: "knowbase-backend-3f1e6f47c227f8e0"
@@ -44,6 +44,12 @@ data:
+  KNOWBENCH_INTERNAL_URL: https://knowbench-tls.app-platform-dev.svc.cluster.local/api/internal/v1/knowbot-runtime
+  KNOWBENCH_FUNCTION_PUBLISH_SERVICE_APPLICATION: "sunmoonai-knowbase-knowbench-function-publish"
+  KNOWBENCH_FUNCTION_PUBLISH_SERVICE_CLIENT_ID: "sunmoon-knowbase-knowbench-function-publish"
+  KNOWBENCH_FUNCTION_PUBLISH_SERVICE_SCOPE: "knowbench:function-publish"
+  KNOWBENCH_FUNCTION_PUBLISH_SERVICE_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  KNOWBENCH_FUNCTION_PUBLISH_SERVICE_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
@@ -139,7 +145,7 @@ spec:
@@ -149,7 +155,7 @@ spec:
@@ -208,7 +214,7 @@ spec:
@@ -218,7 +224,7 @@ spec:
@@ -271,7 +277,7 @@ spec:
@@ -281,7 +287,7 @@ spec:
@@ -407,7 +413,7 @@ metadata: {name: knowbase-service-https-out, namespace: app-platform-dev}
-      - {key: app.kubernetes.io/name, operator: In, values: [knowbase-api]}
+      - {key: app.kubernetes.io/name, operator: In, values: [knowbase-api, knowbase-worker]}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-90d165c1f0dc5f83"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-4aadaff728ec0f5d"}
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
-            - {name: DEPLOYMENT_ID, value: 'a3c21a487d318f5a512b71bc6c136f0235275afa'}
+            - {name: DEPLOYMENT_ID, value: 'e2dc7252c7031c183dc1d2882f013001b267ab15'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261121_0053'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261121_0054'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/platform-computer/workload.yaml
@@ -97,7 +97,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:83c04c4325342e5aee542b253bf9f4a785bd27caf1b2b0c85dfe2045c5da7e15
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 31518fe902d0d42857763e7f7d8b9351318a2c5d
pointer-commit 6cd934db9598616250af946a785ba0f19ef989b6
tag release-20261121-2
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
kustomization.kustomize.toolkit.fluxcd.io/knowbase-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-knowbench-function-publish-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-provider condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-web condition met
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

### 11-check-knowbase.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=57   changed=1    unreachable=0    failed=0    skipped=17   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-100 推送成功后可删。
