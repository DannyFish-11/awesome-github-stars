#!/bin/bash

# ========================================
# GitHub 高 Star 项目每日自动收集脚本
# ========================================

set -e

# 配置变量
REPO_DIR="/home/ubuntu/awesome-github-stars"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$REPO_DIR/logs"
DATE=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
MONTH=$(date +%m-%B)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 创建日志目录
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/collect_${DATE}.log"

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "开始执行每日项目收集任务"
log "========================================="

# 切换到仓库目录
cd "$REPO_DIR"

# 拉取最新代码（如果远程仓库已配置）
if git remote | grep -q origin; then
    log "拉取远程仓库最新代码..."
    git pull origin main 2>&1 | tee -a "$LOG_FILE" || log "警告: 拉取失败，继续执行"
fi

# 执行 Python 收集脚本
log "执行项目收集脚本..."
python3 "$SCRIPT_DIR/collect_projects.py" 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    log "错误: 项目收集失败"
    exit 1
fi

# 检查是否有新文件生成
PROJECT_FILE="$REPO_DIR/$YEAR/$MONTH/$DATE.md"
if [ ! -f "$PROJECT_FILE" ]; then
    log "错误: 项目文件未生成 - $PROJECT_FILE"
    exit 1
fi

log "项目文件已生成: $PROJECT_FILE"

# 更新月度索引
log "更新月度索引..."
python3 "$SCRIPT_DIR/update_index.py" 2>&1 | tee -a "$LOG_FILE"

# Git 提交
log "提交到 Git 仓库..."
git add .
git commit -m "📅 Daily update: Add 15 projects ($DATE)" 2>&1 | tee -a "$LOG_FILE"

# 推送到远程仓库（如果已配置）
if git remote | grep -q origin; then
    log "推送到远程仓库..."
    git push origin main 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "✅ 成功推送到 GitHub"
    else
        log "⚠️ 推送失败，请检查 GitHub 认证"
    fi
else
    log "⚠️ 远程仓库未配置，跳过推送"
fi

# 统计信息
TOTAL_PROJECTS=$(find "$REPO_DIR" -name "*.md" -type f ! -name "README.md" | wc -l)
log "========================================="
log "任务完成！"
log "今日收集: 15 个项目"
log "累计收集: $TOTAL_PROJECTS 天"
log "========================================="

exit 0
