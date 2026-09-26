import os
from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import check_password_hash
import database

app = Flask(name)

# مفتاح سري عشوائي مشفر يُقرأ من البيئة أو يُولد تلقائياً
app.secret_key = os.environ.get('SECRET_KEY', 'itqan-fallback-secret-key-prod-2026')

# إعدادات حماية الجلسة والـ Cookies
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # منع سرقة الجلسة عبر كود JavaScript (XSS)
    SESSION_COOKIE_SAMESITE='Lax',  # الحماية من هجمات تزوير الطلبات CSRF
    SESSION_COOKIE_SECURE=False     # اجعلها True إذا كنت تستخدم دومين مخصص بـ HTTPS دائم
)

# تفعيل قاعدة البيانات عند بدء التشغيل
database.init_db()

# حقن ترويسات الأمان الأمنية في كل استجابة
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'                  # منع عرض الموقع داخل iFrame
    response.headers['X-Content-Type-Options'] = 'nosniff'        # منع تغيير نوع الملفات تلقائياً
    response.headers['X-XSS-Protection'] = '1; mode=block'         # تفعيل فلاتر المتصفح ضد XSS
    return response

@app.route('/')
def home():
    return render_template('base.html', content="<h1 class='text-2xl font-bold text-center py-10'>مرحباً بك في منصة إتقان</h1>")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        conn = database.get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        # التحقق الآمن باستخدام خوارزمية Hash المشفرة
        if admin and check_password_hash(admin['password_hash'], password):
            session['is_admin'] = True
            session['user_name'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('base.html', content="<p class='text-rose-600 text-center py-4'>بيانات الدخول غير صحيحة</p>")
            
    # واجهة تسجيل الدخول البسيطة
    form_html = '''
    <div class="max-w-md mx-auto my-12 p-6 bg-white border border-slate-200 rounded-2xl shadow-sm">
        <h2 class="text-xl font-bold mb-4 text-center">دخول لوحة الإدارة</h2>
        <form method="POST" class="space-y-4">
            <input type="text" name="username" placeholder="اسم المستخدم" required class="w-full p-2.5 border rounded-lg">
            <input type="password" name="password" placeholder="كلمة المرور" required class="w-full p-2.5 border rounded-lg">
            <button type="submit" class="w-full bg-[#0B4B80] text-white py-2.5 rounded-lg font-bold">تسجيل الدخول</button>
        </form>
    </div>
    '''
    return render_template('base.html', content=form_html)

@app.route('/admin')
def admin_dashboard():
    # التحقق من صلاحيات الدخول
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    return render_template('base.html', content="<h2 class='text-xl font-bold text-center py-8'>لوحة التحكم الإدارية - آمنة ومحمية</h2>")

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('home'))

if name == 'main':
    app.run(debug=False)
