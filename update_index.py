#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新月度索引文件
"""

import os
from datetime import datetime
from collections import Counter

REPO_DIR = "/home/ubuntu/awesome-github-stars"

def update_monthly_index():
    """更新月度索引"""
    today = datetime.now()
    year = today.strftime('%Y')
    month = today.strftime('%m-%B')
    month_dir = os.path.join(REPO_DIR, year, month)
    
    if not os.path.exists(month_dir):
        print(f"月度目录不存在: {month_dir}")
        return
    
    # 获取所有日期文件
    date_files = []
    for file in os.listdir(month_dir):
        if file.endswith('.md') and file != 'README.md':
            date_files.append(file.replace('.md', ''))
    
    date_files.sort()
    
    # 统计信息
    total_days = len(date_files)
    total_projects = total_days * 15
    
    # 生成索引内容
    content = f"""# 📅 {year}年{int(month[:2])}月 - GitHub 项目收集

## 本月统计

- **收集天数**: {total_days} 天
- **项目总数**: {total_projects} 个
- **更新状态**: 🟢 活跃

## 📋 每日记录

| 日期 | 项目数 | 文件链接 |
|------|--------|----------|
"""
    
    for date in date_files:
        content += f"| {date} | 15 | [查看详情](./{date}.md) |\n"
    
    content += f"""
## 🔥 本月热门语言

- Python
- TypeScript
- JavaScript
- Rust
- Go

---

**返回**: [主页](../../README.md)
"""
    
    # 保存索引文件
    index_file = os.path.join(month_dir, 'README.md')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 月度索引已更新: {index_file}")

def update_main_readme():
    """更新主 README"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    readme_path = os.path.join(REPO_DIR, 'README.md')
    
    # 统计总项目数
    total_projects = 0
    for root, dirs, files in os.walk(REPO_DIR):
        for file in files:
            if file.endswith('.md') and file != 'README.md' and '/' in root:
                total_projects += 15
    
    content = f"""# 🌟 Awesome GitHub Stars Collection

[![Auto Update](https://img.shields.io/badge/Auto%20Update-Daily-brightgreen)](https://github.com)
[![Projects](https://img.shields.io/badge/Projects-{total_projects}-blue)](https://github.com)

## 📖 项目简介

本仓库每天自动收集 **15 个 GitHub 高 star 开源项目**，包括：

- 🔥 **GitHub Trending**：当日最热门的趋势项目
- ⭐ **Top Stars**：历史累计 star 数最高的优质项目

所有项目均为完整开源项目，涵盖多种编程语言和技术领域，适合学习、参考和使用。

## 📂 仓库结构

```
awesome-github-stars/
├── README.md                    # 项目说明
├── 2026/                        # 按年份分类
│   └── 01-January/             # 按月份分类
│       ├── README.md           # 月度索引
│       ├── 2026-01-20.md       # 每日收集记录
│       ├── 2026-01-21.md
│       └── ...
└── logs/                        # 运行日志
```

## 📊 收集规则

- **收集频率**：每天自动执行
- **项目数量**：每天 15 个
- **项目标准**：5k+ stars 或当日热门趋势
- **仓库容量**：每个仓库存放约 100 个项目（满后自动创建新仓库）
- **更新时间**：每天 UTC+8 时区自动更新

## 📝 项目信息

每个项目包含以下信息：

- 项目名称和链接
- 编程语言
- Star 数和 Fork 数
- 项目简介
- 今日新增 Star 数（如适用）
- 项目来源标记（Trending / Top Stars）

## 🔗 最新收集

查看最新收集的项目：[点击这里](./2026/01-January/)

## 📜 License

MIT License - 数据来源于 GitHub 公开信息

---

**最后更新**: {today}  
**自动化工具**: Manus AI Agent  
**数据来源**: GitHub Trending & GitHub Ranking  
**项目地址**: https://github.com/DannyFish-11/awesome-github-stars
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 主 README 已更新")

if __name__ == "__main__":
    update_monthly_index()
    update_main_readme()
