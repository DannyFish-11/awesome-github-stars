#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub 高 Star 项目自动收集脚本
每天收集 15 个高 star 开源项目
优化版本：增强错误处理、重试机制、日志系统
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import sys
import time
import random

# 配置
REPO_DIR = "/home/ubuntu/awesome-github-stars"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒

def log(message, level="INFO"):
    """增强的日志输出"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level_emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔍"
    }
    emoji = level_emoji.get(level, "📝")
    print(f"[{timestamp}] {emoji} [{level}] {message}")

def retry_on_failure(func, *args, max_retries=MAX_RETRIES, **kwargs):
    """通用重试装饰器"""
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < max_retries:
                log(f"尝试 {attempt}/{max_retries} 失败: {e}，{RETRY_DELAY}秒后重试...", "WARNING")
                time.sleep(RETRY_DELAY)
            else:
                log(f"所有重试失败: {e}", "ERROR")
                raise
    return None

def get_trending_projects(limit=8):
    """获取 GitHub Trending 项目（增强版）"""
    url = "https://github.com/trending"
    
    def fetch_trending():
        log(f"正在访问 GitHub Trending: {url}", "DEBUG")
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        projects = []
        
        # 尝试多种选择器
        articles = soup.find_all('article', class_='Box-row')
        if not articles:
            articles = soup.find_all('article')
        
        log(f"找到 {len(articles)} 个候选项目", "DEBUG")
        
        for article in articles[:limit]:
            try:
                # 项目名称和链接
                h2 = article.find('h2')
                if not h2:
                    h2 = article.find('h1', class_='h3')
                
                if h2 and h2.find('a'):
                    link = h2.find('a')
                    repo_name = link.get('href', '').strip('/')
                    repo_url = f"https://github.com{link.get('href', '')}"
                    
                    # 描述
                    desc_elem = article.find('p', class_='col-9')
                    if not desc_elem:
                        desc_elem = article.find('p')
                    description = desc_elem.text.strip() if desc_elem else "No description available"
                    
                    # Stars
                    stars_elem = article.find('svg', class_='octicon-star')
                    stars = "N/A"
                    if stars_elem and stars_elem.parent:
                        stars_text = stars_elem.parent.text.strip()
                        import re
                        match = re.search(r'([\d,]+)', stars_text)
                        if match:
                            stars = match.group(1)
                    
                    # 语言
                    lang_elem = article.find('span', itemprop='programmingLanguage')
                    language = lang_elem.text.strip() if lang_elem else "Unknown"
                    
                    # 今日新增 stars
                    today_stars = ""
                    stars_today_elem = article.find('span', class_='d-inline-block float-sm-right')
                    if stars_today_elem:
                        today_stars = stars_today_elem.text.strip()
                    
                    # Forks（尝试获取）
                    forks = "N/A"
                    fork_elem = article.find('svg', class_='octicon-repo-forked')
                    if fork_elem and fork_elem.parent:
                        forks_text = fork_elem.parent.text.strip()
                        import re
                        match = re.search(r'([\d,]+)', forks_text)
                        if match:
                            forks = match.group(1)
                    
                    project = {
                        'name': repo_name,
                        'url': repo_url,
                        'description': description,
                        'stars': stars,
                        'forks': forks,
                        'language': language,
                        'today_stars': today_stars,
                        'source': 'trending'
                    }
                    
                    projects.append(project)
                    log(f"收集项目: {repo_name} ({language})", "DEBUG")
                    
            except Exception as e:
                log(f"解析单个项目失败: {e}", "WARNING")
                continue
        
        if len(projects) == 0:
            raise Exception("未能解析到任何项目，可能页面结构已变化")
        
        log(f"从 Trending 成功获取 {len(projects)} 个项目", "SUCCESS")
        return projects
    
    try:
        return retry_on_failure(fetch_trending)
    except Exception as e:
        log(f"获取 Trending 项目失败: {e}", "ERROR")
        return []

def get_top_starred_projects(limit=7):
    """获取历史高 star 项目（扩展版）"""
    projects = [
        {
            'name': 'codecrafters-io/build-your-own-x',
            'url': 'https://github.com/codecrafters-io/build-your-own-x',
            'stars': '458,524',
            'forks': '42,983',
            'language': 'Markdown',
            'description': 'Master programming by recreating your favorite technologies from scratch.',
            'source': 'top-stars'
        },
        {
            'name': 'freeCodeCamp/freeCodeCamp',
            'url': 'https://github.com/freeCodeCamp/freeCodeCamp',
            'stars': '436,070',
            'forks': '43,128',
            'language': 'TypeScript',
            'description': "freeCodeCamp.org's open-source codebase and curriculum. Learn to code for free.",
            'source': 'top-stars'
        },
        {
            'name': 'sindresorhus/awesome',
            'url': 'https://github.com/sindresorhus/awesome',
            'stars': '430,688',
            'forks': '32,881',
            'language': 'None',
            'description': '😎 Awesome lists about all kinds of interesting topics',
            'source': 'top-stars'
        },
        {
            'name': 'public-apis/public-apis',
            'url': 'https://github.com/public-apis/public-apis',
            'stars': '392,084',
            'forks': '41,968',
            'language': 'Python',
            'description': 'A collective list of free APIs',
            'source': 'top-stars'
        },
        {
            'name': 'EbookFoundation/free-programming-books',
            'url': 'https://github.com/EbookFoundation/free-programming-books',
            'stars': '380,748',
            'forks': '65,761',
            'language': 'None',
            'description': '📚 Freely available programming books',
            'source': 'top-stars'
        },
        {
            'name': 'kamranahmedse/developer-roadmap',
            'url': 'https://github.com/kamranahmedse/developer-roadmap',
            'stars': '347,550',
            'forks': '43,634',
            'language': 'TypeScript',
            'description': 'Interactive roadmaps, guides and other educational content to help developers grow.',
            'source': 'top-stars'
        },
        {
            'name': 'jwasham/coding-interview-university',
            'url': 'https://github.com/jwasham/coding-interview-university',
            'stars': '335,965',
            'forks': '81,577',
            'language': 'None',
            'description': 'A complete computer science study plan to become a software engineer.',
            'source': 'top-stars'
        },
        {
            'name': 'donnemartin/system-design-primer',
            'url': 'https://github.com/donnemartin/system-design-primer',
            'stars': '332,703',
            'forks': '54,087',
            'language': 'Python',
            'description': 'Learn how to design large-scale systems. Prep for the system design interview.',
            'source': 'top-stars'
        },
        {
            'name': 'vuejs/vue',
            'url': 'https://github.com/vuejs/vue',
            'stars': '210,000',
            'forks': '33,000',
            'language': 'JavaScript',
            'description': '🖖 Vue.js is a progressive, incrementally-adoptable JavaScript framework.',
            'source': 'top-stars'
        },
        {
            'name': 'facebook/react',
            'url': 'https://github.com/facebook/react',
            'stars': '242,393',
            'forks': '50,435',
            'language': 'JavaScript',
            'description': 'The library for web and native user interfaces.',
            'source': 'top-stars'
        },
        {
            'name': 'torvalds/linux',
            'url': 'https://github.com/torvalds/linux',
            'stars': '200,000',
            'forks': '55,000',
            'language': 'C',
            'description': 'Linux kernel source tree',
            'source': 'top-stars'
        },
        {
            'name': 'microsoft/vscode',
            'url': 'https://github.com/microsoft/vscode',
            'stars': '180,000',
            'forks': '32,000',
            'language': 'TypeScript',
            'description': 'Visual Studio Code',
            'source': 'top-stars'
        }
    ]
    
    # 随机打乱并选择指定数量
    random.shuffle(projects)
    selected = projects[:limit]
    
    log(f"从 Top Stars 列表获取了 {len(selected)} 个项目", "SUCCESS")
    return selected

def create_markdown(projects, date):
    """生成 Markdown 文档（增强版）"""
    year = date.strftime('%Y')
    month = date.strftime('%m-%B')
    date_str = date.strftime('%Y-%m-%d')
    
    # 创建目录
    target_dir = os.path.join(REPO_DIR, year, month)
    os.makedirs(target_dir, exist_ok=True)
    log(f"目标目录: {target_dir}", "DEBUG")
    
    # 统计信息
    trending_count = sum(1 for p in projects if p.get('source') == 'trending')
    top_stars_count = sum(1 for p in projects if p.get('source') == 'top-stars')
    languages = list(set(p.get('language', 'Unknown') for p in projects if p.get('language') != 'Unknown'))
    
    # 生成 Markdown 内容
    content = f"""# 🌟 GitHub 高 Star 开源项目精选

**收集日期**: {date_str}  
**项目数量**: {len(projects)} 个  
**来源分布**: 🔥 Trending ({trending_count}) | ⭐ Top Stars ({top_stars_count})  
**涵盖语言**: {', '.join(languages[:5])}{'...' if len(languages) > 5 else ''}

---

## 📊 项目列表

"""
    
    for idx, project in enumerate(projects, 1):
        name = project.get('name', 'Unknown')
        url = project.get('url', '#')
        description = project.get('description', 'No description')
        language = project.get('language', 'Unknown')
        stars = project.get('stars', 'N/A')
        forks = project.get('forks', 'N/A')
        today_stars = project.get('today_stars', '')
        source = project.get('source', 'unknown')
        
        source_badge = "🔥 Trending" if source == 'trending' else "⭐ Top Stars"
        
        content += f"""### {idx}. [{name}]({url})

**编程语言**: `{language}` | **来源**: {source_badge}  
"""
        
        if stars != 'N/A' and stars != 'Star':
            content += f"**⭐ Stars**: {stars}  \n"
        if forks != 'N/A':
            content += f"**🔀 Forks**: {forks}  \n"
        if today_stars:
            content += f"**📈 今日新增**: {today_stars}  \n"
        
        content += f"""
**项目简介**: {description}

**项目链接**: {url}

---

"""
    
    # 添加页脚
    content += f"""
## 📝 说明

本文档收集了 GitHub 上的高 star 开源项目，包括：

**🔥 热门趋势项目**：当日 GitHub Trending 上的热门项目，代表当前最受关注的开源项目。这些项目通常具有创新性、实用性强，是开发者学习和参考的优质资源。

**⭐ 历史高 star 项目**：GitHub 历史累计 star 数最多的项目，经过时间检验的经典项目。这些项目通常是各个领域的标杆，具有极高的学习和参考价值。

所有项目均为完整开源项目，可供学习、参考和使用。项目信息包括名称、描述、编程语言、star 数、fork 数等，帮助开发者快速了解项目概况。

---

## 📊 统计信息

- **收集日期**: {date_str}
- **项目总数**: {len(projects)} 个
- **Trending 项目**: {trending_count} 个
- **Top Stars 项目**: {top_stars_count} 个
- **涵盖语言**: {len(languages)} 种

---

**最后更新**: {date_str}  
**收集方式**: 自动化脚本  
**数据来源**: GitHub Trending & GitHub Ranking  
**项目仓库**: https://github.com/DannyFish-11/awesome-github-stars
"""
    
    # 保存文件
    output_file = os.path.join(target_dir, f"{date_str}.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    log(f"Markdown 文档已生成: {output_file}", "SUCCESS")
    return output_file

def validate_projects(projects):
    """验证项目数据完整性"""
    valid_projects = []
    for project in projects:
        if not project.get('name') or not project.get('url'):
            log(f"跳过无效项目: {project}", "WARNING")
            continue
        valid_projects.append(project)
    return valid_projects

def main():
    """主函数"""
    log("=" * 60, "INFO")
    log("开始收集 GitHub 高 Star 项目", "INFO")
    log("=" * 60, "INFO")
    
    try:
        # 获取项目
        log("步骤 1/4: 获取 Trending 项目...", "INFO")
        trending = get_trending_projects(8)
        
        log("步骤 2/4: 获取 Top Stars 项目...", "INFO")
        top_stars = get_top_starred_projects(7)
        
        # 合并项目列表
        all_projects = trending + top_stars
        
        # 验证数据
        log("步骤 3/4: 验证项目数据...", "INFO")
        all_projects = validate_projects(all_projects)
        
        # 确保有 15 个项目
        if len(all_projects) < 15:
            log(f"只收集到 {len(all_projects)} 个项目，补充到 15 个", "WARNING")
            additional_needed = 15 - len(all_projects)
            additional = get_top_starred_projects(additional_needed)
            all_projects.extend(additional)
        
        all_projects = all_projects[:15]
        
        log(f"共收集 {len(all_projects)} 个有效项目", "SUCCESS")
        
        # 生成 Markdown
        log("步骤 4/4: 生成 Markdown 文档...", "INFO")
        today = datetime.now()
        output_file = create_markdown(all_projects, today)
        
        log("=" * 60, "INFO")
        log("✅ 收集任务完成！", "SUCCESS")
        log(f"输出文件: {output_file}", "INFO")
        log("=" * 60, "INFO")
        
        return 0
        
    except Exception as e:
        log(f"任务执行失败: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())
