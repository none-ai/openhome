"""
访客统计模块
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = 'stats.db'

def init_stats_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        page TEXT DEFAULT 'home',
        referer TEXT,
        user_agent TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def record_visit(ip, page='home', referer='', user_agent=''):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('INSERT INTO visits (ip, page, referer, user_agent) VALUES (?, ?, ?, ?)',
                (ip, page, referer, user_agent))
    conn.commit()
    conn.close()

def get_stats(days=7):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    
    # 总访问量
    total = conn.execute('SELECT COUNT(*) FROM visits').fetchone()[0]
    
    # 今日访问
    today = conn.execute('SELECT COUNT(*) FROM visits WHERE date(created) = date("now")').fetchone()[0]
    
    # 昨日访问
    yesterday = conn.execute('SELECT COUNT(*) FROM visits WHERE date(created) = date("now", "-1 day")').fetchone()[0]
    
    # 独立IP
    unique_ip = conn.execute('SELECT COUNT(DISTINCT ip) FROM visits').fetchone()[0]
    
    # 最近7天
    week_data = []
    for i in range(7):
        date_str = f'date("now", "-{i} day")'
        count = conn.execute(f'SELECT COUNT(*) FROM visits WHERE date(created) = {date_str}').fetchone()[0]
        week_data.append(count)
    
    conn.close()
    return {
        "total": total,
        "today": today,
        "yesterday": yesterday,
        "unique_ip": unique_ip,
        "week": week_data
    }

if not os.path.exists(DB_FILE):
    init_stats_db()
