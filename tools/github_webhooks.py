#!/usr/bin/env python3
"""
GitHub Webhook 管理工具
用于创建和管理GitHub Webhooks
"""
import requests
import os
import json
import sys

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def get_hooks(owner, repo):
    """获取仓库webhooks"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Webhook-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    resp = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/hooks',
        headers=headers
    )
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    
    return resp.json()

def create_hook(owner, repo, config, events=None, active=True):
    """创建webhook"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Webhook-Tool',
        'Content-Type': 'application/json'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    data = {
        'config': config,
        'events': events or ['push'],
        'active': active
    }
    
    resp = requests.post(
        f'https://api.github.com/repos/{owner}/{repo}/hooks',
        headers=headers, json=data
    )
    
    if resp.status_code != 201:
        print(f"Error: {resp.status_code} - {resp.text}")
        return None
    
    return resp.json()

def delete_hook(owner, repo, hook_id):
    """删除webhook"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Webhook-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    resp = requests.delete(
        f'https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}',
        headers=headers
    )
    
    return resp.status_code == 204

def ping_hook(owner, repo, hook_id):
    """测试webhook"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenHome-Webhook-Tool'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    resp = requests.post(
        f'https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}/pings',
        headers=headers
    )
    
    return resp.status_code == 204

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python github_webhooks.py <owner/repo> list")
        print("  python github_webhooks.py <owner/repo> create <url> [--events push,issues]")
        print("  python github_webhooks.py <owner/repo> delete <hook_id>")
        print("  python github_webhooks.py <owner/repo> ping <hook_id>")
        return
    
    parts = sys.argv[1].split('/')
    if len(parts) != 2:
        print("错误: 请使用 owner/repo 格式")
        return
    
    owner, repo = parts
    command = sys.argv[2] if len(sys.argv) > 2 else 'list'
    
    if command == 'list':
        print(f"🔗 获取 {owner}/{repo} Webhooks...")
        hooks = get_hooks(owner, repo)
        
        if hooks:
            print(f"\n找到 {len(hooks)} 个 Webhooks:")
            for hook in hooks:
                active = "✅ 启用" if hook.get('active') else "❌ 禁用"
                print(f"\nID: {hook['id']}")
                print(f"  类型: {hook['type']}")
                print(f"  状态: {active}")
                print(f"  事件: {', '.join(hook['events'])}")
                if hook.get('config', {}).get('url'):
                    print(f"  URL: {hook['config']['url']}")
                print(f"  创建时间: {hook['created_at']}")
        else:
            print("没有 Webhooks")
    
    elif command == 'create':
        if len(sys.argv) < 4:
            print("请指定 webhook URL")
            return
        
        url = sys.argv[3]
        events = ['push']
        
        for i, arg in enumerate(sys.argv):
            if arg == '--events' and i + 1 < len(sys.argv):
                events = sys.argv[i + 1].split(',')
        
        print(f"🔗 创建 Webhook: {url}")
        config = {'url': url, 'content_type': 'json'}
        
        result = create_hook(owner, repo, config, events)
        if result:
            print(f"✅ Webhook 创建成功!")
            print(f"  ID: {result['id']}")
            print(f"  事件: {', '.join(result['events'])}")
    
    elif command == 'delete':
        if len(sys.argv) < 4:
            print("请指定 webhook ID")
            return
        
        hook_id = sys.argv[3]
        
        confirm = input(f"确认删除 webhook {hook_id}? (y/n): ")
        if confirm.lower() == 'y':
            if delete_hook(owner, repo, hook_id):
                print(f"✅ Webhook 已删除")
            else:
                print(f"❌ 删除失败")
    
    elif command == 'ping':
        if len(sys.argv) < 4:
            print("请指定 webhook ID")
            return
        
        hook_id = sys.argv[3]
        
        if ping_hook(owner, repo, hook_id):
            print(f"✅ 测试ping已发送")
        else:
            print(f"❌ 发送失败")

if __name__ == "__main__":
    main()
