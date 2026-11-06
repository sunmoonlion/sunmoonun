# release #59：采集等待修复与Markdown成稿合并发版

- 时间：2026-11-03T01:36:27+08:00；分支 release/recovery-methods；目标 knowbase, knowfeed, knowbench, knowlab；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/59/）
- 提交：deploy 7b715dff919fe788514e3ac45be918431ec3b5ad；指针 b19c99fd656e539c82688289771707b28bb69075；tag release-20261103-1；批准：批准人 admin  2026-11-03T01:25:50+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml: digest: sha256:cfb3d69998ba00447e60d59d58369b205822bf0411b1afe751b233bd09ff2531 source_revision: f2f6df3163a01c71be13efdd20b87187b63693ec 
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:ea1f230a3ee5dd60c00273701ade5182cbec3e2462a94bd1c8d72db11fa9696a source_revision: 45f703a7bac0213b66ff67a6b9ca4fd4a2a93afd 
gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml: digest: sha256:7e8968701d9dce4b2669dd5d80b6c601d80360bbd39067f3010b17b2df83e2a7 source_revision: be6d29ed6f054304aa0f38d53831f5f7fa238fa2 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:0ef9061cdd2870e2158a73810257d36c2b18ad5a019e12483b93886b70e704bb source_revision: eb74f0b6d01fbabde0767c4a4439b49554f24291 
gitops/components/app-platform/knowfeed-app/knowfeed-admin-frontend/image.lock.yaml: digest: sha256:6a64e0c20ed73c17b3eb5a221abdaafbb71ae9aedb8e3d09a90943d7db8e84fd source_revision: a290cde1ffdf1abc3acc2885f23503057a8034f7 
gitops/components/app-platform/knowfeed-app/knowfeed-backend/image.lock.yaml: digest: sha256:a2bda94b46c5ab38e057f0d6015b997034c3132a3d0f50b1af10377844ef49a4 source_revision: df981b29762a2156f8879d832c1eb7cbe23d856c 
gitops/components/app-platform/knowfeed-app/knowfeed-web-frontend/image.lock.yaml: digest: sha256:b2fedaa1321af7e6198a7ce366f597bf463d72766dc5c2f1ea6f365348179456 source_revision: bb03f1ac21ffea0bc4e71dd5efc678256dd354ab 
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:84ebe1e02f204ff58fb990b8665bdbbfdf58ff37470dedbd6c7529cdb8940233 source_revision: fc8b4edc9144365248a7a96c58eaac5947fed111 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:23106450a31ef26ca3749fd13a79be2b51fbcbcd32e0b96503b789e69527f75a source_revision: 491538c0506aa39c96352b154f979fda02b438f3 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:bd4f55b39316396ba867e2d775719919776e93b93d3e154394097d332943b577 source_revision: a2577541a9dc59c1cc4b9896ad5a28a3ebb08771 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-app/knowbase-admin-frontend/image.lock.yaml       |  4 ++--
 .../knowbase-app/knowbase-admin-frontend/workload.yaml         |  4 ++--
 .../knowbase-app/knowbase-backend/identity/workload.yaml       |  4 ++--
 .../app-platform/knowbase-app/knowbase-backend/image.lock.yaml |  6 +++---
 .../knowbase-app/knowbase-backend/migration/workload.yaml      |  6 +++---
 .../knowbase-app/knowbase-backend/rabbitmq/workload.yaml       |  4 ++--
 .../knowbase-app/knowbase-backend/redis/workload.yaml          |  4 ++--
 .../knowbase-app/knowbase-backend/runtime/workload.yaml        |  8 ++++----
 .../knowbase-app/knowbase-web-frontend/image.lock.yaml         |  4 ++--
 .../knowbase-app/knowbase-web-frontend/workload.yaml           |  4 ++--
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
 .../knowlab-app/knowlab-admin-frontend/image.lock.yaml         |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/workload.yaml           |  4 ++--
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
 54 files changed, 126 insertions(+), 126 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-a259d4515d2b4ba6"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-admin-frontend-cfb3d69998ba0044"}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'c5c131598467ef32e7be1b91f596f0a0cac27445'}
+            - {name: DEPLOYMENT_ID, value: '45f703a7bac0213b66ff67a6b9ca4fd4a2a93afd'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-2d843f276cbae361"
+  DEPLOYMENT_ID: "knowbase-backend-ea1f230a3ee5dd60"
@@ -149,7 +149,7 @@ spec:
@@ -218,7 +218,7 @@ spec:
@@ -281,7 +281,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-fcf501f37efdcf19"}
+            - {name: DEPLOYMENT_ID, value: "knowbase-web-frontend-7e8968701d9dce4b"}
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
-            - {name: DEPLOYMENT_ID, value: 'f15e4920ce2d6dfe0834a6646a2f4b14eca1ce65'}
+            - {name: DEPLOYMENT_ID, value: 'eb74f0b6d01fbabde0767c4a4439b49554f24291'}
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/redis/workload.yaml
@@ -135,7 +135,7 @@ spec:
@@ -149,7 +149,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbench-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbench-backend-3ef1ce2110b3b3c3"
+  DEPLOYMENT_ID: "knowbench-backend-0ef9061cdd2870e2"
@@ -136,7 +136,7 @@ spec:
@@ -208,7 +208,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:d5a1ed1ecdc82461d45d84354a61e11e196603976ce3a9f3a8b1d135aebddceb
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 7b715dff919fe788514e3ac45be918431ec3b5ad
pointer-commit b19c99fd656e539c82688289771707b28bb69075
tag release-20261103-1
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

### 11-check-knowfeed.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=54   changed=0    unreachable=0    failed=0    skipped=20   rescued=0    ignored=0   

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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-59 推送成功后可删。
