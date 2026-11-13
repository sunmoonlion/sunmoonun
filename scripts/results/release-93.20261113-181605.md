# release #93：Install skills and method connector scope; isolated script infrastructure

- 时间：2026-11-13T18:16:06+08:00；分支 capabilities-release-20261113；目标 knowbench, knowlab, sandbox；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/93/）
- 提交：deploy f7dde164138f4568631a6feaf822339c568906e9；指针 af64946576a8bed4daeac31a82985e121b5a97c3；tag release-20261113-2；批准：批准人 admin  2026-11-13T18:08:00+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml: digest: sha256:90d165c1f0dc5f83a1a26ec2990d09999ab661dfafaf713573074f549a7399be source_revision: 540d9f38bf9ef5015684686f6abe576c7144aea0 
gitops/components/app-platform/knowbench-app/knowbench-backend/image.lock.yaml: digest: sha256:d18a641187c6c136ac9fa1a7a3592a609c4aacee95e8ec92c4cd6680d3aa2d08 source_revision: 23ed7182a562c799ba990249f286f7c22120b6e9 
gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml: digest: sha256:b83ea800cea9920b1f54c568f5956bcce6c0d4d092c643a910bf17fee67db34d source_revision: b17271c3ec078b12c059666cbd0ab00f39728373 
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:b4a4def63b091d949e8ff1ed19eebc4bad2be4a35e9ef61cb932e07ee1d322b6 source_revision: 89fe3ac1f6178018186584db7542f11102896381 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:eaf9fb02c9000a3389ed589b9b59f42930987c5d6b22b1aeadcf1d7d5313218d source_revision: a042df08d3efe9c3ec9a6fcfcae3f127764dbf0b 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:215f3b00b9ee4f992087ff975c5622dbfc29f9868a94b966e872850c94d1e694 source_revision: e1bb08056f8a9abe038cb03a4a7f4613287a5239 
gitops/components/sandbox-platform/provisioner/image.lock.yaml: digest: sha256:597b736dd220e653ad8413b78acf8ba78d673a9ce03229fa42bbd41128c1e008 source_revision: baea88dbbbbed8d2ec69679593a6961db4b63520 
gitops/components/sandbox-platform/sandbox/image.lock.yaml: digest: sha256:0fd50c3fe714cbb004367fe32120843d71b6e82668b22805d41df8270ab2dc9f source_revision: baea88dbbbbed8d2ec69679593a6961db4b63520 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbench-app/knowbench-admin-frontend/image.lock.yaml   |  4 ++--
 .../knowbench-app/knowbench-admin-frontend/workload.yaml     |  4 ++--
 .../knowbench-app/knowbench-backend/identity/workload.yaml   |  4 ++--
 .../knowbench-app/knowbench-backend/image.lock.yaml          |  6 +++---
 .../knowbase-user-data-output-identity/workload.yaml         |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml           |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml            |  4 ++--
 .../knowlab-incubation-request-identity/workload.yaml        |  4 ++--
 .../knowmart-catalog-identity/workload.yaml                  |  4 ++--
 .../knowbench-backend/knowmart-demand-identity/workload.yaml |  4 ++--
 .../knowbench-backend/knowmart-summon-identity/workload.yaml |  4 ++--
 .../knowbench-app/knowbench-backend/migration/workload.yaml  |  6 +++---
 .../knowbench-backend/platform-computer/workload.yaml        |  4 ++--
 .../knowbench-app/knowbench-backend/rabbitmq/workload.yaml   |  4 ++--
 .../knowbench-app/knowbench-backend/redis/workload.yaml      |  4 ++--
 .../knowbench-app/knowbench-backend/runtime/workload.yaml    | 10 +++++-----
 .../knowbench-backend/service-identity/workload.yaml         |  4 ++--
 .../knowbench-app/knowbench-web-frontend/image.lock.yaml     |  6 +++---
 .../knowbench-app/knowbench-web-frontend/workload.yaml       |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/image.lock.yaml       |  4 ++--
 .../knowlab-app/knowlab-admin-frontend/workload.yaml         |  4 ++--
 .../knowlab-app/knowlab-backend/identity/workload.yaml       |  4 ++--
 .../app-platform/knowlab-app/knowlab-backend/image.lock.yaml |  6 +++---
 .../knowbase-user-data-directory-identity/workload.yaml      |  4 ++--
 .../knowbase-user-data-grant-test-identity/workload.yaml     |  4 ++--
 .../knowbase-user-data-output-identity/workload.yaml         |  4 ++--
 .../knowbase-user-data-read-identity/workload.yaml           |  4 ++--
 .../knowbench-incubate-identity/workload.yaml                |  4 ++--
 .../knowlab-backend/knowbench-testrun-identity/workload.yaml |  4 ++--
 .../knowfeed-supply-demand-identity/workload.yaml            |  4 ++--
 .../knowlab-backend/knowmart-deliver-identity/workload.yaml  |  4 ++--
 .../knowlab-app/knowlab-backend/migration/workload.yaml      |  6 +++---
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml       |  4 ++--
 .../knowlab-app/knowlab-backend/redis/workload.yaml          |  4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml        |  8 ++++----
 .../knowlab-app/knowlab-web-frontend/image.lock.yaml         |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml           |  4 ++--
 .../components/sandbox-platform/provisioner/image.lock.yaml  |  6 +++---
 gitops/components/sandbox-platform/provisioner/workload.yaml | 12 +++++++++---
 gitops/components/sandbox-platform/sandbox/image.lock.yaml   |  6 +++---
 40 files changed, 100 insertions(+), 94 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-2fb98ed57a9aeca7"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-admin-frontend-90d165c1f0dc5f83"}
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
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'a128987fed884906df5134fc9f45e9513cec0d04'}
+            - {name: DEPLOYMENT_ID, value: '23ed7182a562c799ba990249f286f7c22120b6e9'}
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
-  DEPLOYMENT_ID: "knowbench-backend-b4bf22d5ac66e624"
+  DEPLOYMENT_ID: "knowbench-backend-d18a641187c6c136"
@@ -140,7 +140,7 @@ spec:
@@ -212,7 +212,7 @@ spec:
@@ -273,7 +273,7 @@ spec:
@@ -330,7 +330,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/service-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbench-app/knowbench-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-bde4ecf4e7cd4d04"}
+            - {name: DEPLOYMENT_ID, value: "knowbench-web-frontend-b83ea800cea9920b"}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-7ad7e4bd1aed37cb"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-b4a4def63b091d94"}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/identity/workload.yaml
@@ -298,7 +298,7 @@ spec:
@@ -312,7 +312,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbase-user-data-directory-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:90945a3aa0360dc2f0fc45c14953f1233345639971e90d998dfc77d870dc8fb0
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: f7dde164138f4568631a6feaf822339c568906e9
pointer-commit af64946576a8bed4daeac31a82985e121b5a97c3
tag release-20261113-2
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-93 推送成功后可删。
