"""
评论系统模块
"""
import sqlite3
import os
from datetime import datetime

DB_FILE = 'comments.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        content TEXT NOT NULL,
        page TEXT DEFAULT 'home',
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def add_comment(name, content, page='home'):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('INSERT INTO comments (name, content, page) VALUES (?, ?, ?)',
                (name, content, page))
    conn.commit()
    conn.close()

def get_comments(page='home', limit=20):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.execute('SELECT * FROM comments WHERE page=? ORDER BY created DESC LIMIT ?',
                       (page, limit))
    comments = [dict(row) for row in cur.fetchall()]
    conn.close()
    return comments

# 初始化
if not os.path.exists(DB_FILE):
    init_db()
