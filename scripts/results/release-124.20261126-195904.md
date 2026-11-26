# release #124：KnowLab旧固定专家父申请退役补发，沿用#123前端与库版本

- 时间：2026-11-26T19:59:04+08:00；分支 knowlab-parent-retire-20261126；目标 knowlab；PIN=heads；Jenkins https://jenkins.dev.sunmoonai.com:30443/job/release/124/ 结果 FAILURE（apply 等待超时）；集群与 Git 由人工收尾补齐。
- 提交：deploy 653b6ae21644a12b0e81f004ab2dfc6239eb9ca2；指针 7bc4e62f64108a3b8ef2feb1d47948bed647e524；tag release-20261126-1；批准：批准人 admin  2026-11-26T19:14:17+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index b86fade72..a0f6027f6 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -39,9 +39,9 @@ applications:
     admin_revision: 33559e926c3ebb7570716d5bb318b5a014e0d645
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowlab:
-    parent_revision: 7c18a9e6bc915639c1006652dd2d9bace065437e
-    backend_parent_revision: 7d518645992d2ce26930db5a6cf43ad8082c6172
-    backend_revision: 7d518645992d2ce26930db5a6cf43ad8082c6172
+    parent_revision: 3857400992ae70ea19e0d118e9cf4550a69aaa49
+    backend_parent_revision: 8ddff9028ff360c106597e645f74c9ae86ed9c99
+    backend_revision: 8ddff9028ff360c106597e645f74c9ae86ed9c99
     web_parent_revision: b681780fdcf8446900516e1a2d8f19802aac0eee
     web_revision: b681780fdcf8446900516e1a2d8f19802aac0eee
     admin_parent_revision: 89fe3ac1f6178018186584db7542f11102896381
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml: digest: sha256:43f928c3713631099f020f7406cc443f68c7e56ec13b23109732d01a7b01f0eb source_revision: 89fe3ac1f6178018186584db7542f11102896381 
gitops/components/app-platform/knowlab-app/knowlab-backend/image.lock.yaml: digest: sha256:93a212a69dd48ee48f407cb4731c827e3ce9c240915486f4baab4a493d7f4e63 source_revision: 8ddff9028ff360c106597e645f74c9ae86ed9c99 
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:ddac0f193132b8b0d76cec31cc7b83acdbb5563a6dbb7a144bb6241aa2c7b09f source_revision: b681780fdcf8446900516e1a2d8f19802aac0eee 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowlab-app/knowlab-admin-frontend/image.lock.yaml            | 4 ++--
 .../app-platform/knowlab-app/knowlab-admin-frontend/workload.yaml | 4 ++--
 .../knowlab-app/knowlab-backend/identity/workload.yaml            | 4 ++--
 .../app-platform/knowlab-app/knowlab-backend/image.lock.yaml      | 6 +++---
 .../knowbase-user-data-directory-identity/workload.yaml           | 4 ++--
 .../knowbase-user-data-grant-test-identity/workload.yaml          | 4 ++--
 .../knowbase-user-data-output-identity/workload.yaml              | 4 ++--
 .../knowbase-user-data-read-identity/workload.yaml                | 4 ++--
 .../knowlab-backend/knowbench-incubate-identity/workload.yaml     | 4 ++--
 .../knowlab-backend/knowbench-testrun-identity/workload.yaml      | 4 ++--
 .../knowlab-backend/knowfeed-supply-demand-identity/workload.yaml | 4 ++--
 .../knowlab-backend/knowmart-deliver-identity/workload.yaml       | 4 ++--
 .../knowlab-app/knowlab-backend/migration/workload.yaml           | 6 +++---
 .../knowlab-app/knowlab-backend/rabbitmq/workload.yaml            | 4 ++--
 .../app-platform/knowlab-app/knowlab-backend/redis/workload.yaml  | 4 ++--
 .../knowlab-app/knowlab-backend/runtime/workload.yaml             | 8 ++++----
 .../app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml | 4 ++--
 .../app-platform/knowlab-app/knowlab-web-frontend/workload.yaml   | 4 ++--
 18 files changed, 40 insertions(+), 40 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-f1bcd03485246b15"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-admin-frontend-43f928c371363109"}
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
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowfeed-supply-demand-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/knowmart-deliver-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,14 +72,14 @@ spec:
-            - {name: DEPLOYMENT_ID, value: '7d518645992d2ce26930db5a6cf43ad8082c6172'}
+            - {name: DEPLOYMENT_ID, value: '8ddff9028ff360c106597e645f74c9ae86ed9c99'}
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowlab-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowlab-backend-b431732365415829"
+  DEPLOYMENT_ID: "knowlab-backend-93a212a69dd48ee4"
@@ -113,7 +113,7 @@ spec:
@@ -181,7 +181,7 @@ spec:
@@ -244,7 +244,7 @@ spec:
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-b4deb052ef3b06e5"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-ddac0f193132b8b0"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:f16889a9a3b7719008db57aa5292bbc0b5b96c45935772822193eb45ccc55276
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 653b6ae21644a12b0e81f004ab2dfc6239eb9ca2
pointer-commit 7bc4e62f64108a3b8ef2feb1d47948bed647e524
tag release-20261126-1
```

## 部署（10-apply.log 尾部、10-wait.txt）

```text
[ERROR]: Task failed: Module failed: The command exited with a non-zero return code.
Origin: /mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure/flux/source.yaml:259:11

257           ansible.builtin.include_tasks: ../../gitops/components/data-platform/neo4j/recover-rollout.yaml
258           when: flux_source_action == 'apply' and services_neo4j_enabled | default(false) | bool and neo4j_failed...
259         - name: Wait for root reconciliation
              ^ column 11

fatal: [localhost]: FAILED! => {"changed": true, "changed_when_result": true, "cmd": ["/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure/flux/../.tools/bin/flux", "--kubeconfig=/home/zymun/.kube/sunmoon-kind.config", "--context=kind-sunmoon-kind", "reconcile", "kustomization", "platform", "--timeout=600s"], "delta": "0:10:00.029139", "end": "2026-11-26 19:24:42.535835", "msg": "The command exited with a non-zero return code.", "rc": 1, "start": "2026-11-26 19:14:42.506696", "stderr": "► annotating Kustomization platform in flux-system namespace\n✔ Kustomization annotated\n◎ waiting for Kustomization reconciliation\n✗ context deadline exceeded", "stderr_lines": ["► annotating Kustomization platform in flux-system namespace", "✔ Kustomization annotated", "◎ waiting for Kustomization reconciliation", "✗ context deadline exceeded"], "stdout": "", "stdout_lines": []}

PLAY RECAP *********************************************************************
localhost                  : ok=33   changed=2    unreachable=0    failed=1    skipped=28   rescued=0    ignored=0   

make: *** [Makefile:287: flux-source-apply] Error 2
make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'

Jenkins #124 flux-source-apply 在 Wait for root reconciliation 超时（600s）。
根因：data-platform-dev/valkey AOF incr 尾部损坏（CrashLoopBackOff）。
处置：备份 /data/.aof-backup-20261126-115004；valkey-check-aof --fix 截断 35 字节；恢复 STS；flux reconcile platform 成功。
当前 platform/valkey/ragflow-runtime/knowbase-runtime/knowlab-runtime Ready，修订 sha256:f16889a9a3b7719008db57aa5292bbc0b5b96c45935772822193eb45ccc55276。
knowlab-api/worker/scheduler 镜像 sha256:93a212a69dd48ee48f407cb4731c827e3ce9c240915486f4baab4a493d7f4e63，Ready 1/1。
```

## 检查（11-check-*.log 尾部）

### 11-check-knowlab.log
```text

TASK [Report only public assertions for selected frontend checks] **************
skipping: [localhost]

TASK [End frontend-only verification without dispatching backend tasks] ********
skipping: [localhost]

TASK [Wait for current generation Ready at the promoted digest] ****************
make: *** [Makefile:419: application-check] Terminated

NOTE: skipped hung application-check wait; cluster Ready confirmed.
2026-11-26T19:59:04+08:00
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-124 推送成功后可删。

## 后半段人工收尾

- 根因：valkey AOF incr 尾部 35 字节损坏 → CrashLoop → platform 健康检查超时。
- 处置：PVC 备份后 valkey-check-aof --fix；恢复 STS；flux reconcile platform 成功。
- 现场：platform/knowlab-runtime/valkey Ready；knowlab-api/worker/scheduler 镜像 sha256:93a212a69dd48ee48f407cb4731c827e3ce9c240915486f4baab4a493d7f4e63，1/1。
