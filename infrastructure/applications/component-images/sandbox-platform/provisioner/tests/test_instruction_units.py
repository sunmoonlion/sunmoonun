"""Exercise admission against an isolated local kube-apiserver with no kubelet.

Set INSTRUCTION_KUBE_TEST_DIR to a test CA/client certificate directory and
INSTRUCTION_KUBE_TEST_PORT to the loopback API port. Readiness is injected.
"""

import asyncio
import os
import ssl
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from test_provisioner import target


@pytest.mark.anyio
async def test_instruction_unit_lifecycle(monkeypatch):
    directory = os.environ.get("INSTRUCTION_KUBE_TEST_DIR")
    if not directory:
        pytest.skip("requires a disposable loopback kube-apiserver")
    directory = Path(directory)
    ctx = ssl.create_default_context(cafile=str(directory / "ca.crt"))
    ctx.load_cert_chain(directory / "client.crt", directory / "client.key")
    ns = "instruction-test-" + uuid4().hex[:12]
    monkeypatch.setattr(target, "NAMESPACE", ns)
    monkeypatch.setattr(target, "PROVISIONER_TOKEN", "test-lifecycle")
    kube = target.KubeClient(
        base_url="https://127.0.0.1:" + os.environ["INSTRUCTION_KUBE_TEST_PORT"],
        verify=ctx,
    )
    del kube.client.headers[
        "Authorization"
    ]  # Authenticate with this test client certificate.
    headers = {"Authorization": "Bearer test-lifecycle"}
    owner, task, attempt = uuid4(), uuid4(), uuid4()
    root = f"/v1/instruction-executions/{owner}/{task}"
    namespace = {
        "metadata": {
            "name": ns,
            "labels": {"pod-security.kubernetes.io/enforce": "restricted"},
        }
    }
    async with kube.client:
        (
            await kube.client.post("/api/v1/namespaces", json=namespace)
        ).raise_for_status()
        try:
            app = target.create_app(target.Provisioner(kube))
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://p"
            ) as client:
                assert (await client.post(root + "/prepare")).status_code == 401
                client.headers.update(headers)
                assert (await client.get(root + "/reservation")).status_code == 404
                monkeypatch.delenv("INSTRUCTION_CONTROL_ORIGIN", raising=False)
                assert (await client.post(root + "/prepare")).status_code == 503
                monkeypatch.setenv(
                    "INSTRUCTION_CONTROL_ORIGIN",
                    "https://test-control.test.svc.cluster.local",
                )
                first, second = await asyncio.gather(
                    *(client.post(root + "/prepare") for _ in range(2))
                )
                assert first.status_code == second.status_code == 200, (
                    first.text,
                    second.text,
                )
                uid = first.json()["uid"]
                assert second.json()["uid"] == uid
                assert (await client.get(root + "/reservation")).json() == {"uid": uid}
                prefix = root + "/" + uid
                binding = {
                    "attempt": str(attempt),
                    "ticket": "test-ticket",
                    "model": "test-model",
                }
                assert (
                    await client.put(f"{root}/{uuid4()}/binding", json=binding)
                ).status_code == 409
                assert (await client.put(prefix + "/worker")).status_code == 409
                assert (
                    await client.put(prefix + "/binding", json=binding)
                ).status_code == 200
                assert (
                    await client.put(
                        prefix + "/binding", json={**binding, "attempt": str(uuid4())}
                    )
                ).status_code == 409
                bind_turn = {**binding, "turn": "first"}
                assert (
                    await client.put(prefix + "/binding", json=bind_turn)
                ).status_code == 200
                assert (
                    await client.put(
                        prefix + "/binding", json={**binding, "turn": "second"}
                    )
                ).status_code == 409
                assert (
                    await client.put(
                        prefix + "/binding", json={**binding, "ticket": "renewed"}
                    )
                ).status_code == 200
                (gateway,) = await kube.list("pods", "app=instruction-gateway")
                assert "activeDeadlineSeconds" not in gateway["spec"]
                name = gateway["metadata"]["name"]
                assert (await kube.get("secrets", name + "-binding"))["data"][
                    "turn"
                ] == "Zmlyc3Q="
                # This independent API has no scheduler or kubelet.
                gateway["status"] = {
                    "phase": "Running",
                    "podIP": "10.0.0.1",
                    "conditions": [{"type": "Ready", "status": "True"}],
                }
                (
                    await kube.client.put(
                        kube.path("pods", name) + "/status", json=gateway
                    )
                ).raise_for_status()
                first, second = await asyncio.gather(
                    *(client.put(prefix + "/worker") for _ in range(2))
                )
                assert first.status_code == second.status_code == 200, (
                    first.text,
                    second.text,
                )
                assert first.json() == second.json()
                (worker,) = await kube.list("pods", "app=instruction-worker")
                spec = worker["spec"]
                assert spec["activeDeadlineSeconds"] == 900
                assert not spec["automountServiceAccountToken"]
                assert [
                    v["secret"]["items"] for v in spec["volumes"] if "secret" in v
                ] == [[{"key": "token", "path": "token"}]]
                policy = (await kube.get("networkpolicies", name + "-worker"))["spec"]
                assert policy["egress"] == [
                    {
                        "ports": [{"protocol": "TCP", "port": 47801}],
                        "to": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "app": "instruction-gateway",
                                        "sunmoonai.com/unit": gateway["metadata"][
                                            "labels"
                                        ]["sunmoonai.com/unit"],
                                    }
                                }
                            }
                        ],
                    }
                ]
                assert (await client.delete(prefix + "/proof")).status_code == 409
                assert (await client.delete(prefix)).status_code == 409
                assert (await client.post(prefix + "/stop")).status_code == 200
                assert (await client.post(prefix + "/stop")).status_code == 200
                assert (await client.put(prefix + "/worker")).status_code == 409
                assert (await kube.get("pods", name + "-worker"))["spec"][
                    "activeDeadlineSeconds"
                ] == 1
                assert (await client.delete(prefix)).status_code == 409
                assert (
                    await client.delete(
                        prefix, params={"settled_attempt": str(attempt)}
                    )
                ).status_code == 200
                proof = await kube.get("persistentvolumeclaims", name + "-proof")
                assert proof["metadata"]["annotations"][
                    "sunmoonai.com/retired-attempt"
                ] == str(attempt)
                assert (
                    await client.delete(
                        prefix + "/proof", params={"settled_attempt": str(uuid4())}
                    )
                ).status_code == 409
                # Complete foreground deletion as the absent local GC would do.
                if await kube.get("pods", name):
                    (
                        await kube.client.patch(
                            kube.path("pods", name),
                            headers={"Content-Type": "application/merge-patch+json"},
                            json={"metadata": {"finalizers": []}},
                        )
                    ).raise_for_status()
                assert (await client.post(root + "/prepare")).status_code == 404
                assert (
                    await client.delete(
                        prefix + "/proof", params={"settled_attempt": str(attempt)}
                    )
                ).json() == {"removed": True}
        finally:
            await kube.client.delete("/api/v1/namespaces/" + ns)
