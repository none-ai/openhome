#!/usr/bin/env python3
"""
GitHub PR 管理工具
用于查看和管理Pull Requests
"""
import requests
import os
import json
import sys

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def get_pull_requests(owner, repo, state='open'):
    """获取仓库PRs"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-PR-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    params = {
        'state': state,
        'sort': 'updated',
        'direction': 'desc'
    }
    
    resp = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/pulls',
        headers=headers, params=params
    )
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    
    prs = []
    for item in resp.json():
        prs.append({
            'number': item.get('number'),
            'title': item.get('title'),
            'state': item.get('state'),
            'draft': item.get('draft', False),
            'author': item.get('user', {}).get('login'),
            'base': item.get('base', {}).get('ref'),
            'head': item.get('head', {}).get('ref'),
            'comments': item.get('comments'),
            'commits': item.get('commits'),
            'additions': item.get('additions', 0),
            'deletions': item.get('deletions', 0),
            'changed_files': item.get('changed_files', 0),
            'created_at': item.get('created_at')[:10],
            'updated_at': item.get('updated_at')[:10],
            'url': item.get('html_url'),
            'mergeable': item.get('mergeable'),
        })
    
    return prs

def get_pr_reviews(owner, repo, pr_number):
    """获取PR的reviews"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-PR-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    resp = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews',
        headers=headers
    )
    
    if resp.status_code != 200:
        return []
    
    reviews = []
    for item in resp.json():
        reviews.append({
            'user': item.get('user', {}).get('login'),
            'state': item.get('state'),
            'body': item.get('body', '')[:200],
            'submitted_at': item.get('submitted_at', '')[:10],
        })
    
    return reviews

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python github_prs.py <owner/repo> [list|view]")
        print("  python github_prs.py none-ai/openhome list --state all")
        print("  python github_prs.py none-ai/openhome view <number>")
        return
    
    parts = sys.argv[1].split('/')
    if len(parts) != 2:
        print("错误: 请使用 owner/repo 格式")
        return
    
    owner, repo = parts
    command = sys.argv[2] if len(sys.argv) > 2 else 'list'
    
    if command == 'list':
        state = 'open'
        
        for i, arg in enumerate(sys.argv):
            if arg == '--state' and i + 1 < len(sys.argv):
                state = sys.argv[i + 1]
        
        print(f"🔀 获取 {owner}/{repo} Pull Requests (状态: {state})...")
        prs = get_pull_requests(owner, repo, state)
        
        if prs:
            print(f"\n找到 {len(prs)} 个 Pull Requests:")
            for pr in prs:
                draft = "📝 草稿" if pr['draft'] else "✅"
                merge_status = "✅ 可合并" if pr.get('mergeable') else "❌ 不可合并"
                print(f"\n#{pr['number']} {draft} {pr['title']}")
                print(f"   作者: {pr['author']} | 状态: {pr['state']}")
                print(f"   {pr['head']} → {pr['base']}")
                print(f"   提交: {pr['commits']} | 评论: {pr['comments']} | 文件: {pr['changed_files']}")
                print(f"   创建: {pr['created_at']} | 更新: {pr['updated_at']}")
                print(f"   {merge_status}")
        else:
            print("没有找到 Pull Requests")
    
    elif command == 'view':
        if len(sys.argv) < 4:
            print("请指定 PR 编号")
            return
        
        number = sys.argv[3]
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OpenHome-PR-Tool'
        }
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        resp = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}',
            headers=headers
        )
        
        if resp.status_code == 200:
            pr = resp.json()
            print(f"\n#{pr['number']}: {pr['title']}")
            print(f"状态: {pr['state']} | 草稿: {pr['draft']}")
            print(f"作者: {pr['user']['login']}")
            print(f"分支: {pr['head']['ref']} → {pr['base']['ref']}")
            print(f"\n内容:\n{pr['body']}")
            
            # 获取reviews
            print(f"\n📋 Reviews:")
            reviews = get_pr_reviews(owner, repo, number)
            for review in reviews:
                print(f"  - {review['user']}: {review['state']} ({review['submitted_at']})")
        else:
            print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    main()
