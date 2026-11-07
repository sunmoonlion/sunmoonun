# 要对齐的目标工位；目录名就是分支名。基准由命令参数指定。
# 本机不存在的工位会明确跳过，已存在但缺仓的工位会报错。
# master 的业务历史可能独立，默认不纳入；确需对齐时再加入。
ALIGN_WORKSPACES=(cursor fable kimi luna qwen agy)

# 默认采用 sync/config.sh 的仓清单（各父仓包含递归子仓）。
# 可缩小为例如 ALIGN_REPOS=(sunmoonun knowbench-app)。
ALIGN_REPOS=("${REPOS[@]}")
