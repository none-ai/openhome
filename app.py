import os
import time
import threading
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import yaml
import requests
import json
import feedparser
from io import BytesIO
from colorthief import ColorThief

# 速率限制配置
RATE_LIMIT_DICT = {}  # {ip: [timestamp1, timestamp2, ...]}
RATE_LIMIT_WINDOW = 60  # 时间窗口（秒）
RATE_LIMIT_MAX = 30   # 窗口内最大请求数

# 配置静态文件夹用于README图片
READMES_DIR = os.path.join(os.path.dirname(__file__), 'readmes')
app = Flask(__name__, static_folder=READMES_DIR, static_url_path='/static/readmes')

# 缓存配置
CACHE_DIR = os.path.join(os.path.dirname(__file__), '.cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'theme_colors.json')
CACHE_EXPIRE = 3600 * 24  # 缓存24小时

# GitHub数据缓存配置
GITHUB_CACHE_FILE = os.path.join(CACHE_DIR, 'github_data.json')
GITHUB_CACHE_EXPIRE = 3600  # GitHub数据1小时
GITHUB_CACHE_RETRY = 900    # 失败15分钟重试

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)

# 加载配置
def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()

# 速率限制检查
def check_rate_limit(ip):
    """检查IP是否超过速率限制，返回 (是否允许, 剩余请求数)"""
    now = time.time()
    if ip not in RATE_LIMIT_DICT:
        RATE_LIMIT_DICT[ip] = []

    # 清理过期的请求记录
    RATE_LIMIT_DICT[ip] = [t for t in RATE_LIMIT_DICT[ip] if now - t < RATE_LIMIT_WINDOW]

    # 检查是否超过限制
    if len(RATE_LIMIT_DICT[ip]) >= RATE_LIMIT_MAX:
        return False, 0

    # 记录本次请求
    RATE_LIMIT_DICT[ip].append(now)
    return True, RATE_LIMIT_MAX - len(RATE_LIMIT_DICT[ip])

# 缓存管理
def get_cached_colors(username):
    """从缓存获取主题色"""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        if username in cache:
            cached = cache[username]
            # 检查是否过期
            if time.time() - cached.get('timestamp', 0) < CACHE_EXPIRE:
                return cached.get('colors')
    except Exception as e:
        print(f"Error reading cache: {e}")
    return None

def save_colors_to_cache(username, colors):
    """保存主题色到缓存"""
    try:
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
        
        cache[username] = {
            'colors': colors,
            'timestamp': time.time()
        }
        
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

# 智能颜色调整
def adjust_color_saturation(rgb):
    """智能调整颜色饱和度，避免太淡或太鲜艳"""
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    
    # 计算亮度
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2
    
    # 计算饱和度
    if max_c == min_c:
        s = 0
    else:
        if l <= 0.5:
            s = (max_c - min_c) / (max_c + min_c)
        else:
            s = (max_c - min_c) / (2 - max_c - min_c)
    
    # 智能调整：目标饱和度在0.4-0.8之间
    target_s = max(0.4, min(0.8, s))
    
    if s == 0:
        # 无彩色，返回中灰色
        adjusted = [128, 128, 128]
    else:
        # 调整饱和度
        if s > target_s:
            # 太鲜艳，降低饱和度
            factor = target_s / s
            adjusted = [
                int(((1 - target_s) + (r - (1 - target_s)) * factor) * 255),
                int(((1 - target_s) + (g - (1 - target_s)) * factor) * 255),
                int(((1 - target_s) + (b - (1 - target_s)) * factor) * 255)
            ]
        else:
            # 太淡，提高饱和度
            factor = target_s / s if s > 0 else 1
            if l <= 0.5:
                adjusted = [
                    int((l + s * (1 - l)) * 255),
                    int((l + s * (1 - l) * g / max(r, g, b)) * 255),
                    int((l + s * (1 - l) * b / max(r, g, b)) * 255)
                ]
            else:
                adjusted = [
                    int((l + s * (1 - l) * r / max(r, g, b)) * 255),
                    int((l + s * (1 - l) * g / max(r, g, b)) * 255),
                    int((l + s * (1 - l) * b / max(r, g, b)) * 255)
                ]
    
    # 确保值在有效范围内
    adjusted = [max(0, min(255, x)) for x in adjusted]
    
    return adjusted

def adjust_color_lightness(rgb):
    """智能调整颜色亮度"""
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2  # 亮度
    
    # 目标亮度范围：0.3-0.7（避免太暗或太亮）
    target_l = max(0.3, min(0.7, l))
    
    if abs(l - target_l) > 0.1:
        # 调整亮度
        if l < target_l:
            factor = target_l / l if l > 0 else 1
        else:
            factor = target_l / l if l > 0 else 1
        
        adjusted = [int(x * factor * 255) for x in [r, g, b]]
    else:
        adjusted = list(rgb)
    
    # 确保值在有效范围内
    adjusted = [max(0, min(255, x)) for x in adjusted]
    return adjusted

def smart_adjust_color(rgb):
    """智能调整颜色（饱和度和亮度）"""
    # 先调整饱和度
    adjusted = adjust_color_saturation(rgb)
    # 再调整亮度
    adjusted = adjust_color_lightness(adjusted)
    return adjusted

# GitHub数据缓存管理
def get_github_cache(key):
    """从缓存获取GitHub数据"""
    if not os.path.exists(GITHUB_CACHE_FILE):
        return None, None
    try:
        with open(GITHUB_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        if key in cache:
            cached = cache[key]
            return cached.get('data'), cached.get('timestamp')
    except Exception as e:
        print(f"Error reading GitHub cache: {e}")
    return None, None

def save_github_cache(key, data, error=None):
    """保存GitHub数据到缓存"""
    try:
        cache = {}
        if os.path.exists(GITHUB_CACHE_FILE):
            with open(GITHUB_CACHE_FILE, 'r') as f:
                cache = json.load(f)
        cache[key] = {
            'data': data,
            'error': error,
            'timestamp': time.time()
        }
        with open(GITHUB_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving GitHub cache: {e}")

def is_cache_valid(timestamp, retry=False):
    """检查缓存是否有效"""
    if timestamp is None:
        return False
    expire = GITHUB_CACHE_RETRY if retry else GITHUB_CACHE_EXPIRE
    return time.time() - timestamp < expire

# GitHub API 获取用户信息
def get_github_user(username):
    # 先检查缓存
    cached_data, cached_time = get_github_cache(f'user_{username}')
    if cached_data and is_cache_valid(cached_time):
        print(f"Using cached user data for {username}")
        return cached_data
    
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            save_github_cache(f'user_{username}', data)
            return data
        else:
            if cached_data:
                print(f"Using stale cache for user {username}")
                return cached_data
    except Exception as e:
        print(f"Error fetching GitHub user: {e}")
        if cached_data and is_cache_valid(cached_time, retry=True):
            print(f"Using stale cache for user {username} (retry)")
            return cached_data
    return None

# GitHub API 获取用户仓库
def get_github_repos(username):
    # 先检查缓存
    cached_data, cached_time = get_github_cache(f'repos_{username}')
    if cached_data and is_cache_valid(cached_time):
        print(f"Using cached repos for {username}")
        return cached_data
    
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            repos = response.json()
            # 过滤掉fork的仓库，按star数量排序
            repos = [r for r in repos if not r.get('fork', False)]
            repos.sort(key=lambda x: x.get('stargazers_count', 0), reverse=True)
            result = repos[:12]
            save_github_cache(f'repos_{username}', result)
            return result
    except Exception as e:
        print(f"Error fetching GitHub repos: {e}")
    
    if cached_data and is_cache_valid(cached_time, retry=True):
        print(f"Using stale cache for repos {username}")
        return cached_data
    return []

# GitHub GraphQL API 获取贡献数据
def get_github_contributions(username):
    """使用GitHub GraphQL API获取用户的贡献数据"""
    # 先检查缓存
    cached_data, cached_time = get_github_cache(f'contrib_{username}')
    if cached_data and is_cache_valid(cached_time):
        print(f"Using cached contributions for {username}")
        return cached_data
    
    url = "https://api.github.com/graphql"
    token = os.environ.get('GITHUB_TOKEN', '')
    
    query = """
    {
      user(login: "%s") {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """ % username
    
    try:
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(url, json={"query": query}, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data'].get('user'):
                    calendar = data['data']['user']['contributionsCollection']['contributionCalendar']
                    result = {
                        'total': calendar.get('totalContributions', 0),
                        'weeks': calendar.get('weeks', [])
                    }
                    save_github_cache(f'contrib_{username}', result)
                    return result
    except Exception as e:
        print(f"Error fetching GitHub contributions: {e}")
    
    if cached_data and is_cache_valid(cached_time, retry=True):
        print(f"Using stale cache for contributions {username}")
        return cached_data
    return None

# 从头像提取主题色（带智能调整和缓存）
def get_theme_colors(avatar_url, username=''):
    """从头像图片提取主题色（智能调整 + 缓存）"""
    
    # 尝试从缓存获取
    if username:
        cached = get_cached_colors(username)
        if cached:
            print(f"Using cached colors for {username}")
            return cached
    
    try:
        # 下载头像
        response = requests.get(avatar_url, timeout=10)
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            color_thief = ColorThief(img_data)
            
            # 获取主色
            dominant_color = color_thief.get_color(quality=1)
            # 获取调色板
            palette = color_thief.get_palette(color_count=5, quality=1)
            
            # 转换RGB为HEX
            def rgb_to_hex(rgb):
                return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
            
            # 智能调整主色
            adjusted_primary = smart_adjust_color(dominant_color)
            adjusted_secondary = smart_adjust_color(palette[1]) if len(palette) > 1 else smart_adjust_color(palette[0])
            adjusted_tertiary = smart_adjust_color(palette[2]) if len(palette) > 2 else adjusted_secondary
            
            # 构建调色板
            palette = [rgb_to_hex(c) for c in [adjusted_primary, adjusted_secondary, adjusted_tertiary]]
            
            colors = {
                'primary': rgb_to_hex(adjusted_primary),
                'primary_rgb': adjusted_primary,
                'secondary': rgb_to_hex(adjusted_secondary),
                'tertiary': rgb_to_hex(adjusted_tertiary),
                'gradient_start': rgb_to_hex(adjusted_primary),
                'gradient_end': rgb_to_hex(adjusted_secondary),
                'palette': palette
            }
            
            # 保存到缓存
            if username:
                save_colors_to_cache(username, colors)
            
            return colors
            
    except Exception as e:
        print(f"Error extracting colors: {e}")
    
    # 默认颜色
    return {
        'primary': '#d97706',
        'secondary': '#f59e0b',
        'gradient_start': '#d97706',
        'gradient_end': '#dc2626',
        'primary_rgb': [217, 119, 6],
        'palette': ['#d97706', '#f59e0b', '#dc2626']
    }

# 解析RSS订阅
def parse_rss(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            return [
                {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200]
                }
                for entry in feed.entries[:5]
            ]
    except Exception as e:
        print(f"Error parsing RSS: {e}")
    return []

# 健康检查端点
@app.route('/api/health')
def health_check():
    """健康检查端点，返回服务状态"""
    try:
        # 检查配置是否加载
        config_ok = config is not None

        # 检查缓存目录
        cache_dir_ok = os.path.exists(CACHE_DIR)

        # 检查GitHub缓存
        github_cache_ok = os.path.exists(GITHUB_CACHE_FILE)

        # 检查主题色缓存
        colors_cache_ok = os.path.exists(CACHE_FILE)

        status = "healthy" if config_ok and cache_dir_ok else "degraded"

        return jsonify({
            'status': status,
            'services': {
                'config': 'ok' if config_ok else 'error',
                'cache_dir': 'ok' if cache_dir_ok else 'error',
                'github_cache': 'ok' if github_cache_ok else 'not_found',
                'colors_cache': 'ok' if colors_cache_ok else 'not_found'
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/')
def index():
    github_username = config.get('github_username', '')
    github_token = config.get('github_token', '')
    if github_token:
        os.environ['GITHUB_TOKEN'] = github_token
    
    user_info = get_github_user(github_username) if github_username else None
    repos = get_github_repos(github_username) if github_username else []
    contributions = get_github_contributions(github_username) if github_username else None
    
    # 同步README到本地（启动时同步一次）
    if repos:
        try:
            from readme_sync import sync_all_readmes, start_sync_scheduler
            import threading
            # 后台同步（不阻塞页面加载）
            def background_sync():
                import time
                time.sleep(5)  # 等待页面加载完成后再同步
                sync_all_readmes(repos)
                start_sync_scheduler(repos)
            threading.Thread(target=background_sync, daemon=True).start()
        except Exception as e:
            print(f"README同步出错: {e}")
    
    # 计算总star数
    total_stars = sum(r.get('stargazers_count', 0) for r in repos) if repos else 0
    
    # 提取主题色（带缓存）
    theme_colors = {'primary': '#d97706', 'secondary': '#f59e0b', 'gradient_start': '#d97706', 'gradient_end': '#dc2626', 'primary_rgb': [217, 119, 6], 'palette': ['#d97706', '#f59e0b', '#dc2626']}
    if user_info and user_info.get('avatar_url'):
        theme_colors = get_theme_colors(user_info['avatar_url'], github_username)
    
    # 加载配色方案
    saved_scheme = '0'
    scheme_file = os.path.join(os.path.dirname(__file__), '.cache', 'color_scheme.txt')
    if os.path.exists(scheme_file):
        try:
            with open(scheme_file, 'r') as f:
                saved_scheme = f.read().strip()
        except:
            pass
    
    # 获取RSS内容（带缓存）
    rss_cache_key = 'rss_feeds'
    cached_rss, rss_time = get_github_cache(rss_cache_key)
    if cached_rss and is_cache_valid(rss_time):
        rss_items = cached_rss
        print("Using cached RSS feeds")
    else:
        rss_items = []
        for feed in config.get('rss_feeds', []):
            items = parse_rss(feed.get('url', ''))
            for item in items:
                item['source'] = feed.get('name', '')
            rss_items.extend(items)
        if rss_items:
            save_github_cache(rss_cache_key, rss_items)
        elif cached_rss and is_cache_valid(rss_time, retry=True):
            rss_items = cached_rss
            print("Using stale RSS cache")
    
    return render_template('index.html',
                         config=config,
                         user_info=user_info,
                         repos=repos,
                         total_stars=total_stars,
                         rss_items=rss_items[:10],
                         theme_colors=theme_colors,
                         contributions=contributions,
                         saved_scheme=saved_scheme)

@app.route('/api/repos')
def api_repos():
    # 速率限制检查
    ip = request.remote_addr
    allowed, remaining = check_rate_limit(ip)
    if not allowed:
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded. Please try again later.'}), 429

    try:
        github_username = config.get('github_username', '')
        repos = get_github_repos(github_username) if github_username else []
        return jsonify({'status': 'ok', 'data': repos})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/rss')
def api_rss():
    # 速率限制检查
    ip = request.remote_addr
    allowed, remaining = check_rate_limit(ip)
    if not allowed:
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded. Please try again later.'}), 429

    try:
        rss_items = []
        for feed in config.get('rss_feeds', []):
            items = parse_rss(feed.get('url', ''))
            for item in items:
                item['source'] = feed.get('name', '')
            rss_items.extend(items)
        return jsonify({'status': 'ok', 'data': rss_items})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 清除缓存API
@app.route('/api/clear-cache')
def clear_cache():
    """清除主题色缓存"""
    # 速率限制检查
    ip = request.remote_addr
    allowed, remaining = check_rate_limit(ip)
    if not allowed:
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded. Please try again later.'}), 429

    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        return jsonify({'status': 'ok', 'message': 'Cache cleared'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/save-scheme', methods=['POST'])
def save_scheme():
    """保存配色方案到服务器"""
    # 速率限制检查
    ip = request.remote_addr
    allowed, remaining = check_rate_limit(ip)
    if not allowed:
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded. Please try again later.'}), 429

    try:
        scheme = request.json.get('scheme', '0')
        scheme_file = os.path.join(os.path.dirname(__file__), '.cache', 'color_scheme.txt')
        os.makedirs(os.path.dirname(scheme_file), exist_ok=True)
        with open(scheme_file, 'w') as f:
            f.write(str(scheme))
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/readme/<owner>/<repo>')
def get_readme(owner, repo):
    """获取项目的README（从本地缓存）"""
    # 导入README同步模块
    try:
        from readme_sync import get_local_readme, sync_readme
        
        # 尝试从本地获取
        local_data = get_local_readme(owner, repo)
        
        if local_data:
            return jsonify({
                'status': 'ok',
                'name': local_data.get('name', repo),
                'html': local_data.get('html', ''),
                'url': local_data.get('html_url', f'https://github.com/{owner}/{repo}')
            })
        
        # 本地没有则同步一次
        sync_readme(owner, repo)
        local_data = get_local_readme(owner, repo)
        
        if local_data:
            return jsonify({
                'status': 'ok',
                'name': local_data.get('name', repo),
                'html': local_data.get('html', ''),
                'url': local_data.get('html_url', f'https://github.com/{owner}/{repo}')
            })
        
        return jsonify({'status': 'error', 'message': 'README not found'})
    except Exception as e:
        print(f"Error getting README: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/rss/<path:url>')
def get_rss_content(url):
    """获取RSS文章内容（从缓存）"""
    import urllib.parse
    
    # 解码URL
    url = urllib.parse.unquote(url)
    
    try:
        from readme_sync import get_rss_cache, fetch_and_cache_rss
        
        # 尝试从缓存获取
        cached = get_rss_cache(url)
        if cached:
            return jsonify({
                'status': 'ok',
                'title': cached.get('title', ''),
                'html': cached.get('html', ''),
                'url': url
            })
        
        # 缓存没有则获取并缓存
        result = fetch_and_cache_rss(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# 统计API
@app.route("/api/stats")
def stats_api():
    from stats import get_stats, record_visit
    ip = request.remote_addr
    record_visit(ip)
    return jsonify({"status": "ok", "stats": get_stats()})

# 评论API
@app.route("/api/comments", methods=["GET", "POST"])
def comments_api():
    from comments import get_comments, add_comment
    if request.method == "POST":
        data = request.json
        add_comment(data.get("name", "匿名"), data.get("content", ""))
        return jsonify({"status": "ok"})
    comments = get_comments()
    return jsonify({"status": "ok", "comments": comments})

# 天气API - 使用 Open-Meteo（免费无需API Key）
@app.route('/api/weather')
def weather_api():
    """获取天气信息"""
    weather_config = config.get('weather', {})
    if not weather_config.get('enabled', False):
        return jsonify({'status': 'disabled'})
    
    city = weather_config.get('city', 'Shantou')
    location = weather_config.get('location', 'China')
    
    # 城市坐标映射
    city_coords = {
        'Shantou': (23.354, 116.681),
        'Beijing': (39.904, 116.407),
        'Shanghai': (31.230, 121.474),
        'Guangzhou': (23.129, 113.264),
        'Shenzhen': (22.543, 114.058),
        'Hangzhou': (30.274, 120.155),
        'Chengdu': (30.572, 104.066),
        'Xian': (34.341, 108.940),
    }
    
    coords = city_coords.get(city, (23.354, 116.681))  # 默认汕头
    
    try:
        # 使用 Open-Meteo API（免费无需API Key）
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': coords[0],
            'longitude': coords[1],
            'current': 'temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m',
            'timezone': 'auto'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            
            # 天气代码映射
            weather_codes = {
                0: {'desc': '晴', 'icon': '☀️'},
                1: {'desc': '晴间多云', 'icon': '⛅'},
                2: {'desc': '多云', 'icon': '☁️'},
                3: {'desc': '阴', 'icon': '☁️'},
                45: {'desc': '雾', 'icon': '🌫️'},
                48: {'desc': '雾', 'icon': '🌫️'},
                51: {'desc': '小雨', 'icon': '🌧️'},
                53: {'desc': '中雨', 'icon': '🌧️'},
                55: {'desc': '大雨', 'icon': '🌧️'},
                61: {'desc': '小雨', 'icon': '🌧️'},
                63: {'desc': '中雨', 'icon': '🌧️'},
                65: {'desc': '大雨', 'icon': '🌧️'},
                71: {'desc': '小雪', 'icon': '❄️'},
                73: {'desc': '中雪', 'icon': '❄️'},
                75: {'desc': '大雪', 'icon': '❄️'},
                80: {'desc': '阵雨', 'icon': '🌦️'},
                81: {'desc': '阵雨', 'icon': '🌦️'},
                82: {'desc': '强阵雨', 'icon': '⛈️'},
                95: {'desc': '雷暴', 'icon': '⛈️'},
                96: {'desc': '雷暴', 'icon': '⛈️'},
                99: {'desc': '雷暴', 'icon': '⛈️'},
            }
            
            code = current.get('weather_code', 0)
            weather_info = weather_codes.get(code, {'desc': '未知', 'icon': '🌡️'})
            
            return jsonify({
                'status': 'ok',
                'city': city,
                'temperature': current.get('temperature_2m', 0),
                'weather': weather_info['desc'],
                'icon': weather_info['icon'],
                'humidity': current.get('relative_humidity_2m', 0),
                'wind_speed': current.get('wind_speed_10m', 0),
            })
    except Exception as e:
        print(f"Error fetching weather: {e}")
    
    return jsonify({'status': 'error', 'message': str(e)})

# 获取语言统计
@app.route('/api/languages')
def languages_api():
    """获取仓库语言分布"""
    github_username = config.get('github_username', '')
    repos = get_github_repos(github_username) if github_username else []
    
    languages = {}
    for repo in repos:
        lang = repo.get('language', 'Other')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    
    # 转换为列表格式
    lang_list = [{'name': k, 'count': v} for k, v in languages.items()]
    lang_list.sort(key=lambda x: x['count'], reverse=True)
    
    return jsonify({'status': 'ok', 'languages': lang_list[:8]})

if __name__ == '__main__':
    port = config.get('port', 8004)
    print(f"🚀 启动Claude风格个人主页: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
