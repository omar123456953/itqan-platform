import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_NAME = "itqan.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جدول المشرفين مع تخزين كلمة المرور المشفرة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # جدول المحتوى التعليمي / المواد
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            university TEXT,
            link TEXT
        )
    ''')

    # إنشاء حساب أدمن افتراضي مشفر إذا لم يكن موجوداً
    cursor.execute('SELECT * FROM admins WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # كلمة المرور الافتراضية هنا هي Admin@2026 (تُخزن مشفرة تماماً)
        default_hash = generate_password_hash("Admin@2026")
        cursor.execute(
            'INSERT INTO admins (username, password_hash) VALUES (?, ?)',
            ('admin', default_hash)
        )
    
    conn.commit()
    conn.close()

if name == "main":
    init_db()
