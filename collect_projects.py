#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub 高 Star 项目自动收集脚本
每天收集 15 个高 star 开源项目
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import sys

# 配置
REPO_DIR = "/home/ubuntu/awesome-github-stars"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def log(message):
    """日志输出"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def get_trending_projects(limit=8):
    """获取 GitHub Trending 项目"""
    url = "https://github.com/trending"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        projects = []
        articles = soup.find_all('article', class_='Box-row')[:limit]
        
        for article in articles:
            try:
                # 项目名称和链接
                h2 = article.find('h2')
                if h2 and h2.find('a'):
                    link = h2.find('a')
                    repo_name = link.get('href', '').strip('/')
                    repo_url = f"https://github.com{link.get('href', '')}"
                    
                    # 描述
                    desc_elem = article.find('p', class_='col-9')
                    description = desc_elem.text.strip() if desc_elem else "No description"
                    
                    # Stars
                    stars_elem = article.find('svg', class_='octicon-star')
                    stars = "N/A"
                    if stars_elem and stars_elem.parent:
                        stars_text = stars_elem.parent.text.strip()
                        # 提取数字
                        import re
                        match = re.search(r'([\d,]+)', stars_text)
                        if match:
                            stars = match.group(1)
                    
                    # 语言
                    lang_elem = article.find('span', itemprop='programmingLanguage')
                    language = lang_elem.text.strip() if lang_elem else "Unknown"
                    
                    # 今日新增 stars
                    today_stars_elem = article.find('span', class_='d-inline-block float-sm-right')
                    today_stars = ""
                    if today_stars_elem:
                        today_stars = today_stars_elem.text.strip()
                    
                    projects.append({
                        'name': repo_name,
                        'url': repo_url,
                        'description': description,
                        'stars': stars,
                        'language': language,
                        'today_stars': today_stars,
                        'source': 'trending'
                    })
            except Exception as e:
                log(f"解析项目失败: {e}")
                continue
        
        log(f"✅ 从 Trending 获取了 {len(projects)} 个项目")
        return projects
    except Exception as e:
        log(f"❌ 获取 Trending 失败: {e}")
        return []

def get_top_starred_projects(limit=7):
    """获取历史高 star 项目"""
    projects = [
        {
            'name': 'build-your-own-x',
            'url': 'https://github.com/codecrafters-io/build-your-own-x',
            'stars': '458,524',
            'forks': '42,983',
            'language': 'Markdown',
            'description': 'Master programming by recreating your favorite technologies from scratch.',
            'source': 'top-stars'
        },
        {
            'name': 'freeCodeCamp',
            'url': 'https://github.com/freeCodeCamp/freeCodeCamp',
            'stars': '436,070',
            'forks': '43,128',
            'language': 'TypeScript',
            'description': "freeCodeCamp.org's open-source codebase and curriculum. Learn to code for free.",
            'source': 'top-stars'
        },
        {
            'name': 'awesome',
            'url': 'https://github.com/sindresorhus/awesome',
            'stars': '430,688',
            'forks': '32,881',
            'language': 'None',
            'description': '😎 Awesome lists about all kinds of interesting topics',
            'source': 'top-stars'
        },
        {
            'name': 'public-apis',
            'url': 'https://github.com/public-apis/public-apis',
            'stars': '392,084',
            'forks': '41,968',
            'language': 'Python',
            'description': 'A collective list of free APIs',
            'source': 'top-stars'
        },
        {
            'name': 'free-programming-books',
            'url': 'https://github.com/EbookFoundation/free-programming-books',
            'stars': '380,748',
            'forks': '65,761',
            'language': 'Python',
            'description': '📚 Freely available programming books',
            'source': 'top-stars'
        },
        {
            'name': 'developer-roadmap',
            'url': 'https://github.com/kamranahmedse/developer-roadmap',
            'stars': '347,550',
            'forks': '43,634',
            'language': 'TypeScript',
            'description': 'Interactive roadmaps, guides and other educational content to help developers grow.',
            'source': 'top-stars'
        },
        {
            'name': 'coding-interview-university',
            'url': 'https://github.com/jwasham/coding-interview-university',
            'stars': '335,965',
            'forks': '81,577',
            'language': 'None',
            'description': 'A complete computer science study plan to become a software engineer.',
            'source': 'top-stars'
        },
        {
            'name': 'system-design-primer',
            'url': 'https://github.com/donnemartin/system-design-primer',
            'stars': '332,703',
            'forks': '54,087',
            'language': 'Python',
            'description': 'Learn how to design large-scale systems. Prep for the system design interview.',
            'source': 'top-stars'
        },
        {
            'name': 'vue',
            'url': 'https://github.com/vuejs/vue',
            'stars': '210,000',
            'forks': '33,000',
            'language': 'JavaScript',
            'description': '🖖 Vue.js is a progressive, incrementally-adoptable JavaScript framework.',
            'source': 'top-stars'
        },
        {
            'name': 'react',
            'url': 'https://github.com/facebook/react',
            'stars': '242,393',
            'forks': '50,435',
            'language': 'JavaScript',
            'description': 'The library for web and native user interfaces.',
            'source': 'top-stars'
        }
    ]
    
    log(f"✅ 从 Top Stars 列表获取了 {limit} 个项目")
    return projects[:limit]

def create_markdown(projects, date):
    """生成 Markdown 文档"""
    year = date.strftime('%Y')
    month = date.strftime('%m-%B')
    date_str = date.strftime('%Y-%m-%d')
    
    # 创建目录
    target_dir = os.path.join(REPO_DIR, year, month)
    os.makedirs(target_dir, exist_ok=True)
    
    # 生成 Markdown 内容
    content = f"""# 🌟 GitHub 高 Star 开源项目精选

**收集日期**: {date_str}  
**项目数量**: {len(projects)} 个

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
- **🔥 热门趋势项目**：当日 GitHub Trending 上的热门项目
- **⭐ 历史高 star 项目**：GitHub 历史累计 star 数最多的项目

所有项目均为完整开源项目，可供学习、参考和使用。

---

**最后更新**: {date_str}  
**收集方式**: 自动化脚本  
**数据来源**: GitHub Trending & GitHub Ranking
"""
    
    # 保存文件
    output_file = os.path.join(target_dir, f"{date_str}.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    log(f"✅ Markdown 文档已生成: {output_file}")
    return output_file

def main():
    """主函数"""
    log("=" * 50)
    log("开始收集 GitHub 高 Star 项目")
    log("=" * 50)
    
    # 获取项目
    trending = get_trending_projects(8)
    top_stars = get_top_starred_projects(7)
    
    # 合并项目列表
    all_projects = trending + top_stars
    
    # 确保有 15 个项目
    if len(all_projects) < 15:
        log(f"⚠️ 只收集到 {len(all_projects)} 个项目，补充到 15 个")
        # 如果不足，从 top_stars 补充
        additional = get_top_starred_projects(15 - len(all_projects))
        all_projects.extend(additional)
    
    all_projects = all_projects[:15]
    
    log(f"📦 共收集 {len(all_projects)} 个项目")
    
    # 生成 Markdown
    today = datetime.now()
    output_file = create_markdown(all_projects, today)
    
    log("=" * 50)
    log("✅ 收集任务完成！")
    log("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
