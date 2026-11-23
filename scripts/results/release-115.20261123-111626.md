# release #115：发布 KnowLab 孵化作者模式，只更新 Web

- 时间：2026-11-23T11:16:26+08:00；分支 author-mode-release-20261123；目标 knowlab；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/115/）
- 提交：deploy 2cfc5f80cf13bf8d1f147e0b4c05663c3439d006；指针 5fd8df175a4d47f24e861eea395b43b7e773298b；tag release-20261123-1；批准：批准人 admin  2026-11-23T10:33:19+08:00
- 补记：第 11 阶段读取已成功的迁移任务日志失败，流水线没有推送。所有者确认集群已是本次版本，不要重发。本回执按第 12 阶段的格式补写，没有再次构建、部署或检查。

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml: digest: sha256:9ca30ce238a6eee11c67ccf911453dd01dac7a1cfce11a6eb16599f217838d8e source_revision: 583e6dfcb33a62e60f398f2cd1425aeb94d9f617 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml   | 6 +++---
 .../app-platform/knowlab-app/knowlab-web-frontend/workload.yaml     | 4 ++--
 2 files changed, 5 insertions(+), 5 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowlab-app/knowlab-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-0c4047ba4659cc28"}
+            - {name: DEPLOYMENT_ID, value: "knowlab-web-frontend-9ca30ce238a6eee1"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:21cfcda1eb2a4db0ea257007b819eab967ba473c61b47d0e665a25adeaeb3357
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 2cfc5f80cf13bf8d1f147e0b4c05663c3439d006
pointer-commit 5fd8df175a4d47f24e861eea395b43b7e773298b
tag release-20261123-1
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

### 11-check-knowlab.log
```text

fatal: [localhost]: FAILED! => {"censored": "the output has been hidden due to the fact that 'no_log: true' was specified for this result", "changed": false}

PLAY RECAP *********************************************************************
localhost                  : ok=17   changed=0    unreachable=0    failed=1    skipped=17   rescued=0    ignored=0   

make: *** [Makefile:419: application-check] Error 2
make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-115 推送成功后可删。
