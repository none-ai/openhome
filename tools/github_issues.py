#!/usr/bin/env python3
"""
GitHub Issue 管理工具
用于创建、查看和管理GitHub issues
"""
import requests
import os
import json
import sys

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def get_issues(owner, repo, state='open', limit=10):
    """获取仓库issues"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Issue-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    params = {
        'state': state,
        'per_page': limit,
        'sort': 'updated',
        'direction': 'desc'
    }
    
    resp = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/issues',
        headers=headers, params=params
    )
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    
    issues = []
    for item in resp.json():
        # 排除pull requests
        if 'pull_request' not in item:
            issues.append({
                'number': item.get('number'),
                'title': item.get('title'),
                'state': item.get('state'),
                'labels': [l['name'] for l in item.get('labels', [])],
                'author': item.get('user', {}).get('login'),
                'comments': item.get('comments'),
                'created_at': item.get('created_at')[:10],
                'updated_at': item.get('updated_at')[:10],
                'url': item.get('html_url'),
            })
    
    return issues

def create_issue(owner, repo, title, body='', labels=None):
    """创建issue"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Issue-Tool',
        'Content-Type': 'application/json'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    data = {
        'title': title,
        'body': body
    }
    if labels:
        data['labels'] = labels
    
    resp = requests.post(
        f'https://api.github.com/repos/{owner}/{repo}/issues',
        headers=headers, json=data
    )
    
    if resp.status_code != 201:
        print(f"Error: {resp.status_code} - {resp.text}")
        return None
    
    return resp.json()

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python github_issues.py <owner/repo> [list|create|view]")
        print("  python github_issues.py none-ai/openhome list --state open")
        print("  python github_issues.py none-ai/openhome create \"标题\" --body \"内容\"")
        print("  python github_issues.py none-ai/openhome view <number>")
        return
    
    parts = sys.argv[1].split('/')
    if len(parts) != 2:
        print("错误: 请使用 owner/repo 格式")
        return
    
    owner, repo = parts
    command = sys.argv[2] if len(sys.argv) > 2 else 'list'
    
    if command == 'list':
        state = 'open'
        limit = 10
        
        for i, arg in enumerate(sys.argv):
            if arg == '--state' and i + 1 < len(sys.argv):
                state = sys.argv[i + 1]
            if arg == '--limit' and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
        
        print(f"📋 获取 {owner}/{repo} issues (状态: {state})...")
        issues = get_issues(owner, repo, state, limit)
        
        if issues:
            print(f"\n找到 {len(issues)} 个 issues:")
            for issue in issues:
                labels = f"[{', '.join(issue['labels'])}]" if issue['labels'] else ""
                print(f"\n#{issue['number']} {issue['title']}")
                print(f"   状态: {issue['state']} | 作者: {issue['author']} | 评论: {issue['comments']}")
                print(f"   标签: {labels}")
                print(f"   创建: {issue['created_at']} | 更新: {issue['updated_at']}")
        else:
            print("没有找到 issues")
    
    elif command == 'create':
        title = sys.argv[3] if len(sys.argv) > 3 else "新Issue"
        body = ""
        labels = []
        
        for i, arg in enumerate(sys.argv):
            if arg == '--body' and i + 1 < len(sys.argv):
                body = sys.argv[i + 1]
            if arg == '--labels' and i + 1 < len(sys.argv):
                labels = sys.argv[i + 1].split(',')
        
        print(f"📝 创建 issue: {title}")
        result = create_issue(owner, repo, title, body, labels)
        if result:
            print(f"✅ Issue 创建成功: {result.get('html_url')}")
    
    elif command == 'view':
        if len(sys.argv) < 4:
            print("请指定 issue 编号")
            return
        
        number = sys.argv[3]
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OpenHome-Issue-Tool'
        }
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        resp = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/issues/{number}',
            headers=headers
        )
        
        if resp.status_code == 200:
            issue = resp.json()
            print(f"\n#{issue['number']}: {issue['title']}")
            print(f"状态: {issue['state']}")
            print(f"作者: {issue['user']['login']}")
            print(f"标签: {', '.join([l['name'] for l in issue['labels']])}")
            print(f"\n内容:\n{issue['body']}")
        else:
            print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    main()
