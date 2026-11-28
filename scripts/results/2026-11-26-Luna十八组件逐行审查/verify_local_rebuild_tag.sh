#!/usr/bin/env bash
# 在仓库组根目录运行。docker 是记录参数的 shell 函数。
set -euo pipefail
build_dir=tpl-app/tpl-web-frontend/mybuild
capture=$(mktemp)
export capture
trap 'rm -f "$capture"' EXIT
docker() { printf '%s\n' "$*" >> "$capture"; }
export -f docker
bash "$build_dir/test-release-tag.sh"
bash "$build_dir/rebuild-and-run.sh" >/dev/null
grep -Fxq 'rmi tpl-web-frontend:1.0.0' "$capture"
grep -Fxq 'build -t tpl-web-frontend:1.0.0 -f mybuild/Dockerfile .' "$capture"
