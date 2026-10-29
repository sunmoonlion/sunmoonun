# release #30：数据第四版新增服务关系与孵化 incubate 测试电脑改平台电脑 交Fable-gitops 第一三节

- 时间：2026-10-29T12:05:21+08:00；分支 fable；应用 knowfeed, knowbase, knowbench, knowlab；PIN=keep；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/30/）
- 提交：deploy 71891c3250ebd4be308c3b264e6964306813183f；指针 6eff0fb83a80f0c911d2af14184f97da24e184d8；tag release-20261029-1；批准：批准人 admin  2026-10-29T11:43:52+08:00

## 改钉（2-sources.diff）

```diff
```

## 镜像锁（3-image-locks.txt）

```text
(no image lock changed: same pins rebuilt to the same digests)
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-backend/runtime/workload.yaml         | 41 ++++++++++++--
 .../platform-computer/download.sops.yaml           | 26 ++++-----
 .../platform-computer/workload.yaml                | 62 ++++++++++++----------
 .../knowbench-backend/runtime/kustomization.yaml   |  2 +
 .../knowbench-backend/runtime/workload.yaml        | 33 ++++++++++--
 .../knowfeed-backend/runtime/kustomization.yaml    |  1 +
 .../knowfeed-backend/runtime/workload.yaml         | 29 ++++++++--
 .../knowlab-backend/runtime/kustomization.yaml     |  5 ++
 .../knowlab-backend/runtime/workload.yaml          | 42 +++++++++++++--
 9 files changed, 186 insertions(+), 55 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -44,6 +44,13 @@ data:
+  SERVICE_AUTH_USER_DATA_DIRECTORY_CALLERS: "knowlab"
+  SERVICE_AUTH_USER_DATA_DIRECTORY_KNOWLAB_CASDOOR_APPLICATION: "sunmoonai-knowlab-knowbase-user-data-directory"
+  SERVICE_AUTH_USER_DATA_DIRECTORY_KNOWLAB_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_USER_DATA_DIRECTORY_KNOWLAB_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_USER_DATA_DIRECTORY_KNOWLAB_AUDIENCE: "sunmoon-knowlab-knowbase-user-data-directory"
+  SERVICE_AUTH_USER_DATA_DIRECTORY_KNOWLAB_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowlab-knowbase-user-data-directory"
+  SERVICE_AUTH_USER_DATA_DIRECTORY_KNOWLAB_REQUIRED_SCOPE: "knowbase:user-data-directory"
@@ -58,6 +65,19 @@ data:
+  SERVICE_AUTH_USER_DATA_OUTPUT_CALLERS: "knowbench,knowlab"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWBENCH_CASDOOR_APPLICATION: "sunmoonai-knowbench-knowbase-user-data-output"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWBENCH_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWBENCH_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWBENCH_AUDIENCE: "sunmoon-knowbench-knowbase-user-data-output"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWBENCH_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowbench-knowbase-user-data-output"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWBENCH_REQUIRED_SCOPE: "knowbase:user-data-output"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWLAB_CASDOOR_APPLICATION: "sunmoonai-knowlab-knowbase-user-data-output"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWLAB_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWLAB_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWLAB_AUDIENCE: "sunmoon-knowlab-knowbase-user-data-output"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWLAB_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowlab-knowbase-user-data-output"
+  SERVICE_AUTH_USER_DATA_OUTPUT_KNOWLAB_REQUIRED_SCOPE: "knowbase:user-data-output"
@@ -65,13 +85,26 @@ data:
-  SERVICE_AUTH_USER_DATA_READ_CALLERS: "knowbench"
+  SERVICE_AUTH_USER_DATA_READ_CALLERS: "knowbench,knowlab"
+  SERVICE_AUTH_USER_DATA_READ_KNOWLAB_CASDOOR_APPLICATION: "sunmoonai-knowlab-knowbase-user-data-read"
+  SERVICE_AUTH_USER_DATA_READ_KNOWLAB_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_USER_DATA_READ_KNOWLAB_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_USER_DATA_READ_KNOWLAB_AUDIENCE: "sunmoon-knowlab-knowbase-user-data-read"
+  SERVICE_AUTH_USER_DATA_READ_KNOWLAB_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowlab-knowbase-user-data-read"
+  SERVICE_AUTH_USER_DATA_READ_KNOWLAB_REQUIRED_SCOPE: "knowbase:user-data-read"
+  SERVICE_AUTH_USER_DATA_SUPPLY_CALLERS: "knowfeed"
+  SERVICE_AUTH_USER_DATA_SUPPLY_KNOWFEED_CASDOOR_APPLICATION: "sunmoonai-knowfeed-knowbase-user-data-supply"
+  SERVICE_AUTH_USER_DATA_SUPPLY_KNOWFEED_DISCOVERY_URL: https://casdoor.dev.sunmoonai.com:30443/.well-known/openid-configuration
+  SERVICE_AUTH_USER_DATA_SUPPLY_KNOWFEED_BACKCHANNEL_ENDPOINT: https://casdoor-tls.app-platform-dev.svc.cluster.local
+  SERVICE_AUTH_USER_DATA_SUPPLY_KNOWFEED_AUDIENCE: "sunmoon-knowfeed-knowbase-user-data-supply"
+  SERVICE_AUTH_USER_DATA_SUPPLY_KNOWFEED_SUBJECT_ALLOWLIST: "admin/sunmoonai-knowfeed-knowbase-user-data-supply"
+  SERVICE_AUTH_USER_DATA_SUPPLY_KNOWFEED_REQUIRED_SCOPE: "knowbase:user-data-supply"
@@ -120,7 +153,7 @@ spec:
@@ -189,7 +222,7 @@ spec:
@@ -252,7 +285,7 @@ spec:
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/platform-computer/download.sops.yaml
@@ -1,26 +1,26 @@
-    name: knowbench-test-computer-download
+    name: knowbench-platform-computer-download
-    endpoint: ENC[AES256_GCM,data:+RYnMbmQDExADHXmHrrAGZIlrf4h/4it/XnIb21YzAAMDjcvXdaVIRnZV4fHh/PwDi7Dku62DDpw1cMPqx06,iv:orURi6VYPoH9cIAnLqZu56+YIKsRS6NNc3LUYNzS1vI=,tag:PxCOCMRKVB5bY8q3l2JdyA==,type:str]
-    region: ENC[AES256_GCM,data:bEBw9ou0Rs3/,iv:yR+Q5TZpyzACSr+AB/xJCp8UV5JEuCUsSs0LihvpMGk=,tag:ErS5HDMNZyE3u1DtXlcQqg==,type:str]
-    access-key: ENC[AES256_GCM,data:NoCRl8ibHSThys3n29KbRxFv05GDUX3x,iv:wFAiky42DxZiYC7J1PcRee6sArdbsL4P68/fz/PxMoc=,tag:IRWD4k9Y6jNmsDy4DyopLw==,type:str]
-    secret-key: ENC[AES256_GCM,data:oiIctS4EZr4mNPw5AOdJjaFdRb0qywSfG2fn+I6i2JjdaAkuWUTnSw==,iv:Av6FOvh4q21SBEO4roakRvsquKbi6TQuO1Aw/YZqNEk=,tag:BdiesWKkINIdpPohM9AFzQ==,type:str]
-    ca.crt: ENC[AES256_GCM,data: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,iv:hY3Mo9cB1NwiFQa0dfLmQd4+1ujOK6C1sUahJGZYjG4=,tag:2DxS9RFCM71J7NCGkqmkbg==,type:str]
+    endpoint: ENC[AES256_GCM,data:2wJpL083WsnskX9UlmEOGJd8nTjMSkLPbN8bFNIzyi39zUKjf0KAXBSKmKeNlkN9zlND9r5q85E2qxqEkLbQ,iv:W47DgkXi0S92oZlQpHIamk2yzBB8MqdR2ktWEag1ZBk=,tag:xXyIwB9bUFSJw4Yad3ZpZQ==,type:str]
+    region: ENC[AES256_GCM,data:aknnwuXFfrAJ,iv:zBYMO427B/kbekoKKutcUWNypcqcQ9yqURZVa342ebs=,tag:cRB06YnZvkfgHeMhR6kpVg==,type:str]
+    access-key: ENC[AES256_GCM,data:f/i3ESa5MThj37N9w3wBJCofLSmui02Y,iv:B1vA1VONT9jpZwnDL5Q1AZrKrKHvXrwrlpoBmGEX62U=,tag:aRXgtkQ53fEdihmhGN9BnQ==,type:str]
+    secret-key: ENC[AES256_GCM,data:j37nzP7Yiu7EzPt4u6h2Gvni4KYZQa+lbkB1rKYWF9qR8OdevgIu8w==,iv:dVZE1iWPjEyRujDRdssjz4dT4/FeMBeFNTMy7UBXMZk=,tag:pSL1FW5TLjYafv23ZH+J1g==,type:str]
+    ca.crt: ENC[AES256_GCM,data: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,iv:vadA3lV+qdEld7ejmdXM59/t88CZD5SFpmlW11mTRrs=,tag:mMdjeglh3xNa/PnhCUtw0A==,type:str]
-            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSAwMWlaVkJ3TmRENGZnZDdX
-            Tll4bTNMdnZMblNMWEFyd1lqaWlXbmYzREVjClJnNDRNSDV1d01tak9nUEZnNi9m
-            Wnd0K3pkdXZIMW02dnFPM3hmRUNHeFEKLS0tIGV5ejI0MHlqL1lOYmF0Zm1wZmQ0
-            K0Z4alF6alN5N2pHakNwYUEyamJScWMKgav1Pim9GSGLG2AXvA3YlHaX2WkfORP1
-            YCKwxdVBKt+ZCaoz9sswAzE4pMNg5Oj1t4u1oUv2i/kdqRlHip/L/Q==
+            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBCS0FzODNBZURMRHRNSmtL
+            WW5jRVFjSWVUY21qZjZFMjRFczB1N0hmMFhVClFQT01DMk13aVVDenlLVGZ6VDE1
+            UlJMZko3d0hQQUpHbFptcW1rd0hTYXcKLS0tIGlsbkF3KysvcTRIZWQ5SFhCd1Jl
+            Mzh3WTJ0eU8rMkpGQjluS05NejA5V2MKLPezlTwev325KaAual+/zD9vnt3Vdrig
+            JQkFiP70fSmZ5ge0PO+nHmasVHPTeBABPsuSqjWLJQLlRXIz878AoA==
-    lastmodified: "2026-10-17T13:40:26Z"
-    mac: ENC[AES256_GCM,data:EIZsBpG/f0inXlFeiw5l1gVAyyPMPjTxsFjkkeBu3wr/lJrzQiyYtBxCUi0TpiU1AQy0GkGYDw1IYWRVGswYpeeOK9yRitjrG/hNLn1xUTciOem41p/mSCAgi0ptae/nJG4Ym2RB4N+U1d2ag9USJ3eN6McVRCx5kg1oK1mms+A=,iv:oqezEGj1mMNGewMo4WwGn6smJLC4zv22GudOgWeX62Q=,tag:ELfNbHMDCAgMaf1HPvEv7w==,type:str]
+    lastmodified: "2026-10-29T02:53:58Z"
+    mac: ENC[AES256_GCM,data:sVhhx7tyjgRy5SCHxK6+VNq61E4isvXA6eVbHchUC4FwLPAh5nBYiwAto/MDEackd+L1Gjinwtcag0D+hVat3hA26+EoX3OINJWsZ8QsglYyXibuu81aBo6Thwl6FND0hKzMwSTPCoHcRbV83joIJaTmwAGLppvai8uw6GAWNSk=,iv:+gzw1CLxVyFqTrKR3kXAwTk/qqQXhOVT6v/+j/RTdNE=,tag:CBzomRiDErg5BjukLpyajg==,type:str]
+++ b/gitops/components/app-platform/knowbench-app/knowbench-backend/platform-computer/workload.yaml
@@ -1,17 +1,8 @@
-  name: knowbench-test-computer
-  namespace: app-platform-dev
-  annotations: {kustomize.toolkit.fluxcd.io/prune: disabled}
-  accessModes: [ReadWriteOnce]
-  resources: {requests: {storage: 20Gi}}
@@ -36,7 +27,8 @@ data:
-    # 第一次没有凭据：日志里显示连接码，所有者用测试账号在工作台「接入电脑」里确认；之后直接启动
+    # 第一次没有凭据：日志里显示连接码，配给的那位用自己的账号在工作台「接入电脑」里确认；之后直接启动。
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:fd433ace7bfec63457334a2e67b2fc8a46136a316df9b26ebe9800e9758bd046
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 71891c3250ebd4be308c3b264e6964306813183f
pointer-commit 6eff0fb83a80f0c911d2af14184f97da24e184d8
tag release-20261029-1
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
kustomization.kustomize.toolkit.fluxcd.io/knowbench-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-agent-releases condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowbase-user-data-output-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowbase-user-data-read-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowfeed-supply-demand-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowlab-read-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-knowmart-summon-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-migration condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-platform-computer condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-rabbitmq condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-redis condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-runtime condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-service-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-test-computer condition met
kustomization.kustomize.toolkit.fluxcd.io/knowbench-web condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-admin condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-database condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-directory-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-grant-test-identity condition met
kustomization.kustomize.toolkit.fluxcd.io/knowlab-knowbase-user-data-import-identity condition met
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
kustomization.kustomize.toolkit.fluxcd.io/knowlab-storage condition met
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
localhost                  : ok=50   changed=0    unreachable=0    failed=0    skipped=24   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-30 推送成功后可删。
