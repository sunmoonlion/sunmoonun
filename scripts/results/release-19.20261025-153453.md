# release #19：0042 批次 1/4 knowbase（用户资料、迁移 0008、身份 v6；#18 已部署，本次补检查与写回 Git）

- 时间：2026-10-25T15:34:53+08:00；分支 fable；应用 knowbase；PIN=heads；由 Jenkins 任务 release 生成（https://jenkins.dev.sunmoonai.com:30443/job/release/19/）
- 提交：deploy 1c537637e68e7bbf905bfb26ca3be1b4775b2ea3；指针 62fd32f6f4befe7aa886300e77ea3fa55ccd9ee8；tag release-20261025-2；批准：批准人 admin  2026-10-25T15:29:51+08:00

## 改钉（2-sources.diff）

```diff
diff --git a/infrastructure/applications/sources.yaml b/infrastructure/applications/sources.yaml
index 5734174c..9526cb1b 100644
--- a/infrastructure/applications/sources.yaml
+++ b/infrastructure/applications/sources.yaml
@@ -22,9 +22,9 @@ applications:
     admin_parent_revision: b344c106c4f44522770b8cca3e9a8121e0b3ce32
     admin_revision: b344c106c4f44522770b8cca3e9a8121e0b3ce32
   knowbase:
-    parent_revision: a5051faf4c086e4d282217ce0e8225b4ec39bf8d
-    backend_parent_revision: ad1e2edcceb88e43df0842e1fe3be215406b855a
-    backend_revision: ad1e2edcceb88e43df0842e1fe3be215406b855a
+    parent_revision: b6bf588eb1163a9a62502238780c7a20802c16aa
+    backend_parent_revision: 8ca7fc88f1567da2976ecd53143addc443c48588
+    backend_revision: 8ca7fc88f1567da2976ecd53143addc443c48588
     web_parent_revision: 8c338db2b7222702f71cef892fd283016c148210
     web_revision: 8c338db2b7222702f71cef892fd283016c148210
     admin_parent_revision: f097495080ef6ef7296beb0fcc9430b4079d8011
```

## 镜像锁（3-image-locks.txt）

```text
gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml: digest: sha256:0d6765b3fbec8f01497d4e015a964eaf6ebac57c80576ca5c50528e48425d480 source_revision: 8ca7fc88f1567da2976ecd53143addc443c48588 
```

## 声明差异（4-gitops.stat；4-workload.diff 前 80 行）

```text
 .../knowbase-backend/identity/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/image.lock.yaml      |  6 +++---
 .../knowbase-backend/migration/workload.yaml           |  8 ++++----
 .../knowbase-backend/rabbitmq/workload.yaml            |  4 ++--
 .../knowbase-app/knowbase-backend/redis/workload.yaml  |  4 ++--
 .../knowbase-backend/runtime/tls.sops.yaml             | 18 +++++++++---------
 .../knowbase-backend/runtime/workload.yaml             | 16 +++++++---------
 7 files changed, 29 insertions(+), 31 deletions(-)
```
```diff
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/identity/workload.yaml
@@ -290,7 +290,7 @@ spec:
@@ -304,7 +304,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/image.lock.yaml
@@ -1,6 +1,6 @@
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/migration/workload.yaml
@@ -58,7 +58,7 @@ data:
@@ -72,17 +72,17 @@ spec:
-            - {name: DEPLOYMENT_ID, value: 'ad1e2edcceb88e43df0842e1fe3be215406b855a'}
+            - {name: DEPLOYMENT_ID, value: '8ca7fc88f1567da2976ecd53143addc443c48588'}
-            - {name: EXPECTED_SCHEMA_REVISION, value: '20260927_0007'}
+            - {name: EXPECTED_SCHEMA_REVISION, value: '20261023_0008'}
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/rabbitmq/workload.yaml
@@ -158,7 +158,7 @@ spec:
@@ -172,7 +172,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/redis/workload.yaml
@@ -102,7 +102,7 @@ spec:
@@ -116,7 +116,7 @@ spec:
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/tls.sops.yaml
@@ -5,20 +5,20 @@ metadata:
-    tls.key: ENC[AES256_GCM,data:h0u5tL/vEmsYxIoesdrz3Bov3wITwf/CkjORmYBNzvjBomhhURd/OzjZRSk/IystHFDyC7etpR/aVaoRhFlbDsdGFX0skCSjzHmKZD+1dtbihLnx9vyaO6MUg/95QPtZIjlZ4oGBuJmSEjOG92Ch0gxXPQHGWUOZFVXWzgYZFsc21VIzPzTyt2Zldp6qZn4ISU43qfyypRLEnxdI8R+P6qyLluqwGPkvgAsirDTjoAkTAd1lpwYMBbVx1N3zynFAeLIczfRUd7r7UAfKna5/CWBjTh+07uV43yxEBKZtLSpQVkziZdaHbZKVBNMdlVPJtbsS+kGvAPK3Skv1yxn8MQfOd9Vz24kxsUok00GzGqBKCzaH5NacqB44s8eUygaKocjVFakoxTK8ealQgOiSmkFPLAF3F0CL6DxoMMwgZQ18xu45dIz1DQLyo/X+z8GfEtLwyZYxoKtuKI9upxXbR2WQkxbRX4np1TgJ63ccTcpJYOzF8utTnP0vt/kVeMozkpxbRgZuTF5p4ETYEmeMeHiuVnUdpvEdBmODisIb7VhbeQmFb7Dc4GlOLwB3+xXf5nH7BlefRfKwrKKgGAk6cxDvXtMfr953luiC2kzuj89LO3RTOTg3EpIQbwsAcqg/ziegzKHoR0wq28OKRAtzw6CQXPC9J7/zboesO6icJ8sgf+lQ7ojYzqHMrvC89uwjodR2jepCDZ9aotOL4BAbkssJ/mqeRv2YXqYqlSrV6D3qt0133zRSbSSmG1JOER6gkn0ZAW9JtoFmFCChkc0xX8FZkUqHauPSJgsCkTJqKSnzlEnEKlBCtG9xJ/JqlsuJ7l/FLC6kF4whCtrMLMLHDpZNceAqv9Y+huE4AmSBrLoN1pZ05QwUMrFhg5gZSDwOT+kfNM2aOx10uLVKLRtm7NObx4G9sB94hzWr0pi1MGHkhDWfZAotmZX541od9hHlSqwA92tlMZ2ApEcOn3kJCdmKUva1piWeW3dtYgmk9W9A/MNY5wt5scvZ9tn/Yt7siwPI0YMVE/bZAfWesXInLC2E19s8NJasGxAvL2OwdKTOJp93CL3Rbj3HYtyPlxB/3fkwWeByIN5STopkxF5s6F+hKDJFZ696KH43T6WeujhYGmrK1Pm9pz1W/1L2nCl3zXj5uIwO3DTIfx7Q1/nB9QWhHI7jtwSzvRjKMxAm2ATleMWy3wPcv//6YQDCvk2oQIOPqjyLPTJ3gjXygASImXVNQuSR0WUULplwHguBpRehJpcu0rEHbuKz6UsdU8yj+ri9fgRcZn+A34BsbMyXhbntXEWY43S/m3kfMvzQtAUX+9i1La/utN2c1dtZ0BbkE7kUUKzOHxT1emiwqGU5djgkPDlZeOnkAx6eeaK+w0mATvk1LU+gMzlB3a9NvzSrssSQV1GQ1z4JjDaLZcBz6vRzLvj8RQifeTeqe0Vu4ypiXCtIQgrokWI5yt19bXGJhbevLLwJsS2yC2HMoq10sJ/nbxfVlGL0u9ijC98j4RBksmfWTQmtaOcIeiK3+K6Tux6YUSYwhrv+LeYNvBuQzZHcS8in36b99KZuciR/sFCu0m4/egKDmfXOL3w/5Zi6Cq0OLajgbbiHp1ws186HplS7Uh8gbEjPeOi4+ff/VWN3evgsQaavWUyzJ7906Qvh3LChUap99Dg/HB11gmqrIyRCOms958UNaq0UlotnEAMuENevM67DzwwIIBD5HuG6YFpYfBJC+4nQW6F9lAk//mBo+bUyKubnS7dXqqYbofi9mmRvV9yECE2IbhlLR9+w38RaQuTse9NGvxCEB/WulB36w/WK1BpIo9dN2S42IClDGyFP40KXHP0yonOhRdV8dOjD9y9sjjDXMPYPu7GBJ7xIEVj3fmjoGB++Ibmu1vbjgzddL/E+xrityz+H0495u+voUQqKnxIEuuic68rt3y9a/rhymZ0dMgtw6qIpgNmXrm5LhXQvriVBCjy4LEUrNavemBWHM6+4RhL/tCGxtLKRGj1rqBrtZNeAoBBkv44qy1JPsT4/gdHHzfolU70fm8Tf5JqS1uvzW8D5OKN2FDHSi85ZXNQ7yqPln5uH45Jaw7RoGrSGv1aaBo4oS/yJiiRl6r8cSnR/evnlBLmFP5qlgaZ4TvxMSXX3rlmlqQsGUWDZiStOfs6EzHwNkezmwotdNiNMb7B5aAQzXHg3hygIWFxjj7Gx8lUCwQy5ObykmbaPqLRyFIatXb1JVbFye/w65WDmfDqy99lTMxBSmVHFuI4u0wYjIgAthwcSadzE5gL+B24BrMU7hKblK8OYeGePLZV1ayd5NZbpf1s7VfAK2V2gJBOV0r33lwtfSdDm5g2Mq43n7eZzsKTIbO0wU8yC+jpgcPyKPjp8bcEMNIQjAtUHXAiV+owi2rQJVOgCaaTFkC+v16MdYmIRlr2bD3mJYlrM6tNIYcgVHczJfd0j9STrCugC1+X9cVtyKczZ3gWDuBaCOkQ0n4cLlADQi9UHEqqHh8WYyhKD996wDba5shbO589xljrlc3tICmSfKewTkWAldj4Jz1E5+OgApsL10m+o9PRAXD6ciSpeig8cXl8HGNFJgW3qn+gWE+gF20CqyfiTwQwAYB2hl/BfKE1kF92RVN+FKuQAQaRLf0yFUiCZJ/3qausJ7QGiAWYLiBChhJXZV+6U53oFd0Ju/ps9Gu9vWyRXG7M2VcwmdAiOzTfMC8YEahJljF19ERccG1O7MlNZGEJDNAiCBON0hmE0GPQNotymJxIpYYTKeGiFlkvxY2MSzVZc2GnlPCYPP8LfyQ4saTLuifkcX3l7DbbPZ80ryWEryCPFBAl8MESELnEJB4hso2t2VVtKb8tiDw/ys8gh1TrDICDLNYjmC9DP4gf0Iibc48lsey6SY2vJJmeVdXwWiU2wXR2SJMLQwikm4k8dxM/XqLx1oZQkthjn/inwFcw0177j+0E6h++OzIiRxxXGe5vBfmFGyfJFUTFe4dmLrl7lQeku/OLKqxFwNStdInEf11N6V/oa0Qa9fawlBKtyfvuxB9wKXbgpXHITj5qTZWnFVzDau5ikR2OS+BugtSTkr591wEs0MOlNty2dRI8/1HjIWOctiuX6eaZLpp800Jssm9jn300Zw2TeQvyyVcebqQmFlpS1lIf0ygh5rvaCp7lYZcySjAVRr4p4aGo99V5Bu4MG47ChNLcQynGhE55d7aDqleBTIsWZc1O0Fto5WitydKAblNxY7BKHZ/Ps1/T0euoY9s2T+ZRl5ysxeUv63Fv+5xgJrJ7GAeKpx9vwk+OoatFGWwkmtTcYtSpLdJy8ltd/XtntobxPR/UgmHXR1GKoSGTSc7sFpTQUVMUN3uCgMoxOjf5LZW9jmF9leJ7pHf8g0HwIo8rIKv/3Z5YXNjQgjLlMwsRfKIZJoNb6favLXfs3fnLZelPBpMsgXCs1VbN8Py9BkOec4peQvhpSiwrh1yoQiKF2GZ9FeS6ddqcDVF0ARFU/iBFt6yJh2GjYXGEMpJBhywrRi1+VL31zfHXKc4vmSGHiOm0kfp6igWBRVJQ//cMDWESmUPT/bFSB+XXFCpTI6JPtabHnnVLKFx8MIAehJ+OumsQ7MFX7SiciHHIanLEVmVxjs3zyiRk9E/kbPdD2j9WXL+eL1mBQHPOs7za3wx5qT4Mt4hq6r6FlVZh07AoYh64UZAU61J2U/l7XiM5MKb80H/1Od3imS/zFYerra+COaevSltlAYiNF64aG29LrxdRDU7DCjuJqD3XuaHjLghqfve5oBoStJP96eX5EyjjOb2Xa1ph16DWP+tdZImrChYZ+3EP99zI9IKUYUDyLEH1oGnhjaWu0kj8f0jGNxVHvmmP1vLitGDnSD8coTf7lICH6/tTurzpkXh5ddLnDuLc1LkdPKnFyGrhxtlq/sc4Sp6GJURbwwk1cadMyIZYleA41TsmbTg1KijX8Y3gEB5IJQk9io0+LjLbg4ypo5RWOTX+qkjgQjnCfOBKsRUnygaQSKbZA8CkNV34kqw2MBnznSC4ebMt2/nTB86t+WfsJOt+7ebJjezu0rfT8lL1WydOQUtD6xZbYI224C0Oh9zvdq1Rk73nGCpGHZBjQ0qThMbQS+6VJLWMgQKzkN+LFF/tLgrgTm6Tm1xxHib6avRlgYqWpKUZo407SVVhOUn5n6N2wf6We3RYfgt/0SRtsE7faWZdPikvoI0xWlCZdHtaOyLZfH4QgSmROtwzAradA8Sc8toZ7ZBmn6MZTqPa2JMPXelz/h+700Jdc8iUAXZ+STLUk715UHjE7iwX6+NZecK3mz3l04cvnvt5YbXo7uMmDnnhO1dQMfeVBeH8dCeQAluX9w1ju7rGssJLHrZqc/9gD6MhLKzjtFA/FSpk69ntVLUbybRDURlqk9FZg,iv:w89R/+aKj3jSMzL/tWZTgk17JSThJrNUBO9FvIBo5/w=,tag:0O7AJVxpCtAOpKbtxmYysg==,type:str]
-    tls.crt: ENC[AES256_GCM,data:bDSUQM0iGNmjDpUDR8+//gihrMxyaz+KcHL2WkNnCqnfhEE3aQzBdgK6UEb8+tvdUKZjs9ScC3AfQX7rBuPP3WoEUpzihFAkNJ3CzLNyWfgMq9FMqwxdpNO9lqCjZB5t/JFZlWLGCt1rBzaj95Z1UejoAcFsmyPrDpvp1lkFMT+8p2x+AAzteqpbWKr3n1HeOZLLnhpL+xI+FScLZ0TfYHJU6+GwWmPHRKdFB+HtNz0I/Xrf1qwrv5kmMJ6jpvrErMEK51XTLggq/cxIM/XeQpjLc+LdKe99rCG3u/EJGY6soxeRJdumwwtK5gyoy0u9OkfPkwDdi0CK2pFGkUMlp4qgS43DVX59RZDc1ilst/ortNSvODGcECh8KEmtbkzSi/5zlpR06fJfHfvd/ZwmpJAfn9pUin+zbVsfWoEdDn9YC6eWhKFDxl1Tv8f56CLGNMgm3ZVM2qXbK7fb/v87j/xiKx+1BAKN7eBbcmjcFmDQvklHzZCufpa43eB/Aqv100t3kr+5fYwoxtKGt7G0LCO7Io7rZuwxvrptFBXZBZlodvJW+04aWO4O+vHtNBZO+xd7s+PivC0lB2qympCF6MQ8kbf3T3N2Ns+OVwIuDKluh6xcxt7t7L5l9d3Q9QM24hOhC/Wvrk33bhs5lCsnGwbmfqEtfiB953mC5j9dsu6BJCM6cc7RE9fD91zh5laTlqQEsiag1/OqaZeyX+HqesaA5to6SCjJrQUy3S9kC66aJ+Vm+A5anJhk6uL/qC3cO25StOIKuCaM+Lt/aBL2Eq12kRPhbURN3ONq9HnWF4PI6Pg0l8OdH8Pwm/CfylXaMVE3agHiWhGiDeY+ZaoakCS9H2Vx6kftzAiEKHupgjj4t1EAOGWAo+cogBgR4D2lq70TjF5XYgxS8G6GIz6Ttoldrde37nQBpJeDk3C7FjgyEs7Dw9VKQpiQYZKx8pnNGkiZebg0gYZhMgrWTeHr3vkPIiSO3mec6E4gOv6OBrpjoRtvdvbkJzigc8vRlULuBnnOwcgp/1I4dm6tGjOhK1T6O0ofBV9LVja4mOB3gIS9aAbruYWZu3ZWutgLAdvNyc7r0cV7r+RGB6We49uIUXpZWc0afwRv+0NcuwVvmPKsPIOEWsoIApxl/2j0B7Xhk1A2xcbcnCOIvgyvXHMCGKwbJNDhnbLbKIi9K7wAhXjMRcjuDQWrC//b2wrv1yqKQCLseIJiSo7UnQrSCuOUCPOXY/5LiyMc5cBMVLIDuJtrGOEs7AnJa4nhsLLWX7VyjjEvMHOV0rGdG+QDQFm3Wmn52/91wCnPhcedpUSJwz6yd7+cnKcW29l2HfNS8FZ5IMRNV12wsNCiyYSZ00UN7FuySymvCUwOaS/pkpKXgPNsTaAh1OiBw6uNK6pv59i7MiIGbXPgn3YoqxdmGmW/d3mddg7asEhQ/INSJCqKUla6nQF0X38r/SlKw//u57PZW8KN6uMALFRDqam7nIfCl10hIz2J7EepM1nDOMBMowlgeFJDK5e+kTncdTxUDB3yhPZr+L5Uj/T3Ow5+KLcv85dKvxrTDJ1/WO9Hboq+y2ei1SYVjzkfM4vyDUohVOkX3b2yL2C3r0Kua8fQltoKKYgGDANDy0k82Cx8kPAfu2fgYaodmWv9eS8TqqUm1PxxAxgpq7eedOUwllrQCTCl0V5vixdu6aeCm4dq+dwv/oIpaLqAYzlhjElZIGyAtntkt0FpDYPHsEe/RyQrJcKkiedgmjIZA0CnzACMS3ilawvsphXoUUOxv2/TpJXfu+k3mXdtwwu8n1RyzRT5DgKxq+kAbVNOIUn2wd/nkutXryzPFFkIXuLmcl6c8uvsZ6gbmKS+jwYPEgZp7Be8uPPLYo1RvyTw8p8x9We0Pqb9LLHyvVynvpsov2zPgVqacYKhF4dvi70Ag4d/vvxMrEUE+aXOyNlzpgOJWGFmr4hgHpRsqoavEIsx6yAMZbEYvhU/R+dCZGsNl7xMuCRTJobif/v1Wr7N6trLxIz88DAVEMxizH0lnOpiYOMeJzrpcvttqIyzzCc1j+f5vLWd0NcMiOcnEZ8hyvS0fTOCyw6Ovow4gHyBkMqXTSC4zTYyYvFAcWKuDYR8h9r0x4ngYa6bQIam/taTGgbb5drDP41Fle9lwN8pvZcz5uyD8ujU7W7aFWJPNdzT/U7V1bYZMAphZnwevZkS4lhr61ZACAVLt5/n9e5V4vNVhaHCWaQ33O/6Xt1Eh7KcGPp4pIVgfQ3xjsPNIyUS8atxt8rmr55KW5GKOc+QVKPHo/8KONatTppXnZEXmB8wh1Jkx/X7LbCW8Ho5NzD9/VjvHNzvw1lJ7mN7YixWe43GN/2KpcFa+8poddaS7IFUW0hvPGUF7HiTGju3FlTA6bUlTGxsIqKuwCSun4fMW0JpQGqgaE0vR3RrNui07A4OTOBZUO1k/WCjxzMPuwIZ3UhwUkCm7RJhzGdEi80L8RX17WcyEqocxkFXSrXy8ChubNeggTFIe9V0PA3ohz/MgQ7yhEp0RkggI5IAvIfclNVMtfUM9KxhXOyfGWeMrV+F+iAqDRqclV7u8eBqfQcWRQHXaMtk6RhRcaHVx3e/vkX5fbljx5HezGFhhcJy7wxBXtEDSqN8PTx2yVGNsZWI4mcYmZmYR5dyNa6n1AwGSAKDFPWVnEi0LIFiPwa1Lav3q2p7FcreOIWmHxtYpY2LlR0c0hPhbf2xxp4r4PqepVlszvlowOMg6yF5B4bScLlNHiJXrH++71iPHPAjn7cy/xZqUHh3J1347jEFaHG+WqZ1Wyz9eux+HSeTMvXrN+yUMRf73kZlm4bHFn5HAIKFi3Mpsko+Q6/gIKp5JjsLC0D3+6qC4XiJOqPa5NEseti6AzQURM4ha+rSH4OCgGhlvAq3ysaOCSTSHZ45g4GQ,iv:vevLxJEYqn967gruVI2HD5+0hHzk6XPAq5Vtrp+b8Oc=,tag:L7mJkawQa3+Xe1Vav7l0bQ==,type:str]
+    tls.key: ENC[AES256_GCM,data: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,iv:EEajK6FMkCMSlHWNaAlUFDpIRzwRG1VW7xPrXhEwCtU=,tag:J0vf78r0DU+pY8YZc/BfIg==,type:str]
+    tls.crt: ENC[AES256_GCM,data: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,iv:r3Dpm6TWsEZlkSvUhKCl0Izv/Xcp+JhgdxL5BuCgZyM=,tag:YqzvWaJTyQqbZBUwWXvnSQ==,type:str]
-            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBkKzZRVzZBWXpIdlE1WG16
-            WHgrWlZLczJjcVFheTJSSmNZdC9Xblpoam1BCjVqVmo1Zk8rT2RJdUk3TnlabnRy
-            WVFwODJld2ZDNmZZWlVnM3FZTzB6RjAKLS0tIDRycFdwaDVSL1IxRXoxYUxZTkpV
-            MmVyTU1VWXB6aDVGSFBacW9GaE1ReHMK5CABDpIc3uN99XkKm2Nf8+Leis4EAVbU
-            ZrRRaBZH1V0Tj0sfKi7ETLH7DQ9Q/f+Vb4KRocHyOUZJhfM0RscQAw==
+            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBMS2VVaXAzbHhzQ3lSYitp
+            UnErTFhkOGtLalJwSGt3MjlPWXJubTBrM2dJClRwYnlOY3R4UkVKelU5V21GRFVo
+            L1V3S1l6cmZORlpsMThoWUJVVWw0LzQKLS0tIDlrZ3c4MkIveGtPalZ0dW1HNnRH
+            cTNDcHYvUzR4RUViUHQzWThYWHYrdFkKOHuObovRUyBMIo10U/H1Ms0c1i4r9Y87
+            +ZFPTwZ1SYzZ2JH29Yiit3vsLEYO9uyRpQFR0NYqySgBLMzmz0nuBw==
-    lastmodified: "2026-10-25T04:37:49Z"
-    mac: ENC[AES256_GCM,data:DvVWvYUEErC2kv6ETXJkpbxGUPrXi8VYF+6/H6+fNykBrqIyvbIrShtd53bY1JR08D0ipUWl84AH63QpysYpTgdSFQQk1Bi6G3rqhEj6iOq5U2X0zR6MVhv1ggeH8z5AtjEcnLJQBMMZY8jZQSDRsFoypc/s0jHv2QOeajMPNu4=,iv:8TAwZEMDDXkletZ2TMKIwLATrXv5yUd98nQCspL1cvE=,tag:sxr1h8O0BJLfWVNP7/RoBg==,type:str]
+    lastmodified: "2026-10-22T01:53:44Z"
+    mac: ENC[AES256_GCM,data:Z5jquoR2QgJptRSz04hWcoV+kwtl0WRGyAwS+Da3jsjqYnr+0jSwxYKQfG3RmAyvUTQbosDnOYd98eTsG1qOtrZeXwd7PFyzykAoQaL98b7D2kTrrSvpriAfbF8Spd1aIC5EzxRW/SGL+D7Ku13MI0y3upH8VwUZPBaSy40djtQ=,iv:mB8QzcF5RPZzGwoJMaTuwtREnZ/xpbUoBZEWvQF5CAA=,tag:s7X2PITjFiAxfbXt4Hnq3A==,type:str]
+++ b/gitops/components/app-platform/knowbase-app/knowbase-backend/runtime/workload.yaml
@@ -4,7 +4,7 @@ metadata: {name: knowbase-runtime, namespace: app-platform-dev}
-  DEPLOYMENT_ID: "knowbase-backend-52e6b4ffea7b6af1"
+  DEPLOYMENT_ID: "knowbase-backend-0d6765b3fbec8f01"
@@ -118,10 +118,9 @@ spec:
-        sunmoonai.com/object-storage-client: 'true'
@@ -131,7 +130,7 @@ spec:
@@ -189,9 +188,8 @@ spec:
-        sunmoonai.com/object-storage-client: 'true'
@@ -201,7 +199,7 @@ spec:
@@ -254,7 +252,7 @@ spec:
@@ -264,7 +262,7 @@ spec:
```

## 候选与指针（7-source-candidate.yaml / 9-pointer.txt）

```yaml
digest: sha256:c191afb26ebaa66f8efe12dbafbcf7ce057afe915746ad50e616d4429306e25e
path: ./clusters/kind
repository: oci://harbor.sunmoonai.com:30443/platform/deployments-kind
requires_sops: true
revision: 1c537637e68e7bbf905bfb26ca3be1b4775b2ea3
pointer-commit 62fd32f6f4befe7aa886300e77ea3fa55ccd9ee8
tag release-20261025-2
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

完整控制台与全部产物在 Jenkins 构建页；代理克隆里的分支 abandoned/release-19 推送成功后可删。
