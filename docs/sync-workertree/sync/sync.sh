#!/usr/bin/env bash
# 就地执行：脚本所在 sunmoonun 的父目录就是当前工位。
set -euo pipefail
case "${1:-}" in
  -h|--help|help|'')
    cat <<'EOF'
用法：./sync.sh <pull|push|status>
  pull    并行抓取，全部检查后快进；子仓跟随父仓指针
  push    只推已提交内容，子仓先于父仓；不自动提交
  status  只看当前工位，不联网
从工位目录执行：./sunmoonun/docs/sync-workertree/sync/sync.sh pull
自动使用脚本所在工位，无需家目录安装、WS、工位名单或 SSH 开发机配置。
默认分支与工位目录同名；特殊布局可显式设置 BRANCH。SYNC_JOBS 默认 4。
EOF
    exit 0 ;;
esac
[[ $# == 1 ]] || { echo '只需一个动作；工位由脚本位置确定，不接受另一个工位名称' >&2; exit 2; }
action="$1"
case "$action" in
  pull|push|status) ;;
  *) echo '仅支持 pull / push / status' >&2; exit 2 ;;
esac
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo="$(git -C "$script_dir" rev-parse --show-toplevel)"
[[ "$script_dir" == "$repo/docs/sync-workertree/sync" ]] || {
  echo '请使用 sunmoonun 仓库内的正式入口，不能复制到家目录运行' >&2; exit 2;
}
root="$(dirname -- "$repo")"
ws="$(basename -- "$root")"
source "$script_dir/config.sh"
export WS="$ws" ROOT_REPO="$(basename -- "$repo")" GIT_REMOTE
exec python3 "$script_dir/workstation_sync.py" "$action" --root "$root" --branch "${BRANCH:-$ws}" --repos "${REPOS[@]}"
