# 0042 knowbase 本人凭据：Casdoor 令牌交换实验（Opus，远程机）

结论：Casdoor 4.12.0（与正式环境同一镜像，摘要前缀 `bf84c727d59d`）的 RFC 8693 令牌交换可直接用作 knowbase 的「用户本人凭据」。应用后端拿本应用发给用户的访问令牌去换，换出的令牌 `aud` = knowbase、`azp` = 代办的应用、`sub` = 用户编号，权限只能收窄；别的应用拿不到、换不了；吊销后换不了。

## 做法

临时 Casdoor 4.12.0 + 临时 postgres（远程机 docker，独立网络，只听 127.0.0.1:38000，测完删除）；组织 `sunmoonai`；应用 `lab-knowbench`、`lab-knowmart`（打开 password、token-exchange 授权类型）、`lab-nox`（不打开 token-exchange）、`lab-knowbase`（目标）；用户 `labuser`。用户令牌用 password 授权取（格式与浏览器登录取到的相同），只打印声明，不打印令牌。

## 结果

| 试了什么 | 结果 |
| --- | --- |
| 用户令牌（发给 lab-knowbench） | `aud` = [lab-knowbench]、`azp` = lab-knowbench、`sub` = 用户编号、`owner` = sunmoonai、`name` = labuser、`scope` = openid profile、1 小时 |
| lab-knowbench 换成给 lab-knowbase 的 | **成功**：`aud` = [lab-knowbase]、`azp` = lab-knowbench、`sub` 同上、`scope` 不变、1 小时；回包没有 `issued_token_type` |
| 收窄到 `openid` | 成功，`scope` = openid |
| 放大到 `openid admin` | `invalid_scope`：requested scope 'admin' is not in subject token's scope |
| lab-knowmart 拿 lab-knowbench 的用户令牌去换 | `invalid_grant`：subject_token audience does not include the requesting client |
| 目标应用不存在 | `invalid_target` |
| 应用没打开 token-exchange 授权类型 | `unsupported_grant_type` |
| 客户端秘密错 | `invalid_client` |
| 管理员把用户令牌改成过期（吊销）后再换 | `invalid_grant`：subject_token is revoked or unknown |

## 对实施的输入

1. 各应用（knowbench、knowlab、knowmart）的 Casdoor 网页端应用要加 token-exchange 授权类型；knowbase 建一个目标应用（只作 `audience`）。
2. 应用后端的会话要存用户的访问令牌（现在登录时只验 id_token、访问令牌丢了），存在服务端会话里，不给浏览器；换出来的 knowbase 令牌只在后端用、不落盘。
3. knowbase 验：签名（JWKS）、`iss`、`aud` = 自己、`exp`，再按 `azp` 认是哪个应用（只认 knowbench、knowlab、knowmart 三个的客户端编号），用户 = `sub`。现有 `oidc.py` 的 `verify_access_token` 管前四样，`azp` 要新加。
4. 用户令牌 1 小时过期（实验应用设的）：正式环境的 `expireInHours` 与刷新令牌要和会话时长对上，实施时核。

## 脚本

放 scratchpad 跑，不进仓。`provision.py` 建组织、应用、用户；`exchange.py` 跑上表前八行；`revoke.py` 跑最后一行。

### `provision.py`

```python
# 一次性 Casdoor：组织 sunmoonai、三个应用（模拟 knowbench、knowmart 两个网页端与目标 knowbase）、测试用户
import json, sys, urllib.request, http.cookiejar, datetime, secrets
L = sys.argv[1]; B = 'http://127.0.0.1:38000'
cj = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def api(m, p, b=None):
    d = json.load(op.open(urllib.request.Request(B + p, data=json.dumps(b).encode() if b is not None else None, headers={'Content-Type': 'application/json'}, method=m)))
    if d.get('status') != 'ok': raise SystemExit(f'{p}: {d.get("msg")}')
    return d.get('data')
api('POST', '/api/login', {'application': 'app-built-in', 'organization': 'built-in', 'username': 'admin', 'password': '123', 'type': 'login'})
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
base = api('GET', '/api/get-application?id=admin/app-built-in')
api('POST', '/api/add-organization', {'owner': 'admin', 'name': 'sunmoonai', 'displayName': 'SunMoonAI', 'passwordType': 'bcrypt', 'passwordOptions': ['AtLeast8'], 'enableSoftDeletion': False, 'createdTime': now})
out = {}
for key, grants in {'knowbench': ['authorization_code', 'password', 'urn:ietf:params:oauth:grant-type:token-exchange'],
                    'knowmart': ['authorization_code', 'password', 'urn:ietf:params:oauth:grant-type:token-exchange'],
                    'nox': ['authorization_code', 'password'],
                    'knowbase': ['client_credentials']}.items():
    sec = secrets.token_hex(16); out[key] = sec
    api('POST', '/api/add-application', {'owner': 'admin', 'name': 'lab-' + key, 'organization': 'sunmoonai', 'displayName': key, 'category': 'Default', 'type': 'Web',
        'clientId': 'lab-' + key, 'clientSecret': sec, 'redirectUris': ['https://' + key + '.example/cb'], 'cert': base['cert'],
        'grantTypes': grants, 'tokenFormat': 'JWT', 'tokenSigningMethod': 'RS256', 'expireInHours': 1, 'refreshExpireInHours': 0,
        'enablePassword': True, 'enableSignUp': False, 'isShared': False, 'signinMethods': [{'name': 'Password', 'displayName': 'Password', 'rule': 'All'}], 'createdTime': now})
json.dump(out, open(L + '/client-secrets.json', 'w'))
api('POST', '/api/add-user', {'owner': 'sunmoonai', 'name': 'labuser', 'displayName': 'Lab', 'type': 'normal-user', 'password': open(L + '/user.pw').read().strip(), 'createdTime': now})
print('provisioned')
```

### `exchange.py`

```python
# 令牌交换实测：只打印声明里的键与非敏感值，不打印令牌本身
import json, sys, base64, urllib.request, urllib.parse, urllib.error
L = sys.argv[1]; B = 'http://127.0.0.1:38000'; sec = json.load(open(L + '/client-secrets.json')); pw = open(L + '/user.pw').read().strip()
def post(form):
    req = urllib.request.Request(B + '/api/login/oauth/access_token', data=urllib.parse.urlencode(form).encode(), method='POST')
    try: return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e: return json.load(e)
def claims(tok):
    p = tok.split('.')[1]; return json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4)))
def show(label, c):
    keep = {k: c.get(k) for k in ('iss', 'sub', 'aud', 'azp', 'owner', 'name', 'scope', 'tokenType') if k in c}
    print(label, json.dumps(keep, ensure_ascii=False), 'exp-iat=', c.get('exp', 0) - c.get('iat', 0))
TX = 'urn:ietf:params:oauth:grant-type:token-exchange'; AT = 'urn:ietf:params:oauth:token-type:access_token'
user = post({'grant_type': 'password', 'client_id': 'lab-knowbench', 'client_secret': sec['knowbench'], 'username': 'labuser', 'password': pw, 'scope': 'openid profile'})
subj = user.get('access_token'); print('password grant:', 'ok' if subj else user)
show('subject token  ', claims(subj))
r = post({'grant_type': TX, 'client_id': 'lab-knowbench', 'client_secret': sec['knowbench'], 'subject_token': subj, 'subject_token_type': AT, 'audience': 'lab-knowbase'})
if r.get('access_token'): show('exchanged token', claims(r['access_token'])); print('  response keys:', sorted(k for k in r if k != 'access_token' and 'token' not in k), 'token_type=', r.get('token_type'), 'issued_token_type=', r.get('issued_token_type'))
else: print('exchange FAILED:', r)
r2 = post({'grant_type': TX, 'client_id': 'lab-knowbench', 'client_secret': sec['knowbench'], 'subject_token': subj, 'subject_token_type': AT, 'audience': 'lab-knowbase', 'scope': 'openid'})
print('downscope openid:', claims(r2['access_token']).get('scope') if r2.get('access_token') else r2)
r3 = post({'grant_type': TX, 'client_id': 'lab-knowbench', 'client_secret': sec['knowbench'], 'subject_token': subj, 'subject_token_type': AT, 'audience': 'lab-knowbase', 'scope': 'openid admin'})
print('upscope admin  :', r3.get('error'), '-', r3.get('error_description'))
r4 = post({'grant_type': TX, 'client_id': 'lab-knowmart', 'client_secret': sec['knowmart'], 'subject_token': subj, 'subject_token_type': AT, 'audience': 'lab-knowbase'})
print('knowmart swaps knowbench token:', r4.get('error'), '-', r4.get('error_description'))
r5 = post({'grant_type': TX, 'client_id': 'lab-knowbench', 'client_secret': sec['knowbench'], 'subject_token': subj, 'subject_token_type': AT, 'audience': 'no-such-app'})
print('unknown audience:', r5.get('error'), '-', r5.get('error_description'))
nox = post({'grant_type': 'password', 'client_id': 'lab-nox', 'client_secret': sec['nox'], 'username': 'labuser', 'password': pw, 'scope': 'openid profile'})
r6 = post({'grant_type': TX, 'client_id': 'lab-nox', 'client_secret': sec['nox'], 'subject_token': nox.get('access_token', ''), 'subject_token_type': AT, 'audience': 'lab-knowbase'})
print('app without token-exchange grant:', r6.get('error'), '-', r6.get('error_description'))
r7 = post({'grant_type': TX, 'client_id': 'lab-knowbench', 'client_secret': 'wrong', 'subject_token': subj, 'subject_token_type': AT, 'audience': 'lab-knowbase'})
print('wrong client secret:', r7.get('error'), '-', r7.get('error_description'))
json.dump({'subject': subj}, open(L + '/subject.json', 'w'))
```

### `revoke.py`

```python
# 吊销后再换：管理员把这张令牌的 expiresIn 改成 0（等同吊销），再拿它去换
import json, sys, urllib.request, urllib.parse, urllib.error, http.cookiejar
L = sys.argv[1]; B = 'http://127.0.0.1:38000'; sec = json.load(open(L + '/client-secrets.json')); subj = json.load(open(L + '/subject.json'))['subject']
cj = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def api(m, p, b=None):
    d = json.load(op.open(urllib.request.Request(B + p, data=json.dumps(b).encode() if b is not None else None, headers={'Content-Type': 'application/json'}, method=m)))
    if d.get('status') != 'ok': raise SystemExit(f'{p}: {d.get("msg")}')
    return d.get('data')
api('POST', '/api/login', {'application': 'app-built-in', 'organization': 'built-in', 'username': 'admin', 'password': '123', 'type': 'login'})
toks = api('GET', '/api/get-tokens?owner=admin')
mine = [t for t in toks if t.get('accessToken') == subj]
print('found subject token record:', len(mine))
t = mine[0]; t['expiresIn'] = 0
api('POST', '/api/update-token?id=admin/' + t['name'], t)
form = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange', 'client_id': 'lab-knowbench', 'client_secret': sec['knowbench'], 'subject_token': subj,
        'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token', 'audience': 'lab-knowbase'}
try: r = json.load(urllib.request.urlopen(urllib.request.Request(B + '/api/login/oauth/access_token', data=urllib.parse.urlencode(form).encode(), method='POST')))
except urllib.error.HTTPError as e: r = json.load(e)
print('exchange after revoke:', r.get('error'), '-', r.get('error_description'))
```
