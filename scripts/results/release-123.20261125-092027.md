# release #123：三端退役旧专家入口与历史回执，沿用现场路由报价与库版本

- 时间：2026-11-25T09:20:28+08:00；分支 legacy-expert-retire-20261125；目标 knowbench, knowlab, knowmart；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/123/）
- 提交：deploy 6bc2630446c779a05972351251be5421982a1621；指针 5ac35b73277f7d02f89cb8ddcc6b5c6c3b7f54f5；tag release-20261125-1；批准：批准人 admin  2026-11-25T09:10:57+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 0759febc9..b86fade72 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -30,28 +30,28 @@ applications:
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: c14eca8ae07b8c6ebc92afb1a2cc2dca23a5b82e
-    backend_parent_revision: 644ca9be97de7825e7b0c01f1d869b6155b50e76
-    backend_revision: 644ca9be97de7825e7b0c01f1d869b6155b50e76
-    web_parent_revision: 56a5f7ded75465583dac0262d4b7febae9ee59c7
-    web_revision: 56a5f7ded75465583dac0262d4b7febae9ee59c7
+    parent_revision: 53ebdca24a34643f5ada0f425cf36419a8cb584f
+    backend_parent_revision: 984fd50157cef2a77752e853628adf72bf45760d
+    backend_revision: 984fd50157cef2a77752e853628adf72bf45760d
+    web_parent_revision: 6c96e4386477ec2aa08e509b157a4de0752ac428
+    web_revision: 6c96e4386477ec2aa08e509b157a4de0752ac428
     admin_parent_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
     admin_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 8a8af13f32c4d707ab9d1a5856a08b00bb4e01b9
-    backend_parent_revision: f85f3d2ac53935c3f736b601d5421b1980815950
-    backend_revision: f85f3d2ac53935c3f736b601d5421b1980815950
-    web_parent_revision: db5870a093ee8b2f622a85e96cf42bcc87cb21a8
-    web_revision: db5870a093ee8b2f622a85e96cf42bcc87cb21a8
+    parent_revision: 7c18a9e6bc915639c1006652dd2d9bace065437e
+    backend_parent_revision: 7d518645992d2ce26930db5a6cf43ad8082c6172
+    backend_revision: 7d518645992d2ce26930db5a6cf43ad8082c6172
+    web_parent_revision: b681780fdcf8446900516e1a2d8f19802aac0eee
+    web_revision: b681780fdcf8446900516e1a2d8f19802aac0eee
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
     admin_revision: 89fe3ac1f6178018186584db7542f11102896381
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowmart:
-    parent_revision: 2dccb3677f4da9a777cc0326ad22b50032eb803e
-    backend_parent_revision: 410fc4633e107d7c8b6570dadb78b6632d0da9f6
-    backend_revision: 410fc4633e107d7c8b6570dadb78b6632d0da9f6
-    web_parent_revision: db4cbd0b4b552c46d2371f6de4e8108d05e55bba
-    web_revision: db4cbd0b4b552c46d2371f6de4e8108d05e55bba
+    parent_revision: 1a849d7498632dad1b1c25774ebdd9667d2630cd
+    backend_parent_revision: fbf1e4d1bd0c3c7951338985cff442b2c5c93cc1
+    backend_revision: fbf1e4d1bd0c3c7951338985cff442b2c5c93cc1
+    web_parent_revision: b55591d55b2bb666ee55792424d596dd8036af9b
+    web_revision: b55591d55b2bb666ee55792424d596dd8036af9b
     admin_parent_revision: 5f109118ffbaca623a732ed33eaea61a2905241a
     admin_revision: 5f109118ffbaca623a732ed33eaea61a2905241a
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:61ab4d84b5ea779f03b30bb140c3172e9e25116933915f73a560bdaa765a908a source_revision: 984fd50157cef2a77752e853628adf72bf45760d 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:9aad3a7d30cbee336eb7abb0b277327e060d0850a58df77c56e8a15040f2d718 source_revision: 6c96e4386477ec2aa08e509b157a4de0752ac428 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:b4317323654158295305c8b976906decd6d79424674d80eeccd38fba1edbd34a source_revision: 7d518645992d2ce26930db5a6cf43ad8082c6172 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:b4deb052ef3b06e520f04df1edfccec7e25a3c602b0c1de163a6c9687170e54d source_revision: b681780fdcf8446900516e1a2d8f19802aac0eee 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:7385d4cca18cd776c5b4a7e621a62bb4915334de5238339d391d3bcf61202f2e source_revision: fbf1e4d1bd0c3c7951338985cff442b2c5c93cc1 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:6e5a70e85fe13877e9fb4ecaa199b1be668aa9ccddd5bdb6b567032bb3fb111b source_revision: b55591d55b2bb666ee55792424d596dd8036af9b 
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
 .../knowmart-app/knowmart-backend/identity/workload.yaml       |  4 ++--
 .../app-platform/knowmart-app/knowmart-backend/image.lock.yaml |  6 +++---
 .../knowbase-user-data-purchase-identity/workload.yaml         |  4 ++--
 .../knowmart-app/knowmart-backend/migration/workload.yaml      |  6 +++---
 .../knowmart-app/knowmart-backend/rabbitmq/workload.yaml       |  4 ++--
 .../knowmart-app/knowmart-backend/redis/workload.yaml          |  4 ++--
 .../knowmart-app/knowmart-backend/runtime/workload.yaml        |  8 ++++----
 .../knowmart-app/knowmart-web-frontend/image.lock.yaml         |  6 +++---
 .../knowmart-app/knowmart-web-frontend/workload.yaml           |  4 ++--
 42 files changed, 100 insertions(+), 100 deletions(-)
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
-            - {name: DEPLOYMENT_ID, value: '644ca9be97de7825e7b0c01f1d869b6155b50e76'}
+            - {name: DEPLOYMENT_ID, value: '984fd50157cef2a77752e853628adf72bf45760d'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-f4c409e506d43947"
+  DEPLOYMENT_ID: "knowbench-backend-61ab4d84b5ea779f"
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
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-1be8c33b29c31274"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-9aad3a7d30cbee33"}
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
digest: sha256:74d6eb3eca7ff9a78533fd02e01d6e0e0aea0035a973b4e32ce3293d51cf6224
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 6bc2630446c779a05972351251be5421982a1621
pointer-commit 5ac35b73277f7d02f89cb8ddcc6b5c6c3b7f54f5
tag release-20261125-1
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
kustomization.kustomize.toolkit.fluxcd.io/knowmart-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-knowbase-user-data-purchase-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowmart-web condition met
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-123 推送成功后可删。
