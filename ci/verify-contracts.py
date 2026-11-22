"""Check component source pins and the selected release's cross-repository contracts."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import yaml


PLATFORM = Path(__file__).resolve().parents[1]
APPLICATIONS = PLATFORM / "infrastructure/applications"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def check_images():
    manifest = yaml.safe_load((APPLICATIONS / "component-images.yaml").read_text())
    for name, image in manifest["images"].items():
        revision = image.get("revision", manifest["revision"])
        context = image["context"]
        git(PLATFORM, "merge-base", "--is-ancestor", revision, "HEAD")
        paths = git(PLATFORM, "diff", "--name-only", revision, "HEAD", "--", context)
        if paths:
            raise SystemExit(
                f"{name} {revision[:12]} misses committed build inputs:\n{paths.decode()}"
            )


def keys(node, path=()):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from keys(value, (*path, key))
    else:
        yield path


def contracts(repos, pinned):
    pins = yaml.safe_load((APPLICATIONS / "sources.yaml").read_text())["applications"]

    def read(app, component, path):
        suffix = "backend" if component == "backend" else component + "-frontend"
        repo = repos / (app + "-app") / (app + "-" + suffix)
        if pinned:
            return git(
                repo, "show", pins[app][component + "_revision"] + ":app/" + path
            )
        return (repo / "app" / path).read_bytes()

    def verify(app, component, path, expected):
        if hashlib.sha256(read(app, component, path)).hexdigest() != expected:
            raise SystemExit(f"Contract drift in {app}/{component}/{path}")

    lock = json.loads(read("knowbench", "backend", "contracts/formal-method-lock.json"))
    web_dir = "contracts/formal-method-provider/"
    web = json.loads(read("knowlab", "web", web_dir + "lock.json"))
    if len(lock["source_sha256"]) != 5 or lock["source_sha256"] != web["source_sha256"]:
        raise SystemExit(
            "KnowBench and the author editor consume different formal method contracts"
        )
    for name, expected in lock["source_sha256"].items():
        verify("knowlab", "backend", "app/domain/knowbots/" + name, expected)
        generated = name.removesuffix(".py") + "_generated.py"
        verify(
            "knowbench",
            "backend",
            "app/domain/workbench/" + generated,
            lock["generated_sha256"][generated],
        )
    verify(
        "knowbench", "backend", "contracts/formal-method-v1.json", lock["schema_sha256"]
    )
    for name, expected in lock["validation_schema_sha256"].items():
        verify(
            "knowbench", "backend", f"contracts/formal-method-{name}-v1.json", expected
        )
    for name, expected in web["files_sha256"].items():
        verify("knowlab", "web", web_dir + name, expected)

    folder = "component-images/sandbox-platform/provisioner"
    script = (APPLICATIONS / folder / "script_contract.py").read_bytes()
    generated = read(
        "knowbench", "backend", "app/domain/workbench/script_contract_generated.py"
    )
    if generated.partition(b"\n")[2] != script:
        raise SystemExit("KnowBench script contract differs from provisioner")
    script_lock = json.loads(
        read(
            "knowbench",
            "backend",
            "app/domain/workbench/script_contract_generated.lock.json",
        )
    )
    if script_lock["sha256"] != hashlib.sha256(script).hexdigest():
        raise SystemExit("Script contract content lock differs from provisioner")
    for app, target in [
        ("knowbench", "web"),
        ("knowbench", "admin"),
        ("knowlab", "web"),
        ("knowmart", "web"),
    ]:
        langs = [
            set(keys(json.loads(read(app, target, f"messages/{code}.json"))))
            for code in ("en", "zh-CN")
        ]
        if langs[0] != langs[1]:
            raise SystemExit(
                f"Translation keys differ for {app}/{target}: {sorted(langs[0] ^ langs[1])}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos", type=Path, default=PLATFORM.parent)
    parser.add_argument("--pinned", action="store_true")
    parser.add_argument("--images-only", action="store_true")
    args = parser.parse_args()
    check_images()
    if not args.images_only:
        contracts(args.repos, args.pinned)
