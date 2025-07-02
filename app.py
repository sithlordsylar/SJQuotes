# app.py
import os, json
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, send_from_directory, flash, jsonify
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 1) Load credentials from .env
load_dotenv()
ADMIN_USER  = os.getenv('ADMIN_USER')
ADMIN_PASS  = os.getenv('ADMIN_PASS')
SECRET_KEY  = os.getenv('SECRET_KEY', 'change_this')

# 2) Paths & allowed extensions
BASE_DIR      = os.path.dirname(__file__)
QUOTES_FILE   = os.path.join(BASE_DIR, 'quotes.json')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXT   = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

# 3) Flask setup (Option A: serve static files from project root)
app = Flask(
    __name__,
    static_folder='.',       # serve files (index.html, style.css, app.js, assets/) from root
    static_url_path=''       # so '/index.html', '/style.css', '/assets/...' work
)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 4) Auth decorator
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

# 5) JSON helpers
def load_quotes():
    with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_quotes(data):
    with open(QUOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 6) Public site (serves index.html + static assets)
@app.route('/')
def public_index():
    return app.send_static_file('index.html')

# 7) Login/logout
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if (request.form['username'] == ADMIN_USER 
            and request.form['password'] == ADMIN_PASS):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 8) Admin dashboard
@app.route('/admin')
@login_required
def admin():
    quotes = load_quotes()
    return render_template('admin.html', quotes=quotes)

# 9) Posting handler
@app.route('/admin/posting', methods=['POST'])
@login_required
def posting():
    text  = request.form.get('text', '')
    type_ = request.form.get('type', '')
    role  = request.form.get('role', '')
    file  = request.files.get('file')
    image_url = ''

    # Handle file upload
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext in ALLOWED_EXT:
            filename = f"{datetime.utcnow().timestamp()}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = url_for('uploaded_file', filename=filename)

    # Append new entry
    quotes = load_quotes()
    new_id = str(int(quotes[-1]['id']) + 1) if quotes else '1'
    entry = {
        'id': new_id,
        'text': text,
        'imageUrl': image_url,
        'type': type_,
        'role': role,
        'createdAt': datetime.utcnow().isoformat() + 'Z'
    }
    quotes.append(entry)
    save_quotes(quotes)

    flash('Entry published!', 'success')
    return redirect(url_for('admin'))

# 10) Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 11) Public API endpoint
@app.route('/api/entries')
def api_entries():
    return jsonify(load_quotes())

# 12) Run app
if __name__ == '__main__':
    app.run(debug=True)