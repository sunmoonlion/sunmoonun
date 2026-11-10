"""Exercise both ends of the public route using their actual templates."""
import json
import tomllib
import unittest
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[3]
EDGE = ROOT / 'infrastructure/edge'
FRPC = ROOT / 'gitops/components/ingress-platform/frpc'
ENGINE = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
ENGINE.filters['to_json'] = json.dumps


def render(path, values):
    return ENGINE.from_string(path.read_text()).render(**values)


def configuration(domain):
    values = yaml.safe_load((ROOT / 'infrastructure/environments/kind/site.yaml').read_text())
    values.update(site_domain=domain, ingress_namespace='ingress-platform-dev')
    values.update(yaml.safe_load(render(EDGE / 'config.yaml', values)))
    frpc = yaml.safe_load((FRPC / 'config.yaml').read_text())
    # The local address refers to a port defined in the same configuration.
    values.update(frpc)
    values.update(yaml.safe_load(render(FRPC / 'config.yaml', values)))
    lock = json.loads((ROOT / 'infrastructure/artifacts/upstream-images.lock.json').read_text())
    values['image_map'] = {item['id']: item for item in lock['images']}
    values['frpc_input_digest'] = '0' * 64  # Synthetic; no credentials needed.
    return values


class PublicRoutes(unittest.TestCase):
    def test_market_route_reaches_cluster_with_host_and_https_preserved(self):
        for domain in ('dev.sunmoonai.com', 'route-test.example'):
            with self.subTest(domain=domain):
                values = configuration(domain)
                edge = yaml.safe_load(render(EDGE / 'templates/dynamic.yml.j2', values))['http']
                objects = list(yaml.safe_load_all(render(FRPC / 'workload.yaml.j2', values)))
                proxies = tomllib.loads(objects[0]['data']['frpc.toml'])['proxies']
                route = edge['routers']['knowmart']
                self.assertEqual(route['rule'], f'Host(`knowmart.{domain}`)')
                self.assertEqual(route['entryPoints'], ['websecure'])
                self.assertEqual(route['tls'], {'certResolver': 'le'})
                service = edge['services'][route['service']]['loadBalancer']
                self.assertTrue(service['passHostHeader'])
                self.assertEqual(service['servers'], [{'url': 'http://127.0.0.1:8080'}])
                proxy = next(p for p in proxies if p['name'] == 'knowmart')
                self.assertEqual(proxy['customDomains'], [f'knowmart.{domain}'])
                self.assertEqual(proxy['plugin'], {
                    'type': 'http2https',
                    'localAddr': 'traefik.ingress-platform-dev.svc.cluster.local:443',
                    'requestHeaders': {'set': {'x-forwarded-proto': 'https'}},
                })
                self.assertEqual([p['customDomains'][0] for p in proxies], values['edge_domains'])

    def test_admin_hosts_stay_private_and_casdoor_keeps_path_restrictions(self):
        values = configuration('dev.sunmoonai.com')
        routers = yaml.safe_load(render(EDGE / 'templates/dynamic.yml.j2', values))['http']['routers']
        self.assertEqual(set(routers), {
            'to-https', 'knowbench', 'knowmart', 'casdoor', 'casdoor-verification', 'casdoor-deny', 'relay',
        })
        login = routers['casdoor']
        self.assertIn('Path(`/login/oauth/authorize`)', login['rule'])
        self.assertNotIn('PathPrefix(`/`)', login['rule'])
        self.assertNotIn('/api/get-users', login['rule'])
        deny = routers['casdoor-deny']
        self.assertIn('deny-all', deny['middlewares'])
        self.assertGreater(login['priority'], deny['priority'])

    def test_signup_routes_have_bounded_email_sending_and_no_admin_access(self):
        values = configuration('dev.sunmoonai.com')
        http = yaml.safe_load(render(EDGE / 'templates/dynamic.yml.j2', values))['http']
        rules = http['routers']['casdoor']['rule']
        for path in ('/api/signup', '/api/send-verification-code', '/api/get-captcha-status'):
            self.assertIn(f'Path(`{path}`)', rules)
        for path in ('/api/add-user', '/api/update-application', '/api/send-email', '/api/get-providers'):
            self.assertNotIn(path, rules)
        route = http['routers']['casdoor-verification']
        self.assertEqual(route['rule'], 'Host(`casdoor.dev.sunmoonai.com`) && Path(`/api/send-verification-code`)')
        self.assertGreater(route['priority'], http['routers']['casdoor']['priority'])
        self.assertEqual(route['middlewares'], ['per-ip-limit', 'verification-limit'])
        self.assertEqual(http['middlewares']['verification-limit']['rateLimit'], {
            'average': 1, 'period': '1m', 'burst': 3, 'sourceCriterion': {'ipStrategy': {'depth': 0}},
        })

    def test_staged_manifest_contains_same_domain_list_as_both_templates(self):
        values = configuration('dev.sunmoonai.com')
        staged = list(yaml.safe_load_all((FRPC / 'workload.yaml').read_text()))
        expected = list(yaml.safe_load_all(render(FRPC / 'workload.yaml.j2', values)))
        deployment = next(obj for obj in staged if obj['kind'] == 'Deployment')
        digest = deployment['spec']['template']['metadata']['annotations']['sunmoonai.com/input-sha256']
        self.assertRegex(digest, r'^[0-9a-f]{64}$')
        self.assertNotEqual(digest, '0' * 64)
        # The native renderer derives this from private inputs; compare all public fields.
        expected_deployment = next(obj for obj in expected if obj['kind'] == 'Deployment')
        expected_deployment['spec']['template']['metadata']['annotations']['sunmoonai.com/input-sha256'] = digest
        self.assertEqual(staged, expected)


if __name__ == '__main__':
    unittest.main()
