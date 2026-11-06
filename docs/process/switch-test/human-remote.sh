#!/usr/bin/env bash
# 所有者在本地机上跑的（推）：本地助手说「跑完了」之后，把它写下的结果和其它改动提交，并同步回远程。
# 用法：WS=<工位> bash ~/switch-test/human-remote.sh    （工位必须给，不猜；先推子仓与 sunmoon-link，再通过 origin 推送父仓）
# 工位定目录 ~/worktrees/<工位>；分支默认与工位同名，特殊用途可显式 BRANCH=<分支>
# 推之前每个仓都先 fetch：远端有本地没有的提交（远程助手这期间推的）就停下，不 rebase、不强推（所有者 2026-11-06 定，账 64）。
# 第 1 步就查完，查完才提交和推。停下时：本地没有已提交未推的（只有未提交的改动也算）就先跑 human-local.sh 拉下来再跑本脚本；
# 本地也有已提交未推的（两边分叉）就把输出贴给远程助手。
# 跑完把最后打印的「仓 提交号」告诉远程助手。
set -euo pipefail
if [ -z "${WS:-}" ]; then
  echo "✗ 要指定工位：WS=<fable|cursor|kimi|luna|qwen|agy> bash ~/switch-test/$(basename "$0")   （不猜，和 five-repos-sync 一样）" >&2
  exit 2
fi
WS="$WS"
WORKTREE_ROOT="${WORKTREE_ROOT:-$HOME/worktrees/$WS}"
ROOT_REPO="${ROOT_REPO:-sunmoonun}"
# 2026-11-06：每工位只有一条同名分支；日常同步只经过 Git，不 SSH 到旧开发机。
BRANCH="${BRANCH:-$WS}"
export BRANCH
FIVE="$ROOT_REPO knowfeed-app knowbench-app knowbase-app tpl-app knowlab-app knowmart-app"
# 父仓下的全部子仓（前端也在内：2026-10-08 luna 的网页修复因只列了两个后端而没推上来）
SUBS="knowfeed-app/knowfeed-backend knowfeed-app/knowfeed-web-frontend knowfeed-app/knowfeed-admin-frontend
  knowbench-app/knowbench-backend knowbench-app/knowbench-web-frontend knowbench-app/knowbench-admin-frontend
  knowbase-app/knowbase-backend knowbase-app/knowbase-web-frontend knowbase-app/knowbase-admin-frontend
  tpl-app/tpl-backend tpl-app/tpl-web-frontend tpl-app/tpl-admin-frontend
  knowlab-app/knowlab-backend knowlab-app/knowlab-web-frontend knowlab-app/knowlab-admin-frontend
  knowmart-app/knowmart-backend knowmart-app/knowmart-web-frontend knowmart-app/knowmart-admin-frontend"
OTHERS="$SUBS sunmoon-link"
pushed=()
changed=()

check_repo() { # 仓目录 标签 是否允许 detached HEAD
  local d="$1" tag="$2" allow_detached="${3:-no}" branch
  [ -e "$d/.git" ] || { echo "✗ $tag 不存在：$d"; return 1; }
  branch=$(git -C "$d" branch --show-current) || return 1
  if [ "$branch" != "$BRANCH" ] && { [ -n "$branch" ] || [ "$allow_detached" != yes ]; }; then
    echo "✗ $tag 当前分支 ${branch:-detached HEAD}，预期 $BRANCH"
    return 1
  fi
}

stop_if_behind() { # 仓目录 标签：远端有本地没有的提交就停。不 rebase：改了号，写进回执、卡、文档、Flux 的提交号就对不上（账 64）
  local d="$1" tag="$2"
  git -C "$d" ls-remote --exit-code -q origin "refs/heads/$BRANCH" >/dev/null 2>&1 || return 0   # 远端还没有这个分支（首次推）
  git -C "$d" fetch -q origin "$BRANCH" || { echo "✗ $tag fetch 失败"; return 1; }
  local behind ahead
  behind=$(git -C "$d" rev-list --count "HEAD..origin/$BRANCH" 2>/dev/null || echo 0)
  [ "$behind" = 0 ] && return 0
  ahead=$(git -C "$d" rev-list --count "origin/$BRANCH..HEAD" 2>/dev/null || echo 0)
  if [ "$ahead" = 0 ]; then
    echo "✗ $tag 落后远端 $behind 个提交、本地没有新提交：停止回传。先跑 WS=$WS bash ~/switch-test/human-local.sh 拉下来，再跑本脚本"
  else
    echo "✗ $tag 和远端分叉（远端多 $behind 个、本地多 $ahead 个）：停止回传，没有 rebase。把上面的输出贴给远程助手"
  fi
  return 1
}

commit_if_dirty() { # 仓目录 标签
  local d="$1" tag="$2" status
  status=$(git -C "$d" status --porcelain) || return 1
  if [ -n "$status" ]; then
    echo "--- $tag 有改动："; git -C "$d" status --short || return 1
    git -C "$d" add -A || return 1
    git -C "$d" commit -q -m "test(local): $tag 本地改动" || return 1
    changed+=("$tag $(git -C "$d" rev-parse --short HEAD)")
    echo "    已提交 $(git -C "$d" rev-parse --short HEAD)"
  fi
}

echo "===== 1. 检查本地仓库（工位 $WS，分支 $BRANCH）"
for r in $FIVE sunmoon-link; do check_repo "$WORKTREE_ROOT/$r" "$r" || exit 1; done
for r in $SUBS; do
  check_repo "$WORKTREE_ROOT/$r" "$r" yes || exit 1
done
# 提交、推送之前一次查完：有一个仓落后远端就整次停，不留「子仓推了、父仓停了」的半截
echo "    查远端有没有本地没有的提交（有就停，不 rebase）"
for r in $FIVE sunmoon-link; do stop_if_behind "$WORKTREE_ROOT/$r" "$r" || exit 1; done
for r in $SUBS; do
  d="$WORKTREE_ROOT/$r"
  # 没改动、当前提交已在远端某分支上的子仓不推，也不用查
  if [ -z "$(git -C "$d" status --porcelain)" ] && [ -n "$(git -C "$d" branch -r --contains HEAD 2>/dev/null)" ]; then continue; fi
  stop_if_behind "$d" "$r" || exit 1
done

echo "===== 2. 先提交并推送子仓与 sunmoon-link"
for r in $OTHERS; do
  d="$WORKTREE_ROOT/$r"
  commit_if_dirty "$d" "$r" || { echo "✗ $r 提交失败"; exit 1; }
  # 子仓没有新提交（当前提交已在远端某分支上）就不推，免得给每个子仓都建一个工位分支
  if [ "$r" != sunmoon-link ] && [ -n "$(git -C "$d" branch -r --contains HEAD 2>/dev/null)" ]; then continue; fi
  # 子模块 update 后通常 detached；推当前 HEAD，不能依赖可能不存在或过期的本地分支。
  git -C "$d" push -q origin "HEAD:refs/heads/$BRANCH" || { echo "✗ $r push 失败，停止回传"; exit 1; }
  echo "  已推 $r"; pushed+=("$r")
done

echo "===== 3. 提交并同步父仓（子仓提交已推送）"
for r in $FIVE; do
  commit_if_dirty "$WORKTREE_ROOT/$r" "$r" || { echo "✗ $r 提交失败"; exit 1; }
done
if [ ${#changed[@]} -eq 0 ]; then echo "没有改动要提交（可能本地助手已经自己提交了）。"; fi
for r in $FIVE; do
  git -C "$WORKTREE_ROOT/$r" push -q origin "$BRANCH" || { echo "✗ $r push 失败"; exit 1; }
done

echo "===== 4. 告诉远程助手这一句："
line="本地回来了"
for r in $FIVE sunmoon-link ${pushed[@]+"${pushed[@]}"}; do d="$WORKTREE_ROOT/$r"; line="$line；$r $(git -C "$d" rev-parse --short HEAD)"; done
echo "$line"
