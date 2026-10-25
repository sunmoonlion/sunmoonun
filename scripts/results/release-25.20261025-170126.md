# release #25：0042 批次 knowlab 重发：#23 验收倒在管理端列表路径（cf267149 修正）；#23 的钉没推上去，#24 PIN=keep 撞上旧钉，改回 PIN=heads（与 #23 同一组头）

- 时间：2026-10-25T17:01:26+08:00；分支 fable；应用 knowlab；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/25/）
- 提交：deploy 42d9cb7e1257242210d179a5486fe30626c52001；指针 33a55ed5cb6a962e045cd0f3f23296bf74749bd7；tag release-20261025-6；批准：批准人 admin  2026-10-25T16:56:49+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 1ff36386..57ed4d72 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -39,13 +39,13 @@ applications:
     admin_revision: 26964553ed9d581ac855c38edeaee8e65add792f
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 43cd00fc7c930419474a86cee0317dfe54dad2f4
-    backend_parent_revision: e3287024050aef46b6d6954e5e8ab6f59294eaad
-    backend_revision: e3287024050aef46b6d6954e5e8ab6f59294eaad
-    web_parent_revision: d7589583436d7d42d90e390f91508acb6ed76a39
-    web_revision: d7589583436d7d42d90e390f91508acb6ed76a39
-    admin_parent_revision: 2d5c1124c0b3f76ec0efda2371fadbd5f13787b0
-    admin_revision: 2d5c1124c0b3f76ec0efda2371fadbd5f13787b0
+    parent_revision: 6e95425348b673f7a02efb59b1bdf3f719092ef2
+    backend_parent_revision: 519e21d695ce95cc97446f0107d6693e1471ded0
+    backend_revision: 519e21d695ce95cc97446f0107d6693e1471ded0
+    web_parent_revision: 3a0f2c847c220770d28177288023debc75172f19
+    web_revision: 3a0f2c847c220770d28177288023debc75172f19
+    admin_parent_revision: 28c79f0c38d4a01753dd92f403587470585f9ac3
+    admin_revision: 28c79f0c38d4a01753dd92f403587470585f9ac3
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowmart:
     parent_revision: 09218c16a29cb9150b7758e1aca06798e928efde
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:b58c6d795c52697031d66e648a29cb1a30e8ec0c83de4c7a6d3ecb0214f66474 source_revision: 28c79f0c38d4a01753dd92f403587470585f9ac3 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:b9ef0ed12b8e878305202f724ed2bce93f18d768f5040324ae38638460f35f16 source_revision: 519e21d695ce95cc97446f0107d6693e1471ded0 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:34509fdcb6bed0f643086671ff3ffedcd750110bd16f453d17f058305fd7b608 source_revision: 3a0f2c847c220770d28177288023debc75172f19 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowlab-app/knowlab-admin-frontend/image.lock.yaml |  6 +++---
 .../knowlab-app/knowlab-admin-frontend/workload.yaml   |  4 ++--
 .../knowlab-app/knowlab-backend/identity/workload.yaml |  4 ++--
 .../knowlab-app/knowlab-backend/image.lock.yaml        |  6 +++---
 .../workload.yaml                                      |  4 ++--
 .../knowbase-user-data-import-identity/workload.yaml   |  4 ++--
 .../knowbench-testrun-identity/workload.yaml           |  4 ++--
 .../knowmart-deliver-identity/workload.yaml            |  4 ++--
 .../knowlab-backend/migration/workload.yaml            |  8 ++++----
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml |  4 ++--
 .../knowlab-app/knowlab-backend/redis/workload.yaml    |  4 ++--
 .../knowlab-app/knowlab-backend/runtime/tls.sops.yaml  | 18 +++++++++---------
 .../knowlab-app/knowlab-backend/runtime/workload.yaml  | 14 +++++++-------
 .../knowlab-app/knowlab-web-frontend/image.lock.yaml   |  6 +++---
 .../knowlab-app/knowlab-web-frontend/workload.yaml     |  4 ++--
 15 files changed, 47 insertions(+), 47 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-63c78b382f1eb0ee"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-b58c6d795c526970"}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbase-user-data-grant-test-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbase-user-data-import-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowbench-testrun-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowmart-deliver-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'e3287024050aef46b6d6954e5e8ab6f59294eaad'}
+            - {name: DEPLOYMENT_ID, value: '519e21d695ce95cc97446f0107d6693e1471ded0'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261019_0010'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261024_0012'}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/runtime/tls.sops.yaml
@@ -5,20 +5,20 @@ metadata:
-    tls.key: ENC[AES256_GCM,data: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,iv:LfRKuEYJYyHWLnQxNKgjmmeZqSxDF1Xa+EzjetRKuP8=,tag:E56jgnme5SformxHR2j6TQ==,type:str]
-    tls.crt: ENC[AES256_GCM,data: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,iv:I1K5tkhrE+pZkLCY0FKrlfu1l+4H3mNC2MJsAzDYOgM=,tag:HyiXb5r+0g4Mws0yaCgcew==,type:str]
+    tls.key: ENC[AES256_GCM,data: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,iv:Ia2QEOk1Vr+d39Ntm2JGHDnTI1p9R01S4iqdCsUGtoQ=,tag:pNevb7JtrG4fVWczd6Zezg==,type:str]
+    tls.crt: ENC[AES256_GCM,data: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,iv:Y5SluK2+Kq0SuvDEFsswSYxdGPHLVUyDbEhL5TiMchg=,tag:ue6fofN8S3pdzprB2XWKug==,type:str]
-            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBsbEtBRXBRL28xdis3bmxm
-            WXV4Sk5OOGRxQm10Z04yMnRrYVI1ZndRUENzCnpkTjdYb3RmUGdnMTBRZWFkRktV
-            UDI0YzhrMHJFeU9OY1huVGxvL1cyVGMKLS0tIDkzYmlSamRyMXZ3Z1JYeU9VUm50
-            M3duZUIzWVA1aEtORDk2MnlJbVVWclUKXaAACAm1mzbXb+XQA6uMlVHm0EjfIxHj
-            re/pPmUuYg+yJ3dsiTgqIlWstd1qkexi3DHgS1cKOjDtGmo6NIOAiw==
+            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBkZlV4WkZRQklRSXdIaU9p
+            bTB0a1ZxdXUxQ1lVY0JTazcwcjd5UkdjekdzCklVTi9MVVZVZ2hDUkVQVnVPQ25P
+            ZFJ5aC9HY242YkpKRGdFeUUvR1JqUjQKLS0tIG5NbHNmejhJZnNjTzluV2dyRHF0
+            NXUwcUVRcTJoSjRJbm8xdHprcFlRZ2MKK7n5Ni+lT9sbCBQsa4Q14jhvg1pBMY29
+            tmW2dOpdHRou/oyK9bc2yuAGxPn4xBUweWTBDq6CUTENs+pwiPCtCQ==
-    lastmodified: "2026-10-25T04:42:39Z"
-    mac: ENC[AES256_GCM,data:bv9B7P4cGNeVG4xcqrZZgnXZhVemAdIQlFGWdfj7wr7Ve/04akKIxD0wxh3S/XqXitHhC7VshBDSQYVESqAtss/+FCv+igU+8UuTlBtnF203Ov+nMHPKL2GNE9UkSjKprAWS6BDo/QMVHjazu8Upt9l3d1L0lA1n7PWqtUGmso0=,iv:ypVdqSs0z7/dhTm72nOdtUqVzv2c69vcihQccInZxJc=,tag:0wLrIWXSC3q8wEv3naAr4A==,type:str]
+    lastmodified: "2026-10-22T01:56:13Z"
+    mac: ENC[AES256_GCM,data:dbbYcl5pazMJgUaWdqiCs38nCiLJKW+UMQ09fUpL0XSDnl7j+2iU9buu+PrZKc1YPqi6xDoCBksxs46Ik8gKbJ2PFTHZb3IBCagGmkHb1y1BQTNR0VlNMz567MHMsrJtZuYnumj66bNIub7DBRAXYJqVaRw1OCmtGbOi4cToTrI=,iv:AiCNrds4vB0KCViVyw4i6hogviyaRQGzDzs6CvsYeqc=,tag:uG38SHriZdecatoTkh6M0A==,type:str]
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowlab-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowlab-backend-16b489d0aff64b2b"
+  DEPLOYMENT_ID: "knowlab-backend-b9ef0ed12b8e8783"
@@ -87,7 +87,7 @@ spec:
@@ -97,7 +97,7 @@ spec:
@@ -155,7 +155,7 @@ spec:
@@ -165,7 +165,7 @@ spec:
@@ -218,7 +218,7 @@ spec:
@@ -228,7 +228,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-5df261c550b38329"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-34509fdcb6bed0f6"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:5020bae5adbad62ef2c1dbfedf93d34714b32089becc1f2725b95b5cf16f9d10
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 42d9cb7e1257242210d179a5486fe30626c52001
pointer-commit 33a55ed5cb6a962e045cd0f3f23296bf74749bd7
tag release-20261025-6
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
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-grant-test-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-import-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbench-testrun-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowmart-deliver-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-storage condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-web condition met
```

## 检查（11-check-*.log 尾部）

### 11-check-knowlab.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=50   changed=0    unreachable=0    failed=0    skipped=24   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-25 推送成功后可删。
