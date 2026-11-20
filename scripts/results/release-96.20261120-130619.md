# release #96：发布已复核的连接器与脚本范围及 Codex 0.170.0

- 时间：2026-11-20T13:06:20+08:00；分支 c1-c6-release-20261120；目标 knowbench, knowlab, knowbase, knowmart, sandbox；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/96/）
- 提交：deploy 8c6893f496f839727088a4e341cc6ec35a0a9173；指针 e16fba8413deb1fdfbcd7b6265bb916ea3f8e890；tag release-20261120-1；批准：批准人 admin  2026-11-20T12:54:18+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml: digest: sha256:00e481c455d0a2c667af8e8ee6135341d8024a5024480368675525851088eb4a source_revision: f2f6df3163a01c71be13efdd20b87187b63693ec 
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:acd2487ccb02794d58e902a845ba05112ceedccf832065c5b772c06bc117b28d source_revision: 906f88aeaf8bd6f08495cb16ff3a34151909d9b5 
gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml: digest: sha256:04a7db3481cf18ba0900ff6f10b2544404656b214d50e6998e20611b7eb3a478 source_revision: 884d235418f63676a88002978bf99bd99112cdb1 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:d52419126a2574f168c25ae4e668b41f2fd708bc6822d19348372f6fe4987539 source_revision: 4aa68b7d0fe58b9d78c7ebc14742790da3840c02 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:bd761ca251b612a267d3a0e08adc54c5dfb14f7d86f4aef839c604a11caa27f7 source_revision: 11a3fd728ad63d35d47cd2b1a9bd60d2850ce5ea 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:5323de113029902efe50980f4a03131e4e2781682ce2102e57c1fa8421344ff4 source_revision: e7e3c5451492c116cf094c480a974c2068b71018 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:47af9a8bc6b5dadf431e30493f55488770b2309ce0ff5031e4e3c74678cc65eb source_revision: 7eb57a755c676e6208dd1b33abf1e30af81e6145 
gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml: digest: sha256:9f0c0a4b52549aca9bde02d966592f302a9c01da51cf42eb7e46b7c7c8627b8d source_revision: 5f109118ffbaca623a732ed33eaea61a2905241a 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:4c7ee214ddce35da392f691de2a93c5ef2efda8e2b64028283895b2808df5195 source_revision: 090da88031ef0fa0b6db1300acc778ed41d7c050 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:24f05af2490abb7869211e96908deff6782cced6a57f2b59ceb545d9dd49074a source_revision: 305f0876c9a1174e625f840c8d907da935c4b006 
gitops/components/sandbox-platform/provisioner/image.lock.yaml: digest: sha256:3eeb6761c7ffc69dc5943b6cf3346e6f5e559e2f87402926bc5e9e12b348d9fb source_revision: 42ef8470eaf8df065184dbae0537c963ad15b8a8 
gitops/components/sandbox-platform/sandbox/image.lock.yaml: digest: sha256:aaf941ee938d30b6a938f7e46ed2d1521142dc654e75fe8ff61fb483bb05f46b source_revision: 42ef8470eaf8df065184dbae0537c963ad15b8a8 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-admin-frontend/image.lock.yaml        |  4 ++--
 .../knowbase-admin-frontend/workload.yaml          |  4 ++--
 .../knowbase-backend/identity/workload.yaml        |  4 ++--
 .../knowbase-app/knowbase-backend/image.lock.yaml  |  6 +++---
 .../knowbase-backend/migration/workload.yaml       | 12 ++++++------
 .../knowbase-backend/rabbitmq/workload.yaml        |  4 ++--
 .../knowbase-backend/redis/workload.yaml           |  4 ++--
 .../knowbase-backend/runtime/workload.yaml         | 14 +++++++-------
 .../knowbase-web-frontend/image.lock.yaml          |  6 +++---
 .../knowbase-web-frontend/workload.yaml            |  4 ++--
 .../knowbench-backend/identity/workload.yaml       |  4 ++--
 .../knowbench-backend/image.lock.yaml              |  6 +++---
 .../workload.yaml                                  |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml  |  4 ++--
 .../workload.yaml                                  |  4 ++--
 .../knowmart-catalog-identity/workload.yaml        |  4 ++--
 .../knowmart-demand-identity/workload.yaml         |  4 ++--
 .../knowmart-summon-identity/workload.yaml         |  4 ++--
 .../knowbench-backend/migration/workload.yaml      | 12 ++++++------
 .../platform-computer/workload.yaml                | 16 ++++++++--------
 .../knowbench-backend/rabbitmq/workload.yaml       |  4 ++--
 .../knowbench-backend/redis/workload.yaml          |  4 ++--
 .../runtime/agent-releases.sops.yaml               | 22 +++++++++++-----------
 .../knowbench-backend/runtime/workload.yaml        | 19 ++++++++++---------
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
 .../knowlab-backend/migration/workload.yaml        | 12 ++++++------
 .../knowlab-backend/rabbitmq/workload.yaml         |  4 ++--
 .../knowlab-backend/redis/workload.yaml            |  4 ++--
 .../knowlab-backend/runtime/workload.yaml          | 14 +++++++-------
 .../knowlab-web-frontend/image.lock.yaml           |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml |  4 ++--
 .../knowmart-admin-frontend/image.lock.yaml        |  4 ++--
 .../knowmart-admin-frontend/workload.yaml          |  4 ++--
 .../knowmart-backend/identity/workload.yaml        |  4 ++--
 .../knowmart-app/knowmart-backend/image.lock.yaml  |  6 +++---
 .../workload.yaml                                  |  4 ++--
 .../knowmart-backend/migration/workload.yaml       | 12 ++++++------
 .../knowmart-backend/rabbitmq/workload.yaml        |  4 ++--
 .../knowmart-backend/redis/workload.yaml           |  4 ++--
 .../knowmart-backend/runtime/workload.yaml         | 14 +++++++-------
 .../knowmart-web-frontend/image.lock.yaml          |  6 +++---
 .../knowmart-web-frontend/workload.yaml            |  4 ++--
 .../sandbox-platform/provisioner/image.lock.yaml   |  6 +++---
 .../sandbox-platform/provisioner/workload.yaml     | 13 ++++++++-----
 .../sandbox-platform/sandbox/image.lock.yaml       |  6 +++---
 58 files changed, 186 insertions(+), 182 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-89a85ac75c092acb"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-00e481c455d0a2c6"}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -298,7 +298,7 @@ spec:
@@ -312,7 +312,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -1,6 +1,6 @@
@@ -58,7 +58,7 @@ data:
@@ -72,22 +72,22 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '5d78176c5d0e899d9b5fa649c927641c2e8acdfd'}
+            - {name: DEPLOYMENT_ID, value: '906f88aeaf8bd6f08495cb16ff3a34151909d9b5'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261101_0021'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261119_0022'}
-        - {name: verify, configMap: {name: 'knowbase-schema-check-v4'}}
+        - {name: verify, configMap: {name: 'knowbase-schema-check-v5'}}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-10384ba19f29152a"
+  DEPLOYMENT_ID: "knowbase-backend-acd2487ccb02794d"
@@ -139,7 +139,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
@@ -208,7 +208,7 @@ spec:
@@ -218,7 +218,7 @@ spec:
@@ -271,7 +271,7 @@ spec:
@@ -281,7 +281,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-4c729217e3d6307c"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-04a7db3481cf18ba"}
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
@@ -1,6 +1,6 @@
@@ -58,7 +58,7 @@ data:
@@ -72,22 +72,22 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '5f1c7d71baf01d240eb41376d46d3064882178eb'}
+            - {name: DEPLOYMENT_ID, value: '4aa68b7d0fe58b9d78c7ebc14742790da3840c02'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261113_0040'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261120_0049'}
-        - {name: verify, configMap: {name: 'knowbench-schema-check-v10'}}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:51e5cbfd61f433e0785eaede7e94b18e858e1cd56f1b6e6fcc3d4db10fdcd76c
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 8c6893f496f839727088a4e341cc6ec35a0a9173
pointer-commit e16fba8413deb1fdfbcd7b6265bb916ea3f8e890
tag release-20261120-1
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-96 推送成功后可删。
