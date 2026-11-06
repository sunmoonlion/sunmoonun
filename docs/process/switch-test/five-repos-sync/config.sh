# SunMoonAI 多仓同步配置
# 目录布局见 mb 的 layout.conf，不要在这里再写一份根路径。

REMOTE_HOST="43.153.135.74"
REMOTE_USER="zym"
REMOTE_PORT="1022"
REMOTE_IDENTITY_FILE="$HOME/.ssh/id_rsa"
GIT_REMOTE="origin"

# mb 工位布局（LAYOUT_MASTER / LAYOUT_WORKTREES）
LAYOUT_CONF="${LAYOUT_CONF:-$HOME/toolboxes/Vlinux/utils/set-up-tools/model-switch/layout.conf}"

# 工作区列表来自 layout.conf 的 LAYOUT_WORKSPACES（再加 master）。
# 可选：工作区名与 Git 分支不同时再写。默认分支名等于工作区名。
declare -A BRANCHES=()

REPOS=(
  "tpl-app"
  "knowbase-app"
  "sunmoonun"
  "knowfeed-app"
  "knowbench-app"
  "sunmoon-link"
  "knowlab-app"
  "knowmart-app"
)
