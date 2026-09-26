import os
import time
from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory
from werkzeug.utils import secure_filename
from database import get_db, init_db

app = Flask(__name__)

# ================= إعدادات الحماية والأمان =================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'itqan-bravo-fixed-admin-2026-safe-key')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# ================= بيانات لوحة الإدارة =================
ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASS', '123')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db()

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def home():
    conn = get_db()
    unis = conn.execute('SELECT * FROM universities').fetchall()
    courses = conn.execute('''
        SELECT c.*, u.name as uni_name 
        FROM courses c 
        LEFT JOIN universities u ON c.uni_id=u.id 
        ORDER BY c.id DESC
    ''').fetchall()
    
    uni_cards = []
    for idx, u in enumerate(unis):
        c_count = conn.execute('SELECT COUNT(*) FROM courses WHERE uni_id=?', (u['id'],)).fetchone()[0]
        logo_img = u['logo_img'] if 'logo_img' in u.keys() else None
        logo_html = f'<img src="/uploads/{logo_img}" class="w-14 h-14 object-contain">' if logo_img else f'<span class="text-3xl">{u["logo"] or "🏛️"}</span>'
        
        card_bg = "bg-[#1E293B] text-white" if idx % 2 == 1 else "bg-[#F4F6F8] text-slate-900"
        text_title = "text-white" if idx % 2 == 1 else "text-slate-900"
        text_sub = "text-slate-300" if idx % 2 == 1 else "text-slate-500"
        badge_bg = "bg-white text-slate-900"

        uni_cards.append(f'''
        <a href="/uni/{u['id']}" class="relative block {card_bg} rounded-[36px] pt-12 pb-6 px-6 text-center shadow-md transition hover:scale-[1.01]">
            <div class="absolute -top-7 left-1/2 -translate-x-1/2 w-16 h-16 {badge_bg} rounded-full shadow-md flex items-center justify-center overflow-hidden border-4 border-white">
                {logo_html}
            </div>
            <h3 class="font-black text-base mb-1 {text_title}">{u['name']}</h3>
            <p class="text-xs font-bold {text_sub}">{c_count} مادة تعليمية &lsaquo;</p>
        </a>''')

    course_cards = []
    for c in courses:
        if c['cover_img']:
            cover_tag = f'<img src="/uploads/{c["cover_img"]}" class="w-full h-52 object-cover rounded-[32px]">'
        else:
            cover_tag = '''
            <div class="w-full h-52 bg-gradient-to-b from-[#38bdf8] to-[#60a5fa] rounded-[32px] flex items-center justify-center relative overflow-hidden">
                <div class="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center text-4xl shadow-inner">🎯</div>
            </div>'''

        uni_name = c['uni_name'] or 'جامعة الملك خالد'
        code_tag = f"<span class='text-xs font-bold text-slate-400 mr-2'>{c['code']}</span>" if ('code' in c.keys() and c['code']) else ""
        faculty_name = c['faculty'] if 'faculty' in c.keys() else 'كلية الهندسة'
        
        course_cards.append(f'''
        <div class="bg-white rounded-[36px] border border-slate-100 p-2 shadow-xs flex flex-col justify-between mb-6">
            <div class="relative">
                {cover_tag}
                <div class="absolute top-4 left-4 w-10 h-10 bg-white/95 backdrop-blur-xs rounded-full flex items-center justify-center text-slate-700 shadow-sm cursor-pointer">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
                </div>
            </div>
            
            <div class="p-4 pt-3">
                <div class="flex items-center gap-1.5 mb-2 flex-wrap">
                    <span class="text-[11px] font-black text-slate-900 bg-[#FDE68A] px-3 py-1 rounded-full">{uni_name}</span>
                    <span class="text-[11px] font-black text-slate-900 bg-[#5EEAD4] px-3 py-1 rounded-full">{faculty_name}</span>
                </div>
                
                <h3 class="font-black text-lg text-slate-900 mb-1">{c['title']} {code_tag}</h3>
                <p class="text-xs text-slate-500 line-clamp-2 mb-4 leading-relaxed">{c['desc']}</p>
                
                <div class="flex items-center justify-between pt-3 border-t border-slate-100">
                    <div class="flex items-center gap-1 text-xs text-slate-600 font-bold">
                        <span>🎓 أكاديمية إتقان</span>
                    </div>
                    <a href="/course/{c['id']}" class="bravo-teal-btn text-xs font-black px-6 py-2 rounded-full text-slate-900">
                        {c['price']} ر.س
                    </a>
                </div>
            </div>
        </div>''')

    conn.close()

    content = f'''
    <div class="max-w-md mx-auto px-4 py-8 space-y-6">
        <div class="text-center">
            <span class="inline-block bg-amber-50 text-amber-900 text-xs font-bold px-4 py-1.5 rounded-full border border-amber-200 mb-4">
                تأسست لخدمتكم منذ 2023 🏆
            </span>
            <h1 class="text-2xl font-black text-slate-900">الخيار الأول للطالب الجامعي</h1>
        </div>

        <div class="bg-gradient-to-r from-teal-50 to-sky-50 p-4 rounded-3xl border border-teal-200 flex items-center justify-between shadow-xs">
            <div>
                <h3 class="font-black text-sm text-teal-950">الأعمال الفصلية والواجبات</h3>
                <p class="text-[11px] text-teal-700 font-bold">تصفح التكاليف والأنشطة والملازم الفصلية</p>
            </div>
            <a href="/semester-works" class="bravo-teal-btn px-4 py-2 rounded-2xl text-xs font-black text-slate-900">
                عرض الأعمال &lsaquo;
            </a>
        </div>

        <div id="unis" class="space-y-10 pt-4">
            <h2 class="text-lg font-black text-slate-900 mb-4 text-center">الجامعات المعتمدة</h2>
            {''.join(uni_cards)}
        </div>

        <div class="space-y-3 pt-6">
            <a href="#courses" class="bravo-teal-btn w-full block text-center py-3.5 rounded-full font-black text-slate-900 text-sm">كل المواد &lsaquo;</a>
            <a href="https://wa.me/966593521664" target="_blank" class="bravo-yellow-btn w-full block text-center py-3.5 rounded-full font-black text-slate-900 text-sm">عن إتقان &lsaquo;</a>
        </div>

        <div id="courses" class="space-y-6 pt-6">
            <h2 class="text-lg font-black text-slate-900 mb-2">أبرز المقررات والملخصات</h2>
            {''.join(course_cards) if course_cards else '<p class="text-center text-xs text-slate-400 py-8">لا توجد مواد مضافة بعد</p>'}
        </div>
    </div>
    '''
    return render_template('base.html', content=content)

@app.route('/semester-works')
def semester_works():
    conn = get_db()
    works = conn.execute('SELECT * FROM semester_works ORDER BY id DESC').fetchall()
    conn.close()

    cards = []
    for w in works:
        file_btn = f'<a href="/uploads/{w["file_name"]}" target="_blank" class="bravo-teal-btn text-xs font-black px-4 py-1.5 rounded-full text-slate-900">تحميل المرفق 📥</a>' if w['file_name'] else ''
        cards.append(f'''
        <div class="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex flex-col justify-between">
            <div>
                <span class="text-[10px] font-black bg-amber-100 text-amber-900 px-3 py-1 rounded-full mb-2 inline-block">{w['faculty']}</span>
                <h3 class="font-black text-base text-slate-900 mb-1">{w['title']}</h3>
                <p class="text-xs text-slate-500 mb-4 leading-relaxed">{w['desc']}</p>
            </div>
            <div class="flex items-center justify-between pt-3 border-t border-slate-100">
                <span class="text-[11px] text-slate-400 font-bold">{w['created_at'][:10]}</span>
                {file_btn}
            </div>
        </div>''')

    content = f'''
    <div class="max-w-md mx-auto px-4 py-8">
        <div class="text-center mb-6">
            <span class="text-3xl">📝</span>
            <h1 class="text-2xl font-black text-slate-900 mt-2">الأعمال الفصلية والتكاليف</h1>
            <p class="text-xs text-slate-400 mt-1">واجبات، أنشطة، وملفات المشاريع الفصلية المعتمدة</p>
        </div>

        <div class="space-y-4">
            {''.join(cards) if cards else '<div class="bg-slate-50 p-8 rounded-3xl text-center text-xs text-slate-400">لا توجد أعمال فصلية منشورة حالياً</div>'}
        </div>
    </div>
    '''
    return render_template('base.html', content=content)

@app.route('/uni/<int:uni_id>')
def uni_detail(uni_id):
    conn = get_db()
    uni = conn.execute('SELECT * FROM universities WHERE id=?', (uni_id,)).fetchone()
    courses = conn.execute('SELECT * FROM courses WHERE uni_id=?', (uni_id,)).fetchall()
    cards = []
    for c in courses:
        cover_tag = f'<img src="/uploads/{c["cover_img"]}" class="w-full h-44 object-cover rounded-2xl mb-3">' if c['cover_img'] else '<div class="w-full h-44 bg-gradient-to-b from-[#38bdf8] to-[#60a5fa] rounded-2xl flex items-center justify-center text-3xl mb-3">🎯</div>'
        cards.append(f'''
        <div class="bg-white p-4 rounded-3xl border border-slate-100 shadow-sm flex flex-col justify-between">
            <div>
                {cover_tag}
                <h4 class="font-black text-base text-slate-900 mb-1">{c['title']}</h4>
                <p class="text-xs text-slate-500 line-clamp-2 mb-4">{c['desc']}</p>
            </div>
            <div class="flex items-center justify-between pt-3 border-t border-slate-100">
                <span class="font-black text-base text-slate-900">{c['price']} <span class="text-xs font-bold text-slate-400">ر.س</span></span>
                <a href="/course/{c['id']}" class="bravo-teal-btn text-xs font-black px-5 py-2 rounded-full text-slate-900">عرض التفاصيل</a>
            </div>
        </div>''')
    conn.close()

    logo_img = uni['logo_img'] if uni and 'logo_img' in uni.keys() else None
    logo_tag = f'<img src="/uploads/{logo_img}" class="w-14 h-14 object-contain rounded-2xl">' if logo_img else f'<div class="text-4xl">{uni["logo"] if uni else "🏛️"}</div>'
    content = f'''
    <div class="max-w-md mx-auto px-4 py-8">
        <div class="bg-white rounded-[32px] p-6 border border-slate-100 shadow-sm mb-8 flex items-center gap-4">
            <div class="w-16 h-16 bg-slate-50 rounded-full shadow-xs flex items-center justify-center">{logo_tag}</div>
            <div>
                <h1 class="text-xl font-black text-slate-900">{uni["name"] if uni else "الجامعة"}</h1>
                <p class="text-xs text-slate-500 mt-1">{(uni["desc"] if uni else "") or "مقررات وشروحات الجامعة"}</p>
            </div>
        </div>

        <h2 class="text-lg font-black text-slate-900 mb-4">المواد المتاحة في الجامعة ({len(cards)})</h2>
        <div class="grid grid-cols-1 gap-6">
            {''.join(cards) if cards else '<div class="text-center py-12 text-slate-400 text-xs">لا توجد مواد مضافة لهذه الجامعة حالياً</div>'}
        </div>
    </div>
    '''
    return render_template('base.html', content=content)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    conn = get_db()
    c = conn.execute('''
        SELECT c.*, u.name as uname 
        FROM courses c 
        LEFT JOIN universities u ON c.uni_id=u.id 
        WHERE c.id=?
    ''', (course_id,)).fetchone()
    
    lessons = conn.execute('SELECT * FROM lessons WHERE course_id=? ORDER BY id ASC', (course_id,)).fetchall()
    uid = session.get('user_id')
    
    enrolled = False
    if uid:
        row = conn.execute('SELECT status FROM enrollments WHERE user_id=? AND course_id=?', (uid, course_id)).fetchone()
        if row and row['status'] == 'approved':
            enrolled = True

    lesson_items = []
    for idx, l in enumerate(lessons, 1):
        is_first_lesson = (idx == 1)
        can_access = is_first_lesson or enrolled or session.get('is_admin')
        
        has_video = ('video_filename' in l.keys() and l['video_filename'])
        has_pdf = ('pdf_filename' in l.keys() and l['pdf_filename'])

        btn_video = f'<a href="/watch/{l["id"]}" class="bravo-teal-btn text-[11px] font-black px-3.5 py-1.5 rounded-full text-slate-900">الشرح ▶</a>' if (has_video and can_access) else ('<span class="text-[11px] text-slate-400 font-bold bg-slate-100 px-2.5 py-1.5 rounded-full border border-slate-200">🔒 مقفل</span>' if has_video else '')
        btn_pdf = f'<a href="/uploads/{l["pdf_filename"]}" target="_blank" class="bg-blue-50 text-blue-700 border border-blue-200 text-[11px] font-black px-3 py-1.5 rounded-full hover:bg-blue-100">الملخص 📄</a>' if (has_pdf and can_access) else ('<span class="text-[11px] text-slate-400 font-bold bg-slate-100 px-2.5 py-1.5 rounded-full border border-slate-200">🔒 ملخص</span>' if has_pdf else '')
        preview_badge = '<span class="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-md font-black mr-2">تجريبي مجاناً</span>' if is_first_lesson else ''

        lesson_items.append(f'''
        <div class="p-3.5 flex items-center justify-between hover:bg-slate-50 transition">
            <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-full bg-slate-100 text-slate-800 text-xs font-black flex items-center justify-center">{idx}</span>
                <span class="text-xs font-bold text-slate-800">{l["title"]}</span>
                {preview_badge}
            </div>
            <div class="flex items-center gap-1.5">
                {btn_pdf}
                {btn_video}
            </div>
        </div>''')

    conn.close()

    cover_tag = f'<img src="/uploads/{c["cover_img"]}" class="w-full h-56 object-cover rounded-[32px]">' if (c and c['cover_img']) else '<div class="w-full h-56 bg-gradient-to-b from-[#38bdf8] to-[#60a5fa] rounded-[32px] flex items-center justify-center text-5xl">🎯</div>'

    code_val = c['code'] if (c and 'code' in c.keys()) else ''
    faculty_val = c['faculty'] if (c and 'faculty' in c.keys()) else 'كلية الهندسة'
    target_val = c['target_audience'] if (c and 'target_audience' in c.keys()) else 'طلاب وطالبات'
    old_p = c['old_price'] if (c and 'old_price' in c.keys()) else 0
    mid_p = c['mid_price'] if (c and 'mid_price' in c.keys()) else 100
    mid_old = c['mid_old_price'] if (c and 'mid_old_price' in c.keys()) else 150
    fin_p = c['final_price'] if (c and 'final_price' in c.keys()) else 120
    fin_old = c['final_old_price'] if (c and 'final_old_price' in c.keys()) else 170

    admin_manage_box = ""
    if session.get('is_admin'):
        admin_manage_box = f'''
        <div class="bg-amber-50 p-4 rounded-3xl border border-amber-200 mb-4">
            <div class="flex justify-between items-center mb-2">
                <span class="text-xs font-black text-amber-900">إدارة هذه المادة (خاص بالإدارة):</span>
                <span class="text-[11px] text-amber-700 font-bold">{len(lessons)} محاضرات حالية</span>
            </div>
            <a href="/admin/add-lesson-direct/{c['id']}" class="bravo-yellow-btn w-full block text-center py-2.5 rounded-full text-slate-900 font-black text-xs">
                ➕ إضافة محاضرة وشرح لهذه المادة مباشرة
            </a>
        </div>'''

    course_js = """
    <script>
        function switchTab(num) {
            for (var i = 1; i <= 4; i++) {
                document.getElementById('tab-content-' + i).classList.add('hidden');
                document.getElementById('tab-btn-' + i).className = 'bg-[#F4F6F8] text-slate-700 py-2.5 rounded-2xl transition';
            }
            document.getElementById('tab-content-' + num).classList.remove('hidden');
            document.getElementById('tab-btn-' + num).className = 'bg-[#1E293B] text-white py-2.5 rounded-2xl transition shadow-xs';
        }

        function togglePackageModal() {
            document.getElementById('package-modal').classList.toggle('hidden');
        }

        function selectPackage(type, price, oldPrice, label) {
            document.getElementById('display-price').innerText = price;
            document.getElementById('display-old-price').innerText = oldPrice > 0 ? oldPrice : '';
            document.getElementById('selected-package-label').innerText = label;
            togglePackageModal();
        }
    </script>
    """

    content = f'''
    <div class="max-w-md mx-auto px-4 py-4 pb-28">
        <div class="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 mb-3">
            <a href="/" class="hover:underline">الرئيسية</a>
            <span>&rsaquo;</span>
            <span class="text-slate-600">{(c['uname'] if c else 'جامعة الملك خالد') or 'جامعة الملك خالد'}</span>
        </div>

        <div class="mb-4">{cover_tag}</div>

        <div class="flex items-center justify-between mb-2">
            <h1 class="text-xl font-black text-slate-900">{c['title'] if c else 'المقرر'} {code_val}</h1>
            <div class="flex items-center gap-1 text-xs font-bold text-slate-700">
                <span>5.0</span>
                <span class="text-amber-400">★</span>
            </div>
        </div>

        <div class="bg-rose-50 border border-rose-100 rounded-2xl p-2.5 text-center text-[11px] font-bold text-rose-600 mb-4">
            تحذير قانوني : لا يجوز نشره او مشاركته
        </div>

        <div class="flex items-center gap-2 mb-4 flex-wrap">
            <span class="bg-[#F8CD46] text-slate-900 text-xs font-black px-4 py-1 rounded-full">{(c['uname'] if c else 'جامعة الملك خالد') or 'جامعة الملك خالد'}</span>
            <span class="bg-[#4AD7C5] text-slate-900 text-xs font-black px-4 py-1 rounded-full">{faculty_val}</span>
            <span class="bg-[#8B5CF6] text-white text-xs font-black px-4 py-1 rounded-full">{target_val}</span>
        </div>

        {admin_manage_box}

        <div class="flex items-center justify-between mb-4">
            <div class="text-2xl font-black text-slate-900">
                <span id="display-price">{c['price'] if c else 0}</span> <span class="text-sm font-bold text-slate-500">ر.س</span>
                <span id="display-old-price" class="text-slate-400 line-through text-sm font-bold mr-1">{old_p if old_p > 0 else ''}</span>
            </div>
            
            <button onclick="togglePackageModal()" class="bg-white border border-slate-200 rounded-2xl px-4 py-2 text-xs font-bold text-slate-700 flex items-center gap-2 shadow-xs">
                <span id="selected-package-label">المنهج كامل</span>
                <span class="text-[10px] text-slate-400">▼</span>
            </button>
        </div>

        <div class="space-y-3 mb-6">
            <a href="/checkout/{c['id'] if c else 1}" class="bravo-teal-btn w-full block text-center py-3 rounded-full font-black text-slate-900 text-xs">شراء للملخص &lsaquo;</a>
        </div>

        <div class="grid grid-cols-4 gap-1.5 mb-6 text-center text-xs font-black">
            <button id="tab-btn-1" onclick="switchTab(1)" class="bg-[#1E293B] text-white py-2.5 rounded-2xl transition shadow-xs">محتوى المنهج</button>
            <button id="tab-btn-2" onclick="switchTab(2)" class="bg-[#F4F6F8] text-slate-700 py-2.5 rounded-2xl transition">تفاصيل المقرر</button>
            <button id="tab-btn-3" onclick="switchTab(3)" class="bg-[#F4F6F8] text-slate-700 py-2.5 rounded-2xl transition">الجهة الشارحة</button>
            <button id="tab-btn-4" onclick="switchTab(4)" class="bg-[#F4F6F8] text-slate-700 py-2.5 rounded-2xl transition">التقييمات</button>
        </div>

        <div id="tab-content-1" class="space-y-4">
            <div class="bg-white rounded-3xl border border-slate-100 shadow-xs overflow-hidden">
                <div class="p-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                    <span class="font-black text-xs text-slate-800">قائمة الشروحات والملخصات المرفقة</span>
                    <span class="text-xs font-bold text-slate-400">{len(lessons)} درس</span>
                </div>
                <div class="divide-y divide-slate-100">
                    {''.join(lesson_items) if lesson_items else '<p class="p-6 text-xs text-slate-400 text-center">لا توجد دروس مرفوعة بعد</p>'}
                </div>
            </div>
        </div>

        <div id="tab-content-2" class="hidden space-y-4">
            <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-xs">
                <h3 class="font-black text-sm text-slate-900 mb-2">📖 وصف وتفاصيل المقرر:</h3>
                <p class="text-xs text-slate-600 leading-relaxed">{c['desc'] if c else ''}</p>
            </div>
        </div>

        <div id="tab-content-3" class="hidden space-y-4">
            <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-xs text-center">
                <div class="w-14 h-14 rounded-full bg-[#0B4B80] text-white flex items-center justify-center font-black text-xl mx-auto mb-3">إ</div>
                <h2 class="text-lg font-black text-slate-900 mb-1">أكاديمية إتقان التعليمية</h2>
                <div class="flex justify-center gap-4 text-xs font-bold text-slate-500 mb-4">
                    <span>👥 +1000 طالب وطالبة</span>
                    <span>📚 أعلى جودة تعليمية</span>
                </div>
                <p class="text-xs text-slate-600 leading-relaxed mb-4">نخبة من الأكاديميين والمحاضرين المتخصصين في تبسيط وشرح المقررات الجامعية وتلخيصها ومتابعة الطلاب لتحقيق الامتياز A+.</p>
                <a href="/instructor/1" class="bravo-teal-btn inline-block px-8 py-2.5 rounded-full text-xs font-black text-slate-900">الملف الأكاديمي &lsaquo;</a>
            </div>
        </div>

        <div id="tab-content-4" class="hidden space-y-4">
            <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-xs text-center">
                <span class="text-4xl font-black text-slate-900 block mb-1">5.0</span>
                <div class="flex justify-center text-amber-400 text-lg mb-2">★★★★★</div>
                <span class="text-xs text-slate-400 font-bold block mb-4">تقييم الطلاب المعتمد</span>
            </div>
        </div>
    </div>

    <div id="package-modal" class="fixed inset-0 z-50 flex items-end justify-center hidden">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs" onclick="togglePackageModal()"></div>
        <div class="relative bg-white w-full max-w-md rounded-t-[36px] p-6 z-10 shadow-2xl space-y-4">
            <div class="w-12 h-1 bg-slate-200 rounded-full mx-auto mb-2"></div>
            <h3 class="text-center font-black text-sm text-slate-800 mb-4">اختر باقة المقرر</h3>
            
            <div onclick="selectPackage('full', {c['price'] if c else 0}, {old_p or 0}, 'المنهج كامل')" class="flex items-center justify-between p-4 rounded-2xl border-2 border-teal-400 bg-teal-50/50 cursor-pointer">
                <span class="font-black text-xs text-slate-800">المنهج كامل</span>
                <span class="font-black text-sm text-slate-900">{c['price'] if c else 0} ر.س</span>
            </div>

            <div onclick="selectPackage('mid', {mid_p}, {mid_old}, 'الميد')" class="flex items-center justify-between p-4 rounded-2xl border border-slate-200 hover:border-slate-800 transition cursor-pointer">
                <span class="font-black text-xs text-slate-800">الميد</span>
                <span class="font-black text-sm text-slate-900">{mid_p} ر.س</span>
            </div>

            <div onclick="selectPackage('final', {fin_p}, {fin_old}, 'الفاينل')" class="flex items-center justify-between p-4 rounded-2xl border border-slate-200 hover:border-slate-800 transition cursor-pointer">
                <span class="font-black text-xs text-slate-800">الفاينل</span>
                <span class="font-black text-sm text-slate-900">{fin_p} ر.س</span>
            </div>
        </div>
    </div>

    <div class="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-slate-100 p-3 z-40">
        <div class="max-w-md mx-auto flex items-center justify-between gap-3">
            <a href="/checkout/{c['id'] if c else 1}" class="bravo-red-btn flex-grow py-3 rounded-full text-center text-white font-black text-xs shadow-md">
                تحميل للملخص &lsaquo;
            </a>
            <div class="bg-slate-100 px-3.5 py-2 rounded-2xl text-[11px] font-bold text-slate-600 whitespace-nowrap">
                📖 {len(lessons)} درس
            </div>
            <a href="https://wa.me/966593521664" target="_blank" class="w-10 h-10 bg-[#FACC15] border-2 border-slate-900 rounded-full flex items-center justify-center shrink-0 shadow-xs">
                <svg class="w-5 h-5 text-slate-900" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1c-4.97 0-9 4.03-9 9v7c0 2.21 1.79 4 4 4h1v-7H5v-4c0-3.87 3.13-7 7-7s7 3.13 7 7v4h-3v7h1c2.21 0 4-1.79 4-4v-7c0-4.97-4.03-9-9-9z"/></svg>
            </a>
        </div>
    </div>
    ''' + course_js
    return render_template('base.html', content=content)

@app.route('/instructor/<int:inst_id>')
def instructor_detail(inst_id):
    conn = get_db()
    inst = conn.execute('SELECT * FROM instructors WHERE id=?', (inst_id,)).fetchone()
    courses = conn.execute('''
        SELECT c.*, u.name as uname 
        FROM courses c 
        LEFT JOIN universities u ON c.uni_id=u.id 
        WHERE c.instructor_id=?
    ''', (inst_id,)).fetchall()
    conn.close()

    cards = []
    for c in courses:
        cover_img = c['cover_img'] if 'cover_img' in c.keys() else None
        cover_tag = f'<img src="/uploads/{cover_img}" class="w-full h-44 object-cover rounded-[28px] mb-2">' if cover_img else '<div class="w-full h-44 bg-[#0B4B80] rounded-[28px] mb-2 flex items-center justify-center text-3xl font-black text-white/40">🎯</div>'
        cards.append(f'''
        <a href="/course/{c['id']}" class="bg-white p-3 rounded-[32px] border border-slate-100 shadow-xs block">
            <div class="relative">
                {cover_tag}
                <div class="absolute bottom-4 right-3 bg-white/95 backdrop-blur-md px-3 py-1 rounded-xl text-[11px] font-bold text-slate-800 shadow-xs flex items-center gap-1">
                    <span class="text-amber-400">★ 5.0</span>
                    <span>{c['title']}</span>
                </div>
            </div>
            <div class="flex justify-between items-center px-2 pt-1 text-xs">
                <span class="font-black text-slate-900">{c['price']} ر.س</span>
                <span class="text-teal-600 font-bold">عرض المقرر &lsaquo;</span>
            </div>
        </a>''')

    avatar_tag = f'<img src="/uploads/{inst["avatar_img"]}" class="w-20 h-20 rounded-full object-cover border-4 border-white shadow-md">' if (inst and 'avatar_img' in inst.keys() and inst['avatar_img']) else '<div class="w-20 h-20 rounded-full bg-[#0B4B80] text-white flex items-center justify-center text-2xl font-black border-4 border-white shadow-md">إ</div>'

    content = f'''
    <div class="max-w-md mx-auto px-4 py-4 pb-20">
        <div class="relative bg-gradient-to-r from-slate-900 to-[#0B4B80] h-32 rounded-[32px] shadow-sm mb-12">
            <div class="absolute -bottom-8 left-1/2 -translate-x-1/2">{avatar_tag}</div>
        </div>

        <div class="text-center mb-6">
            <h1 class="text-xl font-black text-slate-900 mb-1">{inst['name'] if inst else 'الأكاديمية'}</h1>
            <div class="flex justify-center text-amber-400 text-sm mb-1">★★★★★ <span class="text-slate-400 text-xs font-bold mr-1">(تقييم 5.0)</span></div>
            
            <div class="flex justify-center gap-6 text-center my-4">
                <div><span class="text-lg font-black text-slate-900 block">{len(courses)}</span><span class="text-[11px] text-slate-400 font-bold">مادة</span></div>
                <div class="border-r border-slate-200"></div>
                <div><span class="text-lg font-black text-slate-900 block">+1000</span><span class="text-[11px] text-slate-400 font-bold">طالب مشترك</span></div>
            </div>
        </div>

        <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-xs mb-6">
            <h3 class="font-black text-sm text-slate-900 mb-2">نبذة عن الأكاديمية</h3>
            <p class="text-xs text-slate-600 leading-relaxed mb-4">{inst['bio'] if inst else ''}</p>
        </div>

        <h3 class="font-black text-sm text-slate-900 mb-3">المواد والشروحات المقدمة ({len(courses)})</h3>
        <div class="space-y-4">
            {''.join(cards) if cards else '<p class="text-center text-xs text-slate-400 py-6">لا توجد مواد مضافة بعد</p>'}
        </div>
    </div>
    '''
    return render_template('base.html', content=content)

@app.route('/admin/add-lesson-direct/<int:course_id>', methods=['GET', 'POST'])
def add_lesson_direct(course_id):
    if not session.get('is_admin'):
        return redirect('/admin/login')

    conn = get_db()
    c = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
    
    if request.method == 'POST':
        title = request.form.get('title')
        video = request.files.get('video_file')
        pdf = request.files.get('pdf_file')

        video_filename = None
        pdf_filename = None

        if video and video.filename:
            ext = os.path.splitext(secure_filename(video.filename))[1] or '.mp4'
            video_filename = f"vid_{int(time.time())}{ext}"
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

        if pdf and pdf.filename:
            ext = os.path.splitext(secure_filename(pdf.filename))[1] or '.pdf'
            pdf_filename = f"pdf_{int(time.time())}{ext}"
            pdf.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))

        conn.execute('INSERT INTO lessons (course_id, title, video_filename, pdf_filename) VALUES (?, ?, ?, ?)',
                     (course_id, title, video_filename, pdf_filename))
        conn.commit()
        conn.close()
        return redirect(f'/course/{course_id}')

    conn.close()
    content = f'''
    <div class="max-w-md mx-auto px-4 py-8">
        <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-xl">
            <h2 class="text-lg font-black text-slate-900 mb-1">إضافة محاضرة جديدة</h2>
            <p class="text-xs text-teal-600 font-bold mb-6">للمادة: {c['title'] if c else ''}</p>
            
            <form method="POST" enctype="multipart/form-data" class="space-y-4 text-xs font-bold">
                <div>
                    <label class="block mb-1 text-slate-700">عنوان المحاضرة:</label>
                    <input type="text" name="title" placeholder="مثال: المحاضرة 1" required class="w-full p-3 border rounded-2xl outline-none">
                </div>

                <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-3">
                    <div>
                        <label class="block mb-1 text-slate-700">ملف الفيديو (MP4) - اختياري:</label>
                        <input type="file" name="video_file" accept="video/*" class="w-full p-2 border border-dashed rounded-xl bg-white">
                    </div>
                    <div>
                        <label class="block mb-1 text-slate-700">ملف الملخص (PDF) - اختياري:</label>
                        <input type="file" name="pdf_file" accept=".pdf" class="w-full p-2 border border-dashed rounded-xl bg-white">
                    </div>
                </div>

                <button class="bravo-teal-btn w-full py-3.5 rounded-full font-black text-slate-900 text-sm shadow-md">
                    حفظ ونشر المحاضرة مباشرة
                </button>
            </form>
            <a href="/course/{course_id}" class="block text-center text-xs text-slate-400 mt-4 hover:underline">إلغاء والعودة للمادة</a>
        </div>
    </div>
    '''
    return render_template('base.html', content=content)

@app.route('/checkout/<int:course_id>')
def checkout(course_id):
    if not session.get('user_id'):
        return redirect('/login')
    conn = get_db()
    c = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
    banks = conn.execute('SELECT * FROM bank_accounts').fetchall()
    conn.close()
    
    wa_msg = f"مرحباً، أود تفعيل اشتراكي في مادة ({c['title'] if c else 'المقرر'}) باسم الطالب ({session.get('user_name')}) عبر منصة إتقان، وهذا إشعار التحويل."
    wa_link = f"https://wa.me/966593521664?text={wa_msg}"

    bank_cards = []
    for b in banks:
        bank_cards.append(f'''
        <div class="bg-slate-50 border-2 border-slate-200 p-4 rounded-2xl text-xs space-y-2 mb-3">
            <div class="flex justify-between items-center"><span class="text-slate-500 font-bold">البنك / المحفظة:</span><span class="font-black text-slate-900">{b['bank_name']}</span></div>
            <div class="flex justify-between items-center"><span class="text-slate-500 font-bold">المستفيد:</span><span class="font-black text-slate-900">{b['beneficiary']}</span></div>
            <div class="pt-1">
                <span class="text-slate-500 font-bold block mb-0.5">رقم الحساب:</span>
                <div class="bg-white p-2 rounded-xl border border-slate-300 text-center font-mono font-black text-slate-800 select-all tracking-wider">{b['account_num']}</div>
            </div>
            {f"""<div><span class='text-slate-500 font-bold block mb-0.5'>رقم الآيبان (IBAN):</span><div class='bg-white p-2 rounded-xl border border-slate-300 text-center font-mono font-black text-slate-800 select-all tracking-wide text-[11px]'>{b['iban']}</div></div>""" if b['iban'] else ""}
        </div>''')

    content = f'''
    <div class="max-w-md mx-auto px-4 py-8">
        <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-xl">
            <h2 class="text-xl font-black text-slate-900 mb-1 text-center">التحويل البنكي وتأكيد الاشتراك</h2>
            <p class="text-xs text-slate-500 mb-5 text-center">المادة: <b class="text-slate-800">{c['title'] if c else ''}</b> | المبلغ: <b class="text-teal-600 font-black">{c['price'] if c else 0} ر.س</b></p>
            <div class="mb-4">{''.join(bank_cards)}</div>
            <div class="space-y-3">
                <a href="{wa_link}" target="_blank" class="w-full flex items-center justify-center gap-2 bg-[#25D366] text-slate-900 font-black py-3.5 rounded-full text-xs border-2 border-slate-900 shadow-[0_4px_0_#0f172a]">📲 إرسال إشعار التحويل عبر واتساب</a>
                <form action="/buy/{c['id'] if c else 1}" method="POST">
                    <button class="w-full bg-[#0B4B80] hover:bg-slate-800 text-white font-black py-3.5 rounded-full text-xs transition">تأكيد التحويل (طلب التفعيل من الإدارة)</button>
                </form>
            </div>
        </div>
    </div>
    '''
    return render_template('base.html', content=content)

@app.route('/buy/<int:course_id>', methods=['POST'])
def buy(course_id):
    if not session.get('user_id'):
        return redirect('/login')
    conn = get_db()
    conn.execute('''INSERT INTO enrollments (user_id, course_id, status) 
                    VALUES (?, ?, 'pending') 
                    ON CONFLICT(user_id, course_id) DO UPDATE SET status='pending' ''', 
                 (session['user_id'], course_id))
    conn.commit()
    conn.close()
    return redirect(f'/course/{course_id}')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            conn = get_db()
            u = conn.execute('SELECT * FROM users WHERE name=?', (name,)).fetchone()
            if not u:
                c = conn.cursor()
                c.execute('INSERT INTO users (name) VALUES (?)', (name,))
                conn.commit()
                u_id = c.lastrowid
                is_admin = 0
            else:
                u_id = u['id']
                is_admin = u['is_admin']
            conn.close()
            session['user_id'] = u_id
            session['user_name'] = name
            session['is_admin'] = is_admin
            return redirect('/')
    return render_template('base.html', content='''
    <div class="max-w-sm mx-auto px-4 py-16">
        <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-xl text-center">
            <div class="w-14 h-14 bg-white border-2 border-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-sm p-1">
                <span class="text-2xl font-black text-[#0B4B80]">إ</span>
            </div>
            <h2 class="text-lg font-black mb-1 text-slate-900">تسجيل الدخول للطلاب</h2>
            <p class="text-xs text-slate-400 mb-6">اكتب اسمك الثلاثي للوصول السريع لحسابك</p>
            <form method="POST" class="space-y-3">
                <input type="text" name="name" placeholder="أدخل اسمك الثلاثي" required class="w-full p-3.5 border-2 border-slate-100 rounded-2xl text-xs font-bold outline-none focus:border-slate-800">
                <button class="bravo-teal-btn w-full font-black py-3 rounded-full text-xs text-slate-900">دخول المنصة</button>
            </form>
        </div>
    </div>''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= مسارات حماية وتسجيل دخول الإدارة =================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error_msg = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = 1
            session['user_name'] = "المدير العام"
            session['user_id'] = 1
            return redirect('/admin')
        else:
            error_msg = "اسم المستخدم أو كلمة المرور غير صحيحة!"

    content = f'''
    <div class="max-w-sm mx-auto px-4 py-16">
        <div class="bg-white p-7 rounded-[32px] border border-slate-100 shadow-xl text-center">
            <div class="w-16 h-16 bg-[#0B4B80] rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm text-2xl text-white font-black">
                🔐
            </div>
            <h2 class="text-xl font-black mb-1 text-slate-900">لوحة الإدارة - إتقان</h2>
            <p class="text-xs text-slate-400 mb-6">تسجيل الدخول للمدير العام</p>
            
            {f'<div class="bg-rose-50 text-rose-600 border border-rose-200 text-xs p-3 rounded-2xl font-bold mb-4">{error_msg}</div>' if error_msg else ''}

            <form method="POST" class="space-y-3 text-xs font-bold">
                <div class="text-right">
                    <label class="block mb-1 text-slate-700">اسم المستخدم:</label>
                    <input type="text" name="username" placeholder="أدخل اسم المستخدم" required class="w-full p-3.5 border-2 border-slate-100 rounded-2xl outline-none focus:border-slate-800">
                </div>
                <div class="text-right">
                    <label class="block mb-1 text-slate-700">كلمة المرور:</label>
                    <input type="password" name="password" placeholder="أدخل كلمة المرور" required class="w-full p-3.5 border-2 border-slate-100 rounded-2xl outline-none focus:border-slate-800">
                </div>
                <button type="submit" class="bravo-teal-btn w-full font-black py-3.5 rounded-full text-xs text-slate-900 shadow-md mt-2">
                    دخول لوحة التحكم
                </button>
            </form>
            <a href="/" class="block text-center text-xs text-slate-400 mt-4 hover:underline">العودة للرئيسية</a>
        </div>
    </div>'''
    return render_template('base.html', content=content)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect('/')

# ================= لوحة الإدارة الشاملة =================
@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect('/admin/login')

    try:
        conn = get_db()
        unis = conn.execute('SELECT * FROM universities').fetchall()
        courses = conn.execute('SELECT c.*, u.name as uname FROM courses c LEFT JOIN universities u ON c.uni_id=u.id ORDER BY c.id DESC').fetchall()
        lessons = conn.execute('SELECT l.*, c.title as cname FROM lessons l LEFT JOIN courses c ON l.course_id=c.id ORDER BY l.id DESC').fetchall()
        banks = conn.execute('SELECT * FROM bank_accounts').fetchall()
        works = conn.execute('SELECT * FROM semester_works ORDER BY id DESC').fetchall()

        pending_enr = conn.execute('''
            SELECT e.user_id, e.course_id, u.name as uname, c.title as cname 
            FROM enrollments e 
            JOIN users u ON e.user_id=u.id 
            JOIN courses c ON e.course_id=c.id 
            WHERE e.status='pending'
        ''').fetchall()

        active_enr = conn.execute('''
            SELECT e.user_id, e.course_id, u.name as uname, c.title as cname, c.price 
            FROM enrollments e 
            JOIN users u ON e.user_id=u.id 
            JOIN courses c ON e.course_id=c.id 
            WHERE e.status='approved'
        ''').fetchall()

        total_revenue = sum([float(row['price'] or 0) for row in active_enr if row['price']])
        total_students = len(conn.execute('SELECT DISTINCT user_id FROM enrollments WHERE status="approved"').fetchall())

        opts = "".join(['<option value="' + str(u['id']) + '">' + u['name'] + '</option>' for u in unis])
        c_opts = "".join(['<option value="' + str(c['id']) + '">' + (c['uname'] or '') + ' - ' + c['title'] + '</option>' for c in courses])

        work_items = []
        for w in works:
            work_items.append(f'''
            <div class="flex items-center justify-between p-3.5 bg-slate-50 rounded-2xl border border-slate-200 text-xs">
                <div>
                    <p class="font-black text-slate-900">{w['title']}</p>
                    <p class="text-slate-500 font-bold">{w['faculty']}</p>
                </div>
                <a href="/admin/delete-work/{w['id']}" onclick="return confirm('حذف هذا العمل الفصلي؟')" class="bg-rose-50 text-rose-600 px-3 py-1.5 rounded-xl font-black">حذف 🗑️</a>
            </div>''')

        course_items = []
        for c in courses:
            course_items.append(f'''
            <div class="flex items-center justify-between p-3.5 bg-slate-50 rounded-2xl border border-slate-200 text-xs">
                <div>
                    <p class="font-black text-slate-900">{c['title']}</p>
                    <p class="text-slate-500 font-bold">{c['uname'] or 'جامعة معتمدة'} ({c['price']} ر.س)</p>
                </div>
                <div class="flex items-center gap-1.5">
                    <a href="/course/{c['id']}" class="bg-blue-50 text-blue-700 px-3 py-1.5 rounded-xl font-bold">عرض</a>
                    <a href="/admin/delete-course/{c['id']}" onclick="return confirm('حذف المادة وجميع ملفاتها؟')" class="bg-rose-50 text-rose-600 px-3 py-1.5 rounded-xl font-black">حذف 🗑️</a>
                </div>
            </div>''')

        bank_items = []
        for b in banks:
            bank_items.append(f'''
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs">
                <div>
                    <span class="font-black text-slate-800">{b['bank_name']} - {b['beneficiary']}</span>
                    <p class="text-slate-500 font-mono text-[11px]">{b['account_num']}</p>
                </div>
                <a href="/admin/delete-bank/{b['id']}" onclick="return confirm('حذف هذا الحساب؟')" class="text-rose-600 bg-rose-50 px-2.5 py-1 rounded-xl font-bold">حذف 🗑️</a>
            </div>''')

        uni_rows = []
        for u in unis:
            logo_img = u['logo_img'] if 'logo_img' in u.keys() else None
            uni_logo = f'<img src="/uploads/{logo_img}" class="w-8 h-8 rounded-full object-contain bg-white p-1 border">' if logo_img else f'<span class="text-xl">{u["logo"] or "🏛️"}</span>'
            uni_rows.append(f'''
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs">
                <div class="flex items-center gap-2">
                    {uni_logo}
                    <span class="font-black text-slate-800">{u['name']}</span>
                </div>
                <a href="/admin/delete-uni/{u['id']}" onclick="return confirm('حذف الجامعة؟')" class="text-rose-600 bg-rose-50 px-2.5 py-1 rounded font-bold">حذف 🗑️</a>
            </div>''')

        lesson_rows = []
        for l in lessons:
            cname = l['cname'] or 'مقرر'
            has_video = '🎬 فيديو' if ('video_filename' in l.keys() and l['video_filename']) else ''
            has_pdf = '📄 ملخص' if ('pdf_filename' in l.keys() and l['pdf_filename']) else ''
            lesson_rows.append(f'''
            <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs flex flex-col gap-2">
                <div class="flex justify-between items-center">
                    <div>
                        <span class="font-black text-slate-800">{cname} - {l['title']}</span>
                        <div class="flex gap-2 text-[10px] text-teal-700 font-bold mt-0.5">
                            <span>{has_video}</span>
                            <span>{has_pdf}</span>
                        </div>
                    </div>
                    <a href="/admin/delete-lesson/{l['id']}" onclick="return confirm('حذف هذا الدرس؟')" class="text-rose-600 font-bold bg-rose-50 px-2.5 py-1 rounded-lg">حذف 🗑️</a>
                </div>
                <form action="/admin/edit-lesson-title" method="POST" class="flex gap-2">
                    <input type="hidden" name="lesson_id" value="{l['id']}">
                    <input type="text" name="title" value="{l['title']}" class="w-full p-2 border rounded-xl bg-white font-bold" required>
                    <button class="bg-[#0B4B80] text-white px-4 py-2 rounded-xl font-bold whitespace-nowrap">تعديل الاسم</button>
                </form>
            </div>''')

        pending_rows = []
        for p in pending_enr:
            pending_rows.append(f'''
            <div class="flex items-center justify-between p-3.5 bg-amber-50 rounded-2xl border border-amber-200 text-xs">
                <div>
                    <p class="font-black text-slate-800">{p['uname']}</p>
                    <p class="text-slate-500 font-bold">{p['cname']}</p>
                </div>
                <form action="/admin/approve-enrollment" method="POST" class="inline">
                    <input type="hidden" name="user_id" value="{p['user_id']}">
                    <input type="hidden" name="course_id" value="{p['course_id']}">
                    <button class="bg-emerald-600 text-white px-4 py-2 rounded-xl font-bold">تفعيل الاشتراك ✅</button>
                </form>
            </div>''')

        conn.close()

        content = f'''
        <div class="max-w-xl mx-auto px-4 py-8 space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-2xl font-black text-slate-900">لوحة الإدارة والتحكم الشاملة</h2>
                <a href="/admin/logout" class="bg-rose-50 text-rose-600 border border-rose-200 px-3.5 py-1.5 rounded-full text-xs font-black">خروج 🔒</a>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <div class="bg-gradient-to-tr from-sky-500 to-blue-600 text-white p-4 rounded-3xl shadow-sm text-center">
                    <span class="text-xs font-bold block mb-1">إجمالي المبيعات</span>
                    <span class="text-2xl font-black">{total_revenue} <span class="text-xs">ر.س</span></span>
                </div>
                <div class="bg-gradient-to-tr from-emerald-500 to-teal-600 text-white p-4 rounded-3xl shadow-sm text-center">
                    <span class="text-xs font-bold block mb-1">الطلاب المعتمدون</span>
                    <span class="text-2xl font-black">{total_students} <span class="text-xs">طالب</span></span>
                </div>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-amber-800 mb-3">🔔 طلبات اشتراك جديدة ({len(pending_rows)})</h3>
                <div class="space-y-2">
                    {''.join(pending_rows) if pending_rows else '<p class="text-xs text-slate-400 text-center py-2">لا توجد طلبات معلقة</p>'}
                </div>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-emerald-800 mb-3">💳 إضافة حساب أو بطاقة بنكية للتحويل</h3>
                <form action="/admin/add-bank" method="POST" class="space-y-3 text-xs mb-4">
                    <input type="text" name="bank_name" placeholder="اسم البنك أو المحفظة" required class="w-full p-3 border rounded-xl font-bold">
                    <input type="text" name="beneficiary" placeholder="اسم المستفيد الكامل" required class="w-full p-3 border rounded-xl font-bold">
                    <input type="text" name="account_num" placeholder="رقم الحساب / رقم الهاتف" required class="w-full p-3 border rounded-xl font-bold">
                    <input type="text" name="iban" placeholder="رقم الآيبان IBAN (اختياري)" class="w-full p-3 border rounded-xl font-bold">
                    <button class="bravo-teal-btn w-full py-3 rounded-full font-black text-slate-900">حفظ وإضافة الحساب البنكي</button>
                </form>
                <div class="border-t pt-3 space-y-2">
                    {''.join(bank_items)}
                </div>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-teal-800 mb-3">📝 نشر عمل فصلي / تكليف جديد</h3>
                <form action="/admin/add-work" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs mb-4">
                    <input type="text" name="title" placeholder="عنوان العمل الفصلي (مثال: واجب الرياضيات الأول)" required class="w-full p-3 border rounded-xl font-bold">
                    <input type="text" name="faculty" placeholder="الكلية أو القسم (مثال: كلية الهندسة)" required class="w-full p-3 border rounded-xl font-bold">
                    <textarea name="desc" placeholder="تفاصيل التكليف أو موعد التسليم والشروط" required class="w-full p-3 border rounded-xl"></textarea>
                    <div>
                        <label class="block mb-1 text-slate-600 font-bold">ملف التكليف أو الشرح (PDF أو صورة):</label>
                        <input type="file" name="work_file" class="w-full p-2 border border-dashed rounded-xl bg-slate-50">
                    </div>
                    <button class="bravo-teal-btn w-full py-3.5 rounded-full font-black text-slate-900">نشر العمل الفصلي للطلاب</button>
                </form>
                <div class="border-t pt-3 space-y-2">
                    <p class="text-[11px] font-bold text-slate-400 mb-1">الأعمال الفصلية المنشورة حالياً ({len(works)}):</p>
                    {''.join(work_items) if work_items else '<p class="text-xs text-slate-400 py-2 text-center">لا توجد أعمال فصلية مضافة</p>'}
                </div>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-slate-800 mb-3">📚 المواد المضافة حالياً ({len(courses)})</h3>
                <div class="space-y-2 max-h-60 overflow-y-auto">
                    {''.join(course_items) if course_items else '<p class="text-xs text-slate-400 py-3 text-center">لا توجد مواد مضافة</p>'}
                </div>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-emerald-800 mb-3">🏛️ إضافة جامعة جديدة</h3>
                <form action="/admin/add-uni" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs mb-4">
                    <input type="text" name="name" placeholder="اسم الجامعة" required class="w-full p-3 border rounded-xl font-bold">
                    <div>
                        <label class="block mb-1 text-slate-600 font-bold">صورة شعار الجامعة (PNG / JPG):</label>
                        <input type="file" name="logo_file" accept="image/*" class="w-full p-2 border border-dashed rounded-xl bg-slate-50">
                    </div>
                    <input type="text" name="desc" placeholder="وصف الجامعة" class="w-full p-3 border rounded-xl">
                    <button class="bravo-teal-btn w-full py-3 rounded-full font-black text-slate-900">حفظ وإضافة الجامعة</button>
                </form>
                <div class="border-t pt-3 space-y-2">
                    <p class="text-[11px] font-bold text-slate-400 mb-1">الجامعات المسجلة حالياً:</p>
                    {''.join(uni_rows)}
                </div>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-slate-800 mb-3">➕ إضافة مقرر جديد</h3>
                <form action="/admin/add-course" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs">
                    <select name="uni_id" class="w-full p-3 border rounded-xl bg-white font-bold">{opts}</select>
                    <div class="grid grid-cols-2 gap-2">
                        <input type="text" name="title" placeholder="اسم المادة" required class="p-3 border rounded-xl font-bold">
                        <input type="text" name="code" placeholder="رمز المادة" class="p-3 border rounded-xl font-bold">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <input type="number" step="1" name="price" placeholder="سعر المنهج بالريال" required class="p-3 border rounded-xl font-bold">
                        <input type="text" name="faculty" placeholder="الكلية" class="p-3 border rounded-xl font-bold">
                    </div>
                    <div>
                        <label class="block mb-1 text-slate-600 font-bold">صورة الغلاف (اتركه فارغاً للتدرج السماوي 🎯):</label>
                        <input type="file" name="cover_file" accept="image/*" class="w-full p-2 border border-dashed rounded-xl bg-slate-50">
                    </div>
                    <textarea name="desc" placeholder="وصف المادة" required class="w-full p-3 border rounded-xl"></textarea>
                    <button class="w-full bg-[#0B4B80] text-white py-3.5 rounded-full font-black">حفظ ونشر المقرر</button>
                </form>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-teal-800 mb-3">🎬 رفع درس (فيديو + ملخص PDF معاً)</h3>
                <form action="/admin/add-unified-lesson" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs">
                    <select name="c_id" class="w-full p-3 border rounded-xl bg-white font-bold">{c_opts}</select>
                    <input type="text" name="title" placeholder="عنوان المحاضرة" required class="w-full p-3 border rounded-xl font-bold">
                    <div class="bg-slate-50 p-3 rounded-2xl border border-slate-200 space-y-2">
                        <div>
                            <label class="block mb-1 text-slate-700 font-bold">1. فيديو الشرح (MP4) - اختياري:</label>
                            <input type="file" name="video_file" accept="video/*" class="w-full p-2 border border-dashed rounded-xl bg-white">
                        </div>
                        <div>
                            <label class="block mb-1 text-slate-700 font-bold">2. ملف الملخص (PDF) - اختياري:</label>
                            <input type="file" name="pdf_file" accept=".pdf" class="w-full p-2 border border-dashed rounded-xl bg-white">
                        </div>
                    </div>
                    <button class="bravo-teal-btn w-full py-3.5 rounded-full font-black text-slate-900 text-sm">حفظ ونشر المحاضرة</button>
                </form>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-emerald-800 mb-3">🏛️ إدارة وحذف الجامعات</h3>
                <div class="space-y-2">
                    {''.join(uni_rows)}
                </div>
            </div>

            <div class="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm">
                <h3 class="font-black text-sm text-slate-800 mb-3">🛠️ إدارة وحذف المحاضرات</h3>
                <div class="space-y-2 max-h-60 overflow-y-auto">
                    {''.join(lesson_rows) if lesson_rows else '<p class="text-xs text-slate-400 text-center py-2">لا توجد محاضرات</p>'}
                </div>
            </div>
        </div>
        '''
        return render_template('base.html', content=content)
    except Exception as e:
        return f"<div style='font-family:sans-serif; direction:rtl; padding:20px; color:#b91c1c;'><h2>حدث خطأ أثناء تحميل لوحة الإدارة:</h2><p>{str(e)}</p></div>", 500

@app.route('/admin/add-work', methods=['POST'])
def add_work():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    title = request.form.get('title')
    faculty = request.form.get('faculty')
    desc = request.form.get('desc')
    work_file = request.files.get('work_file')
    filename = None

    if work_file and work_file.filename:
        ext = os.path.splitext(secure_filename(work_file.filename))[1]
        filename = f"work_{int(time.time())}{ext}"
        work_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db()
    conn.execute('INSERT INTO semester_works (title, faculty, desc, file_name) VALUES (?, ?, ?, ?)',
                 (title, faculty, desc, filename))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/delete-work/<int:work_id>')
def delete_work(work_id):
    if not session.get('is_admin'):
        return redirect('/admin/login')
    conn = get_db()
    w = conn.execute('SELECT file_name FROM semester_works WHERE id=?', (work_id,)).fetchone()
    if w and w['file_name']:
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], w['file_name'])
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass
    conn.execute('DELETE FROM semester_works WHERE id=?', (work_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/add-bank', methods=['POST'])
def add_bank():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    bank_name = request.form.get('bank_name')
    beneficiary = request.form.get('beneficiary')
    account_num = request.form.get('account_num')
    iban = request.form.get('iban') or ''

    conn = get_db()
    conn.execute('INSERT INTO bank_accounts (bank_name, beneficiary, account_num, iban) VALUES (?, ?, ?, ?)',
                 (bank_name, beneficiary, account_num, iban))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/delete-bank/<int:bank_id>')
def delete_bank(bank_id):
    if not session.get('is_admin'):
        return redirect('/admin/login')
    conn = get_db()
    conn.execute('DELETE FROM bank_accounts WHERE id=?', (bank_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/approve-enrollment', methods=['POST'])
def approve_enrollment():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    u_id = request.form.get('user_id')
    c_id = request.form.get('course_id')
    conn = get_db()
    conn.execute("UPDATE enrollments SET status='approved' WHERE user_id=? AND course_id=?", (u_id, c_id))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/add-uni', methods=['POST'])
def add_uni():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    name = request.form.get('name')
    desc = request.form.get('desc') or ''
    logo_file = request.files.get('logo_file')
    logo_img_name = None

    if logo_file and logo_file.filename:
        ext = os.path.splitext(secure_filename(logo_file.filename))[1]
        logo_img_name = f"logo_{int(time.time())}{ext}"
        logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_img_name))

    conn = get_db()
    conn.execute("INSERT INTO universities (name, logo, desc, logo_img) VALUES (?, '🏛️', ?, ?)", 
                 (name, desc, logo_img_name))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/delete-uni/<int:uni_id>')
def delete_uni(uni_id):
    if not session.get('is_admin'):
        return redirect('/admin/login')
    conn = get_db()
    conn.execute("DELETE FROM universities WHERE id=?", (uni_id,))
    conn.execute("DELETE FROM courses WHERE uni_id=?", (uni_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/delete-course/<int:course_id>')
def delete_course(course_id):
    if not session.get('is_admin'):
        return redirect('/admin/login')
    conn = get_db()
    lessons = conn.execute("SELECT video_filename, pdf_filename FROM lessons WHERE course_id=?", (course_id,)).fetchall()
    for l in lessons:
        for fname in [l['video_filename'], l['pdf_filename']]:
            if fname:
                fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                if os.path.exists(fpath):
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass
    conn.execute("DELETE FROM lessons WHERE course_id=?", (course_id,))
    conn.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/add-unified-lesson', methods=['POST'])
def add_unified_lesson():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    try:
        c_id = request.form.get('c_id')
        title = request.form.get('title')
        video = request.files.get('video_file')
        pdf = request.files.get('pdf_file')

        video_filename = None
        pdf_filename = None

        if video and video.filename:
            ext = os.path.splitext(secure_filename(video.filename))[1] or '.mp4'
            video_filename = f"vid_{int(time.time())}{ext}"
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

        if pdf and pdf.filename:
            ext = os.path.splitext(secure_filename(pdf.filename))[1] or '.pdf'
            pdf_filename = f"pdf_{int(time.time())}{ext}"
            pdf.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))

        conn = get_db()
        conn.execute('INSERT INTO lessons (course_id, title, video_filename, pdf_filename) VALUES (?, ?, ?, ?)',
                     (c_id, title, video_filename, pdf_filename))
        conn.commit()
        conn.close()
    except Exception as e:
        return f"حدث خطأ أثناء الرفع: {str(e)}", 500
    return redirect('/admin')

@app.route('/admin/edit-lesson-title', methods=['POST'])
def edit_lesson_title():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    l_id = request.form.get('lesson_id')
    title = request.form.get('title')
    conn = get_db()
    conn.execute("UPDATE lessons SET title=? WHERE id=?", (title, l_id))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/delete-lesson/<int:lesson_id>')
def delete_lesson(lesson_id):
    if not session.get('is_admin'):
        return redirect('/admin/login')
    conn = get_db()
    l = conn.execute("SELECT video_filename, pdf_filename FROM lessons WHERE id=?", (lesson_id,)).fetchone()
    if l:
        for fname in [l['video_filename'], l['pdf_filename']]:
            if fname:
                fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                if os.path.exists(fpath):
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass
    conn.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/add-course', methods=['POST'])
def add_c():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    try:
        uni_id = request.form.get('uni_id')
        title = request.form.get('title')
        code = request.form.get('code') or ''
        desc = request.form.get('desc')
        price = request.form.get('price')
        faculty = request.form.get('faculty') or 'كلية الهندسة'
        cover_file = request.files.get('cover_file')
        cover_img_name = None

        if cover_file and cover_file.filename:
            ext = os.path.splitext(secure_filename(cover_file.filename))[1]
            cover_img_name = f"cover_{int(time.time())}{ext}"
            cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_img_name))

        conn = get_db()
        c = conn.cursor()
        c.execute('''INSERT INTO courses (uni_id, title, code, desc, price, cover_img, faculty) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (uni_id, title, code, desc, price, cover_img_name, faculty))
        new_id = c.lastrowid
        conn.commit()
        conn.close()
        return redirect(f'/course/{new_id}')
    except Exception as e:
        return f"حدث خطأ: {str(e)}", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
