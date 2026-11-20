# release #97：P1与审查修复合并发布，脚本开关保持关闭

- 时间：2026-11-20T21:33:17+08:00；分支 p1-f21-release-20261120；目标 knowbase, knowmart, knowbench, knowlab, sandbox；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/97/）
- 提交：deploy 522f76c1571f432c668a1c42e811635f73386d27；指针 ab1e0994fe803f1d8133b99f7ccc9f9d9ff5ff75；tag release-20261120-2；批准：批准人 admin  2026-11-20T21:22:40+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 54cf2453f..589a58847 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -22,36 +22,36 @@ applications:
     admin_parent_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
     admin_revision: 1bdcbcd042a45a0d19de1787778fd78f96cf49b6
   knowbase:
-    parent_revision: 9552fba44565e0a71b5a8f0d9d921b217537bbba
-    backend_parent_revision: 906f88aeaf8bd6f08495cb16ff3a34151909d9b5
-    backend_revision: 906f88aeaf8bd6f08495cb16ff3a34151909d9b5
+    parent_revision: c9ed334702e3dd9e2fd0fd4842b923947d9ed2ea
+    backend_parent_revision: b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b
+    backend_revision: b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b
     web_parent_revision: 884d235418f63676a88002978bf99bd99112cdb1
     web_revision: 884d235418f63676a88002978bf99bd99112cdb1
     admin_parent_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
     admin_revision: f2f6df3163a01c71be13efdd20b87187b63693ec
   knowbench:
-    parent_revision: 0b56e0a7b2f4f9ff7a2b7e45452a358acb891927
-    backend_parent_revision: 4aa68b7d0fe58b9d78c7ebc14742790da3840c02
-    backend_revision: 4aa68b7d0fe58b9d78c7ebc14742790da3840c02
-    web_parent_revision: 11a3fd728ad63d35d47cd2b1a9bd60d2850ce5ea
-    web_revision: 11a3fd728ad63d35d47cd2b1a9bd60d2850ce5ea
+    parent_revision: 0f031cd78351a1e95d3bfbbb1e2b1e28c736afeb
+    backend_parent_revision: 3a3eb862ffb6d752eec84e477c6c6a417dad710f
+    backend_revision: 3a3eb862ffb6d752eec84e477c6c6a417dad710f
+    web_parent_revision: ed6ed7aefddd313ea2b304c0cc35413297024a50
+    web_revision: ed6ed7aefddd313ea2b304c0cc35413297024a50
     admin_parent_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
     admin_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 8bbce621c053a861d8e7bcfad1b6ebdeb4c67163
-    backend_parent_revision: e7e3c5451492c116cf094c480a974c2068b71018
-    backend_revision: e7e3c5451492c116cf094c480a974c2068b71018
-    web_parent_revision: 7eb57a755c676e6208dd1b33abf1e30af81e6145
-    web_revision: 7eb57a755c676e6208dd1b33abf1e30af81e6145
+    parent_revision: c61b98e92c6b2f9254ab3e9ee8dd566eb49e998a
+    backend_parent_revision: 185e1ca91d2d114f7d466b89b55d028900e2ca47
+    backend_revision: 185e1ca91d2d114f7d466b89b55d028900e2ca47
+    web_parent_revision: f4ace6f9e9b5194a75ca6c613b6a1dd7bbcc18af
+    web_revision: f4ace6f9e9b5194a75ca6c613b6a1dd7bbcc18af
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
     admin_revision: 89fe3ac1f6178018186584db7542f11102896381
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowmart:
-    parent_revision: bbc14059920140252c9ebf4977ee763d5c3c71ed
-    backend_parent_revision: 090da88031ef0fa0b6db1300acc778ed41d7c050
-    backend_revision: 090da88031ef0fa0b6db1300acc778ed41d7c050
-    web_parent_revision: 305f0876c9a1174e625f840c8d907da935c4b006
-    web_revision: 305f0876c9a1174e625f840c8d907da935c4b006
+    parent_revision: 190f8ce3282a4ac4dd3cf15448077d7383e8ba58
+    backend_parent_revision: 71751d52b5d145c32d3d829103f0486ccfe1cdb8
+    backend_revision: 71751d52b5d145c32d3d829103f0486ccfe1cdb8
+    web_parent_revision: 14515db89f249d76ea67f83b746fed030ccdf7f0
+    web_revision: 14515db89f249d76ea67f83b746fed030ccdf7f0
     admin_parent_revision: 5f109118ffbaca623a732ed33eaea61a2905241a
     admin_revision: 5f109118ffbaca623a732ed33eaea61a2905241a
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:ea82f12d44b25e4bc1d9a3c459c42768ab31e85808b2bb15511848a253794eb0 source_revision: b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:aec3f2bddad53bb6af599e0449114e9f4963b6c178051e71e697cf48b9f44fc9 source_revision: 3a3eb862ffb6d752eec84e477c6c6a417dad710f 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:32af4acb375d0c37619378a7ecb2f29275a29d0ad9aa854711cc13e32ec2ab52 source_revision: ed6ed7aefddd313ea2b304c0cc35413297024a50 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:45282caca6d9832400ed73187ce569a4da66ce598d977ea5cdf8c1fa01879c0b source_revision: 185e1ca91d2d114f7d466b89b55d028900e2ca47 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:83827a55898ef1cbdb73464020834b64054e857542f1fddf3f553d0883d343a3 source_revision: f4ace6f9e9b5194a75ca6c613b6a1dd7bbcc18af 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:d3575d6e11ca203c67e205ce4759e3308cdb90ca42b015ea9d240334718378f9 source_revision: 71751d52b5d145c32d3d829103f0486ccfe1cdb8 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:bea512b3ab1bae69b9f7f9c9c6a2698027e1cf46bd749945d24698dd1020ec09 source_revision: 14515db89f249d76ea67f83b746fed030ccdf7f0 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-backend/identity/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/image.lock.yaml      |  6 +++---
 .../knowbase-backend/migration/workload.yaml           |  6 +++---
 .../knowbase-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/redis/workload.yaml  |  4 ++--
 .../knowbase-backend/runtime/workload.yaml             |  8 ++++----
 .../knowbench-backend/identity/workload.yaml           |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml    |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml   |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml     |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml      |  4 ++--
 .../knowlab-incubation-request-identity/workload.yaml  |  4 ++--
 .../knowmart-catalog-identity/workload.yaml            |  4 ++--
 .../knowmart-demand-identity/workload.yaml             |  4 ++--
 .../knowmart-summon-identity/workload.yaml             |  4 ++--
 .../knowbench-backend/migration/workload.yaml          |  8 ++++----
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
 .../knowlab-backend/migration/workload.yaml            |  8 ++++----
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml |  4 ++--
 .../knowlab-app/knowlab-backend/redis/workload.yaml    |  4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml  | 14 +++++++-------
 .../knowlab-app/knowlab-web-frontend/image.lock.yaml   |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml     |  4 ++--
 .../knowmart-backend/identity/workload.yaml            |  4 ++--
 .../knowmart-app/knowmart-backend/image.lock.yaml      |  6 +++---
 .../knowbase-user-data-purchase-identity/workload.yaml |  4 ++--
 .../knowmart-backend/migration/workload.yaml           |  8 ++++----
 .../knowmart-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowmart-app/knowmart-backend/redis/workload.yaml  |  4 ++--
 .../knowmart-backend/runtime/workload.yaml             | 14 +++++++-------
 .../knowmart-app/knowmart-web-frontend/image.lock.yaml |  6 +++---
 .../knowmart-app/knowmart-web-frontend/workload.yaml   |  4 ++--
 47 files changed, 127 insertions(+), 127 deletions(-)
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
-            - {name: DEPLOYMENT_ID, value: '906f88aeaf8bd6f08495cb16ff3a34151909d9b5'}
+            - {name: DEPLOYMENT_ID, value: 'b2cbb9f99e8a98c0cc3c7e02e8253fe10c8ef53b'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-acd2487ccb02794d"
+  DEPLOYMENT_ID: "knowbase-backend-ea82f12d44b25e4b"
@@ -149,7 +149,7 @@ spec:
@@ -218,7 +218,7 @@ spec:
@@ -281,7 +281,7 @@ spec:
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
-            - {name: DEPLOYMENT_ID, value: '4aa68b7d0fe58b9d78c7ebc14742790da3840c02'}
+            - {name: DEPLOYMENT_ID, value: '3a3eb862ffb6d752eec84e477c6c6a417dad710f'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261120_0049'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261120_0050'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-d52419126a2574f1"
+  DEPLOYMENT_ID: "knowbench-backend-aec3f2bddad53bb6"
@@ -131,7 +131,7 @@ spec:
@@ -141,7 +141,7 @@ spec:
@@ -203,7 +203,7 @@ spec:
@@ -213,7 +213,7 @@ spec:
@@ -264,7 +264,7 @@ spec:
@@ -274,7 +274,7 @@ spec:
@@ -321,7 +321,7 @@ spec:
@@ -331,7 +331,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:086da47df80d5dfcbdffdefd351fc73ccbfe2e9c4861c43874ffed16fcc0e670
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 522f76c1571f432c668a1c42e811635f73386d27
pointer-commit ab1e0994fe803f1d8133b99f7ccc9f9d9ff5ff75
tag release-20261120-2
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
kustomization.kustomize.toolkit.fluxcd.io/knowbase-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-provider condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbase-web condition met
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

### 11-check-knowmart.log
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-97 推送成功后可删。
