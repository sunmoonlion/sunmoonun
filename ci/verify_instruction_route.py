"""Check the staged callback route when the provisioner enables instruction trials."""

from pathlib import Path
from urllib.parse import urlsplit

import yaml

COMPONENTS = Path(__file__).resolve().parents[1] / "gitops/components"


def verify(provisioner, service_access):
    deployment = next(
        obj
        for obj in provisioner
        if obj
        and obj["kind"] == "Deployment"
        and obj["metadata"]["name"] == "sandbox-provisioner"
    )
    container = next(
        item
        for item in deployment["spec"]["template"]["spec"]["containers"]
        if item["name"] == "provisioner"
    )
    env = {item["name"]: item.get("value") for item in container["env"]}
    if not env.get("INSTRUCTION_CONTROL_ORIGIN"):
        return
    host = urlsplit(env["INSTRUCTION_CONTROL_ORIGIN"]).hostname
    for ingress in service_access:
        if (
            not ingress
            or ingress["kind"] != "Ingress"
            or ingress["metadata"]["namespace"] != env["APP_NAMESPACE"]
        ):
            continue
        spec = ingress["spec"]
        if not any(host in entry["hosts"] for entry in spec.get("tls", [])):
            continue
        for rule in spec["rules"]:
            if rule["host"] == host and any(
                path["path"] == "/api/internal/v1/instruction-control"
                and path["pathType"] == "Prefix"
                and path["backend"]["service"]
                == {"name": "knowbench-api", "port": {"name": "http"}}
                for path in rule["http"]["paths"]
            ):
                return
    raise ValueError(
        f"Missing instruction-control route to knowbench-api on {host}. Stage the traefik release target."
    )


if __name__ == "__main__":

    def objects(path):
        yield from yaml.safe_load_all((COMPONENTS / path / "workload.yaml").read_text())

    verify(
        objects("sandbox-platform/provisioner"),
        objects("ingress-platform/traefik/service-access"),
    )
