"""Offline policy and rendered-manifest checks; no real emails or live API calls."""
import copy
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import yaml
from jinja2 import Environment, StrictUndefined

IDENTITY = Path(__file__).resolve().parents[1]
ROOT = next(p for p in IDENTITY.parents if (p / 'infrastructure').is_dir())
spec = importlib.util.spec_from_file_location('signup', IDENTITY / 'signup.py')
signup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signup)
SETTINGS = {'enabled': True, 'smtp_host': 'smtpdm.aliyun.com', 'smtp_port': 465,
            'smtp_username': 'noreply@notify.sunmoonai.com'}
PASSWORD = 'synthetic-only-NOT-a-credential-42'
APP = 'sunmoonai-knowbench-web'


class Api:
    def __init__(self):
        self.applications = {
            'admin/app-built-in': {'owner': 'admin', 'name': 'app-built-in', 'organization': 'built-in', 'enableSignUp': True},
            'admin/' + APP: {'owner': 'admin', 'name': APP, 'organization': 'sunmoonai', 'enableSignUp': False,
                             'providers': [], 'signinItems': [{'name': 'Signup link', 'visible': False}],
                             'clientSecret': 'unchanged-client', 'redirectUris': ['https://example.test/callback']},
        }
        self.providers = {}
        self.writes = []
        self.fail_provider = False

    def __call__(self, method, path, payload=None, params=None):
        kind = path.rsplit('-', 1)[-1]
        objects = self.providers if kind == 'provider' else self.applications
        if method == 'GET':
            value = copy.deepcopy(objects.get(params['id']))
            if kind == 'provider' and value:
                value['clientSecret'] = '***'
            return value
        if kind == 'provider' and self.fail_provider:
            raise RuntimeError('Casdoor API rejected operation')
        self.writes.append(path)
        identity = payload['owner'] + '/' + payload['name']
        objects[identity] = copy.deepcopy(payload)
        return 'Affected'

    def current(self):
        return self('GET', '/api/get-application', params={'id': 'admin/' + APP})


class SignupPolicy(unittest.TestCase):
    def test_email_required_no_invitation_and_only_ordinary_users(self):
        api = Api()
        before = api.current()
        report = signup.configure_signup(api, before, SETTINGS, PASSWORD)
        current = api.current()
        self.assertTrue(current['enableSignUp'])
        self.assertFalse(api.applications['admin/app-built-in']['enableSignUp'])
        self.assertEqual(current['organization'], 'sunmoonai')
        self.assertEqual(current['clientSecret'], before['clientSecret'])
        self.assertEqual(current['redirectUris'], before['redirectUris'])
        fields = {item['name']: item for item in current['signupItems']}
        self.assertTrue(fields['Email']['visible'])
        self.assertTrue(fields['Email']['required'])
        self.assertEqual(fields['Email']['rule'], 'Normal')
        self.assertNotIn('Invitation code', fields)
        self.assertNotIn('Phone', fields)
        self.assertTrue(current['signinItems'][0]['visible'])
        self.assertEqual(current['providers'], [{'name': APP + '-signup-email', 'rule': 'signup'}])
        self.assertEqual(current['codeResendTimeout'], 60)
        provider = api.providers['admin/' + APP + '-signup-email']
        self.assertEqual(provider['port'], 465)
        self.assertEqual(provider['sslMode'], 'Enable')
        self.assertFalse(provider['disableSsl'])
        self.assertEqual(provider['clientId'], provider['clientId2'])
        self.assertEqual(provider['clientSecret'], PASSWORD)
        self.assertEqual(provider['content'].count('%s'), 1)
        self.assertLess(api.writes.index('/api/add-provider'), len(api.writes) - 1)
        self.assertFalse(report['smtp_delivery_verified'])
        self.assertNotIn(PASSWORD, json.dumps(report))

    def test_missing_or_malformed_password_stops_before_any_write(self):
        for password in ('', 'short', PASSWORD + '\n', PASSWORD + ' ', None):
            with self.subTest(password_type=type(password).__name__):
                api = Api()
                with self.assertRaisesRegex(RuntimeError, 'password'):
                    signup.configure_signup(api, api.current(), SETTINGS, password)
                self.assertEqual(api.writes, [])
                self.assertFalse(api.current()['enableSignUp'])

    def test_no_plaintext_or_wrong_region_smtp(self):
        for change in ({'smtp_port': 25}, {'smtp_host': 'untrusted.example'}, {'enabled': 'true'}):
            api = Api()
            with self.assertRaises(RuntimeError):
                signup.configure_signup(api, api.current(), dict(SETTINGS, **change), PASSWORD)
            self.assertEqual(api.writes, [])

    def test_provider_failure_does_not_enable_signup(self):
        api = Api()
        api.fail_provider = True
        with self.assertRaises(RuntimeError):
            signup.configure_signup(api, api.current(), SETTINGS, PASSWORD)
        self.assertFalse(api.current()['enableSignUp'])

    def test_reject_admin_organization_and_unmanaged_providers(self):
        for change in ({'organization': 'built-in'}, {'providers': [{'name': 'unrelated-provider'}]}):
            api = Api()
            with self.assertRaises(RuntimeError):
                signup.configure_signup(api, dict(api.current(), **change), SETTINGS, PASSWORD)
            self.assertEqual(api.writes, [])

    def test_reconcile_twice_preserves_state_and_updates_masked_password(self):
        api = Api()
        signup.configure_signup(api, api.current(), SETTINGS, PASSWORD)
        before = copy.deepcopy(api.applications)
        signup.configure_signup(api, api.current(), SETTINGS, PASSWORD)
        self.assertEqual(api.applications, before)
        signup.configure_signup(api, api.current(), SETTINGS, PASSWORD + '-rotated')
        self.assertEqual(api.providers['admin/' + APP + '-signup-email']['clientSecret'], PASSWORD + '-rotated')

    def test_disable_detaches_email_provider_without_requiring_password(self):
        api = Api()
        signup.configure_signup(api, api.current(), SETTINGS, PASSWORD)
        report = signup.configure_signup(api, api.current(), {'enabled': False}, '')
        self.assertFalse(report['enabled'])
        self.assertFalse(api.current()['enableSignUp'])
        self.assertEqual(api.current()['providers'], [])
        self.assertEqual(api.current()['signupItems'], [])


def render_identity(name, enabled=None):
    engine = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    engine.filters.update(to_json=json.dumps, bool=bool, regex_replace=lambda s, p, v: re.sub(p, v, s))
    values = yaml.safe_load((ROOT / 'infrastructure/environments/kind/site.yaml').read_text())
    app = ROOT / 'gitops/components/app-platform' / (name + '-app')
    def configuration(path):
        return yaml.safe_load(engine.from_string(path.read_text()).render(**values))
    casdoor = yaml.safe_load((ROOT / 'gitops/components/app-platform/auth-app/casdoor/config.yaml').read_text())
    values['casdoor_hostname'] = engine.from_string(casdoor['casdoor_hostname']).render(**values)
    # Read only the identity fields; unrelated component configuration has its own bindings.
    cfg = yaml.safe_load((app / (name + '-backend/config.yaml')).read_text())[name + '_backend_deployment']
    if enabled is not None:
        cfg['public_signup'] = dict(SETTINGS, enabled=enabled)
    clients = {}
    for surface in ('web', 'admin'):
        config = configuration(app / (name + '-' + surface + '-frontend/config.yaml'))[name + '_' + surface + '_deployment']
        clients[surface] = {'name': config['casdoor_application'], 'client_id': config['casdoor_client_id'], 'origin': config['origin']}
    values.update(application_name=name, cfg=cfg, browser_clients=clients, mechanism_root=str(IDENTITY.parent),
                  app_images={'backend': yaml.safe_load((app / (name + '-backend/image.lock.yaml')).read_text())})
    def lookup(kind, path):
        text = Path(path).read_text()
        return engine.from_string(text).render(**values) if kind == 'template' else text.rstrip('\n')
    values['lookup'] = lookup
    return engine.from_string((IDENTITY / 'workload.yaml.j2').read_text()).render(**values)


class ManifestBoundaries(unittest.TestCase):
    def test_other_five_applications_keep_byte_identical_identity_manifests(self):
        for name in ('tpl', 'knowfeed', 'knowbase', 'knowlab', 'knowmart'):
            with self.subTest(application=name):
                existing = ROOT / f'gitops/components/app-platform/{name}-app/{name}-backend/identity/workload.yaml'
                self.assertEqual(render_identity(name), existing.read_text())

    def test_knowbench_rolls_job_and_keeps_smtp_secret_out_of_public_manifests(self):
        rendered = render_identity('knowbench')
        objects = list(yaml.safe_load_all(rendered))
        script = objects[0]['data']
        compile(script['provision.py'], '<provision>', 'exec')
        compile(script['signup.py'], '<signup>', 'exec')
        self.assertNotIn(PASSWORD, rendered)
        job = next(obj for obj in objects if obj['kind'] == 'Job')
        self.assertTrue(job['metadata']['name'].endswith('-v7'))
        env = job['spec']['template']['spec']['containers'][0]['env']
        self.assertTrue(json.loads(next(x['value'] for x in env if x['name'] == 'PUBLIC_SIGNUP'))['enabled'])
        smtp = next(obj for obj in objects if obj['metadata']['name'] == 'knowbench-signup-smtp')
        self.assertEqual(smtp['spec']['podSelector']['matchLabels'], {'app.kubernetes.io/name': 'casdoor'})
        self.assertEqual(smtp['spec']['egress'][0]['ports'], [{'protocol': 'TCP', 'port': 465}])

    def test_rollback_replaces_smtp_egress_with_empty_rules(self):
        objects = list(yaml.safe_load_all(render_identity('knowbench', enabled=False)))
        smtp = next(obj for obj in objects if obj['metadata']['name'] == 'knowbench-signup-smtp')
        self.assertEqual(smtp['spec']['egress'], [])


class ProvisionIntegration(unittest.TestCase):
    def test_generated_job_reconciles_signup_twice_and_rejects_admin_drift(self):
        objects = list(yaml.safe_load_all(render_identity('knowbench')))
        source = objects[0]['data']['provision.py']
        job = next(obj for obj in objects if obj['kind'] == 'Job')
        env = {item['name']: item['value'] for item in job['spec']['template']['spec']['containers'][0]['env']}
        api = Api()
        api.applications = {'admin/app-built-in': dict(api.applications['admin/app-built-in'], cert='synthetic-cert')}

        class Client:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def request(self, method, path, json=None, params=None):
                if path == '/api/login':
                    data = 'ok'
                elif path == '/api/get-organization':
                    data = {'owner': 'admin', 'name': 'sunmoonai', 'displayName': 'SunMoonAI',
                            'passwordType': 'bcrypt', 'passwordOptions': ['AtLeast8'], 'enableSoftDeletion': False}
                elif path == '/api/get-role':
                    data = {'isEnabled': True, 'users': ['built-in/admin'] if params['id'] == 'built-in/admin' else []}
                elif path == '/api/get-applications':
                    data = list(api.applications.values())
                else:
                    data = api(method, path, json, params)
                return SimpleNamespace(status_code=200, json=lambda: {'status': 'ok', 'data': data})

            def get(self, path):
                if path == '/.well-known/openid-configuration':
                    origin = env['CASDOOR_ORIGIN']
                    data = {'issuer': origin, 'code_challenge_methods_supported': ['S256'],
                            'authorization_endpoint': origin + '/login/oauth/authorize',
                            'token_endpoint': origin + '/api/login/oauth/access_token', 'jwks_uri': origin + '/.well-known/jwks'}
                else:
                    data = {'keys': [{'kid': 'synthetic-key'}]}
                return SimpleNamespace(status_code=200, json=lambda: data)

        files = {
            '/run/app/clients.json': json.dumps({'web_secret': 'synthetic-web', 'admin_secret': 'synthetic-admin'}),
            '/run/admin/init_data.json': json.dumps({'users': [{'owner': 'built-in', 'name': 'admin', 'password': 'synthetic-admin-login'}]}),
            '/run/app/smtp-password': PASSWORD + '\n',
        }
        namespace = {'__name__': 'provision_test'}
        with patch.dict(sys.modules, {'httpx': SimpleNamespace(Client=lambda **kwargs: Client()), 'signup': signup}):
            exec(compile(source, '<generated provision>', 'exec'), namespace)
        with patch.dict(os.environ, env), patch.object(Path, 'read_text', lambda path: files[str(path)]):
            for _ in range(2):
                output = io.StringIO()
                with redirect_stdout(output):
                    namespace['run']()
                report = json.loads(output.getvalue())
                self.assertFalse(report['signup_disabled'])
                self.assertTrue(report['public_signup']['email_verification_required'])
                self.assertNotIn(PASSWORD, output.getvalue())
            admin_name = json.loads(env['BROWSER_CLIENTS'])['admin']['name']
            self.assertFalse(api.applications['admin/' + admin_name]['enableSignUp'])
            api.applications['admin/' + admin_name]['enableSignUp'] = True
            api.writes.clear()
            with self.assertRaisesRegex(RuntimeError, 'Existing browser application differs'):
                namespace['run']()
            self.assertEqual(api.writes, [])


if __name__ == '__main__':
    unittest.main()
