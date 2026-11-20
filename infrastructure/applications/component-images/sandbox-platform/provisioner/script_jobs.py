"""One bounded script Job per account. The application's call ledger owns receipts."""

from __future__ import annotations

import asyncio
import base64
from uuid import UUID

from fastapi import HTTPException
from script_contract import (
    ScriptContainerMeter,
    ScriptExecution,
    ScriptFrame,
    ScriptNotStarted,
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

    async def ensure_isolation_policy(self, run):
        name = "skill-execution-deny-all"
        selector = {"matchLabels": {"app": "skill-execution"}}
        current = await self.kube.get("networkpolicies", name)
        if current is None:
            response = await self.kube.client.post(
                self.kube.path("networkpolicies"),
                json={
                    "apiVersion": "networking.k8s.io/v1",
                    "kind": "NetworkPolicy",
                    "metadata": {"name": name, "namespace": self.namespace},
                    "spec": {
                        "podSelector": selector,
                        "policyTypes": ["Ingress", "Egress"],
                        "ingress": [],
                        "egress": [],
                    },
                },
            )
            if response.status_code == 409:
                current = await self.kube.get("networkpolicies", name)
            else:
                response.raise_for_status()
                current = response.json()
        spec = (current or {}).get("spec", {})
        if (
            not current
            or current["metadata"].get("deletionTimestamp")
            or spec.get("podSelector") != selector
            or set(spec.get("policyTypes", [])) != {"Ingress", "Egress"}
            or spec.get("ingress")
            or spec.get("egress")
        ):
            raise HTTPException(
                409,
                {"code": "isolation_unavailable_before_creation", "run_id": str(run)},
            )

    async def reserve(self, owner: UUID, run: UUID, frame: ScriptFrame):
        name = job_name(owner)
        existing = await self.kube.get("jobs", name)
        if existing:
            self.check_slot(existing, run)
            self.check_frame(existing, run, frame)
            return False, existing
        labels = {
            "app": "skill-execution",
            "sunmoonai.com/owner": owner.hex,
            "sunmoonai.com/call": run.hex,
        }
        meta = {"name": name, "namespace": self.namespace, "labels": labels}
        await self.ensure_isolation_policy(run)
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
            self.check_slot(current, run)
            self.check_frame(current, run, frame)
            return False, current
        response.raise_for_status()
        return True, response.json()

    @staticmethod
    def check_slot(job, run):
        if job and job["metadata"]["annotations"].get("sunmoonai.com/call") != str(run):
            raise HTTPException(
                409, {"code": "slot_occupied_before_creation", "run_id": str(run)}
            )

    @staticmethod
    def check_frame(job, run, frame):
        annotations = (job or {}).get("metadata", {}).get("annotations", {})
        if (
            annotations.get("sunmoonai.com/call") != str(run)
            or annotations.get("sunmoonai.com/input") != frame.sha256
            or annotations.get("sunmoonai.com/bytes") != str(frame.size)
        ):
            raise HTTPException(409, "Script slot or approved input changed")

    async def owned_pod(self, job):
        uid = job["metadata"]["uid"]
        pods = await self.kube.list("pods", f"batch.kubernetes.io/controller-uid={uid}")
        if len(pods) != 1:
            return None
        pod = pods[0]
        if not any(
            ref.get("controller") is True
            and ref.get("uid") == uid
            and ref.get("kind") == "Job"
            for ref in pod["metadata"].get("ownerReferences", [])
        ):
            return None
        return pod

    async def stop_metered(self, owner, run):
        """Keep the terminal Pod available for metering before its normal cleanup."""
        job = await self.kube.get("jobs", job_name(owner))
        if not job or job["metadata"].get("annotations", {}).get(
            "sunmoonai.com/call"
        ) != str(run):
            raise HTTPException(404, "Execution is unavailable")
        pod = await self.owned_pod(job)
        if not pod:
            raise HTTPException(409, "The controller has not exposed its Pod")

        def stopping_or_done(current):
            return current.get("spec", {}).get(
                "activeDeadlineSeconds"
            ) == 1 or current.get("status", {}).get("phase") in ("Succeeded", "Failed")

        if not stopping_or_done(pod):
            # Kubernetes permits shortening an active Pod deadline. The UID
            # guard excludes a replacement, and its terminal status remains readable.
            response = await self.kube.client.patch(
                self.kube.path("pods", pod["metadata"]["name"]),
                headers={"Content-Type": "application/json-patch+json"},
                json=[
                    {
                        "op": "test",
                        "path": "/metadata/uid",
                        "value": pod["metadata"]["uid"],
                    },
                    {"op": "add", "path": "/spec/activeDeadlineSeconds", "value": 1},
                ],
            )
            if response.status_code in (409, 422):
                current = await self.owned_pod(job)
                if (
                    current
                    and current["metadata"]["uid"] == pod["metadata"]["uid"]
                    and stopping_or_done(current)
                ):
                    return
            response.raise_for_status()

    async def container_meter(self, owner, run):
        job = await self.kube.get("jobs", job_name(owner))
        if not job or job["metadata"].get("annotations", {}).get(
            "sunmoonai.com/call"
        ) != str(run):
            raise HTTPException(404, "No container meter for this execution")
        pod = await self.owned_pod(job)
        if pod:
            for container in pod.get("status", {}).get("containerStatuses", []):
                if (
                    container.get("name") != "script"
                    or container.get("restartCount") != 0
                ):
                    continue
                state = container.get("state", {})
                interval = state.get("terminated") or state.get("running") or {}
                if container.get("containerID") and interval.get("startedAt"):
                    return ScriptContainerMeter(
                        run_id=run,
                        job_uid=job["metadata"]["uid"],
                        pod_uid=pod["metadata"]["uid"],
                        container_id=container["containerID"],
                        started_at=interval["startedAt"],
                        finished_at=interval.get("finishedAt"),
                    )
            status = pod.get("status", {})
            containers = status.get("containerStatuses", [])
            if status.get("phase") == "Failed" and not any(
                c.get("containerID")
                or c.get("restartCount")
                or c.get("lastState")
                or c.get("state", {}).get("running")
                or c.get("state", {}).get("terminated")
                for c in containers
            ):
                reason = None
                if "spec" in pod and not pod["spec"].get("nodeName"):
                    reason = "unscheduled"
                elif len(containers) == 1 and containers[0].get("name") == "script":
                    reason = (
                        containers[0].get("state", {}).get("waiting", {}).get("reason")
                    )
                if reason in (
                    "unscheduled",
                    "ErrImagePull",
                    "ImagePullBackOff",
                    "CreateContainerConfigError",
                ):
                    return ScriptNotStarted(
                        run_id=run,
                        job_uid=job["metadata"]["uid"],
                        pod_uid=pod["metadata"]["uid"],
                        reason=reason,
                    )
        raise HTTPException(409, "No authoritative container interval is available")

    async def waiting_pod(self, job):
        pod = await self.owned_pod(job)
        if pod is None or pod["metadata"].get("deletionTimestamp"):
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
            pod = await self.owned_pod(job)
            if pod is None:
                return ScriptStatus(
                    state="failed", error="Cannot identify a unique script result"
                )
            path = self.kube.path("pods", pod["metadata"]["name"]) + "/log"
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
