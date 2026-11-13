"""Bounded in-cluster acceptance through the provisioner's public execution API.

Creates only a random synthetic account's Job and deletes it on exit. No model,
user workspace, model key or third-party service is used.
"""

import base64
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
import uuid


def main():
    owner, run = uuid.uuid4(), uuid.uuid4()
    url = f"http://127.0.0.1:8080/v1/script-executions/{owner}/{run}"
    token = os.environ["PROVISIONER_TOKEN"]

    def request(method, body=None, *, authenticated=True):
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"}
        if authenticated:
            headers["Authorization"] = "Bearer " + token
        req = urllib.request.Request(url, method=method, headers=headers, data=data)
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)

    code = """import os, socket, subprocess, sys
from pathlib import Path
assert not Path('/data/codex/auth.json').exists()
assert not Path('/secrets/app-server/token').exists()
assert not Path('/var/run/secrets/kubernetes.io/serviceaccount/token').exists()
assert not any(k in os.environ for k in ('OPENAI_API_KEY', 'WORKBENCH_MCP_TOKEN', 'RELAY_TOKEN', 'PROVISIONER_TOKEN'))
try:
    connection=socket.create_connection((sys.argv[1],443),timeout=2)
except (TimeoutError, PermissionError):
    pass
else:
    connection.close()
    raise AssertionError('Cluster network access was not denied')
assert Path('references/value.txt').read_text()=='21'
assert subprocess.check_output(['bash','scripts/calculate.sh'],text=True).strip()=='42'
assert subprocess.check_output(['node','scripts/calculate.js'],text=True).strip()=='42'
Path('outputs/answer.txt').write_text('42')
print('PACKAGE_EXECUTION_AND_NETWORK_ISOLATION_OK')
"""
    files = {
        "SKILL.md": "Run scripts/main.py.",
        "scripts/main.py": code,
        "scripts/calculate.sh": "read n < references/value.txt\necho $((n*2))\n",
        "scripts/calculate.js": "console.log(Number(require('fs').readFileSync('references/value.txt','utf8'))*2)",
        "references/value.txt": "21",
    }
    body = {
        "path": "scripts/main.py",
        "args": [os.environ["KUBERNETES_SERVICE_HOST"]],
        "stdin": "",
        "files": [
            {
                "path": path,
                "data_base64": base64.b64encode(value.encode()).decode(),
                "sha256": hashlib.sha256(value.encode()).hexdigest(),
            }
            for path, value in files.items()
        ],
    }
    try:
        try:
            request("PUT", body, authenticated=False)
        except urllib.error.HTTPError as error:
            assert error.code == 401
        else:
            raise AssertionError("Anonymous execution was allowed")
        request("PUT", body)
        deadline = time.monotonic() + 110
        while time.monotonic() < deadline:
            receipt = request("GET")
            if receipt["state"] != "running":
                break
            time.sleep(1)
        assert receipt["state"] == "finished", receipt["state"]
        result = receipt["result"]
        assert result["exit_code"] == 0 and not result["timed_out"], (
            "Script isolation probe failed"
        )
        assert result["stdout"].strip() == "PACKAGE_EXECUTION_AND_NETWORK_ISOLATION_OK"
        assert len(result["artifacts"]) == 1
        assert base64.b64decode(result["artifacts"][0]["data_base64"]) == b"42"
        print(
            json.dumps(
                {
                    "passed": True,
                    "script_package": True,
                    "python_shell_node": True,
                    "credential_free": True,
                    "cluster_network_denied": True,
                    "artifact_return": True,
                }
            )
        )
    finally:
        request("DELETE")


if __name__ == "__main__":
    main()
