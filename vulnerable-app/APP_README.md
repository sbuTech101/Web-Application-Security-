# Vulnerable Web Application - Security Learning Lab

⚠️ **CRITICAL WARNING: FOR EDUCATIONAL USE ONLY** ⚠️

This web application contains **INTENTIONAL security vulnerabilities** for learning purposes. **NEVER deploy this to the internet or use in production environments.**

## What's Inside?

This application contains 12 common web vulnerabilities:

1. **SQL Injection (SQLi)** - Multiple endpoints
2. **Cross-Site Scripting (XSS)** - Reflected XSS
3. **Insecure Direct Object Reference (IDOR)** - Access control issues
4. **Command Injection** - OS command execution
5. **Path Traversal** - File system access
6. **Broken Authentication** - Weak session management
7. **Sensitive Data Exposure** - Leaked credentials and config
8. **Server-Side Request Forgery (SSRF)** - Internal network access
9. **Insecure Deserialization** - Pickle RCE potential
10. **Weak Passwords** - Plain text storage
11. **Debug Information Leakage** - Exposed internals
12. **Missing Authorization** - No access controls

## Prerequisites

You need Python 3.7+ installed on your computer.

## Installation & Setup

### Step 1: Install Required Libraries

Open your terminal/command prompt and run:

```bash
pip install flask requests
```

### Step 2: Run the Application

```bash
python vulnerable_app.py
```

You should see output like:
```
============================================================
VULNERABLE WEB APPLICATION - EDUCATIONAL USE ONLY
============================================================

⚠️  WARNING: This application is INTENTIONALLY VULNERABLE
   DO NOT deploy this to the internet!
   Use only in isolated local environments for learning

Starting server on http://127.0.0.1:5000
============================================================
```

### Step 3: Open Your Browser

Go to: **http://127.0.0.1:5000**

You'll see the home page with links to all vulnerable endpoints.

## How to Use This for Learning

### Recommended Learning Path:

1. **Pick a vulnerability** from the home page
2. **Try to exploit it** using the hints provided
3. **Understand WHY it worked**
4. **Research the fix**
5. **Modify the code to fix it**
6. **Test that your fix works**
7. **Move to the next vulnerability**

## Vulnerability Exploitation Guide

### 1. SQL Injection (Login Page)

**Endpoint:** `/login`

**How to exploit:**
- Username: `admin' OR '1'='1`
- Password: `anything`
- Click Login

**What happens:** You bypass authentication and log in as admin!

**Why it works:** The SQL query becomes:
```sql
SELECT * FROM users WHERE username='admin' OR '1'='1' AND password='anything'
```
The `OR '1'='1'` is always true, so you get in.

**How to fix:**
- Use parameterized queries (prepared statements)
- Never concatenate user input into SQL
- Replace with: `c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))`

---

### 2. SQL Injection (Search)

**Endpoint:** `/search`

**How to exploit:**
- Search for: `' OR '1'='1`

**What happens:** You get ALL users in the database!

**How to fix:** Same as above - use parameterized queries.

---

### 3. Cross-Site Scripting (XSS)

**Endpoint:** `/comment`

**How to exploit:**
- Enter comment: `<script>alert('XSS')</script>`
- Submit

**What happens:** JavaScript executes in your browser!

**Why it works:** User input is directly inserted into HTML without escaping.

**How to fix:**
- Use `{{ variable }}` in templates (auto-escapes)
- Or manually escape: `from markupsafe import escape` and `escape(comment_text)`
- Never use `render_template_string` with user input

---

### 4. XSS in URL Parameter

**Endpoint:** `/profile?name=<script>alert('XSS')</script>`

**How to exploit:**
- Visit: `http://127.0.0.1:5000/profile?name=<img src=x onerror=alert('XSS')>`

**What happens:** JavaScript executes!

**How to fix:** Same as above - escape all user input.

---

### 5. Insecure Direct Object Reference (IDOR)

**Endpoint:** `/post/1` and `/user/1`

**How to exploit:**
- Visit `/post/1` - you see post 1
- Change to `/post/2` - you see post 2 (even if it's not yours!)
- Same with `/user/1`, `/user/2`, `/user/3`

**What happens:** You access other users' private data!

**Why it works:** No check to see if you're authorized to view that resource.

**How to fix:**
- Add authorization checks
- Verify the logged-in user owns the resource
- Example: `if post.user_id != session['user_id']: return "Access Denied"`

---

### 6. Command Injection

**Endpoint:** `/ping`

**How to exploit:**
- Linux/Mac: `127.0.0.1; ls`
- Windows: `127.0.0.1 & dir`

**What happens:** You execute arbitrary OS commands!

**Why it works:** User input is passed directly to `subprocess` with `shell=True`.

**How to fix:**
- Never use `shell=True`
- Use a list for commands: `subprocess.run(['ping', '-c', '1', host])`
- Validate input against a whitelist

---

### 7. Path Traversal

**Endpoint:** `/download?file=sample.txt`

**How to exploit:**
- Try: `?file=../vulnerable_app.py` (view the source code!)
- Linux: `?file=../../../etc/passwd`
- Windows: `?file=../../../Windows/System32/drivers/etc/hosts`

**What happens:** You read files outside the intended directory!

**How to fix:**
- Validate filename against whitelist
- Use `os.path.basename()` to strip path components
- Check `os.path.abspath()` is within allowed directory

---

### 8. Broken Authentication

**Endpoint:** `/admin`

**How to exploit:**
1. First, log in normally at `/login` (user: user1, pass: password)
2. Open browser Developer Tools (F12)
3. Go to Application/Storage → Cookies
4. Find the session cookie
5. Use a tool to decode it or manipulate it
6. Set `role=admin` in session
7. Visit `/admin`

**Alternative:** Use the SQL injection to log in as admin directly!

**How to fix:**
- Use secure session management
- Implement proper role-based access control
- Sign/encrypt session data
- Always verify permissions server-side

---

### 9. Sensitive Data Exposure

**Endpoint:** `/debug` and `/config`

**How to exploit:**
- Just visit `/debug` - you'll see the secret key, environment variables, etc.
- Visit `/config` - you'll see fake API keys and passwords

**What happens:** You get access to sensitive information!

**Why it works:** Debug info should NEVER be exposed in production.

**How to fix:**
- Remove debug endpoints in production
- Never hardcode credentials
- Use environment variables for secrets
- Set `app.debug = False` in production

---

### 10. Server-Side Request Forgery (SSRF)

**Endpoint:** `/fetch`

**How to exploit:**
- URL: `http://127.0.0.1:5000/debug`
- URL: `http://localhost:5000/config`

**What happens:** The server fetches internal URLs you shouldn't access!

**Why it works:** No validation on what URLs can be fetched.

**How to fix:**
- Whitelist allowed domains
- Block internal IP ranges (127.0.0.1, 192.168.x.x, 10.x.x.x)
- Validate URLs before fetching

---

### 11. Insecure Deserialization

**Endpoint:** `/deserialize`

**How to exploit:**
- This one is advanced - requires creating malicious pickle payloads
- Google "Python pickle RCE" for examples

**What happens:** Potential remote code execution!

**How to fix:**
- Never deserialize untrusted data
- Use JSON instead of pickle
- If you must use pickle, sign the data

---

## Tools to Use

### Browser Developer Tools (Built-in)
- Press F12 in Chrome/Firefox
- Inspect network requests
- View/edit cookies
- See console errors

### Burp Suite Community Edition (Free)
Download: https://portswigger.net/burp/communitydownload

**What it does:**
- Intercepts HTTP requests
- Lets you modify requests before sending
- Perfect for testing these vulnerabilities

### Python Requests (for scripting)
```python
import requests

# Example: Exploit SQL injection programmatically
response = requests.post('http://127.0.0.1:5000/login', data={
    'username': "admin' OR '1'='1",
    'password': 'anything'
})
print(response.text)
```

## Learning Resources

### After exploiting each vulnerability, research:

1. **OWASP Top 10**
   - https://owasp.org/www-project-top-ten/

2. **PortSwigger Web Security Academy** (FREE!)
   - https://portswigger.net/web-security
   - Interactive labs for each vulnerability type

3. **HackTheBox Academy**
   - https://academy.hackthebox.com/
   - More advanced penetration testing courses

4. **TryHackMe**
   - https://tryhackme.com/
   - Guided learning paths

## Next Steps After This Lab

1. **Try to fix each vulnerability** in the code
2. **Re-test to ensure your fix works**
3. **Create your own vulnerable app** with different vulnerabilities
4. **Practice on legal platforms:**
   - HackTheBox
   - TryHackMe
   - PentesterLab
   - DVWA (Damn Vulnerable Web Application)
   - WebGoat

## Default Credentials

For testing purposes:

| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | admin |
| user1    | password  | user  |
| user2    | pass123   | user  |

## Safety Reminders

✅ **DO:**
- Use this in a local, isolated environment
- Learn how vulnerabilities work
- Practice finding and fixing them
- Share knowledge with others learning security

❌ **DO NOT:**
- Deploy this to the internet
- Test these techniques on real websites (illegal!)
- Use vulnerabilities maliciously
- Share exploit code for malicious purposes

## Troubleshooting

**Port already in use:**
```bash
# Change port in vulnerable_app.py, line at the bottom:
app.run(debug=True, host='127.0.0.1', port=5001)  # Changed to 5001
```

**Module not found errors:**
```bash
pip install flask requests
```

**Database errors:**
- Delete `vulnerable.db` file
- Restart the application (it will recreate it)

## Questions?

This is a learning tool. If you're stuck:
1. Read the hints on each page
2. Google the vulnerability name + "tutorial"
3. Check the OWASP page for that vulnerability
4. Look at the source code to understand what's happening

## Legal Disclaimer

This application is provided for educational purposes only. Users must:
- Only use this in isolated, local environments
- Never deploy to production or the internet
- Not use learned techniques on systems without explicit permission
- Understand that unauthorized access to computer systems is illegal

The author assumes no liability for misuse of this educational material.

---

**Good luck on your security learning journey!** 🔐

Remember: Understanding vulnerabilities makes you a better developer and security professional.
