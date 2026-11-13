#!/usr/bin/env python3
"""Verify sandbox provisioner healthz inside the cluster without printing tokens."""
import argparse
import json
import subprocess
import sys


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['kubectl', 'kubeconfig', 'context', 'namespace']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    require(args.namespace.startswith('sandbox-'), 'Unexpected sandbox namespace')
    # 供给器镜像是 python slim，没有 curl（第 27 轮 platform-check 停在这里）：用它自己的 python 探
    probe = ("import json,sys,urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=10); "
             "sys.exit(0 if r.status == 200 and sys.stdout.write(r.read().decode()) is not None else 1)")
    result = subprocess.run(
        [args.kubectl, '--kubeconfig', args.kubeconfig, '--context', args.context, '--request-timeout=30s',
         '-n', args.namespace, 'exec', 'deployment/sandbox-provisioner', '--', 'python', '-c', probe],
        check=False, capture_output=True, text=True)
    require(result.returncode == 0, result.stderr.strip() or 'provisioner healthz exec failed')
    body = json.loads(result.stdout)
    require(body.get('ok') is True and body.get('image_configured') is True, 'Provisioner healthz payload is incomplete')
    script_check = subprocess.run(
        [args.kubectl, '--kubeconfig', args.kubeconfig, '--context', args.context,
         '-n', args.namespace, 'exec', 'deployment/sandbox-provisioner', '--', 'python', '/opt/provisioner/script_probe.py'],
        check=False, capture_output=True, text=True, timeout=150)
    require(script_check.returncode == 0, 'Isolated package execution probe failed: ' + script_check.stderr[-2000:])
    execution = json.loads(script_check.stdout)
    require(execution.get('passed') is True, 'Script execution acceptance did not pass')
    print(json.dumps({'passed': True, 'namespace': args.namespace, 'healthz': True,
        'execution': execution,
        'scope': 'Health, synthetic package execution, denied cluster network and returned artifact; no user workspace or paid model'}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'passed': False, 'reason': str(error)}))
        raise SystemExit(1)
