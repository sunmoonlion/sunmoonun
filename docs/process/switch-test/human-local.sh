#!/usr/bin/env bash
# 兼容原入口：在运行本脚本的机器拉取当前工位；不 SSH、不自动提交。
set -euo pipefail
exec python3 "$(dirname -- "${BASH_SOURCE[0]}")/workstation_sync.py" pull "$@"
