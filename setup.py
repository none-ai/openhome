#!/usr/bin/env python3
"""
OpenHome 一句话自动配置工具
Usage: python setup.py --github YOUR_GITHUB_USERNAME [--port 8004] [--name "Your Name"] [--title "Developer"]
"""

import argparse
import os
import sys


def generate_config(github_username: str, port: int = 8004, name: str = None, title: str = None, description: str = None, email: str = None):
    """Generate config.yaml from command line arguments"""
    
    if not github_username:
        print("Error: GitHub username is required", file=sys.stderr)
        sys.exit(1)
    
    # Use GitHub username as default name
    if not name:
        name = github_username
    if not title:
        title = "Developer"
    if not description:
        description = f"Hello, I'm {name}."
    
    config_content = f'''# OpenHome 配置文件
# 自动生成于 {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# GitHub用户名
github_username: "{github_username}"

# GitHub Token（可选，用于提高API调用限制）
# 如何生成: https://github.com/settings/tokens
# github_token: "ghp_xxxxxxxxxxxxxxxxxxxx"

# 端口号
port: {port}

# RSS订阅（可选）
# rss_feeds:
#   - url: "https://your-blog.com/feed.xml"
#     name: "我的博客"

# 个人简介
bio:
  name: "{name}"
  title: "{title}"
  description: "{description}"

# 社交链接
social:
  github: "{github_username}"
  {"email: \"" + email + "\"" if email else "# email: \"you@example.com\""}
  # twitter: "your-twitter"
  # blog: "https://your-blog.com"
'''
    
    return config_content


def main():
    parser = argparse.ArgumentParser(
        description="OpenHome 一句话自动配置工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python setup.py --github stlin256
  python setup.py --github stlin256 --port 9000
  python setup.py --github stlin256 --name "张三" --title "全栈工程师"
        """
    )
    
    parser.add_argument("--github", "-g", required=True, help="GitHub 用户名（必填）")
    parser.add_argument("--port", "-p", type=int, default=8004, help="服务端口（默认: 8004）")
    parser.add_argument("--name", "-n", help="你的名字（默认: GitHub用户名）")
    parser.add_argument("--title", "-t", help="标题/职位（默认: Developer）")
    parser.add_argument("--description", "-d", help="个人简介")
    parser.add_argument("--email", "-e", help="邮箱地址")
    parser.add_argument("--output", "-o", default="config.yaml", help="输出文件（默认: config.yaml）")
    parser.add_argument("--print", "-P", action="store_true", help="仅打印配置，不写入文件")
    
    args = parser.parse_args()
    
    config = generate_config(
        github_username=args.github,
        port=args.port,
        name=args.name,
        title=args.title,
        description=args.description,
        email=args.email
    )
    
    if args.print:
        print(config)
    else:
        # Check if config.yaml already exists
        if os.path.exists(args.output):
            response = input(f"{args.output} 已存在，是否覆盖？[y/N]: ")
            if response.lower() != 'y':
                print("已取消")
                sys.exit(0)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(config)
        
        print(f"✅ 配置已生成: {args.output}")
        print(f"   运行: python app.py")
        print(f"   访问: http://localhost:{args.port}")


if __name__ == "__main__":
    main()
