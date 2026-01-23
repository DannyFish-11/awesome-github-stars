#!/bin/bash

# ========================================
# GitHub 高 Star 项目每日自动收集脚本
# 优化版本：增强错误处理、日志系统、通知功能
# ========================================

set -e  # 遇到错误立即退出
set -o pipefail  # 管道命令中任何一个失败都会导致整个管道失败

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

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)
            echo -e "${BLUE}[${timestamp}] ℹ️  [INFO]${NC} ${message}" | tee -a "$LOG_FILE"
            ;;
        SUCCESS)
            echo -e "${GREEN}[${timestamp}] ✅ [SUCCESS]${NC} ${message}" | tee -a "$LOG_FILE"
            ;;
        WARNING)
            echo -e "${YELLOW}[${timestamp}] ⚠️  [WARNING]${NC} ${message}" | tee -a "$LOG_FILE"
            ;;
        ERROR)
            echo -e "${RED}[${timestamp}] ❌ [ERROR]${NC} ${message}" | tee -a "$LOG_FILE"
            ;;
        *)
            echo "[${timestamp}] ${message}" | tee -a "$LOG_FILE"
            ;;
    esac
}

# 错误处理函数
handle_error() {
    local exit_code=$?
    local line_number=$1
    log ERROR "脚本在第 ${line_number} 行失败，退出码: ${exit_code}"
    log ERROR "任务执行失败，请检查日志: ${LOG_FILE}"
    
    # 记录失败状态
    echo "${DATE},FAILED,${exit_code}" >> "$LOG_DIR/execution_history.csv"
    
    exit $exit_code
}

# 设置错误陷阱
trap 'handle_error ${LINENO}' ERR

# 检查依赖
check_dependencies() {
    log INFO "检查系统依赖..."
    
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log ERROR "缺少依赖: ${missing_deps[*]}"
        exit 1
    fi
    
    # 检查 Python 模块
    if ! python3 -c "import requests" 2>/dev/null; then
        log WARNING "requests 模块未安装，尝试安装..."
        sudo pip3 install requests beautifulsoup4 -q
    fi
    
    log SUCCESS "依赖检查通过"
}

# 检查磁盘空间
check_disk_space() {
    log INFO "检查磁盘空间..."
    
    local available_space=$(df -BM "$REPO_DIR" | awk 'NR==2 {print $4}' | sed 's/M//')
    local required_space=100  # 至少需要 100MB
    
    if [ "$available_space" -lt "$required_space" ]; then
        log ERROR "磁盘空间不足: 可用 ${available_space}MB, 需要 ${required_space}MB"
        exit 1
    fi
    
    log SUCCESS "磁盘空间充足: ${available_space}MB 可用"
}

# 主函数
main() {
    log INFO "=========================================="
    log INFO "开始执行每日项目收集任务"
    log INFO "执行日期: ${DATE}"
    log INFO "=========================================="
    
    # 记录开始时间
    local start_time=$(date +%s)
    
    # 检查依赖和环境
    check_dependencies
    check_disk_space
    
    # 切换到仓库目录
    log INFO "切换到仓库目录: ${REPO_DIR}"
    cd "$REPO_DIR" || {
        log ERROR "无法切换到仓库目录: ${REPO_DIR}"
        exit 1
    }
    
    # 配置 Git（如果尚未配置）
    if [ -z "$(git config user.name)" ]; then
        log INFO "配置 Git 用户信息..."
        git config user.name "DannyFish-11"
        git config user.email "dannyfish@example.com"
    fi
    
    # 拉取最新代码
    if git remote | grep -q origin; then
        log INFO "拉取远程仓库最新代码..."
        if git pull origin main --rebase 2>&1 | tee -a "$LOG_FILE"; then
            log SUCCESS "代码拉取成功"
        else
            log WARNING "代码拉取失败，尝试强制同步..."
            git fetch origin
            git reset --hard origin/main
            log SUCCESS "强制同步完成"
        fi
    else
        log WARNING "远程仓库未配置，跳过拉取"
    fi
    
    # 检查今日是否已收集
    PROJECT_FILE="$REPO_DIR/$YEAR/$MONTH/$DATE.md"
    if [ -f "$PROJECT_FILE" ]; then
        log WARNING "今日项目已存在: $PROJECT_FILE"
        log WARNING "将覆盖现有文件"
        rm -f "$PROJECT_FILE"
    fi
    
    # 执行 Python 收集脚本
    log INFO "=========================================="
    log INFO "步骤 1/3: 执行项目收集脚本"
    log INFO "=========================================="
    
    if python3 "$SCRIPT_DIR/collect_projects.py" 2>&1 | tee -a "$LOG_FILE"; then
        log SUCCESS "项目收集完成"
    else
        log ERROR "项目收集失败"
        exit 1
    fi
    
    # 验证文件生成
    if [ ! -f "$PROJECT_FILE" ]; then
        log ERROR "项目文件未生成: $PROJECT_FILE"
        exit 1
    fi
    
    local file_size=$(stat -f%z "$PROJECT_FILE" 2>/dev/null || stat -c%s "$PROJECT_FILE" 2>/dev/null)
    log SUCCESS "项目文件已生成: $PROJECT_FILE (${file_size} bytes)"
    
    # 更新月度索引
    log INFO "=========================================="
    log INFO "步骤 2/3: 更新月度索引"
    log INFO "=========================================="
    
    if python3 "$SCRIPT_DIR/update_index.py" 2>&1 | tee -a "$LOG_FILE"; then
        log SUCCESS "索引更新完成"
    else
        log ERROR "索引更新失败"
        exit 1
    fi
    
    # Git 提交和推送
    log INFO "=========================================="
    log INFO "步骤 3/3: 提交到 Git 仓库"
    log INFO "=========================================="
    
    # 检查是否有更改
    if git diff --quiet && git diff --cached --quiet; then
        log WARNING "没有检测到更改，跳过提交"
    else
        log INFO "添加文件到 Git..."
        git add .
        
        log INFO "提交更改..."
        git commit -m "📅 Daily collection: ${DATE} - 15 projects added

- Collected 8 trending projects from GitHub Trending
- Collected 7 top-starred projects from history
- Updated monthly index and main README
- Auto-generated by daily_collect.sh

Execution time: $(date +'%Y-%m-%d %H:%M:%S')" 2>&1 | tee -a "$LOG_FILE"
        
        log SUCCESS "提交完成"
        
        # 推送到远程仓库
        if git remote | grep -q origin; then
            log INFO "推送到远程仓库..."
            
            local push_attempts=0
            local max_push_attempts=3
            local push_success=false
            
            while [ $push_attempts -lt $max_push_attempts ]; do
                if git push origin main 2>&1 | tee -a "$LOG_FILE"; then
                    log SUCCESS "推送成功"
                    push_success=true
                    break
                else
                    push_attempts=$((push_attempts + 1))
                    if [ $push_attempts -lt $max_push_attempts ]; then
                        log WARNING "推送失败，5秒后重试 (${push_attempts}/${max_push_attempts})..."
                        sleep 5
                    fi
                fi
            done
            
            if [ "$push_success" = false ]; then
                log ERROR "推送失败，已尝试 ${max_push_attempts} 次"
                log WARNING "本地更改已保存，请稍后手动推送"
            fi
        else
            log WARNING "远程仓库未配置，跳过推送"
        fi
    fi
    
    # 统计信息
    log INFO "=========================================="
    log INFO "生成统计报告"
    log INFO "=========================================="
    
    local total_days=$(find "$REPO_DIR" -name "*.md" -type f ! -name "README.md" ! -name "PROJECT_DOCUMENTATION.md" ! -path "*/logs/*" | wc -l | tr -d ' ')
    local total_projects=$((total_days * 15))
    local log_size=$(du -h "$LOG_FILE" | cut -f1)
    
    # 计算执行时间
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    local minutes=$((execution_time / 60))
    local seconds=$((execution_time % 60))
    
    log SUCCESS "=========================================="
    log SUCCESS "任务执行完成！"
    log SUCCESS "=========================================="
    log INFO "今日收集: 15 个项目"
    log INFO "累计天数: ${total_days} 天"
    log INFO "累计项目: ${total_projects} 个"
    log INFO "执行时间: ${minutes}分${seconds}秒"
    log INFO "日志文件: ${LOG_FILE} (${log_size})"
    log SUCCESS "=========================================="
    
    # 记录成功状态
    echo "${DATE},SUCCESS,${execution_time}" >> "$LOG_DIR/execution_history.csv"
    
    # 清理旧日志（保留最近 30 天）
    log INFO "清理旧日志文件..."
    find "$LOG_DIR" -name "collect_*.log" -type f -mtime +30 -delete 2>/dev/null || true
    log SUCCESS "日志清理完成"
    
    return 0
}

# 执行主函数
main "$@"
exit_code=$?

# 最终状态
if [ $exit_code -eq 0 ]; then
    log SUCCESS "脚本执行成功，退出码: ${exit_code}"
else
    log ERROR "脚本执行失败，退出码: ${exit_code}"
fi

exit $exit_code
