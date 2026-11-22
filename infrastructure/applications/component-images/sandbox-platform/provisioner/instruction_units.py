"""Dedicated Pods for one instruction execution. Kubernetes UIDs fence lifecycle operations."""

import hashlib
import json
import secrets
from base64 import b64decode, b64encode
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from fastapi import HTTPException
from httpx import HTTPStatusError
from k8s_lifecycle import expire_pod
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class ReviewProvider(BaseModel):
    model_config = ConfigDict(extra="forbid")
    credential_id: UUID
    provider: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    base_url: str = Field(min_length=1, max_length=512)
    key: SecretStr = Field(min_length=1, max_length=512)


class Binding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attempt: UUID
    review_provider: ReviewProvider | None = None
    ticket: SecretStr = Field(min_length=1, max_length=4096)
    model: str = Field(min_length=1, max_length=128)
    turn: str | None = Field(default=None, min_length=1, max_length=128)


def conflict(reason):
    raise HTTPException(409, reason)


def mount(name, path, *, readonly=True):
    return {"name": name, "mountPath": path, "readOnly": readonly}


def projection(name, secret, keys, *, optional=False):
    return {
        "name": name,
        "secret": {
            "secretName": secret,
            "defaultMode": 0o440,
            "optional": optional,
            "items": [{"key": key, "path": key} for key in keys],
        },
    }


class InstructionUnits:
    def __init__(
        self,
        kube,
        *,
        owner,
        task,
        attempt=None,
        namespace,
        app_namespace,
        ingress_namespace,
        image,
        pull_secret,
        origin,
    ):
        self.kube = kube
        self.namespace, self.app_namespace = namespace, app_namespace
        self.image, self.pull_secret, self.origin = image, pull_secret, origin
        self.ingress_namespace = ingress_namespace
        self.owner = owner
        self.attempt = attempt
        identity = owner.bytes + task.bytes + (attempt.bytes if attempt else b"")
        self.name = "instr-" + hashlib.sha256(identity).hexdigest()[:32]
        self.labels = {"sunmoonai.com/owner": owner.hex, "sunmoonai.com/task": task.hex}
        if attempt:
            self.labels["sunmoonai.com/attempt"] = attempt.hex

    def check_attempt(self, attempt):
        if self.attempt and self.attempt != attempt:
            conflict("instruction execution belongs to another attempt")

    async def create(self, kind, body, *, reserve_gateway=False):
        """Create-only. Repeated calls can observe an existing immutable binding."""
        name = body["metadata"]["name"]
        current = await self.kube.get(kind, name)
        if current is None:
            response = await self.kube.client.post(self.kube.path(kind), json=body)
            if response.status_code == 409:
                current = await self.kube.get(kind, name)
            else:
                response.raise_for_status()
                current = response.json()
        meta = (current or {}).get("metadata", {})
        expected = body["metadata"]
        if (
            not meta.get("uid")
            or meta.get("deletionTimestamp")
            or expected.get("ownerReferences", []) != meta.get("ownerReferences", [])
            or any(
                meta.get("labels", {}).get(k) != v
                for k, v in expected.get("labels", {}).items()
                if not (reserve_gateway and k == "sunmoonai.com/unit")
            )
        ):
            conflict("instruction resource binding changed")
        return current

    async def remember(self, kind, obj, key, value):
        """Write one lifecycle fact exactly once even when two hosts observe it."""
        uid, name = obj["metadata"]["uid"], obj["metadata"]["name"]
        for _ in range(3):
            if (
                not obj
                or obj["metadata"]["uid"] != uid
                or obj["metadata"].get("deletionTimestamp")
            ):
                conflict("instruction resource replaced")
            meta = obj["metadata"]
            annotations = meta.setdefault("annotations", {})
            if key in annotations:
                if annotations[key] != value:
                    conflict("instruction lifecycle identity changed")
                return
            annotations[key] = value
            response = await self.kube.client.put(self.kube.path(kind, name), json=obj)
            if response.status_code != 409:
                response.raise_for_status()
                return
            obj = await self.kube.get(kind, name)
        conflict("instruction lifecycle concurrently updated")

    def metadata(self, name, labels, gateway=None):
        meta = {"name": name, "namespace": self.namespace, "labels": labels}
        if gateway:
            meta["ownerReferences"] = [
                {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "name": self.name,
                    "uid": gateway["metadata"]["uid"],
                }
            ]
        return meta

    async def policy(self, name, selector, ingress, egress, *, gateway=None):
        spec = {
            "podSelector": selector,
            "policyTypes": ["Ingress", "Egress"],
            "ingress": ingress,
            "egress": egress,
        }
        meta = self.metadata(name, self.labels if gateway else {}, gateway)
        obj = await self.create(
            "networkpolicies",
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": meta,
                "spec": spec,
            },
        )
        actual = obj["spec"]
        if (
            actual["podSelector"] != selector
            or set(actual["policyTypes"]) != set(spec["policyTypes"])
            or actual.get("ingress", []) != ingress
            or actual.get("egress", []) != egress
        ):
            conflict("instruction network policy changed")

    def pod(self, meta, role, env, volumes, mounts):
        port = 47801 if role == "gateway" else 47800
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": meta,
            "spec": {
                "automountServiceAccountToken": False,
                "enableServiceLinks": False,
                "restartPolicy": "OnFailure" if role == "gateway" else "Never",
                # The gateway must keep replaying its receipt until the ledger settles.
                **({"activeDeadlineSeconds": 900} if role == "worker" else {}),
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
                        "name": role,
                        "image": self.image,
                        "command": [
                            "/usr/bin/tini",
                            "--",
                            "/usr/bin/python3",
                            f"/opt/sandbox/instruction_{role}.py",
                        ],
                        "env": env,
                        "volumeMounts": mounts,
                        "securityContext": {
                            "readOnlyRootFilesystem": True,
                            "allowPrivilegeEscalation": False,
                            "capabilities": {"drop": ["ALL"]},
                        },
                        "resources": {
                            "requests": {"cpu": "50m", "memory": "64Mi"},
                            "limits": {
                                "cpu": "1",
                                "memory": "512Mi",
                                "ephemeral-storage": "64Mi",
                            },
                        },
                        "readinessProbe": {
                            "tcpSocket": {"port": port},
                            "periodSeconds": 2,
                        },
                    }
                ],
                "volumes": volumes,
            },
        }

    async def reservation(self):
        """Observe an in-flight reservation after a lost reply, including a retained proof volume."""
        proof = await self.kube.get("persistentvolumeclaims", self.name + "-proof")
        if proof is None:
            raise HTTPException(404, "instruction reservation absent")
        meta = proof["metadata"]
        if any(meta.get("labels", {}).get(k) != v for k, v in self.labels.items()):
            conflict("instruction receipt storage changed")
        uid = meta.get("annotations", {}).get("sunmoonai.com/gateway-uid")
        pod = await self.kube.get("pods", self.name)
        if pod is not None:
            actual = UUID(pod["metadata"]["uid"])
            if uid and str(actual) != uid:
                conflict("instruction gateway replaced")
            await self.gateway(actual, stopping=True)
            return {"uid": str(actual)}
        if uid:
            return {"uid": uid}
        return {"state": "pvc_only", "proof_uid": meta["uid"]}

    async def reserve(self, proof_uid=None):
        if not self.origin:
            raise HTTPException(503, {"code": "instruction_prepare_disabled"})
        try:
            origin = urlsplit(self.origin)
            port = origin.port
        except ValueError as exc:
            raise HTTPException(
                503, {"code": "instruction_control_origin_invalid"}
            ) from exc
        if (
            origin.scheme != "https"
            or not origin.hostname
            or not origin.hostname.endswith(".svc.cluster.local")
            or port not in (None, 443)
            or origin.username is not None
            or origin.password is not None
            or origin.query
            or origin.fragment
            or origin.path not in ("", "/")
        ):
            raise HTTPException(
                503,
                {"code": "instruction_control_origin_invalid"},
            )
        await self.policy(
            "instruction-deny-all",
            {
                "matchExpressions": [
                    {
                        "key": "app",
                        "operator": "In",
                        "values": ["instruction-gateway", "instruction-worker"],
                    },
                ]
            },
            [],
            [],
        )
        pvc = self.name + "-proof"
        if proof_uid is not None:
            proof = await self.kube.get("persistentvolumeclaims", pvc)
            meta = (proof or {}).get("metadata", {})
            if (
                meta.get("uid") != str(proof_uid)
                or meta.get("deletionTimestamp")
                or any(
                    meta.get("labels", {}).get(k) != v for k, v in self.labels.items()
                )
            ):
                conflict("instruction proof reservation changed")
        else:
            proof = await self.create(
                "persistentvolumeclaims",
                {
                    "apiVersion": "v1",
                    "kind": "PersistentVolumeClaim",
                    "metadata": self.metadata(pvc, self.labels),
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": "16Mi"}},
                    },
                },
            )
        recorded_uid = (
            proof["metadata"].get("annotations", {}).get("sunmoonai.com/gateway-uid")
        )
        if recorded_uid:
            return self.status(await self.gateway(recorded_uid))
        labels = {
            **self.labels,
            "app": "instruction-gateway",
            "sunmoonai.com/unit": uuid4().hex,
        }
        metadata = self.metadata(self.name, labels)
        metadata["ownerReferences"] = [
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "name": pvc,
                "uid": proof["metadata"]["uid"],
            }
        ]
        gateway = await self.create(
            "pods",
            self.pod(
                metadata,
                "gateway",
                [
                    {
                        "name": "POD_UID",
                        "valueFrom": {"fieldRef": {"fieldPath": "metadata.uid"}},
                    },
                    {"name": "INSTRUCTION_CONTROL_ORIGIN", "value": self.origin},
                    {
                        "name": "INSTRUCTION_CONTROL_CA",
                        "value": "/run/control-ca/ca.crt",
                    },
                ],
                [
                    projection(
                        "binding",
                        self.name + "-binding",
                        ["uid", "attempt", "ticket", "turn"],
                    ),
                    projection(
                        "review-provider",
                        self.name + "-binding",
                        ["review-provider.json"],
                        optional=True,
                    ),
                    projection(
                        "provider",
                        "sandbox-u-" + self.owner.hex[:12],
                        ["instruction-provider.json"],
                        optional=True,
                    ),
                    {
                        "name": "control-ca",
                        "configMap": {
                            "name": "instruction-control-ca",
                            "items": [{"key": "ca.crt", "path": "ca.crt"}],
                        },
                    },
                    {"name": "proof", "persistentVolumeClaim": {"claimName": pvc}},
                ],
                [
                    mount("binding", "/run/instruction"),
                    mount("provider", "/run/provider"),
                    mount("review-provider", "/run/review-provider"),
                    mount("proof", "/proof", readonly=False),
                    mount("control-ca", "/run/control-ca"),
                ],
            ),
            reserve_gateway=True,
        )
        await self.remember(
            "persistentvolumeclaims",
            proof,
            "sunmoonai.com/gateway-uid",
            gateway["metadata"]["uid"],
        )
        return self.status(gateway)

    @staticmethod
    def status(pod):
        state = pod.get("status", {})
        return {
            "uid": pod["metadata"]["uid"],
            "phase": state.get("phase", "Pending"),
            "ip": state.get("podIP"),
            "ready": any(
                c["type"] == "Ready" and c["status"] == "True"
                for c in state.get("conditions", [])
            ),
        }

    async def gateway(self, uid, *, stopping=False):
        obj = await self.kube.get("pods", self.name)
        if obj is None:
            raise HTTPException(404, "instruction gateway absent")
        meta = obj["metadata"]
        if (
            meta["uid"] != str(uid)
            or meta.get("deletionTimestamp")
            and not stopping
            or any(meta["labels"].get(k) != v for k, v in self.labels.items())
            or meta["labels"].get("app") != "instruction-gateway"
        ):
            conflict("instruction gateway replaced")
        return obj

    async def allow_peers(self, gateway):
        unit = gateway["metadata"]["labels"]["sunmoonai.com/unit"]

        def peer(role):
            return {
                "podSelector": {
                    "matchLabels": {
                        "app": "instruction-" + role,
                        "sunmoonai.com/unit": unit,
                    }
                }
            }

        worker, gw = peer("worker"), peer("gateway")
        relay_port = [{"protocol": "TCP", "port": 47801}]

        def ns(name):
            return {
                "namespaceSelector": {
                    "matchLabels": {"kubernetes.io/metadata.name": name}
                }
            }

        dns = {
            **ns("kube-system"),
            "podSelector": {"matchLabels": {"k8s-app": "kube-dns"}},
        }
        runner = {
            **ns(self.app_namespace),
            "podSelector": {
                "matchLabels": {"app.kubernetes.io/name": "knowbench-runner"}
            },
        }
        await self.policy(
            self.name + "-gateway",
            gw["podSelector"],
            [{"from": [worker], "ports": relay_port}],
            [
                {
                    "to": [dns],
                    "ports": [{"protocol": p, "port": 53} for p in ("UDP", "TCP")],
                },
                {
                    "to": [
                        {
                            **ns(self.ingress_namespace),
                            "podSelector": {
                                "matchLabels": {"app.kubernetes.io/name": "traefik"}
                            },
                        }
                    ],
                    "ports": [{"protocol": "TCP", "port": 8443}],
                },
                {"ports": [{"protocol": "TCP", "port": 443}]},
            ],
            gateway=gateway,
        )
        await self.policy(
            self.name + "-worker",
            worker["podSelector"],
            [{"from": [runner], "ports": [{"protocol": "TCP", "port": 47800}]}],
            [{"to": [gw], "ports": relay_port}],
            gateway=gateway,
        )

    async def bind(self, uid, body):
        self.check_attempt(body.attempt)
        gateway = await self.gateway(uid)
        if self.stopped(gateway) and not await self.kube.get(
            "secrets", self.name + "-binding"
        ):
            conflict("instruction gateway stopped before activation")
        await self.allow_peers(gateway)
        meta = self.metadata(self.name + "-binding", self.labels, gateway)
        values = {
            "uid": str(uid),
            "attempt": str(body.attempt),
            "model": body.model,
            "ticket": body.ticket.get_secret_value(),
            "turn": body.turn or "",
        }
        if body.review_provider:
            route = body.review_provider
            if (
                route.model != body.model
                or not self.attempt
                or urlsplit(route.base_url).scheme != "https"
            ):
                conflict("review route differs from this per-attempt binding")
            values["review-provider.json"] = json.dumps(
                {
                    **route.model_dump(mode="json", exclude={"key"}),
                    "key": route.key.get_secret_value(),
                },
                sort_keys=True,
            )
        data = {k: b64encode(v.encode()).decode() for k, v in values.items()}
        obj = await self.create(
            "secrets",
            {"apiVersion": "v1", "kind": "Secret", "metadata": meta, "data": data},
        )
        existing = obj["data"]
        if existing.get("review-provider.json") != data.get(
            "review-provider.json"
        ) or any(existing[k] != data[k] for k in ("uid", "attempt", "model")):
            conflict("instruction Attempt or model changed")
        if existing["turn"]:
            if body.turn and existing["turn"] != data["turn"]:
                conflict("instruction turn changed")
            data["turn"] = existing["turn"]
        if data != existing:
            # Compare-and-swap; two hosts must never replace an already observed turn.
            meta["resourceVersion"] = obj["metadata"]["resourceVersion"]
            response = await self.kube.client.put(
                self.kube.path("secrets", meta["name"]),
                json={
                    "apiVersion": "v1",
                    "kind": "Secret",
                    "metadata": meta,
                    "data": data,
                },
            )
            if response.status_code == 409:
                conflict("instruction binding concurrently updated")
            response.raise_for_status()
        return self.status(gateway)

    async def worker(self, uid):
        gateway = await self.gateway(uid)
        if self.stopped(gateway):
            conflict("instruction worker stopped")
        if not self.status(gateway)["ready"]:
            conflict("instruction gateway is not ready")
        binding = await self.kube.get("secrets", self.name + "-binding")
        if (
            not binding
            or binding["data"]["uid"] != b64encode(str(uid).encode()).decode()
        ):
            conflict("instruction gateway is not bound")
        await self.allow_peers(gateway)
        name = self.name + "-worker"
        labels = {
            **self.labels,
            "app": "instruction-worker",
            "sunmoonai.com/unit": gateway["metadata"]["labels"]["sunmoonai.com/unit"],
        }
        token = await self.create(
            "secrets",
            {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": self.metadata(name, self.labels, gateway),
                "immutable": True,
                "data": {
                    "token": b64encode(secrets.token_urlsafe(32).encode()).decode()
                },
            },
        )
        worker_uid = (
            token["metadata"].get("annotations", {}).get("sunmoonai.com/worker-uid")
        )
        if worker_uid:
            obj = await self.kube.get("pods", name)
            if not obj or obj["metadata"]["uid"] != worker_uid:
                conflict("original instruction worker is gone")
        else:
            obj = await self.create(
                "pods",
                self.pod(
                    self.metadata(name, labels, gateway),
                    "worker",
                    [
                        {"name": "CODEX_HOME", "value": "/tmp/codex"},
                        {"name": "GATEWAY_IP", "value": gateway["status"]["podIP"]},
                        {
                            "name": "MODEL",
                            "value": b64decode(binding["data"]["model"]).decode(),
                        },
                    ],
                    [
                        projection("access", name, ["token"]),
                        {"name": "work", "emptyDir": {"sizeLimit": "32Mi"}},
                    ],
                    [
                        mount("access", "/run/worker"),
                        mount("work", "/tmp", readonly=False),
                    ],
                ),
            )
            await self.remember(
                "secrets", token, "sunmoonai.com/worker-uid", obj["metadata"]["uid"]
            )
        # Recheck after create: cancellation may have raced the initial GET.
        if self.stopped(await self.gateway(uid)):
            await self.expire_worker(gateway)
            conflict("instruction worker stopped")
        return {
            **self.status(obj),
            "app_server_token": b64decode(token["data"]["token"]).decode(),
        }

    @staticmethod
    def stopped(gateway):
        return (
            gateway["metadata"]
            .get("annotations", {})
            .get("sunmoonai.com/worker-stopped")
            == "true"
        )

    async def expire_worker(self, gateway):
        pod = await self.kube.get("pods", self.name + "-worker")
        if pod:
            if not any(
                ref.get("uid") == gateway["metadata"]["uid"]
                for ref in pod["metadata"].get("ownerReferences", [])
            ):
                conflict("instruction worker replaced")
            try:
                await expire_pod(self.kube, pod, absent_ok=True)
            except HTTPStatusError as exc:
                if exc.response.status_code in (404, 409, 422):
                    conflict("instruction worker changed during stop")
                raise

    async def stop_worker(self, uid):
        gateway = await self.gateway(uid)
        if not self.stopped(gateway):
            # Merge patch uses UID and resourceVersion preconditions without overwriting other annotations.
            response = await self.kube.client.patch(
                self.kube.path("pods", self.name),
                headers={"Content-Type": "application/merge-patch+json"},
                json={
                    "metadata": {
                        "uid": str(uid),
                        "resourceVersion": gateway["metadata"]["resourceVersion"],
                        "annotations": {"sunmoonai.com/worker-stopped": "true"},
                    }
                },
            )
            if response.status_code in (404, 409, 422):
                conflict("instruction gateway changed during stop")
            response.raise_for_status()
        await self.expire_worker(gateway)
        return {"worker_stopping": True, "gateway_uid": str(uid)}

    async def stop(self, uid, settled_attempt):
        self.check_attempt(settled_attempt)
        gateway = await self.gateway(uid, stopping=True)
        # Only the trusted ledger host may retire an activated gateway once it
        # has reconciled this Attempt. Cancellation alone keeps the gateway alive.
        if not self.stopped(gateway):
            conflict("stop the instruction worker before retiring its gateway")
        binding = await self.kube.get("secrets", self.name + "-binding")
        if binding and (
            not settled_attempt
            or b64decode(binding["data"]["attempt"]).decode() != str(settled_attempt)
        ):
            conflict("settled Attempt required to retire the gateway")
        proof = await self.kube.get("persistentvolumeclaims", self.name + "-proof")
        if not proof or any(
            proof["metadata"].get("labels", {}).get(k) != v
            for k, v in self.labels.items()
        ):
            conflict("instruction receipt storage changed")
        # A lost prepare reply may leave the original Pod created before its UID
        # is recorded on this Task's PVC. Fence it before recording retirement.
        await self.remember(
            "persistentvolumeclaims", proof, "sunmoonai.com/gateway-uid", str(uid)
        )
        await self.remember(
            "persistentvolumeclaims",
            proof,
            "sunmoonai.com/retired-attempt",
            str(settled_attempt) if settled_attempt else "unused",
        )
        await self.kube.delete("pods", self.name, uid=str(uid))
        return {"stopping": True, "retained_proof_claim": self.name + "-proof"}

    async def reclaim(self, uid, settled_attempt):
        self.check_attempt(settled_attempt)
        name = self.name + "-proof"
        proof = await self.kube.get("persistentvolumeclaims", name)
        if not proof:
            return {"removed": False}
        refs = proof["metadata"].get("annotations", {})
        expected = str(settled_attempt) if settled_attempt else "unused"
        if (
            refs.get("sunmoonai.com/gateway-uid") != str(uid)
            or refs.get("sunmoonai.com/retired-attempt") != expected
            or await self.kube.get("pods", self.name)
        ):
            conflict("instruction receipt storage still in use")
        removed = await self.kube.delete(
            "persistentvolumeclaims", name, uid=proof["metadata"]["uid"]
        )
        return {"removed": removed}
