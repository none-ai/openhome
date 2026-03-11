#!/usr/bin/env python3
"""
GitHub 趋势分析工具
获取GitHub trending仓库
"""
import requests
import os
import json
from datetime import datetime, timedelta

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

LANGUAGE_MAP = {
    'python': 'Python',
    'javascript': 'JavaScript',
    'typescript': 'TypeScript',
    'go': 'Go',
    'rust': 'Rust',
    'java': 'Java',
    'cpp': 'C++',
    'c': 'C',
    'csharp': 'C#',
    'php': 'PHP',
    'ruby': 'Ruby',
    'swift': 'Swift',
    'kotlin': 'Kotlin',
}

def get_trending_repos(language=None, since='daily', limit=10):
    """获取GitHub trending仓库"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Trending-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    # 使用GitHub搜索API获取trending
    query = 'stars:>1000'
    if language:
        query += f' language:{language}'
    
    # 计算日期范围
    if since == 'daily':
        date_range = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif since == 'weekly':
        date_range = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        date_range = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    query += f' created:>{date_range}'
    
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': limit
    }
    
    resp = requests.get('https://api.github.com/search/repositories', 
                       headers=headers, params=params)
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    
    data = resp.json()
    repos = []
    
    for item in data.get('items', [])[:limit]:
        repos.append({
            'name': item.get('name'),
            'full_name': item.get('full_name'),
            'description': item.get('description'),
            'stars': item.get('stargazers_count', 0),
            'forks': item.get('forks_count', 0),
            'language': item.get('language'),
            'url': item.get('html_url'),
            'created_at': item.get('created_at')[:10],
        })
    
    return repos

def main():
    import sys
    language = None
    since = 'daily'
    limit = 10
    
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--lang' and i + 1 < len(args):
            language = args[i + 1]
        elif arg == '--since' and i + 1 < len(args):
            since = args[i + 1]
        elif arg == '--limit' and i + 1 < len(args):
            limit = int(args[i + 1])
    
    print(f"🔍 获取 GitHub {since} trending (语言: {language or '全部'})...")
    
    repos = get_trending_repos(language, since, limit)
    
    if repos:
        print(f"\n📈 Top {len(repos)} Trending 仓库:")
        for i, repo in enumerate(repos, 1):
            lang = repo['language'] or 'N/A'
            print(f"\n{i}. {repo['full_name']}")
            print(f"   ⭐ {repo['stars']:,} | 🍴 {repo['forks']:,} | 💻 {lang}")
            if repo['description']:
                desc = repo['description'][:80] + '...' if len(repo['description']) > 80 else repo['description']
                print(f"   📝 {desc}")
            print(f"   🔗 {repo['url']}")
        
        if '--json' in args:
            print("\n" + json.dumps(repos, indent=2, ensure_ascii=False))
    else:
        print("未获取到数据")

if __name__ == "__main__":
    main()
