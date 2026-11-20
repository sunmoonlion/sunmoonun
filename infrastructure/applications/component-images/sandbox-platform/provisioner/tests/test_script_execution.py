"""Isolated execution manifests, immutable inputs and bounded worker results."""

import base64
import hashlib
import importlib.util
import json
from pathlib import Path
from uuid import uuid4

import httpx
import provisioner
import pytest
from script_contract import ScriptExecution, execution_frame
from script_jobs import ScriptJobs, job_name
from test_provisioner import FakeApiServer


def file(path, content):
    raw = content.encode()
    return {
        "path": path,
        "data_base64": base64.b64encode(raw).decode(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def body(code="print(42)"):
    return ScriptExecution(
        path="scripts/run.py",
        args=[],
        stdin="21",
        files=[
            file("SKILL.md", "Run scripts/run.py"),
            file("scripts/run.py", code),
            file("references/n.txt", "2"),
        ],
    )


class JobsApi(FakeApiServer):
    def handler(self, request):
        if request.url.path.endswith("/log"):
            return httpx.Response(
                200,
                text="SUNMOON_INPUT_ACCEPTED\n"
                + json.dumps(
                    {
                        "exit_code": 0,
                        "stdout": "42\n",
                        "stderr": "",
                        "timed_out": False,
                        "output_truncated": False,
                        "artifacts": [],
                    }
                ),
            )
        name = request.url.path.rsplit("/", 1)[-1]
        if request.method == "DELETE" and "/jobs/" in request.url.path:
            current = self.objects.get(("jobs", name))
            if (
                current
                and json.loads(request.content).get("preconditions", {}).get("uid")
                != current["metadata"]["uid"]
            ):
                return httpx.Response(409, json={"code": 409})
        if request.method == "PATCH":
            job = self.objects[("jobs", name)]
            uid, waiting, claim = json.loads(request.content)
            annotations = job["metadata"]["annotations"]
            if (
                uid["value"] != job["metadata"]["uid"]
                or annotations["sunmoonai.com/delivery"] != waiting["value"]
            ):
                return httpx.Response(422)
            annotations["sunmoonai.com/delivery"] = claim["value"]
            return httpx.Response(200, json=job)
        response = super().handler(request)
        if request.method == "POST" and "/jobs" in request.url.path:
            obj = response.json()
            obj["metadata"]["uid"] = str(uuid4())
            self.objects[("jobs", obj["metadata"]["name"])]["metadata"]["uid"] = obj[
                "metadata"
            ]["uid"]
            return httpx.Response(201, json=obj)
        return response


@pytest.mark.anyio
async def test_job_is_secretless_bounded_and_immutable():
    api = JobsApi()
    kube = provisioner.KubeClient(
        base_url="https://kube.test",
        token="service-only",
        transport=httpx.MockTransport(api.handler),
    )
    jobs = ScriptJobs(
        kube, namespace="sandbox-pool", image="pinned-image", pull_secret="puller"
    )
    owner, run = uuid4(), uuid4()
    frame, raw = execution_frame(body())
    created, job = await jobs.reserve(owner, run, frame)
    assert created
    assert not any(kind == "secrets" for kind, _name in api.objects)
    assert "print(42)" not in json.dumps(job)
    uid = job["metadata"]["uid"]
    api.objects[("pods", "recipient")] = {
        "metadata": {
            "name": "recipient",
            "labels": {"batch.kubernetes.io/controller-uid": uid},
            "ownerReferences": [{"uid": uid, "kind": "Job", "controller": True}],
        },
        "status": {"containerStatuses": [{"name": "script", "state": {"running": {}}}]},
    }
    received = []

    async def receive(pod, data):
        received.append((pod, data))

    kube.send_script_input = receive
    await jobs.ready(owner, run, frame)
    await jobs.deliver(owner, run, frame, raw)
    await jobs.deliver(owner, run, frame, raw)
    assert received == [("recipient", raw)]
    job = api.objects[("jobs", job_name(owner))]
    pod = job["spec"]["template"]["spec"]
    assert pod["automountServiceAccountToken"] is False
    assert pod["enableServiceLinks"] is False
    assert (
        job["spec"]["backoffLimit"] == 0 and job["spec"]["activeDeadlineSeconds"] == 90
    )
    container = pod["containers"][0]
    assert "env" not in container and "envFrom" not in container
    assert container["securityContext"]["readOnlyRootFilesystem"]
    assert not any("persistentVolumeClaim" in v for v in pod["volumes"])
    policy = api.objects[("networkpolicies", "skill-execution-deny-all")]
    assert policy["spec"]["egress"] == [] and policy["spec"]["ingress"] == []
    before = len([c for c in api.calls if c == "POST jobs/"])
    await jobs.start(owner, run, body())
    assert len([c for c in api.calls if c == "POST jobs/"]) == before
    with pytest.raises(Exception) as exc:
        await jobs.start(owner, uuid4(), body())
    assert exc.value.status_code == 409
    await jobs.cancel(owner, uuid4())
    assert ("jobs", job_name(owner)) in api.objects
    await jobs.cancel(owner, run)
    assert (await jobs.status(owner, run)).state == "absent"
    await kube.client.aclose()


@pytest.mark.anyio
async def test_cancel_waits_for_job_and_running_pod_to_stop():
    api = JobsApi()
    kube = provisioner.KubeClient(
        base_url="https://kube.test",
        token="service-only",
        transport=httpx.MockTransport(api.handler),
    )
    jobs = ScriptJobs(
        kube,
        namespace="sandbox-pool",
        image="pinned-image",
        pull_secret="",
        cancel_timeout=0,
    )
    owner, run = uuid4(), uuid4()
    await jobs.reserve(owner, run, execution_frame(body())[0])
    api.objects[("pods", "still-running")] = {
        "metadata": {
            "name": "still-running",
            "labels": {
                "app": "skill-execution",
                "sunmoonai.com/owner": owner.hex,
                "sunmoonai.com/call": run.hex,
            },
        },
        "status": {"phase": "Running"},
    }
    with pytest.raises(Exception) as exc:
        await jobs.cancel(owner, run)
    assert exc.value.status_code == 504
    assert ("jobs", job_name(owner)) not in api.objects
    # A new run may occupy the slot while the old Pod is terminating.
    replacement = uuid4()
    await jobs.reserve(owner, replacement, execution_frame(body())[0])
    api.objects[("pods", "still-running")]["status"]["phase"] = "Failed"
    await jobs.cancel(owner, run)
    assert api.objects[("jobs", job_name(owner))]["metadata"]["annotations"][
        "sunmoonai.com/call"
    ] == str(replacement)
    await kube.client.aclose()


@pytest.mark.anyio
async def test_cancel_cannot_delete_a_replacement_job():
    api = JobsApi()

    def replace_on_delete(request):
        if request.method == "DELETE" and "/jobs/" in request.url.path:
            name = request.url.path.rsplit("/", 1)[-1]
            api.objects[("jobs", name)]["metadata"]["uid"] = "replacement-uid"
        return api.handler(request)

    kube = provisioner.KubeClient(
        base_url="https://kube.test",
        token="service-only",
        transport=httpx.MockTransport(replace_on_delete),
    )
    jobs = ScriptJobs(
        kube, namespace="sandbox-pool", image="pinned-image", pull_secret=""
    )
    owner, run = uuid4(), uuid4()
    await jobs.reserve(owner, run, execution_frame(body())[0])
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await jobs.cancel(owner, run)
    assert exc.value.response.status_code == 409
    assert (
        api.objects[("jobs", job_name(owner))]["metadata"]["uid"] == "replacement-uid"
    )
    await kube.client.aclose()


@pytest.mark.parametrize(
    "change",
    [
        {"path": "../run.py"},
        {"path": "/run.py"},
        {"path": "run.exe"},
        {"args": ["a\x00b"]},
        {"unexpected": True},
    ],
)
def test_reject_invalid_execution(change):
    with pytest.raises(ValueError):
        ScriptExecution.model_validate({**body().model_dump(), **change})


@pytest.mark.anyio
async def test_result_only_reads_pod_owned_by_the_exact_job():
    api = JobsApi()
    kube = provisioner.KubeClient(
        base_url="https://kube.test",
        token="service-only",
        transport=httpx.MockTransport(api.handler),
    )
    jobs = ScriptJobs(
        kube, namespace="sandbox-pool", image="pinned-image", pull_secret=""
    )
    owner, run = uuid4(), uuid4()
    await jobs.reserve(owner, run, execution_frame(body())[0])
    job = api.objects[("jobs", job_name(owner))]
    job["status"] = {"succeeded": 1}
    api.objects[("pods", "other-execution")] = {
        "metadata": {
            "name": "other-execution",
            "labels": {
                "batch.kubernetes.io/job-name": job_name(owner),
                "batch.kubernetes.io/controller-uid": "other-job",
            },
        }
    }
    assert (await jobs.status(owner, run)).state == "failed"
    api.objects[("pods", "correct-execution")] = {
        "metadata": {
            "name": "correct-execution",
            "labels": {"batch.kubernetes.io/controller-uid": job["metadata"]["uid"]},
        }
    }
    assert (await jobs.status(owner, run)).state == "failed"
    api.objects[("pods", "correct-execution")]["metadata"]["ownerReferences"] = [
        {"kind": "Job", "controller": True, "uid": job["metadata"]["uid"]}
    ]
    result = await jobs.status(owner, run)
    assert result.state == "finished" and result.result.stdout == "42\n"
    await kube.client.aclose()


def worker():
    path = Path(__file__).resolve().parents[2] / "image/skill_execute.py"
    spec = importlib.util.spec_from_file_location("skill_execute", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_worker_relative_paths_stdin_and_artifacts(tmp_path):
    code = "from pathlib import Path\nimport sys\nn=int(sys.stdin.read())*int(Path('references/n.txt').read_text())\nPath('outputs/result.txt').write_text(str(n))\nprint(n)\n"
    result = worker().execute(body(code).model_dump(), tmp_path / "package")
    assert result["exit_code"] == 0 and result["stdout"] == "42\n", result
    assert base64.b64decode(result["artifacts"][0]["data_base64"]) == b"42"


def test_worker_timeout_output_limit_and_links(tmp_path):
    result = worker().execute(
        body("import time\ntime.sleep(60)").model_dump(),
        tmp_path / "slow",
        timeout=0.05,
    )
    assert result["timed_out"] and result["exit_code"] != 0
    code = "from pathlib import Path\nprint('x'*100000)\nPath('outputs/link').symlink_to('../SKILL.md')\n"
    result = worker().execute(body(code).model_dump(), tmp_path / "bounded")
    assert result["exit_code"] == 0 and result["output_truncated"]
    assert len(result["stdout"]) == 65536 and result["artifacts"] == []
    assert result["artifact_error"]


@pytest.mark.parametrize("names", [["../a"], ["x", "x"], ["x"] * 9])
def test_input_files_are_named_and_bounded(names):
    with pytest.raises(ValueError):
        ScriptExecution.model_validate(
            {**body().model_dump(), "inputs": [file(n, "a") for n in names]}
        )


def test_reject_aggregate_business_inputs_above_two_mib():
    spec = body().model_dump()
    spec["inputs"] = [file(str(i), "a" * 524288) for i in range(4)]
    ScriptExecution.model_validate(spec)
    spec["inputs"].append(file("overflow", "1"))
    with pytest.raises(ValueError, match="2 MiB"):
        ScriptExecution.model_validate(spec)


def test_truncated_frame_cannot_start_a_package(tmp_path):
    import subprocess
    import sys

    marker = tmp_path / "started"
    spec = body(f"from pathlib import Path; Path({str(marker)!r}).touch()")
    frame, raw = execution_frame(spec)
    path = Path(__file__).resolve().parents[2] / "image/skill_execute.py"
    proc = subprocess.run(
        [sys.executable, str(path), str(frame.size), frame.sha256],
        input=raw[:-1],
        capture_output=True,
        check=False,
        timeout=5,
    )
    assert (
        proc.returncode != 0
        and not marker.exists()
        and b"SUNMOON_INPUT_ACCEPTED" not in proc.stdout
    )


@pytest.mark.anyio
async def test_container_meter_uses_owned_pod_and_kubelet_timestamps():
    api = JobsApi()
    kube = provisioner.KubeClient(
        base_url="https://kube.test",
        token="service-only",
        transport=httpx.MockTransport(api.handler),
    )
    jobs = ScriptJobs(
        kube, namespace="sandbox-pool", image="pinned-image", pull_secret=""
    )
    owner, run = uuid4(), uuid4()
    _, job = await jobs.reserve(owner, run, execution_frame(body())[0])
    job_uid = job["metadata"]["uid"]
    pod_uid = str(uuid4())
    pod = {
        "metadata": {
            "name": "measured",
            "uid": pod_uid,
            "labels": {"batch.kubernetes.io/controller-uid": job_uid},
            "ownerReferences": [{"uid": job_uid, "kind": "Job", "controller": True}],
        },
        "status": {
            "containerStatuses": [
                {
                    "name": "script",
                    "restartCount": 0,
                    "containerID": "containerd://test",
                    "state": {
                        "terminated": {
                            "startedAt": "2026-11-20T00:00:00Z",
                            "finishedAt": "2026-11-20T00:00:04Z",
                        }
                    },
                }
            ]
        },
    }
    api.objects[("pods", "measured")] = pod
    meter = await jobs.container_meter(owner, run)
    assert (
        str(meter.job_uid) == job_uid
        and str(meter.pod_uid) == pod_uid
        and meter.run_id == run
    )
    assert (meter.finished_at - meter.started_at).total_seconds() == 4
    with pytest.raises(provisioner.HTTPException, match="404"):
        await jobs.container_meter(owner, uuid4())
    pod["spec"] = {"nodeName": "test"}
    pod["status"] = {
        "phase": "Failed",
        "containerStatuses": [
            {
                "name": "script",
                "restartCount": 0,
                "state": {"waiting": {"reason": "ErrImagePull"}},
            }
        ],
    }
    assert (await jobs.container_meter(owner, run)).reason == "ErrImagePull"
    pod["status"]["containerStatuses"][0]["lastState"] = {"running": {}}
    with pytest.raises(provisioner.HTTPException, match="409"):
        await jobs.container_meter(owner, run)
    pod["status"] = {"phase": "Pending"}
    pod["spec"] = {}
    with pytest.raises(provisioner.HTTPException, match="409"):
        await jobs.container_meter(owner, run)
    pod["status"]["phase"] = "Failed"
    assert (await jobs.container_meter(owner, run)).reason == "unscheduled"
    pod["metadata"]["ownerReferences"][0]["uid"] = str(uuid4())
    with pytest.raises(provisioner.HTTPException, match="409"):
        await jobs.container_meter(owner, run)
    await kube.client.aclose()


@pytest.mark.anyio
async def test_shared_script_policy_creation_race_and_drift():
    api = JobsApi()
    first = True

    def race(request):
        nonlocal first
        response = api.handler(request)
        if (
            first
            and request.method == "POST"
            and request.url.path.endswith("/networkpolicies")
        ):
            # The concurrent account wins the create; this request receives AlreadyExists.
            first = False
            return httpx.Response(409, json={"reason": "AlreadyExists"})
        return response

    kube = provisioner.KubeClient(
        base_url="https://kube.test", token="test", transport=httpx.MockTransport(race)
    )
    jobs = ScriptJobs(kube, namespace="sandbox-pool", image="test", pull_secret="")
    try:
        frame, _ = execution_frame(body())
        for _ in range(2):
            assert (await jobs.reserve(uuid4(), uuid4(), frame))[0]
        assert api.calls.count("POST networkpolicies/") == 1
        assert not any(c.startswith("PUT networkpolicies/") for c in api.calls)
        api.objects[("networkpolicies", "skill-execution-deny-all")]["spec"][
            "egress"
        ] = [{}]
        with pytest.raises(
            provisioner.HTTPException, match="isolation_unavailable_before_creation"
        ):
            await jobs.reserve(uuid4(), uuid4(), frame)
        assert api.calls.count("POST jobs/") == 2
    finally:
        await kube.client.aclose()


@pytest.mark.anyio
@pytest.mark.parametrize("code, replaced", [(409, False), (422, False), (409, True)])
async def test_metered_stop_rereads_same_pod_after_patch_conflict(code, replaced):
    from unittest.mock import AsyncMock, Mock

    owner, run = uuid4(), uuid4()
    uid = str(uuid4())
    kube = Mock()
    kube.get = AsyncMock(
        return_value={"metadata": {"annotations": {"sunmoonai.com/call": str(run)}}}
    )
    response = httpx.Response(
        code, request=httpx.Request("PATCH", "https://kube.test/pod")
    )
    kube.client.patch = AsyncMock(return_value=response)
    jobs = ScriptJobs(kube, namespace="test", image="test", pull_secret="")
    running = {
        "metadata": {"uid": uid, "name": "script"},
        "status": {"phase": "Running"},
    }
    terminal = {
        "metadata": {"uid": str(uuid4()) if replaced else uid},
        "status": {"phase": "Succeeded"},
    }
    jobs.owned_pod = AsyncMock(
        side_effect=[
            running,
            terminal,
            {**running, "spec": {"activeDeadlineSeconds": 1}},
        ]
    )
    if replaced:
        with pytest.raises(httpx.HTTPStatusError):
            await jobs.stop_metered(owner, run)
    else:
        await jobs.stop_metered(owner, run)
    await jobs.stop_metered(owner, run)
    kube.client.patch.assert_awaited_once()
