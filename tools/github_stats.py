#!/usr/bin/env python3
"""
GitHub 仓库统计工具
用于获取指定仓库的统计数据
"""
import requests
import os
import json
from datetime import datetime

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def get_repo_stats(owner, repo):
    """获取仓库统计信息"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    base_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    # 获取仓库信息
    resp = requests.get(f'{base_url}', headers=headers)
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return None
    
    data = resp.json()
    
    stats = {
        'name': data.get('name'),
        'full_name': data.get('full_name'),
        'description': data.get('description'),
        'stars': data.get('stargazers_count', 0),
        'forks': data.get('forks_count', 0),
        'watchers': data.get('watchers_count', 0),
        'open_issues': data.get('open_issues_count', 0),
        'language': data.get('language'),
        'license': data.get('license', {}).get('name') if data.get('license') else None,
        'created_at': data.get('created_at'),
        'updated_at': data.get('updated_at'),
        'pushed_at': data.get('pushed_at'),
        'subscribers_count': data.get('subscribers_count', 0),
    }
    
    return stats

def main():
    import sys
    if len(sys.argv) < 2:
        # 默认获取 openhome 仓库统计
        owner, repo = 'none-ai', 'openhome'
    else:
        owner, repo = sys.argv[1].split('/')
    
    stats = get_repo_stats(owner, repo)
    if stats:
        print(f"\n📊 {stats['full_name']} 统计信息")
        print(f"  ⭐ Stars: {stats['stars']:,}")
        print(f"  🍴 Forks: {stats['forks']:,}")
        print(f"  👁️ Watchers: {stats['watchers']:,}")
        print(f"  📝 Issues: {stats['open_issues']:,}")
        print(f"  💻 Language: {stats['language']}")
        print(f"  📜 License: {stats['license']}")
        print(f"  📅 创建于: {stats['created_at'][:10]}")
        print(f"  🔄 最后更新: {stats['updated_at'][:10]}")
        
        # 输出 JSON 格式
        if '--json' in sys.argv:
            print("\n" + json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
