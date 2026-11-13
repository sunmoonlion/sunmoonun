"""Isolated execution manifests, immutable inputs and bounded worker results."""

import base64
import hashlib
import importlib.util
import json
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from test_provisioner import FakeApiServer
import provisioner
from script_contract import ScriptExecution
from script_jobs import ScriptJobs, job_name


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
                text=json.dumps(
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
            self.objects[("jobs", name)]["spec"]["suspend"] = json.loads(
                request.content
            )["spec"]["suspend"]
            return httpx.Response(200, json=self.objects[("jobs", name)])
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
    assert (await jobs.start(owner, run, body())).state == "running"
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
    await jobs.start(owner, run, body())
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
    await jobs.start(owner, replacement, body())
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
    await jobs.start(owner, run, body())
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
    await jobs.start(owner, run, body())
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
