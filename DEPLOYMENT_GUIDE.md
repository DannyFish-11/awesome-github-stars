# 🚀 GitHub 项目收集系统 - 部署指南

## 📋 目录

- [部署概述](#部署概述)
- [部署平台选择](#部署平台选择)
- [部署方案](#部署方案)
  - [方案一：GitHub Actions（推荐）](#方案一github-actions推荐)
  - [方案二：云服务器 Cron](#方案二云服务器-cron)
  - [方案三：Manus 定时任务](#方案三manus-定时任务)
- [环境要求](#环境要求)
- [部署步骤](#部署步骤)
- [配置说明](#配置说明)
- [测试验证](#测试验证)
- [故障排查](#故障排查)

---

## 📖 部署概述

本系统是一个全自动化的 GitHub 项目收集工具，需要部署到能够定时执行任务的平台上。系统每天自动收集 15 个 GitHub 高 star 项目，生成 Markdown 文档并推送到 GitHub 仓库。

### 核心特性

- **全自动化**：无需人工干预，定时自动执行
- **稳定可靠**：完善的错误处理和重试机制
- **日志完整**：详细的执行日志和状态记录
- **易于维护**：清晰的代码结构和文档

### 系统架构

```
定时触发器 → daily_collect.sh → collect_projects.py → update_index.py → Git Push
                    ↓                      ↓                    ↓
                日志记录              项目收集              索引更新
```

---

## 🎯 部署平台选择

### 平台对比

| 平台 | 优点 | 缺点 | 推荐度 | 成本 |
|------|------|------|--------|------|
| **GitHub Actions** | 免费、集成度高、无需服务器 | 执行时间限制、公开仓库免费 | ⭐⭐⭐⭐⭐ | 免费 |
| **云服务器 Cron** | 完全控制、无限制 | 需要服务器、需要维护 | ⭐⭐⭐⭐ | $5-20/月 |
| **Manus 定时任务** | 简单易用、无需配置 | 依赖 Manus 平台 | ⭐⭐⭐⭐ | 按使用量 |
| **Heroku Scheduler** | 简单易用 | 免费版有限制 | ⭐⭐⭐ | 免费/$7/月 |
| **AWS Lambda** | 按需付费、高可用 | 配置复杂 | ⭐⭐⭐ | 按使用量 |

### 推荐方案

**首选：GitHub Actions**（免费、稳定、易维护）  
**备选：云服务器 Cron**（完全控制、无限制）  
**快速：Manus 定时任务**（最简单、立即可用）

---

## 🚀 部署方案

### 方案一：GitHub Actions（推荐）

**适用场景**：公开仓库、希望零成本运行、不需要服务器

#### 优点
- ✅ 完全免费（公开仓库）
- ✅ 无需服务器维护
- ✅ 与 GitHub 深度集成
- ✅ 自动处理认证
- ✅ 提供执行日志

#### 部署步骤

##### 1. 创建 GitHub Actions 工作流

在仓库中创建文件 `.github/workflows/daily-collect.yml`：

```yaml
name: Daily GitHub Stars Collection

on:
  schedule:
    # 每天 UTC 01:00 执行（北京时间 09:00）
    - cron: '0 1 * * *'
  workflow_dispatch:  # 允许手动触发

jobs:
  collect:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install requests beautifulsoup4
    
    - name: Configure Git
      run: |
        git config user.name "DannyFish-11"
        git config user.email "dannyfish@example.com"
    
    - name: Run collection script
      run: |
        chmod +x daily_collect.sh
        ./daily_collect.sh
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Upload logs
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: collection-logs
        path: logs/
        retention-days: 30
```

##### 2. 配置 GitHub Token

GitHub Actions 会自动提供 `GITHUB_TOKEN`，无需额外配置。如果需要更高权限：

1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 生成新 token，勾选 `repo` 权限
3. 在仓库 Settings → Secrets → Actions 中添加 `GH_TOKEN`
4. 修改 workflow 中的 `token: ${{ secrets.GH_TOKEN }}`

##### 3. 启用 GitHub Actions

1. 进入仓库的 **Actions** 标签
2. 如果是首次使用，点击 **I understand my workflows, go ahead and enable them**
3. 找到 **Daily GitHub Stars Collection** 工作流
4. 点击 **Enable workflow**

##### 4. 测试运行

1. 进入 **Actions** 标签
2. 选择 **Daily GitHub Stars Collection**
3. 点击 **Run workflow** → **Run workflow**
4. 等待执行完成，查看日志

##### 5. 验证结果

- 检查是否生成新的项目文件
- 查看 Git 提交历史
- 下载日志文件查看详细信息

---

### 方案二：云服务器 Cron

**适用场景**：已有服务器、需要完全控制、私有部署

#### 支持的云平台

- **阿里云 ECS**
- **腾讯云 CVM**
- **AWS EC2**
- **DigitalOcean Droplet**
- **Vultr VPS**
- **任何 Linux 服务器**

#### 部署步骤

##### 1. 准备服务器

**最低配置**：
- CPU: 1 核
- 内存: 512MB
- 存储: 10GB
- 系统: Ubuntu 20.04+ / CentOS 7+

**推荐配置**：
- CPU: 1 核
- 内存: 1GB
- 存储: 20GB
- 系统: Ubuntu 22.04 LTS

##### 2. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y git python3 python3-pip

# 安装 Python 依赖
sudo pip3 install requests beautifulsoup4
```

##### 3. 克隆仓库

```bash
# 切换到工作目录
cd /home/ubuntu

# 克隆仓库
git clone https://github.com/DannyFish-11/awesome-github-stars.git

# 进入目录
cd awesome-github-stars
```

##### 4. 配置 Git 认证

```bash
# 配置 Git 用户信息
git config user.name "DannyFish-11"
git config user.email "dannyfish@example.com"

# 配置远程仓库（使用 Token）
git remote set-url origin https://YOUR_GITHUB_TOKEN@github.com/DannyFish-11/awesome-github-stars.git
```

**替换 `YOUR_GITHUB_TOKEN`** 为你的 GitHub Personal Access Token（从 GitHub Settings → Developer settings → Personal access tokens 获取）。

##### 5. 测试脚本

```bash
# 设置执行权限
chmod +x daily_collect.sh

# 手动执行测试
./daily_collect.sh

# 查看日志
tail -f logs/collect_$(date +%Y-%m-%d).log
```

##### 6. 配置 Cron 定时任务

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天 09:00 执行）
0 9 * * * /home/ubuntu/awesome-github-stars/daily_collect.sh >> /home/ubuntu/awesome-github-stars/logs/cron.log 2>&1
```

**时区说明**：
- 服务器时区通常是 UTC
- 如果要在北京时间 09:00 执行，cron 应设置为 UTC 01:00
- 查看服务器时区：`date` 或 `timedatectl`

##### 7. 验证 Cron 配置

```bash
# 查看 crontab 列表
crontab -l

# 查看 cron 服务状态
sudo systemctl status cron

# 查看 cron 日志
tail -f /var/log/syslog | grep CRON
```

##### 8. 监控和维护

```bash
# 查看执行历史
cat logs/execution_history.csv

# 查看最近的日志
ls -lt logs/collect_*.log | head -5

# 清理旧日志（自动，也可手动）
find logs/ -name "collect_*.log" -mtime +30 -delete
```

---

### 方案三：Manus 定时任务

**适用场景**：快速部署、无需服务器、使用 Manus 平台

#### 部署步骤

##### 1. 准备 Playbook

Playbook 已在项目根目录，内容如下：

```markdown
**任务流程**：
1. 切换到仓库目录 /home/ubuntu/awesome-github-stars
2. 拉取远程最新代码（如果有冲突则覆盖本地）
3. 执行 Python 收集脚本 collect_projects.py
4. 执行索引更新脚本 update_index.py
5. Git 提交所有更改
6. 推送到远程仓库

**关键配置**：
- GitHub Token: 使用你自己的 GitHub Personal Access Token
- 仓库地址: https://github.com/DannyFish-11/awesome-github-stars
- 每天收集 15 个项目（8 个 Trending + 7 个 Top Stars）
- 按年/月目录结构组织文件

**注意事项**：
- 确保网络连接正常
- 检查 GitHub API 访问限制
- 日志文件保存在 logs/ 目录
- 如果推送失败，本地仍会保留提交记录
```

##### 2. 使用 Manus Schedule 工具

在 Manus 对话中执行：

```
请帮我设置定时任务：
- 任务名称：GitHub 项目每日收集
- 执行时间：每天 09:00（北京时间）
- 任务内容：执行 playbook 中的任务流程
- Playbook 路径：/home/ubuntu/awesome-github-stars/playbook.md
```

##### 3. 验证定时任务

```
请显示我的定时任务列表
```

##### 4. 手动触发测试

```
请立即执行一次 GitHub 项目收集任务
```

---

## 🔧 环境要求

### 系统要求

- **操作系统**：Linux (Ubuntu 20.04+, CentOS 7+) 或 macOS
- **Python**：3.8+（推荐 3.11）
- **Git**：2.0+
- **磁盘空间**：至少 1GB 可用空间
- **网络**：能够访问 GitHub 和 GitHub Trending

### Python 依赖

```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

安装命令：
```bash
pip3 install requests beautifulsoup4
```

### 权限要求

- **GitHub Token 权限**：`repo`（完整仓库访问）
- **文件系统权限**：读写执行权限
- **网络权限**：访问 github.com 和 api.github.com

---

## ⚙️ 配置说明

### 1. GitHub Token 配置

**获取 Token**：
1. 登录 GitHub
2. 访问 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 **Generate new token (classic)**
4. 勾选 `repo` 权限
5. 设置过期时间（建议 90 天或无过期）
6. 生成并复制 Token

**配置 Token**：

方法一：Git Remote URL
```bash
git remote set-url origin https://YOUR_GITHUB_TOKEN@github.com/DannyFish-11/awesome-github-stars.git
```

方法二：环境变量
```bash
export GITHUB_TOKEN="YOUR_TOKEN"
```

方法三：Git Credential Helper
```bash
git config --global credential.helper store
# 首次 push 时输入 Token
```

### 2. 时区配置

**查看当前时区**：
```bash
date
timedatectl
```

**设置时区（如需要）**：
```bash
# 设置为上海时区
sudo timedatectl set-timezone Asia/Shanghai

# 或者
sudo ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

**Cron 时间对照**：
- 北京时间 09:00 = UTC 01:00
- Cron 表达式：`0 1 * * *`（UTC）
- Cron 表达式：`0 9 * * *`（Asia/Shanghai）

### 3. 日志配置

日志文件位置：`/home/ubuntu/awesome-github-stars/logs/`

**日志类型**：
- `collect_YYYY-MM-DD.log`：每日收集日志
- `cron.log`：Cron 执行日志
- `execution_history.csv`：执行历史记录

**日志保留策略**：
- 自动清理 30 天前的日志
- 可在 `daily_collect.sh` 中修改保留天数

---

## ✅ 测试验证

### 1. 手动执行测试

```bash
cd /home/ubuntu/awesome-github-stars
./daily_collect.sh
```

**预期结果**：
- ✅ 收集 15 个项目
- ✅ 生成 Markdown 文档
- ✅ 更新索引文件
- ✅ Git 提交成功
- ✅ 推送到 GitHub 成功

### 2. 检查生成文件

```bash
# 查看今日文件
ls -lh 2026/01-January/$(date +%Y-%m-%d).md

# 查看文件内容
cat 2026/01-January/$(date +%Y-%m-%d).md | head -50
```

### 3. 验证 Git 提交

```bash
# 查看最近提交
git log --oneline -5

# 查看远程状态
git remote -v
git status
```

### 4. 查看日志

```bash
# 查看今日日志
tail -f logs/collect_$(date +%Y-%m-%d).log

# 查看执行历史
cat logs/execution_history.csv
```

### 5. 验证 GitHub 仓库

访问：https://github.com/DannyFish-11/awesome-github-stars

检查：
- ✅ 最新提交时间
- ✅ 文件是否更新
- ✅ README 统计数据

---

## 🔍 故障排查

### 问题 1：推送失败（Authentication failed）

**原因**：GitHub Token 无效或过期

**解决方案**：
```bash
# 重新配置 Token
git remote set-url origin https://NEW_TOKEN@github.com/DannyFish-11/awesome-github-stars.git

# 测试推送
git push origin main
```

### 问题 2：收集失败（Network error）

**原因**：网络连接问题或 GitHub 访问受限

**解决方案**：
```bash
# 测试网络连接
ping github.com
curl -I https://github.com/trending

# 检查代理设置（如需要）
export http_proxy="http://proxy:port"
export https_proxy="http://proxy:port"
```

### 问题 3：Cron 未执行

**原因**：Cron 配置错误或服务未运行

**解决方案**：
```bash
# 检查 Cron 服务
sudo systemctl status cron

# 启动 Cron 服务
sudo systemctl start cron

# 查看 Cron 日志
tail -f /var/log/syslog | grep CRON

# 验证 crontab 配置
crontab -l
```

### 问题 4：Python 模块未找到

**原因**：依赖未安装或 Python 版本不对

**解决方案**：
```bash
# 检查 Python 版本
python3 --version

# 安装依赖
sudo pip3 install requests beautifulsoup4

# 验证安装
python3 -c "import requests; import bs4; print('OK')"
```

### 问题 5：磁盘空间不足

**原因**：日志文件过多或仓库过大

**解决方案**：
```bash
# 查看磁盘使用
df -h

# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete

# 清理 Git 历史（谨慎）
git gc --prune=now
```

### 问题 6：GitHub API 限制

**原因**：请求频率过高

**解决方案**：
- 使用 GitHub Token（提高限制到 5000/小时）
- 减少请求频率
- 等待限制重置（每小时重置）

---

## 📊 监控和维护

### 日常监控

**每日检查**：
```bash
# 查看今日是否执行
ls -l 2026/01-January/$(date +%Y-%m-%d).md

# 查看最新日志
tail -20 logs/collect_$(date +%Y-%m-%d).log
```

**每周检查**：
```bash
# 查看执行历史
tail -7 logs/execution_history.csv

# 检查日志大小
du -sh logs/
```

**每月检查**：
```bash
# 查看项目统计
cat README.md | grep "累计"

# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete
```

### 性能优化

**优化建议**：
1. 定期清理日志文件
2. 使用 Git shallow clone（如果仓库过大）
3. 优化网络请求（使用缓存）
4. 监控磁盘使用情况

### 备份策略

**GitHub 自动备份**：
- 所有数据已推送到 GitHub
- GitHub 提供自动备份

**本地备份**（可选）：
```bash
# 备份整个仓库
tar -czf awesome-github-stars-backup-$(date +%Y%m%d).tar.gz awesome-github-stars/

# 上传到云存储
# rclone copy awesome-github-stars-backup-*.tar.gz remote:backups/
```

---

## 🎯 最佳实践

### 1. Token 安全

- ✅ 使用环境变量或 Secret 存储 Token
- ✅ 定期更新 Token
- ✅ 限制 Token 权限（只给必要权限）
- ❌ 不要在代码中硬编码 Token
- ❌ 不要在日志中输出 Token

### 2. 错误处理

- ✅ 使用重试机制
- ✅ 记录详细日志
- ✅ 设置错误通知（邮件/Webhook）
- ✅ 定期检查执行状态

### 3. 资源管理

- ✅ 定期清理日志
- ✅ 监控磁盘使用
- ✅ 优化网络请求
- ✅ 使用缓存机制

### 4. 代码维护

- ✅ 定期更新依赖
- ✅ 测试新功能
- ✅ 备份重要数据
- ✅ 文档保持更新

---

## 📞 支持和反馈

### 问题反馈

- **GitHub Issues**：https://github.com/DannyFish-11/awesome-github-stars/issues
- **项目文档**：[PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)

### 相关资源

- **GitHub Actions 文档**：https://docs.github.com/en/actions
- **Cron 表达式生成器**：https://crontab.guru/
- **GitHub API 文档**：https://docs.github.com/en/rest

---

**文档版本**：2.0  
**最后更新**：2026-01-22  
**维护状态**：✅ 活跃维护中
