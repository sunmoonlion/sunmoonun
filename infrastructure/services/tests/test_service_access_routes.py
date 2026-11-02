"""Render the actual internal ingress template: data MCP must reach its JWT provider."""
import unittest
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[3]
COMPONENT = ROOT / 'gitops/components/ingress-platform/traefik/service-access'


def render(namespace):
    engine = Environment(undefined=StrictUndefined)
    config = yaml.safe_load(engine.from_string((COMPONENT / 'config.yaml').read_text()).render(app_namespace=namespace))
    return list(yaml.safe_load_all(engine.from_string((COMPONENT / 'workload.yaml.j2').read_text()).render(
        **config, app_namespace=namespace, ingress_namespace='ingress-platform-test',
    )))


class ServiceAccessRoutes(unittest.TestCase):
    def test_data_mcp_routes_to_provider_without_widening_other_internal_paths(self):
        for namespace in ['app-platform-dev', 'app-platform-test']:
            with self.subTest(namespace=namespace):
                objects = render(namespace)
                ingresses = {o['metadata']['name']: o for o in objects if o['kind'] == 'Ingress'}
                kb = ingresses['knowbase-service-access']
                rule = kb['spec']['rules'][0]
                self.assertEqual(rule['host'], f'knowbase-tls.{namespace}.svc.cluster.local')
                paths = {p['path']: p for p in rule['http']['paths']}
                self.assertEqual({p: v['pathType'] for p, v in paths.items()}, {
                    '/api/internal/v1/knowledge': 'Prefix',
                    '/api/internal/v2/user-data': 'Prefix',
                    '/api/mcp/data': 'Exact',
                })
                self.assertEqual(paths['/api/mcp/data']['backend']['service'], {
                    'name': 'knowbase-api', 'port': {'name': 'http'},
                })
                self.assertEqual(kb['spec']['tls'], [{
                    'secretName': 'service-access-tls', 'hosts': [rule['host']],
                }])
                self.assertEqual(kb['metadata']['namespace'], namespace)
                self.assertEqual(kb['metadata']['annotations']['traefik.ingress.kubernetes.io/router.entrypoints'], 'websecure')
                for name, expected in {
                    'casdoor': '/', 'knowmart': '/api/internal/v1/knowmart',
                    'knowbench': '/api/internal/v1/knowbot-runtime',
                    'knowlab': '/api/internal/v1/knowlab', 'knowfeed': '/api/internal/v1/supply',
                }.items():
                    other = ingresses[f'{name}-service-access']['spec']['rules'][0]['http']['paths']
                    self.assertEqual([(p['path'], p['pathType']) for p in other], [(expected, 'Prefix')])
                self.assertEqual(len(objects), 12)  # Six HTTPS services and six ingresses.


if __name__ == '__main__':
    unittest.main()
