"""One bounded script Job per account. The application's call ledger owns receipts."""

from __future__ import annotations

import asyncio
import base64
import hashlib
from uuid import UUID

from fastapi import HTTPException
from script_contract import ScriptExecution, ScriptResult, ScriptStatus


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
        name = job_name(owner)
        raw = body.model_dump_json().encode()
        checksum = hashlib.sha256(raw).hexdigest()
        existing = await self.kube.get("jobs", name)
        if existing:
            annotations = existing["metadata"].get("annotations", {})
            if (
                annotations.get("sunmoonai.com/call") != str(run)
                or annotations.get("sunmoonai.com/input") != checksum
            ):
                raise HTTPException(
                    409, "Another script occupies this account's execution slot"
                )
            return await self.status(owner, run)
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
        chunks = [raw[i : i + 400000] for i in range(0, len(raw), 400000)]
        job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                **meta,
                "annotations": {
                    "sunmoonai.com/call": str(run),
                    "sunmoonai.com/input": checksum,
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
                                ],
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
                                    {
                                        "name": "input",
                                        "mountPath": "/input",
                                        "readOnly": True,
                                    },
                                    {"name": "work", "mountPath": "/tmp"},
                                ],
                            }
                        ],
                        "volumes": [
                            {
                                "name": "work",
                                "emptyDir": {"medium": "Memory", "sizeLimit": "32Mi"},
                            },
                            {
                                "name": "input",
                                "projected": {
                                    "defaultMode": 0o440,
                                    "sources": [
                                        {
                                            "secret": {
                                                "name": f"{name}-{i}",
                                                "items": [
                                                    {
                                                        "key": "input",
                                                        "path": f"chunk-{i:03d}",
                                                    }
                                                ],
                                            }
                                        }
                                        for i in range(len(chunks))
                                    ],
                                },
                            },
                        ],
                    },
                },
            },
        }
        # Create only. Concurrent requests never replace a Job or change its input.
        response = await self.kube.client.post(self.kube.path("jobs"), json=job)
        if response.status_code == 409:
            raise HTTPException(409, "Script execution slot is occupied")
        response.raise_for_status()
        created = response.json()
        reference = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "name": name,
            "uid": created["metadata"]["uid"],
            "controller": True,
            "blockOwnerDeletion": True,
        }
        try:
            for i, chunk in enumerate(chunks):
                await self.kube.apply(
                    "secrets",
                    {
                        "apiVersion": "v1",
                        "kind": "Secret",
                        "type": "Opaque",
                        "immutable": True,
                        "metadata": {
                            **meta,
                            "name": f"{name}-{i}",
                            "ownerReferences": [reference],
                        },
                        "data": {"input": base64.b64encode(chunk).decode()},
                    },
                )
        except Exception:
            # All projected Secrets are required: no container can start with a
            # partial package. If this process dies, the Job deadline still runs.
            await self.kube.delete("jobs", name, uid=created["metadata"]["uid"])
            raise
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
                result = ScriptResult.model_validate_json(response.content)
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
