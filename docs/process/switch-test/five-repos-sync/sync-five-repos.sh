#!/usr/bin/env bash

set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="${FIVE_REPOS_CONFIG:-$SCRIPT_DIR/config.sh}"

if [[ ! -r "$CONFIG_FILE" ]]; then
  printf '错误：配置文件不存在或不可读：%s\n' "$CONFIG_FILE" >&2
  exit 1
fi

# 配置文件由当前用户维护，内容采用 Bash 赋值语法。
# shellcheck source=config.sh
source "$CONFIG_FILE"

: "${REMOTE_HOST:?配置缺少 REMOTE_HOST}"
: "${REMOTE_USER:?配置缺少 REMOTE_USER}"
: "${REMOTE_PORT:?配置缺少 REMOTE_PORT}"
: "${REMOTE_IDENTITY_FILE:?配置缺少 REMOTE_IDENTITY_FILE}"
: "${GIT_REMOTE:?配置缺少 GIT_REMOTE}"
: "${LAYOUT_CONF:?配置缺少 LAYOUT_CONF}"
if [[ ! -r "$LAYOUT_CONF" ]]; then
  printf '错误：布局文件不存在或不可读：%s\n' "$LAYOUT_CONF" >&2
  exit 1
fi
# shellcheck source=../toolboxes/Vlinux/utils/set-up-tools/model-switch/layout.conf
source "$LAYOUT_CONF"
: "${LAYOUT_MASTER:?布局缺少 LAYOUT_MASTER}"
: "${LAYOUT_WORKTREES:?布局缺少 LAYOUT_WORKTREES}"
if ! declare -p LAYOUT_WORKSPACES >/dev/null 2>&1 || (( ${#LAYOUT_WORKSPACES[@]} == 0 )); then
  printf '错误：布局缺少 LAYOUT_WORKSPACES\n' >&2
  exit 1
fi
if ! declare -p BRANCHES >/dev/null 2>&1; then
  declare -A BRANCHES=()
fi
if (( ${#REPOS[@]} == 0 )); then
  printf '错误：配置中的 REPOS 不能为空\n' >&2
  exit 1
fi
if ! declare -p WORKSPACES >/dev/null 2>&1 || (( ${#WORKSPACES[@]} == 0 )); then
  WORKSPACES=("master" "${LAYOUT_WORKSPACES[@]}")
fi

readonly REMOTE_HOST REMOTE_USER REMOTE_PORT REMOTE_IDENTITY_FILE GIT_REMOTE
readonly -a REPOS WORKSPACES

CURRENT_WORKSPACE=""
LOCAL_ROOT=""
REL_ROOT=""
SYNC_BRANCH=""

usage() {
  cat <<'EOF'
用法：
  ~/five-repos-sync/sync-five-repos.sh <命令> <工作区|-all>

示例：
  ~/five-repos-sync/sync-five-repos.sh status luna
  ~/five-repos-sync/sync-five-repos.sh to-remote opus
  ~/five-repos-sync/sync-five-repos.sh from-remote master
  ~/five-repos-sync/sync-five-repos.sh realign-to-remote opus
  ~/five-repos-sync/sync-five-repos.sh realign-from-remote kimi
  ~/five-repos-sync/sync-five-repos.sh status -all
  ~/five-repos-sync/sync-five-repos.sh to-remote-all

命令：
  status       查看本地和远程五仓状态
  to-remote    本地五仓推送，再由远程五仓拉取（本地开发的常用命令）
  from-remote  远程五仓推送，再由本地五仓拉取
  local-push   仅推送本地五仓
  local-pull   仅拉取本地五仓
  remote-push  仅推送远程五仓
  remote-pull  仅拉取远程五仓
  realign-to-remote    本地重建分支为准，强制对齐 Git 远端和远程工作区
  realign-from-remote  远程重建分支为准，强制对齐 Git 远端和本地工作区

注意：脚本只同步已提交的 Git 内容；任一相关工作区不干净或分支不符时会停止。
realign 命令会改写分支历史，只接受单个非 master 工作区，不支持 -all。
EOF

  printf '\n当前配置：\n'
  printf '  配置文件  %s\n' "$CONFIG_FILE"
  printf '  远程地址  %s@%s:%s\n' "$REMOTE_USER" "$REMOTE_HOST" "$REMOTE_PORT"
  printf '  SSH 私钥  %s\n' "$REMOTE_IDENTITY_FILE"
  printf '  Git remote %s\n' "$GIT_REMOTE"
  printf '  布局文件  %s\n' "$LAYOUT_CONF"
  printf '  主目录    $HOME/%s\n' "$LAYOUT_MASTER"
  printf '  工位根    $HOME/%s/<名字>\n' "$LAYOUT_WORKTREES"
  printf '  全部工作区 %s\n' "${WORKSPACES[*]}"
}

log() {
  printf '\n==> %s\n' "$*"
}

select_workspace() {
  local workspace="$1"
  local configured=0
  local name
  for name in "${WORKSPACES[@]}"; do
    if [[ "$name" == "$workspace" ]]; then
      configured=1
      break
    fi
  done
  if [[ "$configured" -ne 1 ]]; then
    printf '错误：未配置工作区 %s\n' "$workspace" >&2
    printf '可用工作区：%s\n' "${WORKSPACES[*]}" >&2
    return 2
  fi

  CURRENT_WORKSPACE="$workspace"
  if [[ "$workspace" == master ]]; then
    REL_ROOT="$LAYOUT_MASTER"
  else
    REL_ROOT="$LAYOUT_WORKTREES/$workspace"
  fi
  LOCAL_ROOT="$HOME/$REL_ROOT"
  if [[ -n "${BRANCHES[$workspace]+configured}" ]]; then
    SYNC_BRANCH="${BRANCHES[$workspace]}"
  else
    SYNC_BRANCH="$workspace"
  fi
}

repo_path() {
  printf '%s/%s' "$LOCAL_ROOT" "$1"
}

assert_local_repo() {
  local repo="$1"
  local path
  path="$(repo_path "$repo")"
  git -C "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    printf '错误：本地仓库不存在或无效：%s\n' "$path" >&2
    return 1
  }
}

assert_local_branch() {
  local repo="$1"
  local path current_branch
  path="$(repo_path "$repo")"
  current_branch="$(git -C "$path" branch --show-current)"
  if [[ "$current_branch" != "$SYNC_BRANCH" ]]; then
    printf '错误：%s 当前分支是 %s，预期为 %s\n' \
      "$path" "${current_branch:-<detached HEAD>}" "$SYNC_BRANCH" >&2
    return 1
  fi
}

assert_local_clean() {
  local repo="$1"
  local path
  path="$(repo_path "$repo")"
  if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
    printf '错误：本地仓库有未提交内容：%s\n' "$path" >&2
    git -C "$path" status --short >&2
    return 1
  fi
}

local_preflight() {
  local role="$1"
  local repo
  log "检查本地五仓（$role）"
  for repo in "${REPOS[@]}"; do
    assert_local_repo "$repo"
    assert_local_branch "$repo"
    assert_local_clean "$repo"
    printf '  OK  %s\n' "$repo"
  done
}

local_status() {
  local repo path
  log "本地状态：$CURRENT_WORKSPACE（$LOCAL_ROOT，分支 $SYNC_BRANCH）"
  for repo in "${REPOS[@]}"; do
    path="$(repo_path "$repo")"
    printf '\n[%s]\n' "$repo"
    if git -C "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      git -C "$path" status --short --branch
    else
      printf '缺少仓库：%s\n' "$path"
    fi
  done
}

push_submodules_first() {
  # 父仓指针指向的子仓提交必须先在 Git 远端，否则对端 submodule update 报 not our ref。
  # 子仓 HEAD 已在远端任一分支上就不推（免得给每个子仓都建一个工位分支）；否则推到同名分支（只许快进）。
  local parent_path="$1" remote_name="$2" branch_name="$3"
  [[ -f "$parent_path/.gitmodules" ]] || return 0
  local sub sub_path
  while IFS= read -r sub; do
    [[ -n "$sub" ]] || continue
    sub_path="$parent_path/$sub"
    git -C "$sub_path" rev-parse --is-inside-work-tree >/dev/null 2>&1 || continue
    git -C "$sub_path" fetch --prune --quiet "$remote_name" || return 1
    if [[ -z "$(git -C "$sub_path" branch -r --contains HEAD 2>/dev/null)" ]]; then
      printf '  子仓 %s：HEAD 不在远端，先推到 %s/%s\n' "$sub" "$remote_name" "$branch_name"
      git -C "$sub_path" push "$remote_name" "HEAD:refs/heads/$branch_name" || return 1
    fi
  done < <(git -C "$parent_path" submodule --quiet foreach 'echo "$sm_path"')
}

local_git_action() {
  local action="$1"
  local repo path
  for repo in "${REPOS[@]}"; do
    path="$(repo_path "$repo")"
    log "本地 $repo：git $action"
    case "$action" in
      push)
        push_submodules_first "$path" "$GIT_REMOTE" "$SYNC_BRANCH"
        git -C "$path" push "$GIT_REMOTE" "$SYNC_BRANCH"
        ;;
      pull)
        git -C "$path" pull --ff-only "$GIT_REMOTE" "$SYNC_BRANCH"
        if [[ -f "$path/.gitmodules" ]]; then
          git -C "$path" submodule sync --recursive
          git -C "$path" submodule update --init --recursive
        fi
        ;;
      *) printf '内部错误：未知 Git 操作 %s\n' "$action" >&2; return 2 ;;
    esac
  done
}

force_push_all_urls_with_lease() {
  local repo_dir="$1"
  local remote_name="$2"
  local branch_name="$3"
  local branch_ref="refs/heads/$branch_name"
  local push_url remote_sha endpoint_index
  local -a push_urls=()

  mapfile -t push_urls < <(
    git -C "$repo_dir" remote get-url --push --all "$remote_name"
  )
  if (( ${#push_urls[@]} == 0 )); then
    printf '错误：%s 的 remote %s 没有 push URL\n' \
      "$repo_dir" "$remote_name" >&2
    return 1
  fi

  endpoint_index=0
  for push_url in "${push_urls[@]}"; do
    ((endpoint_index += 1))
    # 每个 push URL 都可能指向独立托管平台，必须分别取得期望值。
    # 空值表示该端点当前不存在此分支，lease 会要求它仍然不存在。
    remote_sha="$(
      git ls-remote --refs "$push_url" "$branch_ref" |
        awk 'NR == 1 { print $1 }'
    )"
    printf '  推送端点 %d/%d：独立 force-with-lease\n' \
      "$endpoint_index" "${#push_urls[@]}"
    git -C "$repo_dir" push \
      "--force-with-lease=$branch_ref:$remote_sha" \
      "$push_url" "$branch_ref:$branch_ref"
  done
}

local_realign_action() {
  local action="$1"
  local repo path target_ref
  target_ref="refs/remotes/$GIT_REMOTE/$SYNC_BRANCH"
  for repo in "${REPOS[@]}"; do
    path="$(repo_path "$repo")"
    case "$action" in
      force-push)
        log "本地 $repo：force-with-lease 推送 $SYNC_BRANCH"
        git -C "$path" fetch --prune "$GIT_REMOTE"
        force_push_all_urls_with_lease "$path" "$GIT_REMOTE" "$SYNC_BRANCH"
        ;;
      hard-align)
        log "本地 $repo：强制对齐 $GIT_REMOTE/$SYNC_BRANCH"
        git -C "$path" fetch --prune "$GIT_REMOTE"
        git -C "$path" show-ref --verify --quiet "$target_ref" || {
          printf '错误：本地未取得目标引用 %s\n' "$target_ref" >&2
          return 1
        }
        git -C "$path" reset --hard "$GIT_REMOTE/$SYNC_BRANCH"
        if [[ -f "$path/.gitmodules" ]]; then
          git -C "$path" submodule sync --recursive
          git -C "$path" submodule update --init --recursive
        fi
        ;;
      *) printf '内部错误：未知本地对齐操作 %s\n' "$action" >&2; return 2 ;;
    esac
  done
}

remote_action() {
  local action="$1"
  ssh -p "$REMOTE_PORT" -i "$REMOTE_IDENTITY_FILE" \
    "$REMOTE_USER@$REMOTE_HOST" bash -s -- \
    "$REL_ROOT" "$GIT_REMOTE" "$SYNC_BRANCH" "$action" "${REPOS[@]}" <<'REMOTE_SCRIPT'
set -Eeuo pipefail

readonly rel_root_arg="$1"
readonly git_remote_arg="$2"
readonly sync_branch_arg="$3"
readonly action_arg="$4"
shift 4
readonly -a repo_args=("$@")
readonly remote_root_arg="$HOME/$rel_root_arg"

remote_log() {
  printf '\n==> %s\n' "$*"
}

assert_remote_repo() {
  local repo="$1"
  local path="$remote_root_arg/$repo"
  git -C "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    printf '错误：远程仓库不存在或无效：%s\n' "$path" >&2
    return 1
  }
}

assert_remote_branch() {
  local repo="$1"
  local path="$remote_root_arg/$repo"
  local current_branch
  current_branch="$(git -C "$path" branch --show-current)"
  if [[ "$current_branch" != "$sync_branch_arg" ]]; then
    printf '错误：%s 当前分支是 %s，预期为 %s\n' \
      "$path" "${current_branch:-<detached HEAD>}" "$sync_branch_arg" >&2
    return 1
  fi
}

assert_remote_clean() {
  local repo="$1"
  local path="$remote_root_arg/$repo"
  if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
    printf '错误：远程仓库有未提交内容：%s\n' "$path" >&2
    git -C "$path" status --short >&2
    return 1
  fi
}

force_push_all_urls_with_lease() {
  local repo_dir="$1"
  local remote_name="$2"
  local branch_name="$3"
  local branch_ref="refs/heads/$branch_name"
  local push_url remote_sha endpoint_index
  local -a push_urls=()

  mapfile -t push_urls < <(
    git -C "$repo_dir" remote get-url --push --all "$remote_name"
  )
  if (( ${#push_urls[@]} == 0 )); then
    printf '错误：%s 的 remote %s 没有 push URL\n' \
      "$repo_dir" "$remote_name" >&2
    return 1
  fi

  endpoint_index=0
  for push_url in "${push_urls[@]}"; do
    ((endpoint_index += 1))
    remote_sha="$(
      git ls-remote --refs "$push_url" "$branch_ref" |
        awk 'NR == 1 { print $1 }'
    )"
    printf '  推送端点 %d/%d：独立 force-with-lease\n' \
      "$endpoint_index" "${#push_urls[@]}"
    git -C "$repo_dir" push \
      "--force-with-lease=$branch_ref:$remote_sha" \
      "$push_url" "$branch_ref:$branch_ref"
  done
}

push_submodules_first() {
  # 父仓指针指向的子仓提交必须先在 Git 远端，否则对端 submodule update 报 not our ref。
  # 子仓 HEAD 已在远端任一分支上就不推（免得给每个子仓都建一个工位分支）；否则推到同名分支（只许快进）。
  local parent_path="$1" remote_name="$2" branch_name="$3"
  [[ -f "$parent_path/.gitmodules" ]] || return 0
  local sub sub_path
  while IFS= read -r sub; do
    [[ -n "$sub" ]] || continue
    sub_path="$parent_path/$sub"
    git -C "$sub_path" rev-parse --is-inside-work-tree >/dev/null 2>&1 || continue
    git -C "$sub_path" fetch --prune --quiet "$remote_name" || return 1
    if [[ -z "$(git -C "$sub_path" branch -r --contains HEAD 2>/dev/null)" ]]; then
      printf '  子仓 %s：HEAD 不在远端，先推到 %s/%s\n' "$sub" "$remote_name" "$branch_name"
      git -C "$sub_path" push "$remote_name" "HEAD:refs/heads/$branch_name" || return 1
    fi
  done < <(git -C "$parent_path" submodule --quiet foreach 'echo "$sm_path"')
}

case "$action_arg" in
  status)
    remote_log "远程状态：$remote_root_arg（分支 $sync_branch_arg）"
    for repo in "${repo_args[@]}"; do
      path="$remote_root_arg/$repo"
      printf '\n[%s]\n' "$repo"
      if git -C "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        git -C "$path" status --short --branch
      else
        printf '缺少仓库：%s\n' "$path"
      fi
    done
    ;;
  preflight)
    remote_log "检查远程五仓"
    for repo in "${repo_args[@]}"; do
      assert_remote_repo "$repo"
      assert_remote_branch "$repo"
      assert_remote_clean "$repo"
      printf '  OK  %s\n' "$repo"
    done
    ;;
  push|pull|force-push|hard-align)
    for repo in "${repo_args[@]}"; do
      path="$remote_root_arg/$repo"
      remote_log "远程 $repo：git $action_arg"
      case "$action_arg" in
        push)
          push_submodules_first "$path" "$git_remote_arg" "$sync_branch_arg"
          git -C "$path" push "$git_remote_arg" "$sync_branch_arg"
          ;;
        pull)
          git -C "$path" pull --ff-only "$git_remote_arg" "$sync_branch_arg"
          if [[ -f "$path/.gitmodules" ]]; then
            git -C "$path" submodule sync --recursive
            git -C "$path" submodule update --init --recursive
          fi
          ;;
        force-push)
          git -C "$path" fetch --prune "$git_remote_arg"
          force_push_all_urls_with_lease \
            "$path" "$git_remote_arg" "$sync_branch_arg"
          ;;
        hard-align)
          target_ref="refs/remotes/$git_remote_arg/$sync_branch_arg"
          git -C "$path" fetch --prune "$git_remote_arg"
          git -C "$path" show-ref --verify --quiet "$target_ref" || {
            printf '错误：远程工作区未取得目标引用 %s\n' "$target_ref" >&2
            exit 1
          }
          git -C "$path" reset --hard "$git_remote_arg/$sync_branch_arg"
          if [[ -f "$path/.gitmodules" ]]; then
            git -C "$path" submodule sync --recursive
            git -C "$path" submodule update --init --recursive
          fi
          ;;
      esac
    done
    ;;
  *)
    printf '内部错误：未知远程操作 %s\n' "$action_arg" >&2
    exit 2
    ;;
esac
REMOTE_SCRIPT
}

run_single() {
  local command_name="$1"
  case "$command_name" in
    status)
      local_status
      remote_action status
      ;;
    to-remote)
      local_preflight "源端"
      remote_action preflight
      local_git_action push
      remote_action pull
      log "同步完成：本地 -> 远程"
      ;;
    from-remote)
      remote_action preflight
      local_preflight "目标端"
      remote_action push
      local_git_action pull
      log "同步完成：远程 -> 本地"
      ;;
    local-push)
      local_preflight "源端"
      local_git_action push
      ;;
    local-pull)
      local_preflight "目标端"
      local_git_action pull
      ;;
    remote-push)
      remote_action preflight
      remote_action push
      ;;
    remote-pull)
      remote_action preflight
      remote_action pull
      ;;
    realign-to-remote)
      local_preflight "权威源"
      remote_action preflight
      local_realign_action force-push
      remote_action hard-align
      log "强制对齐完成：本地 -> Git 远端 -> 远程工作区"
      ;;
    realign-from-remote)
      remote_action preflight
      local_preflight "目标端"
      remote_action force-push
      local_realign_action hard-align
      log "强制对齐完成：远程 -> Git 远端 -> 本地工作区"
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main() {
  local command_name="${1:-}"
  local workspace_name="${2:-}"
  local workspace

  if (( $# > 2 )); then
    usage >&2
    exit 2
  fi

  case "$command_name" in
    -h|--help|help)
      usage
      return
      ;;
    *-all)
      if [[ -n "$workspace_name" ]]; then
        printf '错误：%s 已包含 -all，不能再指定工作区 %s\n' \
          "$command_name" "$workspace_name" >&2
        exit 2
      fi
      command_name="${command_name%-all}"
      workspace_name="-all"
      ;;
  esac

  case "$command_name" in
    status|to-remote|from-remote|local-push|local-pull|remote-push|remote-pull|realign-to-remote|realign-from-remote) ;;
    "")
      printf '错误：缺少命令。\n' >&2
      usage >&2
      exit 2
      ;;
    *)
      printf '错误：未知命令 %s\n' "$command_name" >&2
      usage >&2
      exit 2
      ;;
  esac

  if [[ -z "$workspace_name" ]]; then
    printf '错误：必须显式指定工作区或 -all；脚本不会根据当前目录猜测。\n' >&2
    printf '可用工作区：%s\n' "${WORKSPACES[*]}" >&2
    printf '例如：%s %s opus\n' "$0" "$command_name" >&2
    if [[ "$command_name" != realign-to-remote &&
          "$command_name" != realign-from-remote ]]; then
      printf '全部：%s %s -all\n' "$0" "$command_name" >&2
    fi
    exit 2
  fi

  if [[ "$command_name" == realign-to-remote ||
        "$command_name" == realign-from-remote ]]; then
    if [[ "$workspace_name" == "-all" || "$workspace_name" == "--all" ||
          "$workspace_name" == "all" ]]; then
      printf '错误：%s 是强制改写操作，不支持 -all。\n' "$command_name" >&2
      exit 2
    fi
    if [[ "$workspace_name" == master ]]; then
      printf '错误：%s 不允许改写 master。\n' "$command_name" >&2
      exit 2
    fi
  fi

  if [[ "$workspace_name" == "-all" || "$workspace_name" == "--all" ||
        "$workspace_name" == "all" ]]; then
    for workspace in "${WORKSPACES[@]}"; do
      log "处理工作区：$workspace"
      select_workspace "$workspace"
      run_single "$command_name"
    done
  else
    select_workspace "$workspace_name"
    run_single "$command_name"
  fi
}

main "$@"
