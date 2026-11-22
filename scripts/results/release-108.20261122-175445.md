# release #108：重渲染供给器以发布指令控制面地址

- 时间：2026-11-22T17:54:45+08:00；分支 expert-entry-release-20261122；目标 sandbox；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/108/）
- 提交：deploy ca2d9423e05d3784b3c03d64c75ebc8552eb7c0d；指针 304e733bdc0be56954e5113ec1072c4439aafc94；tag release-20261122-5；批准：批准人 admin  2026-11-22T17:51:43+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
(no image lock changed: same pins rebuilt to the same digests)
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 gitops/components/sandbox-platform/provisioner/workload.yaml | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```
```diff
+++ b/gitops/components/sandbox-platform/provisioner/workload.yaml
@@ -74,7 +74,7 @@ spec:
-            - {name: INSTRUCTION_CONTROL_ORIGIN, value: 'https://knowbench-tls.app-platform-dev.svc.cluster.local'}
+            - {name: INSTRUCTION_CONTROL_ORIGIN, value: "https://knowbench-tls.app-platform-dev.svc.cluster.local"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:6783cc31adc0a8fba5a8fad2d4032ef8cd60e7afce55660f3da52df0887787bd
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: ca2d9423e05d3784b3c03d64c75ebc8552eb7c0d
pointer-commit 304e733bdc0be56954e5113ec1072c4439aafc94
tag release-20261122-5
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
```

## 检查（11-check-*.log 尾部）

### 11-check-sandbox.log
```text
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=23   changed=1    unreachable=0    failed=0    skipped=77   rescued=0    ignored=0   

make[2]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make[1]: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-108 推送成功后可删。
