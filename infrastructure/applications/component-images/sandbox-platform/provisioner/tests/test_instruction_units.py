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
@pytest.mark.parametrize("scoped", [False, True], ids=["legacy-task", "per-attempt"])
async def test_instruction_unit_lifecycle(monkeypatch, scoped):
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
    sibling_attempt = uuid4()
    sibling_root = root + "/attempts/" + str(sibling_attempt)
    if scoped:
        root += "/attempts/" + str(attempt)
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
                # Interrupt the first reservation immediately after the PVC commit.
                original_create = target.InstructionUnits.create

                async def interrupt(unit, kind, body, **kwargs):
                    if kind == "pods":
                        raise target.HTTPException(503, "interrupted")
                    return await original_create(unit, kind, body, **kwargs)

                with monkeypatch.context() as interrupted:
                    interrupted.setattr(target.InstructionUnits, "create", interrupt)
                    assert (await client.post(root + "/prepare")).status_code == 503
                partial = (await client.get(root + "/reservation")).json()
                assert partial["state"] == "pvc_only"
                assert (
                    await client.post(
                        root + "/prepare", params={"proof_uid": str(uuid4())}
                    )
                ).status_code == 409
                first, second = await asyncio.gather(
                    *(
                        client.post(
                            root + "/prepare",
                            params={"proof_uid": partial["proof_uid"]},
                        )
                        for _ in range(2)
                    )
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
                async def mark_ready(pod, ip):
                    pod["status"] = {
                        "phase": "Running",
                        "podIP": ip,
                        "conditions": [{"type": "Ready", "status": "True"}],
                    }
                    (
                        await kube.client.put(
                            kube.path("pods", pod["metadata"]["name"]) + "/status",
                            json=pod,
                        )
                    ).raise_for_status()

                await mark_ready(gateway, "10.0.0.1")
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
                if scoped:
                    sibling = await client.post(sibling_root + "/prepare")
                    assert sibling.status_code == 200, sibling.text
                    sibling_uid = sibling.json()["uid"]
                    assert sibling_uid != uid
                    sibling_prefix = sibling_root + "/" + sibling_uid
                    assert (
                        await client.put(sibling_prefix + "/binding", json=binding)
                    ).status_code == 409
                    assert (
                        await client.post(sibling_root + "/" + uid + "/stop")
                    ).status_code == 409
                    sibling_binding = {**binding, "attempt": str(sibling_attempt)}
                    assert (
                        await client.put(
                            sibling_prefix + "/binding", json=sibling_binding
                        )
                    ).status_code == 200
                    (sibling_gateway,) = await kube.list(
                        "pods",
                        "app=instruction-gateway,sunmoonai.com/attempt="
                        + sibling_attempt.hex,
                    )
                    await mark_ready(sibling_gateway, "10.0.0.2")
                    sibling_worker = await client.put(sibling_prefix + "/worker")
                    assert sibling_worker.status_code == 200
                    assert sibling_worker.json()["uid"] != first.json()["uid"]
                    claims = await kube.list(
                        "persistentvolumeclaims", "sunmoonai.com/task=" + task.hex
                    )
                    assert {
                        obj["metadata"]["labels"]["sunmoonai.com/attempt"]
                        for obj in claims
                    } == {attempt.hex, sibling_attempt.hex}
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
                if scoped:
                    assert (await client.get(sibling_root + "/reservation")).json() == {
                        "uid": sibling_uid
                    }
                    assert (await client.get(sibling_prefix)).status_code == 200
                    remaining = await client.put(sibling_prefix + "/worker")
                    assert (
                        remaining.status_code == 200
                        and remaining.json()["uid"] == sibling_worker.json()["uid"]
                    )
                    assert (
                        await client.delete(
                            sibling_prefix + "/proof",
                            params={"settled_attempt": str(attempt)},
                        )
                    ).status_code == 409
        finally:
            await kube.client.delete("/api/v1/namespaces/" + ns)


@pytest.mark.anyio
@pytest.mark.parametrize("phase", ["Succeeded", "Failed"])
async def test_terminal_worker_expiry_including_patch_race(phase):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from k8s_lifecycle import expire_pod

    pod = {"metadata": {"uid": str(uuid4()), "name": "worker"}}
    terminal = {**pod, "status": {"phase": phase}}
    response = httpx.Response(422, request=httpx.Request("PATCH", "https://test/pod"))
    patch = AsyncMock(return_value=response)
    kube = SimpleNamespace(
        client=SimpleNamespace(patch=patch),
        get=AsyncMock(return_value=terminal),
        path=lambda kind, name: "/pods/" + name,
    )
    await expire_pod(kube, terminal, absent_ok=True)
    patch.assert_not_awaited()
    await expire_pod(kube, pod, absent_ok=True)
    patch.assert_awaited_once()
    kube.get.return_value = {**terminal, "metadata": {"uid": str(uuid4())}}
    with pytest.raises(httpx.HTTPStatusError):
        await expire_pod(kube, pod, absent_ok=True)


@pytest.mark.anyio
async def test_attempt_credential_only_reaches_original_gateway(monkeypatch):
    import json
    from base64 import b64decode
    from unittest.mock import AsyncMock

    from instruction_units import Binding, InstructionUnits

    owner, task, attempt = uuid4(), uuid4(), uuid4()
    objects = {}

    async def create(kind, body, **_kwargs):
        key = (kind, body["metadata"]["name"])
        if key not in objects:
            body["metadata"]["uid"] = str(uuid4())
            body["status"] = {
                "podIP": "127.0.0.1",
                "conditions": [{"type": "Ready", "status": "True"}],
            }
            objects[key] = body
        return objects[key]

    kube = AsyncMock()
    kube.get.side_effect = lambda kind, name: objects.get((kind, name))
    unit = InstructionUnits(
        kube,
        owner=owner,
        task=task,
        attempt=attempt,
        namespace="test",
        app_namespace="app",
        ingress_namespace="ingress",
        image="test-image",
        pull_secret=None,
        origin="https://control.test.svc.cluster.local",
    )
    monkeypatch.setattr(unit, "create", create)
    monkeypatch.setattr(unit, "policy", AsyncMock())
    monkeypatch.setattr(unit, "remember", AsyncMock())
    uid = (await unit.reserve())["uid"]
    route = {
        "credential_id": str(uuid4()),
        "model": "review",
        "provider": "fixture",
        "base_url": "https://review.example.test/v1",
        "key": "fixture-only",
    }
    binding = Binding(
        attempt=attempt, ticket="test-ticket", model="review", review_provider=route
    )
    await unit.bind(uid, binding)
    await unit.bind(uid, binding)
    with pytest.raises(target.HTTPException) as conflict:
        await unit.bind(
            uid,
            Binding(
                attempt=attempt,
                ticket="test-ticket",
                model="review",
                review_provider={**route, "credential_id": str(uuid4())},
            ),
        )
    assert conflict.value.status_code == 409
    await unit.worker(uid)
    secret = objects["secrets", unit.name + "-binding"]
    assert secret["metadata"]["ownerReferences"][0]["uid"] == uid
    assert json.loads(b64decode(secret["data"]["review-provider.json"])) == route
    gateway_spec = objects["pods", unit.name]["spec"]
    volume = next(v for v in gateway_spec["volumes"] if v["name"] == "review-provider")
    assert volume["secret"]["secretName"] == unit.name + "-binding"
    worker_spec = objects["pods", unit.name + "-worker"]["spec"]
    assert {v["name"] for v in worker_spec["volumes"]} == {"access", "work"}
    assert "fixture-only" not in json.dumps(worker_spec)
