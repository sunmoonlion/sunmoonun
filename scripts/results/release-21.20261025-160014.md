# release #21：0042 批次 2/4 knowmart（供需市场、迁移 0008、买知识复制、身份 v6）

- 时间：2026-10-25T16:00:14+08:00；分支 fable；应用 knowmart；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/21/）
- 提交：deploy 7987146cb0f32429029b4879d6032f53939cdbb8；指针 d43ce2d62cf7f8245cc357df9473be2118a6223f；tag release-20261025-3；批准：批准人 admin  2026-10-25T15:55:19+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 9526cb1b..1a319534 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -48,10 +48,10 @@ applications:
     admin_revision: 2d5c1124c0b3f76ec0efda2371fadbd5f13787b0
   # 2026-10-16 由 tpl-app 4b19daf 实例化的空应用（qwen-003）
   knowmart:
-    parent_revision: a7f68471d5013ee972d4aeafdc6efb19a34ec228
-    backend_parent_revision: c00eebf376e804984f3eabd070daaed50573cc13
-    backend_revision: c00eebf376e804984f3eabd070daaed50573cc13
-    web_parent_revision: 50e280ea37609f0ca198a5d1308aa02bc4074dc8
-    web_revision: 50e280ea37609f0ca198a5d1308aa02bc4074dc8
-    admin_parent_revision: 107fda29642e9bf7259af274fa6d6c991302bfeb
-    admin_revision: 107fda29642e9bf7259af274fa6d6c991302bfeb
+    parent_revision: 09218c16a29cb9150b7758e1aca06798e928efde
+    backend_parent_revision: 928ad749fe0d5ac9a186b41de7baef13ca1d295f
+    backend_revision: 928ad749fe0d5ac9a186b41de7baef13ca1d295f
+    web_parent_revision: db315f20e6354ce9fdaee34b563a6d0a3ef2ef9e
+    web_revision: db315f20e6354ce9fdaee34b563a6d0a3ef2ef9e
+    admin_parent_revision: d14c3dc41293c660634a92aed2f1b14d46d5ef80
+    admin_revision: d14c3dc41293c660634a92aed2f1b14d46d5ef80
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml: digest: sha256:437e960c5872247d808aa2b111b46b57ecb8297fa44fd2c367807cf9d74a584c source_revision: d14c3dc41293c660634a92aed2f1b14d46d5ef80 
gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml: digest: sha256:3999e06f108550d4ab92e1b1ab69dd45e53a8918e32eb2d8f23e51dc23a1c272 source_revision: 928ad749fe0d5ac9a186b41de7baef13ca1d295f 
gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml: digest: sha256:633c94a34676b5274d716fbc85d45e29b223d8bbaa98f21540763be750bdd856 source_revision: db315f20e6354ce9fdaee34b563a6d0a3ef2ef9e 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowmart-admin-frontend/image.lock.yaml            |  6 +++---
 .../knowmart-app/knowmart-admin-frontend/workload.yaml |  4 ++--
 .../knowmart-backend/identity/workload.yaml            |  4 ++--
 .../knowmart-app/knowmart-backend/image.lock.yaml      |  6 +++---
 .../knowbase-user-data-purchase-identity/workload.yaml |  4 ++--
 .../knowmart-backend/migration/workload.yaml           |  8 ++++----
 .../knowmart-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowmart-app/knowmart-backend/redis/workload.yaml  |  4 ++--
 .../knowmart-backend/runtime/tls.sops.yaml             | 18 +++++++++---------
 .../knowmart-backend/runtime/workload.yaml             | 14 +++++++-------
 .../knowmart-app/knowmart-web-frontend/image.lock.yaml |  6 +++---
 .../knowmart-app/knowmart-web-frontend/workload.yaml   |  4 ++--
 12 files changed, 41 insertions(+), 41 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowmart-app/knowmart-admin-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowmart-admin-frontend-1af12695257e262d"}
+            - {name: DEPLOYMENT_ID, value: "knowmart-admin-frontend-437e960c5872247d"}
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/knowbase-user-data-purchase-identity/workload.yaml
@@ -125,7 +125,7 @@ spec:
@@ -139,7 +139,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'c00eebf376e804984f3eabd070daaed50573cc13'}
+            - {name: DEPLOYMENT_ID, value: '928ad749fe0d5ac9a186b41de7baef13ca1d295f'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20261018_0006'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261024_0008'}
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/runtime/tls.sops.yaml
@@ -5,20 +5,20 @@ metadata:
-    tls.key: ENC[AES256_GCM,data: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,iv:l/b2efl5awHnQmNb7Q0aeL3aBM/11fyl+yJ7U/Qk67U=,tag:dDI4pahyjJDl9tCV8Gi82A==,type:str]
-    tls.crt: ENC[AES256_GCM,data:IRNKSjq6ilJmGvcYChMTjnTNvxiMdUCWrwAyrOvqlYEtLHK7JaeSexU9BblZ4EBc8pdy5CGnqAKZam1YLTC2+lUcLUxTINZJQ7KEqjAHVAMiHhQSwMslP46UCK16IyCGsA+wPMVZsUXzYhSo7iJAssDV5I1HWtwAPs4e6m+kBKsALGsr5+KyZKl+R9tr0z8repBXrlDZrTwktA7x3YU3KjxQQzi0PB7lEvRBy5zreiab6Z2zZwpVVod7VRcMPBw6zLBYIHHz/xgMNpKTjdQqJLT1OapBmrnrqkDM8cEUawMcdqx5ngYIxYSFg9+sXVdbIwzWNpVCF+J1hc53vC6HxWvGjCaFIA0dygPJLP5REcyiMFu2Lbz2BEovYoGKLr7d0awXhptGth+Gxv5sW3clK6n3WcUbz+g7tJqbdUNxEmvnl+bafTlDfyLK1vZRpm61jSbXNPNTcQZxzMnrKwk8FL+L02RlolK2l1rYYCEzGrH0rj6ePDMHKeoCAwpkmGB+58aKidr1Q79Pwun5mos7/CtdhfmrzZqkP+/jSf9Wa/W/oMHhE3gqBZhtVKqqXmsoBRa+NKCjNLFy1m0Co9RmzIBANPJu0xo86romB8IJssQypAAR8qjbPQE/L5h1ZyyYWv3B4Ee4dYfBpXT9Cxof5I/uEH2jA6HJl7V8SQBCfUmbriqejp+/VxYNkaBzcJjlnBdq/n4znO8zonNSamtevtJ+60PSkJqFwvDM0BZTAT29bnlKtvSCA4vJI3Eqa1gOhopTZHAlEe6/ZtzGMniMgAtJnqLgIHkcg86uQZPRvschbaK+sDA37f8DmXR7XM2zvENNhjjootDzqmVWBmtpy1RalVfD3qZPTlNXdlIVNnWJPfqPCLlh2KlredD4s8D1XZqU7xOqsTwejeE/QxatlzK+poLzM9Sr+cERGSUUnj7n8nHwV60L8MPNE+jNLlcLaSPhZTmoNYCJ6JkOp6ibK4/aPgXZFv0sw5so35zj1qXY4nHDTOhujG21clLzPvQ+h8HfvoaHRBt1wxoFTP57zLvHfOu0ODXzuBkn2bTVQwLPBOZjWickpKTlJDd8Y4bpkdpiJ4XXzeiQyOf0sASoxsy72puNcA2ZpXd7Sze9TNkilLzyYeIPIo9H7EdvrWy7ySAEhUFu0CQv/fy8M3kzpWF22US+a1lFlCKDiTWYhL4NpxuOK8jC262QrRfqgEir3O0dzIvJDRDotE/w4U/Dar2RWL2BX7NTTOqZpE4w95mbGooyJck9UGrpg08wVNCkxBpcuv/fOAh1R4Hd6bSQAvCJLMvAfaRgOjKZdA7r+ofqIFNmvidR4oAMBSxkK21lTwkKLeUkcY6KD+XrQt+Gmevx0+FYj+Stt5MI7WMeseDmqvKsPEoOyG8YwSiVZzTHtbYtVCwHa27KVNV+Otp4egILPbsXVZoZGiOTbWu+LTIu/oswBvUV077yFZnDz+5kb17yAcff3zZvdkXKvM1IZAAhL0JkUkErwYs2BKdcgMk5J2htgggxW02+PaBeaDJSn7DkYXdz5WZBZfL9C0ZryS4+8rJxW40baTKG6IVk75tGJHKlNLAfxETsTZcGu2ewFaKM4QaA/9HVRyH0fQP3qE2xiq7JMkhLjCw7nI1ehqtQesXbWZVePrVLPkR1I0vDKGiCykx0OhKUQyU2udDBoND7WxQM10SL107dc3fmoJzOWslz85rc+hWwY4JIxUiNWFdSRrbboOUMF0PVs9JM5aS4CH2h0RN8YPPrtRZE24jH5j8e/x31AhbcJiGNwM6oVcuBRgSbM6fnZHiwzJqz5CRB2x2qGxqXdwoZJSJA7mpjKaiD7hXbFv8W7qPKZXVTMB+NqZ7bEZXkXF5sg+AyAeXiyd+LQxsYouPmNy2m1ROc4imC19PZkGUdraCOp3jPGaGLHfX7XraWVWAF7Mjdv5R6R0jBMBZPvk5QozIQR9r6B/SUL0RuWnJiwhYGMZb0yly9/r+nSRCmSfdGt4ndh35aOL281oB6StGxRoobi3f7AZSjK57UE4yw9zwjs5baQBSn1z0L0nHbVE1vh0LZL650XAEaiO89yOB84651xohp5q9f+PXHmv8wpguvakt22HZsNujui1Cvtu+dLhjujnjjasPDS8fQcJcMJFomX2xoPou9+xVv1165vRZ6rkH6Wq5pOMzM4hlFZOTJsuFglt57Mf+rXKvHwBUg7W0mBTR08SUAW+wV5H/s1JlAhQuV/7b4LDMjaiRllH+SIUbYfmw9JxA8hvo0MaZIvMUklNiqToDsnzX8pJYk3YDLltsvUQ/C/H3T2566VQ5yCE5MaxiKZs8ccfdoWiozLMk/JwdVONa5ByJmHgwq/cMGthhHj9qxES7iFZ0d9xQuFLLHSQCtsOgAKuSr1lUDJyNkyKC7B1B3BLdGFkwD6lW7e1k/Er/AhnjazMmsO6bcSqrq3RxLvIIXV5WePw4g4YTe2UBP+KJ+pxwEmsJPCIP2u/APgmimJzgxJ5PQxvDK/S7s0sTigRbNGPsVMSeAZ2aULWrzcr8ZI7oa4Br0nGAYp/Rb5oYj6ERfUouuxq3+0VYftRzPrG4+7a2AwAAXyKlELKaAEmaARGkHIe+t9h1LJ1dNiGc3oLVPhWEMgwDpzFcyRRHFdZ5EQMO4I+XL+0Sm6zIkzllkryjlSZGqaTKJzvaIp1JeBIYiUtXaSEJL5QfpBlpTXJGsV3Pw7medB7RYOkQlGfnDnd2qJOIDNfjctyyaH2Wv+/RU8efHjiqOrnhkLBqO1e1Lk0LhtiRr628NkeFAW8Itb7NwoS+w6+ciH81Wft2fj4h5I/WImY7/Bs3S2d3K/1NBqy60js3yzKwEq+qBXiG6FlFuuaU8SxqsXExHv42rywfbicUT6Quj6tXESdL1fxjstag2sQ9IPB88oTKs1g9S,iv:STHOd4UtgzEKHjwPD8KYFLKMI3n5VU+SlSxgAM1tKSg=,tag:QO/8yq+Pjmdhp3662tznbw==,type:str]
+    tls.key: ENC[AES256_GCM,data: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,iv:sQsE83UgnXWveo3izMM5WwXAZqPjfSPZ4EqwfN+A3pk=,tag:70WmTEKNlQoqOnxYuRR+Qg==,type:str]
+    tls.crt: ENC[AES256_GCM,data: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,iv:QK4ma8zZkP59vxciYFIK2S5Rbw5mhuLEukm9pb1Bdh0=,tag:YCaw5Wft2R3ELEqly/Mi3w==,type:str]
-            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBIOXBvamdKOEpCbVpKaFhr
-            d3ZTZkJGYmo2U3ptT29pb0lkcTIrRW9hdGwwClhUYmM5Q05XWWpxVGJuZWNMc3F0
-            UFdBbGFObFZXUnVRTG5FbXI5K1pEdTAKLS0tIHVKSXdmUzY0NGZFdzJ3Q1M2THZs
-            dUNYNVRQZFVOSWRrNmZ3Wlc0VFpWY0UKqrE88gYgje2iDR6AKjFyzBOrS/E5/pAG
-            U+cM9Pq37dH4CdqbSuBh12BMXqDAVHiZdkF2qDxOdFedw2vku7sv4g==
+            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSAwSEVjUitkS3Q4ZjRHNm1X
+            bzUyQWtpRmNBRkd6Q0ZOS3NKbFZDaGxPNXdrCkRqTDF6RmpFNXBqcHkxcWtEOVJv
+            anRmWHZudXpvdGJJdWgrT3BlRlNsaFkKLS0tIGs4amdFcXJ3T0dOeVQ4WURFOHM5
+            OHVhQ1JhcHBmejFiRmxncndYTFdBT0UKncg8+GlZ8vNeES7NyLni5+/0LnUXEmZ7
+            QCckIzr5XFUsDt9TwfafDGQrCxl6002dmr7r5y8w49i5Keo4uuJ62w==
-    lastmodified: "2026-10-25T04:43:41Z"
-    mac: ENC[AES256_GCM,data:g8EGf+TKnEJN6f9QG1e+zNnf4O92S7DDGOH2tq+mux6SERBDxUzzqwvZE4gd4cDD4EtHnHyOzOtsy7dl8vpQY19Pvdw1VWb/162IQa80GA/tXc4aHdwEXVeC9Wk7PnFugIo/cEWVRoVMYTeUlxGSWqlEXg9l5s60W/BmhSO85iY=,iv:3/yIumNWcpxpl7oOgeFEPHRDvgk6CUzO0SYohj26M84=,tag:TfUU0runBMqnvV7XVrYmOQ==,type:str]
+    lastmodified: "2026-10-22T01:57:03Z"
+    mac: ENC[AES256_GCM,data:OD7hbk4/0tGcsMIb86z4LQEqI3X4gS6AhdP4zwU253VawS1W/ogVQSs3AyrRVt3G41BPw++nax+3BJuUZwpIXPIcjsyM+8CPQiMVhVPgQfEtHc5k3aEirp0pGIOaNJUEOoTHIPftEBS9eouycX2P9Y6O8bye9XWIrECdkNNNt+8=,iv:fQIHHmQ9XF6WaBbc755L+chL9f/yU11io+L1KXZsCdM=,tag:n0eaPEgo6FspUru7bVnATg==,type:str]
+++ b/gitops/components/app-platform/knowmart-app/knowmart-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowmart-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowmart-backend-3a754bcd1f2e4196"
+  DEPLOYMENT_ID: "knowmart-backend-3999e06f108550d4"
@@ -72,7 +72,7 @@ spec:
@@ -82,7 +82,7 @@ spec:
@@ -134,7 +134,7 @@ spec:
@@ -144,7 +144,7 @@ spec:
@@ -192,7 +192,7 @@ spec:
@@ -202,7 +202,7 @@ spec:
+++ b/gitops/components/app-platform/knowmart-app/knowmart-web-frontend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowmart-app/knowmart-web-frontend/workload.yaml
@@ -20,7 +20,7 @@ spec:
@@ -29,7 +29,7 @@ spec:
-            - {name: DEPLOYMENT_ID, value: "knowmart-web-frontend-fc58c9e43d73271f"}
+            - {name: DEPLOYMENT_ID, value: "knowmart-web-frontend-633c94a34676b527"}
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:6a825242c4c43b9d042e2cfd52dfc32cc81feeb02e61d4e54bc2b6d904950e78
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 7987146cb0f32429029b4879d6032f53939cdbb8
pointer-commit d43ce2d62cf7f8245cc357df9473be2118a6223f
tag release-20261025-3
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

### 11-check-knowmart.log
```text
        "web_member_organization": "sunmoonai"
    }
}

PLAY RECAP *********************************************************************
localhost                  : ok=45   changed=0    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0   

make: Leaving directory '/mnt/sunmoon-data/jenkins/repos/sunmoonun/infrastructure'
```

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-21 推送成功后可删。
