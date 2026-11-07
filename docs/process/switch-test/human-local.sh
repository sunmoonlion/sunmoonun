#!/usr/bin/env bash
# 兼容原入口：在运行本脚本的机器拉取当前工位；不 SSH、不自动提交。
set -euo pipefail
# 旧版完成拉取后会交回这个标志；仅兼容交回，不再重复联网。
if [[ "${1:-}" == --after-sync ]]; then echo "同步完成；下次起使用新版单机同步。"; exit 0; fi
exec python3 "$(dirname -- "${BASH_SOURCE[0]}")/workstation_sync.py" pull "$@"
