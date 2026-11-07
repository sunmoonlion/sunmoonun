#!/usr/bin/env bash
# 日常单机入口；两端各自在自己的机器运行。实现随工位文档仓更新。
set -euo pipefail
case "${1:-}" in
  -h|--help|help|'')
    cat <<'EOF'
用法：sync-five-repos.sh <pull|push|status> <工位>
  pull    并行抓取，全部检查后快进；子仓跟随父仓指针
  push    只推已提交内容，子仓先于父仓；不自动提交
  status  只看当前机器工作区，不联网
示例：~/five-repos-sync/sync-five-repos.sh pull qwen
两端都这样用：开工 pull，手动提交，收工 push。不会 SSH 操作对方。
SYNC_JOBS=4 控制并行联网数。工位创建/跨机器对齐另行维护，不在日常命令内。
EOF
    exit 0 ;;
esac
[[ $# == 2 ]] || { echo '需要命令与一个工位；日常同步不支持 -all' >&2; exit 2; }
action="$1"; ws="$2"
case "$action" in
  pull|push|status) ;;
  local-pull|from-remote) action=pull ;;
  local-push|to-remote) action=push ;;
  *) echo '仅支持 pull / push / status；跨机与强制对齐请另用维护入口' >&2; exit 2 ;;
esac
config="${FIVE_REPOS_CONFIG:-$HOME/five-repos-sync/config.sh}"
[[ -r "$config" ]] || { echo "配置不存在：$config" >&2; exit 2; }
source "$config"
source "${LAYOUT_CONF:?缺少 LAYOUT_CONF}"
configured=false
for name in master "${LAYOUT_WORKSPACES[@]}"; do [[ "$ws" != "$name" ]] || configured=true; done
[[ "$configured" == true ]] || { echo "未配置工位：$ws" >&2; exit 2; }
if [[ "$ws" == master ]]; then root="$HOME/$LAYOUT_MASTER"; else root="$HOME/$LAYOUT_WORKTREES/$ws"; fi
branch="${BRANCH:-${BRANCHES[$ws]:-$ws}}"
export WS="$ws" GIT_REMOTE="${GIT_REMOTE:-origin}"
engine="$root/${ROOT_REPO:-sunmoonun}/docs/process/switch-test/workstation_sync.py"
[[ -f "$engine" ]] || { echo "当前工位缺少新版同步程序：$engine；请先拉取文档仓" >&2; exit 2; }
exec python3 "$engine" "$action" --root "$root" --branch "$branch" --repos "${REPOS[@]}"
