"""One bounded script Job per account. The application's call ledger owns receipts."""

from __future__ import annotations

import asyncio
import base64
from uuid import UUID

from fastapi import HTTPException
from script_contract import (
    ScriptExecution,
    ScriptFrame,
    ScriptResult,
    ScriptStatus,
    execution_frame,
)


def job_name(owner: UUID) -> str:
    return "skill-" + owner.hex


class ScriptJobs:
    def __init__(
        self,
        kube,
        *,
        namespace: str,
        image: str,
        pull_secret: str,
        cancel_timeout: float = 5,
    ):
        self.kube, self.namespace, self.image, self.pull_secret = (
            kube,
            namespace,
            image,
            pull_secret,
        )
        self.cancel_timeout = cancel_timeout

    async def start(
        self, owner: UUID, run: UUID, body: ScriptExecution
    ) -> ScriptStatus:
        frame, raw = execution_frame(body)
        created, _ = await self.reserve(owner, run, frame)
        if created:
            await self.ready(owner, run, frame)
            await self.deliver(owner, run, frame, raw)
        return await self.status(owner, run)

    async def reserve(self, owner: UUID, run: UUID, frame: ScriptFrame):
        name = job_name(owner)
        existing = await self.kube.get("jobs", name)
        if existing:
            self.check_frame(existing, run, frame)
            return False, existing
        labels = {
            "app": "skill-execution",
            "sunmoonai.com/owner": owner.hex,
            "sunmoonai.com/call": run.hex,
        }
        meta = {"name": name, "namespace": self.namespace, "labels": labels}
        # A static deny-all policy for all package executors; no connection to Codex,
        # the Kubernetes API, cloud metadata or a user's local link.
        await self.kube.apply(
            "networkpolicies",
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "skill-execution-deny-all",
                    "namespace": self.namespace,
                },
                "spec": {
                    "podSelector": {"matchLabels": {"app": "skill-execution"}},
                    "policyTypes": ["Ingress", "Egress"],
                    "ingress": [],
                    "egress": [],
                },
            },
        )
        job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                **meta,
                "annotations": {
                    "sunmoonai.com/call": str(run),
                    "sunmoonai.com/input": frame.sha256,
                    "sunmoonai.com/bytes": str(frame.size),
                    "sunmoonai.com/delivery": "waiting",
                },
            },
            "spec": {
                "backoffLimit": 0,
                "activeDeadlineSeconds": 90,
                "ttlSecondsAfterFinished": 900,
                "template": {
                    "metadata": {"labels": labels},
                    "spec": {
                        "restartPolicy": "Never",
                        "automountServiceAccountToken": False,
                        "enableServiceLinks": False,
                        "terminationGracePeriodSeconds": 1,
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 10001,
                            "runAsGroup": 10001,
                            "fsGroup": 10001,
                            "seccompProfile": {"type": "RuntimeDefault"},
                        },
                        **(
                            {"imagePullSecrets": [{"name": self.pull_secret}]}
                            if self.pull_secret
                            else {}
                        ),
                        "containers": [
                            {
                                "name": "script",
                                "image": self.image,
                                "command": [
                                    "/usr/bin/tini",
                                    "--",
                                    "/usr/bin/python3",
                                    "/opt/sandbox/skill_execute.py",
                                    str(frame.size),
                                    frame.sha256,
                                ],
                                "stdin": True,
                                "stdinOnce": True,
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "readOnlyRootFilesystem": True,
                                    "capabilities": {"drop": ["ALL"]},
                                },
                                "resources": {
                                    "requests": {"cpu": "50m", "memory": "64Mi"},
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "256Mi",
                                        "ephemeral-storage": "64Mi",
                                    },
                                },
                                "volumeMounts": [
                                    {"name": "work", "mountPath": "/tmp"},
                                ],
                            }
                        ],
                        "volumes": [
                            {
                                "name": "work",
                                "emptyDir": {"medium": "Memory", "sizeLimit": "32Mi"},
                            },
                        ],
                    },
                },
            },
        }
        # Create only. Concurrent requests never replace a Job or change its input.
        response = await self.kube.client.post(self.kube.path("jobs"), json=job)
        if response.status_code == 409:
            current = await self.kube.get("jobs", name)
            self.check_frame(current, run, frame)
            return False, current
        response.raise_for_status()
        return True, response.json()

    @staticmethod
    def check_frame(job, run, frame):
        annotations = (job or {}).get("metadata", {}).get("annotations", {})
        if (
            annotations.get("sunmoonai.com/call") != str(run)
            or annotations.get("sunmoonai.com/input") != frame.sha256
            or annotations.get("sunmoonai.com/bytes") != str(frame.size)
        ):
            raise HTTPException(409, "Script slot or approved input changed")

    async def waiting_pod(self, job):
        uid = job["metadata"]["uid"]
        pods = await self.kube.list("pods", f"batch.kubernetes.io/controller-uid={uid}")
        if len(pods) != 1:
            return None
        pod = pods[0]
        if pod["metadata"].get("deletionTimestamp") or not any(
            ref.get("controller") and ref.get("uid") == uid and ref.get("kind") == "Job"
            for ref in pod["metadata"].get("ownerReferences", [])
        ):
            return None
        if any(
            c.get("name") == "script" and "running" in c.get("state", {})
            for c in pod.get("status", {}).get("containerStatuses", [])
        ):
            return pod["metadata"]["name"]
        return None

    async def ready(self, owner, run, frame):
        async with asyncio.timeout(50):
            while True:
                job = await self.kube.get("jobs", job_name(owner))
                self.check_frame(job, run, frame)
                if (
                    job["metadata"]["annotations"].get("sunmoonai.com/delivery")
                    == "claimed"
                ):
                    return
                if await self.waiting_pod(job):
                    return
                if job.get("status", {}).get("failed") or job.get("status", {}).get(
                    "succeeded"
                ):
                    raise HTTPException(409, "Script slot is already closed")
                await asyncio.sleep(0.25)

    async def deliver(self, owner, run, frame, raw):
        job = await self.kube.get("jobs", job_name(owner))
        self.check_frame(job, run, frame)
        if job["metadata"]["annotations"].get("sunmoonai.com/delivery") == "claimed":
            return await self.status(owner, run)
        pod = await self.waiting_pod(job)
        if not pod:
            raise HTTPException(409, "Script input receiver is unavailable")
        # One immutable delivery claim across concurrent requests and provisioner restarts.
        field = "/metadata/annotations/sunmoonai.com~1delivery"
        response = await self.kube.client.patch(
            self.kube.path("jobs", job_name(owner)),
            headers={"Content-Type": "application/json-patch+json"},
            json=[
                {
                    "op": "test",
                    "path": "/metadata/uid",
                    "value": job["metadata"]["uid"],
                },
                {"op": "test", "path": field, "value": "waiting"},
                {"op": "replace", "path": field, "value": "claimed"},
            ],
        )
        if response.status_code in (409, 422):
            current = await self.kube.get("jobs", job_name(owner))
            self.check_frame(current, run, frame)
            if (
                current["metadata"]["annotations"].get("sunmoonai.com/delivery")
                == "claimed"
            ):
                return await self.status(owner, run)
        response.raise_for_status()
        await self.kube.send_script_input(pod, raw)
        return ScriptStatus(state="running")

    async def status(self, owner: UUID, run: UUID) -> ScriptStatus:
        name = job_name(owner)
        job = await self.kube.get("jobs", name)
        if not job or job["metadata"].get("annotations", {}).get(
            "sunmoonai.com/call"
        ) != str(run):
            return ScriptStatus(state="absent")
        status = job.get("status", {})
        if status.get("succeeded"):
            pods = await self.kube.list(
                "pods", f"batch.kubernetes.io/controller-uid={job['metadata']['uid']}"
            )
            if len(pods) != 1:
                return ScriptStatus(
                    state="failed", error="Cannot identify a unique script result"
                )
            path = self.kube.path("pods", pods[0]["metadata"]["name"]) + "/log"
            response = await self.kube.client.get(
                path, params={"container": "script", "limitBytes": 2000000}
            )
            response.raise_for_status()
            try:
                raw = response.content
                if "sunmoonai.com/bytes" in job["metadata"].get("annotations", {}):
                    marker = b"SUNMOON_INPUT_ACCEPTED\n"
                    if not raw.startswith(marker):
                        raise ValueError("Script input was never acknowledged")
                    raw = raw[len(marker) :]
                result = ScriptResult.model_validate_json(raw)
                if (
                    sum(len(base64.b64decode(a.data_base64)) for a in result.artifacts)
                    > 512 * 1024
                ):
                    raise ValueError("Artifact limit exceeded")
            except ValueError:
                return ScriptStatus(
                    state="failed",
                    error="Script returned an invalid or oversized result",
                )
            return ScriptStatus(state="finished", result=result)
        if any(
            c.get("status") == "True" and c.get("type") == "Failed"
            for c in status.get("conditions", [])
        ):
            return ScriptStatus(
                state="failed",
                error="Execution stopped: startup, resource limit or deadline failure",
            )
        return ScriptStatus(state="running")

    async def cancel(self, owner: UUID, run: UUID) -> None:
        job = await self.kube.get("jobs", job_name(owner))
        if job and job["metadata"].get("annotations", {}).get(
            "sunmoonai.com/call"
        ) == str(run):
            # A slot may be reused between GET and DELETE. Never delete its new Job.
            await self.kube.delete("jobs", job_name(owner), uid=job["metadata"]["uid"])
        deadline = asyncio.get_running_loop().time() + self.cancel_timeout
        while True:
            current = await self.kube.get("jobs", job_name(owner))
            same_job = bool(
                current
                and current["metadata"].get("annotations", {}).get("sunmoonai.com/call")
                == str(run)
            )
            pods = await self.kube.list(
                "pods",
                f"app=skill-execution,sunmoonai.com/owner={owner.hex},sunmoonai.com/call={run.hex}",
            )
            active = any(
                p.get("status", {}).get("phase") not in ("Succeeded", "Failed")
                for p in pods
            )
            if not same_job and not active:
                return
            if asyncio.get_running_loop().time() >= deadline:
                raise HTTPException(
                    504,
                    "Stop requested, but execution termination is not confirmed; query status or retry",
                )
            await asyncio.sleep(0.1)
