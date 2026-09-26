import os
import sqlite3

BASE_DIR = os.getcwd()
DB_NAME = os.path.join(BASE_DIR, 'itqan.db')

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # 1. جداول النظام الأساسية
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        is_admin INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS universities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        logo TEXT,
        desc TEXT,
        logo_img TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS instructors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        bio TEXT,
        avatar_img TEXT,
        banner_img TEXT,
        rating REAL DEFAULT 5.0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uni_id INTEGER,
        instructor_id INTEGER DEFAULT 1,
        title TEXT,
        code TEXT DEFAULT '',
        desc TEXT, 
        price REAL,
        old_price REAL DEFAULT 0,
        mid_price REAL DEFAULT 0,
        mid_old_price REAL DEFAULT 0,
        final_price REAL DEFAULT 0,
        final_old_price REAL DEFAULT 0,
        cover_img TEXT,
        faculty TEXT DEFAULT 'كلية الهندسة',
        target_audience TEXT DEFAULT 'طلاب وطالبات'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        video_filename TEXT,
        pdf_filename TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER,
        package_type TEXT DEFAULT 'full',
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, course_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bank_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank_name TEXT,
        beneficiary TEXT,
        account_num TEXT,
        iban TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS semester_works (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        faculty TEXT,
        desc TEXT,
        file_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # تحديثات الحقول والأعمدة
    alter_columns = [
        'ALTER TABLE universities ADD COLUMN logo_img TEXT',
        'ALTER TABLE courses ADD COLUMN code TEXT DEFAULT ""',
        'ALTER TABLE courses ADD COLUMN instructor_id INTEGER DEFAULT 1',
        'ALTER TABLE courses ADD COLUMN old_price REAL DEFAULT 0',
        'ALTER TABLE courses ADD COLUMN mid_price REAL DEFAULT 0',
        'ALTER TABLE courses ADD COLUMN mid_old_price REAL DEFAULT 0',
        'ALTER TABLE courses ADD COLUMN final_price REAL DEFAULT 0',
        'ALTER TABLE courses ADD COLUMN final_old_price REAL DEFAULT 0',
        'ALTER TABLE courses ADD COLUMN cover_img TEXT',
        'ALTER TABLE courses ADD COLUMN faculty TEXT DEFAULT "كلية الهندسة"',
        'ALTER TABLE courses ADD COLUMN target_audience TEXT DEFAULT "طلاب وطالبات"',
        'ALTER TABLE lessons ADD COLUMN pdf_filename TEXT',
        'ALTER TABLE lessons ADD COLUMN video_filename TEXT',
        'ALTER TABLE enrollments ADD COLUMN status TEXT DEFAULT "approved"'
    ]

    for alter_sql in alter_columns:
        try:
            c.execute(alter_sql)
        except Exception:
            pass

    # البيانات الابتدائية الافتراضية
    c.execute('SELECT COUNT(*) FROM instructors')
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO instructors (name, bio, rating) 
                     VALUES ('أكاديمية إتقان التعليمية', 'نخبة من الأكاديميين والمحاضرين المتخصصين في تبسيط وشرح المقررات الجامعية وتلخيصها ومتابعة الطلاب لتحقيق الامتياز A+.', 5.0)''')
    else:
        c.execute('''UPDATE instructors SET name='أكاديمية إتقان التعليمية' WHERE id=1''')

    c.execute('SELECT COUNT(*) FROM bank_accounts')
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO bank_accounts (bank_name, beneficiary, account_num, iban) 
                     VALUES ('بنك الجزيرة', 'عدنان محمد سعيد عبدالكريم', '003381468188001', 'SA2160100003381468188001')''')

    c.execute('SELECT COUNT(*) FROM universities')
    if c.fetchone()[0] == 0:
        unis = [
            ("جامعة الملك خالد", "⛰️", "شروحات واختبارات جامعة الملك خالد"),
            ("جامعة الملك عبدالعزيز", "🏢", "شروحات ومقررات جامعة الملك عبدالعزيز"),
            ("جامعة أم القرى", "🕋", "شروحات ومقررات جامعة أم القرى"),
            ("جامعة جدة", "🏛️", "مقررات وملخصات جامعة جدة"),
            ("جامعة الملك سعود", "👑", "مقررات جامعة الملك سعود")
        ]
        for name, logo, desc in unis:
            c.execute('INSERT INTO universities (name, logo, desc) VALUES (?, ?, ?)', (name, logo, desc))

    conn.commit()
    conn.close()
