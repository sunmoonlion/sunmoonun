#!/usr/bin/env bash
set -euo pipefail
case "${1:-}" in
  -h|--help|help|'')
    cat <<'HELP'
用法：./align.sh <基准工位> [--check]
示例：./align.sh qwen --check  # 检查并展示计划，不移动分支
      ./align.sh qwen          # 全部检查通过后，快进配置中的本机工位
目标工位和仓范围在同目录 config.sh；保留目标分支名。
不联网、不提交、不推送、不强制重置；分叉或未提交改动时停止。
HELP
    exit 0 ;;
esac
[[ $# == 1 || ( $# == 2 && "$2" == --check ) ]] || {
  echo '需要基准工位，可选 --check' >&2; exit 2;
}
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo="$(git -C "$script_dir" rev-parse --show-toplevel)"
[[ "$script_dir" == "$repo/docs/sync-cowork/align" ]] || {
  echo '请使用仓内 align 入口' >&2; exit 2;
}
workspace="$(dirname -- "$repo")"
if [[ "$(basename -- "$workspace")" == master ]]; then
  base_home="$(dirname -- "$workspace")"
else
  [[ "$(basename -- "$(dirname -- "$workspace")")" == worktrees ]] || {
    echo '工位必须位于 master 或 worktrees/<工位>' >&2; exit 2;
  }
  base_home="$(dirname -- "$(dirname -- "$workspace")")"
fi
source "$script_dir/../sync/config.sh"
source "$script_dir/config.sh"
exec python3 "$script_dir/workstation_align.py" "$1" "${@:2}" \
  --home "$base_home" --workspaces "${ALIGN_WORKSPACES[@]}" --repos "${ALIGN_REPOS[@]}"
