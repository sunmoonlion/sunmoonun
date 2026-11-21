"""Exercise the candidate instruction units in fresh namespaces on an explicitly selected cluster."""

import argparse
import asyncio
import json
import subprocess
import sys
import tempfile
import time
from contextlib import ExitStack
from functools import partial
from pathlib import Path
from uuid import uuid4

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[2]
PLATFORM = ROOT / "infrastructure/applications/component-images/sandbox-platform"
sys.path.insert(0, str(PLATFORM / "provisioner"))
import provisioner
from instruction_units import Binding, InstructionUnits

# The receipt listener returns 503 until the test releases it after a gateway restart.
RECEIVER = """
import json, ssl, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
class Receiver(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        assert self.path == '/api/internal/v1/instruction-control/receipt'
        assert self.headers['Authorization'] == 'Bearer cni-test'
        assert self.headers['X-Instruction-Gateway'] == sys.argv[1]
        assert self.headers['X-Instruction-Attempt'] == sys.argv[2]
        assert body == {'response_id':'synthetic','turn_id':'original','usage':{'output_tokens':1}}
        Path('/tmp/observed').touch()
        if not Path('/tmp/accept').exists():
            self.send_error(503)
            return
        Path('/tmp/received').write_text(json.dumps(body))
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(b'{"recorded":true}')
server=HTTPServer(('0.0.0.0',8443),Receiver)
ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('/tls/crt','/tls/key')
server.socket=ctx.wrap_socket(server.socket,server_side=True)
server.serve_forever()
"""
TCP = """
import socket, sys
try:
    with socket.create_connection((sys.argv[1], int(sys.argv[2])), 2): pass
except TimeoutError:
    print('blocked')
else:
    print('connected')
"""
DNS = """
import socket, sys
ip=sys.argv[1]
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.settimeout(2)
q=b'\\x12\\x34\\x01\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00'+b'\\x0akubernetes\\x07default\\x03svc\\x07cluster\\x05local\\x00\\x00\\x01\\x00\\x01'
s.sendto(q,(ip,53))
try:
    data,_=s.recvfrom(4096)
except TimeoutError:
    print('blocked')
else:
    assert data[:2]==q[:2] and data[2]&128 and int.from_bytes(data[6:8],'big')>0
    print('answered')
"""


async def run(args, directory, stack):
    def ctl(*cmd, obj=None):
        r = subprocess.run(
            ["kubectl", "--context", args.context, "--request-timeout=12s", *cmd],
            input=json.dumps(obj) if obj else None,
            text=True,
            capture_output=True,
            check=False,
        )
        if r.returncode:
            raise RuntimeError(f"kubectl {cmd[:2]} failed: {r.stderr[:500]}")
        return r.stdout.strip()

    def create(ns, obj):
        return json.loads(ctl("-n", ns, "create", "-f", "-", "-o", "json", obj=obj))

    def execute(ns, pod, script, *params):
        return ctl("-n", ns, "exec", pod, "--", "python3", "-c", script, *params)

    async def wait(fn, description, timeout=150):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            result = fn()
            if asyncio.iscoroutine(result):
                result = await result
            if result:
                return result
            await asyncio.sleep(1)
        raise TimeoutError(description)

    suffix = uuid4().hex[:10]
    sandbox, app = "instr-sbx-" + suffix, "instr-app-" + suffix
    for ns in (sandbox, app):
        ctl(
            "create",
            "-f",
            "-",
            obj={
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": ns,
                    "labels": {"pod-security.kubernetes.io/enforce": "restricted"},
                },
            },
        )
        stack.callback(ctl, "delete", "namespace", ns, "--timeout=120s")
    print("测试命名空间", sandbox, app, flush=True)

    # Use the same foundation selector and both runner egress selectors as deployment.
    policies = yaml.safe_load_all(
        (ROOT / "gitops/components/foundations/runtime.yaml").read_text()
    )
    for doc in policies:
        if (
            doc
            and doc["kind"] == "NetworkPolicy"
            and doc["metadata"]["namespace"]
            in ("sandbox-platform-dev", "app-platform-dev")
        ):
            ns = (
                sandbox
                if doc["metadata"]["namespace"] == "sandbox-platform-dev"
                else app
            )
            doc["metadata"]["namespace"] = ns
            create(ns, doc)
    cfg = yaml.safe_load(
        (
            ROOT
            / "gitops/components/app-platform/knowbench-app/knowbench-backend/config.yaml"
        ).read_text()
    )
    rule = next(
        rule
        for rule in cfg["knowbench_backend_deployment"]["domain_egress"]
        if rule["name"] == "instruction-workers"
    )
    create(
        app,
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "instruction-workers-out"},
            "spec": {
                "podSelector": {
                    "matchExpressions": [
                        {
                            "key": "app.kubernetes.io/name",
                            "operator": "In",
                            "values": ["knowbench-" + r for r in rule["roles"]],
                        }
                    ]
                },
                "policyTypes": ["Egress"],
                "egress": [
                    {
                        "to": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "kubernetes.io/metadata.name": sandbox
                                    }
                                },
                                "podSelector": {"matchLabels": rule["pod_labels"]},
                            }
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": p} for p in rule["ports"]
                        ],
                    }
                ],
            },
        },
    )
    dns = json.loads(ctl("-n", "kube-system", "get", "svc", "kube-dns", "-o", "json"))[
        "spec"
    ]["clusterIP"]
    # Enable only the synthetic receiver in this namespace.
    create(
        app,
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "control-in"},
            "spec": {
                "podSelector": {"matchLabels": {"app.kubernetes.io/name": "traefik"}},
                "policyTypes": ["Ingress"],
                "ingress": [{"ports": [{"protocol": "TCP", "port": 8443}]}],
            },
        },
    )
    host = f"control.{app}.svc.cluster.local"
    key, crt = directory / "key", directory / "crt"
    await asyncio.to_thread(
        subprocess.run,
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-days",
            "1",
            "-subj",
            "/CN=" + host,
            "-addext",
            "subjectAltName=DNS:" + host,
            "-keyout",
            key,
            "-out",
            crt,
        ],
        capture_output=True,
        check=True,
    )
    create(
        sandbox,
        {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": "instruction-control-ca"},
            "data": {"ca.crt": crt.read_text()},
        },
    )
    create(
        app,
        {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {"name": "control-tls"},
            "stringData": {"key": key.read_text(), "crt": crt.read_text()},
        },
    )
    create(
        app,
        {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "control"},
            "spec": {
                "selector": {"app.kubernetes.io/name": "traefik"},
                "ports": [{"port": 443, "targetPort": 8443}],
            },
        },
    )

    sock = directory / "proxy.sock"
    with (directory / "proxy.log").open("w") as stream:
        proxy = await asyncio.to_thread(
            subprocess.Popen,
            ["kubectl", "--context", args.context, "proxy", "--unix-socket", str(sock)],
            stdout=stream,
            stderr=stream,
        )

    def stop_proxy():
        proxy.terminate()
        proxy.wait(timeout=8)

    stack.callback(stop_proxy)
    await wait(sock.exists, "kubectl proxy", 10)
    provisioner.NAMESPACE = sandbox
    kube = provisioner.KubeClient(
        base_url="http://localhost",
        token="test",
        transport=httpx.AsyncHTTPTransport(uds=str(sock)),
    )
    del kube.client.headers["Authorization"]
    owner, attempt = uuid4(), uuid4()

    class Unit(InstructionUnits):
        def pod(self, meta, role, env, volumes, mounts):
            pod = super().pod(meta, role, env, volumes, mounts)
            node = (
                args.worker_node if role == "worker" and args.worker_node else args.node
            )
            if node:
                pod["spec"]["nodeSelector"] = {"kubernetes.io/hostname": node}
            return pod

    def unit():
        return Unit(
            kube,
            owner=owner,
            task=uuid4(),
            namespace=sandbox,
            app_namespace=app,
            ingress_namespace=app,
            image=args.image,
            pull_secret="",
            origin="https://" + host,
        )

    def helper(role, name, command, volumes=(), mounts=()):
        sec = {
            "allowPrivilegeEscalation": False,
            "readOnlyRootFilesystem": True,
            "capabilities": {"drop": ["ALL"]},
        }
        spec = {
            "automountServiceAccountToken": False,
            "restartPolicy": "Never",
            "securityContext": {
                "runAsNonRoot": True,
                "runAsUser": 10001,
                "seccompProfile": {"type": "RuntimeDefault"},
            },
            "containers": [
                {
                    "name": "fixture",
                    "image": args.image,
                    "command": command,
                    "securityContext": sec,
                    "volumeMounts": [{"name": "tmp", "mountPath": "/tmp"}, *mounts],
                }
            ],
            "volumes": [{"name": "tmp", "emptyDir": {}}, *volumes],
        }
        if args.node:
            spec["nodeSelector"] = {"kubernetes.io/hostname": args.node}
        return create(
            app,
            {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": name, "labels": {"app.kubernetes.io/name": role}},
                "spec": spec,
            },
        )

    async with kube.client:
        first, other = unit(), unit()
        a, b = await asyncio.gather(first.reserve(), other.reserve())
        for u, uid, aid in [(first, a["uid"], attempt), (other, b["uid"], uuid4())]:
            await u.bind(uid, Binding(attempt=aid, model="test", ticket="cni-test"))
        helper(
            "traefik",
            "control",
            ["python3", "-c", RECEIVER, a["uid"], str(attempt)],
            [{"name": "tls", "secret": {"secretName": "control-tls"}}],
            [{"name": "tls", "mountPath": "/tls", "readOnly": True}],
        )
        helper("knowbench-runner", "runner", ["sleep", "1200"])

        async def ready(u, uid):
            return u.status(await u.gateway(uid))["ready"]

        for u, uid in [(first, a["uid"]), (other, b["uid"])]:
            await wait(partial(ready, u, uid), "gateway readiness " + u.name)
        worker = first.name + "-worker"

        async def worker_ready():
            w = await first.worker(a["uid"])
            return w if w["ready"] else None

        w = await wait(worker_ready, "worker readiness")
        gateway_pod = await first.gateway(a["uid"])
        worker_pod = await kube.get("pods", worker)
        assert "activeDeadlineSeconds" not in gateway_pod["spec"]
        assert worker_pod["spec"]["activeDeadlineSeconds"] == 900
        print(
            "gateway",
            gateway_pod["spec"]["nodeName"],
            "worker",
            worker_pod["spec"]["nodeName"],
            flush=True,
        )
        for name in ("control", "runner"):
            ctl(
                "-n",
                app,
                "wait",
                "--for=condition=Ready",
                "pod/" + name,
                "--timeout=75s",
            )
        control = json.loads(ctl("-n", app, "get", "pod", "control", "-o", "json"))[
            "status"
        ]["podIP"]
        g, other_g = [
            (await kube.get("pods", u.name))["status"]["podIP"] for u in (first, other)
        ]
        assert execute(app, "runner", TCP, w["ip"], "47800") == "connected"
        assert execute(sandbox, worker, TCP, g, "47801") == "connected"
        assert execute(sandbox, first.name, TCP, control, "8443") == "connected"
        assert execute(sandbox, worker, TCP, other_g, "47801") == "blocked"
        assert execute(sandbox, worker, TCP, control, "8443") == "blocked"
        svc_ip = json.loads(ctl("-n", app, "get", "service", "control", "-o", "json"))[
            "spec"
        ]["clusterIP"]
        assert execute(sandbox, first.name, TCP, svc_ip, "443") == "connected"
        assert execute(sandbox, worker, TCP, svc_ip, "443") == "blocked"
        for code, params in [(TCP, (dns, "53")), (DNS, (dns,))]:
            assert execute(sandbox, first.name, code, *params) in (
                "connected",
                "answered",
            )
            assert execute(sandbox, worker, code, *params) == "blocked"
        print(
            "runner 到 worker、worker 到原网关连通；其他任务网关、供应商替身及 TCP/UDP DNS 均隔离",
            flush=True,
        )
        proof = await kube.get("persistentvolumeclaims", first.name + "-proof")
        assert proof["status"]["phase"] == "Bound"
        volume = proof["spec"]["volumeName"]
        print("PVC 已绑定", volume, flush=True)
        # Inject one synthetic, already received bill through the gateway's write-once persistence code.
        execute(
            sandbox,
            first.name,
            """
import os, sys
sys.path.insert(0, '/opt/sandbox')
from instruction_control import InstructionControl
control = InstructionControl(os.environ['INSTRUCTION_CONTROL_ORIGIN'],
    gateway_uid=os.environ['POD_UID'], attempt_id=sys.argv[1],
    ticket_file='/run/instruction/ticket', credential_file='/run/provider/instruction-provider.json',
    receipt_dir='/proof')
control.retain_receipt({'response_id':'synthetic','turn_id':'original','usage':{'output_tokens':1}})
""",
            str(attempt),
        )

        def has_file(file):
            return (
                execute(
                    app,
                    "control",
                    "from pathlib import Path; import sys; print(Path(sys.argv[1]).is_file())",
                    file,
                )
                == "True"
            )

        await wait(lambda: has_file("/tmp/observed"), "first receipt submission")
        await first.stop_worker(a["uid"])

        async def stopped():
            return (await kube.get("pods", worker))["status"]["phase"] in (
                "Failed",
                "Succeeded",
            )

        await wait(stopped, "worker termination")
        prev = (await kube.get("pods", first.name))["status"]["containerStatuses"][0][
            "restartCount"
        ]
        # Let kubectl finish the exec request before the test gateway process exits.
        execute(
            sandbox,
            first.name,
            "import subprocess as s; s.Popen(['sh','-c','sleep 1; kill -TERM 1'],"
            "stdin=s.DEVNULL,stdout=s.DEVNULL,stderr=s.DEVNULL,start_new_session=True)",
        )

        async def restarted():
            pod = await first.gateway(a["uid"])
            return (
                first.status(pod)["ready"]
                and pod["status"]["containerStatuses"][0]["restartCount"] > prev
            )

        await wait(restarted, "gateway restart on original mount")
        assert (await kube.get("persistentvolumeclaims", first.name + "-proof"))[
            "metadata"
        ]["uid"] == proof["metadata"]["uid"]
        execute(app, "control", "from pathlib import Path; Path('/tmp/accept').touch()")
        await wait(lambda: has_file("/tmp/received"), "receipt replay")
        await first.stop(a["uid"], attempt)

        async def gone(kind, name):
            return await kube.get(kind, name) is None

        await wait(lambda: gone("pods", first.name), "gateway deletion")
        await first.reclaim(a["uid"], attempt)
        await wait(
            lambda: gone("persistentvolumeclaims", first.name + "-proof"),
            "PVC deletion",
        )
        await wait(
            lambda: not ctl("get", "pv", volume, "--ignore-not-found", "-o", "name"),
            "PV reclamation",
        )
        print("执行停止、网关进程重启、原回执补交、PVC/PV 回收已验证", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--node", help="schedule on a node with the test image cached")
    parser.add_argument(
        "--worker-node", help="place the execution Pod on a second node"
    )
    args = parser.parse_args()
    if not __debug__:
        parser.error("run with Python assertions enabled")
    with tempfile.TemporaryDirectory() as tmp, ExitStack() as resources:
        asyncio.run(run(args, Path(tmp), resources))
