"""Verify browser protocol and SSR against an explicit TLS entry; never print secrets."""
import http.client
from http.cookies import SimpleCookie
from html.parser import HTMLParser
from datetime import datetime, timezone
import json
import secrets
import socket
import ssl
import sys
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit


# 管理员读得出的一张管理端列表（只读）：路径由应用在 gitops 的 <app>_deployment.admin_list_path 声明（账 173），
# 没声明就跳过这一项。knowfeed、knowbase 的旧接口（security-requests、knowledge/datasets）随旧版删了，等有新的管理端列表再声明


def require(value, label):
    if not value:
        raise RuntimeError(label)


class LoginRedirectHTML(HTMLParser):
    """Read Next's actual streamed redirect, not strings in RSC scripts or inert HTML."""
    inert_tags = {'script', 'style', 'template', 'noscript', 'textarea', 'title', 'xmp',
                  'iframe', 'noembed', 'noframes', 'plaintext'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inert = []
        self.refresh = []
        self.redirect_ids = 0
        self.has_base = False

    def handle_starttag(self, tag, attributes):
        if tag in self.inert_tags:
            self.inert.append(tag)
            return
        if self.inert:
            return
        attrs = dict(attributes)
        if tag == 'base' and 'href' in attrs:
            self.has_base = True
        if attrs.get('id') == '__next-page-redirect':
            self.redirect_ids += 1
        if tag == 'meta':
            require(len(attrs) == len(attributes), 'web: ambiguous redirect HTML attributes')
            if (attrs.get('http-equiv') or '').lower() == 'refresh':
                self.refresh.append(attrs)

    def handle_startendtag(self, tag, attributes):
        # HTML void elements (meta/base) may use '/>'; non-void inert elements
        # remain inert even if written with a self-closing slash.
        self.handle_starttag(tag, attributes)

    def handle_endtag(self, tag):
        if self.inert and self.inert[-1] == tag and tag != 'plaintext':
            self.inert.pop()

    def destination(self):
        require(not self.has_base and self.redirect_ids == 1 and len(self.refresh) == 1,
                'web: missing or conflicting streamed redirect')
        meta = self.refresh[0]
        content = meta.get('content') or ''
        require(meta.get('id') == '__next-page-redirect' and content.startswith('1;url='),
                'web: invalid streamed redirect')
        return content[len('1;url='):]


def check_login_entry(browser, origin, surface):
    status, headers, body = browser.request(origin + '/zh-CN/login')
    if surface == 'admin':
        require(status == 200, 'admin: login page unavailable')
        return
    if status == 307:
        destination = headers.get('location', '')
    else:
        require(status == 200 and headers.get('content-type', '').split(';')[0].strip().lower() == 'text/html',
                'web: login did not return an HTTP or streamed redirect')
        parser = LoginRedirectHTML()
        parser.feed(body.decode('utf-8'))
        parser.close()
        destination = parser.destination()
    require(destination and destination == destination.strip() and
            not any(ord(char) <= 32 or ord(char) == 127 for char in destination) and '\\' not in destination,
            'web: invalid login redirect destination')
    target = urlsplit(urljoin(origin, destination))
    require(target.scheme + '://' + target.netloc == origin and
            target.path == '/api/auth/web/login' and not target.fragment and
            parse_qs(target.query, keep_blank_values=True) == {'return_to': ['/zh-CN/dashboard']},
            'web: login did not continue to the exact local SSO entry')


def check_lifetime(browser, origin, surface, session):
    expected = 86400
    remaining = (datetime.fromisoformat(session['user']['expires_at'].replace('Z', '+00:00')) -
                 datetime.now(timezone.utc)).total_seconds()
    ages = browser.session_ages.get(urlsplit(origin).hostname, {})
    require(expected - 90 <= remaining <= expected, surface + ': unexpected session lifetime')
    require(len(ages) == 1 and all(expected - 90 <= age <= expected for age in ages.values()),
            surface + ': unexpected session cookie lifetime')


def sso_login(settings, browser, client, application):
    """Complete authorization using only the existing provider cookie, never a password."""
    origin = client['origin']
    check_login_entry(browser, origin, 'web')
    status, headers, _ = browser.request(origin + '/api/auth/web/login')
    require(status == 302, 'SSO login start failed')
    target = urlsplit(headers.get('location', ''))
    query = {key: values[0] for key, values in parse_qs(target.query).items()}
    require(target.scheme + '://' + target.netloc == settings['provider'] and
            query.get('client_id') == client['client_id'] and
            query.get('redirect_uri') == origin + '/api/auth/web/callback' and
            query.get('code_challenge_method') == 'S256' and bool(query.get('state')),
            'SSO authorization identity mismatch')
    aliases = {'client_id': 'clientId', 'response_type': 'responseType', 'redirect_uri': 'redirectUri'}
    login_query = {aliases.get(key, key): value for key, value in query.items()}
    status, _, body = browser.request(settings['provider'] + '/api/login?' + urlencode(login_query),
        method='POST', data={'application': client['name'], 'type': 'code'},
        headers={'Origin': settings['provider']})
    result = json.loads(body)
    require(status == 200 and result.get('status') == 'ok' and
            isinstance(result.get('data'), str) and bool(result['data']), 'Passwordless SSO rejected')
    status, headers, _ = browser.request(query['redirect_uri'] + '?' +
        urlencode({'code': result['data'], 'state': query['state']}))
    require(status == 302 and headers.get('location') == origin + '/zh-CN/dashboard',
            'SSO callback rejected')
    status, _, body = browser.request(origin + '/api/auth/web/me')
    session = json.loads(body)
    require(status == 200 and session.get('authenticated') is True and
            session['user']['app'] == application and session['user']['surface'] == 'web',
            'SSO session identity mismatch')
    check_lifetime(browser, origin, 'web', session)
    return session


def check_switch(settings, browser, client):
    origin = client['origin']
    provider = settings['provider']
    status, _, before = browser.request(provider + '/api/get-account')
    account = json.loads(before)
    require(status == 200 and account.get('status') == 'ok' and isinstance(account.get('data'), dict) and
            all(isinstance(account['data'].get(k), str) and account['data'][k] for k in ('owner', 'name')),
            'Provider session missing before switch')
    status, _, body = browser.request(origin + '/api/auth/web/switch-account')
    require(status == 200, 'Switch preparation failed')
    token = json.loads(body).get('csrf_token')
    require(isinstance(token, str) and len(token) == 43, 'Switch preparation token invalid')
    for headers in ({}, {'Origin': origin}, {'Origin': 'https://invalid.example', 'X-CSRF-Token': token},
                    {'Origin': origin, 'X-CSRF-Token': 'x' * 43}):
        status, _, _ = browser.request(origin + '/api/auth/web/switch-account', method='POST', headers=headers)
        require(status == 403, 'Switch accepted missing or mismatched CSRF/origin')
    status, _, body = browser.request(provider + '/api/get-account')
    current = json.loads(body)
    require(status == 200 and current.get('status') == 'ok' and
            all(current['data'].get(k) == account['data'].get(k) for k in ('owner', 'name')),
            'Switch preparation or rejected request changed provider identity')
    status, _, _ = browser.request(origin + '/api/auth/web/me')
    require(status == 200, 'Switch preparation ended local session')
    status, _, body = browser.request(origin + '/api/auth/web/switch-account', method='POST',
        headers={'Origin': origin, 'X-CSRF-Token': token})
    require(status == 200, 'Explicit switch failed')
    logout_url = json.loads(body).get('logout_url', '')
    target = urlsplit(logout_url)
    query = parse_qs(target.query)
    landing = origin + '/api/auth/web/logged-out'
    require(target.scheme + '://' + target.netloc == provider and target.path == '/api/logout' and
            not target.fragment and query.get('client_id') == [client['client_id']] and
            query.get('post_logout_redirect_uri') == [landing] and
            set(query) <= {'client_id', 'post_logout_redirect_uri', 'state'}, 'Unsafe switch logout URL')
    status, headers, _ = browser.request(logout_url)
    returned = urlsplit(headers.get('location', ''))
    require(status == 302 and returned.scheme + '://' + returned.netloc + returned.path == landing and
            not returned.fragment and parse_qs(returned.query) ==
            ({'state': query['state']} if 'state' in query else {}), 'Provider logout return rejected')
    status, headers, _ = browser.request(headers['location'])
    require(status == 302 and headers.get('location') == origin + '/zh-CN/dashboard',
            'Local logout landing rejected')
    status, _, _ = browser.request(origin + '/api/auth/web/me')
    require(status == 401, 'Switched local session still accepted')
    status, _, body = browser.request(provider + '/api/get-account')
    account = json.loads(body)
    # Casdoor 4.12.0 repeats the anonymous error message in data; it is not a user.
    require(status in (200, 401) and account.get('status') == 'error' and
            account.get('msg') == 'Please login first' and
            account.get('data') in (None, 'Please login first'),
            'Provider identity survived explicit switch')


def run(settings):
    origins = {surface: client['origin'] for surface, client in settings['clients'].items()}
    peers = settings.get('sso_clients', {})
    require((settings['application'] == 'knowbench' and set(peers) == {'tpl', 'knowfeed', 'knowbase', 'knowlab', 'knowmart'})
            or (settings['application'] != 'knowbench' and not peers), 'Unexpected SSO client selection')
    peer_origins = [client['origin'] for client in peers.values()]
    allowed = {urlsplit(o).hostname for o in [settings['provider'], *origins.values(), *peer_origins]}
    # URLs carry the site's public port; every connection still goes to the local entry_port.
    public_port = urlsplit(settings['provider']).port
    require(public_port and all(urlsplit(o).port == public_port for o in [*origins.values(), *peer_origins]),
            'Provider and frontend origins disagree on the public port')
    context = ssl.create_default_context(cafile=settings['ca_file'])

    class Connection(http.client.HTTPSConnection):
        def connect(self):
            self.sock = context.wrap_socket(
                socket.create_connection(('127.0.0.1', settings['entry_port']), timeout=15),
                server_hostname=self.host,
            )

    class Browser:
        def __init__(self):
            self.cookies = {}
            self.session_ages = {}

        def request(self, url, method='GET', data=None, headers=None):
            target = urlsplit(url)
            require(target.scheme == 'https' and target.hostname in allowed and target.port == public_port,
                    'Unexpected protocol destination')
            connection = Connection(target.hostname, public_port, timeout=15, context=context)
            request_headers = {'Host': target.netloc, **(headers or {})}
            jar = self.cookies.get(target.hostname, {})
            if jar:
                request_headers['Cookie'] = '; '.join(k + '=' + v for k, v in jar.items())
            payload = json.dumps(data) if data is not None else None
            if payload is not None:
                request_headers['Content-Type'] = 'application/json'
            path = target.path + ('?' + target.query if target.query else '')
            try:
                connection.request(method, path, body=payload, headers=request_headers)
                response = connection.getresponse()
                body = response.read()
                pairs = response.getheaders()
                for key, value in pairs:
                    if key.lower() == 'set-cookie':
                        parsed = SimpleCookie()
                        parsed.load(value)
                        for name, cookie in parsed.items():
                            jar = self.cookies.setdefault(target.hostname, {})
                            if cookie['max-age'] == '0':
                                jar.pop(name, None)
                                self.session_ages.get(target.hostname, {}).pop(name, None)
                            else:
                                if name.endswith('_sid'):
                                    require(bool(cookie['secure']) and bool(cookie['httponly']) and
                                            cookie['samesite'].lower() == 'lax' and not cookie['domain'], 'Insecure session cookie')
                                    self.session_ages.setdefault(target.hostname, {})[name] = int(cookie['max-age'])
                                jar[name] = cookie.value
                return response.status, {k.lower(): v for k, v in pairs}, body
            finally:
                connection.close()

    outcomes = {}
    require(bool(settings['clients']) and set(settings['clients']) <= {'web', 'admin'}, 'Invalid selected frontend surfaces')
    require(settings['user_organization'] == 'sunmoonai' and settings['organization'] == 'built-in',
            'Unexpected identity organizations')
    provider_headers = {'Origin': settings['provider']}
    operator = Browser()

    def provider_api(path, data):
        status, _, body = operator.request(settings['provider'] + path, method='POST', data=data,
                                           headers=provider_headers)
        require(status == 200, 'Provider administration HTTP failure')
        return json.loads(body)

    # Web clients belong to the user organization, where the administrator cannot sign in
    # (SDD 0014). A throwaway member with a random password is created for this run only
    # and always deleted afterwards; nothing about it is printed or stored.
    member = None
    if 'web' in settings['clients']:
        signed_in = provider_api('/api/login', {'application': 'app-built-in', 'organization': 'built-in',
            'username': settings['username'], 'password': settings['password'], 'type': 'login'})
        require(signed_in.get('status') == 'ok', 'Provider administrator login failed')
        member = {'owner': settings['user_organization'], 'name': 'verify-' + secrets.token_hex(6),
                  'password': secrets.token_urlsafe(24)}
        added = provider_api('/api/add-user', {**member, 'type': 'normal-user', 'displayName': 'verification',
            'createdTime': datetime.now(timezone.utc).isoformat()})
        require(added.get('status') == 'ok' and added.get('data') == 'Affected', 'Verification member not created')
    try:
        install_issued = _check_surfaces(settings, Browser, member, outcomes)
    finally:
        if member is not None:
            removed = provider_api('/api/delete-user', {'owner': member['owner'], 'name': member['name']})
            require(removed.get('status') == 'ok', 'Verification member not removed')
    report = {'entry_port': settings['entry_port'], 'protocol_checks': outcomes,
        'web_member_organization': settings['user_organization'] if member else None,
        'browser_ui_clicks_verified': False, 'business_provider_configured': False}
    if settings['application'] == 'knowbench':
        report['install_command_issued'] = install_issued is True
    print(json.dumps(report))


def _check_surfaces(settings, Browser, member, outcomes):
    install_issued = None
    for surface in settings['clients']:
        client = settings['clients'][surface]
        origin = client['origin']
        browser = Browser()
        check_login_entry(browser, origin, surface)
        status, _, _ = browser.request(origin + '/api/auth/' + surface + '/me')
        require(status == 401, surface + ': anonymous session was accepted')
        status, headers, _ = browser.request(origin + '/api/auth/' + surface + '/login')
        require(status == 302, surface + ': login start failed')
        flags = headers.get('set-cookie', '').lower()
        require(all(flag in flags for flag in ['secure', 'httponly', 'samesite=lax']),
                surface + ': insecure transaction cookie')
        authorize = urlsplit(headers['location'])
        query = {key: values[0] for key, values in parse_qs(authorize.query).items()}
        require(authorize.scheme + '://' + authorize.netloc == settings['provider'] and
                query['client_id'] == client['client_id'] and query['code_challenge_method'] == 'S256',
                surface + ': unexpected authorization identity')
        aliases = {'client_id': 'clientId', 'response_type': 'responseType', 'redirect_uri': 'redirectUri'}
        login_query = {aliases.get(key, key): value for key, value in query.items()}
        if surface == 'admin' and member is not None:
            # The user organization must not obtain an authorization code from an admin client.
            status, _, body = Browser().request(settings['provider'] + '/api/login?' + urlencode(login_query),
                method='POST', data={'application': client['name'], 'organization': member['owner'],
                'username': member['name'], 'password': member['password'], 'type': 'code'},
                headers={'Origin': settings['provider']})
            require(status == 200 and json.loads(body).get('status') != 'ok', 'User organization reached admin client')
        account = ({'organization': member['owner'], 'username': member['name'], 'password': member['password']}
                   if surface == 'web' else {'organization': settings['organization'],
                   'username': settings['username'], 'password': settings['password']})
        status, _, body = browser.request(settings['provider'] + '/api/login?' + urlencode(login_query),
            method='POST', data={'application': client['name'], 'type': 'code', **account},
            headers={'Origin': settings['provider']})
        require(status == 200, surface + ': provider login HTTP failure')
        response = json.loads(body)
        require(response.get('status') == 'ok' and isinstance(response.get('data'), str) and response['data'],
                surface + ': provider did not return an authorization code')
        callback = query['redirect_uri'] + '?' + urlencode({'code': response['data'], 'state': query['state']})
        status, headers, _ = browser.request(callback)
        require(status == 302 and 'error=' not in headers.get('location', ''), surface + ': callback rejected')
        status, _, body = browser.request(origin + '/api/auth/' + surface + '/me')
        require(status == 200, surface + ': authenticated session unavailable')
        session = json.loads(body)
        require(session['authenticated'] and session['user']['app'] == settings['application'] and
                session['user']['surface'] == surface, surface + ': session identity mismatch')
        check_lifetime(browser, origin, surface, session)
        if surface == 'web':
            for application, peer in settings.get('sso_clients', {}).items():
                sso_login(settings, browser, peer, application)
        status, _, _ = browser.request(origin + '/zh-CN/dashboard')
        require(status == 200, surface + ': authenticated SSR failed')
        opposite = 'admin' if surface == 'web' else 'web'
        status, _, _ = browser.request(origin + '/api/auth/' + opposite + '/me')
        require(status == 401, surface + ': cross-surface session accepted')
        headers = {'Origin': origin, 'X-CSRF-Token': session['csrf_token']}
        permission_denied = admin_list_read = None
        # 管理员 = 白名单里的管理角色（admin、operator，待办 98）或带「应用名:admin」权限（账 134）。
        # 管理员读一张管理端列表（只读、不派任务），读得出才算管理端能用；不是管理员的，诊断接口必须 403
        privileged = surface == 'admin' and (
            settings['application'] + ':admin' in session['user']['scopes'] or
            bool(set(session['user'].get('roles') or []) & {'admin', 'operator'}))
        # 列表路径由应用在 gitops 的 <app>_deployment.admin_list_path 声明（账 173：以前写死在这里，应用改接口就在验收倒）
        if privileged and settings.get('admin_list_path'):
            require(settings['admin_list_path'].startswith('/api/admin/'), 'admin_list_path must be an admin API path')
            status, _, _ = browser.request(origin + settings['admin_list_path'])
            require(status == 200, 'Administrator could not read the admin console list')
            admin_list_read = True
        if surface == 'admin' and not privileged:
            status, _, _ = browser.request(origin + '/api/admin/v1/diagnostics/tasks/ping',
                                          method='POST', headers=headers)
            require(status == 403, 'Unprivileged browser could invoke administrator diagnostic')
            permission_denied = True
        if surface == 'web' and settings['application'] in ('tpl', 'knowlab', 'knowmart'):  # 由模板实例化、还没有业务的应用
            status, _, body = browser.request(origin + '/api/web/v1/runs/00000000-0000-5000-8000-000000000001')
            require(status == 503 and json.loads(body).get('error', {}).get('code') == 'provider_unavailable',
                    'Production template unexpectedly exposes a reference business fixture')
        if surface == 'web' and settings['application'] == 'knowbench':
            status, _, body = browser.request(origin + '/api/workbench/agent/install-command',
                                              method='POST', headers=headers)
            if status == 404 and b'agent_download_unavailable' in body:
                # 安装包下载开关关着（0028 R5.3 上传、读回校验之前）：明确说「下载不可用」也算对，报告里记 install_issued: false
                install_issued = False
                status = None
            require(status in (200, None), 'Install command was not issued')
        if surface == 'web' and settings['application'] == 'knowbench' and install_issued is not False:
            issued = json.loads(body)
            command = issued.get('command')
            require(isinstance(command, str) and command.startswith("irm '"),
                    'Install command was not issued')
            try:
                expiry = datetime.fromisoformat(issued['expires_at'])
            except (KeyError, TypeError, ValueError):
                expiry = None
            require(isinstance(expiry, datetime), 'Install command expiry was not parseable')
            install_issued = True
        status, _, _ = browser.request(origin + '/api/auth/' + surface + '/logout',
                                       method='POST', headers={'Origin': origin})
        require(status == 403, surface + ': missing CSRF accepted')
        status, _, body = browser.request(origin + '/api/auth/' + surface + '/logout', method='POST', headers=headers)
        # 单点退出（0027 P1b）：本地会话已结束，回 200 带去 Casdoor 结束会话的地址；没配 Casdoor 的退出地址时回 204
        if status == 200:
            ended = urlsplit(json.loads(body).get('logout_url') or '')
            require(ended.scheme + '://' + ended.netloc == settings['provider'] and ended.path == '/api/logout',
                    surface + ': logout did not hand over to the provider')
        require(status in (200, 204), surface + ': logout rejected')
        status, _, _ = browser.request(origin + '/api/auth/' + surface + '/me')
        require(status == 401, surface + ': logged-out session accepted')
        if surface == 'web':
            # The regular logout contract above revokes the local session only until
            # its provider URL is visited. Reuse SSO, then exercise the explicit action.
            sso_login(settings, browser, client, settings['application'])
            check_switch(settings, browser, client)
        outcomes[surface] = {'pkce_callback': True, 'authenticated_ssr': True,
            'secure_cookie': True, 'cross_surface_denied': True, 'csrf_required': True,
            'logout_revoked': True, 'session_lifetime_seconds': 86400,
            'explicit_switch_verified': True if surface == 'web' else None,
            'passwordless_sso_apps': sorted(settings.get('sso_clients', {})) if surface == 'web' else [],
            'unprivileged_admin_diagnostic_denied': permission_denied,
            'admin_list_read': admin_list_read,
            'user_organization_denied': True if surface == 'admin' and member is not None else None}
    return install_issued


if __name__ == '__main__':
    try:
        run(json.load(sys.stdin))
    except Exception as error:
        # HTTP URLs, credentials, cookies and responses must never be stringified.
        message = str(error) if type(error) is RuntimeError else type(error).__name__
        raise SystemExit('Browser verification failed: ' + message)
