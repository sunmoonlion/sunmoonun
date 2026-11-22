"""Fresh Codex app-server with one Responses route and no platform credentials."""

import json
import os
from ipaddress import ip_address
from pathlib import Path


def configure(home, gateway_ip, model):
    ip = ip_address(gateway_ip)
    host = f"[{ip}]" if ip.version == 6 else str(ip)
    home.mkdir(mode=0o700, exist_ok=True)
    (home / "config.toml").write_text(f"""
model = {json.dumps(model, ensure_ascii=False)}
model_provider = "instruction"
approval_policy = "never"
sandbox_mode = "read-only"
web_search = "disabled"
[agents]
enabled = false
[features]
multi_agent = false
multi_agent_v2 = false
apps = false
goals = false
shell_tool = false
view_image = false
default_mode_request_user_input = false
[model_providers.instruction]
name = "instruction"
base_url = "http://{host}:47801/v1"
wire_api = "responses"
supports_websockets = false
requires_openai_auth = false
request_max_retries = 0
stream_max_retries = 0
""")
    (home / "environments.toml").write_text("include_local = false\n")


if __name__ == "__main__":
    configure(
        Path(os.environ["CODEX_HOME"]), os.environ["GATEWAY_IP"], os.environ["MODEL"]
    )
    os.chdir("/tmp")
    os.execvp(
        "codex",
        [
            "codex",
            "app-server",
            "--listen",
            "ws://0.0.0.0:47800",
            "--ws-auth",
            "capability-token",
            "--ws-token-file",
            "/run/worker/token",
        ],
    )
