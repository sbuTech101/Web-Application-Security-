"""
VULNERABLE WEB APPLICATION - FOR LEARNING PURPOSES ONLY
DO NOT DEPLOY THIS TO THE INTERNET OR USE IN PRODUCTION

This application contains INTENTIONAL security vulnerabilities.
Your goal: Find and exploit them yourself.

Author: Educational purposes for security testing
"""

from flask import Flask, request, render_template_string, redirect, session, make_response
import sqlite3
import os
import subprocess
import pickle
import base64
import requests
from xml.etree import ElementTree as ET

app = Flask(__name__)
app.secret_key = 'weak_secret_key_123'

# Initialize database
def init_db():
    conn = sqlite3.connect('vulnerable.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS files 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, filename TEXT, filepath TEXT)''')
    
    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users VALUES (1, 'admin', 'admin123', 'admin@vuln.com', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'user1', 'password', 'user1@vuln.com', 'user')")
    c.execute("INSERT INTO users VALUES (3, 'user2', 'pass123', 'user2@vuln.com', 'user')")
    
    c.execute("DELETE FROM posts")
    c.execute("INSERT INTO posts VALUES (1, 1, 'Admin Post', 'This is an admin post with secret info')")
    c.execute("INSERT INTO posts VALUES (2, 2, 'User Post', 'Regular user post')")
    
    conn.commit()
    conn.close()

# Home page
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable Web App - Learning Lab</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 8px; max-width: 800px; margin: 0 auto; }
            h1 { color: #d32f2f; }
            .warning { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }
            .section { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; }
            a { color: #1976d2; text-decoration: none; display: block; margin: 5px 0; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔓 Vulnerable Web Application</h1>
            <div class="warning">
                <strong>⚠️ WARNING:</strong> This application contains intentional security vulnerabilities. 
                DO NOT deploy to the internet. Use only in isolated local environments for learning.
            </div>
            
            <h2>Available Endpoints:</h2>
            
            <div class="section">
                <h3>Authentication & User Management</h3>
                <a href="/login">→ Login Page</a>
                <a href="/search">→ User Search</a>
            </div>
            
            <div class="section">
                <h3>User Content</h3>
                <a href="/comment">→ Comment Section</a>
                <a href="/profile">→ Profile Page</a>
                <a href="/post/1">→ View Post</a>
                <a href="/user/1">→ View User Profile</a>
            </div>
            
            <div class="section">
                <h3>Utilities</h3>
                <a href="/ping">→ Ping Tool</a>
                <a href="/download">→ File Download</a>
                <a href="/fetch">→ URL Fetcher</a>
            </div>
            
            <div class="section">
                <h3>Admin & System</h3>
                <a href="/admin">→ Admin Panel</a>
                <a href="/debug">→ Debug Info</a>
                <a href="/config">→ Configuration</a>
                <a href="/deserialize">→ Data Deserializer</a>
            </div>
            
            <h3 style="margin-top: 30px;">Your Mission:</h3>
            <ol>
                <li>Explore each endpoint</li>
                <li>Try to find vulnerabilities</li>
                <li>Exploit them (ethically!)</li>
                <li>Understand WHY they work</li>
                <li>Research how to fix them</li>
                <li>Modify the code to patch the vulnerabilities</li>
            </ol>
            
            <p><strong>Credentials to try:</strong> admin/admin123, user1/password, user2/pass123</p>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = sqlite3.connect('vulnerable.db')
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        try:
            c.execute(query)
            user = c.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[4]
                return redirect('/dashboard')
            else:
                return render_template_string('<h2>Login Failed</h2><a href="/login">Try again</a>')
        except Exception as e:
            conn.close()
            return f"<h2>Error:</h2><pre>{str(e)}</pre><a href='/login'>Back</a>"
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Login</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        input { display: block; margin: 10px 0; padding: 8px; width: 300px; }
        button { padding: 10px 20px; background: #1976d2; color: white; border: none; cursor: pointer; }
    </style>
    </head>
    <body>
        <h1>Login</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <a href="/">Back to Home</a>
    </body>
    </html>
    '''
    return render_template_string(html)

# Search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search', '')
        
        conn = sqlite3.connect('vulnerable.db')
        c = conn.cursor()
        query = f"SELECT username, email FROM users WHERE username LIKE '%{search_term}%'"
        
        try:
            c.execute(query)
            results = c.fetchall()
            conn.close()
            
            html = f'<html><body><h2>Search Results for: {search_term}</h2><ul>'
            for row in results:
                html += f"<li>{row[0]} - {row[1]}</li>"
            html += '</ul><a href="/search">Search again</a> | <a href="/">Home</a></body></html>'
            return render_template_string(html)
        except Exception as e:
            conn.close()
            return f"<h2>Error:</h2><pre>{str(e)}</pre><a href='/search'>Back</a>"
    
    html = '''
    <html><body>
        <h1>User Search</h1>
        <form method="POST">
            <input type="text" name="search" placeholder="Search username">
            <button type="submit">Search</button>
        </form>
        <a href="/">Home</a>
    </body></html>
    '''
    return render_template_string(html)

# Comment
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        comment_text = request.form.get('comment', '')
        
        html = f'''
        <html><body>
            <h2>Your Comment:</h2>
            <div style="border: 1px solid #ccc; padding: 10px; margin: 20px 0;">
                {comment_text}
            </div>
            <a href="/comment">Post another comment</a> | <a href="/">Home</a>
        </body></html>
        '''
        return render_template_string(html)
    
    html = '''
    <html><body>
        <h1>Post a Comment</h1>
        <form method="POST">
            <textarea name="comment" rows="4" cols="50" placeholder="Enter your comment"></textarea><br>
            <button type="submit">Post Comment</button>
        </form>
        <a href="/">Home</a>
    </body></html>
    '''
    return render_template_string(html)

# Profile
@app.route('/profile')
def profile():
    name = request.args.get('name', 'Guest')
    
    html = f'''
    <html><body>
        <h1>Welcome, {name}!</h1>
        <p>This is your profile page.</p>
        <a href="/">Home</a>
    </body></html>
    '''
    return render_template_string(html)

# View Post
@app.route('/post/<int:post_id>')
def view_post(post_id):
    conn = sqlite3.connect('vulnerable.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()
    conn.close()
    
    if post:
        html = f'''
        <html><body>
            <h1>{post[2]}</h1>
            <p>{post[3]}</p>
            <p><em>Posted by user ID: {post[1]}</em></p>
            <a href="/">Home</a>
        </body></html>
        '''
        return render_template_string(html)
    return "<h2>Post not found</h2><a href='/'>Home</a>"

# View User
@app.route('/user/<int:user_id>')
def view_user(user_id):
    conn = sqlite3.connect('vulnerable.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        html = f'''
        <html><body>
            <h1>User Profile</h1>
            <p><strong>Username:</strong> {user[1]}</p>
            <p><strong>Email:</strong> {user[3]}</p>
            <p><strong>Password:</strong> {user[2]}</p>
            <p><strong>Role:</strong> {user[4]}</p>
            <a href="/">Home</a>
        </body></html>
        '''
        return render_template_string(html)
    return "<h2>User not found</h2><a href='/'>Home</a>"

# Ping
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        host = request.form.get('host', '')
        
        try:
            if os.name == 'nt':
                command = f'ping -n 1 {host}'
            else:
                command = f'ping -c 1 {host}'
            
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5)
            output = result.decode()
        except Exception as e:
            output = str(e)
        
        html = f'''
        <html><body>
            <h2>Ping Result:</h2>
            <pre>{output}</pre>
            <a href="/ping">Ping again</a> | <a href="/">Home</a>
        </body></html>
        '''
        return render_template_string(html)
    
    html = '''
    <html><body>
        <h1>Ping Tool</h1>
        <form method="POST">
            <input type="text" name="host" placeholder="Enter IP or hostname">
            <button type="submit">Ping</button>
        </form>
        <a href="/">Home</a>
    </body></html>
    '''
    return render_template_string(html)

# Download
@app.route('/download')
def download():
    filename = request.args.get('file', 'sample.txt')
    
    try:
        filepath = os.path.join('files', filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        html = f'''
        <html><body>
            <h2>File Content:</h2>
            <pre>{content}</pre>
            <a href="/">Home</a>
        </body></html>
        '''
        return render_template_string(html)
    except Exception as e:
        return f"<h2>Error:</h2><p>{str(e)}</p><a href='/'>Home</a>"

# Admin
@app.route('/admin')
def admin():
    if session.get('role') == 'admin':
        html = '''
        <html><body>
            <h1>Admin Panel</h1>
            <p>Welcome to the secret admin area!</p>
            <p>Database password: SuperSecret123</p>
            <p>API Key: sk-1234567890abcdef</p>
            <a href="/">Home</a>
        </body></html>
        '''
        return render_template_string(html)
    return "<h2>Access Denied</h2><p>Admin access only</p><a href='/login'>Login</a>"

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        html = f'''
        <html><body>
            <h1>Dashboard</h1>
            <p>Welcome, {session['username']}!</p>
            <p>Your role: {session.get('role', 'user')}</p>
            <a href="/admin">Admin Panel</a><br>
            <a href="/logout">Logout</a><br>
            <a href="/">Home</a>
        </body></html>
        '''
        return render_template_string(html)
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Debug
@app.route('/debug')
def debug():
    debug_info = {
        'Database Path': os.path.abspath('vulnerable.db'),
        'Secret Key': app.secret_key,
        'Environment Variables': dict(os.environ),
        'Current Session': dict(session),
        'Python Version': os.sys.version,
        'Working Directory': os.getcwd()
    }
    
    html = '<html><body><h1>Debug Information</h1><pre>'
    for key, value in debug_info.items():
        html += f"{key}: {value}\n\n"
    html += '</pre><a href="/">Home</a></body></html>'
    return render_template_string(html)

# Config
@app.route('/config')
def config():
    html = '''
    <html><body>
        <h1>Application Configuration</h1>
        <pre>
DATABASE_URL=postgresql://admin:password123@localhost/mydb
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STRIPE_SECRET_KEY=FAKE-stripe-key-for-training-only
ADMIN_PASSWORD=admin123
        </pre>
        <a href="/">Home</a>
    </body></html>
    '''
    return render_template_string(html)

# Fetch URL
@app.route('/fetch', methods=['GET', 'POST'])
def fetch_url():
    if request.method == 'POST':
        url = request.form.get('url', '')
        
        try:
            response = requests.get(url, timeout=5)
            content = response.text[:1000]
            
            html = f'''
            <html><body>
                <h2>Fetched Content:</h2>
                <pre>{content}</pre>
                <a href="/fetch">Fetch another URL</a> | <a href="/">Home</a>
            </body></html>
            '''
            return render_template_string(html)
        except Exception as e:
            return f"<h2>Error:</h2><p>{str(e)}</p><a href='/fetch'>Back</a>"
    
    html = '''
    <html><body>
        <h1>URL Fetcher</h1>
        <form method="POST">
            <input type="text" name="url" placeholder="Enter URL" style="width: 400px;">
            <button type="submit">Fetch</button>
        </form>
        <a href="/">Home</a>
    </body></html>
    '''
    return render_template_string(html)

# Deserialize
@app.route('/deserialize', methods=['GET', 'POST'])
def deserialize():
    if request.method == 'POST':
        data = request.form.get('data', '')
        
        try:
            decoded = base64.b64decode(data)
            obj = pickle.loads(decoded)
            
            html = f'''
            <html><body>
                <h2>Deserialized Object:</h2>
                <pre>{str(obj)}</pre>
                <a href="/deserialize">Try again</a> | <a href="/">Home</a>
            </body></html>
            '''
            return render_template_string(html)
        except Exception as e:
            return f"<h2>Error:</h2><p>{str(e)}</p><a href='/deserialize'>Back</a>"
    
    sample_obj = {'name': 'Sample', 'value': 123}
    serialized = base64.b64encode(pickle.dumps(sample_obj)).decode()
    
    html = f'''
    <html><body>
        <h1>Deserialize Data</h1>
        <form method="POST">
            <textarea name="data" rows="4" cols="60" placeholder="Base64 encoded pickled object">{serialized}</textarea><br>
            <button type="submit">Deserialize</button>
        </form>
        <a href="/">Home</a>
    </body></html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    os.makedirs('files', exist_ok=True)
    
    with open('files/sample.txt', 'w') as f:
        f.write('This is a sample file for testing.')
    
    init_db()
    
    print("\n" + "="*60)
    print("VULNERABLE WEB APPLICATION - EDUCATIONAL USE ONLY")
    print("="*60)
    print("\n⚠️  WARNING: This application is INTENTIONALLY VULNERABLE")
    print("   DO NOT deploy this to the internet!")
    print("   Use only in isolated local environments for learning\n")
    print("Starting server on http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
