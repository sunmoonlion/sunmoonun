"""Offline protocol checks: no sockets, passwords, or running services."""
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest
from urllib.parse import urlencode

import jinja2
import yaml

SPEC = importlib.util.spec_from_file_location('browser_check', Path(__file__).resolve().parents[1] / 'check-browser.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
ORIGIN = 'https://web.example.test:30443'
PROVIDER = 'https://identity.example.test:30443'
CLIENT = {'name': 'example-web', 'client_id': 'example-client', 'origin': ORIGIN}


def response(status=200, body=None, location=None):
    return status, ({'location': location} if location else {}), json.dumps(body).encode()


class Browser:
    def __init__(self, replies, age=86399):
        self.replies = list(replies)
        self.calls = []
        self.session_ages = {'web.example.test': {'example_web_sid': age}}

    def request(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self.replies:
            raise AssertionError('unexpected request')
        return self.replies.pop(0)


def session(surface='web', seconds=86399):
    return {'authenticated': True, 'user': {'app': 'example', 'surface': surface,
        'expires_at': (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()}}


def switch_replies():
    identity = {'status': 'ok', 'data': {'owner': 'sunmoonai', 'name': 'synthetic-member'}}
    landing = ORIGIN + '/api/auth/web/logged-out'
    logout = PROVIDER + '/api/logout?' + urlencode({
        'client_id': CLIENT['client_id'], 'post_logout_redirect_uri': landing, 'state': 'test-state'})
    return [response(body=identity), response(body={'csrf_token': 's' * 43}),
            *[response(403) for _ in range(4)], response(body=identity), response(),
            response(body={'logout_url': logout}), response(302, location=landing + '?state=test-state'),
            response(302, location=ORIGIN + '/zh-CN/dashboard'), response(401),
            response(body={'status': 'error', 'msg': 'Please login first', 'data': 'Please login first'})]


class LoginRecoveryChecks(unittest.TestCase):
    def test_peer_metadata_is_rendered_from_the_five_existing_web_configs(self):
        repo = Path(__file__).resolve().parents[3]
        variables = yaml.safe_load((repo / 'infrastructure/applications/verify.yaml').read_text())[-1]['vars']
        environment = jinja2.Environment(undefined=jinja2.StrictUndefined)
        environment.filters['from_yaml'] = yaml.safe_load
        context = {'repo': str(repo), 'playbook_dir': str(repo / 'infrastructure/applications'),
                   'application_name': 'knowbench', 'site_domain': 'test.example', 'public_port': 30443}
        def lookup(kind, filename, **kwargs):
            content = Path(filename).read_text()
            return environment.from_string(content).render(context) if kind == 'template' else content
        environment.globals['lookup'] = lookup
        peers = yaml.safe_load(environment.from_string(variables['sso_browser_clients']).render(context))
        self.assertEqual(set(peers), {'tpl', 'knowfeed', 'knowbase', 'knowlab', 'knowmart'})
        for app, peer in peers.items():
            source = repo / f'gitops/components/app-platform/{app}-app/{app}-web-frontend/config.yaml'
            cfg = yaml.safe_load(lookup('template', source))[app + '_web_deployment']
            self.assertEqual(peer, {'name': cfg['casdoor_application'], 'client_id': cfg['casdoor_client_id'], 'origin': cfg['origin']})
        context['application_name'] = 'tpl'
        self.assertEqual(yaml.safe_load(environment.from_string(variables['sso_browser_clients']).render(context)), {})

    def test_login_entry_requires_exact_web_redirect_and_admin_page(self):
        CHECK.check_login_entry(Browser([response(307, location='/api/auth/web/login?return_to=%2Fzh-CN%2Fdashboard')]), ORIGIN, 'web')
        CHECK.check_login_entry(Browser([response()]), ORIGIN, 'admin')
        for destination in ['https://other.example/api/auth/web/login?return_to=%2Fzh-CN%2Fdashboard',
                            '/api/auth/web/login?return_to=%2Fzh-CN%2Flogin', '/api/auth/web/signup']:
            with self.subTest(destination=destination), self.assertRaisesRegex(RuntimeError, 'exact local SSO entry'):
                CHECK.check_login_entry(Browser([response(307, location=destination)]), ORIGIN, 'web')
        with self.assertRaises(RuntimeError):
            CHECK.check_login_entry(Browser([response()]), ORIGIN, 'web')

    def test_expiry_and_cookie_both_have_exact_surface_bounds(self):
        CHECK.check_lifetime(Browser([]), ORIGIN, 'web', session())
        CHECK.check_lifetime(Browser([], age=3599), ORIGIN, 'admin', session('admin', 3599))
        for age, seconds in [(3599, 86399), (86399, 3599), (172800, 172800)]:
            with self.subTest(age=age, seconds=seconds), self.assertRaises(RuntimeError):
                CHECK.check_lifetime(Browser([], age=age), ORIGIN, 'web', session(seconds=seconds))

    def test_passwordless_sso_uses_cookie_only_and_checks_callback_identity(self):
        query = {'client_id': CLIENT['client_id'], 'redirect_uri': ORIGIN + '/api/auth/web/callback',
                 'code_challenge_method': 'S256', 'state': 'test-state', 'response_type': 'code'}
        browser = Browser([
            response(307, location=ORIGIN + '/api/auth/web/login?return_to=%2Fzh-CN%2Fdashboard'),
            response(302, location=PROVIDER + '/login/oauth/authorize?' + urlencode(query)),
            response(body={'status': 'ok', 'data': 'synthetic-code'}),
            response(302, location=ORIGIN + '/zh-CN/dashboard'), response(body=session())])
        CHECK.sso_login({'provider': PROVIDER}, browser, CLIENT, 'example')
        post = browser.calls[2][1]
        self.assertEqual(post['data'], {'application': CLIENT['name'], 'type': 'code'})
        self.assertEqual(post['headers'], {'Origin': PROVIDER})
        self.assertEqual(browser.replies, [])

    def test_switch_rejects_bad_csrf_then_visits_provider_and_registered_return(self):
        browser = Browser(switch_replies())
        CHECK.check_switch({'provider': PROVIDER}, browser, CLIENT)
        self.assertEqual(browser.replies, [])
        self.assertEqual(browser.calls[1][1], {})  # preparation is only GET
        posts = [kwargs for _, kwargs in browser.calls if kwargs.get('method') == 'POST']
        self.assertEqual(len(posts), 5)
        self.assertEqual(posts[-1]['headers'], {'Origin': ORIGIN, 'X-CSRF-Token': 's' * 43})
        self.assertTrue(browser.calls[9][0].startswith(PROVIDER + '/api/logout?'))
        self.assertEqual(browser.calls[-1][0], PROVIDER + '/api/get-account')

    def test_switch_stops_before_visiting_unsafe_logout(self):
        replies = switch_replies()
        replies[8] = response(body={'logout_url': 'https://attacker.example/logout'})
        browser = Browser(replies)
        with self.assertRaisesRegex(RuntimeError, 'Unsafe switch logout URL'):
            CHECK.check_switch({'provider': PROVIDER}, browser, CLIENT)
        self.assertEqual(len(browser.calls), 9)

    def test_switch_does_not_accept_failed_return_or_surviving_provider_session(self):
        for index, replacement, error in [
            (9, response(body={'status': 'error'}), 'Provider logout return rejected'),
            (12, response(body={'status': 'ok', 'data': {'name': 'still-signed-in'}}), 'identity survived'),
            (12, response(body={'status': 'error', 'msg': 'Backend unavailable', 'data': None}), 'identity survived'),
            (6, response(body={'status': 'error'}), 'preparation or rejected request'),
            (2, response(), 'missing or mismatched CSRF')]:
            with self.subTest(index=index), self.assertRaisesRegex(RuntimeError, error):
                replies = switch_replies()
                replies[index] = replacement
                CHECK.check_switch({'provider': PROVIDER}, Browser(replies), CLIENT)


if __name__ == '__main__':
    unittest.main()
