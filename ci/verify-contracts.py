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


def check_images(commit=None):
    manifest_path = APPLICATIONS / "component-images.yaml"
    manifest = yaml.safe_load(
        git(PLATFORM, "show", commit + ":" + str(manifest_path.relative_to(PLATFORM)))
        if commit
        else manifest_path.read_bytes()
    )
    head = commit or "HEAD"
    for name, image in manifest["images"].items():
        revision = image.get("revision", manifest["revision"])
        context = image["context"]
        git(PLATFORM, "merge-base", "--is-ancestor", revision, head)
        paths = git(PLATFORM, "diff", "--name-only", revision, head, "--", context)
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
    public_sources = {
        "formal_method.py",
        "formal_method_compiler.py",
        "formal_method_plan.py",
        "formal_method_admission.py",
        "formal_method_execution.py",
    }
    generated_files = {
        name: name.removesuffix(".py") + "_generated.py" for name in public_sources
    }
    # Selection is a backend-to-backend contract, introduced after the five
    # public editor contracts. Old pinned releases have no generated selector.
    backend = repos / "knowbench-app/knowbench-backend"
    selector = "app/app/domain/workbench/incubation_selection.py"
    has_selector = (
        bool(
            git(
                backend,
                "ls-tree",
                "--name-only",
                pins["knowbench"]["backend_revision"],
                "--",
                selector,
            )
        )
        if pinned
        else (backend / selector).is_file()
    )
    if has_selector:
        generated_files["selection.py"] = "incubation_selection.py"
    sources = lock["source_sha256"]
    if set(sources) != set(generated_files) or set(lock["generated_sha256"]) != set(
        generated_files.values()
    ):
        raise SystemExit(
            "KnowBench formal method contract inventory differs from its runtime"
        )
    if web["source_sha256"] != {name: sources[name] for name in public_sources}:
        raise SystemExit(
            "KnowBench and the author editor consume different formal method contracts"
        )
    for name, generated in generated_files.items():
        verify("knowlab", "backend", "app/domain/knowbots/" + name, sources[name])
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

    public_dir = "contracts/formal-method/v1/"
    provider = repos / "knowlab-app"

    def published(name):
        if pinned:
            return git(
                provider,
                "show",
                pins["knowlab"]["parent_revision"] + ":" + public_dir + name,
            )
        return (provider / public_dir / name).read_bytes()

    expected_schemas = {
        name + ".schema.json": checksum
        for name, checksum in {
            "definition": lock["schema_sha256"],
            **lock["validation_schema_sha256"],
        }.items()
    }
    manifest = json.loads(published("contract-manifest.json"))
    if manifest != {
        "contract": "formal-method",
        "major_version": 1,
        "schemas": expected_schemas,
    }:
        raise SystemExit(
            "Published KnowLab manifest differs from consumer contract locks"
        )
    for name, checksum in expected_schemas.items():
        if hashlib.sha256(published(name)).hexdigest() != checksum:
            raise SystemExit("Published KnowLab schema drift: " + name)

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
    parser.add_argument(
        "--image-commit",
        help="validate the image manifest and inputs at this exact commit",
    )
    args = parser.parse_args()
    check_images(args.image_commit)
    if not args.images_only:
        contracts(args.repos, args.pinned)
