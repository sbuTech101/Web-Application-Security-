# Part 1: HTTP Basics

Notes from my web application testing practice, using a local vulnerable app (`127.0.0.1:5000`) and Burp Suite Community Edition.

> Lab only. Nothing here comes from a live site.

---
https://github.com/sbuTech101/Web-Application-Security-/blob/2e11d108e7bd3a378f00d2e7b6ecf4e120d00ef7/App-Sec/Vulnersql%20injection.PNG

## 1. Anatomy of an HTTP request

A request has four parts:

| Part | Example | Purpose |
|------|---------|---------|
| Request line | `POST /login HTTP/1.1` | Method, path, HTTP version |
| Headers | `Host: 127.0.0.1:5000` | `Name: value` metadata, one per line |
| Blank line | *(empty)* | Marks the end of the headers |
| Body | `username=...&password=...` | Optional data (used by POST, not GET) |

Key points I learned:
- The **method** says what to do (GET retrieves, POST submits data).
- The **query string** starts after `?` and holds `name=value` pairs joined by `&`.
- In HTTP/1.1 the `Host` header is mandatory.
- A GET request has no body, so the blank line ends the message.

## 2. Anatomy of an HTTP response

| Part | Example |
|------|---------|
| Status line | `HTTP/1.1 302 FOUND` |
| Headers | `Location: /dashboard`, `Set-Cookie: ...` |
| Blank line | *(empty)* |
| Body | The HTML, JSON or file being returned |

## 3. Status codes

| Code | Meaning | Why a tester cares |
|------|---------|--------------------|
| 200 | OK | Request succeeded |
| 301 / 302 | Redirect | Where does `Location` send me? |
| 400 | Bad request | Server rejected my malformed input |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Logged in, but not allowed (access control) |
| 404 | Not found | Resource doesn't exist (or is hidden) |
| 500 | Server error | My input may have broken something, worth investigating |

## 4. Worked example: login flow in Burp

![Burp Suite HTTP history showing login flow](screenshots/01-login-flow.jpg)

What happened, step by step:

1. **`POST /login` (request #5):** my credentials were sent in the body. `Content-Type: application/x-www-form-urlencoded` means the body is URL-encoded.
2. **`302 FOUND` response:** the server redirected me with `Location: /dashboard`.
3. **`Set-Cookie: session=...`:** the server issued a session cookie in that same response. My browser stores it.
4. **`GET /dashboard` (request #6):** the browser sent the cookie back in a `Cookie:` header, and the server returned `200` with the dashboard ("Welcome, admin!").

This is how the server recognises me between requests: HTTP is stateless, so the cookie carries my identity.

## 5. Observations

- **`HttpOnly` is set** on the cookie, so JavaScript can't read it. Good.
- **No `Secure` flag visible**, so the cookie could be sent over plain HTTP.
- **`Server: Werkzeug/3.0.3 Python/3.11.9`** reveals the tech stack (minor information disclosure).
- **The cookie looks like a Flask signed session** (starts with `eJ`, contains dots). I'll decode it in Part 2.

## 6. Key takeaway

Everything the client sends or stores (parameters, headers, cookies) can be read and changed by the user. **The client is untrusted, so the server must verify everything itself.**

---

**Next:** [Part 2: Encoding (URL, HTML, Base64)](02-encoding.md)
