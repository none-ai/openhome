#!/usr/bin/env python3
"""
GitHub 仓库搜索工具
使用GitHub API搜索仓库和代码
"""
import requests
import os
import json
import sys

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def search_repos(query, language=None, sort='stars', order='desc', limit=10):
    """搜索仓库"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Search-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    search_query = query
    if language:
        search_query += f' language:{language}'
    
    params = {
        'q': search_query,
        'sort': sort,
        'order': order,
        'per_page': limit
    }
    
    resp = requests.get(
        'https://api.github.com/search/repositories',
        headers=headers, params=params
    )
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    
    return resp.json().get('items', [])[:limit]

def search_code(query, repo=None, limit=10):
    """搜索代码"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Search-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    params = {
        'q': query,
        'per_page': limit
    }
    if repo:
        params['q'] += f' repo:{repo}'
    
    resp = requests.get(
        'https://api.github.com/search/code',
        headers=headers, params=params
    )
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    
    return resp.json().get('items', [])[:limit]

def search_users(query, limit=10):
    """搜索用户"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Search-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    params = {
        'q': query,
        'per_page': limit
    }
    
    resp = requests.get(
        'https://api.github.com/search/users',
        headers=headers, params=params
    )
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    
    return resp.json().get('items', [])[:limit]

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python github_search.py repos <关键词> [--lang Python] [--sort stars]")
        print("  python github_search.py code <关键词> [--repo owner/repo]")
        print("  python github_search.py users <关键词>")
        print("  python github_search.py repos agent framework --lang python")
        return
    
    search_type = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not query:
        print("请输入搜索关键词")
        return
    
    # 解析额外参数
    language = None
    repo = None
    sort = 'stars'
    limit = 10
    
    for i, arg in enumerate(sys.argv):
        if arg == '--lang' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
        if arg == '--repo' and i + 1 < len(sys.argv):
            repo = sys.argv[i + 1]
        if arg == '--sort' and i + 1 < len(sys.argv):
            sort = sys.argv[i + 1]
        if arg == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
    
    if search_type == 'repos':
        print(f"🔍 搜索仓库: {query}" + (f" (语言: {language})" if language else ""))
        results = search_repos(query, language, sort, 'desc', limit)
        
        if results:
            print(f"\n找到 {len(results)} 个仓库:")
            for i, item in enumerate(results, 1):
                print(f"\n{i}. {item['full_name']}")
                print(f"   ⭐ {item['stargazers_count']:,} | 🍴 {item['forks_count']:,} | 💻 {item['language'] or 'N/A'}")
                if item.get('description'):
                    desc = item['description'][:100] + '...' if len(item['description']) > 100 else item['description']
                    print(f"   📝 {desc}")
                print(f"   🔗 {item['html_url']}")
        else:
            print("未找到结果")
    
    elif search_type == 'code':
        print(f"🔍 搜索代码: {query}" + (f" (仓库: {repo})" if repo else ""))
        results = search_code(query, repo, limit)
        
        if results:
            print(f"\n找到 {len(results)} 条代码:")
            for i, item in enumerate(results, 1):
                print(f"\n{i}. {item['repository']['full_name']} - {item['path']}")
                print(f"   📄 {item['name']}")
                print(f"   🔗 {item['html_url']}")
        else:
            print("未找到结果")
    
    elif search_type == 'users':
        print(f"🔍 搜索用户: {query}")
        results = search_users(query, limit)
        
        if results:
            print(f"\n找到 {len(results)} 个用户:")
            for i, item in enumerate(results, 1):
                print(f"\n{i}. {item['login']}")
                print(f"   🔗 {item['html_url']}")
        else:
            print("未找到结果")

if __name__ == "__main__":
    main()
