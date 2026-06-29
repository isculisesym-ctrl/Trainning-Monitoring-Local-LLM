# Security - OWASP Top 10 + Sr Principles

## 1. Injection (SQL, Command, NoSQL)

### SQL Injection
```python
# ❌ VULNERABLE
user = db.query(f"SELECT * FROM users WHERE email = '{email}'")

# ✅ SAFE: Parameterized query
user = db.query("SELECT * FROM users WHERE email = ?", email)

# FastAPI/SQLAlchemy (automatic)
user = await db.execute(
    select(User).where(User.email == email)
)
```

### NoSQL Injection
```python
# ❌ VULNERABLE (MongoDB)
db.users.find({"email": {"$regex": user_input}})

# ✅ SAFE
db.users.find({"email": {"$eq": email}})
```

---

## 2. Authentication & Authorization

### JWT Best Practices
```python
from datetime import datetime, timedelta
import jwt

class TokenManager:
    def create_token(self, user_id: str, expires_in: int = 3600) -> str:
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "jti": uuid.uuid4().hex  # Unique token ID (revocation)
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm="HS256"  # or RS256 for public key
        )
    
    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid token")

# Token Revocation (blacklist)
revoked_tokens = set()

def revoke_token(jti: str):
    revoked_tokens.add(jti)
    # Better: Redis con TTL = token expiry
    redis.sadd("revoked_tokens", jti, ex=token_expiry)

def is_revoked(jti: str) -> bool:
    return redis.sismember("revoked_tokens", jti)
```

### OAuth2 + Refresh Tokens
```python
# Access token: corta vida (15 min)
access_token = create_token(user_id, expires_in=900)

# Refresh token: larga vida (7 días)
refresh_token = create_token(user_id, expires_in=604800, type="refresh")

# Endpoint para refrescar
@app.post("/auth/refresh")
async def refresh(refresh_token: str):
    payload = verify_token(refresh_token)
    new_access = create_token(payload["sub"], expires_in=900)
    return {"access_token": new_access, "token_type": "bearer"}
```

---

## 3. Cross-Site Scripting (XSS)

### ❌ VULNERABLE
```html
<div id="user-name">{{ user_input }}</div>
```
Si user_input = `<script>alert('hacked')</script>`, ejecuta.

### ✅ SAFE: HTML Escape
```python
from markupsafe import escape

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    user = get_user(user_id)
    # Automático en Jinja2, Django
    return HTMLResponse(f"<h1>{escape(user.name)}</h1>")
```

### Content-Security-Policy (CSP)
```python
@app.middleware("http")
async def add_csp(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' cdn.example.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
    )
    return response
```

---

## 4. Cross-Site Request Forgery (CSRF)

### CSRF Token
```python
from fastapi import Form
from secrets import token_urlsafe

@app.get("/form")
async def get_form():
    csrf_token = token_urlsafe(32)
    request.session["csrf_token"] = csrf_token
    return {
        "html": f'<form method="POST" action="/submit">'
                f'<input type="hidden" name="csrf_token" value="{csrf_token}">'
                f'<input type="submit">'
                f'</form>'
    }

@app.post("/submit")
async def submit(csrf_token: str = Form(...), request: Request):
    if csrf_token != request.session.get("csrf_token"):
        raise HTTPException(403, "CSRF token invalid")
    # Process...

# Better: Use middleware (FastAPI has built-in)
from starlette.middleware.csrf import CSRFMiddleware
app.add_middleware(CSRFMiddleware, secret_key="secret")
```

---

## 5. Sensitive Data Exposure

### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor
)

# Hash (irreversible)
hashed = pwd_context.hash("user_password")

# Verify
is_valid = pwd_context.verify("user_password", hashed)

# ❌ NEVER: store plaintext, MD5, SHA1
# ✅ ALWAYS: bcrypt, argon2, scrypt (slow by design)
```

### API Key Rotation
```python
class APIKeyManager:
    async def rotate_key(self, user_id: str):
        # 1. Crea new key
        new_key = secrets.token_urlsafe(32)
        new_hash = hash_key(new_key)
        
        # 2. Keep old key valid por N horas (grace period)
        old_key = await self.get_current_key(user_id)
        await self.mark_as_deprecated(old_key, expires_in=3600)
        
        # 3. Set new key
        await self.store_key(user_id, new_hash)
        
        return new_key  # Return once, never again
```

---

## 6. Broken Access Control

### Role-Based Access Control (RBAC)
```python
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

def requires_role(*allowed_roles):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user_role = request.user.role
            if user_role not in allowed_roles:
                raise HTTPException(403, "Forbidden")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

@app.delete("/users/{user_id}")
@requires_role(Role.ADMIN)
async def delete_user(user_id: str, request: Request):
    # Only admin can delete
    await db.delete_user(user_id)
```

### Attribute-Based Access Control (ABAC)
```python
def check_permission(user, resource, action):
    # More granular: user.department == resource.department
    if user.role == "admin":
        return True
    
    if action == "read" and resource.is_public:
        return True
    
    if action == "edit" and resource.owner_id == user.id:
        return True
    
    return False
```

---

## 7. Security Headers

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Prevents clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevents MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enables XSS protection in older browsers
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # HSTS: Force HTTPS
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    
    return response
```

---

## 8. Data Encryption

### At Rest
```python
from cryptography.fernet import Fernet

cipher = Fernet(key)

# Encrypt sensitive field
encrypted_ssn = cipher.encrypt(ssn.encode())
await db.save({"ssn": encrypted_ssn})

# Decrypt only when needed
decrypted = cipher.decrypt(row.ssn).decode()
```

### In Transit
```
✅ HTTPS/TLS 1.3+
✅ Verify SSL certificates
❌ HTTP plaintext
❌ Self-signed certs in production
```

---

## 9. Dependency Vulnerabilities

```bash
# Scan dependencies
pip-audit
safety check

# Keep updated
pip list --outdated
pip install --upgrade package-name

# Lock versions
pip freeze > requirements.txt
pip install -r requirements.txt --require-hashes
```

---

## Sr Principles Summary

1. **Defense in Depth**: Multiple layers (auth + validation + encryption)
2. **Least Privilege**: Users get minimum permissions needed
3. **Secure by Default**: Safe defaults, explicit opt-out for risky
4. **Fail Secure**: When uncertain, deny access
5. **Input Validation**: Never trust user input
6. **Principle of Zero Trust**: Verify everything, always
