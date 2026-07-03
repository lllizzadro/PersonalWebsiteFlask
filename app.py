#Imports
from flask import Flask, render_template, redirect, url_for, request, g, flash, session
from functools import wraps
from werkzeug.security import check_password_hash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timezone
import sqlite3
import os
from werkzeug.middleware.proxy_fix import ProxyFix

#Initialize Flask app and variables
app = Flask(__name__)
# Fly terminates TLS and proxies to gunicorn over http; trust its forwarded headers so
# url_for(_external=True) / request.base_url emit correct https:// URLs (OG tags, etc.).
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
app.config['SESSION_COOKIE_SECURE'] = app.secret_key != 'dev'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
csrf = CSRFProtect(app)
DB_PATH = os.environ.get('DATABASE_PATH', 'guestbook.db')
SITE_URL='https://louislizzadro.com'

#Projects
PROJECTS = [
    {
        'name': 'Personal Website',
        'description': 'Personal website deployed on an automated CI/CD pipeline.',
        'tech': ['Python', 'Flask', 'Jinja', 'Tailwind', 'Docker'],
        'live': 'https://louislizzadro.com',
        'source': 'https://github.com/lllizzadro/PersonalWebsiteFlask'
    },
    {
        'name': 'Portal & Quill',
        'description': 'Website for a fantasy/sci-fi bookstore.',
        'tech': ['Python', 'Flask', 'Jinja', 'CSS', 'Docker'],
        'live': 'https://portalandquill.com',
        'source': 'https://github.com/lllizzadro/PortalAndQuill'
    },
    {
        'name': 'Music Generating Neural Network',
        'description': 'Generative Adversarial Network and Recurrent Neural Network that'
                       ' produce music after learning on MIDI data.',
        'tech': ['Python', 'TensorFlow', 'Keras', 'Pandas', 'NumPy'],
        'source': 'https://colab.research.google.com/drive/1FC11WSZKx_-6bCRr5oG6zxEbdJpZ71eo?usp=drive_link'
    }
]

#Admin
def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return view(**kwargs)
    return wrapped_view

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        if ADMIN_PASSWORD_HASH and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        flash('Invalid Password.')
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin/logout', methods=['POST'])
@admin_required
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

#Routes
@app.context_processor
def inject_site_url():
    return {'SITE_URL': SITE_URL}

@app.before_request
def canonical_host():
    host = request.host.split(':')[0] #Strip any port
    if host in ('www.louislizzadro.com', 'lllizzadro.fly.dev'):
        return redirect(SITE_URL + request.full_path.rstrip('?'), code=301)

@app.route('/robots.txt')
def robots():
    body = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    return app.response_class(body, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    paths = ['/', '/guestbook', '/resume']
    items = ''.join(f'<url><loc>{SITE_URL}{p}</loc></url>' for p in paths)
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>'
    return app.response_class(xml, mimetype='application/xml')

@app.route('/')
def home():
    return render_template('index.html', projects=PROJECTS)

@app.route('/guestbook')
def guestbook():
    db = get_db()
    entries = db.execute("SELECT * FROM guestbook ORDER BY timestamp DESC").fetchall()
    return render_template('guestbook.html', entries=entries)

@app.route('/admin/guestbook/<int:id>/delete', methods=['POST'])
@admin_required
def delete_entry(id):
    db = get_db()
    db.execute("DELETE FROM guestbook WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('guestbook'))


@app.route('/guestbook', methods=['POST'])
def add_message():
    if request.form.get('website'):
        return redirect(url_for('guestbook'))
    db = get_db()
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    if not name or not message:
        flash('Name and message are required.')
        return redirect(url_for('guestbook'))
    if len(name) > 50 or len(message) > 1000:
        flash('Name and message must be less than 50 and 1000 characters respectively.')
        return redirect(url_for('guestbook'))
    db.execute("INSERT INTO guestbook (name, message) VALUES (?, ?)", (name, message))
    db.commit()
    return redirect(url_for('guestbook'))

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.after_request
def set_security_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    resp.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return resp

@app.template_filter('prettydate')
def prettydate(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%b %d, %Y %I:%M %p')

@app.template_filter('isodate')
def isodate(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    return dt.isoformat()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(db):
    if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guestbook'").fetchone() is None:
        db.execute('CREATE TABLE guestbook (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, message TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
        db.commit()
    return

db = sqlite3.connect(DB_PATH)
init_db(db)
db.close()

if __name__ == '__main__':
    app.run(debug=True)