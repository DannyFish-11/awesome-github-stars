#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新月度索引文件
优化版本：增强统计功能、错误处理、语言分析
"""

import os
import re
from datetime import datetime
from collections import Counter

REPO_DIR = "/home/ubuntu/awesome-github-stars"

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level_emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    emoji = level_emoji.get(level, "📝")
    print(f"[{timestamp}] {emoji} [{level}] {message}")

def extract_languages_from_file(file_path):
    """从 Markdown 文件中提取编程语言"""
    languages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 匹配 **编程语言**: `XXX`
            matches = re.findall(r'\*\*编程语言\*\*:\s*`([^`]+)`', content)
            languages.extend(matches)
    except Exception as e:
        log(f"读取文件失败 {file_path}: {e}", "WARNING")
    return languages

def update_monthly_index():
    """更新月度索引（增强版）"""
    today = datetime.now()
    year = today.strftime('%Y')
    month = today.strftime('%m-%B')
    month_dir = os.path.join(REPO_DIR, year, month)
    
    if not os.path.exists(month_dir):
        log(f"月度目录不存在: {month_dir}", "ERROR")
        return False
    
    # 获取所有日期文件
    date_files = []
    for file in os.listdir(month_dir):
        if file.endswith('.md') and file != 'README.md':
            date_files.append(file.replace('.md', ''))
    
    date_files.sort()
    
    if not date_files:
        log("没有找到任何日期文件", "WARNING")
        return False
    
    # 统计信息
    total_days = len(date_files)
    total_projects = total_days * 15
    
    # 分析语言分布
    all_languages = []
    for date_file in date_files:
        file_path = os.path.join(month_dir, f"{date_file}.md")
        languages = extract_languages_from_file(file_path)
        all_languages.extend(languages)
    
    # 统计语言出现次数
    language_counter = Counter(all_languages)
    top_languages = language_counter.most_common(10)
    
    # 生成索引内容
    content = f"""# 📅 {year}年{int(month[:2])}月 - GitHub 项目收集

## 📊 本月统计

- **收集天数**: {total_days} 天
- **项目总数**: {total_projects} 个
- **更新状态**: 🟢 活跃
- **最后更新**: {date_files[-1]}

## 📋 每日记录

| 日期 | 项目数 | 文件链接 |
|------|--------|----------|
"""
    
    for date in date_files:
        content += f"| {date} | 15 | [查看详情](./{date}.md) |\n"
    
    # 添加语言统计
    if top_languages:
        content += f"""
## 🔥 本月热门语言

"""
        for idx, (lang, count) in enumerate(top_languages, 1):
            percentage = (count / len(all_languages)) * 100 if all_languages else 0
            content += f"{idx}. **{lang}** - {count} 个项目 ({percentage:.1f}%)\n"
    
    content += f"""
## 📈 趋势分析

本月收集的项目涵盖了 {len(language_counter)} 种编程语言，展现了开源社区的多样性。热门语言反映了当前技术发展趋势和开发者关注重点。

## 🎯 项目来源

- **🔥 GitHub Trending**: 每天 8 个热门趋势项目
- **⭐ Top Stars**: 每天 7 个历史高 star 项目

所有项目均经过筛选，确保质量和实用性。

---

**返回**: [主页](../../README.md)  
**仓库地址**: https://github.com/DannyFish-11/awesome-github-stars
"""
    
    # 保存索引文件
    index_file = os.path.join(month_dir, 'README.md')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    log(f"月度索引已更新: {index_file}", "SUCCESS")
    return True

def update_main_readme():
    """更新主 README（增强版）"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    readme_path = os.path.join(REPO_DIR, 'README.md')
    
    # 统计总项目数和天数
    total_days = 0
    total_projects = 0
    all_languages = []
    
    for root, dirs, files in os.walk(REPO_DIR):
        for file in files:
            if file.endswith('.md') and file != 'README.md' and '/' in root:
                # 排除根目录的 README
                if root != REPO_DIR:
                    total_days += 1
                    total_projects += 15
                    # 提取语言信息
                    file_path = os.path.join(root, file)
                    languages = extract_languages_from_file(file_path)
                    all_languages.extend(languages)
    
    # 统计语言
    language_counter = Counter(all_languages)
    top_5_languages = [lang for lang, _ in language_counter.most_common(5)]
    
    content = f"""# 🌟 Awesome GitHub Stars Collection

[![Auto Update](https://img.shields.io/badge/Auto%20Update-Daily-brightgreen)](https://github.com/DannyFish-11/awesome-github-stars)
[![Projects](https://img.shields.io/badge/Projects-{total_projects}-blue)](https://github.com/DannyFish-11/awesome-github-stars)
[![Days](https://img.shields.io/badge/Days-{total_days}-orange)](https://github.com/DannyFish-11/awesome-github-stars)
[![Languages](https://img.shields.io/badge/Languages-{len(language_counter)}-red)](https://github.com/DannyFish-11/awesome-github-stars)

## 📖 项目简介

本仓库每天自动收集 **15 个 GitHub 高 star 开源项目**，通过自动化脚本从 GitHub Trending 和历史高 star 项目列表中精选优质开源项目，整理成结构化的 Markdown 文档。

### 收集来源

- **🔥 GitHub Trending**：每天 8 个最热门的趋势项目，代表当前最受关注的开源项目
- **⭐ Top Stars**：每天 7 个历史累计 star 数最高的优质项目，经过时间检验的经典项目

所有项目均为完整开源项目，涵盖多种编程语言和技术领域，适合学习、参考和使用。

## 📊 统计数据

- **累计收集天数**: {total_days} 天
- **累计收集项目**: {total_projects} 个
- **涵盖编程语言**: {len(language_counter)} 种
- **热门语言**: {', '.join(top_5_languages[:5])}
- **最后更新**: {today}

## 📂 仓库结构

```
awesome-github-stars/
├── README.md                    # 项目说明（本文件）
├── PROJECT_DOCUMENTATION.md     # 完整项目文档
├── daily_collect.sh            # 每日自动收集脚本
├── collect_projects.py         # 项目收集核心脚本
├── update_index.py             # 索引更新脚本
├── logs/                       # 运行日志
│   └── collect_YYYY-MM-DD.log
├── 2026/                       # 按年份分类
│   └── 01-January/            # 按月份分类
│       ├── README.md          # 月度索引
│       ├── 2026-01-20.md      # 每日收集记录
│       ├── 2026-01-21.md
│       └── ...
└── .git/                       # Git 仓库
```

## 📊 收集规则

- **收集频率**：每天自动执行一次
- **项目数量**：每天固定 15 个项目
- **项目标准**：5k+ stars 或当日热门趋势
- **更新时间**：每天 UTC+8 时区自动更新
- **数据来源**：GitHub Trending + GitHub Ranking

## 📝 项目信息

每个项目包含以下完整信息：

- **项目名称和链接**：直达 GitHub 仓库
- **编程语言**：项目主要使用的编程语言
- **Star 数**：项目获得的 star 数量
- **Fork 数**：项目被 fork 的次数
- **项目简介**：项目的功能和特点描述
- **今日新增 Star 数**：Trending 项目的当日新增 star（如适用）
- **项目来源标记**：标识项目来自 Trending 还是 Top Stars

## 🔗 快速导航

### 最新收集
查看最新收集的项目：[点击这里](./2026/01-January/)

### 按月浏览
- [2026年1月](./2026/01-January/) - {total_days} 天，{total_projects} 个项目

## 🚀 使用说明

### 浏览项目
1. 进入对应年份和月份的目录
2. 选择日期查看当天收集的 15 个项目
3. 点击项目链接直达 GitHub 仓库

### 本地运行
```bash
# 克隆仓库
git clone https://github.com/DannyFish-11/awesome-github-stars.git

# 进入目录
cd awesome-github-stars

# 查看项目
cat 2026/01-January/2026-01-22.md
```

### 自动化部署
本项目使用自动化脚本每天定时执行，详见 [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)

## 🛠️ 技术栈

- **爬虫**: Python + Requests + BeautifulSoup4
- **版本控制**: Git + GitHub
- **自动化**: Bash Shell + Cron
- **文档格式**: Markdown

## 📈 项目特点

- ✅ **全自动化**：无需人工干预，每天自动收集和推送
- ✅ **结构清晰**：按年/月/日组织，便于查找和浏览
- ✅ **信息完整**：包含项目的所有关键信息
- ✅ **持续更新**：每天定时更新，保持内容新鲜
- ✅ **开源免费**：所有代码和数据完全开源

## 📜 License

MIT License - 数据来源于 GitHub 公开信息

本项目仅用于学习和参考目的，所有项目信息均来自 GitHub 公开数据。

---

**最后更新**: {today}  
**自动化工具**: Manus AI Agent  
**数据来源**: GitHub Trending & GitHub Ranking  
**项目地址**: https://github.com/DannyFish-11/awesome-github-stars  
**维护状态**: 🟢 活跃维护中
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    log(f"主 README 已更新 (总计 {total_days} 天, {total_projects} 个项目)", "SUCCESS")
    return True

def main():
    """主函数"""
    log("=" * 60, "INFO")
    log("开始更新索引文件", "INFO")
    log("=" * 60, "INFO")
    
    try:
        # 更新月度索引
        log("步骤 1/2: 更新月度索引...", "INFO")
        success1 = update_monthly_index()
        
        # 更新主 README
        log("步骤 2/2: 更新主 README...", "INFO")
        success2 = update_main_readme()
        
        if success1 and success2:
            log("=" * 60, "INFO")
            log("✅ 索引更新完成！", "SUCCESS")
            log("=" * 60, "INFO")
            return 0
        else:
            log("部分更新失败", "WARNING")
            return 1
            
    except Exception as e:
        log(f"更新失败: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
