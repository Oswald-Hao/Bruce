#!/bin/bash
# 自动推送clawd仓库到GitHub
# 使用方法：./tools/git-push.sh "提交信息"

# 设置变量
REPO_DIR="/home/lejurobot/clawd"
REPO_URL="git@github.com:Oswald-Hao/Bruce.git"
COMMIT_MSG="${1:-自动更新：$(date '+%Y-%m-%d %H:%M')}"

# 进入仓库目录
cd "$REPO_DIR" || exit 1

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
    echo "没有需要提交的更改"
    exit 0
fi

# 添加所有更改
git add .

# 提交更改
git commit -m "$COMMIT_MSG"

# 推送到GitHub
git push origin master

echo "✅ 推送完成：$COMMIT_MSG"
