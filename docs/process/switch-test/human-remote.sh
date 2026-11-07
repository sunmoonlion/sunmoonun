#!/usr/bin/env bash
# 兼容原入口：只推当前机器已提交的内容；对方自己拉取。
set -euo pipefail
exec python3 "$(dirname -- "${BASH_SOURCE[0]}")/workstation_sync.py" push "$@"
