#!/usr/bin/env bash
# mb — 多仓批量 git 操作器
#
#   mb [仓名]                        状态一览（只读）：当前分支 + worktree
#   mb checkout <分支> [仓名|--all]      把主目录切到指定分支
#                                    （不存在则从 master 新建；被 worktree 占用或
#                                    有未提交改动的仓会跳过并报原因）
#   mb worktree add [--from-master] <名字> [仓名|--all]
#                                    挂出 ~/worktrees/<名字>/<仓>
#                                    --from-master：已有工位拨回 master；已收目录
#                                    但分支还在时，先把分支拨回 master 再挂出
#   mb worktree add --all --all            挂出 layout.conf 里全部具名工位 × 全部仓
#   mb worktree remove [--delete-branch [--force]] <名字> [仓名|--all]
#                                    移除整套 worktree（有未提交改动则拒绝）
#                                    --delete-branch：连同名分支一起删（未并入
#                                    master 时拒绝，除非再加 --force）
#   mb worktree remove --all --all         移除 layout.conf 里全部具名工位
#   mb repo list                       列出注册仓
#   mb repo add <路径>                 注册一个仓（必须是 git 仓）
#   mb repo remove <仓名|路径>         取消注册
#
# 作用域：省略或 --all = 全部注册仓；给仓名 = 只操作那一仓。
# 注册仓清单见脚本同目录的 repos.conf（可用 mb repo 命令维护）。
#
# 分支名/工位名任意。模型与分支是正交的：本工具不做身份假设，
# 「谁写的」由使用者在提交粒度上自行负责（见 README）。

set -euo pipefail

die() { echo "错误：$*" >&2; exit 1; }

SWITCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_FILE="$SWITCH_DIR/repos.conf"
LAYOUT_FILE="$SWITCH_DIR/layout.conf"
[[ -f "$LAYOUT_FILE" ]] || die "找不到 $LAYOUT_FILE"
# shellcheck source=layout.conf
source "$LAYOUT_FILE"
: "${LAYOUT_MASTER:?layout.conf 缺少 LAYOUT_MASTER}"
: "${LAYOUT_WORKTREES:?layout.conf 缺少 LAYOUT_WORKTREES}"
WORKTREE_ROOT="${WORKTREE_ROOT:-$HOME/$LAYOUT_WORKTREES}"

layout_workspace_names() {
  if ! declare -p LAYOUT_WORKSPACES >/dev/null 2>&1 || (( ${#LAYOUT_WORKSPACES[@]} == 0 )); then
    die "layout.conf 缺少 LAYOUT_WORKSPACES，无法对全部工位操作"
  fi
  local n
  for n in "${LAYOUT_WORKSPACES[@]}"; do
    [[ "$n" != master ]] || continue
    printf '%s\n' "$n"
  done
}

errline() { grep -m1 -E 'fatal|error' "$1" || tail -1 "$1"; }

repo_dirty() { [[ -n $(git -C "$1" status --porcelain 2>/dev/null) ]]; }

# repos.conf 允许 $HOME 或 ~，避免本机 /home/zymun 与远端 /home/zym 各写一份
expand_repo_path() {
  local p="$1"
  if [[ "$p" == "~/"* ]]; then
    p="$HOME/${p#~/}"
  elif [[ "$p" == "~" ]]; then
    p="$HOME"
  fi
  p="${p/#\$HOME/$HOME}"
  printf '%s' "$p"
}

load_repos() {
  REPOS=()
  [[ -f "$REPOS_FILE" ]] || die "找不到 $REPOS_FILE（用 mb repo add <路径> 注册）"
  local line
  while IFS= read -r line; do
    line="${line%%#*}"; line="${line//[[:space:]]/}"
    [[ -n "$line" ]] || continue
    REPOS+=("$(expand_repo_path "$line")")
  done < "$REPOS_FILE"
  [[ ${#REPOS[@]} -gt 0 ]] || die "$REPOS_FILE 没有注册任何仓"
}

cmd_repo() {
  local sub="${1:-list}"
  case "$sub" in
    list|ls|"")
      printf '%s\n' "${REPOS[@]}" | sed "s|$HOME|~|" | cat -n
      ;;
    add)
      local p="${2:?用法：mb repo add <路径>}"
      p=$(realpath -m "$p")
      git -C "$p" rev-parse --git-dir >/dev/null 2>&1 || die "$p 不是 git 仓"
      if grep -qxF "$p" "$REPOS_FILE" 2>/dev/null; then
        echo "已注册：$p"
      else
        echo "$p" >> "$REPOS_FILE"
        echo "已注册：$p（当前共 $(grep -c . "$REPOS_FILE") 仓）"
      fi
      ;;
    remove|rm)
      local t="${2:?用法：mb repo remove <仓名|路径>}"
      local matches
      matches=$(awk -v t="$t" 'NF && $0 !~ /^[[:space:]]*#/ {n=$0; sub(".*/","",n); if ($0==t || n==t) print $0}' "$REPOS_FILE")
      local n; n=$(printf '%s' "$matches" | grep -c . || true)
      [[ "$n" == "0" ]] && die "未注册：$t"
      [[ "$n" -gt 1 ]] && die "匹配到多个仓，请用完整路径：\n$matches"
      grep -vxF "$matches" "$REPOS_FILE" > "$REPOS_FILE.tmp" && mv "$REPOS_FILE.tmp" "$REPOS_FILE"
      echo "已取消注册：$matches"
      ;;
    *) die "用法：mb repo list | add <路径> | remove <仓名|路径>" ;;
  esac
}

# 工位名/分支名不能以 - 开头，否则会被 git 当成选项（例如 --all → -a）。
assert_plain_name() {
  local kind="$1" val="${2:-}" usage="$3"
  [[ -n "$val" ]] || die "$usage"
  [[ "$val" != -* ]] || die "${kind}不能是选项：$val
$usage"
}

resolve_repos() {
  case "${1:-}" in
    ""|--all|-all) printf '%s\n' "${REPOS[@]}" ;;
    *)
      local r
      for r in "${REPOS[@]}"; do
        [[ $(basename "$r") == "$1" ]] && { echo "$r"; return 0; }
      done
      die "未注册的仓：$1（已注册：$(for r in "${REPOS[@]}"; do basename "$r"; done | tr '\n' ' ')）"
      ;;
  esac
}

cmd_status() {
  local repo
  local resolved
  resolved=$(resolve_repos "${1:-}") || exit 1
  mapfile -t TARGET <<< "$resolved"
  echo "== 主目录 =="
  for repo in "${TARGET[@]}"; do
    local name; name=$(basename "$repo")
    if [[ ! -d "$repo/.git" ]]; then printf "%-20s %s\n" "$name" "（不是 git 仓）"; continue; fi
    local b d=""
    b=$(git -C "$repo" branch --show-current 2>/dev/null || true)
    [[ -z "$b" ]] && b="(detached)"
    repo_dirty "$repo" && d="（有未提交改动）"
    printf "%-20s %-14s %s\n" "$name" "$b" "$d"
  done
  echo "== worktree =="
  local any=0
  for repo in "${TARGET[@]}"; do
    git -C "$repo" worktree list 2>/dev/null | tail -n +2 | sed "s|^|$(basename "$repo"): |" && any=1
  done
  [[ $any -eq 0 ]] && echo "（无）"
  return 0
}

cmd_checkout() {
  assert_plain_name "分支名" "${1:-}" "用法：mb checkout <分支> [仓名|--all]"
  local target="$1"
  local errfile failed=0
  errfile=$(mktemp)
  local repo
  local resolved
  resolved=$(resolve_repos "${2:-}") || exit 1
  mapfile -t TARGET <<< "$resolved"
  for repo in "${TARGET[@]}"; do
    local name; name=$(basename "$repo")
    [[ ! -d "$repo/.git" ]] && { printf "%-20s %s\n" "$name" "跳过（不是 git 仓）"; continue; }
    local cur; cur=$(git -C "$repo" branch --show-current 2>/dev/null || true)
    [[ "$cur" == "$target" ]] && { printf "%-20s 已在 %s，不动\n" "$name" "$target"; continue; }
    if repo_dirty "$repo"; then printf "%-20s 有未提交改动，跳过\n" "$name"; failed=1; continue; fi
    if git -C "$repo" show-ref --verify --quiet "refs/heads/$target"; then
      if git -C "$repo" checkout -q "$target" 2>"$errfile"; then
        printf "%-20s 已切到 %s\n" "$name" "$target"
      else
        printf "%-20s 失败：%s\n" "$name" "$(errline "$errfile")"; failed=1
      fi
    else
      if git -C "$repo" checkout -q -b "$target" master 2>"$errfile"; then
        printf "%-20s 已从 master 新建并切入 %s\n" "$name" "$target"
      else
        printf "%-20s 失败：%s\n" "$name" "$(errline "$errfile")"; failed=1
      fi
    fi
  done
  rm -f "$errfile"
  [[ $failed -eq 0 ]] && echo "完成。" || echo "有仓未切换（见上）。"
}

# 从参数里抽出 worktree 开关，剩下的位置参数写入 WT_POS。
parse_wt_flags() {
  WT_FROM_MASTER=0
  WT_DELETE_BRANCH=0
  WT_FORCE=0
  WT_POS=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --from-master) WT_FROM_MASTER=1; shift ;;
      --delete-branch) WT_DELETE_BRANCH=1; shift ;;
      --force|-f) WT_FORCE=1; shift ;;
      *) WT_POS+=("$1"); shift ;;
    esac
  done
}

branch_ahead_of_master() {
  git -C "$1" rev-list --count "master..$2" 2>/dev/null || printf '0'
}

wt_add_one() {
  local name="$1"
  local from_master="${3:-0}"
  local errfile
  errfile=$(mktemp)
  local repo
  local resolved
  resolved=$(resolve_repos "${2:-}") || exit 1
  mapfile -t TARGET <<< "$resolved"
  for repo in "${TARGET[@]}"; do
    local base dest ahead home
    base=$(basename "$repo"); dest="$WORKTREE_ROOT/$name/$base"
    [[ ! -d "$repo/.git" ]] && { printf "%-20s %s\n" "$base" "跳过（不是 git 仓）"; continue; }

    if [[ -d "$dest" ]]; then
      if [[ "$from_master" -ne 1 ]]; then
        printf "%-20s 已存在，跳过\n" "$base"
        continue
      fi
      if repo_dirty "$dest"; then
        printf "%-20s 有未提交改动，拒绝拨回 master\n" "$base"
        continue
      fi
      ahead=$(branch_ahead_of_master "$repo" "$name")
      if git -C "$dest" reset --hard master >/dev/null 2>"$errfile"; then
        if [[ "$ahead" != "0" ]]; then
          printf "%-20s 已拨回 master（丢弃相对 master 的 %s 个提交，reflog 可找回）\n" \
            "$base" "$ahead"
        else
          printf "%-20s 已拨回 master\n" "$base"
        fi
      else
        printf "%-20s 失败：%s\n" "$base" "$(errline "$errfile")"
      fi
      continue
    fi

    home=$(git -C "$repo" worktree list --porcelain | awk -v b="refs/heads/$name" '
      /^worktree /{p=$2} /^branch /{if ($2==b) print p}')
    if [[ -n "$home" ]]; then
      printf "%-20s 冲突：分支 %s 已检出在 %s\n" "$base" "$name" "$home"
      continue
    fi
    mkdir -p "$WORKTREE_ROOT/$name"
    if git -C "$repo" show-ref --verify --quiet "refs/heads/$name"; then
      if [[ "$from_master" -eq 1 ]]; then
        ahead=$(branch_ahead_of_master "$repo" "$name")
        if ! git -C "$repo" branch -f "$name" master 2>"$errfile"; then
          printf "%-20s 失败：%s\n" "$base" "$(errline "$errfile")"
          continue
        fi
        if git -C "$repo" worktree add "$dest" "$name" 2>"$errfile"; then
          if [[ "$ahead" != "0" ]]; then
            printf "%-20s 挂出 %s（从 master 重建，丢弃相对 master 的 %s 个提交）\n" \
              "$base" "$dest" "$ahead"
          else
            printf "%-20s 挂出 %s（分支已拨回 master）\n" "$base" "$dest"
          fi
        else
          printf "%-20s 失败：%s\n" "$base" "$(errline "$errfile")"
        fi
      elif git -C "$repo" worktree add "$dest" "$name" 2>"$errfile"; then
        printf "%-20s 挂出 %s\n" "$base" "$dest"
      else
        printf "%-20s 失败：%s\n" "$base" "$(errline "$errfile")"
      fi
    else
      if git -C "$repo" worktree add -b "$name" "$dest" master 2>"$errfile"; then
        printf "%-20s 挂出 %s（从 master 新建分支）\n" "$base" "$dest"
      else
        printf "%-20s 失败：%s\n" "$base" "$(errline "$errfile")"
      fi
    fi
  done
  rm -f "$errfile"
  rmdir "$WORKTREE_ROOT/$name" 2>/dev/null || true   # 全失败时不留空目录
}

# 第一个 --all = 全部工位；第二个必须是 --all（全部仓）或仓名。
require_all_scope() {
  local cmd="$1" scope="${2:-}"
  [[ -n "$scope" ]] || die "用法：mb worktree ${cmd} --all --all
第一个 --all = layout.conf 全部具名工位；第二个 --all = 全部注册仓（也可改成仓名）。"
}

wt_add() {
  parse_wt_flags "$@"
  [[ "$WT_DELETE_BRANCH" -eq 0 ]] || die "mb worktree add 不接受 --delete-branch（收工位时用 remove --delete-branch）"
  [[ "$WT_FORCE" -eq 0 ]] || die "mb worktree add 不接受 --force"
  if ((${#WT_POS[@]})); then
    set -- "${WT_POS[@]}"
  else
    set --
  fi
  local scope="${2:-}"
  case "${1:-}" in
    --all|-all)
      require_all_scope add "$scope"
      local n
      while IFS= read -r n; do
        [[ -n "$n" ]] || continue
        printf '\n== 工位 %s ==\n' "$n"
        wt_add_one "$n" "$scope" "$WT_FROM_MASTER"
      done < <(layout_workspace_names)
      ;;
    *)
      assert_plain_name "工位名" "${1:-}" "用法：mb worktree add [--from-master] <名字> [仓名|--all]
  mb worktree add --from-master --all --all
省略仓名或写 --all 表示全部注册仓；两个 --all 表示全部工位 × 全部仓。"
      wt_add_one "$1" "$scope" "$WT_FROM_MASTER"
      ;;
  esac
}

wt_remove_one() {
  local name="$1"
  local delete_branch="${3:-0}"
  local force="${4:-0}"
  local repo
  local resolved
  resolved=$(resolve_repos "${2:-}") || exit 1
  mapfile -t TARGET <<< "$resolved"
  for repo in "${TARGET[@]}"; do
    local base dest errfile
    base=$(basename "$repo"); dest="$WORKTREE_ROOT/$name/$base"
    if [[ -d "$dest" ]]; then
      if [[ -n $(git -C "$dest" status --porcelain 2>/dev/null) ]]; then
        printf "%-20s 有未提交改动，拒绝移除\n" "$base"
        continue
      fi
      if git -C "$repo" worktree remove "$dest"; then
        printf "%-20s 已移除\n" "$base"
      else
        printf "%-20s 移除 worktree 失败\n" "$base"
        continue
      fi
    elif [[ "$delete_branch" -ne 1 ]]; then
      continue
    fi
    if [[ "$delete_branch" -eq 1 ]] &&
       git -C "$repo" show-ref --verify --quiet "refs/heads/$name"; then
      errfile=$(mktemp)
      if [[ "$force" -eq 1 ]]; then
        if git -C "$repo" branch -D "$name" >/dev/null 2>"$errfile"; then
          printf "%-20s 已删除分支 %s\n" "$base" "$name"
        else
          printf "%-20s 删除分支失败：%s\n" "$base" "$(errline "$errfile")"
        fi
      else
        if git -C "$repo" branch -d "$name" >/dev/null 2>"$errfile"; then
          printf "%-20s 已删除分支 %s\n" "$base" "$name"
        else
          printf "%-20s 分支 %s 未并入 master，保留。要丢掉加 --force\n" \
            "$base" "$name"
        fi
      fi
      rm -f "$errfile"
    fi
  done
  rmdir "$WORKTREE_ROOT/$name" 2>/dev/null || true
}

wt_remove() {
  parse_wt_flags "$@"
  [[ "$WT_FROM_MASTER" -eq 0 ]] || die "mb worktree remove 不接受 --from-master（重新挂出时用 add --from-master）"
  if ((${#WT_POS[@]})); then
    set -- "${WT_POS[@]}"
  else
    set --
  fi
  local scope="${2:-}"
  case "${1:-}" in
    --all|-all)
      require_all_scope remove "$scope"
      local n
      while IFS= read -r n; do
        [[ -n "$n" ]] || continue
        printf '\n== 工位 %s ==\n' "$n"
        wt_remove_one "$n" "$scope" "$WT_DELETE_BRANCH" "$WT_FORCE"
      done < <(layout_workspace_names)
      ;;
    *)
      assert_plain_name "工位名" "${1:-}" "用法：mb worktree remove [--delete-branch [--force]] <名字> [仓名|--all]
  mb worktree remove --delete-branch --all --all"
      wt_remove_one "$1" "$scope" "$WT_DELETE_BRANCH" "$WT_FORCE"
      ;;
  esac
}

usage() { sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'; }

main() {
  load_repos
  case "${1:-}" in
    "")      cmd_status ;;
    checkout) shift; cmd_checkout "$@" ;;
    repo)    shift; cmd_repo "$@" ;;
    worktree|wt)
      shift
      case "${1:-}" in
        add)        shift; wt_add "$@" ;;
        remove|rm)  shift; wt_remove "$@" ;;
        --all|-all)
          # 漏写 add 时：mb worktree --all --all 视为 add
          wt_add "$@" ;;
        *)
          die "用法：mb worktree add [--from-master] --all --all
  或：mb worktree add [--from-master] <名字> [仓名|--all]
  或：mb worktree remove [--delete-branch [--force]] <名字|--all --all>
（刚才缺 add/remove。一次挂齐是：mb worktree add --all --all）" ;;
      esac ;;
    -h|--help) usage ;;
    *)
      # 仓名裸调 = 查该仓状态（mb k8s 等价于 mb 状态只看 k8s）
      if resolve_repos "$1" >/dev/null 2>&1; then cmd_status "$1"
      else die "未知命令或未注册的仓：$1（mb --help 看用法）"; fi ;;
  esac
}

main "$@"
