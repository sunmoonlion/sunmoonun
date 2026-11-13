"""Execute one package in a dedicated secretless container, never in Codex's pod.

The provisioner supplies validated files; Kubernetes owns isolation, deadline,
resources and network policy. This program is not itself a security sandbox.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import selectors
import signal
import stat
import subprocess
import time
from pathlib import Path

INTERPRETERS = {
    ".py": "/usr/bin/python3",
    ".sh": "/bin/bash",
    ".js": "/usr/local/bin/node",
    ".mjs": "/usr/local/bin/node",
    ".cjs": "/usr/local/bin/node",
}
OUTPUT_LIMIT = 65536


def execute(body: dict, work: Path, *, timeout: float = 30) -> dict:
    work.mkdir(parents=True, exist_ok=False)
    for file in body["files"]:
        relative = file["path"]
        if any(p in ("", ".", "..") for p in relative.split("/")) or "\\" in relative:
            raise ValueError("Invalid package path")
        target = work / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = base64.b64decode(file["data_base64"], validate=True)
        if hashlib.sha256(raw).hexdigest() != file["sha256"]:
            raise ValueError("Package digest mismatch")
        target.write_bytes(raw)
    script = work / body["path"]
    if not script.is_file() or not script.resolve().is_relative_to(work.resolve()):
        raise ValueError("Script is not in the installed package")
    outputs = work / "outputs"
    outputs.mkdir(exist_ok=True)
    # A regular file avoids deadlock when the script does not consume stdin.
    stdin_path = work.parent / "stdin"
    stdin_path.write_text(body["stdin"], encoding="utf-8")
    env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(work),
        "TMPDIR": "/tmp",
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "SUNMOON_OUTPUT_DIR": str(outputs),
    }
    with stdin_path.open("rb") as stdin:
        process = subprocess.Popen(
            [INTERPRETERS[script.suffix], str(script), *body["args"]],
            cwd=work,
            env=env,
            stdin=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    expired, truncated = False, False
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        deadline = time.monotonic() + timeout
        try:
            while selector.get_map():
                if time.monotonic() >= deadline:
                    expired = True
                    break
                for key, _ in selector.select(
                    timeout=min(0.1, max(0, deadline - time.monotonic()))
                ):
                    data = os.read(key.fileobj.fileno(), 8192)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    dest = captured[key.data]
                    room = max(0, OUTPUT_LIMIT - len(dest))
                    dest.extend(data[:room])
                    truncated = truncated or len(data) > room
            if not expired:
                try:
                    process.wait(timeout=max(0.001, deadline - time.monotonic()))
                except subprocess.TimeoutExpired:
                    expired = True
        finally:
            # Descendants must not outlive their call, even after a successful parent.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            process.stdout.close()
            process.stderr.close()
    result = {
        "exit_code": process.returncode,
        "timed_out": expired,
        "output_truncated": truncated,
        **{k: bytes(v).decode("utf-8", errors="replace") for k, v in captured.items()},
        "artifacts": [],
        "artifact_error": None,
    }
    size, visited = 0, 0
    if outputs.is_symlink() or not outputs.is_dir():
        result["artifact_error"] = "Output directory was replaced"
        return result
    # Never follow package-produced links or open devices/FIFOs as artifacts.
    for directory, dirs, files in os.walk(outputs, followlinks=False):
        visited += 1
        if visited > 256:
            result["artifact_error"] = "Too many output entries"
            return result
        dirs[:] = [d for d in dirs if not (Path(directory) / d).is_symlink()]
        for name in sorted(files):
            visited += 1
            path = Path(directory) / name
            if visited > 256:
                result["artifact_error"] = "Too many output files"
                return result
            if path.is_symlink() or not path.is_file():
                result["artifact_error"] = (
                    "Links and special output files are not returned"
                )
                continue
            length = path.stat().st_size
            if (
                length > 512 * 1024
                or size + length > 512 * 1024
                or len(result["artifacts"]) >= 32
            ):
                result["artifact_error"] = (
                    "Outputs exceed 32 files or 512 KiB; return smaller artifacts"
                )
                continue
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                with os.fdopen(fd, "rb") as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        continue
                    data = stream.read(512 * 1024 + 1)
            except OSError:
                result["artifact_error"] = "An output could not be read"
                continue
            if size + len(data) > 512 * 1024:
                result["artifact_error"] = "Output size changed during collection"
                continue
            size += len(data)
            result["artifacts"].append(
                {
                    "path": str(path.relative_to(outputs)),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "data_base64": base64.b64encode(data).decode(),
                }
            )
    return result


def main() -> None:
    # Projected Secret volumes split the bounded request into chunks. No credentials.
    raw = b"".join(p.read_bytes() for p in sorted(Path("/input").glob("chunk-*")))
    body = json.loads(raw)
    print(
        json.dumps(execute(body, Path("/tmp/run/package")), ensure_ascii=True),
        flush=True,
    )


if __name__ == "__main__":
    main()
