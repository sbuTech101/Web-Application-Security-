# Security Fixes Guide - How to Make the App Secure

This guide shows you exactly how to fix each vulnerability in the vulnerable_app.py

## 🔧 Fix #1: SQL Injection

### Vulnerable Code:
```python
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
c.execute(query)
```

### Secure Code:
```python
# Use parameterized queries (prepared statements)
c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
```

**Why it works:** The database treats the parameters as DATA, not as part of the SQL command. No matter what the user types, it can't break out of the query.

---

## 🔧 Fix #2: Cross-Site Scripting (XSS)

### Vulnerable Code:
```python
comment_text = request.form.get('comment', '')
html = f'<div>{comment_text}</div>'
return render_template_string(html)
```

### Secure Code - Option 1 (Best):
```python
# Create a template file: templates/comment.html
from flask import render_template

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        comment_text = request.form.get('comment', '')
        return render_template('comment.html', comment=comment_text)
```

In `templates/comment.html`:
```html
<div>{{ comment }}</div>  <!-- Auto-escapes! -->
```

### Secure Code - Option 2 (Manual Escaping):
```python
from markupsafe import escape

comment_text = request.form.get('comment', '')
safe_comment = escape(comment_text)
html = f'<div>{safe_comment}</div>'
return render_template_string(html)
```

**Why it works:** Converts `<script>` to `&lt;script&gt;` so it displays as text instead of executing.

---

## 🔧 Fix #3: Insecure Direct Object Reference (IDOR)

### Vulnerable Code:
```python
@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = get_post(post_id)
    return render(post)  # Anyone can view any post!
```

### Secure Code:
```python
@app.route('/post/<int:post_id>')
def view_post(post_id):
    if 'user_id' not in session:
        return "Please login first", 401
    
    post = get_post(post_id)
    if not post:
        return "Post not found", 404
    
    # Authorization check
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        return "Access Denied: You don't own this post", 403
    
    return render(post)
```

**Why it works:** Checks if the logged-in user is authorized to view that specific resource.

---

## 🔧 Fix #4: Command Injection

### Vulnerable Code:
```python
command = f'ping -c 1 {host}'
subprocess.check_output(command, shell=True)  # DANGEROUS!
```

### Secure Code:
```python
import shlex

# Validate input first
if not re.match(r'^[\w\.-]+$', host):
    return "Invalid hostname"

# Use list format, no shell=True
result = subprocess.check_output(
    ['ping', '-c', '1', host],  # List, not string!
    shell=False,  # NEVER use shell=True with user input
    timeout=5
)
```

**Even Better - Whitelist:**
```python
ALLOWED_HOSTS = ['google.com', 'cloudflare.com', '1.1.1.1']

if host not in ALLOWED_HOSTS:
    return "Host not allowed"

result = subprocess.check_output(['ping', '-c', '1', host])
```

**Why it works:** Using a list prevents command injection because each element is treated as a separate argument, not as part of the command.

---

## 🔧 Fix #5: Path Traversal

### Vulnerable Code:
```python
filename = request.args.get('file')
filepath = os.path.join('files', filename)
with open(filepath, 'r') as f:
    return f.read()
```

### Secure Code:
```python
import os

filename = request.args.get('file')

# Strip any path components
filename = os.path.basename(filename)

# Build the full path
base_dir = os.path.abspath('files')
filepath = os.path.join(base_dir, filename)

# Security check: ensure file is still within allowed directory
if not os.path.abspath(filepath).startswith(base_dir):
    return "Access denied", 403

# Additional check: file exists and is a file
if not os.path.isfile(filepath):
    return "File not found", 404

with open(filepath, 'r') as f:
    return f.read()
```

**Why it works:** 
- `os.path.basename()` removes `../` attempts
- The `startswith()` check ensures the final path is still in the allowed directory

---

## 🔧 Fix #6: Broken Authentication

### Vulnerable Code:
```python
@app.route('/admin')
def admin():
    if session.get('role') == 'admin':
        return "Secret admin stuff"
```

### Secure Code:
```python
from functools import wraps

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if logged in
            if 'user_id' not in session:
                return redirect('/login')
            
            # Verify role from database (don't trust session alone)
            conn = sqlite3.connect('vulnerable.db')
            c = conn.cursor()
            c.execute("SELECT role FROM users WHERE id=?", (session['user_id'],))
            user = c.fetchone()
            conn.close()
            
            if not user or user[0] != role:
                return "Access Denied", 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin')
@require_role('admin')
def admin():
    return "Secret admin stuff"
```

**Additional Security:**
```python
# Use secure session cookies
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Not accessible via JavaScript
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)  # Sessions expire
)
```

---

## 🔧 Fix #7: Sensitive Data Exposure

### Vulnerable Code:
```python
@app.route('/debug')
def debug():
    return str(os.environ)  # Exposes everything!

@app.route('/config')
def config():
    return "DATABASE_PASSWORD=secret123"
```

### Secure Code:
```python
# REMOVE these endpoints entirely in production!
# Only enable in development

if app.debug:  # Only in development
    @app.route('/debug')
    def debug():
        # Even in dev, limit what you show
        safe_info = {
            'Python Version': sys.version,
            'Flask Version': flask.__version__
        }
        return safe_info

# For configuration, use environment variables:
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
API_KEY = os.getenv('API_KEY')

# NEVER hardcode secrets in source code!
```

**Create `.env` file (add to .gitignore!):**
```
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=randomly-generated-secret-key
API_KEY=your-api-key-here
```

---

## 🔧 Fix #8: Server-Side Request Forgery (SSRF)

### Vulnerable Code:
```python
url = request.form.get('url')
response = requests.get(url)  # Fetches ANY URL!
```

### Secure Code:
```python
from urllib.parse import urlparse
import ipaddress

def is_safe_url(url):
    """Check if URL is safe to fetch"""
    try:
        parsed = urlparse(url)
        
        # Only allow HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Block localhost and private IPs
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # Try to resolve IP
        ip = ipaddress.ip_address(hostname)
        
        # Block private networks
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
        
        return True
    except:
        return False

@app.route('/fetch', methods=['POST'])
def fetch_url():
    url = request.form.get('url')
    
    # Whitelist approach (best)
    ALLOWED_DOMAINS = ['example.com', 'api.trusted.com']
    parsed = urlparse(url)
    
    if parsed.hostname not in ALLOWED_DOMAINS:
        return "Domain not allowed", 403
    
    if not is_safe_url(url):
        return "URL not allowed", 403
    
    response = requests.get(url, timeout=5, allow_redirects=False)
    return response.text
```

---

## 🔧 Fix #9: Insecure Deserialization

### Vulnerable Code:
```python
import pickle
data = request.form.get('data')
obj = pickle.loads(base64.b64decode(data))  # DANGEROUS!
```

### Secure Code:
```python
import json

# Use JSON instead of pickle
data = request.form.get('data')
try:
    obj = json.loads(data)  # Much safer!
except json.JSONDecodeError:
    return "Invalid JSON", 400

# If you MUST use pickle (rare), verify signature first
import hmac

SECRET_KEY = os.getenv('SECRET_KEY')

def sign_data(data):
    signature = hmac.new(SECRET_KEY.encode(), data, 'sha256').hexdigest()
    return base64.b64encode(data).decode() + '.' + signature

def verify_and_load(signed_data):
    try:
        data_b64, signature = signed_data.split('.')
        data = base64.b64decode(data_b64)
        
        expected_sig = hmac.new(SECRET_KEY.encode(), data, 'sha256').hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError("Invalid signature")
        
        return pickle.loads(data)
    except:
        raise ValueError("Invalid data")
```

**Best Practice:** Just use JSON. Avoid pickle with user input entirely.

---

## 🔧 Fix #10: Password Security

### Vulnerable Code:
```python
# Storing passwords in plain text
c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, email))
```

### Secure Code:
```python
from werkzeug.security import generate_password_hash, check_password_hash

# When creating user
password_hash = generate_password_hash(password, method='pbkdf2:sha256')
c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password_hash, email))

# When checking login
c.execute("SELECT password FROM users WHERE username=?", (username,))
user = c.fetchone()

if user and check_password_hash(user[0], password):
    # Login successful
    session['user_id'] = user_id
else:
    # Login failed
    return "Invalid credentials"
```

---

## 🔐 Complete Secure Configuration

Put this at the top of your Flask app:

```python
from flask import Flask
import os
from datetime import timedelta

app = Flask(__name__)

# Security configuration
app.config.update(
    SECRET_KEY=os.urandom(32),  # Random secret key
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),  # Auto logout
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max upload
)

# Production settings
if not app.debug:
    # Disable debug mode in production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
```

---

## 📋 Security Checklist

Before deploying ANY web application:

- [ ] All user input is validated and sanitized
- [ ] SQL queries use parameterized statements
- [ ] Passwords are hashed (never plain text)
- [ ] XSS protection (escape all output)
- [ ] CSRF protection enabled
- [ ] HTTPS enforced
- [ ] Secure session configuration
- [ ] No debug endpoints in production
- [ ] Environment variables for secrets
- [ ] Authorization checks on all resources
- [ ] Input validation (whitelist, not blacklist)
- [ ] Rate limiting on sensitive endpoints
- [ ] Logging and monitoring enabled
- [ ] Regular security updates
- [ ] Security headers configured

---

## 🎯 Practice Exercise

**Challenge:** Take the vulnerable_app.py and fix ALL the vulnerabilities!

1. Create a new file: `secure_app.py`
2. Copy the vulnerable code
3. Fix each vulnerability one by one
4. Test that exploits no longer work
5. Verify legitimate functionality still works

This is the BEST way to learn - by actually fixing the code yourself!

---

Good luck! 🚀
